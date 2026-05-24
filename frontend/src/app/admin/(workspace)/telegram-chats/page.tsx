import Link from "next/link";
import { MessageSquare, Plus } from "lucide-react";
import { AdminStatusBadge } from "@/components/admin-status-badge";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { adminTelegramChats } from "@/lib/admin-mock-data";

export default function TelegramChatsPage() {
  return (
    <>
      <PageHeader
        title="Telegram-группы"
        description="Связь клиентских и агентских групп с клиентами, агентами, менеджерами и сделками."
        action={
          <Button>
            <Plus className="h-4 w-4" />
            Привязать группу
          </Button>
        }
      />
      <div className="space-y-5 p-4 lg:p-8">
        <div className="overflow-x-auto rounded-lg border bg-white">
          <div className="grid min-w-[1120px] grid-cols-[1.4fr_1fr_1.3fr_1fr_1.2fr_.8fr_.8fr_.8fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>Название группы</div>
            <div>Тип</div>
            <div>Клиент по умолчанию</div>
            <div>Агент</div>
            <div>Ответственный менеджер</div>
            <div>Клиентов</div>
            <div>Сделок</div>
            <div>Статус</div>
          </div>
          {adminTelegramChats.map((chat) => (
            <Link
              href={`/admin/telegram-chats/${chat.id}`}
              key={chat.id}
              className="grid min-w-[1120px] grid-cols-[1.4fr_1fr_1.3fr_1fr_1.2fr_.8fr_.8fr_.8fr] items-center border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
            >
              <div>
                <div className="font-medium text-slate-950">{chat.title}</div>
                <div className="text-xs text-muted-foreground">{chat.telegramChatId}</div>
              </div>
              <div><Badge label={chat.chatType} /></div>
              <div>{chat.defaultClient}</div>
              <div>{chat.agent}</div>
              <div>{chat.manager}</div>
              <div>{chat.clientsCount}</div>
              <div>{chat.dealsCount}</div>
              <div><AdminStatusBadge status={chat.status} /></div>
            </Link>
          ))}
        </div>

        <div className="rounded-lg border bg-white p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-950">
            <MessageSquare className="h-4 w-4" />
            Карточка группы
          </div>
          <div className="grid gap-3 text-sm md:grid-cols-4">
            <div className="rounded-md border bg-muted/30 p-3">Основное</div>
            <div className="rounded-md border bg-muted/30 p-3">Клиенты/плательщики</div>
            <div className="rounded-md border bg-muted/30 p-3">Сделки</div>
            <div className="rounded-md border bg-muted/30 p-3">История</div>
          </div>
        </div>
      </div>
    </>
  );
}
