"use client";

/**
 * AppShell
 *
 * このコンポーネントは、ai-workbench Frontend における
 * 「アプリ全体のレイアウト骨格」を定義する。
 *
 * 重要な役割:
 * - 画面全体のレイアウト構造を決める
 * - 各 UI コンポーネントを配置する
 * - アプリ全体で共有される Provider を最上位でラップする
 *
 * 注意:
 * - AppShell 自身は状態を持たない
 * - ビジネスロジックを持たない
 * - API を直接呼ばない
 *
 * Provider は「表示されない中枢」であり、
 * AppShell はそれを包む「器」である。
 */

import { Sidebar } from "@/components/chat/sidebar";
import { Header } from "@/components/chat/header";
import { ChatPanel } from "@/components/chat/chat";
import { ChatComposer } from "@/components/chat/chat-composer";
import { ActionPanel } from "@/components/chat/action-panel";

/**
 * ChatProvider
 *
 * - Chat / Snapshot / Diff / Backend 実行状態を一元管理する
 * - UI は一切持たない
 * - 子コンポーネントは useChat() を通じてのみ状態にアクセスする
 *
 * AppShell 直下でラップすることで、
 * - Sidebar
 * - ChatPanel
 * - ChatComposer
 * - ActionPanel
 *
 * のすべてが同一の Chat 状態を共有できる。
 */
import { ChatProvider } from "@/app/providers/chat-provider";

export function AppShell() {
  return (
    /**
     * ChatProvider は UI を描画しない。
     * あくまで「データと操作」を提供するだけ。
     */
    <ChatProvider>
      <div
        className="
          h-screen w-screen
          bg-[var(--background)]
          text-[var(--foreground)]
          overflow-hidden
        "
      >
        <div className="h-full grid grid-cols-[260px_1fr_360px]">
          {/* =================================================
              Sidebar（左ペイン）
              - チャット一覧
              - プロジェクト一覧
              - 将来的な Workspace 選択
             ================================================= */}
          <Sidebar />

          {/* =================================================
              Center Column（中央）
              - 実際のチャット操作領域
             ================================================= */}
          <section
            className="
              relative
              flex flex-col
              min-h-0
              bg-[var(--background)]
            "
          >
            {/* -------------------------------
                Header（固定ヘッダー）
                - プロジェクト名
                - モード表示
                - 将来的な実行状態表示
               ------------------------------- */}
            <div
              className="
                sticky top-0
                z-30
                bg-[var(--background)]
              "
            >
              <Header />
            </div>

            {/* -------------------------------
                Chat Area
                - ChatPanel   : 会話・Diff 表示
                - ChatComposer: 入力・実行トリガ
               ------------------------------- */}
            <div className="flex-1 min-h-0 flex flex-col">
              <ChatPanel />
              <ChatComposer />
            </div>
          </section>

          {/* =================================================
              ActionPanel（右ペイン）
              - Snapshot 状態表示
              - Diff 状態表示
              - 実行ボタン・制御UI（予定）
             ================================================= */}
          <ActionPanel />
        </div>
      </div>
    </ChatProvider>
  );
}
