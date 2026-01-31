"use client";

/**
 * DiffFileView
 *
 * 選択された DiffFile の BEFORE / AFTER を表示するビュー。
 *
 * 役割:
 * - BEFORE（元の内容）を表示
 * - AFTER（提案後の内容）を表示
 *
 * 設計原則:
 * - 差分計算はしない
 * - 行単位ハイライトをしない
 * - Diff の正当性を判断しない
 *
 * この段階では
 * 「全文を並べて見せる」ことだけが目的。
 * 精密な Diff 表現は次フェーズ。
 */

import { DiffFile } from "@/app/providers/chat-provider";

type DiffFileViewProps = {
  /**
   * 表示対象の DiffFile
   * 未選択時は null
   */
  file: DiffFile | null;
};

export function DiffFileView({ file }: DiffFileViewProps) {
  if (!file) {
    return (
      <div className="h-full flex items-center justify-center text-xs text-[var(--text-muted)]">
        Select a file to view diff
      </div>
    );
  }

  return (
    <div
      className="
        h-full
        grid
        grid-cols-2
        gap-0
        bg-[var(--background)]
      "
    >
      {/* =========================================
          BEFORE
         ========================================= */}
      <section
        className="
          h-full
          overflow-auto
          border-r
          border-[var(--border-muted)]
        "
      >
        <div
          className="
            sticky top-0
            z-10
            bg-[var(--background)]
            px-3 py-2
            text-xs
            text-[var(--text-muted)]
            border-b
            border-[var(--border-muted)]
          "
        >
          BEFORE
        </div>

        <pre
          className="
            p-3
            text-xs
            leading-relaxed
            whitespace-pre
            font-mono
            text-[var(--foreground)]
          "
        >
          {file.before || ""}
        </pre>
      </section>

      {/* =========================================
          AFTER
         ========================================= */}
      <section
        className="
          h-full
          overflow-auto
        "
      >
        <div
          className="
            sticky top-0
            z-10
            bg-[var(--background)]
            px-3 py-2
            text-xs
            text-[var(--text-muted)]
            border-b
            border-[var(--border-muted)]
          "
        >
          AFTER
        </div>

        <pre
          className="
            p-3
            text-xs
            leading-relaxed
            whitespace-pre
            font-mono
            text-[var(--foreground)]
          "
        >
          {file.after || ""}
        </pre>
      </section>
    </div>
  );
}
