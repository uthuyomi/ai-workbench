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
# スキャン除外設定（infra 固有）
# ============================================================
#
# 重要:
# - ここに定義される除外ルールは「ファイルシステム都合」
# - domain / api / service には一切漏らさない
# - 将来 .ai-workbenchignore 等を作る場合も
#   ここが拡張ポイントになる
#

# Python / JavaScript 系で「読む意味がない or 危険」なディレクトリ
IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    ".next",
    "node_modules",
}

# 読み取る必要がない・ロックされがちな拡張子
IGNORE_EXTENSIONS = {
    ".pyc",
    ".lock",
}


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

        # ----------------------------------------------------
        # os.walk による再帰走査
        #
        # 注意:
        # - dirnames を in-place で書き換えることで
        #   以降の再帰そのものを止める
        # - これをやらないと .git / node_modules を
        #   無限に舐めることになる
        # ----------------------------------------------------
        for dirpath, dirnames, filenames in os.walk(root_path):
            # 除外ディレクトリをその場で削除
            dirnames[:] = [
                d for d in dirnames
                if d not in IGNORE_DIRS
            ]

            for filename in filenames:
                # 拡張子ベースの除外
                _, ext = os.path.splitext(filename)
                if ext in IGNORE_EXTENSIONS:
                    continue

                full_path = os.path.join(dirpath, filename)

                # ルートからの相対パスに正規化
                rel_path = os.path.relpath(full_path, root_path)

                try:
                    file_hash = self._calculate_file_hash(full_path)
                except (PermissionError, OSError) as e:
                    # 読めないファイルは想定内
                    # （lock / 権限 / 使用中など）
                    logger.info(
                        "Skipped unreadable file: %s (%s)",
                        full_path,
                        e.__class__.__name__,
                    )
                    continue

                # scan フェーズでは意味情報は一切扱わない
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