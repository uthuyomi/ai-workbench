# backend/infra/file_loader.py
"""
File Loader 定義

このファイルは、ai-workbench Backend における
「ファイル読み込み」専用の infra 層実装である。

この層の役割は極めて限定的である。

やること:
- Workspace 内の実ファイルを読み取る
- 指定されたパスの内容を文字列として返す

やってはいけないこと:
- ファイル内容を解析する
- 意味を解釈する
- Snapshot の要否を判断する
- Diff や変更案を生成する

このファイルは、
「現実のファイルシステム」と
「Backend 内部構造」を分離するための
最前線の境界層である。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List

from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# File Loader
# ============================================================
def read_file(root_dir: Path, relative_path: str) -> str:
    """
    単一ファイルを読み込む。

    引数:
    - root_dir      : Workspace のルートディレクトリ
    - relative_path : Workspace ルートからの相対パス

    戻り値:
    - ファイルの全文内容（文字列）

    注意:
    - ファイルが存在しない場合は例外を投げる
    - 文字コードの推測は行わない（UTF-8 前提）
    """

    file_path = root_dir / relative_path

    logger.debug("Reading file: %s", file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが存在しません: {file_path}")

    if not file_path.is_file():
        raise IsADirectoryError(f"ファイルではありません: {file_path}")

    # UTF-8 前提で全文を読み込む
    # 正規化・トリム・変換はここでは行わない
    return file_path.read_text(encoding="utf-8")


def read_files(
    root_dir: Path,
    relative_paths: Iterable[str],
) -> List[str]:
    """
    複数ファイルをまとめて読み込む。

    引数:
    - root_dir        : Workspace のルートディレクトリ
    - relative_paths : 読み込むファイルの相対パス一覧

    戻り値:
    - ファイル内容のリスト（順序は入力に従う）

    注意:
    - 途中でエラーが発生した場合は即例外を投げる
    - 部分成功・部分失敗は扱わない
    """

    contents: List[str] = []

    for path in relative_paths:
        contents.append(read_file(root_dir, path))

    return contents


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - このファイルは infra 層から外に出してはいけない
# - domain / core 層から直接 import してはいけない
# - 「便利そうだから」処理を足さない
#
# File Loader はあくまで「読むだけ」。
# ここが賢くなり始めたら、それは設計崩壊の兆候である。
#

__all__ = [
    "read_file",
    "read_files",
]
