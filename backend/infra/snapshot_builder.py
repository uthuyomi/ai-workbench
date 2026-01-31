# backend/infra/snapshot_builder.py
"""
SnapshotBuilder 定義

このファイルは、ai-workbench Backend における
「Snapshot」を生成する責務を持つ。

SnapshotBuilder の役割:
- WorkspaceIndex を入力として受け取る
- 実ファイルシステムからファイル内容を読み取る
- Snapshot / SnapshotFile を組み立てる

重要:
- SnapshotBuilder は「判断」を行わない
- SnapshotBuilder は「必要な分だけ」ファイルを読む
- SnapshotBuilder は「一時データ」を作るだけ

やってはいけないこと:
- ファイル内容の意味解釈
- import / export 解析
- Diff / Workflow の生成
- 永続化
- LLM 呼び出し
- キャラクター・表現ロジック

infra/snapshot_builder.py は
「WorkspaceIndex と実ファイルの橋渡し」を行う層であり、
判断ロジックを持たせてはいけない。
"""

from __future__ import annotations

import os
from typing import List, Optional

from backend.domain.workspace_index import WorkspaceIndex
from backend.domain.snapshot import Snapshot, SnapshotFile
from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# SnapshotBuilder
# ============================================================
class SnapshotBuilder:
    """
    Snapshot を構築するクラス。

    設計方針:
    - ステートレス（状態を持たない）
    - 毎回インスタンス化して使い捨てる
    - WorkspaceIndex を唯一の参照情報とする
    """

    def build(
        self,
        workspace: WorkspaceIndex,
        root_path: str,
        target_paths: Optional[List[str]] = None,
    ) -> Snapshot:
        """
        WorkspaceIndex を元に Snapshot を生成する。

        Parameters:
        - workspace:
            WorkspaceIndex。
            ファイル構造・パス情報の唯一の参照元。
        - root_path:
            Workspace の実体が存在するルートディレクトリ。
            WorkspaceScanner と同じルートを想定する。
        - target_paths:
            Snapshot に含めたい相対パスのリスト。
            None の場合は WorkspaceIndex に含まれる全ファイルを対象とする。

        Returns:
        - Snapshot（不変データ）

        注意:
        - 読めないファイルはログ出力してスキップする
        - Snapshot の生成に失敗しても WorkspaceIndex は壊さない
        """

        logger.info(
            "Snapshot build started: project_id=%s target_paths=%s",
            workspace.project_id,
            "ALL" if target_paths is None else len(target_paths),
        )

        # ルートパスの存在確認
        if not os.path.exists(root_path):
            raise RuntimeError(f"root_path does not exist: {root_path}")

        if not os.path.isdir(root_path):
            raise RuntimeError(f"root_path is not a directory: {root_path}")

        snapshot_files: List[SnapshotFile] = []

        # WorkspaceIndex に含まれるファイル一覧を走査
        for wf in workspace.files:
            # target_paths が指定されている場合は対象を絞る
            if target_paths is not None and wf.path not in target_paths:
                continue

            # Workspace ルートからの実ファイルパスを復元
            full_path = os.path.join(root_path, wf.path)

            # 念のためパス正規化（Windows / Unix 差異対策）
            full_path = os.path.normpath(full_path)

            # ファイルが存在しない場合はスキップ
            if not os.path.exists(full_path):
                logger.info(
                    "Snapshot skipped (file not found): %s",
                    full_path,
                )
                continue

            # ディレクトリは Snapshot 対象外
            if not os.path.isfile(full_path):
                continue

            try:
                content = self._read_file_content(full_path)
            except (PermissionError, OSError, UnicodeDecodeError) as e:
                # 読めないファイルは想定内
                # - 権限不足
                # - 使用中
                # - バイナリファイル
                logger.info(
                    "Snapshot skipped unreadable file: %s (%s)",
                    full_path,
                    e.__class__.__name__,
                )
                continue

            snapshot_files.append(
                SnapshotFile(
                    path=wf.path,
                    content=content,
                )
            )

        snapshot = Snapshot(
            project_id=workspace.project_id,
            files=snapshot_files,
        )

        logger.info(
            "Snapshot build completed: project_id=%s files=%d",
            snapshot.project_id,
            len(snapshot.files),
        )

        return snapshot

    # --------------------------------------------------------
    # 内部ユーティリティ
    # --------------------------------------------------------
    def _read_file_content(self, file_path: str) -> str:
        """
        ファイル内容をテキストとして読み取る。

        方針:
        - utf-8 を基本とする
        - 読めない場合は例外を送出する（呼び出し側で握り潰す）

        注意:
        - 正規化や改行変換は行わない
        - Snapshot は「生の内容」を保持する
        """

        # encoding を明示することで OS 依存挙動を防ぐ
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


# ============================================================
# export 制御
# ============================================================
__all__ = [
    "SnapshotBuilder",
]