"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiDelete, apiGet, apiPatch, apiUrl, type ClientRecord, type DocumentRequestRecord } from "@/lib/api";
import { money } from "@/lib/utils";

const statuses = ["submitted", "needs_review", "missing_data", "approved", "documents_generated", "issued", "rejected", "cancelled"];

export default function DocumentRequestDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [request, setRequest] = useState<DocumentRequestRecord | null>(null);
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
      setClientName(record.client_name || payloadString(record, "ru_name"));
      setClientInn(record.client_inn || payloadString(record, "inn"));
      setClientPhone(payloadString(record, "phone"));
      setClientEmail(payloadString(record, "email"));
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
        const client = await apiGet<ClientRecord>(`/clients/${record.client_id}`);
        if (!active || !client) return;
        setClientName(client.ru_name || client.full_name_ru || record.client_name || "");
        setClientInn(client.inn || record.client_inn || "");
        setClientPhone(client.phone || payloadString(record, "phone"));
        setClientEmail(client.email || payloadString(record, "email"));
      }
    });
    return () => {
      active = false;
    };
  }, [params.id]);

  async function saveRequest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
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
    const response = await fetch(apiUrl(`/document-requests/${params.id}/generate-documents`), { method: "POST" });
    if (!response.ok) {
      const payload = await response.json().catch(() => null);
      setGenerationError(payload?.detail || "Не удалось сформировать документы.");
      return;
    }
    const result = await response.json().catch(() => null);
    const updated = await apiGet<DocumentRequestRecord>(`/document-requests/${params.id}`);
    if (updated) {
      setRequest(updated);
      setDealId(updated.deal_id || result?.deal_id || null);
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
            <Field label="Статус" value={request.status} />
            <Field label="Клиент" value={request.client_name || clientName} />
            <Field label="ИНН" value={request.client_inn || clientInn} />
            <Field label="Сумма" value={request.full_payment_amount ? money(Number(request.full_payment_amount)) : null} />
            <Field label="Менеджер" value={request.manager_name || (request.manager_id ? `#${request.manager_id}` : null)} />
            <Field label="Номер договора" value={request.contract_number} />
            <Field label="Номер счет-поручения" value={request.payment_number} />
            <Field label="Дата создания" value={new Date(request.created_at).toLocaleString("ru-RU")} />
          </Block>

          <section className="rounded-lg border bg-white p-4">
            <h2 className="text-base font-semibold text-slate-950">Документы</h2>
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
            <Label>Комментарий админа</Label>
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

function Field({ label, value }: { label: string; value: unknown }) {
  return (
    <div className="rounded-md border bg-muted/20 p-3 text-sm">
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

function payloadString(request: DocumentRequestRecord, key: string) {
  const value = request.payload_json?.[key];
  return typeof value === "string" || typeof value === "number" ? String(value) : "";
}
