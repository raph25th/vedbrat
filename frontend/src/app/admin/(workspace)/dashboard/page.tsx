import { Button } from "@/components/ui/button";
import { DealsTable } from "@/components/deals-table";
import { Metric } from "@/components/metric";
import { PageHeader } from "@/components/page-header";
import { deals, clients } from "@/lib/sample-data";
import { money } from "@/lib/utils";

export default function DashboardPage() {
  const total = deals.reduce((sum, deal) => sum + deal.amount_rub, 0);
  const awaiting = deals.filter((deal) => deal.status.includes("waiting") || deal.status.includes("submitted")).length;

  return (
    <>
      <PageHeader
        title="Дашборд"
        description="Операционный обзор CFA-сделок и клиентских проверок."
        action={<Button>Новая сделка</Button>}
      />
      <div className="space-y-6 p-4 lg:p-8">
        <div className="grid gap-4 md:grid-cols-3">
          <Metric title="Оборот в работе" value={money(total)} hint="По активным заявкам" />
          <Metric title="Требуют внимания" value={String(awaiting)} hint="Проверки и ожидания" />
          <Metric title="Клиенты" value={String(clients.length)} hint="Физические лица" />
        </div>
        <DealsTable deals={deals} clients={clients} />
      </div>
    </>
  );
}
