import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CFA CRM",
  description: "CFA CRM and Telegram Mini App MVP"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
