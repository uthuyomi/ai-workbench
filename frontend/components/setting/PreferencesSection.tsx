"use client";

import clsx from "clsx";
import { useTranslations } from "next-intl";
import { SectionCard } from "./SectionCard";

type ThemeMode = "dark" | "light" | "gray";
type LangMode = "ja" | "en";

type Props = {
  theme: ThemeMode;
  lang: LangMode;
  onChangeTheme: (t: ThemeMode) => void;
  onChangeLang: (l: LangMode) => void;
};

export function PreferencesSection({
  theme,
  lang,
  onChangeTheme,
  onChangeLang,
}: Props) {
  const t = useTranslations("setting");

  return (
    <SectionCard
      title={t("preferences")}
      description={t("preferencesDescription")}
    >
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {/* =====================
            Language
            ===================== */}
        <div className="rounded-2xl bg-[var(--bg-hover)] p-4">
          <div className="text-sm font-medium">{t("language")}</div>
          <div className="mt-1 text-sm text-[var(--text-muted)]">
            {t("languageDescription")}
          </div>

          <div className="mt-4 flex items-center gap-2">
            {(["ja", "en"] as const).map((l) => (
              <button
                key={l}
                onClick={() => onChangeLang(l)}
                className={clsx(
                  "flex-1 rounded-xl px-4 py-2 text-sm transition",
                  lang === l
                    ? "bg-[var(--bg-card)] shadow-[0_6px_18px_rgba(0,0,0,0.25)]"
                    : "bg-[var(--background)] hover:opacity-90",
                )}
              >
                {l === "ja" ? t("japanese") : t("english")}
              </button>
            ))}
          </div>

          <div className="mt-3 text-xs text-[var(--text-faint)]">
            {t("languageNote")}
          </div>
        </div>

        {/* =====================
            Theme
            ===================== */}
        <div className="rounded-2xl bg-[var(--bg-hover)] p-4">
          <div className="text-sm font-medium">{t("theme")}</div>
          <div className="mt-1 text-sm text-[var(--text-muted)]">
            {t("themeDescription")}
          </div>

          <div className="mt-4 flex items-center gap-2">
            {(["dark", "gray", "light"] as const).map((m) => (
              <button
                key={m}
                onClick={() => onChangeTheme(m)}
                className={clsx(
                  "flex-1 rounded-xl px-4 py-2 text-sm transition capitalize",
                  theme === m
                    ? "bg-[var(--bg-card)] shadow-[0_6px_18px_rgba(0,0,0,0.25)]"
                    : "bg-[var(--background)] hover:opacity-90",
                )}
              >
                {m === "dark"
                  ? t("dark")
                  : m === "gray"
                    ? t("gray")
                    : t("light")}
              </button>
            ))}
          </div>

          <div className="mt-3 text-xs text-[var(--text-faint)]">
            {t("themeNote")}
          </div>
        </div>
      </div>
    </SectionCard>
  );
}
