import Link from "next/link";
import { AdminStatusBadge, RequiredActionBadge } from "@/components/admin-status-badge";
import { type DealRecord } from "@/lib/api";
import { money } from "@/lib/utils";

export function UnifiedDealsTable({ deals, basePath }: { deals: DealRecord[]; basePath: string }) {
  return (
    <div className="overflow-x-auto rounded-lg border bg-white">
      <div className="grid min-w-[1420px] grid-cols-[1fr_1.5fr_.9fr_1fr_.8fr_1fr_1fr_1.4fr_1fr_1fr_1fr_1fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
        <div>Номер сделки</div>
        <div>Клиент</div>
        <div>ИНН</div>
        <div>Сумма RUB</div>
        <div>Курс</div>
        <div>Объем USDT</div>
        <div>Статус</div>
        <div>Требуется действие</div>
        <div>Менеджер</div>
        <div>Реферал</div>
        <div>Документы</div>
        <div>Дата создания</div>
      </div>
      {deals.length === 0 ? (
        <div className="px-4 py-8 text-center text-sm text-muted-foreground">
          Пока нет сделок. Сделка появится после создания или конвертации заявки.
        </div>
      ) : null}
      {deals.map((deal) => (
        <Link
          key={deal.id}
          href={`${basePath}/${deal.id}`}
          className="grid min-w-[1420px] grid-cols-[1fr_1.5fr_.9fr_1fr_.8fr_1fr_1fr_1.4fr_1fr_1fr_1fr_1fr] items-center border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
        >
          <div className="font-medium">{deal.deal_number || `#${deal.id}`}</div>
          <div>{deal.client_name || "Клиент не указан"}</div>
          <div className="text-muted-foreground">{deal.client_inn || "-"}</div>
          <div>{deal.amount_rub ? money(Number(deal.amount_rub)) : "Не указана"}</div>
          <div>{deal.client_rate || "-"}</div>
          <div>{deal.client_asset_amount ? Number(deal.client_asset_amount).toLocaleString("ru-RU") : "-"}</div>
          <div><AdminStatusBadge status={deal.status} /></div>
          <div><RequiredActionBadge action={deal.required_action} /></div>
          <div>{deal.manager_name || (deal.manager_id ? `#${deal.manager_id}` : "-")}</div>
          <div>{deal.referral_name || "-"}</div>
          <div><AdminStatusBadge status={deal.documents_status || "not_generated"} /></div>
          <div className="text-muted-foreground">{new Date(deal.created_at).toLocaleString("ru-RU")}</div>
        </Link>
      ))}
    </div>
  );
}
