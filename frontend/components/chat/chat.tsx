"use client";

/**
 * ChatPanel
 *
 * このコンポーネントは、ai-workbench Frontend における
 * 「チャット表示専用パネル」である。
 *
 * 役割:
 * - ChatProvider が保持している messages を表示する
 * - user / assistant の区別に応じて見た目を切り替える
 *
 * やらないこと:
 * - 入力処理（それは ChatComposer の責務）
 * - API 呼び出し
 * - メッセージ内容の解釈
 *
 * 重要:
 * - このコンポーネントは **完全に state 駆動**
 * - ハードコードされたメッセージは一切持たない
 */

import { useEffect, useRef } from "react";
import { useChat } from "@/app/providers/chat-provider";

export function ChatPanel() {
  /**
   * ChatProvider から状態を取得する
   *
   * state.messages:
   * - user / assistant の発言履歴
   * - ChatComposer / sendMessage によって追加される
   */
  const { state } = useChat();

  /**
   * スクロール制御用の ref
   *
   * 新しいメッセージが追加されたら、
   * 一番下まで自動でスクロールするために使う。
   */
  const bottomRef = useRef<HTMLDivElement | null>(null);

  /**
   * messages が更新されたら自動スクロール
   *
   * - チャットらしさの最低限UX
   * - ロジックは一切含まない
   */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [state.messages]);

  return (
    <div className="flex h-full flex-col bg-[var(--background)]">
      {/* =========================================
          メッセージ表示領域
         ========================================= */}
      <div className="flex-1 overflow-y-auto px-6 py-10">
        <div className="mx-auto max-w-chat space-y-6">
          {/* -----------------------------------------
              メッセージ一覧を state.messages から描画
             ----------------------------------------- */}
          {state.messages.length === 0 && (
            /**
             * メッセージがまだ無い場合のプレースホルダ
             *
             * - UI 的な補助のみ
             * - ロジック的意味は持たせない
             */
            <div className="text-sm text-[var(--text-muted)] text-center">
              No messages yet
            </div>
          )}

          {state.messages.map((message) => {
            /**
             * role によって表示スタイルを切り替える
             *
             * user      : 右寄せ / 少し濃い背景
             * assistant : 左寄せ / カード風背景
             */
            const isUser = message.role === "user";

            return (
              <div
                key={message.id}
                className={`
                  max-w-[85%]
                  rounded-xl
                  px-6 py-4
                  text-sm
                  text-[var(--foreground)]
                  whitespace-pre-wrap
                  break-words
                  ${isUser ? "ml-auto bg-[var(--bg-hover)]" : "bg-[var(--bg-card)]"}
                `}
              >
                {message.content}
              </div>
            );
          })}

          {/* -----------------------------------------
              自動スクロール用ダミー要素
             ----------------------------------------- */}
          <div ref={bottomRef} />
        </div>
      </div>
    </div>
  );
}
