"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiGet, apiPost, type ClientRecord } from "@/lib/api";

const emptyClient = {
  client_type: "individual",
  ru_name: "",
  en_name: "",
  inn: "",
  phone: "",
  email: "",
  telegram_id: "",
  telegram_username: ""
};

export default function ClientsPage() {
  const [clients, setClients] = useState<ClientRecord[]>([]);
  const [form, setForm] = useState(emptyClient);
  const [loading, setLoading] = useState(true);

  async function loadClients() {
    setLoading(true);
    const records = await apiGet<ClientRecord[]>("/clients");
    setClients(records || []);
    setLoading(false);
  }

  useEffect(() => {
    let active = true;
    apiGet<ClientRecord[]>("/clients").then((records) => {
      if (active) {
        setClients(records || []);
        setLoading(false);
      }
    });
    return () => {
      active = false;
    };
  }, []);

  async function submitClient(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = Object.fromEntries(Object.entries(form).filter(([, value]) => value !== ""));
    const created = await apiPost<ClientRecord>("/clients", payload);
    if (created) {
      setForm(emptyClient);
      await loadClients();
    }
  }

  return (
    <>
      <PageHeader title="Клиенты" description="Реальные клиенты из CRM API. Фейковые записи и демо-данные не показываются." />
      <div className="grid gap-5 p-4 lg:grid-cols-[360px_1fr] lg:p-8">
        <form onSubmit={submitClient} className="space-y-4 rounded-lg border bg-white p-4">
          <div>
            <h2 className="text-base font-semibold text-slate-950">Создать клиента</h2>
            <p className="mt-1 text-sm text-muted-foreground">Минимальная карточка клиента для MVP заявок.</p>
          </div>
          <div className="space-y-2">
            <Label>Тип клиента</Label>
            <select
              className="h-10 w-full rounded-md border bg-white px-3 text-sm"
              value={form.client_type}
              onChange={(event) => setForm({ ...form, client_type: event.target.value })}
            >
              <option value="individual">Физлицо</option>
            </select>
          </div>
          <Field label="ФИО" value={form.ru_name} onChange={(ru_name) => setForm({ ...form, ru_name })} required />
          <Field label="ФИО EN" value={form.en_name} onChange={(en_name) => setForm({ ...form, en_name })} />
          <Field label="INN" value={form.inn} onChange={(inn) => setForm({ ...form, inn })} />
          <Field label="Телефон" value={form.phone} onChange={(phone) => setForm({ ...form, phone })} />
          <Field label="Email" type="email" value={form.email} onChange={(email) => setForm({ ...form, email })} />
          <Field label="Telegram ID" value={form.telegram_id} onChange={(telegram_id) => setForm({ ...form, telegram_id })} />
          <Field label="Telegram username" value={form.telegram_username} onChange={(telegram_username) => setForm({ ...form, telegram_username })} />
          <Button type="submit" className="w-full">Создать клиента</Button>
        </form>

        <div className="overflow-hidden rounded-lg border bg-white">
          <div className="grid min-w-[900px] grid-cols-[1.4fr_.8fr_1fr_1fr_1fr_1fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>ФИО</div>
            <div>Тип клиента</div>
            <div>ИНН</div>
            <div>Телефон</div>
            <div>Email</div>
            <div>Дата создания</div>
          </div>
          {loading ? <EmptyRow text="Загрузка клиентов..." /> : null}
          {!loading && clients.length === 0 ? <EmptyRow text="Пока нет клиентов. Клиенты появятся после создания заявки или ручного добавления." /> : null}
          {clients.map((client) => (
            <Link
              href={`/admin/clients/${client.id}`}
              key={client.id}
              className="grid min-w-[900px] grid-cols-[1.4fr_.8fr_1fr_1fr_1fr_1fr] gap-3 border-b px-4 py-4 text-sm last:border-b-0 hover:bg-muted/40"
            >
              <div className="font-medium">{client.ru_name || client.full_name_ru || "Без имени"}</div>
              <div>{client.client_type}</div>
              <div>{client.inn || "Не указан"}</div>
              <div>{client.phone || "Не указан"}</div>
              <div>{client.email || "Не указан"}</div>
              <div>{client.created_at ? new Date(client.created_at).toLocaleString("ru-RU") : "Не указана"}</div>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  required = false
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <div className="space-y-2">
      <Label>{label}</Label>
      <Input type={type} value={value} onChange={(event) => onChange(event.target.value)} required={required} />
    </div>
  );
}

function EmptyRow({ text }: { text: string }) {
  return <div className="px-4 py-8 text-center text-sm text-muted-foreground">{text}</div>;
}
