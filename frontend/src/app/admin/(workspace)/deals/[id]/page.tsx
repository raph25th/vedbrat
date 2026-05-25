"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiGet, apiPatch, apiUrl, type ClientRecord, type DealRecord } from "@/lib/api";
import { money } from "@/lib/utils";

const statuses = ["documents_generated", "waiting_payment", "payment_received", "waiting_closure", "closed", "cancelled", "problem"];
const statusLabels: Record<string, string> = {
  documents_generated: "Документы сформированы",
  waiting_payment: "Ожидаем оплату",
  payment_received: "Оплата поступила",
  waiting_closure: "Ожидает закрытия",
  closed: "Закрыта",
  cancelled: "Отменена",
  problem: "Проблема"
};

export default function DealDetailPage() {
  const params = useParams<{ id: string }>();
  const [deal, setDeal] = useState<DealRecord | null>(null);
  const [client, setClient] = useState<ClientRecord | null>(null);
  const [status, setStatus] = useState("documents_generated");
  const [paymentReceivedAmount, setPaymentReceivedAmount] = useState("");
  const [paymentReceivedAt, setPaymentReceivedAt] = useState("");
  const [comment, setComment] = useState("");

  useEffect(() => {
    let active = true;
    apiGet<DealRecord>(`/deals/${params.id}`).then(async (record) => {
      if (!active || !record) return;
      setDeal(record);
      setStatus(record.status);
      setPaymentReceivedAmount(record.payment_received_amount ? String(record.payment_received_amount) : "");
      setPaymentReceivedAt(record.payment_received_at ? record.payment_received_at.slice(0, 16) : "");
      setComment(record.comment || "");
      const clientRecord = await apiGet<ClientRecord>(`/clients/${record.client_id}`);
      if (active) setClient(clientRecord);
    });
    return () => {
      active = false;
    };
  }, [params.id]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const updated = await apiPatch<DealRecord>(`/deals/${params.id}`, {
      status,
      payment_received_amount: paymentReceivedAmount ? Number(paymentReceivedAmount) : null,
      payment_received_at: paymentReceivedAt ? new Date(paymentReceivedAt).toISOString() : null,
      comment
    });
    if (updated) setDeal(updated);
  }

  if (!deal) {
    return (
      <>
        <PageHeader title="Сделка" description="Загрузка данных сделки..." />
        <div className="p-8 text-sm text-muted-foreground">Загрузка...</div>
      </>
    );
  }

  return (
    <>
      <PageHeader
        title={`Сделка #${deal.id}`}
        description={statusLabels[deal.status] || deal.status}
        action={
          <Link href="/admin/deals">
            <Button variant="outline">К списку сделок</Button>
          </Link>
        }
      />
      <div className="grid gap-5 p-4 lg:grid-cols-[1fr_360px] lg:p-8">
        <div className="space-y-5">
          <Block title="1. Общая информация">
            <Field label="ID сделки" value={deal.id} />
            <Field label="Статус" value={statusLabels[deal.status] || deal.status} />
            <Field label="Тип сделки" value={deal.deal_direction} />
            <Field label="Актив" value={deal.asset || "USDT"} />
            <Field label="Дата создания" value={new Date(deal.created_at).toLocaleString("ru-RU")} />
          </Block>

          <Block title="2. Клиент">
            <Field label="ФИО" value={client?.ru_name || client?.full_name_ru} />
            <Field label="ИНН" value={client?.inn} />
            <Field label="Телефон" value={client?.phone} />
            <Field label="Email" value={client?.email || "-"} />
          </Block>

          <Block title="3. Документы">
            <Field label="Номер договора" value={deal.contract_number} />
            <Field label="Дата договора" value={deal.contract_date} />
            <Field label="Номер счет-поручения" value={deal.payment_number} />
            <Field label="Дата счет-поручения" value={deal.payment_date} />
            {deal.generated_documents_json ? (
              <div className="grid gap-2 md:col-span-2 xl:col-span-3">
                {Object.entries(deal.generated_documents_json).map(([key, document]) => (
                  <a key={key} href={apiUrl(document.download_url)} className="rounded-md border p-3 text-sm font-medium text-primary hover:bg-muted/40">
                    Скачать: {document.title}
                  </a>
                ))}
              </div>
            ) : null}
          </Block>

          <Block title="4. Финансы по документам">
            <Field label="Сумма клиента" value={deal.full_payment_amount ? money(Number(deal.full_payment_amount)) : null} />
            <Field label="Сумма исполнения" value={deal.supplier_payment_equal ? money(Number(deal.supplier_payment_equal)) : null} />
            <Field label="Агентское вознаграждение" value={deal.agent_fee_amount ? money(Number(deal.agent_fee_amount)) : null} />
            <Field label="Комиссия %" value={deal.agent_fee_percent} />
          </Block>

          <Block title="5. Операция">
            <Field label="Актив USDT" value={deal.asset || "USDT"} />
            <Field label="Кошелек клиента" value={deal.wallet_address} wide />
          </Block>

          <section className="rounded-lg border bg-white p-4">
            <h2 className="text-base font-semibold text-slate-950">Закрытие лотами</h2>
            <Button className="mt-3 w-full" disabled>Закрытие лотами — следующий этап</Button>
          </section>
        </div>

        <form onSubmit={submit} className="h-fit space-y-4 rounded-lg border bg-white p-4">
          <h2 className="text-base font-semibold text-slate-950">6. Оплата и статус</h2>
          <div className="space-y-2">
            <Label>Статус</Label>
            <select className="h-10 w-full rounded-md border bg-white px-3 text-sm" value={status} onChange={(event) => setStatus(event.target.value)}>
              {statuses.map((item) => <option key={item} value={item}>{statusLabels[item]}</option>)}
            </select>
          </div>
          <div className="space-y-2">
            <Label>Сумма оплаты</Label>
            <Input type="number" value={paymentReceivedAmount} onChange={(event) => setPaymentReceivedAmount(event.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Дата оплаты</Label>
            <Input type="datetime-local" value={paymentReceivedAt} onChange={(event) => setPaymentReceivedAt(event.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Комментарий</Label>
            <Textarea value={comment} onChange={(event) => setComment(event.target.value)} />
          </div>
          <Button type="submit" className="w-full">Сохранить сделку</Button>
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
