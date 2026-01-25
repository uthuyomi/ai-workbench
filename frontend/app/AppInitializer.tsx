"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase/client";
import { ensureUserSettings } from "@/lib/supabase/ensureUserSettings";

/* =====================
   Types
   ===================== */
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
   Component
   ===================== */
export function AppInitializer() {
  const router = useRouter();

  useEffect(() => {
    const init = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      // 未ログイン時は何もしない（loginページ用）
      if (!session) return;

      // 🔽 settings を必ず取得（なければ生成）
      const settings = await ensureUserSettings();
      if (!settings) return;

      // 🔽 DOM に即反映
      applyTheme(settings.theme as ThemeMode);
      applyLang(settings.lang as LangMode);
    };

    init();
  }, [router]);

  return null;
}
