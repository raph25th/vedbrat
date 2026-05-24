import Link from "next/link";
import { ArrowUpRight, FileSignature, Plus } from "lucide-react";
import { AdminStatusBadge, RequiredActionBadge } from "@/components/admin-status-badge";
import { Metric } from "@/components/metric";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { adminClients, adminDeals, getAdminClient, getAdminManager } from "@/lib/admin-mock-data";
import { money } from "@/lib/utils";

export default function DashboardPage() {
  const activeDeals = adminDeals.filter((deal) => !["completed", "cancelled"].includes(deal.status));
  const needsAction = adminDeals.filter((deal) => deal.requiredAction && deal.requiredAction !== "—");
  const waitingPayment = adminDeals.filter((deal) => deal.status === "waiting_for_client_payment");
  const docsOnSignature = adminDeals.filter((deal) => deal.documentsStatus === "waiting_for_signature");
  const completedThisMonth = adminDeals.filter((deal) => deal.status === "completed");
  const totalRub = activeDeals.reduce((sum, deal) => sum + deal.amountRub, 0);
  const totalUsdt = adminDeals.reduce((sum, deal) => sum + (deal.clientAssetAmount || 0), 0);

  return (
    <>
      <PageHeader
        title="Дашборд"
        description="Операционный обзор ЦФА-сделок, документов, оплат и клиентских проверок."
        action={
          <Link href="/admin/cfa-deals/new">
            <Button>
              <Plus className="h-4 w-4" />
              Создать ЦФА-сделку
            </Button>
          </Link>
        }
      />
      <div className="space-y-6 p-4 lg:p-8">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Metric title="Оборот в работе" value={money(totalRub)} hint="Активные сделки" />
          <Metric title="Активные ЦФА-сделки" value={String(activeDeals.length)} hint="Без завершенных и отмененных" />
          <Metric title="Требуют действия" value={String(needsAction.length)} hint="Открытые операционные задачи" />
          <Metric title="Ожидают оплату" value={String(waitingPayment.length)} hint="Контроль поступления рублей" />
          <Metric title="Документы на подписи" value={String(docsOnSignature.length)} hint="Выданы клиенту" />
          <Metric title="Завершено за месяц" value={String(completedThisMonth.length)} hint="Май 2026" />
          <Metric title="Клиенты" value={String(adminClients.length)} hint="Физические лица" />
          <Metric title="Объем USDT" value={totalUsdt.toLocaleString("ru-RU", { maximumFractionDigits: 2 })} hint="По всем сделкам" />
        </div>

        <section className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-semibold text-slate-950">Требуют внимания</h2>
              <p className="text-sm text-muted-foreground">Сделки, где есть следующий операционный шаг.</p>
            </div>
            <FileSignature className="h-5 w-5 text-muted-foreground" />
          </div>
          <div className="overflow-x-auto rounded-lg border bg-white">
            <div className="grid min-w-[1040px] grid-cols-[1fr_1.4fr_1fr_1.4fr_1fr_1.1fr_.7fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
              <div>Сделка</div>
              <div>Клиент</div>
              <div>Статус</div>
              <div>Требуется действие</div>
              <div>Менеджер</div>
              <div>Создана / обновлена</div>
              <div></div>
            </div>
            {needsAction.map((deal) => {
              const client = getAdminClient(deal.clientId);
              const manager = getAdminManager(deal.managerId);
              return (
                <div key={deal.id} className="grid min-w-[1040px] grid-cols-[1fr_1.4fr_1fr_1.4fr_1fr_1.1fr_.7fr] items-center border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40">
                  <div className="font-medium">{deal.dealNumber}</div>
                  <div>{client?.fullNameRu}</div>
                  <div><AdminStatusBadge status={deal.status} /></div>
                  <div><RequiredActionBadge action={deal.requiredAction} /></div>
                  <div>{manager?.name}</div>
                  <div className="text-muted-foreground">{deal.createdAt}<br />{deal.updatedAt}</div>
                  <Link href={`/admin/cfa-deals/${deal.id}`} className="inline-flex items-center gap-1 text-primary hover:underline">
                    Открыть <ArrowUpRight className="h-3 w-3" />
                  </Link>
                </div>
              );
            })}
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold text-slate-950">Последние ЦФА-сделки</h2>
          <div className="overflow-x-auto rounded-lg border bg-white">
            <div className="grid min-w-[860px] grid-cols-[1fr_1.5fr_1fr_.8fr_1fr_1fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
              <div>Номер</div>
              <div>Клиент</div>
              <div>Сумма</div>
              <div>Курс</div>
              <div>Объем USDT</div>
              <div>Статус</div>
            </div>
            {adminDeals.slice(0, 5).map((deal) => {
              const client = getAdminClient(deal.clientId);
              return (
                <Link href={`/admin/cfa-deals/${deal.id}`} key={deal.id} className="grid min-w-[860px] grid-cols-[1fr_1.5fr_1fr_.8fr_1fr_1fr] items-center border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40">
                  <div className="font-medium">{deal.dealNumber}</div>
                  <div>{client?.fullNameRu}</div>
                  <div>{money(deal.amountRub)}</div>
                  <div>{deal.clientRate || "—"}</div>
                  <div>{deal.clientAssetAmount ? deal.clientAssetAmount.toLocaleString("ru-RU") : "—"}</div>
                  <div><AdminStatusBadge status={deal.status} /></div>
                </Link>
              );
            })}
          </div>
        </section>
      </div>
    </>
  );
}
