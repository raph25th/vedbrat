import { Send } from "lucide-react";
import { MiniStatusBadge } from "@/components/mini-status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { miniClient } from "@/lib/mock-data";

export default function ProfilePage() {
  const client = miniClient;
  const fields = [
    ["ФИО RU", client.fullNameRu],
    ["ФИО EN", client.fullNameEn],
    ["ИНН", client.inn],
    ["Гражданство", client.citizenship],
    ["Налоговое резидентство", client.taxResidency],
    ["Дата рождения", client.birthDate],
    ["Место рождения", client.birthPlace],
    ["Телефон", client.phone],
    ["Email", client.email],
    ["Паспорт", client.passportNumber],
    ["Дата выдачи", client.passportIssueDate],
    ["Кем выдан", client.passportIssuedBy],
    ["Код подразделения", client.passportDepartmentCode],
    ["Адрес регистрации", client.registrationAddress]
  ];

  return (
    <main className="space-y-4 px-4 py-5">
      <header className="space-y-2 pt-1">
        <h1 className="text-2xl font-semibold text-slate-50">Профиль</h1>
        <MiniStatusBadge status={client.profileStatus} type="client" />
        <p className="text-sm text-slate-400">Персональные данные отправляются менеджеру на проверку.</p>
      </header>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Данные клиента</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {fields.map(([label, value]) => (
            <div key={label} className="rounded-xl border border-slate-700/50 bg-slate-950/25 p-3">
              <div className="text-xs text-slate-500">{label}</div>
              <div className="mt-1 text-sm font-medium text-slate-100">{value}</div>
            </div>
          ))}
          <div className="grid grid-cols-2 gap-2 pt-1">
            <Button variant="secondary">Редактировать данные</Button>
            <Button>Отправить на проверку</Button>
          </div>
        </CardContent>
      </Card>

      <Card className="mini-card">
        <CardHeader className="pb-3">
          <CardTitle className="text-slate-50">Форма редактирования</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>ФИО на русском</Label>
            <Input defaultValue={client.fullNameRu} />
          </div>
          <div className="space-y-2">
            <Label>ФИО на английском</Label>
            <Input defaultValue={client.fullNameEn} />
          </div>
          <div className="space-y-2">
            <Label>ИНН</Label>
            <Input defaultValue={client.inn} />
          </div>
          <div className="space-y-2">
            <Label>Телефон</Label>
            <Input defaultValue={client.phone} />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input defaultValue={client.email} />
          </div>
          <div className="space-y-2">
            <Label>Паспорт</Label>
            <Input defaultValue={client.passportNumber} />
          </div>
          <div className="space-y-2">
            <Label>Адрес регистрации</Label>
            <Textarea defaultValue={client.registrationAddress} />
          </div>
          <Button className="w-full">
            <Send className="h-4 w-4" />
            Отправить на проверку
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
