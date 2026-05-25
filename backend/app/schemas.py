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
    setup_status: str = "pending_setup"
    client_type: str | None = None
    deal_direction: str | None = None
    document_flow_type: str | None = None
    default_client_id: int | None = None
    agent_id: int | None = None
    default_manager_id: int | None = None
    default_referral_mode: str | None = None
    default_referral_id: int | None = None
    rate_mode: str | None = None
    notes: str | None = None
    active_draft_deal_id: int | None = None
    responsible_manager_id: int | None = None
    connected_by: int | None = None


class TelegramChatCreate(TelegramChatBase):
    pass


class TelegramChatUpdate(BaseModel):
    telegram_chat_id: str | None = None
    title: str | None = None
    chat_type: str | None = None
    setup_status: str | None = None
    client_type: str | None = None
    deal_direction: str | None = None
    document_flow_type: str | None = None
    default_client_id: int | None = None
    agent_id: int | None = None
    default_manager_id: int | None = None
    default_referral_mode: str | None = None
    default_referral_id: int | None = None
    rate_mode: str | None = None
    notes: str | None = None
    active_draft_deal_id: int | None = None
    responsible_manager_id: int | None = None
    connected_by: int | None = None


class TelegramChatOut(TelegramChatBase, OrmModel):
    id: int
    created_at: datetime
    updated_at: datetime


class TelegramChatSetup(BaseModel):
    client_type: str
    deal_direction: str
    rate_mode: str = "skip"
    referral_mode: str = "choose_later_in_admin"
    chat_type: str = "client_group"
    default_manager_id: int | None = None
    default_referral_id: int | None = None
    notes: str | None = None


class ClientBase(BaseModel):
    full_name_ru: str | None = None
    client_type: str = "physical_person"
    full_name_en: str | None = None
    ru_name: str | None = None
    en_name: str | None = None
    inn: str | None = None
    telegram_id: str | None = None
    telegram_username: str | None = None
    citizenship: str | None = None
    tax_residency: str | None = None
    tax_residency_country: str | None = None
    birth_date: date | None = None
    birth_place: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    passport_type: str | None = None
    passport_number: str | None = None
    passport_series_number: str | None = None
    passport_issue_date: date | None = None
    passport_issued_by: str | None = None
    passport_department_code: str | None = None
    passport_expires_at: date | None = None
    registration_address: str | None = None
    residential_address: str | None = None
    bank_name: str | None = None
    bank_account: str | None = None
    bank_corr_account: str | None = None
    bank_bik: str | None = None
    bank_inn: str | None = None
    bank_kpp: str | None = None
    profile_status: str = "empty"
    responsible_manager_id: int | None = None
    telegram_chat_id: int | None = None
    referral_id: int | None = None
    default_referral_enabled: bool = False
    default_referral_id: int | None = None
    default_referral_fee_type: str | None = None
    default_referral_fee_value: Decimal | None = None
    default_referral_base: str | None = None
    default_referral_comment: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    full_name_ru: str | None = None
    client_type: str | None = None
    full_name_en: str | None = None
    ru_name: str | None = None
    en_name: str | None = None
    inn: str | None = None
    telegram_id: str | None = None
    telegram_username: str | None = None
    citizenship: str | None = None
    tax_residency: str | None = None
    tax_residency_country: str | None = None
    birth_date: date | None = None
    birth_place: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    passport_type: str | None = None
    passport_number: str | None = None
    passport_series_number: str | None = None
    passport_issue_date: date | None = None
    passport_issued_by: str | None = None
    passport_department_code: str | None = None
    passport_expires_at: date | None = None
    registration_address: str | None = None
    residential_address: str | None = None
    bank_name: str | None = None
    bank_account: str | None = None
    bank_corr_account: str | None = None
    bank_bik: str | None = None
    bank_inn: str | None = None
    bank_kpp: str | None = None
    profile_status: str | None = None
    responsible_manager_id: int | None = None
    telegram_chat_id: int | None = None
    referral_id: int | None = None
    default_referral_enabled: bool | None = None
    default_referral_id: int | None = None
    default_referral_fee_type: str | None = None
    default_referral_fee_value: Decimal | None = None
    default_referral_base: str | None = None
    default_referral_comment: str | None = None


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


class DocumentTemplateBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    template_type: str
    document_type: str | None = None
    direction: str = "cfa"
    client_type: str = "physical_person"
    document_flow_type: str | None = None
    composition_type: str = "single_document"
    executor_id: int | None = None
    version: str = "1.0"
    is_active: bool = True
    file_name: str | None = None
    original_file_name: str | None = None
    file_path: str | None = None
    file_mime_type: str | None = None
    file_size: int | None = None
    variables_json: list[dict] | None = None
    missing_fields_json: list[dict] | None = None
    uploaded_by: int | None = None


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    template_type: str | None = None
    document_type: str | None = None
    direction: str | None = None
    client_type: str | None = None
    composition_type: str | None = None
    executor_id: int | None = None
    version: str | None = None
    is_active: bool | None = None
    variables_json: list[dict] | None = None
    missing_fields_json: list[dict] | None = None


