"use client";

/**
 * ChatComposer
 *
 * このコンポーネントは、ai-workbench Frontend における
 * 「チャット入力専用 UI」である。
 *
 * 役割:
 * - ユーザーのテキスト入力を受け取る
 * - Enter / Send ボタンで送信する
 * - 送信内容を ChatProvider.sendMessage に渡す
 *
 * やらないこと:
 * - メッセージの保存
 * - AI 応答の生成
 * - Snapshot / Diff の操作
 *
 * 重要:
 * - このコンポーネントは「入力と発火」だけを担当する
 * - 実際の状態管理はすべて ChatProvider に委譲する
 */

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useChat } from "@/app/providers/chat-provider";

export function ChatComposer() {
  /**
   * i18n 用テキスト
   * （placeholder / aria-label など UI 表示のみ）
   */
  const t = useTranslations("chat");

  /**
   * ChatProvider から sendMessage を取得
   *
   * - ここでは state は読まない
   * - 入力 → 発火の一本責務に徹する
   */
  const { sendMessage, state } = useChat();

  /**
   * 入力中のテキストをローカル state として保持
   *
   * 理由:
   * - 入力途中の文字列は Provider に持たせない
   * - UI の一時状態はコンポーネントローカルで完結させる
   */
  const [input, setInput] = useState("");

  /**
   * 送信処理
   *
   * - 空文字は送らない
   * - 送信後は input をクリアする
   * - 実際の処理は ChatProvider 側に委譲
   */
  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    await sendMessage(trimmed);

    // 入力欄をクリア
    setInput("");
  };

  /**
   * Enter キー送信対応
   *
   * - Enter        : 送信
   * - Shift+Enter  : 改行（将来拡張用、今は未対応でもOK）
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-[var(--bg-card)] px-6 py-4">
      <div className="mx-auto max-w-chat flex items-center gap-3">
        {/* =========================================
            Add file（将来拡張用・現段階ではダミー）
           ========================================= */}
        <button
          className="
            h-10 w-10
            rounded-full
            bg-[var(--bg-hover)]
            text-[var(--foreground)]
            hover:opacity-90
            disabled:opacity-50
          "
          aria-label={t("addFile")}
          disabled
        >
          ＋
        </button>

        {/* =========================================
            Text Input
           ========================================= */}
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t("messagePlaceholder")}
          className="
            flex-1
            rounded-full
            bg-[var(--background)]
            px-5 py-3
            text-sm
            text-[var(--foreground)]
            outline-none
          "
        />

        {/* =========================================
            Send Button
           ========================================= */}
        <button
          onClick={handleSend}
          disabled={!input.trim() || state.isLoading}
          className="
            h-10 w-10
            rounded-full
            bg-[var(--bg-hover)]
            text-[var(--foreground)]
            hover:opacity-90
            disabled:opacity-50
          "
          aria-label={t("send")}
        >
          ↑
        </button>
      </div>
    </div>
  );
}
