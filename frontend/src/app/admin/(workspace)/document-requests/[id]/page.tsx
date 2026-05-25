"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiGet, apiPatch, apiUrl, type ClientRecord, type DocumentRequestRecord } from "@/lib/api";
import { money } from "@/lib/utils";

const statuses = ["submitted", "needs_review", "missing_data", "approved", "issued", "rejected", "cancelled"];
const packageTemplates = ["Заявление о присоединении к оферте", "Счет-поручение", "Акт-отчет агента"];

export default function DocumentRequestDetailPage() {
  const params = useParams<{ id: string }>();
  const [request, setRequest] = useState<DocumentRequestRecord | null>(null);
  const [client, setClient] = useState<ClientRecord | null>(null);
  const [status, setStatus] = useState("submitted");
  const [managerComment, setManagerComment] = useState("");
  const [adminComment, setAdminComment] = useState("");
  const [contractNumber, setContractNumber] = useState("");
  const [contractDate, setContractDate] = useState("");
  const [paymentNumber, setPaymentNumber] = useState("");
  const [paymentDate, setPaymentDate] = useState("");
  const [generationError, setGenerationError] = useState("");
  const [dealId, setDealId] = useState<number | null>(null);

  useEffect(() => {
    let active = true;
    apiGet<DocumentRequestRecord>(`/document-requests/${params.id}`).then(async (record) => {
      if (!active || !record) return;
      setRequest(record);
      setStatus(record.status);
      setManagerComment(record.manager_comment || "");
      setAdminComment(record.admin_comment || "");
      setContractNumber(record.contract_number || "");
      setContractDate(record.contract_date || "");
      setPaymentNumber(record.payment_number || "");
      setPaymentDate(record.payment_date || "");
      setDealId(record.deal_id || null);
      if (record.client_id) {
        const clientRecord = await apiGet<ClientRecord>(`/clients/${record.client_id}`);
        if (active) setClient(clientRecord);
      }
    });
    return () => {
      active = false;
    };
  }, [params.id]);

  async function submitUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const updated = await apiPatch<DocumentRequestRecord>(`/document-requests/${params.id}`, {
      status,
      manager_comment: managerComment,
      admin_comment: adminComment
    });
    if (updated) setRequest(updated);
  }

  async function saveIssueData() {
    const updated = await apiPatch<DocumentRequestRecord>(`/document-requests/${params.id}`, {
      contract_number: contractNumber,
      contract_date: contractDate || null,
      payment_number: paymentNumber,
      payment_date: paymentDate || null
    });
    if (updated) setRequest(updated);
  }

  async function generateDocuments() {
    setGenerationError("");
    const response = await fetch(apiUrl(`/document-requests/${params.id}/generate-documents`), { method: "POST" });
    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      setGenerationError(payload?.detail || "Не удалось сформировать документы. Проверьте обязательные поля заявки и данные выпуска.");
      return;
    }
    const result = await response.json().catch(() => null);
    if (result?.deal_id) setDealId(result.deal_id);
    const updated = await apiGet<DocumentRequestRecord>(`/document-requests/${params.id}`);
    if (updated) {
      setRequest(updated);
      setDealId(updated.deal_id || result?.deal_id || null);
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
      <div className="grid gap-5 p-4 lg:grid-cols-[1fr_360px] lg:p-8">
        <div className="space-y-5">
          <Block title="1. Общая информация">
            <Field label="ID заявки" value={request.id} />
            <Field label="Статус" value={request.status} />
            <Field label="Источник" value={request.request_source} />
            <Field label="Дата создания" value={new Date(request.created_at).toLocaleString("ru-RU")} />
            <Field label="Тип сделки" value={request.deal_type || "crypto"} />
            <Field label="Пакет документов" value={request.document_package_type || "offer_crypto_individual"} />
          </Block>

          <section className="rounded-lg border bg-white p-4">
            <h2 className="text-base font-semibold text-slate-950">Данные для выпуска документов</h2>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <EditField label="Номер договора" value={contractNumber} onChange={setContractNumber} />
              <EditField label="Дата договора" type="date" value={contractDate} onChange={setContractDate} />
              <EditField label="Номер счет-поручения" value={paymentNumber} onChange={setPaymentNumber} />
              <EditField label="Дата счет-поручения" type="date" value={paymentDate} onChange={setPaymentDate} />
            </div>
            <Button type="button" className="mt-4" onClick={saveIssueData}>Сохранить данные выпуска</Button>
          </section>

          <Block title="2. Клиент">
            <Field label="ФИО" value={client?.ru_name || client?.full_name_ru || payloadValue(request, "ru_name")} />
            <Field label="ИНН" value={client?.inn || payloadValue(request, "inn")} />
            <Field label="Дата рождения" value={client?.birth_date || payloadValue(request, "birth_date")} />
            <Field label="Телефон" value={client?.phone || payloadValue(request, "phone")} />
            <Field label="Email" value={client?.email || payloadValue(request, "email")} />
          </Block>

          <Block title="3. Паспорт">
            <Field label="Серия и номер" value={client?.passport_series_number || payloadValue(request, "passport_series_number")} />
            <Field label="Кем выдан" value={client?.passport_issued_by || payloadValue(request, "passport_issued_by")} />
            <Field label="Дата выдачи" value={client?.passport_issue_date || payloadValue(request, "passport_issue_date")} />
            <Field label="Код подразделения" value={client?.passport_department_code || payloadValue(request, "passport_department_code")} />
          </Block>

          <Block title="4. Адрес">
            <Field label="Адрес регистрации" value={client?.registration_address || payloadValue(request, "registration_address")} wide />
          </Block>

          <Block title="5. Банковские реквизиты клиента">
            <Field label="Банк" value={client?.bank_name || payloadValue(request, "bank_name")} />
            <Field label="Расчетный счет" value={client?.bank_account || payloadValue(request, "bank_account")} />
            <Field label="Корреспондентский счет" value={client?.bank_corr_account || payloadValue(request, "bank_corr_account")} />
            <Field label="БИК" value={client?.bank_bik || payloadValue(request, "bank_bik")} />
            <Field label="ИНН банка" value={client?.bank_inn || payloadValue(request, "bank_inn")} />
            <Field label="КПП банка" value={client?.bank_kpp || payloadValue(request, "bank_kpp")} />
          </Block>

          <Block title="6. Операция">
            <Field label="Сумма оплаты" value={request.full_payment_amount ? money(Number(request.full_payment_amount)) : null} />
            <Field label="Валюта" value={request.currency || "RUB"} />
            <Field label="Комиссия агента %" value={request.agent_fee_percent} />
            <Field label="Сумма на исполнение поручения" value={request.supplier_payment_equal ? money(Number(request.supplier_payment_equal)) : null} />
            <Field label="Агентское вознаграждение" value={request.agent_fee_amount ? money(Number(request.agent_fee_amount)) : null} />
            <Field label="Актив USDT" value={request.crypto_asset || "USDT"} />
            <Field label="Адрес электронного кошелька" value={request.wallet_address || payloadValue(request, "wallet_address")} wide />
          </Block>

          <section className="rounded-lg border bg-white p-4">
            <h2 className="text-base font-semibold text-slate-950">7. Документы</h2>
            <p className="mt-1 text-sm text-muted-foreground">Пакет: Оферта / крипта / физлицо</p>
            <div className="mt-3 grid gap-2">
              {packageTemplates.map((template) => (
                <div key={template} className="rounded-md border bg-muted/20 p-3 text-sm">{template}</div>
              ))}
            </div>
            <Button type="button" className="mt-4 w-full" onClick={generateDocuments}>Сформировать документы</Button>
            {generationError ? <div className="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{generationError}</div> : null}
            {request.generated_documents_json ? (
              <div className="mt-3 grid gap-2">
                {Object.entries(request.generated_documents_json).map(([key, document]) => (
                  <a key={key} href={apiUrl(document.download_url)} className="rounded-md border p-3 text-sm font-medium text-primary hover:bg-muted/40">
                    Скачать: {document.title}
                  </a>
                ))}
              </div>
            ) : null}
            {dealId ? (
              <Link href={`/admin/deals/${dealId}`} className="mt-3 block rounded-md border p-3 text-center text-sm font-medium text-primary hover:bg-muted/40">
                Открыть сделку
              </Link>
            ) : null}
          </section>

          <Block title="8. Комментарии">
            <Field label="Комментарий клиента" value={request.client_comment} wide />
            <Field label="Комментарий менеджера" value={request.manager_comment} wide />
            <Field label="Комментарий админа" value={request.admin_comment} wide />
          </Block>
        </div>

        <form onSubmit={submitUpdate} className="h-fit space-y-4 rounded-lg border bg-white p-4">
          <h2 className="text-base font-semibold text-slate-950">9. Управление статусом</h2>
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
            <Label>Комментарий админа</Label>
            <Textarea value={adminComment} onChange={(event) => setAdminComment(event.target.value)} />
          </div>
          <Button type="submit" className="w-full">Сохранить</Button>
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
      <div className="mt-1 break-words font-medium text-slate-950">{String(value || "Не указано")}</div>
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

function payloadValue(request: DocumentRequestRecord, key: string) {
  const value = request.payload_json?.[key];
  return typeof value === "string" || typeof value === "number" ? value : null;
}
