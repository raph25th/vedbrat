import { Badge } from "@/components/ui/badge";
import { clientStatusLabels, dealStatusLabels } from "@/lib/statuses";

export function DealStatusBadge({ status }: { status: string }) {
  return <Badge status={status} label={dealStatusLabels[status] || status} />;
}

export function ClientStatusBadge({ status }: { status: string }) {
  return <Badge status={status} label={clientStatusLabels[status] || status} />;
}
