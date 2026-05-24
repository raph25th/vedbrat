import { FileText, RefreshCw, WalletCards } from "lucide-react";
import { notFound } from "next/navigation";
import { PageHeader } from "@/components/page-header";
import { DealStatusBadge, ClientStatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { clients, deals } from "@/lib/sample-data";
import { money } from "@/lib/utils";

export default function DealPage({ params }: { params: { id: string } }) {
  const deal = deals.find((item) => item.id === Number(params.id));
  if (!deal) notFound();
  const client = clients.find((item) => item.id === deal.client_id);

  return (
    <>
      <PageHeader
        title={deal.deal_number}
        description={client?.full_name_ru}
        action={<DealStatusBadge status={deal.status} />}
      />
      <div className="space-y-6 p-4 lg:p-8">
        <Tabs
          tabs={[
            {
              value: "overview",
              label: "Обзор",
              content: (
                <div className="grid gap-4 lg:grid-cols-3">
                  <Card>
                    <CardHeader><CardTitle>Параметры</CardTitle></CardHeader>
                    <CardContent className="space-y-3 text-sm">
                      <div className="flex justify-between"><span className="text-muted-foreground">Сумма</span><span>{money(deal.amount_rub)}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Курс клиента</span><span>{deal.client_rate}</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">Актив</span><span>{deal.client_asset_amount?.toLocaleString("ru-RU")} USDT</span></div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader><CardTitle>Действие</CardTitle></CardHeader>
                    <CardContent className="space-y-4">
                      <p className="text-sm text-muted-foreground">{deal.required_action || "Нет открытых действий"}</p>
                      <Button variant="secondary" className="w-full"><RefreshCw className="h-4 w-4" />Обновить статус</Button>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader><CardTitle>Кошелек</CardTitle></CardHeader>
                    <CardContent className="space-y-3">
                      <Input defaultValue={deal.wallet_address || ""} placeholder="USDT TRC20" />
                      <Button variant="outline" className="w-full"><WalletCards className="h-4 w-4" />Сохранить</Button>
                    </CardContent>
                  </Card>
                </div>
              )
            },
            {
              value: "client",
              label: "Клиент",
              content: (
                <Card>
                  <CardHeader><CardTitle>Данные клиента</CardTitle></CardHeader>
                  <CardContent className="grid gap-4 md:grid-cols-2">
                    <div><Label>ФИО</Label><Input defaultValue={client?.full_name_ru} /></div>
                    <div><Label>Email</Label><Input defaultValue={client?.email} /></div>
                    <div><Label>Телефон</Label><Input defaultValue={client?.phone} /></div>
                    <div><Label>Статус</Label><div className="pt-2"><ClientStatusBadge status={client?.profile_status || "empty"} /></div></div>
                    <div className="md:col-span-2"><Button>Одобрить данные</Button></div>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "finance",
              label: "Финансы",
              content: (
                <Card>
                  <CardHeader><CardTitle>Упрощенная прибыль</CardTitle></CardHeader>
                  <CardContent className="grid gap-4 md:grid-cols-3">
                    <div><Label>Фактический курс</Label><Input defaultValue={deal.actual_close_rate} /></div>
                    <div><Label>Gross profit, USDT</Label><Input defaultValue={deal.gross_profit_usdt} /></div>
                    <div><Label>Net profit, USDT</Label><Input defaultValue={deal.net_profit_usdt} /></div>
                    <div><Label>Ставка реферала</Label><Input defaultValue={deal.referral_fee_value} /></div>
                    <div className="md:col-span-3"><Button>Пересчитать прибыль</Button></div>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "documents",
              label: "Документы",
              content: (
                <Card>
                  <CardHeader><CardTitle>Документы сделки</CardTitle></CardHeader>
                  <CardContent className="space-y-4">
                    <div className="rounded-md border p-4 text-sm">Договор поручения — ожидает подпись</div>
                    <div className="rounded-md border p-4 text-sm">Отчет CFA — не сформирован</div>
                    <Button><FileText className="h-4 w-4" />Сформировать документы</Button>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "history",
              label: "История",
              content: (
                <Card>
                  <CardHeader><CardTitle>Журнал статусов</CardTitle></CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <div className="border-l-2 border-primary pl-3">new_request → waiting_for_client_payment</div>
                    <Textarea defaultValue={deal.comment} />
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
