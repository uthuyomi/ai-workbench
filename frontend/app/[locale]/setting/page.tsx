"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase/client";
import { useTranslations } from "next-intl";

import { ensureUserSettings } from "@/lib/supabase/ensureUserSettings";
import { upsertUserSettings, UserSettings } from "@/lib/supabase/userSettings";

import { AccountSection } from "@/components/setting/AccountSection";
import { PreferencesSection } from "@/components/setting/PreferencesSection";
import { SecuritySection } from "@/components/setting/SecuritySection";
import { IntegrationsSection } from "@/components/setting/IntegrationsSection";
import { AboutSection } from "@/components/setting/AboutSection";

/* =====================
   Types
   ===================== */
type UserInfo = {
  id?: string;
  name: string;
  email: string | null;
  avatarUrl: string | null;
  provider: string | null;
  providersConnected: {
    google: boolean;
    github: boolean;
  };
};

type ThemeMode = "dark" | "gray" | "light";
type LangMode = "ja" | "en";

/* =====================
   Helpers
   ===================== */
function applyTheme(theme: ThemeMode) {
  document.documentElement.dataset.theme = theme;
}

function applyLang(lang: LangMode) {
  document.documentElement.lang = lang;
  document.documentElement.dataset.lang = lang;
}

/* =====================
   Page
   ===================== */
export default function SettingsPage() {
  const t = useTranslations("setting");
  const router = useRouter();

  const [checking, setChecking] = useState(true);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [settings, setSettings] = useState<UserSettings | null>(null);

  /* =====================
     Auth + Initial Load
     ===================== */
  useEffect(() => {
    const load = async () => {
      const {
        data: { session },
        error,
      } = await supabase.auth.getSession();

      if (!session || error) {
        router.replace("/login");
        return;
      }

      const u = session.user;

      const identities = (u.identities ?? []) as Array<{ provider?: string }>;
      const providers = new Set(
        identities.map((i) => i.provider).filter(Boolean) as string[],
      );

      const providerMain =
        (u.app_metadata?.provider as string | undefined) ?? null;

      const name =
        (u.user_metadata?.name as string | undefined) ??
        (u.user_metadata?.full_name as string | undefined) ??
        u.email ??
        t("defaultUser");

      const avatarUrl =
        (u.user_metadata?.avatar_url as string | undefined) ?? null;

      setUser({
        id: u.id,
        name,
        email: u.email ?? null,
        avatarUrl,
        provider: providerMain,
        providersConnected: {
          google: providerMain === "google" || providers.has("google"),
          github: providerMain === "github" || providers.has("github"),
        },
      });

      // 🔽 DB から settings を必ず取得（なければ生成）
      const s = await ensureUserSettings();
      if (!s) return;

      setSettings(s);

      // 🔽 DOM へ反映
      applyTheme(s.theme as ThemeMode);
      applyLang(s.lang as LangMode);

      setChecking(false);
    };

    load();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) router.replace("/login");
    });

    return () => subscription.unsubscribe();
  }, [router, t]);

  /* =====================
     Update handlers
     ===================== */
  const updateSettings = async (next: Partial<UserSettings>) => {
    if (!settings) return;

    const updated: UserSettings = {
      ...settings,
      ...next,
    };

    // 楽観的更新
    setSettings(updated);

    // DOM 反映
    if (next.theme) applyTheme(next.theme as ThemeMode);
    if (next.lang) applyLang(next.lang as LangMode);

    // DB 永続化
    await upsertUserSettings(updated);

    // locale 切り替え（lang変更時のみ）
    if (next.lang) {
      const currentPath = window.location.pathname.replace(/^\/(ja|en)/, "");
      router.replace(`/${next.lang}${currentPath}`);
    }
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    router.replace("/login");
  };

  const providerLabel = useMemo(() => {
    const p = user?.provider;
    if (!p) return t("noValue");
    if (p === "google") return "Google";
    if (p === "github") return "GitHub";
    return p;
  }, [user?.provider, t]);

  /* =====================
     Render guards
     ===================== */
  if (checking || !user || !settings) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[var(--background)] text-[var(--foreground)]">
        <div className="text-sm text-[var(--text-muted)]">
          {t("checkingSession")}
        </div>
      </div>
    );
  }

  /* =====================
     Render
     ===================== */
  return (
    <div className="min-h-screen w-screen bg-[var(--background)] text-[var(--foreground)]">
      {/* Top Bar */}
      <div className="sticky top-0 z-30 bg-[var(--background)] px-6 py-5">
        <div className="mx-auto max-w-5xl flex items-center justify-between gap-4">
          <div className="min-w-0">
            <div className="text-lg font-medium">{t("settings")}</div>
            <div className="mt-1 text-sm text-[var(--text-muted)]">
              {t("settingsSubtitle")}
            </div>
          </div>

          <button
            onClick={() => router.push("/chat")}
            className="rounded-xl bg-[var(--bg-hover)] px-4 py-2 text-sm hover:opacity-90"
          >
            {t("backToChat")}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="px-6 pb-14 pt-6">
        <div className="mx-auto max-w-5xl grid grid-cols-1 gap-5">
          <AccountSection
            user={{
              id: user.id,
              name: user.name,
              email: user.email,
              avatarUrl: user.avatarUrl,
              providerLabel,
            }}
            onLogout={signOut}
          />

          <PreferencesSection
            theme={settings.theme as ThemeMode}
            lang={settings.lang as LangMode}
            onChangeTheme={(t) => updateSettings({ theme: t })}
            onChangeLang={(l) => updateSettings({ lang: l })}
          />

          <SecuritySection />
          <IntegrationsSection providersConnected={user.providersConnected} />
          <AboutSection />
        </div>
      </div>
    </div>
  );
}
