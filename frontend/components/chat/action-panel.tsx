"use client";

import { useTranslations } from "next-intl";
import { useChat } from "@/app/providers/chat-provider";

/**
 * DiffViewer
 *
 * Diff 結果の表示コンポーネント。
 * ActionPanel は「表示場所」を提供するだけで、
 * Diff の中身の解釈・加工はしない。
 *
 * ※ パスはプロジェクト構成に合わせて調整
 */
import { DiffViewer } from "@/components/chat/diff/DiffViewer";

/* =========================================================
 * API Response Types
 * ======================================================= */

/**
 * WorkspaceFile
 *
 * Frontend API (/api/workspace/scan) が返す WorkspaceIndex 内の 1 ファイル分メタ情報。
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
 * 右サイドに配置される「操作・結果専用パネル」。
 *
 * 役割:
 * - Workspace Scan → Snapshot Build のトリガー
 * - DevEngine（Chat）の実行トリガー
 * - Snapshot / Diff の「状態・結果」を表示する（DiffViewerをここに置く）
 *
 * 設計原則:
 * - UI は操作と表示のみ担当
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
   * 2. 返却された WorkspaceIndex を /api/snapshot/build にそのまま渡す
   * 3. 生成された Snapshot を Provider にセットする
   *
   * 注意:
   * - Snapshot の内容は完全に Backend 責務
   * - ActionPanel は「繋ぐだけ」
   * - ここで Snapshot を加工・解釈しない
   */
  const handleScan = async () => {
    try {
      /* -----------------------------
       * 1) Workspace Scan
       * --------------------------- */
      const scanRes = await fetch("/api/workspace/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
       * 2) Snapshot Build
       * --------------------------- */
      const snapshotRes = await fetch("/api/snapshot/build", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          // WorkspaceIndex をそのまま渡す（解釈しない）
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
       * 3) Provider に Snapshot をセット
       * --------------------------- */
      setSnapshot(snapshot);
    } catch (err) {
      // UI 層では判断・復旧・再試行を行わない（ログだけ）
      console.error("[ActionPanel][handleScan] error:", err);
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
        flex
        flex-col
        border-l
        border-[var(--border)]
      "
    >
      {/* =================================================
          上部（操作・状態）
          - ここは「固定」にして、下のDiffだけスクロールさせてもOK
         ================================================= */}
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

          {/* 追加の状態情報（見える化） */}
          <div className="text-[11px] text-[var(--text-muted)] space-y-1 pt-2 border-t border-[var(--border)]">
            <div>
              Snapshot files:{" "}
              <span className="text-[var(--foreground)]">
                {state.snapshot?.files?.length ?? 0}
              </span>
            </div>
            <div>
              Diff files:{" "}
              <span className="text-[var(--foreground)]">
                {state.diff?.files?.length ?? 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* =================================================
          下部（Diff Viewer）
          - ここが「結果表示領域」
          - state.diff があるときだけ表示
          - ChatPanel とは完全に分離
         ================================================= */}
      <div className="flex-1 min-h-0 px-4 pb-4">
        {state.diff ? (
          <div
            className="
              h-full
              rounded-2xl
              bg-[var(--bg-card)]
              shadow-[0_4px_12px_rgba(0,0,0,0.25)]
              overflow-hidden
              flex
              flex-col
            "
          >
            {/* 見出し */}
            <div
              className="
                px-4
                py-3
                border-b
                border-[var(--border)]
                text-xs
                font-semibold
                text-[var(--text-muted)]
              "
            >
              Diff Result
            </div>

            {/* 本体：DiffViewer を “実際に埋め込む” */}
            <div className="flex-1 min-h-0">
              {/* DiffViewer は diff を読むだけ。判断しない。 */}
              <DiffViewer diff={state.diff} />
            </div>
          </div>
        ) : (
          <div
            className="
              h-full
              rounded-2xl
              bg-[var(--bg-card)]
              shadow-[0_4px_12px_rgba(0,0,0,0.25)]
              flex
              items-center
              justify-center
              text-xs
              text-[var(--text-muted)]
            "
          >
            No diff yet
          </div>
        )}
      </div>
    </aside>
  );
}
