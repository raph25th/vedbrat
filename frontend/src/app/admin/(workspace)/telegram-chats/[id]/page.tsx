import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { notFound } from "next/navigation";
import { AdminStatusBadge } from "@/components/admin-status-badge";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs } from "@/components/ui/tabs";
import { adminDeals, adminTelegramChats } from "@/lib/admin-mock-data";

export default async function TelegramChatDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const chat = adminTelegramChats.find((item) => item.id === Number(id));
  if (!chat) notFound();
  const deals = adminDeals.filter((deal) => deal.telegramChat === chat.title);

  return (
    <>
      <PageHeader
        title={chat.title}
        description={`${chat.chatType} · ${chat.telegramChatId}`}
        action={
          <Link href="/admin/telegram-chats">
            <Button variant="outline"><ArrowLeft className="h-4 w-4" />Вернуться</Button>
          </Link>
        }
      />
      <div className="p-4 lg:p-8">
        <Tabs
          tabs={[
            {
              value: "main",
              label: "Основное",
              content: (
                <Card>
                  <CardHeader><CardTitle>Основное</CardTitle></CardHeader>
                  <CardContent className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-md border p-3 text-sm">Тип: {chat.chatType}</div>
                    <div className="rounded-md border p-3 text-sm">Статус: <AdminStatusBadge status={chat.status} /></div>
                    <div className="rounded-md border p-3 text-sm">Клиент: {chat.defaultClient}</div>
                    <div className="rounded-md border p-3 text-sm">Агент: {chat.agent}</div>
                    <div className="rounded-md border p-3 text-sm">Менеджер: {chat.manager}</div>
                    <div className="rounded-md border p-3 text-sm">Сделок: {chat.dealsCount}</div>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "clients",
              label: "Клиенты/плательщики",
              content: <Card><CardContent className="p-5 text-sm">{chat.defaultClient}</CardContent></Card>
            },
            {
              value: "deals",
              label: "Сделки",
              content: (
                <Card>
                  <CardContent className="space-y-3 p-5">
                    {deals.length ? deals.map((deal) => (
                      <Link key={deal.id} href={`/admin/cfa-deals/${deal.id}`} className="block rounded-md border p-3 text-sm hover:bg-muted/40">
                        {deal.dealNumber} · {deal.status}
                      </Link>
                    )) : <div className="text-sm text-muted-foreground">Сделок пока нет.</div>}
                  </CardContent>
                </Card>
              )
            },
            {
              value: "history",
              label: "История",
              content: <Card><CardContent className="p-5 text-sm text-muted-foreground">Группа привязана к CRM.</CardContent></Card>
            }
          ]}
        />
      </div>
    </>
  );
}
