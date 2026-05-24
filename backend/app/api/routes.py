from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, TypeVar

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
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
    TelegramChatUpdate,
    Token,
    UserCreate,
    UserOut,
    UserUpdate,
)

router = APIRouter()
ModelT = TypeVar("ModelT")


def apply_update(obj: Any, payload: Any) -> Any:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)
    return obj


def get_or_404(db: Session, model: type[ModelT], obj_id: int) -> ModelT:
    obj = db.get(model, obj_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return obj


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


@router.post("/clients", response_model=ClientOut, dependencies=[Depends(require_roles("manager", "admin", "director"))])
def create_client(payload: ClientCreate, db: Session = Depends(get_db)) -> Client:
    obj = Client(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/clients", response_model=list[ClientOut])
def list_clients(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[Client]:
    if current_user.role == "client":
        client = get_client_for_user(db, current_user)
        return [client] if client else []
    return db.query(Client).order_by(Client.id.desc()).all()


@router.get("/clients/{client_id}", response_model=ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Client:
    ensure_staff_or_owner(db, current_user, client_id)
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
