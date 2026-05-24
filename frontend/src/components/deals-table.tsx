import Link from "next/link";
import { DealStatusBadge } from "@/components/status-badge";
import { money } from "@/lib/utils";
import type { CfaDeal, Client } from "@/lib/types";

export function DealsTable({ deals, clients }: { deals: CfaDeal[]; clients: Client[] }) {
  return (
    <div className="overflow-hidden rounded-lg border bg-white">
      <div className="grid min-w-[760px] grid-cols-[1.1fr_1.5fr_1fr_1fr_1fr] border-b bg-muted/60 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
        <div>Сделка</div>
        <div>Клиент</div>
        <div>Сумма</div>
        <div>Курс</div>
        <div>Статус</div>
      </div>
      {deals.map((deal) => {
        const client = clients.find((item) => item.id === deal.client_id);
        return (
          <Link
            href={`/admin/cfa-deals/${deal.id}`}
            key={deal.id}
            className="grid min-w-[760px] grid-cols-[1.1fr_1.5fr_1fr_1fr_1fr] items-center border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
          >
            <div className="font-medium">{deal.deal_number}</div>
            <div>{client?.full_name_ru || `Клиент #${deal.client_id}`}</div>
            <div>{money(deal.amount_rub)}</div>
            <div>{deal.client_rate || "Не задан"}</div>
            <div>
              <DealStatusBadge status={deal.status} />
            </div>
          </Link>
        );
      })}
    </div>
  );
}
