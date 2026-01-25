"use client";

import { useTranslations } from "next-intl";

export function ActionPanel() {
  const t = useTranslations("chat");

  return (
    <aside
      className="
        relative
        h-full
        bg-[var(--bg-side)]
        z-20
      "
    >
      <div className="p-4 space-y-4">
        <div
          className="
            rounded-2xl
            bg-[var(--bg-card)]
            p-4
            text-sm
            text-[var(--text-muted)]
            shadow-[0_4px_12px_rgba(0,0,0,0.25)]
          "
        >
          {t("actionPanel")}
        </div>
      </div>
    </aside>
  );
}
