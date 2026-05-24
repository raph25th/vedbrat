from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr


CLIENT_STATUSES = [
    "empty",
    "personal_data_started",
    "personal_data_submitted",
    "personal_data_approved",
    "bank_details_submitted",
    "bank_details_approved",
    "contract_ready",
    "contract_signed",
    "active",
]

CFA_DEAL_STATUSES = [
    "new_request",
    "client_data_required",
    "client_data_submitted",
    "client_data_approved",
    "bank_details_required",
    "bank_details_submitted",
    "bank_details_approved",
    "documents_requested",
    "documents_generated",
    "waiting_for_signature",
    "documents_signed",
    "waiting_for_client_payment",
    "client_payment_received",
    "rate_required",
    "rate_fixed",
    "wallet_required",
    "wallet_submitted",
    "ready_for_execution",
    "executed",
    "report_generated",
    "waiting_report_signature",
    "report_signed",
    "completed",
    "cancelled",
    "needs_correction",
]


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserBase(BaseModel):
    name: str
    email: EmailStr
    telegram_id: str | None = None
    role: str = "client"
    is_allowed_to_connect_bot: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    telegram_id: str | None = None
    role: str | None = None
    is_allowed_to_connect_bot: bool | None = None
    password: str | None = None


class UserOut(UserBase, OrmModel):
    id: int
    created_at: datetime


class AgentBase(BaseModel):
    name: str
    default_referral_fee_type: str | None = None
    default_referral_fee_value: Decimal | None = None
    default_referral_fee_base: str | None = None
    comment: str | None = None
    status: str = "active"


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: str | None = None
    default_referral_fee_type: str | None = None
    default_referral_fee_value: Decimal | None = None
    default_referral_fee_base: str | None = None
    comment: str | None = None
    status: str | None = None


class AgentOut(AgentBase, OrmModel):
    id: int


class ReferralBase(BaseModel):
    name: str
    type: str | None = None
    default_fee_type: str = "percent"
    default_fee_base: str = "client_amount_rub"
    default_fee_value: Decimal = 0
    comment: str | None = None
    status: str = "active"


class ReferralCreate(ReferralBase):
    pass


class ReferralUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    default_fee_type: str | None = None
    default_fee_base: str | None = None
    default_fee_value: Decimal | None = None
    comment: str | None = None
    status: str | None = None


class ReferralOut(ReferralBase, OrmModel):
    id: int


class TelegramChatBase(BaseModel):
    telegram_chat_id: str
    title: str
    chat_type: str
    default_client_id: int | None = None
    agent_id: int | None = None
    responsible_manager_id: int | None = None
    connected_by: int | None = None


class TelegramChatCreate(TelegramChatBase):
    pass


class TelegramChatUpdate(BaseModel):
    telegram_chat_id: str | None = None
    title: str | None = None
    chat_type: str | None = None
    default_client_id: int | None = None
    agent_id: int | None = None
    responsible_manager_id: int | None = None
    connected_by: int | None = None


class TelegramChatOut(TelegramChatBase, OrmModel):
    id: int
    created_at: datetime


class ClientBase(BaseModel):
    full_name_ru: str
    full_name_en: str | None = None
    inn: str | None = None
    citizenship: str | None = None
    tax_residency: str | None = None
    birth_date: date | None = None
    birth_place: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    passport_number: str | None = None
    passport_issue_date: date | None = None
    passport_issued_by: str | None = None
    passport_department_code: str | None = None
    registration_address: str | None = None
    profile_status: str = "empty"
    responsible_manager_id: int | None = None
    telegram_chat_id: int | None = None
    referral_id: int | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    full_name_ru: str | None = None
    full_name_en: str | None = None
    inn: str | None = None
    citizenship: str | None = None
    tax_residency: str | None = None
    birth_date: date | None = None
    birth_place: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    passport_number: str | None = None
    passport_issue_date: date | None = None
    passport_issued_by: str | None = None
    passport_department_code: str | None = None
    registration_address: str | None = None
    profile_status: str | None = None
    responsible_manager_id: int | None = None
    telegram_chat_id: int | None = None
    referral_id: int | None = None


class ClientOut(ClientBase, OrmModel):
    id: int
    created_at: datetime
    updated_at: datetime


class ClientBankAccountBase(BaseModel):
    client_id: int
    recipient_name: str
    bank_name: str
    account_number: str
    corr_account: str | None = None
    bic: str | None = None
    bank_inn: str | None = None
    bank_kpp: str | None = None
    payment_purpose: str | None = None
    is_default: bool = False
    status: str = "submitted"


class ClientBankAccountCreate(ClientBankAccountBase):
    pass


