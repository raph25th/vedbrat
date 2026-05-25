import Link from "next/link";
import { FileText, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function MiniAppHomePage() {
  return (
    <main className="space-y-4 px-4 py-5">
      <header className="space-y-3 pt-1">
        <div className="text-xs font-medium uppercase tracking-wide text-teal-300/80">VEDBRAT CRM</div>
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold leading-tight text-slate-50">Заявка на подготовку документов</h1>
          <p className="text-sm leading-6 text-slate-400">
            Отправьте данные менеджеру. Номер договора и счет-поручения присваиваются вручную после проверки в CRM.
          </p>
        </div>
      </header>

      <section className="mini-card space-y-4 rounded-xl border border-slate-700/60 bg-slate-900/70 p-5">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-teal-500/12 text-teal-300">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div className="space-y-1">
            <h2 className="text-base font-semibold text-slate-50">Проверка в CRM</h2>
            <p className="text-sm leading-6 text-slate-400">
              Заявка попадет в админку, где менеджер проверит данные и подготовит документы.
            </p>
          </div>
        </div>
        <Link href="/app/document-request">
          <Button className="w-full justify-center">
            <FileText className="h-4 w-4" />
            Заполнить заявку
          </Button>
        </Link>
      </section>
    </main>
  );
}
