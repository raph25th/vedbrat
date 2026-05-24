import Link from "next/link";
import { BarChart3, HandCoins, MessageSquare, Users, UserCog, Network } from "lucide-react";

const nav = [
  { href: "/admin/dashboard", label: "Дашборд", icon: BarChart3 },
  { href: "/admin/cfa-deals", label: "CFA-сделки", icon: HandCoins },
  { href: "/admin/clients", label: "Клиенты", icon: Users },
  { href: "/admin/telegram-chats", label: "Telegram", icon: MessageSquare },
  { href: "/admin/referrals", label: "Рефералы", icon: Network },
  { href: "/admin/users", label: "Пользователи", icon: UserCog }
];

export function AdminSidebar() {
  return (
    <aside className="hidden w-64 shrink-0 border-r bg-white lg:block">
      <div className="border-b px-5 py-4">
        <div className="text-lg font-semibold">CFA CRM</div>
        <div className="text-xs text-muted-foreground">Admin workspace</div>
      </div>
      <nav className="space-y-1 p-3">
        {nav.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              href={item.href}
              key={item.href}
              className="flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
