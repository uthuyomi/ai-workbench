"use client";

import { useTranslations } from "next-intl";
import { SectionCard } from "./SectionCard";
import { Row } from "./Row";
import { Divider } from "./Divider";

export function AboutSection() {
  const t = useTranslations("setting");

  return (
    <SectionCard title={t("about")} description={t("aboutDescription")}>
      <div className="rounded-2xl bg-[var(--bg-hover)] p-4">
        <Row label={t("app")} value={t("appName")} />
        <Divider />
        <Row
          label={t("stack")}
          value={
            <div className="space-y-1">
              <div>{t("stackNext")}</div>
              <div>{t("stackSupabase")}</div>
              <div>{t("stackTailwind")}</div>
            </div>
          }
        />
        <Divider />
        <Row
          label={t("purpose")}
          value={
            <div className="space-y-1">
              <div>{t("purposeLine1")}</div>
              <div className="text-xs text-[var(--text-muted)]">
                {t("purposeLine2")}
              </div>
            </div>
          }
        />
      </div>

      <div className="mt-3 text-xs text-[var(--text-faint)]">
        {t("aboutNote")}
      </div>
    </SectionCard>
  );
}
