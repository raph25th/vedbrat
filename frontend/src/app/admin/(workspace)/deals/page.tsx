import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { apiGet, type ClientRecord, type DealRecord } from "@/lib/api";
import { money } from "@/lib/utils";

const statusLabels: Record<string, string> = {
  documents_generated: "Документы сформированы",
  waiting_payment: "Ожидаем оплату",
  payment_received: "Оплата поступила",
  waiting_closure: "Ожидает закрытия",
  closed: "Закрыта",
  cancelled: "Отменена",
  problem: "Проблема"
};

export default async function DealsPage() {
  const [deals, clients] = await Promise.all([
    apiGet<DealRecord[]>("/deals"),
    apiGet<ClientRecord[]>("/clients")
  ]);
  const clientById = new Map((clients || []).map((client) => [client.id, client]));

  return (
    <>
      <PageHeader title="Сделки" description="Активные сделки, созданные после формирования документов." />
      <div className="p-4 lg:p-8">
        <div className="overflow-x-auto rounded-lg border bg-white">
          <div className="grid min-w-[980px] grid-cols-[.6fr_1.4fr_1fr_.7fr_1fr_.7fr_1fr_1fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>ID</div>
            <div>Клиент</div>
            <div>Тип сделки</div>
            <div>Актив</div>
            <div>Сумма клиента</div>
            <div>Валюта</div>
            <div>Статус</div>
            <div>Дата создания</div>
          </div>
          {(deals || []).length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              Пока нет сделок. Сделка появится после формирования документов по заявке.
            </div>
          ) : null}
          {(deals || []).map((deal) => {
            const client = clientById.get(deal.client_id);
            return (
              <Link
                key={deal.id}
                href={`/admin/deals/${deal.id}`}
                className="grid min-w-[980px] grid-cols-[.6fr_1.4fr_1fr_.7fr_1fr_.7fr_1fr_1fr] border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
              >
                <div className="font-medium">#{deal.id}</div>
                <div>{client?.ru_name || client?.full_name_ru || "Клиент не указан"}</div>
                <div>{deal.deal_direction}</div>
                <div>{deal.asset || "USDT"}</div>
                <div>{deal.full_payment_amount ? money(Number(deal.full_payment_amount)) : "Не указана"}</div>
                <div>{deal.currency || "RUB"}</div>
                <div>{statusLabels[deal.status] || deal.status}</div>
                <div className="text-muted-foreground">{new Date(deal.created_at).toLocaleString("ru-RU")}</div>
              </Link>
            );
          })}
        </div>
      </div>
    </>
  );
}
