import { clientStatusLabels, dealStatusLabels } from "@/lib/statuses";
import { cn } from "@/lib/utils";

function toneForStatus(status: string) {
  if (["completed", "report_signed", "executed", "active", "checked", "bank_details_approved", "personal_data_approved"].includes(status)) {
    return "border-emerald-400/30 bg-emerald-500/15 text-emerald-300";
  }
  if (["documents_generated", "issued", "issued_to_client"].includes(status)) {
    return "border-cyan-400/30 bg-cyan-500/15 text-cyan-300";
  }
  if (["client_data_submitted", "bank_details_submitted", "personal_data_submitted"].includes(status)) {
    return "border-sky-400/30 bg-sky-500/15 text-sky-300";
  }
  if (["waiting_for_client_payment", "waiting_for_signature", "waiting_report_signature", "documents_requested", "requested", "preparing"].includes(status)) {
    return "border-amber-400/35 bg-amber-500/15 text-amber-300";
  }
  if (status.includes("required") || status === "needs_correction" || status === "replacement_required" || status === "cancelled") {
    return "border-orange-400/35 bg-orange-500/15 text-orange-300";
  }
  return "border-slate-400/25 bg-slate-500/12 text-slate-300";
}

export function MiniStatusBadge({ status, type = "deal" }: { status: string; type?: "deal" | "client" }) {
  const documentStatusLabels: Record<string, string> = {
    requested: "Запрошен",
    preparing: "Готовится",
    issued: "Выдан клиенту",
    issued_to_client: "Выдан клиенту",
    waiting_for_signature: "Ожидает подписи",
    signed_uploaded: "Подписанный файл загружен",
    checked: "Проверен",
    replacement_required: "Требует замены"
  };
  const labels = type === "client" ? clientStatusLabels : { ...dealStatusLabels, ...documentStatusLabels };
  return (
    <span className={cn("inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] font-semibold", toneForStatus(status))}>
      {labels[status] || status}
    </span>
  );
}
