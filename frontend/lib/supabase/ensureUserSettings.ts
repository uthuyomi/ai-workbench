// src/lib/supabase/ensureUserSettings.ts
import { supabase } from "./client";
import {
  fetchUserSettings,
  upsertUserSettings,
  UserSettings,
} from "./userSettings";

/**
 * 初期設定（ここを変えれば全体が変わる）
 */
const DEFAULT_SETTINGS: UserSettings = {
  theme: "dark",
  lang: "ja",
};

/**
 * user_settings が存在しなければ自動生成する
 *
 * - 初回ログイン時
 * - セッション復元時
 * - Settings Page 初期表示時
 *
 * どこから呼んでも安全
 */
export async function ensureUserSettings(): Promise<UserSettings | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) return null;

  // 既存設定を確認
  const existing = await fetchUserSettings();
  if (existing) return existing;

  // なければ初期設定を作成
  await upsertUserSettings(DEFAULT_SETTINGS);

  return DEFAULT_SETTINGS;
}
