import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { apiGet, type ClientRecord, type DocumentRequestRecord } from "@/lib/api";
import { money } from "@/lib/utils";

export default async function DocumentRequestsPage() {
  const [requests, clients] = await Promise.all([
    apiGet<DocumentRequestRecord[]>("/document-requests"),
    apiGet<ClientRecord[]>("/clients")
  ]);
  const clientById = new Map((clients || []).map((client) => [client.id, client]));

  return (
    <>
      <PageHeader title="Заявки на документы" description="Клиентские заявки на подготовку документов из Mini App, бота и публичных ссылок." />
      <div className="p-4 lg:p-8">
        <div className="overflow-x-auto rounded-lg border bg-white">
          <div className="grid min-w-[1120px] grid-cols-[.6fr_1.4fr_1fr_1.4fr_1fr_.7fr_.9fr_.9fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>ID</div>
            <div>Клиент</div>
            <div>Тип сделки</div>
            <div>Пакет документов</div>
            <div>Сумма</div>
            <div>Валюта</div>
            <div>Источник</div>
            <div>Статус</div>
          </div>
          {(requests || []).length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-muted-foreground">
              Пока нет заявок. Когда клиент заполнит форму, заявка появится здесь.
            </div>
          ) : null}
          {(requests || []).map((request) => {
            const client = request.client_id ? clientById.get(request.client_id) : null;
            return (
              <Link
                href={`/admin/document-requests/${request.id}`}
                key={request.id}
                className="grid min-w-[1120px] grid-cols-[.6fr_1.4fr_1fr_1.4fr_1fr_.7fr_.9fr_.9fr] border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
              >
                <div className="font-medium">#{request.id}</div>
                <div>{client?.ru_name || client?.full_name_ru || "Клиент не указан"}</div>
                <div>{request.deal_type || "crypto"}</div>
                <div>{request.document_package_type || "offer_crypto_individual"}</div>
                <div>{request.full_payment_amount ? money(Number(request.full_payment_amount)) : "Не указана"}</div>
                <div>{request.currency || "RUB"}</div>
                <div>{request.request_source}</div>
                <div>{request.status}</div>
              </Link>
            );
          })}
        </div>
      </div>
    </>
  );
}
