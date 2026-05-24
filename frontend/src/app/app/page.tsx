import Link from "next/link";
import { FileText, HandCoins, UserRound, WalletCards } from "lucide-react";
import { MiniStatusBadge } from "@/components/mini-status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { miniBankAccounts, miniClient, miniDeals, miniDocuments } from "@/lib/mock-data";
import { money } from "@/lib/utils";

export default function MiniAppHomePage() {
  const client = miniClient;
  const activeDeal = miniDeals[0];
  const defaultBankAccount = miniBankAccounts.find((account) => account.isDefault) || miniBankAccounts[0];
  const activeDealDocuments = miniDocuments.filter((document) => document.dealId === activeDeal.id);
  const hasDocumentsForSignature = activeDealDocuments.some((document) => document.canUploadSigned);
  const documentsHint = hasDocumentsForSignature
    ? "Документы выданы. Скачайте, подпишите и загрузите подписанный файл."
    : "Клиент может запросить выпуск документов у менеджера.";

  return (
    <main className="space-y-4 px-4 py-5">
      <header className="space-y-3 pt-1">
        <div className="text-xs font-medium uppercase tracking-wide text-teal-300/80">CFA Mini App</div>
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold leading-tight text-slate-50">{client.fullNameRu}</h1>
          <MiniStatusBadge status={client.profileStatus} type="client" />
        </div>
      </header>

      <div className="grid grid-cols-2 gap-3">
        <Card className="mini-card">
          <CardContent className="p-4">
            <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500/12 text-teal-300">
              <UserRound className="h-5 w-5" />
            </div>
            <div className="text-sm font-semibold text-slate-100">Профиль</div>
            <div className="mt-2">
              <MiniStatusBadge status={client.profileStatus} type="client" />
            </div>
          </CardContent>
        </Card>
        <Card className="mini-card">
          <CardContent className="p-4">
            <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-teal-500/12 text-teal-300">
              <WalletCards className="h-5 w-5" />
            </div>
            <div className="text-sm font-semibold text-slate-100">Реквизиты</div>
            <div className="mt-2">
              <MiniStatusBadge status={defaultBankAccount?.status || client.bankDetailsStatus} type="client" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Активная сделка</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="text-base font-semibold text-slate-50">{activeDeal.dealNumber}</div>
            </div>
            <MiniStatusBadge status={activeDeal.status} />
          </div>

          {activeDeal.requiredAction ? (
            <div className="rounded-xl border border-orange-400/20 bg-orange-500/10 px-3 py-2 text-sm text-orange-200">
              Требуется: {activeDeal.requiredAction}
            </div>
          ) : null}

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-lg border border-slate-700/60 bg-slate-950/35 p-3">
              <div className="text-xs text-slate-400">Сумма</div>
              <div className="mt-1 font-semibold text-slate-100">{money(activeDeal.amountRub)}</div>
            </div>
            <div className="rounded-lg border border-slate-700/60 bg-slate-950/35 p-3">
              <div className="text-xs text-slate-400">Курс</div>
              <div className="mt-1 font-semibold text-slate-100">{activeDeal.clientRate || "Не задан"}</div>
            </div>
            {activeDeal.clientAssetAmount ? (
              <div className="col-span-2 rounded-lg border border-slate-700/60 bg-slate-950/35 p-3">
                <div className="text-xs text-slate-400">Объем USDT</div>
                <div className="mt-1 font-semibold text-slate-100">
                  {activeDeal.clientAssetAmount.toLocaleString("ru-RU")} USDT
                </div>
              </div>
            ) : null}
          </div>

          <Link href={`/app/deals/${activeDeal.id}`}>
            <Button className="w-full">Открыть сделку</Button>
          </Link>
        </CardContent>
      </Card>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Документы</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-slate-100">Комплект по активной сделке</div>
              <div className="mt-1 text-xs text-slate-400">{documentsHint}</div>
            </div>
            <MiniStatusBadge status={activeDeal.documentsStatus} />
          </div>
          <div className="grid gap-2">
            <Button variant="secondary" className="w-full justify-start">
              <FileText className="h-4 w-4" />
              Запросить документы
            </Button>
            {hasDocumentsForSignature ? (
              <Link href="/app/documents">
                <Button className="w-full justify-start">Загрузить подписанные документы</Button>
              </Link>
            ) : null}
          </div>
        </CardContent>
      </Card>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-200">Быстрые действия</h2>
        <div className="grid grid-cols-2 gap-3">
          <Link href="/app/deals/new" className="rounded-xl border border-slate-700/60 bg-slate-900/70 p-4 text-slate-100">
            <HandCoins className="mb-3 h-5 w-5 text-teal-300" />
            <div className="text-sm font-medium">Запросить сделку</div>
          </Link>
          <Link href="/app/documents" className="rounded-xl border border-slate-700/60 bg-slate-900/70 p-4 text-slate-100">
            <FileText className="mb-3 h-5 w-5 text-teal-300" />
            <div className="text-sm font-medium">Документы</div>
          </Link>
          <Link href="/app/profile" className="rounded-xl border border-slate-700/60 bg-slate-900/70 p-4 text-slate-100">
            <UserRound className="mb-3 h-5 w-5 text-teal-300" />
            <div className="text-sm font-medium">Профиль</div>
          </Link>
          <Link href="/app/bank-accounts" className="rounded-xl border border-slate-700/60 bg-slate-900/70 p-4 text-slate-100">
            <WalletCards className="mb-3 h-5 w-5 text-teal-300" />
            <div className="text-sm font-medium">Реквизиты</div>
          </Link>
        </div>
      </section>

      <div className="rounded-full border border-slate-700/60 bg-slate-950/30 px-3 py-2 text-center text-xs font-medium text-slate-500">
        Тестовый режим · Demo data
      </div>
    </main>
  );
}
