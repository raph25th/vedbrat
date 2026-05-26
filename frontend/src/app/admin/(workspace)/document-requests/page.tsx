import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { apiGet, type DocumentRequestRecord } from "@/lib/api";
import { money } from "@/lib/utils";

export default async function DocumentRequestsPage() {
  const requests = await apiGet<DocumentRequestRecord[]>("/document-requests");

  return (
    <>
      <PageHeader title="Заявки на документы" description="Клиентские заявки из Mini App, бота и публичных ссылок." />
      <div className="p-4 lg:p-8">
        <div className="overflow-x-auto rounded-lg border bg-white">
          <div className="grid min-w-[1280px] grid-cols-[.6fr_1.5fr_.9fr_1fr_1fr_.8fr_1fr_1fr_1fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>ID</div>
            <div>Клиент</div>
            <div>ИНН</div>
            <div>Сумма</div>
            <div>Актив</div>
            <div>Валюта</div>
            <div>Менеджер</div>
            <div>Статус</div>
            <div>Создана</div>
          </div>
          {(requests || []).length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              Пока нет заявок. Когда клиент заполнит форму, заявка появится здесь.
            </div>
          ) : null}
          {(requests || []).map((request) => (
            <Link
              href={`/admin/document-requests/${request.id}`}
              key={request.id}
              className="grid min-w-[1280px] grid-cols-[.6fr_1.5fr_.9fr_1fr_1fr_.8fr_1fr_1fr_1fr] border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
            >
              <div className="font-medium">#{request.id}</div>
              <div>{request.client_name || "Клиент не указан"}</div>
              <div className="text-muted-foreground">{request.client_inn || "-"}</div>
              <div>{request.full_payment_amount ? money(Number(request.full_payment_amount)) : "Не указана"}</div>
              <div>{request.crypto_asset || "USDT"}</div>
              <div>{request.currency || "RUB"}</div>
              <div>{request.manager_name || (request.manager_id ? `#${request.manager_id}` : "-")}</div>
              <div>{request.status}</div>
              <div className="text-muted-foreground">{new Date(request.created_at).toLocaleString("ru-RU")}</div>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
