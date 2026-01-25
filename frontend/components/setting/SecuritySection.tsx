"use client";

import { useTranslations } from "next-intl";
import { SectionCard } from "./SectionCard";

export function SecuritySection() {
  const t = useTranslations("setting");

  return (
    <SectionCard title={t("security")} description={t("securityDescription")}>
      <div className="rounded-2xl bg-[var(--bg-hover)] p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-sm font-medium">{t("deleteAccount")}</div>
            <div className="mt-1 text-sm text-[var(--text-muted)]">
              {t("deleteAccountDescription")}
            </div>
          </div>

          <button
            disabled
            className="rounded-xl bg-[var(--background)] px-4 py-2 text-sm text-[var(--text-faint)] opacity-70 cursor-not-allowed"
          >
            {t("disabled")}
          </button>
        </div>

        <div className="mt-3 text-xs text-[var(--text-faint)]">
          {t("securityNote")}
        </div>
      </div>
    </SectionCard>
  );
}
