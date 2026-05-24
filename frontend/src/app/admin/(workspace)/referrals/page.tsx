import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { referrals } from "@/lib/sample-data";

export default function ReferralsPage() {
  return (
    <>
      <PageHeader title="Рефералы" description="Ставки, базы расчета и статусы партнеров." action={<Button>Добавить</Button>} />
      <div className="p-4 lg:p-8">
        <div className="overflow-hidden rounded-lg border bg-white">
          {referrals.map((referral) => (
            <div key={referral.id} className="grid gap-3 border-b p-4 text-sm last:border-b-0 md:grid-cols-[1.5fr_1fr_1fr]">
              <div className="font-medium">{referral.name}</div>
              <div>{referral.default_fee_type}</div>
              <div>{referral.default_fee_value}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