class ClientBankAccountUpdate(BaseModel):
    recipient_name: str | None = None
    bank_name: str | None = None
    account_number: str | None = None
    corr_account: str | None = None
    bic: str | None = None
    bank_inn: str | None = None
    bank_kpp: str | None = None
    payment_purpose: str | None = None
    is_default: bool | None = None
    status: str | None = None


class ClientBankAccountOut(ClientBankAccountBase, OrmModel):
    id: int
    created_at: datetime


class ContractBase(BaseModel):
    client_id: int
    contract_number: str
    contract_date: date
    status: str = "draft"
    file_path: str | None = None
    signed_file_path: str | None = None


class ContractCreate(ContractBase):
    pass


class ContractUpdate(BaseModel):
    contract_number: str | None = None
    contract_date: date | None = None
    status: str | None = None
    file_path: str | None = None
    signed_file_path: str | None = None


class ContractOut(ContractBase, OrmModel):
    id: int
    created_at: datetime


class CfaDealBase(BaseModel):
    deal_number: str
    client_id: int
    contract_id: int | None = None
    bank_account_id: int | None = None
    manager_id: int | None = None
    telegram_chat_id: int | None = None
    agent_id: int | None = None
    referral_id: int | None = None
    source_type: str = "manual_admin"
    status: str = "new_request"
    required_action: str | None = None
    amount_rub: Decimal = 0
    rate_mode: str = "manual_fixed"
    cb_rate_date: date | None = None
    cb_rate_value: Decimal | None = None
    markup_percent: Decimal | None = None
    client_rate: Decimal | None = None
    client_asset_amount: Decimal | None = None
    wallet_address: str | None = None
    referral_fee_type: str | None = None
    referral_fee_base: str | None = None
    referral_fee_value: Decimal | None = None
    referral_fee_rub: Decimal | None = None
    referral_fee_usdt: Decimal | None = None
    actual_close_rate: Decimal | None = None
    actual_asset_amount: Decimal | None = None
    gross_profit_usdt: Decimal | None = None
    gross_profit_rub: Decimal | None = None
    net_profit_usdt: Decimal | None = None
    net_profit_rub: Decimal | None = None
    client_payment_status: str = "not_received"
    client_payment_amount_rub: Decimal | None = None
    comment: str | None = None


class CfaDealCreate(CfaDealBase):
    pass


class CfaDealUpdate(BaseModel):
    contract_id: int | None = None
    bank_account_id: int | None = None
    manager_id: int | None = None
    telegram_chat_id: int | None = None
    agent_id: int | None = None
    referral_id: int | None = None
    source_type: str | None = None
    status: str | None = None
    required_action: str | None = None
    amount_rub: Decimal | None = None
    rate_mode: str | None = None
    cb_rate_date: date | None = None
    cb_rate_value: Decimal | None = None
    markup_percent: Decimal | None = None
    client_rate: Decimal | None = None
    client_asset_amount: Decimal | None = None
    wallet_address: str | None = None
    referral_fee_type: str | None = None
    referral_fee_base: str | None = None
    referral_fee_value: Decimal | None = None
    referral_fee_rub: Decimal | None = None
    referral_fee_usdt: Decimal | None = None
    actual_close_rate: Decimal | None = None
    actual_asset_amount: Decimal | None = None
    client_payment_status: str | None = None
    client_payment_amount_rub: Decimal | None = None
    comment: str | None = None


class CfaDealOut(CfaDealBase, OrmModel):
    id: int
    wallet_added_at: datetime | None = None
    client_payment_received_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class DealStatusUpdate(BaseModel):
    status: str
    comment: str | None = None


class DealRateUpdate(BaseModel):
    rate_mode: str | None = None
    cb_rate_date: date | None = None
    cb_rate_value: Decimal | None = None
    markup_percent: Decimal | None = None
    client_rate: Decimal | None = None


class DealReferralUpdate(BaseModel):
    referral_id: int | None = None
    referral_fee_type: str | None = None
    referral_fee_base: str | None = None
    referral_fee_value: Decimal | None = None


class DealWalletUpdate(BaseModel):
    wallet_address: str


class DealActualCloseRateUpdate(BaseModel):
    actual_close_rate: Decimal


class CfaDealDocumentBase(BaseModel):
    deal_id: int
    document_type: str
    status: str = "generated"
    file_path: str | None = None
    signed_file_path: str | None = None
    uploaded_by: int | None = None


class CfaDealDocumentCreate(CfaDealDocumentBase):
    pass


class CfaDealDocumentOut(CfaDealDocumentBase, OrmModel):
    id: int
    created_at: datetime


class CfaDealStatusHistoryOut(OrmModel):
    id: int
    deal_id: int
    old_status: str | None = None
    new_status: str
    changed_by: int | None = None
    comment: str | None = None
    created_at: datetime
