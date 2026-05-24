import Link from "next/link";
import { CalendarDays, Plus, Search } from "lucide-react";
import { AdminStatusBadge, RequiredActionBadge } from "@/components/admin-status-badge";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { adminDeals, getAdminClient, getAdminManager } from "@/lib/admin-mock-data";
import { money } from "@/lib/utils";

const tabs = ["Все", "Активные", "Ожидают оплату", "Документы", "Завершенные"];

export default function DealsPage() {
  return (
    <>
      <PageHeader
        title="ЦФА-сделки"
        description="Создание, проверка, документы, статусы и сопровождение ЦФА-сделок."
        action={
          <Link href="/admin/cfa-deals/new">
            <Button>
              <Plus className="h-4 w-4" />
              Создать ЦФА-сделку
            </Button>
          </Link>
        }
      />
      <div className="space-y-5 p-4 lg:p-8">
        <div className="rounded-lg border bg-white p-4">
          <div className="grid gap-3 lg:grid-cols-[1.5fr_1fr_1fr_1fr_auto]">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input className="pl-9" placeholder="Поиск по ФИО, ИНН или номеру сделки" />
            </div>
            <select className="h-10 rounded-md border bg-white px-3 text-sm">
              <option>Все статусы</option>
              <option>Ожидаем оплату</option>
              <option>Данные на проверке</option>
              <option>Завершена</option>
            </select>
            <select className="h-10 rounded-md border bg-white px-3 text-sm">
              <option>Все менеджеры</option>
              <option>Анна Соколова</option>
              <option>Михаил Орлов</option>
              <option>Елена Морозова</option>
            </select>
            <button className="flex h-10 items-center gap-2 rounded-md border bg-white px-3 text-sm text-muted-foreground">
              <CalendarDays className="h-4 w-4" />
              Период
            </button>
            <label className="flex h-10 items-center gap-2 rounded-md border bg-white px-3 text-sm">
              <input type="checkbox" />
              Требуют действия
            </label>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {tabs.map((tab, index) => (
              <button key={tab} className={index === 0 ? "rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground" : "rounded-md border px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted"}>
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border bg-white">
          <div className="grid min-w-[1420px] grid-cols-[1fr_1.5fr_.9fr_1fr_.8fr_1fr_1fr_1.4fr_1fr_1fr_1fr_1fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>Номер сделки</div>
            <div>Клиент</div>
            <div>ИНН</div>
            <div>Сумма RUB</div>
            <div>Курс</div>
            <div>Объем USDT</div>
            <div>Статус</div>
            <div>Требуется действие</div>
            <div>Менеджер</div>
            <div>Реферал</div>
            <div>Документы</div>
            <div>Дата создания</div>
          </div>
          {adminDeals.map((deal) => {
            const client = getAdminClient(deal.clientId);
            const manager = getAdminManager(deal.managerId);
            return (
              <Link
                href={`/admin/cfa-deals/${deal.id}`}
                key={deal.id}
                className="grid min-w-[1420px] grid-cols-[1fr_1.5fr_.9fr_1fr_.8fr_1fr_1fr_1.4fr_1fr_1fr_1fr_1fr] items-center border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
              >
                <div className="font-medium">{deal.dealNumber}</div>
                <div>{client?.fullNameRu}</div>
                <div className="text-muted-foreground">{client?.inn}</div>
                <div>{money(deal.amountRub)}</div>
                <div>{deal.clientRate || "—"}</div>
                <div>{deal.clientAssetAmount ? deal.clientAssetAmount.toLocaleString("ru-RU") : "—"}</div>
                <div><AdminStatusBadge status={deal.status} /></div>
                <div><RequiredActionBadge action={deal.requiredAction} /></div>
                <div>{manager?.name}</div>
                <div>{deal.referralName}</div>
                <div><AdminStatusBadge status={deal.documentsStatus} /></div>
                <div className="text-muted-foreground">{deal.createdAt}</div>
              </Link>
            );
          })}
        </div>
      </div>
    </>
  );
}
