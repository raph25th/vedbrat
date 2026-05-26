from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.deps import ensure_staff_or_owner, get_client_for_user, get_current_user, get_optional_current_user, require_roles
from app.models import (
    Agent,
    CfaDeal,
    CfaDealDocument,
    CfaDealStatusHistory,
    Client,
    ClientBankAccount,
    Contract,
    DocumentTemplate,
    DocumentIssueRequest,
    GeneratedDocument,
    LiquidityLotAllocation,
    LiquidityPurchaseLot,
    Referral,
    TelegramChat,
    User,
)
from app.schemas import (
    AgentCreate,
    AgentOut,
    AgentUpdate,
    CfaDealCreate,
    CfaDealDocumentCreate,
    CfaDealDocumentOut,
    CfaDealOut,
    CfaDealStatusHistoryOut,
    CfaDealUpdate,
    ClientBankAccountCreate,
    ClientBankAccountOut,
    ClientBankAccountUpdate,
    ClientCreate,
    ClientOut,
    ClientUpdate,
    ContractCreate,
    ContractOut,
    ContractUpdate,
    DocumentTemplateCreate,
    DocumentTemplateOut,
    DocumentTemplateUpdate,
    DocumentIssueRequestCreate,
    DocumentIssueRequestOut,
    DocumentIssueRequestUpdate,
    DealActualCloseRateUpdate,
    DealRateUpdate,
    DealReferralUpdate,
    DealStatusUpdate,
    DealWalletUpdate,
    LoginRequest,
    LiquidityAllocationRequest,
    LiquidityAllocationResult,
    LiquidityLotAllocateRequest,
    LiquidityLotAllocationOut,
    LiquidityPurchaseLotCreate,
    LiquidityPurchaseLotOut,
    LiquidityPurchaseLotUpdate,
    ReferralCreate,
    ReferralOut,
    ReferralUpdate,
    TelegramChatCreate,
    TelegramChatOut,
    TelegramChatSetup,
    TelegramChatUpdate,
    TemplateTestRenderOut,
    TemplateTestRenderRequest,
    TemplateVariablesOut,
    Token,
    UserCreate,
    UserOut,
    UserUpdate,
)
from app.services.document_flow import find_matching_document_templates, resolve_document_flow_type
from app.services.document_request_generator import DOCUMENT_KEYS, DocumentGenerationError, format_date, format_money, generate_request_documents
from app.services.document_templates import DocumentTemplateError, DocumentTemplateService

router = APIRouter()
ModelT = TypeVar("ModelT")
template_service = DocumentTemplateService()
DOCUMENT_ISSUER_ROLES = ("admin", "director", "document_admin", "admin_assistant")


def apply_update(obj: Any, payload: Any) -> Any:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    return obj


def get_or_404(db: Session, model: type[ModelT], obj_id: int) -> ModelT:
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


def prepare_client_values(values: dict[str, Any]) -> dict[str, Any]:
    values["full_name_ru"] = values.get("full_name_ru") or values.get("ru_name") or "Unnamed client"
    values["ru_name"] = values.get("ru_name") or values["full_name_ru"]
    values["full_name_en"] = values.get("full_name_en") or values.get("en_name")
    values["en_name"] = values.get("en_name") or values.get("full_name_en")
    values["tax_residency"] = values.get("tax_residency") or values.get("tax_residency_country")
    values["tax_residency_country"] = values.get("tax_residency_country") or values.get("tax_residency")
    values["passport_number"] = values.get("passport_number") or values.get("passport_series_number")
    values["passport_series_number"] = values.get("passport_series_number") or values.get("passport_number")
    return values


def calculate_profit_fields(deal: CfaDeal) -> None:
    if not deal.client_rate or not deal.actual_close_rate or not deal.amount_rub:
        return
    client_asset_amount = Decimal(deal.amount_rub) / Decimal(deal.client_rate)
    actual_asset_amount = Decimal(deal.amount_rub) / Decimal(deal.actual_close_rate)
    gross_profit_usdt = client_asset_amount - actual_asset_amount
    referral_fee_usdt = Decimal(deal.referral_fee_usdt or 0)
    referral_fee_rub = Decimal(deal.referral_fee_rub or 0)

    if deal.referral_fee_type and deal.referral_fee_value is not None:
        fee_value = Decimal(deal.referral_fee_value)
        if deal.referral_fee_type == "percent":
            base = Decimal(deal.amount_rub)
            if deal.referral_fee_base == "client_asset_amount":
                referral_fee_usdt = client_asset_amount * fee_value / Decimal(100)
                referral_fee_rub = referral_fee_usdt * Decimal(deal.actual_close_rate)
            elif deal.referral_fee_base == "profit":
                referral_fee_usdt = gross_profit_usdt * fee_value / Decimal(100)
                referral_fee_rub = referral_fee_usdt * Decimal(deal.actual_close_rate)
            else:
                referral_fee_rub = base * fee_value / Decimal(100)
                referral_fee_usdt = referral_fee_rub / Decimal(deal.actual_close_rate)
        elif deal.referral_fee_type == "fixed_usdt":
            referral_fee_usdt = fee_value
            referral_fee_rub = fee_value * Decimal(deal.actual_close_rate)
        elif deal.referral_fee_type == "fixed_rub":
            referral_fee_rub = fee_value
            referral_fee_usdt = fee_value / Decimal(deal.actual_close_rate)

    deal.client_asset_amount = client_asset_amount
    deal.actual_asset_amount = actual_asset_amount
    deal.gross_profit_usdt = gross_profit_usdt
    deal.gross_profit_rub = gross_profit_usdt * Decimal(deal.actual_close_rate)
    deal.referral_fee_usdt = referral_fee_usdt
    deal.referral_fee_rub = referral_fee_rub
    deal.net_profit_usdt = gross_profit_usdt - referral_fee_usdt
    deal.net_profit_rub = deal.gross_profit_rub - referral_fee_rub


def calculate_liquidity_volume(amount_rub: Decimal, rate: Decimal) -> Decimal:
    if rate <= 0:
        raise HTTPException(status_code=400, detail="Purchase rate must be greater than zero")
    return (Decimal(amount_rub) / Decimal(rate)).quantize(Decimal("0.000001"))


def refresh_liquidity_lot_status(lot: LiquidityPurchaseLot) -> None:
    if Decimal(lot.remaining_asset_volume or 0) <= 0:
        lot.remaining_asset_volume = Decimal("0")
        lot.status = "closed"
    elif Decimal(lot.used_asset_volume or 0) > 0:
        lot.status = "partially_used"
    else:
        lot.status = "open"


def prepare_liquidity_lot_values(values: dict[str, Any]) -> dict[str, Any]:
    amount = Decimal(values["purchase_amount_rub"])
    rate = Decimal(values["purchase_rate"])
    volume = values.get("purchased_asset_volume")
    if volume is None:
        volume = calculate_liquidity_volume(amount, rate)
    values["purchased_asset_volume"] = Decimal(volume)
    values["used_asset_volume"] = Decimal(values.get("used_asset_volume") or 0)
    values["remaining_asset_volume"] = Decimal(values.get("remaining_asset_volume") or values["purchased_asset_volume"])
    values["status"] = values.get("status") or "open"
    return values


def deal_liquidity_volume(deal: CfaDeal, requested_volume: Decimal | None = None) -> Decimal:
    if requested_volume is not None:
        return Decimal(requested_volume)
    if deal.actual_asset_amount:
        return Decimal(deal.actual_asset_amount)
    if deal.client_asset_amount:
        return Decimal(deal.client_asset_amount)
    amount = Decimal(deal.amount_rub or deal.full_payment_amount or 0)
    rate = Decimal(deal.actual_close_rate or deal.client_rate or 0)
    if amount <= 0 or rate <= 0:
        raise HTTPException(status_code=400, detail="Deal asset volume or rate is required for liquidity allocation")
    return (amount / rate).quantize(Decimal("0.000001"))


