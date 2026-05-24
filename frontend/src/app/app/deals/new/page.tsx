import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function NewDealPage() {
  return (
    <main className="space-y-4 px-4 py-5">
      <header className="space-y-1 pt-1">
        <h1 className="text-2xl font-semibold text-slate-50">Новая заявка</h1>
        <p className="text-sm text-slate-400">Менеджер проверит данные и подготовит документы.</p>
      </header>
      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Параметры сделки</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Сумма в рублях</Label>
            <Input inputMode="decimal" placeholder="1000000" />
          </div>
          <div className="space-y-2">
            <Label>Кошелек USDT</Label>
            <Input placeholder="TRC20 адрес, если уже есть" />
          </div>
          <Button className="w-full">
            <Send className="h-4 w-4" />
            Отправить заявку
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
