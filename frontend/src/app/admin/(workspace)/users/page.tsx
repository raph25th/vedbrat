import { ShieldCheck } from "lucide-react";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { users } from "@/lib/sample-data";

export default function UsersPage() {
  return (
    <>
      <PageHeader title="Пользователи" description="Роли client, manager, admin, director и доступ на подключение бота." action={<Button>Создать</Button>} />
      <div className="p-4 lg:p-8">
        <div className="overflow-hidden rounded-lg border bg-white">
          {users.map((user) => (
            <div key={user.id} className="grid gap-3 border-b p-4 text-sm last:border-b-0 md:grid-cols-[1.3fr_1fr_1fr]">
              <div>
                <div className="font-medium">{user.name}</div>
                <div className="text-muted-foreground">{user.email}</div>
              </div>
              <div><Badge label={user.role} /></div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <ShieldCheck className="h-4 w-4" />
                {user.is_allowed_to_connect_bot ? "Может подключать бота" : "Без доступа к подключению"}
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
