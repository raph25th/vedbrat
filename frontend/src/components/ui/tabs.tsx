"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";

export function Tabs({
  tabs
}: {
  tabs: Array<{ value: string; label: string; content: React.ReactNode }>;
}) {
  const [active, setActive] = useState(tabs[0]?.value);
  const current = tabs.find((tab) => tab.value === active) || tabs[0];

  return (
    <div className="space-y-5">
      <div className="flex gap-1 overflow-x-auto rounded-md border bg-white p-1">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            className={cn(
              "h-9 whitespace-nowrap rounded px-3 text-sm font-medium text-muted-foreground transition",
              active === tab.value && "bg-primary text-primary-foreground"
            )}
            onClick={() => setActive(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div>{current.content}</div>
    </div>
  );
}
