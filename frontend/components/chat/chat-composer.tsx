"use client";

import { useTranslations } from "next-intl";

export function ChatComposer() {
  const t = useTranslations("chat");

  return (
    <div className="bg-[var(--bg-card)] px-6 py-4">
      <div className="mx-auto max-w-chat flex items-center gap-3">
        {/* Add file */}
        <button
          className="
            h-10 w-10
            rounded-full
            bg-[var(--bg-hover)]
            text-[var(--foreground)]
            hover:opacity-90
          "
          aria-label={t("addFile")}
        >
          ＋
        </button>

        {/* Input */}
        <div
          className="
            flex-1
            rounded-full
            bg-[var(--background)]
            px-5 py-3
            text-sm
            text-[var(--foreground)]
          "
        >
          {t("messagePlaceholder")}
        </div>

        {/* Send */}
        <button
          className="
            h-10 w-10
            rounded-full
            bg-[var(--bg-hover)]
            text-[var(--foreground)]
            hover:opacity-90
          "
          aria-label={t("send")}
        >
          ↑
        </button>
      </div>
    </div>
  );
}
