from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    telegram_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    role: Mapped[str] = mapped_column(String(32), default="client", index=True)
    is_allowed_to_connect_bot: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str] = mapped_column(String(255))


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    default_referral_fee_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    default_referral_fee_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    default_referral_fee_base: Mapped[str | None] = mapped_column(String(64), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    default_fee_type: Mapped[str] = mapped_column(String(32), default="percent")
    default_fee_base: Mapped[str] = mapped_column(String(64), default="client_amount_rub")
    default_fee_value: Mapped[Decimal] = mapped_column(Numeric(18, 6), default=0)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")


class TelegramChat(Base, TimestampMixin):
    __tablename__ = "telegram_chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_chat_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    chat_type: Mapped[str] = mapped_column(String(32), index=True)
    setup_status: Mapped[str] = mapped_column(String(32), default="pending_setup", index=True)
    client_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    deal_direction: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    document_flow_type: Mapped[str | None] = mapped_column(String(96), nullable=True, index=True)
    default_client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True)
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agents.id"), nullable=True)
    default_manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    default_referral_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    default_referral_id: Mapped[int | None] = mapped_column(ForeignKey("referrals.id"), nullable=True)
    rate_mode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    active_draft_deal_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    responsible_manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    connected_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name_ru: Mapped[str] = mapped_column(String(255), index=True)
    client_type: Mapped[str] = mapped_column(String(64), default="physical_person", index=True)
    full_name_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ru_name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    en_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    inn: Mapped[str | None] = mapped_column(String(32), nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    telegram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    citizenship: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tax_residency: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tax_residency_country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    passport_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    passport_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    passport_series_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    passport_issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    passport_issued_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    passport_department_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    passport_expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    registration_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    residential_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bank_account: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bank_corr_account: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bank_bik: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bank_inn: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bank_kpp: Mapped[str | None] = mapped_column(String(32), nullable=True)
    profile_status: Mapped[str] = mapped_column(String(64), default="empty", index=True)
    responsible_manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    telegram_chat_id: Mapped[int | None] = mapped_column(ForeignKey("telegram_chats.id"), nullable=True)
    referral_id: Mapped[int | None] = mapped_column(ForeignKey("referrals.id"), nullable=True)
    default_referral_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    default_referral_id: Mapped[int | None] = mapped_column(ForeignKey("referrals.id"), nullable=True)
    default_referral_fee_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    default_referral_fee_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    default_referral_base: Mapped[str | None] = mapped_column(String(64), nullable=True)
    default_referral_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    bank_accounts: Mapped[list["ClientBankAccount"]] = relationship(back_populates="client")
    contracts: Mapped[list["Contract"]] = relationship(back_populates="client")
    deals: Mapped[list["CfaDeal"]] = relationship(back_populates="client")


class ClientBankAccount(Base, TimestampMixin):
    __tablename__ = "client_bank_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    recipient_name: Mapped[str] = mapped_column(String(255))
    bank_name: Mapped[str] = mapped_column(String(255))
    account_number: Mapped[str] = mapped_column(String(64))
    corr_account: Mapped[str | None] = mapped_column(String(64), nullable=True)
    bic: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bank_inn: Mapped[str | None] = mapped_column(String(32), nullable=True)
    bank_kpp: Mapped[str | None] = mapped_column(String(32), nullable=True)
    payment_purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="submitted")

    client: Mapped[Client] = relationship(back_populates="bank_accounts")


class Contract(Base, TimestampMixin):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    contract_number: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    contract_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    signed_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    client: Mapped[Client] = relationship(back_populates="contracts")


