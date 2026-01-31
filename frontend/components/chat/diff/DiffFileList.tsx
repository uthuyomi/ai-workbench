"use client";

/**
 * DiffFileList
 *
 * Diff に含まれるファイル一覧を表示する UI コンポーネント。
 *
 * 役割:
 * - Diff.files をそのまま列挙する
 * - 現在選択中のファイルを視覚的に示す
 * - ユーザー操作（クリック）を親へ通知する
 *
 * 設計原則:
 * - 差分内容は一切見ない
 * - BEFORE / AFTER を知らない
 * - ファイル内容を解釈しない
 *
 * このコンポーネントは
 * 「Diff を構成する“ファイルという単位”を選ばせる UI」
 * に徹する。
 */

import { DiffFile } from "@/app/providers/chat-provider";

type DiffFileListProps = {
  /**
   * Diff に含まれるファイル一覧
   * Backend domain/diff.py と 1:1 対応
   */
  files: DiffFile[];

  /**
   * 現在選択中のファイル index
   */
  activeIndex: number;

  /**
   * ファイル選択時の通知コールバック
   */
  onSelect: (index: number) => void;
};

export function DiffFileList({
  files,
  activeIndex,
  onSelect,
}: DiffFileListProps) {
  return (
    <aside
      className="
        h-full
        w-full
        overflow-y-auto
        bg-[var(--bg-side)]
        border-r
        border-[var(--border-muted)]
      "
    >
      <div className="p-3 space-y-1">
        {files.length === 0 && (
          <div className="text-xs text-[var(--text-muted)]">No diff files</div>
        )}

        {files.map((file, index) => {
          const isActive = index === activeIndex;

          return (
            <button
              key={file.path}
              onClick={() => onSelect(index)}
              className={`
                w-full
                text-left
                rounded-md
                px-3 py-2
                text-xs
                transition
                ${
                  isActive
                    ? "bg-[var(--bg-hover)] text-[var(--foreground)]"
                    : "text-[var(--text-muted)] hover:bg-[var(--bg-muted)]"
                }
              `}
            >
              {/* ファイルパスは省略せずフルで表示 */}
              <div className="truncate">{file.path}</div>
            </button>
          );
        })}
      </div>
    </aside>
  );
}
