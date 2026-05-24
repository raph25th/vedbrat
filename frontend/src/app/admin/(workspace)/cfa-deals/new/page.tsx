import Link from "next/link";
import { ArrowLeft, Check, Plus, Search } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { adminBankAccounts, adminClients, adminReferrals } from "@/lib/admin-mock-data";
import { money } from "@/lib/utils";

const steps = ["Клиент", "Реквизиты", "Параметры сделки", "Реферал", "Проверка"];

export default function NewCfaDealPage() {
  const selectedClient = adminClients[0];
  const selectedAccount = adminBankAccounts[0];
  const amountRub = 12500000;
  const clientRate = 92.4;
  const assetAmount = amountRub / clientRate;

  return (
    <>
      <PageHeader
        title="Создать ЦФА-сделку"
        description="Пошаговая форма создания сделки: клиент, реквизиты, курс, реферал и проверка."
        action={
          <Link href="/admin/cfa-deals">
            <Button variant="outline"><ArrowLeft className="h-4 w-4" />К списку</Button>
          </Link>
        }
      />
      <div className="space-y-5 p-4 lg:p-8">
        <div className="flex flex-wrap gap-2">
          {steps.map((step, index) => (
            <div key={step} className={index === 0 ? "rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground" : "rounded-md border bg-white px-3 py-2 text-sm font-medium text-muted-foreground"}>
              {index + 1}. {step}
            </div>
          ))}
        </div>

        <div className="grid gap-5 xl:grid-cols-[1.4fr_.8fr]">
          <div className="space-y-5">
            <Card>
              <CardHeader><CardTitle>1. Выбор клиента</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="relative">
                  <Search className="pointer-events-none absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input className="pl-9" placeholder="Найти по ФИО или ИНН" />
                </div>
                <div className="rounded-md border bg-muted/30 p-4 text-sm">
                  <div className="font-medium">{selectedClient.fullNameRu}</div>
                  <div className="mt-1 text-muted-foreground">ИНН {selectedClient.inn} · {selectedClient.email}</div>
                </div>
                <Button variant="outline"><Plus className="h-4 w-4" />Создать нового клиента</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>2. Реквизиты</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <select className="h-10 w-full rounded-md border bg-white px-3 text-sm">
                  <option>{selectedAccount.bankName} · {selectedAccount.accountNumber}</option>
                </select>
                <Button variant="outline"><Plus className="h-4 w-4" />Добавить новые реквизиты</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>3. Параметры сделки</CardTitle></CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2"><Label>Сумма RUB</Label><Input defaultValue={amountRub} /></div>
                <div className="space-y-2">
                  <Label>Режим курса</Label>
                  <select className="h-10 w-full rounded-md border bg-white px-3 text-sm">
                    <option>manual_fixed — ручной фиксированный</option>
                    <option>cb_plus_percent — ЦБ + процент</option>
                    <option>after_payment_manual — после поступления оплаты</option>
                  </select>
                </div>
                <div className="space-y-2"><Label>Курс клиента</Label><Input defaultValue={clientRate} /></div>
                <div className="space-y-2"><Label>Процент к ЦБ</Label><Input placeholder="0.5" /></div>
                <div className="space-y-2"><Label>Объем USDT auto-calc</Label><Input value={assetAmount.toFixed(2)} readOnly /></div>
                <div className="space-y-2"><Label>Юридическое лицо / получатель</Label><Input placeholder="VEDBRAT / агент" /></div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle>4. Реферал</CardTitle></CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <label className="flex h-10 items-center gap-2 rounded-md border px-3 text-sm"><input type="checkbox" defaultChecked />Есть реферал</label>
                <select className="h-10 rounded-md border bg-white px-3 text-sm">
                  {adminReferrals.map((referral) => <option key={referral.id}>{referral.name}</option>)}
                </select>
                <select className="h-10 rounded-md border bg-white px-3 text-sm">
                  <option>percent — процент</option>
                  <option>fixed_usdt — фикс USDT</option>
                  <option>fixed_rub — фикс RUB</option>
                </select>
                <select className="h-10 rounded-md border bg-white px-3 text-sm">
                  <option>client_amount_rub — сумма RUB</option>
                  <option>client_asset_amount — объем USDT</option>
                  <option>profit — прибыль</option>
                </select>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader><CardTitle>5. Проверка</CardTitle></CardHeader>
            <CardContent className="space-y-4 text-sm">
              <div className="rounded-md border bg-muted/30 p-3"><span className="text-muted-foreground">Клиент:</span> {selectedClient.fullNameRu}</div>
              <div className="rounded-md border bg-muted/30 p-3"><span className="text-muted-foreground">Реквизиты:</span> {selectedAccount.bankName}</div>
              <div className="rounded-md border bg-muted/30 p-3"><span className="text-muted-foreground">Сумма:</span> {money(amountRub)}</div>
              <div className="rounded-md border bg-muted/30 p-3"><span className="text-muted-foreground">Курс:</span> {clientRate}</div>
              <div className="rounded-md border bg-muted/30 p-3"><span className="text-muted-foreground">USDT:</span> {assetAmount.toLocaleString("ru-RU", { maximumFractionDigits: 2 })}</div>
              <Button className="w-full"><Check className="h-4 w-4" />Создать сделку</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
