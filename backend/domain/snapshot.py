# backend/domain/snapshot.py
"""
Snapshot ドメインモデル定義

このファイルは、ai-workbench Backend における
「Snapshot」という概念を定義する。

Snapshot とは:
- 判断に必要な最小限の実ファイル内容の集合
- Workspace Index を元に「必要な分だけ」生成される
- 一時的な参照データであり、永続化を前提としない

重要な前提:
- Snapshot は Workspace Index の代替ではない
- Snapshot はキャッシュではない
- 判断完了後に破棄されることを前提とする

この境界が崩れると、
Backend は簡単に「ブラックボックス化」する。
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


# -----------------------------
# SnapshotFile
# -----------------------------
class SnapshotFile(BaseModel):
    """
    Snapshot 内で扱う単一ファイルの定義。

    このモデルは、
    - 実ファイルの「全文内容」
    - どのパスのファイルか

    だけを保持する。

    注意:
    - 解析結果を保持してはいけない
    - 依存関係情報を持たせてはいけない
    - 判断結果を書き込んではいけない
    """

    # ファイルパス（Workspace ルートからの相対パス）
    path: str = Field(min_length=1)

    # 実ファイルの全文内容
    #
    # - LLM に渡される可能性がある
    # - Snapshot の中で最も重いデータ
    #
    # 注意:
    # - 正規化や加工はこの層で行わない
    content: str = Field(min_length=0)

    # -----------------------------
    # Pydantic 設定
    # -----------------------------
    model_config = {
        # 想定外フィールドの混入を禁止
        "extra": "forbid",

        # SnapshotFile は生成後に書き換えない
        # 必要な場合は Snapshot を作り直す
        "frozen": True,
    }


# -----------------------------
# Snapshot
# -----------------------------
class Snapshot(BaseModel):
    """
    Snapshot 全体を表すモデル。

    Snapshot は、
    - Dev Engine が判断を行うための「参照用データ」
    - Backend 内部でのみ使用される一時構造

    として扱われる。

    注意:
    - 永続化前提で設計してはいけない
    - Workspace Index の代替として使ってはいけない
    """

    # 紐づく Project ID
    project_id: str = Field(min_length=1)

    # Snapshot に含まれるファイル一覧
    #
    # - 必要最小限のみを含める
    # - 全ファイルを無条件に入れない
    files: List[SnapshotFile] = Field(default_factory=list)

    # -----------------------------
    # Pydantic 設定
    # -----------------------------
    model_config = {
        # フィールド肥大化を防止
        "extra": "forbid",

        # Snapshot は不変データとして扱う
        "frozen": True,
    }


# -----------------------------
# export 制御
# -----------------------------
# 外部に公開する構造を限定する
__all__ = [
    "SnapshotFile",
    "Snapshot",
]
