# backend/infra/workspace_scanner.py
"""
WorkspaceScanner 定義

このファイルは、ai-workbench Backend における
「Workspace（作業空間）」を実際のファイルシステムから
走査（scan）する責務を持つ。

この層の役割:
- 実ディスク上のファイル構造をそのまま走査する
- ファイル一覧を WorkspaceIndex として構築する
- 余計な解釈・判断を一切行わない

やってはいけないこと:
- ファイル内容の意味解釈
- import / export 解析
- Snapshot / Diff の生成
- 保存処理
- LLM 呼び出し
- キャラクター・表現ロジック

infra/workspace_scanner.py は
「現実をそのまま写す」ための最下層であり、
賢さを持たせてはいけない。
"""

from __future__ import annotations

import os
import hashlib
from datetime import datetime
from typing import List

from backend.domain.workspace_index import (
    WorkspaceIndex,
    WorkspaceFile,
)
from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# WorkspaceScanner
# ============================================================
class WorkspaceScanner:
    """
    Workspace をスキャンするクラス。

    注意:
    - インスタンスは状態を持たない
    - 毎回生成して使い捨てる前提
    """

    def scan(self, project_id: str, root_path: str) -> WorkspaceIndex:
        """
        指定されたルートパス以下を再帰的に走査し、
        WorkspaceIndex を生成する。

        Parameters:
        - project_id: プロジェクト識別子（API 層から渡される）
        - root_path: スキャン対象のルートディレクトリ

        Returns:
        - WorkspaceIndex

        例外:
        - root_path が存在しない場合は例外を送出する
        - 個々のファイル読み取り失敗はログ出力してスキップする
        """

        logger.info(
            "Workspace scan started: project_id=%s root_path=%s",
            project_id,
            root_path,
        )

        if not os.path.exists(root_path):
            raise RuntimeError(f"root_path does not exist: {root_path}")

        if not os.path.isdir(root_path):
            raise RuntimeError(f"root_path is not a directory: {root_path}")

        files: List[WorkspaceFile] = []

        # os.walk を使ってディレクトリを再帰的に走査する
        for dirpath, dirnames, filenames in os.walk(root_path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)

                # ルートからの相対パスに正規化する
                rel_path = os.path.relpath(full_path, root_path)

                try:
                    file_hash = self._calculate_file_hash(full_path)
                except (PermissionError, OSError) as e:
                    # 読めないファイルは想定内（lock / 権限 / 使用中など）
                    logger.info(
                        "Skipped unreadable file: %s (%s)",
                        full_path,
                        e.__class__.__name__,
                    )
                    continue

                # 注意:
                # - language / imports / exports / dependencies は
                #   scan フェーズでは扱わないため空値とする
                files.append(
                    WorkspaceFile(
                        path=rel_path.replace(os.sep, "/"),
                        language=None,
                        hash=file_hash,
                        imports=[],
                        exports=[],
                        dependencies=[],
                    )
                )

        workspace = WorkspaceIndex(
            project_id=project_id,
            index_version="v1",
            generated_at=datetime.utcnow().isoformat(),
            files=files,
        )

        logger.info(
            "Workspace scan completed: project_id=%s files=%d",
            project_id,
            len(files),
        )

        return workspace

    # --------------------------------------------------------
    # 内部ユーティリティ
    # --------------------------------------------------------
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        ファイル内容から SHA-256 ハッシュを計算する。

        注意:
        - バイナリとして読み取る
        - 大きなファイルにも対応できるよう chunk 単位で読む
        """

        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()


__all__ = [
    "WorkspaceScanner",
]