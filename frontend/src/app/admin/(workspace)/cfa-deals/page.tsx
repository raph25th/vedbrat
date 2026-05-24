import { Plus } from "lucide-react";
import { DealsTable } from "@/components/deals-table";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { clients, deals } from "@/lib/sample-data";

export default function DealsPage() {
  return (
    <>
      <PageHeader
        title="CFA-сделки"
        description="Создание, проверка, ставки, документы и операционные статусы."
        action={
          <Button>
            <Plus className="h-4 w-4" />
            Создать
          </Button>
        }
      />
      <div className="p-4 lg:p-8">
        <DealsTable deals={deals} clients={clients} />
      </div>
    </>
  );
}
