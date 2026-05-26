import Link from "next/link";
import { Plus } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { UnifiedDealsTable } from "@/components/unified-deals-table";
import { apiGet, type DealRecord } from "@/lib/api";

export default async function CfaDealsPage() {
  const deals = await apiGet<DealRecord[]>("/deals");

  return (
    <>
      <PageHeader
        title="ЦФА-сделки"
        description="ЦФА-сделки в той же структуре, что и основной раздел сделок."
        action={
          <Link href="/admin/cfa-deals/new">
            <Button>
              <Plus className="h-4 w-4" />
              Создать ЦФА-сделку
            </Button>
          </Link>
        }
      />
      <div className="p-4 lg:p-8">
        <UnifiedDealsTable deals={deals || []} basePath="/admin/deals" />
      </div>
    </>
  );
}
