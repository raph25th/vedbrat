"use client";

import { FormEvent, Suspense, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiPost, type DocumentRequestRecord } from "@/lib/api";

const initialForm = {
  ru_name: "",
  inn: "",
  birth_date: "",
  phone: "",
  email: "",
  registration_address: "",
  passport_series_number: "",
  passport_issued_by: "",
  passport_issue_date: "",
  passport_department_code: "",
  bank_name: "",
  bank_account: "",
  bank_corr_account: "",
  bank_bik: "",
  bank_inn: "",
  bank_kpp: "",
  full_payment_amount: "",
  currency: "RUB",
  agent_fee_percent: "0.1",
  crypto_asset: "USDT",
  wallet_address: "",
  client_comment: "",
  telegram_id: "",
  telegram_username: ""
};

export default function DocumentRequestPage() {
  return (
    <Suspense fallback={<main className="px-4 py-5 text-sm text-slate-400">Загрузка...</main>}>
      <DocumentRequestForm />
    </Suspense>
  );
}

function DocumentRequestForm() {
  const searchParams = useSearchParams();
  const [form, setForm] = useState({
    ...initialForm,
    telegram_id: searchParams.get("tg_id") || "",
    telegram_username: searchParams.get("username") || ""
  });
  const [submittedId, setSubmittedId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const totals = useMemo(() => {
    const total = Number(form.full_payment_amount || 0);
    const percent = Number(form.agent_fee_percent || 0);
    if (!total || percent < 0) {
      return { supplier_payment_equal: 0, agent_fee_amount: 0 };
    }
    const supplier = total / (1 + percent / 100);
    const roundedSupplier = Math.round(supplier * 100) / 100;
    return {
      supplier_payment_equal: roundedSupplier,
      agent_fee_amount: Math.round((total - roundedSupplier) * 100) / 100
    };
  }, [form.full_payment_amount, form.agent_fee_percent]);

  function update(key: keyof typeof form, value: string) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    const source = searchParams.get("source");
    const requestSource = source === "bot" ? "bot" : source || "mini_app";
    const payload = {
      status: "submitted",
      request_source: requestSource,
      client_type: "individual",
      deal_type: "crypto",
      document_package_type: "offer_crypto_individual",
      offer_version: "1.002",
      offer_date: "2026-05-18",
      currency: form.currency || "RUB",
      full_payment_amount: form.full_payment_amount ? Number(form.full_payment_amount) : null,
      agent_fee_percent: form.agent_fee_percent ? Number(form.agent_fee_percent) : 0.1,
      supplier_payment_equal: totals.supplier_payment_equal || null,
      agent_fee_amount: totals.agent_fee_amount || null,
      crypto_asset: form.crypto_asset || "USDT",
      wallet_address: form.wallet_address,
      client_comment: form.client_comment,
      payload_json: {
        ...form,
        client_type: "individual",
        deal_type: "crypto",
        document_package_type: "offer_crypto_individual",
        offer_version: "1.002",
        offer_date: "2026-05-18",
        request_source: requestSource,
        supplier_payment_equal: totals.supplier_payment_equal,
        agent_fee_amount: totals.agent_fee_amount
      }
    };
    const created = await apiPost<DocumentRequestRecord>("/document-requests", payload);
    setSubmitting(false);
    if (created) {
      setSubmittedId(created.id);
    }
  }

  if (submittedId) {
    return (
      <main className="space-y-4 px-4 py-5">
        <section className="mini-card rounded-xl border border-slate-700/60 bg-slate-900/70 p-5">
          <h1 className="text-2xl font-semibold text-slate-50">Заявка отправлена</h1>
          <p className="mt-2 text-sm text-slate-400">Заявка отправлена на проверку. Документы подготовит специалист.</p>
        </section>
      </main>
    );
  }

  return (
    <main className="space-y-4 px-4 py-5 pb-24">
      <header className="space-y-2 pt-1">
        <h1 className="text-2xl font-semibold text-slate-50">Заявка на подготовку документов</h1>
        <p className="text-sm text-slate-400">Физическое лицо / крипта / USDT / оферта.</p>
      </header>
      <form onSubmit={submit} className="space-y-4">
        <Section title="1. Данные клиента">
          <Field label="ФИО" value={form.ru_name} onChange={(value) => update("ru_name", value)} required />
          <Field label="ИНН" value={form.inn} onChange={(value) => update("inn", value)} />
          <Field label="Дата рождения" type="date" value={form.birth_date} onChange={(value) => update("birth_date", value)} />
          <Field label="Телефон" value={form.phone} onChange={(value) => update("phone", value)} />
          <Field label="Email" type="email" value={form.email} onChange={(value) => update("email", value)} />
          <TextField label="Адрес регистрации" value={form.registration_address} onChange={(value) => update("registration_address", value)} />
        </Section>

        <Section title="2. Паспорт">
          <Field label="Серия и номер паспорта" value={form.passport_series_number} onChange={(value) => update("passport_series_number", value)} />
          <Field label="Кем выдан" value={form.passport_issued_by} onChange={(value) => update("passport_issued_by", value)} />
          <Field label="Дата выдачи" type="date" value={form.passport_issue_date} onChange={(value) => update("passport_issue_date", value)} />
          <Field label="Код подразделения" value={form.passport_department_code} onChange={(value) => update("passport_department_code", value)} />
        </Section>

        <Section title="3. Банковские реквизиты">
          <Field label="Наименование банка" value={form.bank_name} onChange={(value) => update("bank_name", value)} />
          <Field label="Расчетный счет" value={form.bank_account} onChange={(value) => update("bank_account", value)} />
          <Field label="Корреспондентский счет" value={form.bank_corr_account} onChange={(value) => update("bank_corr_account", value)} />
          <Field label="БИК" value={form.bank_bik} onChange={(value) => update("bank_bik", value)} />
          <Field label="ИНН банка" value={form.bank_inn} onChange={(value) => update("bank_inn", value)} />
          <Field label="КПП банка" value={form.bank_kpp} onChange={(value) => update("bank_kpp", value)} />
        </Section>

        <Section title="4. Операция">
          <Field label="Сумма оплаты" type="number" value={form.full_payment_amount} onChange={(value) => update("full_payment_amount", value)} />
          <Field label="Валюта" value={form.currency} onChange={(value) => update("currency", value)} />
          <Field label="Комиссия агента %" type="number" value={form.agent_fee_percent} onChange={(value) => update("agent_fee_percent", value)} />
          <Readonly label="Сумма на исполнение поручения" value={totals.supplier_payment_equal.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} />
          <Readonly label="Агентское вознаграждение" value={totals.agent_fee_amount.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} />
          <Field label="Актив" value={form.crypto_asset} onChange={(value) => update("crypto_asset", value)} />
          <Field label="Адрес электронного кошелька" value={form.wallet_address} onChange={(value) => update("wallet_address", value)} />
          <TextField label="Комментарий клиента" value={form.client_comment} onChange={(value) => update("client_comment", value)} />
        </Section>

        <Button type="submit" className="w-full" disabled={submitting}>
          <Send className="h-4 w-4" />
          {submitting ? "Отправляем..." : "Отправить заявку"}
        </Button>
      </form>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mini-card space-y-3 rounded-xl border border-slate-700/60 bg-slate-900/70 p-4">
      <h2 className="text-base font-semibold text-slate-50">{title}</h2>
      <div className="space-y-3">{children}</div>
    </section>
  );
}

function Field({ label, value, onChange, type = "text", required = false }: { label: string; value: string; onChange: (value: string) => void; type?: string; required?: boolean }) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Input type={type} value={value} onChange={(event) => onChange(event.target.value)} required={required} />
    </div>
  );
}

function TextField({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Textarea value={value} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}

function Readonly({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-700/60 bg-slate-950/35 p-3 text-sm">
      <div className="text-xs text-slate-400">{label}</div>
      <div className="mt-1 font-semibold text-slate-100">{value}</div>
    </div>
  );
}
