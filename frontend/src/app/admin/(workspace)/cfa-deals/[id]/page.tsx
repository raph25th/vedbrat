import Link from "next/link";
import { ArrowLeft, CheckCircle2, FileUp, Pencil, RefreshCw, Upload } from "lucide-react";
import { notFound } from "next/navigation";
import { AdminStatusBadge, RequiredActionBadge } from "@/components/admin-status-badge";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs } from "@/components/ui/tabs";
import {
  adminBankAccounts,
  adminDeals,
  adminDocumentTemplates,
  adminDocuments,
  adminHistory,
  canSeeFinance,
  clientTypeLabels,
  currentAdminUser,
  directionLabels,
  documentTemplateTypeLabels,
  getAdminClient,
  getAdminManager
} from "@/lib/admin-mock-data";
import { money } from "@/lib/utils";

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="rounded-md border bg-white p-3">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm font-medium text-slate-900">{value || "—"}</div>
    </div>
  );
}

export default async function DealPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const deal = adminDeals.find((item) => item.id === Number(id));
  if (!deal) notFound();

  const client = getAdminClient(deal.clientId);
  const manager = getAdminManager(deal.managerId);
  const bankAccount = adminBankAccounts.find((account) => account.clientId === deal.clientId);
  const documents = adminDocuments.filter((document) => document.dealId === deal.id);
  const history = adminHistory.filter((item) => item.dealId === deal.id);
  const showFinance = canSeeFinance(currentAdminUser.role);
  const generationDirection = deal.sourceType === "manual_admin" ? "cfa" : "crypto";
  const generationClientType = "physical_person";
  const matchingTemplates = adminDocumentTemplates.filter(
    (template) =>
      template.isActive &&
      template.direction === generationDirection &&
      (template.clientType === generationClientType || template.clientType === "any")
  );
  const selectedTemplate = matchingTemplates[0];

  return (
    <>
      <PageHeader
        title={deal.dealNumber}
        description={`${client?.fullNameRu || "Клиент"} · менеджер ${manager?.name || "не назначен"} · создана ${deal.createdAt}`}
        action={
          <div className="flex flex-wrap gap-2">
            <Link href="/admin/cfa-deals">
              <Button variant="outline"><ArrowLeft className="h-4 w-4" />Вернуться</Button>
            </Link>
            <Button variant="secondary"><RefreshCw className="h-4 w-4" />Изменить статус</Button>
            <Button variant="outline"><Pencil className="h-4 w-4" />Редактировать</Button>
            <Button><Upload className="h-4 w-4" />Загрузить документ</Button>
          </div>
        }
      />
      <div className="space-y-5 p-4 lg:p-8">
        <div className="flex flex-wrap items-center gap-2">
          <AdminStatusBadge status={deal.status} />
          <RequiredActionBadge action={deal.requiredAction} />
          <span className="rounded-md border bg-white px-2 py-1 text-xs text-muted-foreground">{deal.sourceType}</span>
        </div>

        <Tabs
          tabs={[
            {
              value: "overview",
              label: "Обзор",
              content: (
                <div className="grid gap-5 xl:grid-cols-[1.5fr_1fr]">
                  <div className="space-y-5">
                    <Card>
                      <CardHeader><CardTitle>Основная информация</CardTitle></CardHeader>
                      <CardContent className="grid gap-3 md:grid-cols-2">
                        <Field label="Номер сделки" value={deal.dealNumber} />
                        <Field label="Источник" value={deal.sourceType} />
                        <Field label="Telegram-группа" value={deal.telegramChat} />
                        <Field label="Клиент" value={client?.fullNameRu} />
                        <Field label="Менеджер" value={manager?.name} />
                        <Field label="Текущий статус" value={<AdminStatusBadge status={deal.status} />} />
                        <div className="md:col-span-2">
                          <Field label="Required action" value={<RequiredActionBadge action={deal.requiredAction} />} />
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader><CardTitle>Сделка</CardTitle></CardHeader>
                      <CardContent className="grid gap-3 md:grid-cols-2">
                        <Field label="Сумма RUB" value={money(deal.amountRub)} />
                        <Field label="Режим курса" value={deal.rateMode} />
                        <Field label="Курс клиента" value={deal.clientRate || "—"} />
                        <Field label="Объем USDT" value={deal.clientAssetAmount ? deal.clientAssetAmount.toLocaleString("ru-RU") : "—"} />
                        <Field label="Кошелек" value={deal.walletAddress} />
                        <Field label="Статус оплаты" value={deal.clientPaymentStatus} />
                        <Field label="Дата поступления оплаты" value={deal.paymentReceivedAt} />
                      </CardContent>
                    </Card>
                  </div>

                  <Card>
                    <CardHeader><CardTitle>Быстрые действия</CardTitle></CardHeader>
                    <CardContent className="grid gap-2">
                      <Button variant="secondary" className="justify-start"><CheckCircle2 className="h-4 w-4" />Отметить оплату клиента</Button>
                      <Button variant="secondary" className="justify-start"><RefreshCw className="h-4 w-4" />Зафиксировать курс</Button>
                      <Button variant="outline" className="justify-start">Запросить кошелек</Button>
                      <Button variant="outline" className="justify-start">Отметить сделку исполненной</Button>
                      <Button variant="outline" className="justify-start"><FileUp className="h-4 w-4" />Сформировать/загрузить акт</Button>
                    </CardContent>
                  </Card>
                </div>
              )
            },
            {
              value: "client",
              label: "Клиент",
              content: (
                <div className="space-y-5">
                  <Card>
                    <CardHeader><CardTitle>Клиентские данные</CardTitle></CardHeader>
                    <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                      <Field label="ФИО RU" value={client?.fullNameRu} />
                      <Field label="ФИО EN" value={client?.fullNameEn} />
                      <Field label="ИНН" value={client?.inn} />
                      <Field label="Телефон" value={client?.phone} />
                      <Field label="Email" value={client?.email} />
                      <Field label="Паспорт" value={client?.passport} />
                      <Field label="Дата выдачи" value={client?.passportIssueDate} />
                      <Field label="Кем выдан" value={client?.passportIssuedBy} />
                      <Field label="Код подразделения" value={client?.passportDepartmentCode} />
                      <div className="xl:col-span-3"><Field label="Адрес регистрации" value={client?.registrationAddress} /></div>
                      <Field label="Статус персональных данных" value={<AdminStatusBadge status={client?.personalDataStatus || "empty"} />} />
                      <Field label="Статус реквизитов" value={<AdminStatusBadge status={client?.bankDetailsStatus || "empty"} />} />
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader><CardTitle>Банковские реквизиты</CardTitle></CardHeader>
                    <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                      <Field label="Получатель" value={bankAccount?.recipientName} />
                      <Field label="Банк" value={bankAccount?.bankName} />
                      <Field label="Расчетный счет" value={bankAccount?.accountNumber} />
                      <Field label="Корр. счет" value={bankAccount?.corrAccount} />
                      <Field label="БИК" value={bankAccount?.bic} />
                      <Field label="ИНН банка" value={bankAccount?.bankInn} />
                      <Field label="КПП банка" value={bankAccount?.bankKpp} />
                      <div className="xl:col-span-2"><Field label="Назначение платежа" value={bankAccount?.paymentPurpose} /></div>
                      <div className="flex flex-wrap gap-2 xl:col-span-3">
                        <Button>Подтвердить персональные данные</Button>
                        <Button variant="secondary">Подтвердить реквизиты</Button>
                        <Button variant="outline">Отправить на исправление</Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )
            },
            {
              value: "finance",
              label: "Финансы",
              content: showFinance ? (
                <Card>
                  <CardHeader><CardTitle>Финансы сделки</CardTitle></CardHeader>
                  <CardContent className="space-y-5">
                    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                      <Field label="Сумма клиента RUB" value={money(deal.amountRub)} />
                      <Field label="Курс клиента" value={deal.clientRate || "—"} />
                      <Field label="Объем клиенту USDT" value={deal.clientAssetAmount ? deal.clientAssetAmount.toLocaleString("ru-RU") : "—"} />
                      <Field label="Фактический курс закрытия" value={deal.actualCloseRate || "—"} />
                      <Field label="Расчетный объем по фактическому курсу" value={deal.actualAssetAmount ? deal.actualAssetAmount.toLocaleString("ru-RU") : "—"} />
                      <Field label="Валовая прибыль USDT" value={deal.grossProfitUsdt || "—"} />
                      <Field label="Валовая прибыль RUB" value={deal.grossProfitRub ? money(deal.grossProfitRub) : "—"} />
                      <Field label="Реферал" value={deal.referralName} />
                      <Field label="Тип комиссии реферала" value={deal.referralFeeType} />
                      <Field label="Ставка реферала" value={deal.referralFeeValue} />
                      <Field label="Сумма реферала USDT/RUB" value={`${deal.referralFeeUsdt || 0} / ${money(deal.referralFeeRub || 0)}`} />
                      <Field label="Итоговая прибыль USDT/RUB" value={`${deal.netProfitUsdt || "—"} / ${deal.netProfitRub ? money(deal.netProfitRub) : "—"}`} />
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button>Изменить фактический курс закрытия</Button>
                      <Button variant="secondary">Изменить реферала</Button>
                      <Button variant="outline">Пересчитать прибыль</Button>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card><CardContent className="p-5 text-sm text-muted-foreground">Нет доступа к финансовым данным.</CardContent></Card>
              )
            },
            {
              value: "documents",
              label: "Документы",
              content: (
                <Card>
                  <CardHeader>
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <CardTitle>Документы сделки</CardTitle>
                      <Button variant="outline" disabled>Сгенерировать по шаблону — позже</Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="rounded-lg border bg-muted/30 p-4">
                      <div className="mb-3 text-sm font-semibold text-slate-950">Создать документ из шаблона</div>
                      <div className="grid gap-3 md:grid-cols-[1fr_1fr_1.4fr_auto]">
                        <select className="h-10 rounded-md border bg-white px-3 text-sm" defaultValue={generationDirection}>
                          {Object.entries(directionLabels).map(([value, label]) => (
                            <option key={value} value={value}>{label}</option>
                          ))}
                        </select>
                        <select className="h-10 rounded-md border bg-white px-3 text-sm" defaultValue={generationClientType}>
                          {Object.entries(clientTypeLabels).map(([value, label]) => (
                            <option key={value} value={value}>{label}</option>
                          ))}
                        </select>
                        <select className="h-10 rounded-md border bg-white px-3 text-sm">
                          {matchingTemplates.map((template) => (
                            <option key={template.id}>
                              {documentTemplateTypeLabels[template.documentType]} · {template.name}
                            </option>
                          ))}
                        </select>
                        <Button>Сгенерировать</Button>
                      </div>
                      {selectedTemplate?.missingFields.length ? (
                        <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                          <div className="font-semibold">Не хватает данных для генерации:</div>
                          <div className="mt-1 font-mono">{selectedTemplate.missingFields.join(", ")}</div>
                        </div>
                      ) : (
                        <div className="mt-3 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
                          Данных клиента и реквизитов достаточно для тестовой генерации.
                        </div>
                      )}
                      <div className="mt-2 text-xs text-muted-foreground">
                        Автогенерация дополняет ручную загрузку. Основной сценарий документов остается ручным.
                      </div>
                    </div>
                    {documents.map((document) => (
                      <div key={document.id} className="rounded-lg border bg-white p-4">
                        <div className="flex flex-wrap items-start justify-between gap-3">
                          <div>
                            <div className="font-semibold text-slate-950">{document.type}</div>
                            <div className="mt-1 text-sm text-muted-foreground">
                              Выданный файл: {document.issuedFile} · подписанный файл: {document.signedFile}
                            </div>
                            <div className="mt-1 text-xs text-muted-foreground">
                              uploaded_by: {document.uploadedBy}, uploaded_at: {document.uploadedAt}; checked_by: {document.checkedBy}, checked_at: {document.checkedAt}
                            </div>
                          </div>
                          <AdminStatusBadge status={document.status} />
                        </div>
                        <div className="mt-4 flex flex-wrap gap-2">
                          <Button size="sm">Загрузить документ вручную</Button>
                          <Button size="sm" variant="secondary">Заменить документ</Button>
                          <Button size="sm" variant="outline">Выдать клиенту</Button>
                          <Button size="sm" variant="outline">Загрузить подписанный файл вручную</Button>
                          <Button size="sm" variant="outline">Отметить подписанный файл проверенным</Button>
                          <Button size="sm" variant="outline">Отправить на исправление</Button>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )
            },
            {
              value: "history",
              label: "История",
              content: (
                <Card>
                  <CardHeader><CardTitle>Timeline сделки</CardTitle></CardHeader>
                  <CardContent className="space-y-4">
                    {history.map((item) => (
                      <div key={item.id} className="border-l-2 border-primary pl-4">
                        <div className="text-sm font-semibold text-slate-950">{item.title}</div>
                        <div className="mt-1 text-sm text-muted-foreground">{item.detail}</div>
                        <div className="mt-1 text-xs text-muted-foreground">{item.date}</div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )
            }
          ]}
        />
      </div>
    </>
  );
}
