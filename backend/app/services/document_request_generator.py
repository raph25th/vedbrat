from __future__ import annotations

import re
import shutil
import zipfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from xml.etree import ElementTree as ET

from app.core.config import settings
from app.models import Client, DocumentIssueRequest

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "documents"
OFFER_TEMPLATE = TEMPLATE_DIR / "crypto_individual_offer_statement.docx"
PAYMENT_TEMPLATE = TEMPLATE_DIR / "crypto_individual_payment_order_act.docx"
GENERATED_ROOT = Path(settings.storage_dir) / "generated_documents"

DOCUMENT_KEYS = {
    "offer_statement": {
        "title": "Заявление о присоединении к оферте",
        "template": OFFER_TEMPLATE,
        "filename": "offer_statement_{request_id}.docx",
    },
    "payment_order_act": {
        "title": "Счет-поручение и акт-отчет агента",
        "template": PAYMENT_TEMPLATE,
        "filename": "payment_order_act_{request_id}.docx",
    },
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class DocumentGenerationError(ValueError):
    pass


def format_date(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%d.%m.%Y")
    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")
    if isinstance(value, str) and DATE_RE.match(value):
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d.%m.%Y")
    return str(value)


def format_money(value: Any, keep_cents: bool = True) -> str:
    if value is None or value == "":
        return ""
    amount = Decimal(str(value)).quantize(Decimal("0.01"))
    if not keep_cents and amount == amount.to_integral_value():
        return f"{int(amount):,}".replace(",", " ")
    integer, fraction = f"{amount:.2f}".split(".")
    return f"{int(integer):,}".replace(",", " ") + "," + fraction


def payload_value(request: DocumentIssueRequest, key: str) -> Any:
    payload = request.payload_json or {}
    return payload.get(key)


def first_value(*values: Any, default: str = "") -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return default


def build_context(request: DocumentIssueRequest, client: Client) -> dict[str, str]:
    completion_date = request.payment_date or date.today()
    return {
        "customer.ru.name": str(first_value(client.ru_name, client.full_name_ru, payload_value(request, "ru_name"))),
        "customer.inn": str(first_value(client.inn, payload_value(request, "inn"))),
        "customer.ru.custom.date": format_date(first_value(client.birth_date, payload_value(request, "birth_date"))),
        "customer.ru.custom.pasport": str(first_value(client.passport_series_number, client.passport_number, payload_value(request, "passport_series_number"))),
        "customer.ru.custom.Issued_by": str(first_value(client.passport_issued_by, payload_value(request, "passport_issued_by"))),
        "customer.ru.custom.date_by": format_date(first_value(client.passport_issue_date, payload_value(request, "passport_issue_date"))),
        "customer.ru.custom.department_code": str(first_value(client.passport_department_code, payload_value(request, "passport_department_code"))),
        "customer.ru.address": str(first_value(client.registration_address, payload_value(request, "registration_address"))),
        "customer.ru.custom.telephone": str(first_value(client.phone, payload_value(request, "phone"))),
        "customer.email": str(first_value(client.email, payload_value(request, "email"), default="-")),
        "customer_account.payment_account": str(first_value(client.bank_account, payload_value(request, "bank_account"))),
        "customer_account.correspondent_account": str(first_value(client.bank_corr_account, payload_value(request, "bank_corr_account"))),
        "customer_account.bic": str(first_value(client.bank_bik, payload_value(request, "bank_bik"))),
        "customer_account.ru.name": str(first_value(client.bank_name, payload_value(request, "bank_name"))),
        "payment.number": str(first_value(request.payment_number)),
        "payment.date": format_date(request.payment_date),
        "contract.number": str(first_value(request.contract_number)),
        "contract.date": format_date(request.contract_date),
        "paymentCustom.e_wallet": str(first_value(request.wallet_address, payload_value(request, "wallet_address"))),
        "paymentCustom.full_payment_amount": format_money(request.full_payment_amount, keep_cents=False),
        "paymentCustom.supplier_payment_equal": format_money(request.supplier_payment_equal),
        "paymentCustom.agent_fee_amount": format_money(request.agent_fee_amount),
        "customer.ru.custom.date_of_completion": format_date(completion_date),
    }


def validate_generation_data(request: DocumentIssueRequest, client: Client) -> list[str]:
    checks: list[tuple[str, Any]] = [
        ("Не заполнен номер договора", request.contract_number),
        ("Не заполнена дата договора", request.contract_date),
        ("Не заполнен номер счет-поручения", request.payment_number),
        ("Не заполнена дата счет-поручения", request.payment_date),
        ("Не заполнено ФИО клиента", first_value(client.ru_name, client.full_name_ru, payload_value(request, "ru_name"))),
        ("Не заполнен ИНН клиента", first_value(client.inn, payload_value(request, "inn"))),
        ("Не заполнены серия и номер паспорта", first_value(client.passport_series_number, client.passport_number, payload_value(request, "passport_series_number"))),
        ("Не заполнено поле кем выдан паспорт", first_value(client.passport_issued_by, payload_value(request, "passport_issued_by"))),
        ("Не заполнена дата выдачи паспорта", first_value(client.passport_issue_date, payload_value(request, "passport_issue_date"))),
        ("Не заполнен код подразделения", first_value(client.passport_department_code, payload_value(request, "passport_department_code"))),
        ("Не заполнен адрес регистрации", first_value(client.registration_address, payload_value(request, "registration_address"))),
        ("Не заполнен телефон", first_value(client.phone, payload_value(request, "phone"))),
        ("Не заполнено наименование банка", first_value(client.bank_name, payload_value(request, "bank_name"))),
        ("Не заполнен расчетный счет", first_value(client.bank_account, payload_value(request, "bank_account"))),
        ("Не заполнен корреспондентский счет", first_value(client.bank_corr_account, payload_value(request, "bank_corr_account"))),
        ("Не заполнен БИК", first_value(client.bank_bik, payload_value(request, "bank_bik"))),
        ("Не заполнена сумма оплаты", request.full_payment_amount),
        ("Не заполнена сумма на исполнение поручения", request.supplier_payment_equal),
        ("Не заполнено агентское вознаграждение", request.agent_fee_amount),
        ("Не заполнен адрес электронного кошелька", first_value(request.wallet_address, payload_value(request, "wallet_address"))),
    ]
    return [message for message, value in checks if value in (None, "")]


def render_docx(template_path: Path, output_path: Path, context: dict[str, str]) -> None:
    if not template_path.exists():
        raise DocumentGenerationError(f"Шаблон не найден: {template_path}")

    with TemporaryDirectory() as tmp_dir_name:
        tmp_dir = Path(tmp_dir_name)
        with zipfile.ZipFile(template_path) as source_zip:
            source_zip.extractall(tmp_dir)

        for xml_path in (tmp_dir / "word").rglob("*.xml"):
            replace_placeholders_in_xml(xml_path, context)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as target_zip:
            for path in tmp_dir.rglob("*"):
                if path.is_file():
                    target_zip.write(path, path.relative_to(tmp_dir).as_posix())


def replace_placeholders_in_xml(xml_path: Path, context: dict[str, str]) -> None:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    changed = False

    for paragraph in root.findall(".//w:p", namespace):
        texts = paragraph.findall(".//w:t", namespace)
        if not texts:
            continue
        original = "".join(text.text or "" for text in texts)
        replaced = original
        for key, value in context.items():
            replaced = replaced.replace("${" + key + "}", value)
        if replaced != original:
            texts[0].text = replaced
            for text_node in texts[1:]:
                text_node.text = ""
            changed = True

    if changed:
        ET.register_namespace("w", namespace["w"])
        tree.write(xml_path, encoding="utf-8", xml_declaration=True)


def generate_request_documents(request: DocumentIssueRequest, client: Client) -> dict[str, dict[str, str]]:
    missing = validate_generation_data(request, client)
    if missing:
        raise DocumentGenerationError("; ".join(missing))

    context = build_context(request, client)
    target_dir = GENERATED_ROOT / f"document_request_{request.id}"
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    documents: dict[str, dict[str, str]] = {}
    for key, meta in DOCUMENT_KEYS.items():
        filename = meta["filename"].format(request_id=request.id)
        output_path = target_dir / filename
        render_docx(meta["template"], output_path, context)
        documents[key] = {
            "title": meta["title"],
            "file_name": filename,
            "file_path": str(output_path),
            "download_url": f"/document-requests/{request.id}/documents/{key}/download",
        }
    return documents
