import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { MiniStatusBadge } from "@/components/mini-status-badge";
import { miniBankAccounts } from "@/lib/mock-data";

export default function BankAccountsPage() {
  return (
    <main className="space-y-4 px-4 py-5">
      <header className="space-y-1 pt-1">
        <h1 className="text-2xl font-semibold text-slate-50">Банковские реквизиты</h1>
        <p className="text-sm text-slate-400">Можно добавить несколько счетов и выбрать основной.</p>
      </header>

      <section className="space-y-3">
        {miniBankAccounts.map((account) => (
          <Card className="mini-card" key={account.id}>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-3">
                <CardTitle className="text-slate-50">{account.bankName}</CardTitle>
                <MiniStatusBadge status={account.status} type="client" />
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                ["Получатель", account.recipientName],
                ["Расчетный счет", account.accountNumber],
                ["Корреспондентский счет", account.corrAccount],
                ["БИК", account.bic],
                ["ИНН банка", account.bankInn],
                ["КПП банка", account.bankKpp],
                ["Назначение платежа", account.paymentPurpose]
              ].map(([label, value]) => (
                <div key={label} className="rounded-xl border border-slate-700/50 bg-slate-950/25 p-3">
                  <div className="text-xs text-slate-500">{label}</div>
                  <div className="mt-1 break-words text-sm font-medium text-slate-100">{value}</div>
                </div>
              ))}
              <Button variant="secondary" className="w-full">Отправить реквизиты на проверку</Button>
            </CardContent>
          </Card>
        ))}
      </section>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Новый счет</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Получатель</Label>
            <Input placeholder="ФИО получателя" />
          </div>
          <div className="space-y-2">
            <Label>Банк</Label>
            <Input placeholder="Название банка" />
          </div>
          <div className="space-y-2">
            <Label>Расчетный счет</Label>
            <Input placeholder="40817..." />
          </div>
          <div className="space-y-2">
            <Label>БИК</Label>
            <Input placeholder="044525..." />
          </div>
          <div className="space-y-2">
            <Label>Назначение платежа</Label>
            <Textarea />
          </div>
          <Button className="w-full">
            <Plus className="h-4 w-4" />
            Добавить реквизиты
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
