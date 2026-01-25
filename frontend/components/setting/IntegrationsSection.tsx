"use client";

import Image from "next/image";
import clsx from "clsx";
import { useTranslations } from "next-intl";
import { SectionCard } from "./SectionCard";

type Props = {
  providersConnected: {
    google: boolean;
    github: boolean;
  };
};

export function IntegrationsSection({ providersConnected }: Props) {
  const t = useTranslations("setting");

  return (
    <SectionCard
      title={t("integrations")}
      description={t("integrationsDescription")}
    >
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {(["google", "github"] as const).map((p) => (
          <div key={p} className="rounded-2xl bg-[var(--bg-hover)] p-4">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <Image src={`/login/${p}.png`} alt={p} width={24} height={24} />
                <div>
                  <div className="text-sm font-medium">
                    {p === "google" ? "Google" : "GitHub"}
                  </div>
                  <div className="text-xs text-[var(--text-muted)]">
                    {t("oauth")}
                  </div>
                </div>
              </div>
              <span
                className={clsx(
                  "rounded-full px-3 py-1 text-xs",
                  providersConnected[p]
                    ? "bg-[var(--bg-card)] text-[var(--foreground)]"
                    : "bg-[var(--background)] text-[var(--text-faint)]",
                )}
              >
                {providersConnected[p] ? t("connected") : t("notConnected")}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-[var(--text-faint)]">
        {t("integrationsNote")}
      </div>
    </SectionCard>
  );
}
