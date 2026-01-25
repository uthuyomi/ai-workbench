"use client";

import { useState } from "react";
import clsx from "clsx";
import { useTranslations } from "next-intl";

type VSCodeStatus = "connected" | "waiting" | "disconnected";
type PersonaStyle =
  | "technical"
  | "casual"
  | "minimal"
  | "reviewer"
  | "narrative";

export function Header() {
  const t = useTranslations("chat");

  const personaOptions: { value: PersonaStyle; label: string }[] = [
    { value: "technical", label: t("personaTechnical") },
    { value: "casual", label: t("personaCasual") },
    { value: "minimal", label: t("personaMinimal") },
    { value: "reviewer", label: t("personaReviewer") },
    { value: "narrative", label: t("personaNarrative") },
  ];

  function statusColor(status: VSCodeStatus) {
    switch (status) {
      case "connected":
        return "bg-emerald-400";
      case "waiting":
        return "bg-amber-400";
      default:
        return "bg-rose-400";
    }
  }

  function statusLabel(status: VSCodeStatus) {
    switch (status) {
      case "connected":
        return t("vsCodeConnected");
      case "waiting":
        return t("vsCodeWaiting");
      default:
        return t("vsCodeDisconnected");
    }
  }

  // モック状態（後で Context / API に置き換える）
  const [vscodeStatus, setVSCodeStatus] =
    useState<VSCodeStatus>("disconnected");
  const [persona, setPersona] = useState<PersonaStyle>("technical");

  return (
    <header
      className="
        h-14 flex items-center justify-between
        px-4
        border-b border-border-subtle
        bg-bg-main
      "
    >
      {/* Left */}
      <div className="flex items-center gap-3 min-w-0">
        <div className="text-sm text-text-muted truncate">{t("devChat")}</div>

        {/* VS Code Status */}
        <button
          onClick={() =>
            setVSCodeStatus((s) =>
              s === "disconnected" ? "connected" : "disconnected",
            )
          }
          className="
            flex items-center gap-2
            rounded-full border border-white/10
            bg-white/5 px-3 py-1.5
            text-xs text-text-muted
            hover:bg-white/10 transition
          "
          title={t("vsCodeToggleTitle")}
        >
          <span
            className={clsx(
              "inline-block h-2 w-2 rounded-full",
              statusColor(vscodeStatus),
            )}
          />
          {t("vsCodeStatusLabel", {
            status: statusLabel(vscodeStatus),
          })}
        </button>
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-text-faint">{t("persona")}</span>
        <select
          value={persona}
          onChange={(e) => setPersona(e.target.value as PersonaStyle)}
          className="
            rounded-lg border border-white/10
            bg-white/5 px-2 py-1.5
            text-xs text-text-main
            focus:outline-none
            hover:bg-white/10 transition
          "
        >
          {personaOptions.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </select>
      </div>
    </header>
  );
}
