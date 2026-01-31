"use client";

import { useTranslations } from "next-intl";
import { useChat } from "@/app/providers/chat-provider";

/* =========================================================
 * API Response Types
 * ======================================================= */

/**
 * WorkspaceFile
 *
 * Frontend API (/api/workspace/scan) が返す
 * WorkspaceIndex 内の 1 ファイル分メタ情報。
 *
 * 注意:
 * - ActionPanel では中身を一切解釈しない
 * - SnapshotBuilder にそのまま渡すための「運搬用」
 */
type WorkspaceFile = {
  path: string;
  language: string | null;
  hash: string;
  imports: string[];
  exports: string[];
  dependencies: string[];
};

/**
 * WorkspaceScanResponse
 *
 * /api/workspace/scan のレスポンス型。
 * Backend WorkspaceIndex と 1:1 対応。
 */
type WorkspaceScanResponse = {
  workspace: {
    project_id: string;
    index_version: string;
    generated_at: string;
    files: WorkspaceFile[];
  };
};

/**
 * SnapshotResponse
 *
 * /api/snapshot/build のレスポンス型。
 * Backend domain/snapshot.py と対応。
 *
 * 注意:
 * - ActionPanel は Snapshot の意味を一切知らない
 * - Provider にそのまま渡すだけ
 */
type SnapshotResponse = {
  project_id: string;
  files: {
    path: string;
    content: string;
  }[];
};

/* =========================================================
 * ActionPanel
 * ======================================================= */

/**
 * ActionPanel
 *
 * 右サイドに配置される「操作専用パネル」。
 *
 * 役割:
 * - Workspace Scan → Snapshot Build のトリガー
 * - DevEngine（Chat）の実行トリガー
 *
 * 設計原則:
 * - UI は操作のみ担当
 * - 状態は ChatProvider に完全委譲
 * - API レスポンスの意味解釈は一切行わない
 */
export function ActionPanel() {
  const t = useTranslations("chat");
  const { state, setSnapshot, runChat } = useChat();

  /* -------------------------------------------------------
   * Workspace Scan → Snapshot Build
   * ----------------------------------------------------- */

  /**
   * handleScan
   *
   * 処理フロー:
   * 1. /api/workspace/scan を呼び出す
   * 2. 返却された WorkspaceIndex を
   * 3. /api/snapshot/build にそのまま渡す
   * 4. 生成された Snapshot を Provider にセットする
   *
   * 注意:
   * - Snapshot の内容は完全に Backend 責務
   * - ActionPanel は「繋ぐだけ」
   * - ここで Snapshot を加工・解釈しない
   */
  const handleScan = async () => {
    try {
      /* -----------------------------
       * 1. Workspace Scan
       * --------------------------- */
      const scanRes = await fetch("/api/workspace/scan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          // TODO: Project Selector 実装後に動的指定
          project_id: "test-project",
          path: "C:/souce/ai-workbench",
        }),
      });

      if (!scanRes.ok) {
        throw new Error(`Workspace scan failed: ${scanRes.status}`);
      }

      const scanData: WorkspaceScanResponse = await scanRes.json();

      /* -----------------------------
       * 2. Snapshot Build
       * --------------------------- */
      const snapshotRes = await fetch("/api/snapshot/build", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          // WorkspaceIndex をそのまま渡す
          workspace: scanData.workspace,
          root_path: "C:/souce/ai-workbench",
          target_paths: null, // 現段階では全ファイル対象
        }),
      });

      if (!snapshotRes.ok) {
        throw new Error(`Snapshot build failed: ${snapshotRes.status}`);
      }

      const snapshot: SnapshotResponse = await snapshotRes.json();

      /* -----------------------------
       * 3. Provider に Snapshot をセット
       * --------------------------- */
      // Snapshot の構造・意味は Provider / Backend 側の責務
      setSnapshot(snapshot);
    } catch (err) {
      // UI 層では判断・復旧・再試行を行わない
      console.error(err);
    }
  };

  /* -------------------------------------------------------
   * DevEngine Run
   * ----------------------------------------------------- */

  /**
   * handleRun
   *
   * Snapshot を前提として Chat 実行を指示する。
   *
   * 注意:
   * - Snapshot が無い場合は UI 側でボタンを無効化
   * - mode の解釈は Workflow / ModeRouter の責務
   */
  const handleRun = async () => {
    await runChat("dev");
  };

  /* =======================================================
   * Render
   * ===================================================== */

  return (
    <aside
      className="
        relative
        h-full
        bg-[var(--bg-side)]
        z-20
      "
    >
      <div className="p-4 space-y-4">
        {/* 説明カード */}
        <div
          className="
            rounded-2xl
            bg-[var(--bg-card)]
            p-4
            text-sm
            text-[var(--text-muted)]
            shadow-[0_4px_12px_rgba(0,0,0,0.25)]
          "
        >
          {t("actionPanel")}
        </div>

        {/* 操作カード */}
        <div
          className="
            rounded-2xl
            bg-[var(--bg-card)]
            p-4
            space-y-3
            shadow-[0_4px_12px_rgba(0,0,0,0.25)]
          "
        >
          {/* Scan ボタン */}
          <button
            onClick={handleScan}
            disabled={state.isLoading}
            className="
              w-full
              rounded-lg
              px-4 py-2
              text-sm
              bg-[var(--bg-muted)]
              text-[var(--foreground)]
              hover:bg-[var(--bg-hover)]
              disabled:opacity-50
              transition
            "
          >
            Scan Workspace
          </button>

          {/* Run ボタン */}
          <button
            onClick={handleRun}
            disabled={!state.snapshot || state.isLoading}
            className="
              w-full
              rounded-lg
              px-4 py-2
              text-sm
              bg-[var(--bg-muted)]
              text-[var(--foreground)]
              hover:bg-[var(--bg-hover)]
              disabled:opacity-50
              transition
            "
          >
            Run Dev
          </button>

          {/* 状態表示 */}
          <div className="text-xs text-[var(--text-muted)]">
            {state.isLoading && "Processing..."}
            {!state.isLoading && state.snapshot && "Snapshot ready"}
            {!state.isLoading && !state.snapshot && "No snapshot"}
          </div>
        </div>
      </div>
    </aside>
  );
}
