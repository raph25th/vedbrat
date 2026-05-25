"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiGet, apiPatch, type ClientRecord, type DocumentRequestRecord } from "@/lib/api";
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

  useEffect(() => {
    let active = true;
    apiGet<DocumentRequestRecord>(`/document-requests/${params.id}`).then(async (record) => {
      if (!active || !record) return;
      setRequest(record);
      setStatus(record.status);
      setManagerComment(record.manager_comment || "");
      setAdminComment(record.admin_comment || "");
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
            <h2 className="text-base font-semibold text-slate-950">7. Документный пакет</h2>
            <div className="mt-3 grid gap-2">
              {packageTemplates.map((template) => (
                <div key={template} className="rounded-md border bg-muted/20 p-3 text-sm">{template}</div>
              ))}
            </div>
            <Button className="mt-4 w-full" disabled>Выпустить документы — скоро</Button>
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

function payloadValue(request: DocumentRequestRecord, key: string) {
  const value = request.payload_json?.[key];
  return typeof value === "string" || typeof value === "number" ? value : null;
}
