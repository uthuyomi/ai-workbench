"use client";

import { useTranslations } from "next-intl";

export function ChatPanel() {
  const t = useTranslations("chat");

  return (
    <div className="flex h-full flex-col bg-[var(--background)]">
      <div className="flex-1 overflow-y-auto px-6 py-10">
        <div className="mx-auto max-w-chat space-y-6">
          {/* =====================
              Assistant message
              ===================== */}
          <div
            className="
              max-w-[85%]
              rounded-xl
              bg-[var(--bg-card)]
              px-6 py-4
              text-sm
              text-[var(--foreground)]
            "
          >
            {t("assistantMessageExample")}
          </div>

          {/* =====================
              User message
              ===================== */}
          <div
            className="
              ml-auto
              max-w-[85%]
              rounded-xl
              bg-[var(--bg-hover)]
              px-6 py-4
              text-sm
              text-[var(--foreground)]
            "
          >
            {t("userMessageExample")}
          </div>
        </div>
      </div>
    </div>
  );
}
