import Link from "next/link";
import { Plus } from "lucide-react";
import { MiniStatusBadge } from "@/components/mini-status-badge";
import { Button } from "@/components/ui/button";
import { miniDeals } from "@/lib/mock-data";
import { money } from "@/lib/utils";

export default function MiniDealsPage() {
  return (
    <main className="space-y-4 px-4 py-5">
      <header className="flex items-start justify-between gap-3 pt-1">
        <div>
          <h1 className="text-2xl font-semibold text-slate-50">Сделки</h1>
          <p className="mt-1 text-sm text-slate-400">Заявки, статусы и суммы.</p>
        </div>
        <Link href="/app/deals/new">
          <Button size="icon" aria-label="Создать сделку">
            <Plus className="h-4 w-4" />
          </Button>
        </Link>
      </header>

      <div className="space-y-3">
        {miniDeals.map((deal) => (
          <Link
            href={`/app/deals/${deal.id}`}
            key={deal.id}
            className="block rounded-xl border border-slate-700/60 bg-slate-900/75 p-4 shadow-lg shadow-black/10"
          >
            <div className="mb-4 flex items-start justify-between gap-3">
              <div>
                <div className="font-semibold text-slate-50">{deal.dealNumber}</div>
                <div className="mt-1 text-xs text-slate-500">{deal.requiredAction || "Действий нет"}</div>
              </div>
              <MiniStatusBadge status={deal.status} />
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="rounded-lg bg-slate-950/35 p-3">
                <div className="text-xs text-slate-500">Сумма</div>
                <div className="mt-1 font-medium text-slate-100">{money(deal.amountRub)}</div>
              </div>
              <div className="rounded-lg bg-slate-950/35 p-3">
                <div className="text-xs text-slate-500">USDT</div>
                <div className="mt-1 font-medium text-slate-100">
                  {deal.clientAssetAmount ? deal.clientAssetAmount.toLocaleString("ru-RU") : "Не рассчитан"}
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </main>
  );
}