class DocumentTemplateOut(DocumentTemplateBase, OrmModel):
    id: int
    created_at: datetime
    updated_at: datetime


class TemplateVariablesOut(BaseModel):
    variables: list[str]


class TemplateTestRenderRequest(BaseModel):
    context: dict = {}


class TemplateTestRenderOut(BaseModel):
    generated_file_path: str
    variables_used: list[str]


class CfaDealBase(BaseModel):
    deal_number: str
    client_id: int
    document_request_id: int | None = None
    contract_id: int | None = None
    bank_account_id: int | None = None
    manager_id: int | None = None
    telegram_chat_id: int | None = None
    agent_id: int | None = None
    referral_id: int | None = None
    source_type: str = "manual_admin"
    client_type: str = "physical_person"
    deal_direction: str = "cfa"
    asset: str | None = None
    document_flow_type: str = "offer_join_statement"
    status: str = "new_request"
    required_action: str | None = None
    amount_rub: Decimal = 0
    full_payment_amount: Decimal | None = None
    supplier_payment_equal: Decimal | None = None
    agent_fee_amount: Decimal | None = None
    agent_fee_percent: Decimal | None = None
    currency: str = "RUB"
    contract_number: str | None = None
    contract_date: date | None = None
    payment_number: str | None = None
    payment_date: date | None = None
    generated_documents_json: dict | None = None
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
    referral_mode: str = "inherit_from_client"
    referral_base: str | None = None
    referral_disabled_reason: str | None = None
    referral_comment: str | None = None
    actual_close_rate: Decimal | None = None
    actual_asset_amount: Decimal | None = None
    gross_profit_usdt: Decimal | None = None
    gross_profit_rub: Decimal | None = None
    net_profit_usdt: Decimal | None = None
    net_profit_rub: Decimal | None = None
    client_payment_status: str = "not_received"
    client_payment_amount_rub: Decimal | None = None
    payment_received_amount: Decimal | None = None
    payment_received_at: datetime | None = None
    comment: str | None = None


class CfaDealCreate(CfaDealBase):
    pass


class CfaDealUpdate(BaseModel):
    document_request_id: int | None = None
    contract_id: int | None = None
    bank_account_id: int | None = None
    manager_id: int | None = None
    telegram_chat_id: int | None = None
    agent_id: int | None = None
    referral_id: int | None = None
    source_type: str | None = None
    client_type: str | None = None
    deal_direction: str | None = None
    asset: str | None = None
    document_flow_type: str | None = None
    status: str | None = None
    required_action: str | None = None
    amount_rub: Decimal | None = None
    full_payment_amount: Decimal | None = None
    supplier_payment_equal: Decimal | None = None
    agent_fee_amount: Decimal | None = None
    agent_fee_percent: Decimal | None = None
    currency: str | None = None
    contract_number: str | None = None
    contract_date: date | None = None
    payment_number: str | None = None
    payment_date: date | None = None
    generated_documents_json: dict | None = None
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
    referral_mode: str | None = None
    referral_base: str | None = None
    referral_disabled_reason: str | None = None
    referral_comment: str | None = None
    actual_close_rate: Decimal | None = None
    actual_asset_amount: Decimal | None = None
    client_payment_status: str | None = None
    client_payment_amount_rub: Decimal | None = None
    payment_received_amount: Decimal | None = None
    payment_received_at: datetime | None = None
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


class DocumentIssueRequestBase(BaseModel):
    deal_id: int | None = None
    client_id: int | None = None
    client_type: str | None = None
    document_package_type: str | None = None
    deal_type: str | None = None
    payment_number: str | None = None
    payment_date: date | None = None
    contract_number: str | None = None
    contract_date: date | None = None
    offer_version: str | None = None
    offer_date: date | None = None
    total_amount: Decimal | None = None
    full_payment_amount: Decimal | None = None
    currency: str = "RUB"
    agent_fee_percent: Decimal | None = None
    payment_amount: Decimal | None = None
    supplier_payment_equal: Decimal | None = None
    agent_fee_amount: Decimal | None = None
    crypto_asset: str | None = None
    wallet_address: str | None = None
    counterparty_name: str | None = None
    counterparty_address: str | None = None
    counterparty_tax_number: str | None = None
    counterparty_registration_number: str | None = None
    counterparty_bank_name: str | None = None
    counterparty_bank_account: str | None = None
    counterparty_bank_swift: str | None = None
    counterparty_corr_bank: str | None = None
    counterparty_corr_bank_bik: str | None = None
    counterparty_corr_account: str | None = None
    counterparty_corr_account_extra: str | None = None
    payment_basis_type: str | None = None
    payment_basis_number: str | None = None
    payment_basis_date: date | None = None
    payment_basis_description: str | None = None
    client_comment: str | None = None
    manager_comment: str | None = None
    admin_comment: str | None = None
    payload_json: dict | None = None
    generated_documents_json: dict | None = None
    requested_by_user_id: int | None = None
    requested_by_role: str | None = None
    request_source: str = "manager_admin"
    request_type: str = "contract"
    status: str = "requested"
    comment: str | None = None
    correction_comment: str | None = None
    reviewed_by_user_id: int | None = None
    issued_by_user_id: int | None = None
    selected_template_id: int | None = None
    generated_document_id: int | None = None