class DocumentTemplate(Base, TimestampMixin):
    __tablename__ = "document_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_type: Mapped[str] = mapped_column(String(64), index=True)
    document_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    direction: Mapped[str] = mapped_column(String(32), default="cfa", index=True)
    client_type: Mapped[str] = mapped_column(String(64), default="physical_person", index=True)
    document_flow_type: Mapped[str | None] = mapped_column(String(96), nullable=True, index=True)
    composition_type: Mapped[str] = mapped_column(String(32), default="single_document", index=True)
    executor_id: Mapped[int | None] = mapped_column(ForeignKey("agents.id"), nullable=True)
    version: Mapped[str] = mapped_column(String(32), default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    original_file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    variables_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    missing_fields_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CfaDeal(Base, TimestampMixin):
    __tablename__ = "cfa_deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_number: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), index=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id"), nullable=True)
    bank_account_id: Mapped[int | None] = mapped_column(ForeignKey("client_bank_accounts.id"), nullable=True)
    manager_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    telegram_chat_id: Mapped[int | None] = mapped_column(ForeignKey("telegram_chats.id"), nullable=True)
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agents.id"), nullable=True)
    referral_id: Mapped[int | None] = mapped_column(ForeignKey("referrals.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), default="manual_admin")
    client_type: Mapped[str] = mapped_column(String(64), default="physical_person", index=True)
    deal_direction: Mapped[str] = mapped_column(String(32), default="cfa", index=True)
    document_flow_type: Mapped[str] = mapped_column(String(96), default="offer_join_statement", index=True)
    status: Mapped[str] = mapped_column(String(64), default="new_request", index=True)
    required_action: Mapped[str | None] = mapped_column(String(255), nullable=True)

    amount_rub: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    rate_mode: Mapped[str] = mapped_column(String(32), default="manual_fixed")
    cb_rate_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cb_rate_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    markup_percent: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    client_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    client_asset_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)

    wallet_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    wallet_added_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    referral_fee_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    referral_fee_base: Mapped[str | None] = mapped_column(String(64), nullable=True)
    referral_fee_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    referral_fee_rub: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    referral_fee_usdt: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    referral_mode: Mapped[str] = mapped_column(String(32), default="inherit_from_client")
    referral_base: Mapped[str | None] = mapped_column(String(64), nullable=True)
    referral_disabled_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    referral_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    actual_close_rate: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    actual_asset_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    gross_profit_usdt: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    gross_profit_rub: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    net_profit_usdt: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    net_profit_rub: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    client_payment_status: Mapped[str] = mapped_column(String(32), default="not_received")
    client_payment_received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    client_payment_amount_rub: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    client: Mapped[Client] = relationship(back_populates="deals")
    documents: Mapped[list["CfaDealDocument"]] = relationship(back_populates="deal")
    history: Mapped[list["CfaDealStatusHistory"]] = relationship(back_populates="deal")


class CfaDealDocument(Base, TimestampMixin):
    __tablename__ = "cfa_deal_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("cfa_deals.id"), index=True)
    document_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="generated")
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    signed_file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    deal: Mapped[CfaDeal] = relationship(back_populates="documents")


class CfaDealStatusHistory(Base, TimestampMixin):
    __tablename__ = "cfa_deal_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("cfa_deals.id"), index=True)
    old_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    new_status: Mapped[str] = mapped_column(String(64))
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    deal: Mapped[CfaDeal] = relationship(back_populates="history")


class DocumentIssueRequest(Base, TimestampMixin):
    __tablename__ = "document_issue_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int | None] = mapped_column(ForeignKey("cfa_deals.id"), nullable=True, index=True)
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"), nullable=True, index=True)
    client_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    document_package_type: Mapped[str | None] = mapped_column(String(96), nullable=True)
    deal_type: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    payment_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    offer_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    offer_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    full_payment_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(16), default="RUB")
    agent_fee_percent: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    payment_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    supplier_payment_equal: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    agent_fee_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    crypto_asset: Mapped[str | None] = mapped_column(String(32), nullable=True)
    wallet_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    counterparty_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    counterparty_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    counterparty_tax_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    counterparty_registration_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    counterparty_bank_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    counterparty_bank_account: Mapped[str | None] = mapped_column(String(128), nullable=True)
    counterparty_bank_swift: Mapped[str | None] = mapped_column(String(64), nullable=True)
    counterparty_corr_bank: Mapped[str | None] = mapped_column(String(255), nullable=True)
    counterparty_corr_bank_bik: Mapped[str | None] = mapped_column(String(32), nullable=True)
    counterparty_corr_account: Mapped[str | None] = mapped_column(String(128), nullable=True)
    counterparty_corr_account_extra: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_basis_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payment_basis_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payment_basis_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_basis_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    client_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    manager_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    requested_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    requested_by_role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    request_source: Mapped[str] = mapped_column(String(32), default="manager_admin", index=True)
    request_type: Mapped[str] = mapped_column(String(64), default="contract", index=True)
    status: Mapped[str] = mapped_column(String(32), default="requested", index=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    correction_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    issued_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    selected_template_id: Mapped[int | None] = mapped_column(ForeignKey("document_templates.id"), nullable=True)
    generated_document_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class GeneratedDocument(Base, TimestampMixin):
    __tablename__ = "generated_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("cfa_deals.id"), index=True)
    template_id: Mapped[int | None] = mapped_column(ForeignKey("document_templates.id"), nullable=True)
    issue_request_id: Mapped[int | None] = mapped_column(ForeignKey("document_issue_requests.id"), nullable=True)
    document_type: Mapped[str] = mapped_column(String(64), index=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="generated", index=True)
    generated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    issued_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    signed_uploaded_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
