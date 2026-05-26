"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { PageHeader } from "@/components/page-header";
import { AdminStatusBadge } from "@/components/admin-status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiDelete, apiGet, apiPost, type LiquidityPurchaseLotRecord } from "@/lib/api";
import { money } from "@/lib/utils";

const emptyForm = {
  asset: "USDT",
  purchase_amount_rub: "",
  purchase_rate: "",
  source: "",
  comment: ""
};

export default function LiquidityPurchasesPage() {
  const [lots, setLots] = useState<LiquidityPurchaseLotRecord[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const calculatedVolume = useMemo(() => {
    const amount = Number(form.purchase_amount_rub);
    const rate = Number(form.purchase_rate);
    if (!amount || !rate) return "";
    return (amount / rate).toLocaleString("ru-RU", { maximumFractionDigits: 6 });
  }, [form.purchase_amount_rub, form.purchase_rate]);

  async function loadLots() {
    setLoading(true);
    const records = await apiGet<LiquidityPurchaseLotRecord[]>("/liquidity-purchases");
    setLots(records || []);
    setLoading(false);
  }

  useEffect(() => {
    let active = true;
    async function loadInitialLots() {
      const records = await apiGet<LiquidityPurchaseLotRecord[]>("/liquidity-purchases");
      if (!active) return;
      setLots(records || []);
      setLoading(false);
    }
    void loadInitialLots();
    return () => {
      active = false;
    };
  }, []);

  async function submitLot(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const created = await apiPost<LiquidityPurchaseLotRecord>("/liquidity-purchases", {
      asset: form.asset || "USDT",
      purchase_amount_rub: Number(form.purchase_amount_rub),
      purchase_rate: Number(form.purchase_rate),
      source: form.source || null,
      comment: form.comment || null
    });
    if (!created) {
      setError("Не удалось создать лот ликвидности.");
      return;
    }
    setForm(emptyForm);
    await loadLots();
  }

  async function deleteLot(id: number) {
    setError("");
    const deleted = await apiDelete(`/liquidity-purchases/${id}`);
    if (!deleted) {
      setError("Удалить можно только неиспользованный лот.");
      return;
    }
    await loadLots();
  }

  return (
    <>
      <PageHeader title="Покупка ликвидности" description="Лоты купленной ликвидности и доступные остатки для закрытия клиентских сделок." />
      <div className="grid gap-5 p-4 lg:grid-cols-[360px_1fr] lg:p-8">
        <form onSubmit={submitLot} className="h-fit space-y-4 rounded-lg border bg-white p-4">
          <div>
            <h2 className="text-base font-semibold text-slate-950">Создать лот</h2>
            <p className="mt-1 text-sm text-muted-foreground">Объем актива считается как сумма покупки / курс.</p>
          </div>
          <Field label="Актив" value={form.asset} onChange={(asset) => setForm({ ...form, asset })} />
          <Field label="Сумма покупки RUB" type="number" value={form.purchase_amount_rub} onChange={(purchase_amount_rub) => setForm({ ...form, purchase_amount_rub })} required />
          <Field label="Курс покупки" type="number" value={form.purchase_rate} onChange={(purchase_rate) => setForm({ ...form, purchase_rate })} required />
          <div className="rounded-md border bg-muted/20 p-3 text-sm">
            <div className="text-xs text-muted-foreground">Расчетный объем</div>
            <div className="mt-1 font-medium text-slate-950">{calculatedVolume || "Не рассчитан"}</div>
          </div>
          <Field label="Источник" value={form.source} onChange={(source) => setForm({ ...form, source })} />
          <div className="space-y-2">
            <Label>Комментарий</Label>
            <Textarea value={form.comment} onChange={(event) => setForm({ ...form, comment: event.target.value })} />
          </div>
          {error ? <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
          <Button type="submit" className="w-full">Создать лот</Button>
        </form>

        <div className="overflow-x-auto rounded-lg border bg-white">
          <div className="grid min-w-[1180px] grid-cols-[.5fr_1fr_.8fr_1fr_.8fr_1fr_1fr_1fr_.9fr_.8fr] border-b bg-muted/50 px-4 py-3 text-xs font-medium uppercase text-muted-foreground">
            <div>ID</div>
            <div>Дата</div>
            <div>Актив</div>
            <div>Сумма RUB</div>
            <div>Курс</div>
            <div>Куплено</div>
            <div>Использовано</div>
            <div>Остаток</div>
            <div>Статус</div>
            <div>Действия</div>
          </div>
          {loading ? <EmptyRow text="Загрузка лотов..." /> : null}
          {!loading && lots.length === 0 ? <EmptyRow text="Пока нет лотов ликвидности." /> : null}
          {lots.map((lot) => (
            <div key={lot.id} className="grid min-w-[1180px] grid-cols-[.5fr_1fr_.8fr_1fr_.8fr_1fr_1fr_1fr_.9fr_.8fr] items-center border-b px-4 py-4 text-sm last:border-b-0">
              <div className="font-medium">#{lot.id}</div>
              <div className="text-muted-foreground">{new Date(lot.created_at).toLocaleString("ru-RU")}</div>
              <div>{lot.asset}</div>
              <div>{money(Number(lot.purchase_amount_rub))}</div>
              <div>{lot.purchase_rate}</div>
              <div>{Number(lot.purchased_asset_volume).toLocaleString("ru-RU", { maximumFractionDigits: 6 })}</div>
              <div>{Number(lot.used_asset_volume).toLocaleString("ru-RU", { maximumFractionDigits: 6 })}</div>
              <div>{Number(lot.remaining_asset_volume).toLocaleString("ru-RU", { maximumFractionDigits: 6 })}</div>
              <div><AdminStatusBadge status={lot.status} /></div>
              <div>
                <Button type="button" variant="outline" size="sm" onClick={() => deleteLot(lot.id)} disabled={Number(lot.used_asset_volume) > 0}>
                  Удалить
                </Button>
              </div>
            </div>
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
