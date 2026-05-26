"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiDelete, apiGet, apiPatch, apiPostWithError, apiUrl, type ClientRecord, type DocumentRequestRecord } from "@/lib/api";
import { money } from "@/lib/utils";

const statuses = ["submitted", "needs_review", "missing_data", "approved", "documents_generated", "issued", "rejected", "cancelled"];

export default function DocumentRequestDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [request, setRequest] = useState<DocumentRequestRecord | null>(null);
  const [client, setClient] = useState<ClientRecord | null>(null);
  const [dealId, setDealId] = useState<number | null>(null);
  const [savingError, setSavingError] = useState("");
  const [generationError, setGenerationError] = useState("");
  const [deleteError, setDeleteError] = useState("");

  const [clientName, setClientName] = useState("");
  const [clientInn, setClientInn] = useState("");
  const [clientPhone, setClientPhone] = useState("");
  const [clientEmail, setClientEmail] = useState("");
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("RUB");
  const [asset, setAsset] = useState("USDT");
  const [contractNumber, setContractNumber] = useState("");
  const [contractDate, setContractDate] = useState("");
  const [paymentNumber, setPaymentNumber] = useState("");
  const [paymentDate, setPaymentDate] = useState("");
  const [managerId, setManagerId] = useState("");
  const [status, setStatus] = useState("submitted");
  const [managerComment, setManagerComment] = useState("");
  const [adminComment, setAdminComment] = useState("");

  useEffect(() => {
    let active = true;
    apiGet<DocumentRequestRecord>(`/document-requests/${params.id}`).then(async (record) => {
      if (!active || !record) return;
      setRequest(record);
      setDealId(record.deal_id || null);
      setClientName(record.client_name || payloadString(record, "ru_name", "full_name_ru", "customer.ru.name"));
      setClientInn(record.client_inn || payloadString(record, "inn", "customer.inn"));
      setClientPhone(payloadString(record, "phone", "customer.phone"));
      setClientEmail(payloadString(record, "email", "customer.email"));
      setAmount(record.full_payment_amount ? String(record.full_payment_amount) : "");
      setCurrency(record.currency || "RUB");
      setAsset(record.crypto_asset || "USDT");
      setContractNumber(record.contract_number || "");
      setContractDate(record.contract_date || "");
      setPaymentNumber(record.payment_number || "");
      setPaymentDate(record.payment_date || "");
      setManagerId(record.manager_id ? String(record.manager_id) : "");
      setStatus(record.status);
      setManagerComment(record.manager_comment || "");
      setAdminComment(record.admin_comment || "");

      if (record.client_id) {
        const clientRecord = await apiGet<ClientRecord>(`/clients/${record.client_id}`);
        if (!active || !clientRecord) return;
        setClient(clientRecord);
        setClientName(clientRecord.ru_name || clientRecord.full_name_ru || record.client_name || "");
        setClientInn(clientRecord.inn || record.client_inn || "");
        setClientPhone(clientRecord.phone || payloadString(record, "phone", "customer.phone"));
        setClientEmail(clientRecord.email || payloadString(record, "email", "customer.email"));
      }
    });
    return () => {
      active = false;
    };
  }, [params.id]);

  const verification = useMemo(() => {
    if (!request) return null;

    const clientFullName = client?.ru_name || client?.full_name_ru || request.client_name || payloadString(request, "ru_name", "full_name_ru", "customer.ru.name");
    const clientTaxNumber = client?.inn || request.client_inn || payloadString(request, "inn", "customer.inn");
    const passport = client?.passport_series_number || payloadString(request, "passport_series_number", "passport", "customer.ru.custom.pasport");
    const registrationAddress = client?.registration_address || payloadString(request, "registration_address", "customer.ru.address", "ru_address");
    const paymentAccount = client?.bank_account || payloadString(request, "customer_account.payment_account", "bank_account", "payment_account");
    const bankName = client?.bank_name || payloadString(request, "customer_account.ru.name", "bank_name");
    const bic = client?.bank_bik || payloadString(request, "customer_account.bic", "bank_bic", "bic");
    const correspondentAccount = client?.bank_corr_account || payloadString(request, "customer_account.correspondent_account", "bank_corr_account", "correspondent_account");
    const wallet = request.wallet_address || payloadString(request, "paymentCustom.e_wallet", "e_wallet", "wallet_address");

    return {
      clientFullName,
      clientTaxNumber,
      passport,
      registrationAddress,
      paymentAccount,
      bankName,
      bic,
      correspondentAccount,
      wallet,
      missing: [
        ["ФИО / наименование клиента", clientFullName],
        ["ИНН клиента", clientTaxNumber],
        ["Паспорт", passport],
        ["Адрес регистрации", registrationAddress],
        ["Расчетный счет клиента", paymentAccount],
        ["Банк клиента", bankName],
        ["БИК", bic],
        ["Корреспондентский счет", correspondentAccount],
        ["Номер договора", request.contract_number],
        ["Номер счет-поручения", request.payment_number],
        ["Кошелек клиента", wallet],
        ["Полная сумма платежа", request.full_payment_amount]
      ].filter(([, value]) => !hasValue(value))
    };
  }, [client, request]);

  async function saveRequest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!request) return;
    setSavingError("");
    const numericAmount = amount ? Number(amount) : null;
    const updated = await apiPatch<DocumentRequestRecord>(`/document-requests/${params.id}`, {
      status,
      manager_id: managerId ? Number(managerId) : null,
      full_payment_amount: numericAmount,
      total_amount: numericAmount,
      currency,
      crypto_asset: asset,
      contract_number: contractNumber || null,
      contract_date: contractDate || null,
      payment_number: paymentNumber || null,
      payment_date: paymentDate || null,
      manager_comment: managerComment,
      admin_comment: adminComment,
      payload_json: {
        ...(request.payload_json || {}),
        ru_name: clientName,
        full_name_ru: clientName,
        inn: clientInn,
        phone: clientPhone,
        email: clientEmail
      }
    });
    if (updated) {
      setRequest(updated);
      setDealId(updated.deal_id || null);
    } else {
      setSavingError("Не удалось сохранить заявку.");
    }
  }

  async function generateDocuments() {
    setGenerationError("");
    const result = await apiPostWithError<{ deal_id?: number }>(`/document-requests/${params.id}/generate-documents`);
    if (!result.data) {
      setGenerationError(result.error || "Не удалось сформировать документы.");
      return;
    }
    const updated = await apiGet<DocumentRequestRecord>(`/document-requests/${params.id}`);
    if (updated) {
      setRequest(updated);
      setDealId(updated.deal_id || result.data.deal_id || null);
    }
  }

  async function deleteRequest() {
    if (dealId) {
      setDeleteError("Заявка уже конвертирована в сделку, удаление заблокировано.");
      return;
    }
    setDeleteError("");
    const deleted = await apiDelete(`/document-requests/${params.id}`);
    if (deleted) {
      router.push("/admin/document-requests");
      router.refresh();
    } else {
      setDeleteError("Не удалось удалить заявку.");
    }
  }

  if (!request) {
    return (
      <>
        <PageHeader title="Заявка на документы" description="Загрузка данных заявки..." />
        <div className="p-8 text-sm text-muted-foreground">Загрузка...</div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title={`Заявка #${request.id}`}
        description={`${request.request_source} / ${request.status}`}
        action={
          <Link href="/admin/document-requests">
            <Button variant="outline">К списку заявок</Button>
          </Link>
        }
      />
      <div className="grid gap-5 p-4 lg:grid-cols-[1fr_380px] lg:p-8">
        <div className="space-y-5">
          <Block title="Общая информация">
            <Field label="ID заявки" value={request.id} />
            <Field label="Источник" value={request.request_source} />
            <Field label="Тип заявки" value={request.request_type} />
            <Field label="Статус" value={request.status} />
            <Field label="Создана" value={formatDateTime(request.created_at)} />
            <Field label="Обновлена" value={formatDateTime(request.updated_at)} />
            <Field label="Менеджер" value={request.manager_name || (request.manager_id ? `#${request.manager_id}` : null)} />
            <Field label="Тип клиента" value={request.client_type} />
            <Field label="Тип сделки" value={request.deal_type} />
            <Field label="Пакет документов" value={request.document_package_type} />
            <Field label="Комментарий клиента" value={request.client_comment || request.comment} wide />
            <Field label="Комментарий менеджера" value={request.manager_comment} wide />
            <Field label="Комментарий администратора" value={request.admin_comment || request.correction_comment} wide />
          </Block>

          <Block title="Клиент">
            <Field label="ФИО / наименование" value={verification?.clientFullName} />
            <Field label="ИНН" value={verification?.clientTaxNumber} />
            <Field label="Телефон" value={client?.phone || payloadString(request, "phone", "customer.phone")} />
            <Field label="Email" value={client?.email || payloadString(request, "email", "customer.email") || "-"} />
            <Field label="Дата рождения" value={client?.birth_date || payloadString(request, "birth_date", "customer.birth_date")} />
            <Field label="Паспорт" value={verification?.passport} />
            <Field label="Кем выдан" value={client?.passport_issued_by || payloadString(request, "passport_issued_by")} />
            <Field label="Дата выдачи" value={client?.passport_issue_date || payloadString(request, "passport_issue_date")} />
            <Field label="Код подразделения" value={client?.passport_department_code || payloadString(request, "passport_department_code")} />
            <Field label="Адрес регистрации" value={verification?.registrationAddress} wide />
          </Block>

          <Block title="Банковские реквизиты клиента">
            <Field label="Расчетный счет" value={verification?.paymentAccount} />
            <Field label="Банк" value={verification?.bankName} />
            <Field label="БИК" value={verification?.bic} />
            <Field label="Корреспондентский счет" value={verification?.correspondentAccount} />
          </Block>

          <Block title="Документы">
            <Field label="Номер договора" value={request.contract_number} />
            <Field label="Дата договора" value={request.contract_date} />
            <Field label="Номер счет-поручения" value={request.payment_number} />
            <Field label="Дата счет-поручения" value={request.payment_date} />
            <Field label="Дата исполнения / заявки" value={payloadString(request, "customer.ru.custom.date_of_completion", "date_of_completion") || request.payment_basis_date} />
            <Field label="Шаблон" value={request.selected_template_id ? `#${request.selected_template_id}` : null} />
            <Field label="Пакет" value={request.document_package_type} />
            {request.generated_documents_json ? (
              <div className="grid gap-2 md:col-span-2 xl:col-span-3">
                {Object.entries(request.generated_documents_json).map(([key, document]) => (
                  <a key={key} href={apiUrl(document.download_url)} className="rounded-md border p-3 text-sm font-medium text-primary hover:bg-muted/40">
                    Скачать: {document.title}
                  </a>
                ))}
              </div>
            ) : null}
          </Block>

          <Block title="Финансы">
            <Field label="Сумма клиента" value={formatMoney(request.full_payment_amount)} />
            <Field label="Валюта" value={request.currency} />
            <Field label="Сумма исполнения" value={formatMoney(request.supplier_payment_equal || request.payment_amount)} />
            <Field label="Агентское вознаграждение" value={formatMoney(request.agent_fee_amount)} />
            <Field label="Комиссия %" value={request.agent_fee_percent} />
            <Field label="Курс" value={payloadString(request, "rate", "client_rate", "purchase_rate")} />
            <Field label="Объем USDT" value={payloadString(request, "usdt_volume", "client_asset_amount", "asset_volume")} />
            <Field label="Итого" value={formatMoney(request.total_amount)} />
          </Block>

          <Block title="Операция">
            <Field label="Актив" value={request.crypto_asset} />
            <Field label="Кошелек / e-wallet" value={verification?.wallet} wide />
            <Field label="Сеть" value={payloadString(request, "network", "blockchain_network")} />
            <Field label="Комментарий операции" value={request.payment_basis_description || payloadString(request, "operation_comment")} wide />
          </Block>

          <section className="rounded-lg border bg-white p-4">
            <h2 className="text-base font-semibold text-slate-950">Проверка перед выпуском</h2>
            {verification?.missing.length ? (
              <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
                <div className="font-medium">Проверьте незаполненные поля перед формированием документов:</div>
                <ul className="mt-2 list-disc space-y-1 pl-5">
                  {verification.missing.map(([label]) => (
                    <li key={label}>{label}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="mt-3 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">
                Основные поля для шаблонов заполнены.
              </div>
            )}
          </section>

          <section className="rounded-lg border bg-white p-4">
            <h2 className="text-base font-semibold text-slate-950">Документы</h2>
            <Button type="button" className="mt-4 w-full" onClick={generateDocuments}>Сформировать документы</Button>
            {generationError ? <div className="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{generationError}</div> : null}
            {dealId ? (
              <Link href={`/admin/deals/${dealId}`} className="mt-3 block rounded-md border p-3 text-center text-sm font-medium text-primary hover:bg-muted/40">
                Открыть сделку
              </Link>
            ) : null}
          </section>
        </div>

        <form onSubmit={saveRequest} className="h-fit space-y-4 rounded-lg border bg-white p-4">
          <h2 className="text-base font-semibold text-slate-950">Редактирование заявки</h2>
          <EditField label="ФИО клиента" value={clientName} onChange={setClientName} />
          <EditField label="ИНН клиента" value={clientInn} onChange={setClientInn} />
          <EditField label="Телефон" value={clientPhone} onChange={setClientPhone} />
          <EditField label="Email" type="email" value={clientEmail} onChange={setClientEmail} />
          <EditField label="Сумма" type="number" value={amount} onChange={setAmount} />
          <EditField label="Валюта" value={currency} onChange={setCurrency} />
          <EditField label="Актив" value={asset} onChange={setAsset} />
          <EditField label="Номер договора" value={contractNumber} onChange={setContractNumber} />
          <EditField label="Дата договора" type="date" value={contractDate} onChange={setContractDate} />
          <EditField label="Номер счет-поручения" value={paymentNumber} onChange={setPaymentNumber} />
          <EditField label="Дата счет-поручения" type="date" value={paymentDate} onChange={setPaymentDate} />
          <EditField label="Manager ID" type="number" value={managerId} onChange={setManagerId} />
          <div className="space-y-2">
            <Label>Статус</Label>
            <select className="h-10 w-full rounded-md border bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              {statuses.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </div>
          <div className="space-y-2">
            <Label>Комментарий менеджера</Label>
            <Textarea value={managerComment} onChange={(event) => setManagerComment(event.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Комментарий администратора</Label>
            <Textarea value={adminComment} onChange={(event) => setAdminComment(event.target.value)} />
          </div>
          {savingError ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{savingError}</div> : null}
          <Button type="submit" className="w-full">Сохранить заявку</Button>
          <Button type="button" variant="outline" className="w-full border-red-200 text-red-700 hover:bg-red-50" onClick={deleteRequest} disabled={Boolean(dealId)}>
            Удалить заявку
          </Button>
          {deleteError ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{deleteError}</div> : null}
        </form>
      </div>
    </>
  );
}

function Block({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border bg-white p-4">
      <h2 className="text-base font-semibold text-slate-950">{title}</h2>
      <div className="mt-3 grid gap-3 md:grid-cols-2 xl:grid-cols-3">{children}</div>
    </section>
  );
}

function Field({ label, value, wide = false }: { label: string; value: unknown; wide?: boolean }) {
  return (
    <div className={wide ? "rounded-md border bg-muted/20 p-3 text-sm md:col-span-2 xl:col-span-3" : "rounded-md border bg-muted/20 p-3 text-sm"}>
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="mt-1 break-words font-medium text-slate-950">{String(hasValue(value) ? value : "Не указано")}</div>
    </div>
  );
}

function EditField({ label, value, onChange, type = "text" }: { label: string; value: string; onChange: (value: string) => void; type?: string }) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Input type={type} value={value} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}

function payloadString(request: DocumentRequestRecord, ...keys: string[]) {
  for (const key of keys) {
    const value = payloadValue(request.payload_json, key);
    if (typeof value === "string" || typeof value === "number") return String(value);
  }
  return "";
}

function payloadValue(payload: Record<string, unknown> | null, key: string): unknown {
  if (!payload) return null;
  if (key in payload) return payload[key];
  return key.split(".").reduce<unknown>((current, part) => {
    if (current && typeof current === "object" && part in current) {
      return (current as Record<string, unknown>)[part];
    }
    return null;
  }, payload);
}

function hasValue(value: unknown) {
  return value !== null && value !== undefined && String(value).trim() !== "";
}

function formatDateTime(value: string | null | undefined) {
  return value ? new Date(value).toLocaleString("ru-RU") : null;
}

function formatMoney(value: string | number | null | undefined) {
  return value ? money(Number(value)) : null;
}
