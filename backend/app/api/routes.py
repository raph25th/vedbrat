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
from app.deps import ensure_staff_or_owner, get_client_for_user, get_current_user, require_roles
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
from app.services.document_templates import DocumentTemplateService

router = APIRouter()
ModelT = TypeVar("ModelT")
template_service = DocumentTemplateService()
DOCUMENT_ISSUER_ROLES = ("director", "document_admin", "admin_assistant")


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


@router.get("/document-requests", response_model=list[DocumentIssueRequestOut])
def list_document_requests(db: Session = Depends(get_db)) -> list[DocumentIssueRequest]:
    return db.query(DocumentIssueRequest).order_by(DocumentIssueRequest.id.desc()).all()


@router.post("/document-requests", response_model=DocumentIssueRequestOut)
def create_document_request(payload: DocumentIssueRequestCreate, db: Session = Depends(get_db)) -> DocumentIssueRequest:
    values = prepare_document_request_values(payload.model_dump())
    if not values.get("client_id"):
        client_values = extract_client_values_from_request(values)
        client = None
        if client_values.get("inn"):
            client = db.query(Client).filter(Client.inn == client_values["inn"]).first()
        if client is None and client_values.get("phone"):
            client = db.query(Client).filter(Client.phone == client_values["phone"]).first()
        if client is None:
            client = Client(**client_values)
            db.add(client)
            db.flush()
        else:
            for key, value in client_values.items():
                if value and not getattr(client, key, None):
                    setattr(client, key, value)
        values["client_id"] = client.id
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
    obj = apply_update(get_or_404(db, DocumentIssueRequest, request_id), payload)
    db.commit()
    db.refresh(obj)
    return obj


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
    matches = find_matching_document_templates(db, deal, obj.request_type, DocumentTemplate)
    if matches and not obj.selected_template_id:
        obj.selected_template_id = matches[0].id
    generated = GeneratedDocument(
        deal_id=deal.id,
        template_id=obj.selected_template_id,
        issue_request_id=obj.id,
        document_type=obj.request_type,
        file_name=f"{deal.deal_number}-{obj.request_type}.docx",
        file_path=str(Path(settings.storage_dir) / "generated_documents" / f"{deal.deal_number}-{obj.request_type}.docx"),
        status="generated",
        generated_by_user_id=current_user.id,
    )
    db.add(generated)
    db.flush()
    obj.generated_document_id = generated.id
    obj.status = "generated"
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/document-issue-requests/{request_id}/issue-to-client", response_model=DocumentIssueRequestOut, dependencies=[Depends(require_roles(*DOCUMENT_ISSUER_ROLES))])
def issue_documents_to_client(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> DocumentIssueRequest:
    return transition_issue_request(request_id, "issued_to_client", db, current_user)
