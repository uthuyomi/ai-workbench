"use client";

/**
 * DiffViewer
 *
 * Diff 表示の中核コンポーネント。
 *
 * 役割:
 * - Diff 全体を受け取る
 * - ファイル一覧（DiffFileList）と
 *   ファイル内容表示（DiffFileView）を束ねる
 * - 現在選択中のファイル index を唯一ここで管理する
 *
 * 設計原則:
 * - Diff を解釈しない
 * - Snapshot を知らない
 * - 適用・承認・判断をしない
 *
 * このコンポーネントは
 * 「Diff を“閲覧可能な形”に分解・配置する器」
 * であり、判断主体ではない。
 */

import { useState } from "react";
import { Diff } from "@/app/providers/chat-provider";
import { DiffFileList } from "@/components/chat/diff/DiffFileList";
import { DiffFileView } from "@/components/chat/diff/DiffFileView";

type DiffViewerProps = {
  /**
   * 表示対象の Diff
   * 未生成時は null
   */
  diff: Diff | null;
};

export function DiffViewer({ diff }: DiffViewerProps) {
  /**
   * 現在選択中の DiffFile index
   *
   * - Diff が変わった場合は 0 にリセット
   * - index の解釈は一切しない
   */
  const [activeIndex, setActiveIndex] = useState(0);

  // Diff が存在しない場合の表示
  if (!diff) {
    return (
      <div
        className="
          h-full
          flex
          items-center
          justify-center
          text-xs
          text-[var(--text-muted)]
        "
      >
        No diff generated
      </div>
    );
  }

  const files = diff.files;
  const activeFile = files[activeIndex] ?? null;

  return (
    <div
      className="
        h-full
        w-full
        grid
        grid-cols-[280px_1fr]
        bg-[var(--background)]
      "
    >
      {/* =========================================
          Left: Diff File List
         ========================================= */}
      <DiffFileList
        files={files}
        activeIndex={activeIndex}
        onSelect={setActiveIndex}
      />

      {/* =========================================
          Right: Diff File View
         ========================================= */}
      <section
        className="
          h-full
          min-w-0
          bg-[var(--background)]
        "
      >
        <DiffFileView file={activeFile} />
      </section>
    </div>
  );
}
