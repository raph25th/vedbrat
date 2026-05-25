import Link from "next/link";
import { notFound } from "next/navigation";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { apiGet, type ClientRecord } from "@/lib/api";

const fields: Array<[string, keyof ClientRecord]> = [
  ["Client type", "client_type"],
  ["RU name", "ru_name"],
  ["EN name", "en_name"],
  ["INN", "inn"],
  ["Phone", "phone"],
  ["Email", "email"],
  ["Telegram ID", "telegram_id"],
  ["Telegram username", "telegram_username"],
  ["Citizenship", "citizenship"],
  ["Tax residency", "tax_residency_country"],
  ["Birth date", "birth_date"],
  ["Birth place", "birth_place"],
  ["Passport type", "passport_type"],
  ["Passport", "passport_series_number"],
  ["Passport issue date", "passport_issue_date"],
  ["Passport issued by", "passport_issued_by"],
  ["Department code", "passport_department_code"],
  ["Passport expires", "passport_expires_at"],
  ["Registration address", "registration_address"],
  ["Residential address", "residential_address"],
  ["Bank", "bank_name"],
  ["Bank account", "bank_account"],
  ["Correspondent account", "bank_corr_account"],
  ["BIK", "bank_bik"],
  ["Bank INN", "bank_inn"],
  ["Bank KPP", "bank_kpp"]
];

export default async function ClientPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const client = await apiGet<ClientRecord>(`/clients/${id}`);
  if (!client) notFound();

  return (
    <>
      <PageHeader
        title={client.ru_name || client.full_name_ru || "Client"}
        description="Real client record from CRM API."
        action={
          <Link href="/admin/clients">
            <Button variant="outline">Back to clients</Button>
          </Link>
        }
      />
      <div className="p-4 lg:p-8">
        <div className="grid gap-3 rounded-lg border bg-white p-4 md:grid-cols-2 xl:grid-cols-3">
          {fields.map(([label, key]) => (
            <div key={key} className="rounded-md border bg-muted/20 p-3 text-sm">
              <div className="text-xs text-muted-foreground">{label}</div>
              <div className="mt-1 font-medium text-slate-950">{String(client[key] || "Not provided")}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