def allocated_deal_volume(db: Session, deal_id: int, asset: str) -> Decimal:
    allocations = db.query(LiquidityLotAllocation).filter(
        LiquidityLotAllocation.deal_id == deal_id,
        LiquidityLotAllocation.asset == asset,
    ).all()
    return sum((Decimal(item.asset_volume or 0) for item in allocations), Decimal("0"))


def allocate_from_lot(
    db: Session,
    lot: LiquidityPurchaseLot,
    deal: CfaDeal,
    volume: Decimal,
    comment: str | None = None,
) -> LiquidityLotAllocation:
    if lot.asset != (deal.asset or "USDT"):
        raise HTTPException(status_code=400, detail="Liquidity lot asset does not match deal asset")
    volume = Decimal(volume).quantize(Decimal("0.000001"))
    if volume <= 0:
        raise HTTPException(status_code=400, detail="Allocation volume must be greater than zero")
    if lot.status == "closed" or Decimal(lot.remaining_asset_volume or 0) < volume:
        raise HTTPException(status_code=400, detail="Liquidity lot does not have enough remaining volume")

    allocation = LiquidityLotAllocation(
        lot_id=lot.id,
        deal_id=deal.id,
        asset=lot.asset,
        asset_volume=volume,
        allocation_rate=lot.purchase_rate,
        cost_basis_rub=(volume * Decimal(lot.purchase_rate)).quantize(Decimal("0.01")),
        comment=comment,
    )
    db.add(allocation)
    lot.used_asset_volume = Decimal(lot.used_asset_volume or 0) + volume
    lot.remaining_asset_volume = Decimal(lot.remaining_asset_volume or 0) - volume
    refresh_liquidity_lot_status(lot)
    return allocation


def finalize_deal_liquidity_close(db: Session, deal: CfaDeal, target_volume: Decimal, current_user_id: int | None = None, comment: str | None = None) -> None:
    allocations = db.query(LiquidityLotAllocation).filter(LiquidityLotAllocation.deal_id == deal.id).all()
    total_volume = sum((Decimal(item.asset_volume or 0) for item in allocations), Decimal("0"))
    if total_volume < target_volume:
        return
    total_cost = sum((Decimal(item.cost_basis_rub or 0) for item in allocations), Decimal("0"))
    deal.actual_asset_amount = total_volume.quantize(Decimal("0.000001"))
    if total_volume > 0:
        deal.actual_close_rate = (total_cost / total_volume).quantize(Decimal("0.000001"))
    old_status = deal.status
    deal.status = "closed"
    deal.completed_at = deal.completed_at or datetime.now(timezone.utc)
    deal.required_action = None
    if old_status != deal.status:
        db.add(CfaDealStatusHistory(deal_id=deal.id, old_status=old_status, new_status=deal.status, changed_by=current_user_id, comment=comment))


def auto_allocate_deal_liquidity(
    db: Session,
    deal: CfaDeal,
    target_volume: Decimal,
    comment: str | None = None,
) -> list[LiquidityLotAllocation]:
    asset = deal.asset or "USDT"
    already_allocated = allocated_deal_volume(db, deal.id, asset)
    remaining_need = (Decimal(target_volume) - already_allocated).quantize(Decimal("0.000001"))
    if remaining_need <= 0:
        return db.query(LiquidityLotAllocation).filter(LiquidityLotAllocation.deal_id == deal.id).order_by(LiquidityLotAllocation.id.desc()).all()

    available_lots = db.query(LiquidityPurchaseLot).filter(
        LiquidityPurchaseLot.asset == asset,
        LiquidityPurchaseLot.status != "closed",
        LiquidityPurchaseLot.remaining_asset_volume > 0,
    ).order_by(LiquidityPurchaseLot.remaining_asset_volume.asc(), LiquidityPurchaseLot.id.asc()).all()
    available_volume = sum((Decimal(lot.remaining_asset_volume or 0) for lot in available_lots), Decimal("0"))
    if available_volume < remaining_need:
        raise HTTPException(status_code=400, detail="Not enough available liquidity for this deal")

    created: list[LiquidityLotAllocation] = []
    for lot in available_lots:
        if remaining_need <= 0:
            break
        volume = min(Decimal(lot.remaining_asset_volume or 0), remaining_need)
        created.append(allocate_from_lot(db, lot, deal, volume, comment))
        remaining_need = (remaining_need - volume).quantize(Decimal("0.000001"))
    return created


def prepare_document_request_values(values: dict[str, Any]) -> dict[str, Any]:
    values["status"] = values.get("status") or "submitted"
    values["request_source"] = values.get("request_source") or "mini_app"
    values["request_type"] = values.get("request_type") or values.get("document_package_type") or "offer_crypto_individual"
    values["client_type"] = values.get("client_type") or "individual"
    values["deal_type"] = values.get("deal_type") or "crypto"
    values["document_package_type"] = values.get("document_package_type") or "offer_crypto_individual"
    values["currency"] = values.get("currency") or "RUB"
    values["crypto_asset"] = values.get("crypto_asset") or "USDT"
    values["agent_fee_percent"] = values.get("agent_fee_percent") if values.get("agent_fee_percent") is not None else Decimal("0.1")
    values["offer_version"] = values.get("offer_version") or "1.002"
    values["offer_date"] = values.get("offer_date") or date(2026, 5, 18)
    full_amount = values.get("full_payment_amount") or values.get("total_amount")
    values["full_payment_amount"] = full_amount
    values["total_amount"] = values.get("total_amount") or full_amount
    agent_fee_percent = values.get("agent_fee_percent")
    if full_amount is not None and agent_fee_percent is not None:
        total = Decimal(full_amount)
        fee_percent = Decimal(agent_fee_percent)
        supplier_payment_equal = (total / (Decimal(1) + fee_percent / Decimal(100))).quantize(Decimal("0.01"))
        agent_fee_amount = (total - supplier_payment_equal).quantize(Decimal("0.01"))
        values["supplier_payment_equal"] = values.get("supplier_payment_equal") or supplier_payment_equal
        values["payment_amount"] = values.get("payment_amount") or supplier_payment_equal
        values["agent_fee_amount"] = values.get("agent_fee_amount") or agent_fee_amount
    return values


def payload_value(request: DocumentIssueRequest, key: str) -> Any:
    payload = request.payload_json or {}
    return payload.get(key)


def extract_client_values_from_request(values: dict[str, Any]) -> dict[str, Any]:
    raw_payload = values.get("payload_json") or {}
    return prepare_client_values(
        {
            "client_type": values.get("client_type") or raw_payload.get("client_type") or "individual",
            "ru_name": raw_payload.get("ru_name"),
            "en_name": raw_payload.get("en_name"),
            "inn": raw_payload.get("inn"),
            "phone": raw_payload.get("phone"),
            "email": raw_payload.get("email"),
            "telegram_id": raw_payload.get("telegram_id"),
            "telegram_username": raw_payload.get("telegram_username"),
            "birth_date": raw_payload.get("birth_date") or None,
            "registration_address": raw_payload.get("registration_address"),
            "passport_series_number": raw_payload.get("passport_series_number"),
            "passport_issued_by": raw_payload.get("passport_issued_by"),
            "passport_issue_date": raw_payload.get("passport_issue_date") or None,
            "passport_department_code": raw_payload.get("passport_department_code"),
            "bank_name": raw_payload.get("bank_name"),
            "bank_account": raw_payload.get("bank_account"),
            "bank_corr_account": raw_payload.get("bank_corr_account"),
            "bank_bik": raw_payload.get("bank_bik"),
            "bank_inn": raw_payload.get("bank_inn"),
            "bank_kpp": raw_payload.get("bank_kpp"),
        }
    )


