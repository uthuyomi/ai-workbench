# backend/domain/character.py
"""
Character ドメインモデル定義

このファイルは、ai-workbench Backend における
「キャラクター（Character）」という概念の
純粋なデータモデルを定義する。

重要な前提:
- Character は「人格」ではない
- 思考・判断・推論は一切行わない
- キャラクターとは「表現ルールの集合」を指す

Backend は、
「どのキャラクターを使うか」を選択するだけであり、
キャラクター自身に判断を委ねてはならない。

このファイルは、
Expression Layer の拡張性を長期的に保証するための
設計上の要石となる。
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# -----------------------------
# Character
# -----------------------------
class Character(BaseModel):
    """
    Character 定義モデル。

    このモデルは、
    - 利用可能なキャラクター一覧の表現
    - character_id に対応するメタ情報の保持
    - Expression Layer が参照する静的定義

    のために使用される。

    注意:
    - 思考ロジックを持たせてはいけない
    - 状態を持たせてはいけない
    - ユーザーごとの変化を入れてはいけない
    """

    # キャラクター識別子
    #
    # - API や内部処理で使用される一意な ID
    # - ファイル名・registry のキーと一致する想定
    #
    # 例: "nitori"
    id: str = Field(min_length=1)

    # 表示用名称
    #
    # - フロントエンドや UI で人間に見せる名前
    # - 内部ロジックでは使用しない
    #
    # 例: "河城にとり"
    display_name: str = Field(min_length=1)

    # キャラクターの説明文
    #
    # - UI 表示用
    # - キャラクター選択画面での補助説明
    #
    # 注意:
    # - ここに「性格判断」や「思考傾向」を
    #   ロジック前提で書いてはいけない
    description: Optional[str] = None

    # 表現プロファイル
    #
    # - キャラクターが持つ「表現上の特徴」を
    #   キーワード的に列挙するためのフィールド
    #
    # 使用例:
    # - ["technical", "casual", "short_sentence"]
    #
    # 注意:
    # - これは判断材料ではない
    # - Dev Engine が参照してはいけない
    # - Expression Layer でのみ使用される
    expression_profile: List[str] = Field(default_factory=list)

    # 禁止ルール一覧
    #
    # - キャラクターとして「やってはいけない表現」を明示する
    # - 例: 過度な断定、命令口調、攻撃的表現など
    #
    # 注意:
    # - 判断禁止ではなく「表現禁止」
    # - ロジック分岐条件に使ってはいけない
    forbidden_rules: List[str] = Field(default_factory=list)

    # -----------------------------
    # Pydantic 設定
    # -----------------------------
    model_config = {
        # 想定外フィールドの混入を禁止する。
        # キャラクター定義が静かに肥大化するのを防ぐ。
        "extra": "forbid",

        # Character は「定義」であり「状態」ではないため、
        # イミュータブルとして扱う。
        #
        # 変更が必要な場合は、
        # 新しい Character 定義を作る。
        "frozen": True,
    }


# -----------------------------
# export 制御
# -----------------------------
# 外部に公開するシンボルを明示することで、
# このモジュールの責務範囲を固定する。
__all__ = [
    "Character",
]