class DocumentIssueRequestCreate(BaseModel):
    client_id: int | None = None
    client_type: str | None = None
    document_package_type: str | None = None
    deal_type: str | None = None
    payment_number: str | None = None
    payment_date: date | None = None
    contract_number: str | None = None
    contract_date: date | None = None
    offer_version: str | None = None
    offer_date: date | None = None
    total_amount: Decimal | None = None
    full_payment_amount: Decimal | None = None
    currency: str = "RUB"
    agent_fee_percent: Decimal | None = None
    payment_amount: Decimal | None = None
    supplier_payment_equal: Decimal | None = None
    agent_fee_amount: Decimal | None = None
    crypto_asset: str | None = None
    wallet_address: str | None = None
    counterparty_name: str | None = None
    counterparty_address: str | None = None
    counterparty_tax_number: str | None = None
    counterparty_registration_number: str | None = None
    counterparty_bank_name: str | None = None
    counterparty_bank_account: str | None = None
    counterparty_bank_swift: str | None = None
    counterparty_corr_bank: str | None = None
    counterparty_corr_bank_bik: str | None = None
    counterparty_corr_account: str | None = None
    counterparty_corr_account_extra: str | None = None
    payment_basis_type: str | None = None
    payment_basis_number: str | None = None
    payment_basis_date: date | None = None
    payment_basis_description: str | None = None
    client_comment: str | None = None
    manager_comment: str | None = None
    admin_comment: str | None = None
    payload_json: dict | None = None
    generated_documents_json: dict | None = None
    request_source: str = "manager_admin"
    request_type: str = "contract"
    status: str = "submitted"
    comment: str | None = None


class DocumentIssueRequestUpdate(BaseModel):
    client_id: int | None = None
    client_type: str | None = None
    document_package_type: str | None = None
    deal_type: str | None = None
    payment_number: str | None = None
    payment_date: date | None = None
    contract_number: str | None = None
    contract_date: date | None = None
    offer_version: str | None = None
    offer_date: date | None = None
    total_amount: Decimal | None = None
    full_payment_amount: Decimal | None = None
    currency: str | None = None
    agent_fee_percent: Decimal | None = None
    payment_amount: Decimal | None = None
    supplier_payment_equal: Decimal | None = None
    agent_fee_amount: Decimal | None = None
    crypto_asset: str | None = None
    wallet_address: str | None = None
    counterparty_name: str | None = None
    counterparty_address: str | None = None
    counterparty_tax_number: str | None = None
    counterparty_registration_number: str | None = None
    counterparty_bank_name: str | None = None
    counterparty_bank_account: str | None = None
    counterparty_bank_swift: str | None = None
    counterparty_corr_bank: str | None = None
    counterparty_corr_bank_bik: str | None = None
    counterparty_corr_account: str | None = None
    counterparty_corr_account_extra: str | None = None
    payment_basis_type: str | None = None
    payment_basis_number: str | None = None
    payment_basis_date: date | None = None
    payment_basis_description: str | None = None
    client_comment: str | None = None
    manager_comment: str | None = None
    admin_comment: str | None = None
    payload_json: dict | None = None
    generated_documents_json: dict | None = None
    status: str | None = None
    comment: str | None = None
    correction_comment: str | None = None
    reviewed_by_user_id: int | None = None
    issued_by_user_id: int | None = None
    selected_template_id: int | None = None
    generated_document_id: int | None = None


class DocumentIssueRequestOut(DocumentIssueRequestBase, OrmModel):
    id: int
    created_at: datetime
    updated_at: datetime


class GeneratedDocumentOut(OrmModel):
    id: int
    deal_id: int
    template_id: int | None = None
    issue_request_id: int | None = None
    document_type: str
    file_name: str | None = None
    file_path: str | None = None
    status: str
    generated_by_user_id: int | None = None
    issued_by_user_id: int | None = None
    signed_uploaded_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime
