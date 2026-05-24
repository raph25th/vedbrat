import Link from "next/link";
import { ArrowLeft, Download, FileCog, RefreshCw, Trash2, Upload } from "lucide-react";
import { notFound } from "next/navigation";
import { AdminStatusBadge } from "@/components/admin-status-badge";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
  adminDocumentTemplates,
  clientTypeLabels,
  compositionTypeLabels,
  directionLabels,
  documentTemplateTypeLabels
} from "@/lib/admin-mock-data";

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-md border bg-white p-3">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm font-medium text-slate-900">{value}</div>
    </div>
  );
}

export default async function DocumentTemplateDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const template = adminDocumentTemplates.find((item) => item.id === Number(id));
  if (!template) notFound();

  return (
    <>
      <PageHeader
        title={template.name}
        description={`${documentTemplateTypeLabels[template.documentType]} · ${directionLabels[template.direction]} · версия ${template.version}`}
        action={
          <Link href="/admin/document-templates">
            <Button variant="outline"><ArrowLeft className="h-4 w-4" />К списку</Button>
          </Link>
        }
      />
      <div className="p-4 lg:p-8">
        <Tabs
          tabs={[
            {
              value: "overview",
              label: "Обзор",
              content: (
                <Card>
                  <CardHeader><CardTitle>Обзор шаблона</CardTitle></CardHeader>
                  <CardContent className="space-y-5">
                    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                      <Field label="Название" value={template.name} />
                      <Field label="Тип" value={documentTemplateTypeLabels[template.documentType]} />
                      <Field label="Направление" value={directionLabels[template.direction]} />
                      <Field label="Тип клиента" value={clientTypeLabels[template.clientType]} />
                      <Field label="Состав" value={compositionTypeLabels[template.compositionType]} />
                      <Field label="Версия" value={template.version} />
                      <Field label="Статус" value={<AdminStatusBadge status={template.isActive ? "active" : "inactive"} label={template.isActive ? "Активен" : "Неактивен"} />} />
                      <Field label="Файл" value={template.fileName} />
                      <Field label="Кто загрузил" value={template.uploadedBy} />
                      <Field label="Когда обновлен" value={template.updatedAt} />
                      <div className="xl:col-span-2"><Field label="Описание" value={template.description} /></div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button><Download className="h-4 w-4" />Скачать шаблон</Button>
                      <Button variant="secondary"><Upload className="h-4 w-4" />Заменить файл</Button>
                      <Button variant="outline">Сделать активным</Button>
                      <Button variant="outline">Деактивировать</Button>
                      <Button variant="outline"><Trash2 className="h-4 w-4" />Удалить</Button>
                      <Button variant="outline"><FileCog className="h-4 w-4" />Тестовая генерация</Button>
                    </div>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "variables",
              label: "Переменные",
              content: (
                <Card>
                  <CardHeader><CardTitle>Переменные шаблона</CardTitle></CardHeader>
                  <CardContent className="space-y-5">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="text-sm text-muted-foreground">
                        Найдено placeholders: {template.variables.length}. Extract работает по .docx best-effort.
                      </div>
                      <Button variant="secondary"><RefreshCw className="h-4 w-4" />Извлечь переменные</Button>
                    </div>
                    <div className="overflow-x-auto rounded-lg border">
                      <div className="grid min-w-[880px] grid-cols-[1.2fr_1.5fr_1.3fr_.7fr_1fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
                        <div>Ключ</div>
                        <div>Описание</div>
                        <div>Источник данных</div>
                        <div>Обяз.</div>
                        <div>Пример</div>
                      </div>
                      {template.variables.map((variable) => (
                        <div key={variable.key} className="grid min-w-[880px] grid-cols-[1.2fr_1.5fr_1.3fr_.7fr_1fr] border-b px-4 py-3 text-sm last:border-b-0">
                          <div className="font-mono text-xs">{variable.key}</div>
                          <div>{variable.description}</div>
                          <div className="text-muted-foreground">{variable.source}</div>
                          <div>{variable.required ? "Да" : "Нет"}</div>
                          <div>{variable.example}</div>
                        </div>
                      ))}
                    </div>
                    <div className="grid gap-4 lg:grid-cols-3">
                      <Card>
                        <CardHeader><CardTitle className="text-sm">Найденные переменные</CardTitle></CardHeader>
                        <CardContent className="space-y-2">
                          {template.variables.map((variable) => (
                            <div key={variable.key} className="rounded-md bg-muted px-2 py-1 font-mono text-xs">{variable.key}</div>
                          ))}
                        </CardContent>
                      </Card>
                      <Card>
                        <CardHeader><CardTitle className="text-sm">Есть в CRM</CardTitle></CardHeader>
                        <CardContent className="space-y-2">
                          {template.variables.filter((variable) => !template.missingFields.includes(variable.key)).map((variable) => (
                            <div key={variable.key} className="rounded-md bg-emerald-50 px-2 py-1 font-mono text-xs text-emerald-700">{variable.key}</div>
                          ))}
                        </CardContent>
                      </Card>
                      <Card>
                        <CardHeader><CardTitle className="text-sm">Пока отсутствуют / обязательные</CardTitle></CardHeader>
                        <CardContent className="space-y-2">
                          {template.missingFields.map((field) => (
                            <div key={field} className="rounded-md bg-red-50 px-2 py-1 font-mono text-xs text-red-700">{field}</div>
                          ))}
                          <div className="pt-2 text-xs font-medium uppercase text-muted-foreground">Обязательные</div>
                          {template.requiredFields.map((field) => (
                            <div key={field} className="rounded-md bg-amber-50 px-2 py-1 font-mono text-xs text-amber-800">{field}</div>
                          ))}
                        </CardContent>
                      </Card>
                    </div>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "versions",
              label: "Версии",
              content: <Card><CardContent className="p-5 text-sm">Версия {template.version} · {template.fileName} · {template.updatedAt}</CardContent></Card>
            },
            {
              value: "test",
              label: "Тестовая генерация",
              content: (
                <Card>
                  <CardHeader><CardTitle>Тестовая генерация</CardTitle></CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-2"><Label>contract.number</Label><Input defaultValue="CFA-2026-TEST" /></div>
                      <div className="space-y-2"><Label>customer.ru.name</Label><Input defaultValue="Иванов Алексей Сергеевич" /></div>
                    </div>
                    <Textarea defaultValue={JSON.stringify({ "contract.number": "CFA-2026-TEST", "customer.ru.name": "Иванов Алексей Сергеевич" }, null, 2)} />
                    <Button><FileCog className="h-4 w-4" />Сгенерировать тестовый DOCX</Button>
                  </CardContent>
                </Card>
              )
            },
            {
              value: "history",
              label: "История",
              content: <Card><CardContent className="p-5 text-sm text-muted-foreground">Шаблон создан и загружен. Автоматический аудит будет подключен позже.</CardContent></Card>
            }
          ]}
        />
      </div>
    </>
  );
}
