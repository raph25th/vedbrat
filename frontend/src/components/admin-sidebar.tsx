"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, ClipboardList, FileText, HandCoins, MessageSquare, Users, UserCog, Network } from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/admin/dashboard", label: "Дашборд", icon: BarChart3 },
  { href: "/admin/deals", label: "Сделки", icon: HandCoins },
  { href: "/admin/document-requests", label: "Заявки на документы", icon: ClipboardList },
  { href: "/admin/cfa-deals", label: "ЦФА-сделки", icon: HandCoins },
  { href: "/admin/document-templates", label: "Шаблоны документов", icon: FileText },
  { href: "/admin/clients", label: "Клиенты", icon: Users },
  { href: "/admin/telegram-chats", label: "Telegram-группы", icon: MessageSquare },
  { href: "/admin/referrals", label: "Рефералы", icon: Network },
  { href: "/admin/users", label: "Пользователи", icon: UserCog }
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 border-r bg-white lg:block">
      <div className="border-b px-5 py-4">
        <div className="text-lg font-semibold">VEDBRAT CRM</div>
        <div className="text-xs text-muted-foreground">Операционный центр ЦФА</div>
      </div>
      <nav className="space-y-1 p-3">
        {nav.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              href={item.href}
              key={item.href}
              className={cn(
                "flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground",
                active && "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground"
              )}
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
