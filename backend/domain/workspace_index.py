# backend/domain/workspace_index.py
"""
WorkspaceIndex ドメインモデル定義

このファイルは、ai-workbench Backend における
「Workspace Index」という中核概念のデータ構造を定義する。

Workspace Index とは:
- Workspace（コードベース全体）の「地図」
- ファイル構造・依存関係・識別情報のみを保持する
- 実ファイルの内容（コード本文）は保持しない

重要な前提:
- Workspace Index は記憶装置ではない
- 推論結果や判断結果を保持してはいけない
- Snapshot 生成対象を決めるための参照用構造である

この定義が曖昧になると、
Backend 全体の安全性・追跡性が崩壊するため、
非常に強い制約をかけて設計する。
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# -----------------------------
# WorkspaceFile
# -----------------------------
class WorkspaceFile(BaseModel):
    """
    Workspace Index 内で扱う単一ファイルの構造定義。

    このモデルは、
    - ファイルの存在
    - ファイル同士の関係性
    - Snapshot 生成時の参照判断

    のために使用される。

    注意:
    - ファイル内容（コード本文）は絶対に含めない
    - LLM への入力用データではない
    """

    # ファイルパス（Workspace ルートからの相対パス）
    #
    # 例: "src/app/page.tsx"
    path: str = Field(min_length=1)

    # 判定された言語
    #
    # 例:
    # - "typescript"
    # - "python"
    # - "markdown"
    #
    # 推論精度よりも「安定した分類」を優先する。
    language: Optional[str] = None

    # ファイル内容識別用ハッシュ
    #
    # - 内容変更検知のために使用
    # - 本文を保持しない代替としての識別子
    #
    # 注意:
    # - ハッシュ生成ロジックは infra 層の責務
    hash: Optional[str] = None

    # import しているシンボル・モジュール一覧
    #
    # - 静的解析結果
    # - Snapshot 範囲決定の補助情報
    imports: List[str] = Field(default_factory=list)

    # export しているシンボル・モジュール一覧
    #
    # - 依存関係の逆引き用
    exports: List[str] = Field(default_factory=list)

    # 依存しているファイルパス一覧
    #
    # - import 情報などを元に構築される
    # - Workspace 内部の関係性のみを扱う
    dependencies: List[str] = Field(default_factory=list)

    # -----------------------------
    # Pydantic 設定
    # -----------------------------
    model_config = {
        # 想定外フィールドの混入を禁止
        "extra": "forbid",

        # WorkspaceFile は状態を持たない構造定義のため、
        # イミュータブルとして扱う
        "frozen": True,
    }


# -----------------------------
# WorkspaceIndex
# -----------------------------
class WorkspaceIndex(BaseModel):
    """
    Workspace Index 全体を表すモデル。

    このモデルは、
    - Backend が Workspace をどう「認識しているか」
    - どのファイルが存在し、どう繋がっているか

    を表現するための唯一の正規構造である。

    注意:
    - 実ファイルの内容を保持しない
    - 推論結果・判断結果を含めない
    - キャッシュや履歴として使わない
    """

    # 紐づく Project ID
    #
    # Workspace Index は必ず Project 単位で管理される。
    project_id: str = Field(min_length=1)

    # Index のバージョン識別子
    #
    # - 再生成・更新の識別用
    # - 実装依存の形式でよい（例: UUID / timestamp）
    index_version: str = Field(min_length=1)

    # Index 生成時刻（ISO8601 文字列想定）
    #
    # - デバッグ
    # - 更新履歴確認
    generated_at: str = Field(min_length=1)

    # Workspace 内の全ファイル構造
    #
    # 注意:
    # - 順序に意味を持たせない
    # - 参照・検索は上位層で行う
    files: List[WorkspaceFile] = Field(default_factory=list)

    # -----------------------------
    # Pydantic 設定
    # -----------------------------
    model_config = {
        # フィールド追加による静かな仕様拡張を防止
        "extra": "forbid",

        # Workspace Index はスナップショット的構造であり、
        # 書き換え前提では扱わない
        "frozen": True,
    }


# -----------------------------
# export 制御
# -----------------------------
# このモジュールで公開する構造を明示する。
__all__ = [
    "WorkspaceFile",
    "WorkspaceIndex",
]