def upsert_client_from_document_request_values(
    db: Session,
    values: dict[str, Any],
    *,
    overwrite_existing: bool = False,
) -> Client:
    client_values = extract_client_values_from_request(values)
    client = None
    if values.get("client_id"):
        client = db.get(Client, values["client_id"])
    if client is None and client_values.get("inn"):
        client = db.query(Client).filter(Client.inn == client_values["inn"]).first()
    if client is None and client_values.get("phone"):
        client = db.query(Client).filter(Client.phone == client_values["phone"]).first()
    if client is None:
        client = Client(**client_values)
        db.add(client)
        db.flush()
    else:
        for key, value in client_values.items():
            if value and (overwrite_existing or not getattr(client, key, None)):
                setattr(client, key, value)
    values["client_id"] = client.id
    return client


def client_has_visible_identity(client: Client | None) -> bool:
    return bool(
        client
        and (
            client.ru_name
            or client.full_name_ru
            or client.inn
            or client.phone
            or client.email
        )
    )


def document_request_values(obj: DocumentIssueRequest) -> dict[str, Any]:
    return {
        "client_id": obj.client_id,
        "client_type": obj.client_type,
        "payload_json": obj.payload_json,
    }


def apply_document_request_update(
    db: Session,
    obj: DocumentIssueRequest,
    payload: DocumentIssueRequestUpdate,
) -> DocumentIssueRequest:
    values = payload.model_dump(exclude_unset=True)
    if isinstance(values.get("payload_json"), dict):
        values["payload_json"] = {**(obj.payload_json or {}), **values["payload_json"]}
    for key, value in values.items():
        setattr(obj, key, value)

    if "payload_json" in values or not obj.client_id or "client_id" in values:
        current_values = document_request_values(obj)
        upsert_client_from_document_request_values(db, current_values, overwrite_existing=True)
        obj.client_id = current_values["client_id"]
    return obj


def ensure_deal_client_from_document_request(db: Session, deal: CfaDeal) -> bool:
    request = None
    if deal.document_request_id:
        request = db.get(DocumentIssueRequest, deal.document_request_id)
    if request is None:
        request = db.query(DocumentIssueRequest).filter(DocumentIssueRequest.deal_id == deal.id).first()
    if request is None:
        return False

    current_client = db.get(Client, deal.client_id) if deal.client_id else None
    if request.payload_json or request.client_id:
        values = document_request_values(request)
        client = upsert_client_from_document_request_values(db, values)
        request.client_id = values["client_id"]
        if deal.client_id != client.id or not client_has_visible_identity(current_client):
            deal.client_id = client.id
            return True
    return False


def document_request_deal_status(request: DocumentIssueRequest) -> str:
    return request.status or "documents_generated"


def document_request_amount(request: DocumentIssueRequest) -> Decimal:
    amount = request.full_payment_amount or request.total_amount or request.payment_amount or request.supplier_payment_equal
    return Decimal(amount or 0)


def sync_deal_from_document_request(
    db: Session,
    request: DocumentIssueRequest,
    client: Client,
    documents: dict[str, Any],
) -> CfaDeal:
    deal = None
    if request.deal_id:
        deal = db.get(CfaDeal, request.deal_id)
    if deal is None:
        deal = db.query(CfaDeal).filter(CfaDeal.document_request_id == request.id).first()
    if deal is None:
        deal = CfaDeal(
            deal_number=f"DOCREQ-{request.id}",
            client_id=client.id,
            document_request_id=request.id,
            created_at=request.created_at,
        )
        db.add(deal)

    deal.client_id = client.id
    deal.document_request_id = request.id
    deal.manager_id = request.manager_id
    deal.deal_direction = request.deal_type or "crypto"
    deal.client_type = request.client_type or "individual"
    deal.asset = request.crypto_asset or "USDT"
    deal.status = document_request_deal_status(request)
    deal.source_type = "document_request"
    deal.document_flow_type = request.document_package_type or "offer_crypto_individual"
    deal.contract_number = request.contract_number
    deal.contract_date = request.contract_date
    deal.payment_number = request.payment_number
    deal.payment_date = request.payment_date
    deal.full_payment_amount = request.full_payment_amount
    deal.amount_rub = document_request_amount(request)
    deal.supplier_payment_equal = request.supplier_payment_equal
    deal.agent_fee_amount = request.agent_fee_amount
    deal.agent_fee_percent = request.agent_fee_percent
    deal.currency = request.currency or "RUB"
    deal.wallet_address = request.wallet_address or payload_value(request, "wallet_address")
    deal.generated_documents_json = documents
    deal.required_action = "Ожидаем оплату"
    db.flush()
    request.deal_id = deal.id
    return deal


def build_deal_document_context(deal: CfaDeal, client: Client) -> dict[str, str]:
    return {
        "contract.number": str(deal.contract_number or ""),
        "contract.date": format_date(deal.contract_date),
        "payment.number": str(deal.payment_number or ""),
        "payment.date": format_date(deal.payment_date),
        "customer.ru.name": str(client.ru_name or client.full_name_ru or ""),
        "customer.inn": str(client.inn or ""),
        "customer.email": str(client.email or ""),
        "customer_account.payment_account": str(client.bank_account or ""),
        "customer_account.correspondent_account": str(client.bank_corr_account or ""),
        "customer_account.bic": str(client.bank_bik or ""),
        "customer_account.ru.name": str(client.bank_name or ""),
        "executor.ru.name": "",
        "paymentCustom.full_payment_amount": format_money(deal.full_payment_amount or deal.amount_rub, keep_cents=False),
        "paymentCustom.supplier_payment_equal": format_money(deal.supplier_payment_equal),
        "paymentCustom.agent_fee_amount": format_money(deal.agent_fee_amount),
        "paymentCustom.e_wallet": str(deal.wallet_address or ""),
    }


def render_template_to_pdf(template: DocumentTemplate, context: dict[str, str], target_dir: Path, filename_stem: str) -> tuple[Path, Path]:
    if not template.file_path:
        raise DocumentGenerationError("У шаблона не загружен DOCX-файл")
    variables = template_service.extract_variables_from_docx(template.file_path)
    missing = [variable for variable in variables if variable not in context or context[variable] in ("", None)]
    if missing:
        raise DocumentGenerationError("Не заполнены переменные шаблона: " + ", ".join(missing))
    docx_path = template_service.render_docx(template.file_path, context, target_dir)
    final_docx_path = target_dir / f"{filename_stem}.docx"
    if docx_path != final_docx_path:
        docx_path.replace(final_docx_path)
    unresolved = template_service.unresolved_variables_in_docx(final_docx_path)
    if unresolved:
        raise DocumentGenerationError("Не заполнены переменные шаблона: " + ", ".join(unresolved))
    try:
        pdf_path = template_service.convert_docx_to_pdf(final_docx_path, target_dir)
    except DocumentTemplateError as exc:
        raise DocumentGenerationError(str(exc)) from exc
    return final_docx_path, pdf_path


@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return Token(access_token=create_access_token(user.id))


@router.get("/auth/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/bot/users/{telegram_id}/connect-permission")
def bot_connect_permission(telegram_id: str, db: Session = Depends(get_db)) -> dict[str, bool]:
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    return {"allowed": bool(user and user.is_allowed_to_connect_bot)}


@router.post("/users", response_model=UserOut, dependencies=[Depends(require_roles("admin", "director"))])
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(**payload.model_dump(exclude={"password"}), password_hash=get_password_hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=list[UserOut], dependencies=[Depends(require_roles("admin", "director"))])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return db.query(User).order_by(User.id.desc()).all()


