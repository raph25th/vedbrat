import { PageHeader } from "@/components/page-header";
import { UnifiedDealsTable } from "@/components/unified-deals-table";
import { apiGet, type DealRecord } from "@/lib/api";

export default async function DealsPage() {
  const deals = await apiGet<DealRecord[]>("/deals");

  return (
    <>
      <PageHeader title="Сделки" description="Активные сделки, созданные из заявок и вручную." />
      <div className="p-4 lg:p-8">
        <UnifiedDealsTable deals={deals || []} basePath="/admin/deals" />
      </div>
    </>
  );
}
