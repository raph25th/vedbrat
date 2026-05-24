import { MessageSquare } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { telegramChats } from "@/lib/sample-data";

export default function TelegramChatsPage() {
  return (
    <>
      <PageHeader title="Telegram-чаты" description="client_group для одного клиента, agent_group для агентских групп." action={<Button><MessageSquare className="h-4 w-4" />Привязать чат</Button>} />
      <div className="grid gap-4 p-4 md:grid-cols-2 lg:p-8">
        {telegramChats.map((chat) => (
          <div key={chat.id} className="rounded-lg border bg-white p-5">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div className="font-medium">{chat.title}</div>
              <Badge label={chat.chat_type} />
            </div>
            <div className="text-sm text-muted-foreground">{chat.telegram_chat_id}</div>
          </div>
        ))}
      </div>
    </>
  );
}
