import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { ClientStatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { clients } from "@/lib/sample-data";

export default function ClientsPage() {
  return (
    <>
      <PageHeader title="Клиенты" description="Только физические лица, персональные данные и реквизиты." action={<Button>Новый клиент</Button>} />
      <div className="p-4 lg:p-8">
        <div className="overflow-hidden rounded-lg border bg-white">
          {clients.map((client) => (
            <Link href={`/admin/clients/${client.id}`} key={client.id} className="grid gap-3 border-b p-4 text-sm last:border-b-0 hover:bg-muted/40 md:grid-cols-[1.4fr_1fr_1fr]">
              <div>
                <div className="font-medium">{client.full_name_ru}</div>
                <div className="text-muted-foreground">{client.email}</div>
              </div>
              <div>{client.phone}</div>
              <div><ClientStatusBadge status={client.profile_status} /></div>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
