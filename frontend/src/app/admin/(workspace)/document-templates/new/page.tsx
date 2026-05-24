import Link from "next/link";
import { ArrowLeft, Upload } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export default function NewDocumentTemplatePage() {
  return (
    <>
      <PageHeader
        title="Добавить шаблон"
        description="Загрузка .docx шаблона и описание параметров для будущей генерации документов."
        action={
          <Link href="/admin/document-templates">
            <Button variant="outline"><ArrowLeft className="h-4 w-4" />К списку</Button>
          </Link>
        }
      />
      <div className="p-4 lg:p-8">
        <Card>
          <CardHeader><CardTitle>Параметры шаблона</CardTitle></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2"><Label>Название шаблона</Label><Input placeholder="Агентский договор RSI под физлицо" /></div>
            <div className="space-y-2">
              <Label>Тип шаблона</Label>
              <select className="h-10 w-full rounded-md border bg-white px-3 text-sm">
                <option>Договор</option>
                <option>Заявление о присоединении к оферте</option>
                <option>Поручение</option>
                <option>Акт</option>
                <option>Пакет документов</option>
                <option>Дополнительный документ</option>
              </select>
            </div>
            <div className="space-y-2"><Label>Код шаблона / slug</Label><Input placeholder="rsi-agent-contract-physical-person" /></div>
            <div className="space-y-2"><Label>Версия</Label><Input defaultValue="1.0" /></div>
            <div className="space-y-2"><Label>Юрлицо / исполнитель</Label><Input placeholder="VEDBRAT / RSI" /></div>
            <div className="space-y-2">
              <Label>Тип клиента</Label>
              <select className="h-10 w-full rounded-md border bg-white px-3 text-sm">
                <option>physical_person</option>
                <option>individual_entrepreneur</option>
                <option>legal_entity</option>
                <option>any</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label>Направление</Label>
              <select className="h-10 w-full rounded-md border bg-white px-3 text-sm">
                <option>cfa</option>
                <option>crypto</option>
                <option>cars</option>
                <option>ved</option>
                <option>common</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label>Состав</Label>
              <select className="h-10 w-full rounded-md border bg-white px-3 text-sm">
                <option>single_document</option>
                <option>package</option>
              </select>
            </div>
            <label className="flex h-10 items-center gap-2 rounded-md border px-3 text-sm"><input type="checkbox" defaultChecked />Активен</label>
            <div className="space-y-2 md:col-span-2"><Label>Описание</Label><Textarea placeholder="Где используется шаблон и какие документы покрывает" /></div>
            <div className="space-y-2"><Label>Файл шаблона .docx</Label><Input type="file" accept=".docx" /></div>
            <div className="space-y-2"><Label>Комментарий</Label><Input placeholder="Внутренний комментарий" /></div>
            <div className="md:col-span-2">
              <Button><Upload className="h-4 w-4" />Сохранить шаблон</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
