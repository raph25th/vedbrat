import Link from "next/link";
import { Plus } from "lucide-react";
import { AdminStatusBadge } from "@/components/admin-status-badge";
import { Metric } from "@/components/metric";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import {
  adminDocumentTemplates,
  clientTypeLabels,
  compositionTypeLabels,
  directionLabels,
  documentTemplateTypeLabels
} from "@/lib/admin-mock-data";

const tabs = ["Договоры", "Поручения", "Акты", "Все шаблоны"];

export default function DocumentTemplatesPage() {
  const activeCount = adminDocumentTemplates.filter((template) => template.isActive).length;
  const contracts = adminDocumentTemplates.filter((template) => template.templateType === "contract").length;
  const orders = adminDocumentTemplates.filter((template) => template.templateType === "principal_order").length;
  const reports = adminDocumentTemplates.filter((template) => template.templateType === "agent_report").length;

  return (
    <>
      <PageHeader
        title="Шаблоны документов"
        description="Управление шаблонами договоров, поручений и актов для автоматической генерации документов."
        action={
          <Link href="/admin/document-templates/new">
            <Button><Plus className="h-4 w-4" />Добавить шаблон</Button>
          </Link>
        }
      />
      <div className="space-y-5 p-4 lg:p-8">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <Metric title="Всего шаблонов" value={String(adminDocumentTemplates.length)} />
          <Metric title="Активные" value={String(activeCount)} />
          <Metric title="Договоры" value={String(contracts)} />
          <Metric title="Поручения" value={String(orders)} />
          <Metric title="Акты" value={String(reports)} />
        </div>

        <div className="rounded-lg border bg-white p-4">
          <div className="grid gap-3 lg:grid-cols-3">
            <select className="h-10 rounded-md border bg-white px-3 text-sm">
              <option>Все типы документов</option>
              <option>contract</option>
              <option>offer_join_statement</option>
              <option>principal_order</option>
              <option>agent_report</option>
              <option>package</option>
              <option>additional</option>
            </select>
            <select className="h-10 rounded-md border bg-white px-3 text-sm">
              <option>Все направления</option>
              <option>cfa</option>
              <option>crypto</option>
              <option>cars</option>
              <option>ved</option>
              <option>common</option>
            </select>
            <select className="h-10 rounded-md border bg-white px-3 text-sm">
              <option>Все типы клиентов</option>
              <option>physical_person</option>
              <option>individual_entrepreneur</option>
              <option>legal_entity</option>
              <option>any</option>
            </select>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {tabs.map((tab, index) => (
              <button key={tab} className={index === 3 ? "rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground" : "rounded-md border px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted"}>
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border bg-white">
          <div className="grid min-w-[1280px] grid-cols-[1.6fr_1fr_.8fr_.8fr_.9fr_.9fr_.7fr_.8fr_1fr_.8fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>Название шаблона</div>
            <div>Тип</div>
            <div>Направление</div>
            <div>Версия</div>
            <div>Юрлицо / исполнитель</div>
            <div>Клиентский тип</div>
            <div>Состав</div>
            <div>Переменных</div>
            <div>Активен</div>
            <div>Последнее обновление</div>
          </div>
          {adminDocumentTemplates.map((template) => (
            <Link
              key={template.id}
              href={`/admin/document-templates/${template.id}`}
              className="grid min-w-[1280px] grid-cols-[1.6fr_1fr_.8fr_.8fr_.9fr_.9fr_.7fr_.8fr_1fr_.8fr] items-center border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
            >
              <div>
                <div className="font-medium text-slate-950">{template.name}</div>
                <div className="text-xs text-muted-foreground">{template.slug}</div>
              </div>
              <div>{documentTemplateTypeLabels[template.documentType]}</div>
              <div>{directionLabels[template.direction]}</div>
              <div>{template.version}</div>
              <div>{template.executor}</div>
              <div>{clientTypeLabels[template.clientType]}</div>
              <div>{compositionTypeLabels[template.compositionType]}</div>
              <div>{template.variables.length}</div>
              <div><AdminStatusBadge status={template.isActive ? "active" : "inactive"} label={template.isActive ? "Да" : "Нет"} /></div>
              <div className="text-muted-foreground">{template.updatedAt}</div>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