@router.get("/users/{user_id}", response_model=UserOut, dependencies=[Depends(require_roles("admin", "director"))])
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    return get_or_404(db, User, user_id)


@router.patch("/users/{user_id}", response_model=UserOut, dependencies=[Depends(require_roles("admin", "director"))])
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> User:
    user = get_or_404(db, User, user_id)
    values = payload.model_dump(exclude_unset=True)
    if "password" in values:
        user.password_hash = get_password_hash(values.pop("password"))
    for key, value in values.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204, dependencies=[Depends(require_roles("admin", "director"))])
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_or_404(db, User, user_id))
    db.commit()


@router.post("/agents", response_model=AgentOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def create_agent(payload: AgentCreate, db: Session = Depends(get_db)) -> Agent:
    obj = Agent(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/agents", response_model=list[AgentOut], dependencies=[Depends(require_roles("manager", "admin", "director"))])
def list_agents(db: Session = Depends(get_db)) -> list[Agent]:
    return db.query(Agent).order_by(Agent.id.desc()).all()


@router.get("/agents/{agent_id}", response_model=AgentOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def get_agent(agent_id: int, db: Session = Depends(get_db)) -> Agent:
    return get_or_404(db, Agent, agent_id)


@router.patch("/agents/{agent_id}", response_model=AgentOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def update_agent(agent_id: int, payload: AgentUpdate, db: Session = Depends(get_db)) -> Agent:
    obj = apply_update(get_or_404(db, Agent, agent_id), payload)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/agents/{agent_id}", status_code=204, dependencies=[Depends(require_roles("admin", "director"))])
def delete_agent(agent_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_or_404(db, Agent, agent_id))
    db.commit()


@router.post("/telegram-chats", response_model=TelegramChatOut)
def create_telegram_chat(
    payload: TelegramChatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("manager", "admin", "director")),
) -> TelegramChat:
    if not current_user.is_allowed_to_connect_bot and current_user.role not in {"admin", "director"}:
        raise HTTPException(status_code=403, detail="User is not allowed to connect bot")
    values = payload.model_dump()
    values["connected_by"] = values.get("connected_by") or current_user.id
    obj = TelegramChat(**values)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/telegram-chats", response_model=list[TelegramChatOut], dependencies=[Depends(require_roles("manager", "admin", "director"))])
def list_telegram_chats(db: Session = Depends(get_db)) -> list[TelegramChat]:
    return db.query(TelegramChat).order_by(TelegramChat.id.desc()).all()


@router.get("/telegram-chats/{chat_id}", response_model=TelegramChatOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def get_telegram_chat(chat_id: int, db: Session = Depends(get_db)) -> TelegramChat:
    return get_or_404(db, TelegramChat, chat_id)


@router.patch("/telegram-chats/{chat_id}", response_model=TelegramChatOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def update_telegram_chat(chat_id: int, payload: TelegramChatUpdate, db: Session = Depends(get_db)) -> TelegramChat:
    obj = apply_update(get_or_404(db, TelegramChat, chat_id), payload)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/telegram-chats/{chat_id}", status_code=204, dependencies=[Depends(require_roles("admin", "director"))])
def delete_telegram_chat(chat_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_or_404(db, TelegramChat, chat_id))
    db.commit()


@router.post("/bot/telegram-chats/{chat_id}/setup", response_model=TelegramChatOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def setup_telegram_chat(chat_id: int, payload: TelegramChatSetup, db: Session = Depends(get_db)) -> TelegramChat:
    chat = get_or_404(db, TelegramChat, chat_id)
    chat.chat_type = payload.chat_type
    chat.setup_status = "configured"
    chat.client_type = payload.client_type
    chat.deal_direction = payload.deal_direction
    chat.document_flow_type = resolve_document_flow_type(payload.client_type, payload.deal_direction)
    chat.default_manager_id = payload.default_manager_id
    chat.default_referral_mode = payload.referral_mode
    chat.default_referral_id = payload.default_referral_id
    chat.rate_mode = payload.rate_mode
    chat.notes = payload.notes
    db.commit()
    db.refresh(chat)
    return chat


@router.post("/clients", response_model=ClientOut)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)) -> Client:
    obj = Client(**prepare_client_values(payload.model_dump()))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/clients", response_model=list[ClientOut])
def list_clients(db: Session = Depends(get_db)) -> list[Client]:
    return db.query(Client).order_by(Client.id.desc()).all()


@router.get("/clients/{client_id}", response_model=ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)) -> Client:
    return get_or_404(db, Client, client_id)


@router.patch("/clients/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Client:
    ensure_staff_or_owner(db, current_user, client_id)
    obj = get_or_404(db, Client, client_id)
    values = payload.model_dump(exclude_unset=True)
    if current_user.role == "client":
        values.pop("responsible_manager_id", None)
        values.pop("referral_id", None)
        values.pop("telegram_chat_id", None)
        values["profile_status"] = "personal_data_submitted"
    for key, value in values.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/clients/{client_id}/approve-personal-data", response_model=ClientOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def approve_client_personal_data(client_id: int, db: Session = Depends(get_db)) -> Client:
    obj = get_or_404(db, Client, client_id)
    obj.profile_status = "personal_data_approved"
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/clients/{client_id}/approve-bank-details", response_model=ClientOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def approve_client_bank_details(client_id: int, db: Session = Depends(get_db)) -> Client:
    obj = get_or_404(db, Client, client_id)
    obj.profile_status = "bank_details_approved"
    db.query(ClientBankAccount).filter(ClientBankAccount.client_id == client_id).update({"status": "approved"})
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/clients/{client_id}", status_code=204, dependencies=[Depends(require_roles("admin", "director"))])
def delete_client(client_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_or_404(db, Client, client_id))
    db.commit()


@router.post("/client-bank-accounts", response_model=ClientBankAccountOut)
def create_bank_account(
    payload: ClientBankAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientBankAccount:
    ensure_staff_or_owner(db, current_user, payload.client_id)
    obj = ClientBankAccount(**payload.model_dump())
    db.add(obj)
    client = db.get(Client, payload.client_id)
    if client:
        client.profile_status = "bank_details_submitted"
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/client-bank-accounts", response_model=list[ClientBankAccountOut])
def list_bank_accounts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[ClientBankAccount]:
    query = db.query(ClientBankAccount).order_by(ClientBankAccount.id.desc())
    if current_user.role == "client":
        client = get_client_for_user(db, current_user)
        return query.filter(ClientBankAccount.client_id == client.id).all() if client else []
    return query.all()


@router.get("/client-bank-accounts/{account_id}", response_model=ClientBankAccountOut)
def get_bank_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientBankAccount:
    obj = get_or_404(db, ClientBankAccount, account_id)
    ensure_staff_or_owner(db, current_user, obj.client_id)
    return obj


@router.patch("/client-bank-accounts/{account_id}", response_model=ClientBankAccountOut)
def update_bank_account(
    account_id: int,
    payload: ClientBankAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClientBankAccount:
    obj = get_or_404(db, ClientBankAccount, account_id)
    ensure_staff_or_owner(db, current_user, obj.client_id)
    values = payload.model_dump(exclude_unset=True)
    if current_user.role == "client":
        values["status"] = "submitted"
    for key, value in values.items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/client-bank-accounts/{account_id}", status_code=204)
def delete_bank_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    obj = get_or_404(db, ClientBankAccount, account_id)
    ensure_staff_or_owner(db, current_user, obj.client_id)
    db.delete(obj)
    db.commit()


@router.post("/contracts", response_model=ContractOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)) -> Contract:
    obj = Contract(**payload.model_dump())
    db.add(obj)
    client = db.get(Client, payload.client_id)
    if client:
        client.profile_status = "contract_ready"
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/contracts", response_model=list[ContractOut])
def list_contracts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Contract]:
    query = db.query(Contract).order_by(Contract.id.desc())
    if current_user.role == "client":
        client = get_client_for_user(db, current_user)
        return query.filter(Contract.client_id == client.id).all() if client else []
    return query.all()


@router.get("/contracts/{contract_id}", response_model=ContractOut)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Contract:
    obj = get_or_404(db, Contract, contract_id)
    ensure_staff_or_owner(db, current_user, obj.client_id)
    return obj


@router.patch("/contracts/{contract_id}", response_model=ContractOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def update_contract(contract_id: int, payload: ContractUpdate, db: Session = Depends(get_db)) -> Contract:
    obj = apply_update(get_or_404(db, Contract, contract_id), payload)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/contracts/{contract_id}", status_code=204, dependencies=[Depends(require_roles("admin", "director"))])
def delete_contract(contract_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_or_404(db, Contract, contract_id))
    db.commit()


@router.post("/document-templates", response_model=DocumentTemplateOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def create_document_template(payload: DocumentTemplateCreate, db: Session = Depends(get_db)) -> DocumentTemplate:
    values = payload.model_dump()
    values["document_type"] = values.get("document_type") or values.get("template_type")
    obj = DocumentTemplate(**values)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/document-templates", response_model=list[DocumentTemplateOut], dependencies=[Depends(require_roles("manager", "admin", "director", "document_admin", "admin_assistant"))])
def list_document_templates(db: Session = Depends(get_db)) -> list[DocumentTemplate]:
    return db.query(DocumentTemplate).order_by(DocumentTemplate.updated_at.desc()).all()


@router.get("/document-templates/{template_id}", response_model=DocumentTemplateOut, dependencies=[Depends(require_roles("manager", "admin", "director", "document_admin", "admin_assistant"))])
def get_document_template(template_id: int, db: Session = Depends(get_db)) -> DocumentTemplate:
    return get_or_404(db, DocumentTemplate, template_id)


@router.patch("/document-templates/{template_id}", response_model=DocumentTemplateOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def update_document_template(
    template_id: int,
    payload: DocumentTemplateUpdate,
    db: Session = Depends(get_db),
) -> DocumentTemplate:
    obj = apply_update(get_or_404(db, DocumentTemplate, template_id), payload)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/document-templates/{template_id}", status_code=204, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def delete_document_template(template_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_or_404(db, DocumentTemplate, template_id))
    db.commit()


@router.post("/document-templates/{template_id}/upload", response_model=DocumentTemplateOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
async def upload_document_template(
    template_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentTemplate:
    obj = get_or_404(db, DocumentTemplate, template_id)
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx templates are supported")

    storage_path = Path(settings.storage_dir) / "document_templates" / str(template_id)
    storage_path.mkdir(parents=True, exist_ok=True)
    file_path = storage_path / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    variables = template_service.extract_variables_from_docx(file_path)
    obj.file_name = file.filename
    obj.original_file_name = file.filename
    obj.file_path = str(file_path)
    obj.file_mime_type = file.content_type
    obj.file_size = len(content)
    obj.variables_json = [{"key": variable} for variable in variables]
    obj.uploaded_by = current_user.id
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/document-templates/{template_id}/download", dependencies=[Depends(require_roles("manager", "admin", "director", "document_admin", "admin_assistant"))])
def download_document_template(template_id: int, db: Session = Depends(get_db)) -> FileResponse:
    obj = get_or_404(db, DocumentTemplate, template_id)
    if not obj.file_path or not Path(obj.file_path).exists():
        raise HTTPException(status_code=404, detail="Template file not found")
    return FileResponse(obj.file_path, filename=obj.file_name)


@router.post("/document-templates/{template_id}/extract-variables", response_model=TemplateVariablesOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def extract_document_template_variables(template_id: int, db: Session = Depends(get_db)) -> TemplateVariablesOut:
    obj = get_or_404(db, DocumentTemplate, template_id)
    variables = template_service.extract_variables_from_docx(obj.file_path) if obj.file_path else []
    obj.variables_json = [{"key": variable} for variable in variables]
    obj.missing_fields_json = []
    db.commit()
    return TemplateVariablesOut(variables=variables)


@router.post("/document-templates/{template_id}/test-render", response_model=TemplateTestRenderOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def test_render_document_template(
    template_id: int,
    payload: TemplateTestRenderRequest,
    db: Session = Depends(get_db),
) -> TemplateTestRenderOut:
    obj = get_or_404(db, DocumentTemplate, template_id)
    if not obj.file_path:
        raise HTTPException(status_code=400, detail="Upload .docx template before test render")
    generated_path = template_service.render_docx(
        obj.file_path,
        payload.context,
        Path(settings.storage_dir) / "generated_documents",
    )
    return TemplateTestRenderOut(
        generated_file_path=str(generated_path),
        variables_used=sorted(payload.context.keys()),
    )


@router.post("/referrals", response_model=ReferralOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def create_referral(payload: ReferralCreate, db: Session = Depends(get_db)) -> Referral:
    obj = Referral(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/referrals", response_model=list[ReferralOut], dependencies=[Depends(require_roles("manager", "admin", "director"))])
def list_referrals(db: Session = Depends(get_db)) -> list[Referral]:
    return db.query(Referral).order_by(Referral.id.desc()).all()


@router.get("/referrals/{referral_id}", response_model=ReferralOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def get_referral(referral_id: int, db: Session = Depends(get_db)) -> Referral:
    return get_or_404(db, Referral, referral_id)


@router.patch("/referrals/{referral_id}", response_model=ReferralOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def update_referral(referral_id: int, payload: ReferralUpdate, db: Session = Depends(get_db)) -> Referral:
    obj = apply_update(get_or_404(db, Referral, referral_id), payload)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/referrals/{referral_id}", status_code=204, dependencies=[Depends(require_roles("admin", "director"))])
def delete_referral(referral_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_or_404(db, Referral, referral_id))
    db.commit()


@router.post("/cfa-deals", response_model=CfaDealOut)
def create_deal(
    payload: CfaDealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CfaDeal:
    if current_user.role == "client":
        ensure_staff_or_owner(db, current_user, payload.client_id)
        payload.status = "new_request"
        payload.source_type = "client_group"
        payload.manager_id = None
        payload.referral_id = None
        payload.comment = None
    obj = CfaDeal(**payload.model_dump())
    calculate_profit_fields(obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/cfa-deals", response_model=list[CfaDealOut])
def list_deals(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[CfaDeal]:
    query = db.query(CfaDeal).order_by(CfaDeal.id.desc())
    if current_user.role == "client":
        client = get_client_for_user(db, current_user)
        return query.filter(CfaDeal.client_id == client.id).all() if client else []
    if current_user.role == "manager":
        return query.filter((CfaDeal.manager_id == current_user.id) | (CfaDeal.manager_id.is_(None))).all()
    return query.all()


@router.get("/cfa-deals/{deal_id}", response_model=CfaDealOut)
def get_deal(deal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> CfaDeal:
    deal = get_or_404(db, CfaDeal, deal_id)
    ensure_staff_or_owner(db, current_user, deal.client_id)
    return deal


@router.patch("/cfa-deals/{deal_id}", response_model=CfaDealOut)
def update_deal(
    deal_id: int,
    payload: CfaDealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CfaDeal:
    deal = get_or_404(db, CfaDeal, deal_id)
    ensure_staff_or_owner(db, current_user, deal.client_id)
    if current_user.role == "client":
        allowed = {"wallet_address"}
        payload = CfaDealUpdate(**{k: v for k, v in payload.model_dump(exclude_unset=True).items() if k in allowed})
    apply_update(deal, payload)
    calculate_profit_fields(deal)
    db.commit()
    db.refresh(deal)
    return deal


@router.delete("/cfa-deals/{deal_id}", status_code=204, dependencies=[Depends(require_roles("admin", "director"))])
def delete_deal(deal_id: int, db: Session = Depends(get_db)) -> None:
    db.delete(get_or_404(db, CfaDeal, deal_id))
    db.commit()


@router.post("/cfa-deals/{deal_id}/status", response_model=CfaDealOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def update_deal_status(
    deal_id: int,
    payload: DealStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CfaDeal:
    deal = get_or_404(db, CfaDeal, deal_id)
    old_status = deal.status
    deal.status = payload.status
    if payload.status == "completed":
        deal.completed_at = datetime.now(timezone.utc)
    db.add(CfaDealStatusHistory(deal_id=deal.id, old_status=old_status, new_status=payload.status, changed_by=current_user.id, comment=payload.comment))
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/cfa-deals/{deal_id}/rate", response_model=CfaDealOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def update_deal_rate(deal_id: int, payload: DealRateUpdate, db: Session = Depends(get_db)) -> CfaDeal:
    deal = apply_update(get_or_404(db, CfaDeal, deal_id), payload)
    if deal.rate_mode == "cb_plus_percent" and deal.cb_rate_value and deal.markup_percent:
        deal.client_rate = Decimal(deal.cb_rate_value) * (Decimal(1) + Decimal(deal.markup_percent) / Decimal(100))
    calculate_profit_fields(deal)
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/cfa-deals/{deal_id}/referral", response_model=CfaDealOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def update_deal_referral(deal_id: int, payload: DealReferralUpdate, db: Session = Depends(get_db)) -> CfaDeal:
    deal = apply_update(get_or_404(db, CfaDeal, deal_id), payload)
    calculate_profit_fields(deal)
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/cfa-deals/{deal_id}/wallet", response_model=CfaDealOut)
def update_deal_wallet(
    deal_id: int,
    payload: DealWalletUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CfaDeal:
    deal = get_or_404(db, CfaDeal, deal_id)
    ensure_staff_or_owner(db, current_user, deal.client_id)
    deal.wallet_address = payload.wallet_address
    deal.wallet_added_at = datetime.now(timezone.utc)
    if deal.status == "wallet_required":
        deal.status = "wallet_submitted"
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/cfa-deals/{deal_id}/actual-close-rate", response_model=CfaDealOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def update_actual_close_rate(deal_id: int, payload: DealActualCloseRateUpdate, db: Session = Depends(get_db)) -> CfaDeal:
    deal = get_or_404(db, CfaDeal, deal_id)
    deal.actual_close_rate = payload.actual_close_rate
    calculate_profit_fields(deal)
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/cfa-deals/{deal_id}/calculate-profit", response_model=CfaDealOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def calculate_deal_profit(deal_id: int, db: Session = Depends(get_db)) -> CfaDeal:
    deal = get_or_404(db, CfaDeal, deal_id)
    calculate_profit_fields(deal)
    db.commit()
    db.refresh(deal)
    return deal


@router.post("/cfa-deals/{deal_id}/documents", response_model=CfaDealDocumentOut)
def create_deal_document(
    deal_id: int,
    payload: CfaDealDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CfaDealDocument:
    deal = get_or_404(db, CfaDeal, deal_id)
    ensure_staff_or_owner(db, current_user, deal.client_id)
    if current_user.role == "client" and payload.status != "signed":
        raise HTTPException(status_code=403, detail="Client can upload signed documents only")
    values = payload.model_dump()
    values["deal_id"] = deal_id
    values["uploaded_by"] = values.get("uploaded_by") or current_user.id
    obj = CfaDealDocument(**values)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/cfa-deals/{deal_id}/documents/upload", response_model=CfaDealDocumentOut)
async def upload_deal_document(
    deal_id: int,
    document_type: str,
    status_value: str = "signed",
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CfaDealDocument:
    deal = get_or_404(db, CfaDeal, deal_id)
    ensure_staff_or_owner(db, current_user, deal.client_id)
    if current_user.role == "client" and status_value != "signed":
        raise HTTPException(status_code=403, detail="Client can upload signed documents only")
    storage_path = Path(settings.storage_dir) / "deal-documents" / str(deal_id)
    storage_path.mkdir(parents=True, exist_ok=True)
    file_path = storage_path / file.filename
    file_path.write_bytes(await file.read())
    obj = CfaDealDocument(
        deal_id=deal_id,
        document_type=document_type,
        status=status_value,
        file_path=str(file_path) if status_value != "signed" else None,
        signed_file_path=str(file_path) if status_value == "signed" else None,
        uploaded_by=current_user.id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/cfa-deals/{deal_id}/documents", response_model=list[CfaDealDocumentOut])
def list_deal_documents(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CfaDealDocument]:
    deal = get_or_404(db, CfaDeal, deal_id)
    ensure_staff_or_owner(db, current_user, deal.client_id)
    return db.query(CfaDealDocument).filter(CfaDealDocument.deal_id == deal_id).order_by(CfaDealDocument.id.desc()).all()


@router.get("/cfa-deals/{deal_id}/history", response_model=list[CfaDealStatusHistoryOut])
def get_deal_history(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CfaDealStatusHistory]:
    deal = get_or_404(db, CfaDeal, deal_id)
    ensure_staff_or_owner(db, current_user, deal.client_id)
    if current_user.role == "client":
        return []
    return db.query(CfaDealStatusHistory).filter(CfaDealStatusHistory.deal_id == deal_id).order_by(CfaDealStatusHistory.id.desc()).all()


@router.get("/deals", response_model=list[CfaDealOut])
def list_active_deals(db: Session = Depends(get_db)) -> list[CfaDeal]:
    deals = db.query(CfaDeal).order_by(CfaDeal.id.desc()).all()
    changed = False
    for deal in deals:
        changed = ensure_deal_client_from_document_request(db, deal) or changed
    if changed:
        db.commit()
        for deal in deals:
            db.refresh(deal)
    return deals


@router.get("/deals/{deal_id}", response_model=CfaDealOut)
def get_active_deal(deal_id: int, db: Session = Depends(get_db)) -> CfaDeal:
    deal = get_or_404(db, CfaDeal, deal_id)
    if ensure_deal_client_from_document_request(db, deal):
        db.commit()
        db.refresh(deal)
    return deal


@router.patch("/deals/{deal_id}", response_model=CfaDealOut)
def update_active_deal(deal_id: int, payload: CfaDealUpdate, db: Session = Depends(get_db)) -> CfaDeal:
    deal = get_or_404(db, CfaDeal, deal_id)
    allowed = {"status", "payment_received_amount", "payment_received_at", "comment", "manager_id"}
    values = {key: value for key, value in payload.model_dump(exclude_unset=True).items() if key in allowed}
    for key, value in values.items():
        setattr(deal, key, value)
    if values.get("payment_received_amount") is not None:
        deal.client_payment_amount_rub = values["payment_received_amount"]
    if values.get("payment_received_at") is not None:
        deal.client_payment_received_at = values["payment_received_at"]
    db.commit()
    db.refresh(deal)
    return deal


@router.get("/liquidity-purchases", response_model=list[LiquidityPurchaseLotOut])
def list_liquidity_purchase_lots(db: Session = Depends(get_db)) -> list[LiquidityPurchaseLot]:
    return db.query(LiquidityPurchaseLot).order_by(LiquidityPurchaseLot.id.desc()).all()


@router.post("/liquidity-purchases", response_model=LiquidityPurchaseLotOut)
def create_liquidity_purchase_lot(payload: LiquidityPurchaseLotCreate, db: Session = Depends(get_db)) -> LiquidityPurchaseLot:
    values = prepare_liquidity_lot_values(payload.model_dump())
    lot = LiquidityPurchaseLot(**values)
    refresh_liquidity_lot_status(lot)
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@router.get("/liquidity-purchases/{lot_id}", response_model=LiquidityPurchaseLotOut)
def get_liquidity_purchase_lot(lot_id: int, db: Session = Depends(get_db)) -> LiquidityPurchaseLot:
    return get_or_404(db, LiquidityPurchaseLot, lot_id)


@router.patch("/liquidity-purchases/{lot_id}", response_model=LiquidityPurchaseLotOut)
def update_liquidity_purchase_lot(lot_id: int, payload: LiquidityPurchaseLotUpdate, db: Session = Depends(get_db)) -> LiquidityPurchaseLot:
    lot = get_or_404(db, LiquidityPurchaseLot, lot_id)
    if lot.status == "closed":
        raise HTTPException(status_code=400, detail="Closed liquidity lots cannot be edited")
    values = payload.model_dump(exclude_unset=True)
    has_allocations = db.query(LiquidityLotAllocation.id).filter(LiquidityLotAllocation.lot_id == lot.id).first() is not None
    if has_allocations and "asset" in values and values["asset"] != lot.asset:
        raise HTTPException(status_code=400, detail="Cannot change asset after lot usage")
    for key, value in values.items():
        setattr(lot, key, value)
    if "purchase_amount_rub" in values or "purchase_rate" in values or "purchased_asset_volume" in values:
        if "purchased_asset_volume" not in values:
            lot.purchased_asset_volume = calculate_liquidity_volume(Decimal(lot.purchase_amount_rub), Decimal(lot.purchase_rate))
        lot.remaining_asset_volume = Decimal(lot.purchased_asset_volume) - Decimal(lot.used_asset_volume or 0)
        if lot.remaining_asset_volume < 0:
            raise HTTPException(status_code=400, detail="Purchased volume cannot be less than already used volume")
    refresh_liquidity_lot_status(lot)
    db.commit()
    db.refresh(lot)
    return lot


@router.delete("/liquidity-purchases/{lot_id}", status_code=204)
def delete_liquidity_purchase_lot(lot_id: int, db: Session = Depends(get_db)) -> None:
    lot = get_or_404(db, LiquidityPurchaseLot, lot_id)
    used = db.query(LiquidityLotAllocation.id).filter(LiquidityLotAllocation.lot_id == lot.id).first()
    if used:
        raise HTTPException(status_code=409, detail="Cannot delete a liquidity lot that has allocations")
    db.delete(lot)
    db.commit()


@router.get("/liquidity-purchases/{lot_id}/allocations", response_model=list[LiquidityLotAllocationOut])
def list_liquidity_purchase_lot_allocations(lot_id: int, db: Session = Depends(get_db)) -> list[LiquidityLotAllocation]:
    get_or_404(db, LiquidityPurchaseLot, lot_id)
    return db.query(LiquidityLotAllocation).filter(LiquidityLotAllocation.lot_id == lot_id).order_by(LiquidityLotAllocation.id.desc()).all()


@router.post("/liquidity-purchases/{lot_id}/allocate", response_model=LiquidityAllocationResult)
def allocate_liquidity_lot_to_deal(
    lot_id: int,
    payload: LiquidityLotAllocateRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    lot = get_or_404(db, LiquidityPurchaseLot, lot_id)
    deal = get_or_404(db, CfaDeal, payload.deal_id)
    target_volume = deal_liquidity_volume(deal)
    already_allocated = allocated_deal_volume(db, deal.id, deal.asset or "USDT")
    if already_allocated + payload.asset_volume > target_volume:
        raise HTTPException(status_code=400, detail="Allocation would exceed deal asset volume")
    allocation = allocate_from_lot(db, lot, deal, payload.asset_volume, payload.comment)
    db.flush()
    finalize_deal_liquidity_close(db, deal, target_volume, comment=payload.comment)
    db.commit()
    db.refresh(deal)
    db.refresh(allocation)
    return {"deal": deal, "allocations": [allocation]}


@router.get("/deals/{deal_id}/liquidity-allocations", response_model=list[LiquidityLotAllocationOut])
def list_deal_liquidity_allocations(deal_id: int, db: Session = Depends(get_db)) -> list[LiquidityLotAllocation]:
    get_or_404(db, CfaDeal, deal_id)
    return db.query(LiquidityLotAllocation).filter(LiquidityLotAllocation.deal_id == deal_id).order_by(LiquidityLotAllocation.id.desc()).all()


@router.post("/deals/{deal_id}/close-with-liquidity", response_model=LiquidityAllocationResult)
def close_deal_with_liquidity(
    deal_id: int,
    payload: LiquidityAllocationRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    deal = get_or_404(db, CfaDeal, deal_id)
    target_volume = deal_liquidity_volume(deal, payload.asset_volume)
    allocations = auto_allocate_deal_liquidity(db, deal, target_volume, payload.comment)
    db.flush()
    finalize_deal_liquidity_close(db, deal, target_volume, comment=payload.comment)
    db.commit()
    db.refresh(deal)
    for allocation in allocations:
        db.refresh(allocation)
    return {"deal": deal, "allocations": allocations}


@router.get("/document-requests", response_model=list[DocumentIssueRequestOut])
def list_document_requests(db: Session = Depends(get_db)) -> list[DocumentIssueRequest]:
    return db.query(DocumentIssueRequest).order_by(DocumentIssueRequest.id.desc()).all()


@router.post("/document-requests", response_model=DocumentIssueRequestOut)
def create_document_request(payload: DocumentIssueRequestCreate, db: Session = Depends(get_db)) -> DocumentIssueRequest:
    values = prepare_document_request_values(payload.model_dump())
    if values.get("payload_json") or not values.get("client_id"):
        upsert_client_from_document_request_values(db, values)
    obj = DocumentIssueRequest(**values)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/document-requests/{request_id}", response_model=DocumentIssueRequestOut)
def get_document_request(request_id: int, db: Session = Depends(get_db)) -> DocumentIssueRequest:
    return get_or_404(db, DocumentIssueRequest, request_id)


@router.patch("/document-requests/{request_id}", response_model=DocumentIssueRequestOut)
def update_document_request(
    request_id: int,
    payload: DocumentIssueRequestUpdate,
    db: Session = Depends(get_db),
) -> DocumentIssueRequest:
    obj = apply_document_request_update(db, get_or_404(db, DocumentIssueRequest, request_id), payload)
    deal = None
    if obj.deal_id:
        deal = db.get(CfaDeal, obj.deal_id)
    if deal is None:
        deal = db.query(CfaDeal).filter(CfaDeal.document_request_id == obj.id).first()
    if deal and obj.client_id:
        client = get_or_404(db, Client, obj.client_id)
        sync_deal_from_document_request(db, obj, client, obj.generated_documents_json or deal.generated_documents_json or {})
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/document-requests/{request_id}", status_code=204)
def delete_document_request(request_id: int, db: Session = Depends(get_db)) -> None:
    obj = get_or_404(db, DocumentIssueRequest, request_id)
    linked_deal = obj.deal_id or db.query(CfaDeal.id).filter(CfaDeal.document_request_id == obj.id).first()
    if linked_deal:
        raise HTTPException(status_code=409, detail="Cannot delete a request that has already been converted to a deal")
    db.delete(obj)
    db.commit()


@router.post("/document-requests/{request_id}/generate-documents")
def generate_document_request_documents(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    if current_user and current_user.role not in DOCUMENT_ISSUER_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    obj = get_or_404(db, DocumentIssueRequest, request_id)
    if not obj.client_id:
        raise HTTPException(status_code=400, detail="К заявке не привязан клиент")
    client = get_or_404(db, Client, obj.client_id)
    try:
        documents = generate_request_documents(obj, client)
    except DocumentGenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    obj.generated_documents_json = documents
    deal = sync_deal_from_document_request(db, obj, client, documents)
    db.query(GeneratedDocument).filter(GeneratedDocument.issue_request_id == obj.id).delete(synchronize_session=False)
    for document_key, document in documents.items():
        db.add(
            GeneratedDocument(
                deal_id=deal.id,
                issue_request_id=obj.id,
                document_type=document_key,
                file_name=document["file_name"],
                file_path=document["file_path"],
                status="issued_pdf",
                generated_by_user_id=current_user.id if current_user else None,
                issued_by_user_id=current_user.id if current_user else None,
            )
        )
    db.commit()
    db.refresh(obj)
    db.refresh(deal)
    return {"documents": documents, "deal_id": deal.id}


@router.get("/document-requests/{request_id}/documents/{document_key}/download")
def download_document_request_document(
    request_id: int,
    document_key: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    obj = get_or_404(db, DocumentIssueRequest, request_id)
    if document_key not in DOCUMENT_KEYS:
        raise HTTPException(status_code=404, detail="Document key not found")
    documents = obj.generated_documents_json or {}
    document = documents.get(document_key)
    if not document:
        raise HTTPException(status_code=404, detail="Document has not been generated")
    file_path = Path(document["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Generated file not found")
    return FileResponse(file_path, filename=document["file_name"], media_type=document.get("mime_type") or "application/pdf")


@router.get("/document-issue-requests", response_model=list[DocumentIssueRequestOut], dependencies=[Depends(require_roles("manager", "admin", "director", "document_admin", "admin_assistant"))])
def list_document_issue_requests(db: Session = Depends(get_db)) -> list[DocumentIssueRequest]:
    return db.query(DocumentIssueRequest).order_by(DocumentIssueRequest.id.desc()).all()


@router.post("/deals/{deal_id}/document-issue-requests", response_model=DocumentIssueRequestOut)
def create_document_issue_request(
    deal_id: int,
    payload: DocumentIssueRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentIssueRequest:
    deal = get_or_404(db, CfaDeal, deal_id)
    ensure_staff_or_owner(db, current_user, deal.client_id)
    obj = DocumentIssueRequest(
        deal_id=deal_id,
        requested_by_user_id=current_user.id,
        requested_by_role=current_user.role,
        request_source=payload.request_source,
        request_type=payload.request_type,
        status="requested",
        comment=payload.comment,
    )
    deal.required_action = "Ожидает проверки и выпуска документов"
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/document-issue-requests/{request_id}", response_model=DocumentIssueRequestOut, dependencies=[Depends(require_roles("manager", "admin", "director", "document_admin", "admin_assistant"))])
def get_document_issue_request(request_id: int, db: Session = Depends(get_db)) -> DocumentIssueRequest:
    return get_or_404(db, DocumentIssueRequest, request_id)


@router.patch("/document-issue-requests/{request_id}", response_model=DocumentIssueRequestOut, dependencies=[Depends(require_roles("admin", "director", "document_admin", "admin_assistant"))])
def update_document_issue_request(
    request_id: int,
    payload: DocumentIssueRequestUpdate,
    db: Session = Depends(get_db),
) -> DocumentIssueRequest:
    obj = apply_update(get_or_404(db, DocumentIssueRequest, request_id), payload)
    db.commit()
    db.refresh(obj)
    return obj


def transition_issue_request(
    request_id: int,
    status_value: str,
    db: Session,
    current_user: User,
    correction_comment: str | None = None,
) -> DocumentIssueRequest:
    obj = get_or_404(db, DocumentIssueRequest, request_id)
    obj.status = status_value
    if status_value in {"in_review", "needs_correction", "approved_for_generation"}:
        obj.reviewed_by_user_id = current_user.id
    if status_value == "issued_to_client":
        obj.issued_by_user_id = current_user.id
    if correction_comment:
        obj.correction_comment = correction_comment
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/document-issue-requests/{request_id}/take-in-review", response_model=DocumentIssueRequestOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def take_issue_request_in_review(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DocumentIssueRequest:
    return transition_issue_request(request_id, "in_review", db, current_user)


@router.post("/document-issue-requests/{request_id}/needs-correction", response_model=DocumentIssueRequestOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def issue_request_needs_correction(request_id: int, payload: DocumentIssueRequestUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DocumentIssueRequest:
    return transition_issue_request(request_id, "needs_correction", db, current_user, payload.correction_comment)


@router.post("/document-issue-requests/{request_id}/approve", response_model=DocumentIssueRequestOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def approve_issue_request(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DocumentIssueRequest:
    return transition_issue_request(request_id, "approved_for_generation", db, current_user)


@router.post("/document-issue-requests/{request_id}/generate", response_model=DocumentIssueRequestOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def generate_issue_request_documents(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DocumentIssueRequest:
    obj = get_or_404(db, DocumentIssueRequest, request_id)
    deal = get_or_404(db, CfaDeal, obj.deal_id)
    client = get_or_404(db, Client, deal.client_id)
    matches = find_matching_document_templates(db, deal, obj.request_type, DocumentTemplate)
    if matches and not obj.selected_template_id:
        obj.selected_template_id = matches[0].id
    template = get_or_404(db, DocumentTemplate, obj.selected_template_id) if obj.selected_template_id else (matches[0] if matches else None)
    if template is None:
        raise HTTPException(status_code=400, detail="Не найден активный DOCX-шаблон для генерации документа")
    target_dir = Path(settings.storage_dir) / "generated_documents" / f"issue_request_{obj.id}"
    target_dir.mkdir(parents=True, exist_ok=True)
    filename_stem = f"{deal.deal_number}-{obj.request_type}"
    try:
        source_docx_path, pdf_path = render_template_to_pdf(template, build_deal_document_context(deal, client), target_dir, filename_stem)
    except DocumentGenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    generated = GeneratedDocument(
        deal_id=deal.id,
        template_id=obj.selected_template_id,
        issue_request_id=obj.id,
        document_type=obj.request_type,
        file_name=pdf_path.name,
        file_path=str(pdf_path),
        status="issued_pdf",
        generated_by_user_id=current_user.id,
        issued_by_user_id=current_user.id,
    )
    db.add(generated)
    db.flush()
    obj.generated_document_id = generated.id
    obj.generated_documents_json = {
        obj.request_type: {
            "title": template.name,
            "file_name": pdf_path.name,
            "file_path": str(pdf_path),
            "mime_type": "application/pdf",
            "source_docx_file_path": str(source_docx_path),
            "download_url": f"/generated-documents/{generated.id}/download",
        }
    }
    obj.status = "issued_to_client"
    obj.issued_by_user_id = current_user.id
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/generated-documents/{document_id}/download", dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def download_generated_document(document_id: int, db: Session = Depends(get_db)) -> FileResponse:
    document = get_or_404(db, GeneratedDocument, document_id)
    file_path = Path(document.file_path or "")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Generated PDF not found")
    return FileResponse(file_path, filename=document.file_name or file_path.name, media_type="application/pdf")


@router.post("/document-issue-requests/{request_id}/issue-to-client", response_model=DocumentIssueRequestOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def issue_documents_to_client(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DocumentIssueRequest:
    return transition_issue_request(request_id, "issued_to_client", db, current_user)
