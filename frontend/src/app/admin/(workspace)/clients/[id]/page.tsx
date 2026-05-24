import { notFound } from "next/navigation";
import { PageHeader } from "@/components/page-header";
import { ClientStatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs } from "@/components/ui/tabs";
import { clients, deals } from "@/lib/sample-data";
import { money } from "@/lib/utils";

export default function ClientPage({ params }: { params: { id: string } }) {
  const client = clients.find((item) => item.id === Number(params.id));
  if (!client) notFound();
  const clientDeals = deals.filter((deal) => deal.client_id === client.id);

  return (
    <>
      <PageHeader title={client.full_name_ru} description={client.email} action={<ClientStatusBadge status={client.profile_status} />} />
      <div className="p-4 lg:p-8">
        <Tabs
          tabs={[
            {
              value: "profile",
              label: "Профиль",
              content: (
                <Card>
                  <CardHeader><CardTitle>Персональные данные</CardTitle></CardHeader>
                  <CardContent className="grid gap-4 md:grid-cols-2">
                    <div><Label>ФИО RU</Label><Input defaultValue={client.full_name_ru} /></div>
                    <div><Label>ФИО EN</Label><Input defaultValue={client.full_name_en} /></div>
                    <div><Label>ИНН</Label><Input defaultValue={client.inn} /></div>
                    <div><Label>Телефон</Label><Input defaultValue={client.phone} /></div>
                    <div className="md:col-span-2"><Button>Одобрить персональные данные</Button></div>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "bank",
              label: "Реквизиты",
              content: (
                <Card>
                  <CardHeader><CardTitle>Банковские реквизиты</CardTitle></CardHeader>
                  <CardContent className="space-y-4">
                    <div className="rounded-md border p-4 text-sm">
                      АО Банк, счет 40702...0001, назначение платежа согласовано
                    </div>
                    <Button>Одобрить реквизиты</Button>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "deals",
              label: "Сделки",
              content: (
                <Card>
                  <CardHeader><CardTitle>Сделки клиента</CardTitle></CardHeader>
                  <CardContent className="space-y-3">
                    {clientDeals.map((deal) => (
                      <div key={deal.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                        <span>{deal.deal_number}</span>
                        <span>{money(deal.amount_rub)}</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )
            }
          ]}
        />
      </div>
    </>
  );
}
