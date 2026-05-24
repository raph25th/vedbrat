import { cn } from "@/lib/utils";
import { statusTone } from "@/lib/statuses";

const toneClass = {
  success: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warning: "border-amber-200 bg-amber-50 text-amber-800",
  danger: "border-red-200 bg-red-50 text-red-700",
  neutral: "border-slate-200 bg-slate-50 text-slate-700"
};

export function Badge({ label, status, className }: { label: string; status?: string; className?: string }) {
  const tone = status ? statusTone(status) : "neutral";
  return (
    <span className={cn("inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium", toneClass[tone], className)}>
      {label}
    </span>
  );
}
