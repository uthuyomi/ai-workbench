// src/lib/supabase/userSettings.ts
import { supabase } from "./client";

/**
 * アプリで使う設定の型
 * DB構造とは切り離す
 */
export type UserSettings = {
  theme: "dark" | "gray" | "light";
  lang: "ja" | "en";
};

/**
 * 現在ログイン中ユーザーの設定を取得
 */
export async function fetchUserSettings(): Promise<UserSettings | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) return null;

  const { data, error } = await supabase
    .from("user_settings")
    .select("theme, lang")
    .eq("user_id", user.id)
    .single();

  if (error) {
    // 初回ログインなどでレコードが無いのは正常
    if (error.code === "PGRST116") {
      return null;
    }

    console.warn("[fetchUserSettings]", error.message);
    return null;
  }

  return data;
}

/**
 * 設定を保存（なければ作成）
 */
export async function upsertUserSettings(settings: UserSettings) {
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) return;

  const { error } = await supabase.from("user_settings").upsert(
    {
      user_id: user.id,
      theme: settings.theme,
      lang: settings.lang,
      updated_at: new Date().toISOString(),
    },
    {
      onConflict: "user_id",
    },
  );

  if (error) {
    console.error("[upsertUserSettings]", error.message);
  }
}
