import { AppShell } from "@/components/app-shell";
import "./mini-app.css";

export default function MiniAppLayout({ children }: { children: React.ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
