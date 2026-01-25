"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase/client";
import { useTranslations } from "next-intl";

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

type ThemeMode = "dark" | "light" | "gray";
type LangMode = "ja" | "en";

/* =====================
   Constants
   ===================== */
const LS_THEME = "ui:theme";
const LS_LANG = "ui:lang";

/* =====================
   Helpers
   ===================== */
function setSafeLocalStorage(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {}
}

function applyTheme(theme: ThemeMode) {
  document.documentElement.dataset.theme = theme;
}

function applyLang(lang: LangMode) {
  document.documentElement.lang = lang === "ja" ? "ja" : "en";
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

  /* =====================
     Preferences (INIT)
     ===================== */
  const [theme, setTheme] = useState<ThemeMode>(() => {
    if (typeof window === "undefined") return "dark";
    const stored = localStorage.getItem(LS_THEME);
    return stored === "light" || stored === "gray" || stored === "dark"
      ? stored
      : "dark";
  });

  const [lang, setLang] = useState<LangMode>(() => {
    if (typeof window === "undefined") return "ja";
    const stored = localStorage.getItem(LS_LANG);
    return stored === "en" || stored === "ja" ? stored : "ja";
  });

  /* =====================
     Apply preferences
     ===================== */
  useEffect(() => {
    applyTheme(theme);
    applyLang(lang);
  }, [theme, lang]);

  /* =====================
     Auth + User Load
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
     Handlers
     ===================== */
  const onChangeTheme = (next: ThemeMode) => {
    setTheme(next);
    setSafeLocalStorage(LS_THEME, next);
  };

  const onChangeLang = (next: LangMode) => {
    setLang(next);
    setSafeLocalStorage(LS_LANG, next);

    // 現在のパスを維持したまま locale だけ切り替える
    const currentPath = window.location.pathname.replace(/^\/(ja|en)/, "");
    router.replace(`/${next}${currentPath}`);
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
  if (checking) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-[var(--background)] text-[var(--foreground)]">
        <div className="text-sm text-[var(--text-muted)]">
          {t("checkingSession")}
        </div>
      </div>
    );
  }

  if (!user) return null;

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
            theme={theme}
            lang={lang}
            onChangeTheme={onChangeTheme}
            onChangeLang={onChangeLang}
          />

          <SecuritySection />

          <IntegrationsSection providersConnected={user.providersConnected} />

          <AboutSection />
        </div>
      </div>
    </div>
  );
}
