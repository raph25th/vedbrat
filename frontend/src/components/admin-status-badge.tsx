import { documentStatusLabels } from "@/lib/admin-mock-data";
import { dealStatusLabels } from "@/lib/statuses";
import { cn } from "@/lib/utils";

const tones: Record<string, string> = {
  success: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  danger: "border-red-200 bg-red-50 text-red-700",
  info: "border-sky-200 bg-sky-50 text-sky-700",
  neutral: "border-slate-200 bg-slate-50 text-slate-700"
};

function toneForStatus(status: string) {
  if (["completed", "executed", "report_signed", "checked", "active", "bank_details_approved", "personal_data_approved"].includes(status)) {
    return "success";
  }
  if (["client_data_submitted", "bank_details_submitted", "documents_generated", "issued_to_client", "uploaded"].includes(status)) {
    return "info";
  }
  if (status.includes("waiting") || status.includes("required") || ["requested", "preparing", "rate_required"].includes(status)) {
    return "warning";
  }
  if (["needs_correction", "replacement_required", "cancelled", "pending"].includes(status)) {
    return "danger";
  }
  return "neutral";
}

export function AdminStatusBadge({ status, label }: { status: string; label?: string }) {
  const resolvedLabel = label || documentStatusLabels[status] || dealStatusLabels[status] || status;
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium", tones[toneForStatus(status)])}>
      {resolvedLabel}
    </span>
  );
}

export function RequiredActionBadge({ action }: { action?: string | null }) {
  if (!action || action === "—") {
    return <AdminStatusBadge status="neutral" label="Нет действий" />;
  }
  return (
    <span className="inline-flex items-center rounded-md border border-orange-200 bg-orange-50 px-2 py-1 text-xs font-medium text-orange-800">
      {action}
    </span>
  );
}
