import { Plus } from "lucide-react";
import { AdminStatusBadge } from "@/components/admin-status-badge";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { adminReferrals } from "@/lib/admin-mock-data";
import { money } from "@/lib/utils";

export default function ReferralsPage() {
  return (
    <>
      <PageHeader
        title="Рефералы"
        description="Партнеры, ставки по умолчанию, база расчета и начисления по ЦФА-сделкам."
        action={
          <Button>
            <Plus className="h-4 w-4" />
            Создать реферала
          </Button>
        }
      />
      <div className="p-4 lg:p-8">
        <div className="overflow-x-auto rounded-lg border bg-white">
          <div className="grid min-w-[980px] grid-cols-[1.4fr_.8fr_1fr_1fr_.8fr_.8fr_1fr_1fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>Реферал / партнер</div>
            <div>Тип</div>
            <div>Ставка по умолчанию</div>
            <div>База расчета</div>
            <div>Статус</div>
            <div>Сделок</div>
            <div>Начислено RUB</div>
            <div>Начислено USDT</div>
          </div>
          {adminReferrals.map((referral) => (
            <div key={referral.id} className="grid min-w-[980px] grid-cols-[1.4fr_.8fr_1fr_1fr_.8fr_.8fr_1fr_1fr] items-center border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40">
              <div className="font-medium text-slate-950">{referral.name}</div>
              <div>{referral.type}</div>
              <div>{referral.defaultFeeType} · {referral.defaultFeeValue}</div>
              <div>{referral.defaultFeeBase}</div>
              <div><AdminStatusBadge status={referral.status} /></div>
              <div>{referral.dealsCount}</div>
              <div>{money(referral.accruedRub)}</div>
              <div>{referral.accruedUsdt.toLocaleString("ru-RU")}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
