import { Download, FilePlus2, Upload, WalletCards } from "lucide-react";
import { notFound } from "next/navigation";
import { MiniStatusBadge } from "@/components/mini-status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { miniDeals, miniDocuments } from "@/lib/mock-data";
import { money } from "@/lib/utils";

export default function MiniDealPage({ params }: { params: { id: string } }) {
  const deal = miniDeals.find((item) => item.id === Number(params.id));
  if (!deal) notFound();
  const documents = miniDocuments.filter((document) => document.dealId === deal.id);

  return (
    <main className="space-y-4 px-4 py-5">
      <header className="space-y-2 pt-1">
        <MiniStatusBadge status={deal.status} />
        <h1 className="text-2xl font-semibold text-slate-50">{deal.dealNumber}</h1>
      </header>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Условия</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-lg border border-slate-700/60 bg-slate-950/35 p-3">
            <div className="text-xs text-slate-400">Сумма</div>
            <div className="mt-1 font-semibold text-slate-100">{money(deal.amountRub)}</div>
          </div>
          <div className="rounded-lg border border-slate-700/60 bg-slate-950/35 p-3">
            <div className="text-xs text-slate-400">Курс</div>
            <div className="mt-1 font-semibold text-slate-100">{deal.clientRate || "Не задан"}</div>
          </div>
          {deal.clientAssetAmount ? (
            <div className="col-span-2 rounded-lg border border-slate-700/60 bg-slate-950/35 p-3">
              <div className="text-xs text-slate-400">Объем USDT</div>
              <div className="mt-1 font-semibold text-slate-100">
                {deal.clientAssetAmount.toLocaleString("ru-RU")} USDT
              </div>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Кошелек</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Label>USDT TRC20</Label>
          <Input defaultValue={deal.walletAddress || ""} placeholder="Адрес кошелька" />
          <Button className="w-full" variant="secondary">
            <WalletCards className="h-4 w-4" />
            Указать кошелек
          </Button>
        </CardContent>
      </Card>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Документы</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-2">
          {documents.map((document) => (
            <div key={document.id} className="flex items-start justify-between gap-3 rounded-xl border border-slate-700/50 bg-slate-950/25 p-3">
              <div>
                <div className="text-sm font-semibold text-slate-100">{document.title}</div>
                <div className="mt-1 text-xs text-slate-500">{document.type}</div>
              </div>
              <MiniStatusBadge status={document.status} />
            </div>
          ))}
          <Button variant="secondary" className="w-full justify-start">
            <Download className="h-4 w-4" />
            Скачать документы
          </Button>
          <Button className="w-full justify-start">
            <Upload className="h-4 w-4" />
            Загрузить подписанный файл
          </Button>
          <Button variant="outline" className="w-full justify-start">
            <FilePlus2 className="h-4 w-4" />
            Запросить документы
          </Button>
        </CardContent>
      </Card>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">История</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {deal.statusHistory.map((item) => (
            <div key={item.id} className="border-l border-teal-400/40 pl-3">
              <div className="text-sm font-medium text-slate-100">{item.label}</div>
              <div className="mt-1 text-xs text-slate-500">{item.date}</div>
            </div>
          ))}
        </CardContent>
      </Card>
    </main>
  );
}
