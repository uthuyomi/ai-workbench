"use client";

import { useTranslations } from "next-intl";
import { useChat } from "@/app/providers/chat-provider";

/* =========================================================
 * Workspace Scan Response Types
 * ======================================================= */

/**
 * WorkspaceFile
 *
 * Backend の WorkspaceIndex に含まれる 1 ファイル分のメタ情報。
 * ※ 現時点では Snapshot 化のため path のみ使用。
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
 * /api/workspace/scan のレスポンス全体。
 * Backend 側の構造と 1:1 で対応させる。
 */
type WorkspaceScanResponse = {
  workspace: {
    project_id: string;
    index_version: string;
    generated_at: string;
    files: WorkspaceFile[];
  };
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
 * - Workspace Scan の実行
 * - Chat（DevEngine）の実行トリガー
 *
 * 注意:
 * - UI は薄く、道具感を優先する
 * - 状態の実体は Provider 側が持つ
 * - ここでは判断・加工をしない
 */
export function ActionPanel() {
  const t = useTranslations("chat");
  const { state, setSnapshot, runChat } = useChat();

  /* -------------------------------------------------------
   * Workspace Scan 実行
   * ----------------------------------------------------- */

  /**
   * handleScan
   *
   * 現段階の挙動:
   * - Backend に Workspace Scan を依頼
   * - 返却された WorkspaceIndex から
   *   「仮 Snapshot」を最小構成で生成する
   *
   * 注意:
   * - file.content はダミー
   * - Snapshot の意味解釈は一切しない
   *
   * 将来:
   * - SnapshotBuilder API に置き換える
   */
  const handleScan = async () => {
    try {
      const res = await fetch("/api/workspace/scan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          // TODO: UI / Project Selector から渡す
          project_id: "test-project",
          path: "C:/souce/ai-workbench",
        }),
      });

      if (!res.ok) {
        throw new Error(`Workspace scan failed: ${res.status}`);
      }

      const data: WorkspaceScanResponse = await res.json();

      // --------------------------------------------------
      // 仮 Snapshot 生成（流れ確認用）
      // --------------------------------------------------
      setSnapshot({
        project_id: data.workspace.project_id,
        files: data.workspace.files.slice(0, 5).map((file) => ({
          path: file.path,
          // ※ 今は中身を詰めない（責務外）
          content: "// snapshot content placeholder",
        })),
      });
    } catch (err) {
      // UI で握りつぶさず、最低限のログのみ
      console.error(err);
    }
  };

  /* -------------------------------------------------------
   * DevEngine 実行
   * ----------------------------------------------------- */

  /**
   * handleRun
   *
   * Snapshot を前提に Backend /chat を起動する。
   * mode の意味解釈は Backend 側に委譲。
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
