"use client";

import Image from "next/image";
import { useTranslations } from "next-intl";
import { SectionCard } from "./SectionCard";
import { Row } from "./Row";
import { Divider } from "./Divider";

type Props = {
  user: {
    name: string;
    email: string | null;
    avatarUrl: string | null;
    providerLabel: string;
    id?: string;
  };
  onLogout: () => void;
};

export function AccountSection({ user, onLogout }: Props) {
  const t = useTranslations("setting");

  return (
    <SectionCard title={t("account")} description={t("accountDescription")}>
      <div className="flex items-center gap-4">
        {user.avatarUrl ? (
          <Image
            src={user.avatarUrl}
            alt="Avatar"
            width={56}
            height={56}
            className="rounded-full"
          />
        ) : (
          <div className="h-14 w-14 rounded-full bg-[var(--bg-hover)]" />
        )}

        <div className="min-w-0">
          <div className="text-base font-medium truncate">{user.name}</div>
          <div className="text-sm text-[var(--text-muted)] truncate">
            {user.email ?? t("noValue")}
          </div>
        </div>

        <button
          onClick={onLogout}
          className="ml-auto rounded-xl bg-[var(--bg-hover)] px-4 py-2 text-sm hover:opacity-90"
        >
          {t("logout")}
        </button>
      </div>

      <div className="mt-5 rounded-2xl bg-[var(--bg-hover)] p-4">
        <Row label={t("provider")} value={user.providerLabel} />
        <Divider />
        <Row
          label={t("userId")}
          value={
            <span className="font-mono text-xs">{user.id ?? t("noValue")}</span>
          }
        />
        <div className="mt-2 text-xs text-[var(--text-faint)]">
          {t("userIdNote")}
        </div>
      </div>
    </SectionCard>
  );
}
