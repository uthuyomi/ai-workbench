"use client";

import { useState } from "react";
import Image from "next/image";
import { supabase } from "@/lib/supabase/client";
import { useTranslations } from "next-intl";

export default function LoginPage() {
  const t = useTranslations("login");

  const [loading, setLoading] = useState<null | "google" | "github">(null);
  const [error, setError] = useState<string | null>(null);

  const signIn = async (provider: "google" | "github") => {
    try {
      setError(null);
      setLoading(provider);

      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${location.origin}/chat`,
        },
      });

      if (error) {
        throw error;
      }
    } catch {
      setLoading(null);
      setError(t("errorSignIn"));
    }
  };

  return (
    <div
      className="
        h-screen w-screen
        flex items-center justify-center
        bg-[var(--background)]
        text-[var(--foreground)]
      "
    >
      <div
        className="
          w-full max-w-md
          rounded-3xl
          bg-[var(--bg-card)]
          px-10 py-12
          shadow-[0_12px_40px_rgba(0,0,0,0.35)]
        "
      >
        {/* Title */}
        <div className="mb-10 space-y-2">
          <h1 className="text-2xl font-medium">{t("title")}</h1>
          <p className="text-base text-[var(--text-muted)]">{t("subtitle")}</p>
        </div>

        {/* OAuth buttons */}
        <div className="space-y-4">
          {/* Google */}
          <button
            onClick={() => signIn("google")}
            disabled={loading !== null}
            className="
              w-full
              flex items-center gap-4
              rounded-xl
              bg-[var(--bg-hover)]
              px-5 py-4
              text-base
              text-[var(--foreground)]
              hover:opacity-90
              transition
              disabled:opacity-50
            "
          >
            <Image
              src="/login/google.png"
              alt="Google"
              width={24}
              height={24}
            />
            <span className="flex-1 text-left">
              {loading === "google"
                ? t("redirecting")
                : t("continueWithGoogle")}
            </span>
          </button>

          {/* GitHub */}
          <button
            onClick={() => signIn("github")}
            disabled={loading !== null}
            className="
              w-full
              flex items-center gap-4
              rounded-xl
              bg-[var(--bg-hover)]
              px-5 py-4
              text-base
              text-[var(--foreground)]
              hover:opacity-90
              transition
              disabled:opacity-50
            "
          >
            <Image
              src="/login/github.png"
              alt="GitHub"
              width={24}
              height={24}
            />
            <span className="flex-1 text-left">
              {loading === "github"
                ? t("redirecting")
                : t("continueWithGitHub")}
            </span>
          </button>
        </div>

        {/* Error */}
        {error && (
          <p className="mt-6 text-sm text-red-400 text-center">{error}</p>
        )}

        {/* Hint */}
        <p
          className="
            mt-8
            text-sm
            text-center
            text-[var(--text-faint)]
          "
        >
          {t("hintAutoCreate")}
        </p>
      </div>
    </div>
  );
}
