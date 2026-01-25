"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase/client";
import { AppShell } from "@/components/chat/app-shell";
import { useTranslations } from "next-intl";

export default function ChatPage() {
  const t = useTranslations("chat");

  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkSession = async () => {
      const {
        data: { session },
        error,
      } = await supabase.auth.getSession();

      // セッションがなければログインへ
      if (!session || error) {
        router.replace("/login"); // ← 後で locale 対応させる
        return;
      }

      setChecking(false);
    };

    checkSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) {
        router.replace("/login"); // ← 後で locale 対応
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [router]);

  if (checking) {
    return (
      <div
        className="
          h-screen w-screen
          flex items-center justify-center
          bg-[var(--background)]
          text-[var(--foreground)]
        "
      >
        <div className="text-sm text-[var(--text-muted)]">
          {t("checkingSession")}
        </div>
      </div>
    );
  }

  return <AppShell />;
}
