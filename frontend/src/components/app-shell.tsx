"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText, Home } from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/app", label: "Главная", icon: Home },
  { href: "/app/document-request", label: "Заявка", icon: FileText }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="mini-app">
      <div className="mini-screen">
        {children}
        <nav className="mini-nav fixed inset-x-0 bottom-0 z-30 mx-auto grid h-[72px] max-w-[430px] grid-cols-2 border-t px-2 pb-2 pt-1">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = item.href === "/app" ? pathname === "/app" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex min-w-0 flex-col items-center justify-center gap-1 rounded-lg text-[11px] font-medium text-slate-500 transition",
                  active && "bg-teal-500/12 text-teal-300"
                )}
              >
                <Icon className="h-5 w-5" />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
