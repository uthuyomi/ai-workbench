# backend/services/expression/registry.py
"""
Expression Registry 定義

このファイルは、ai-workbench における
「Expression（表現クラス）」の登録・取得を管理する。

Registry の役割:
- 利用可能な Expression クラスを一元管理する
- expression_id をキーに Expression を取得できるようにする
- キャラクター追加を容易にする

やってはいけないこと:
- Expression の中身を解釈する
- 表現ロジックに介入する
- if / elif / switch 的な分岐でキャラを選ぶ
- 暗黙的なデフォルトを増やす

Registry は
「対応表」であり、
「判断装置」ではない。
"""

from __future__ import annotations

from typing import Dict, Type

from backend.services.expression.base import ExpressionBase


class ExpressionRegistry:
    """
    Expression 登録管理クラス。

    設計方針:
    - expression_id -> Expression クラス のみを管理
    - インスタンス生成もここで行う
    - グローバルな if 分岐は禁止
    """

    def __init__(self) -> None:
        # 登録済み Expression クラスの辞書
        # key: expression_id
        # value: Expression クラス
        self._registry: Dict[str, Type[ExpressionBase]] = {}

    # ============================================================
    # 登録処理
    # ============================================================
    def register(self, expression_cls: Type[ExpressionBase]) -> None:
        """
        Expression クラスを登録する。

        引数:
        - expression_cls:
            ExpressionBase を継承したクラス

        注意:
        - expression_id の重複はエラーとする
        - インスタンスではなく「クラス」を登録する
        """

        # ExpressionBase を継承しているか最低限チェック
        if not issubclass(expression_cls, ExpressionBase):
            raise TypeError(
                "expression_cls must be subclass of ExpressionBase"
            )

        # 一度インスタンス化して ID を取得する
        instance = expression_cls()
        expression_id = instance.expression_id

        if expression_id in self._registry:
            raise ValueError(
                f"Expression already registered: {expression_id}"
            )

        self._registry[expression_id] = expression_cls

    # ============================================================
    # 取得処理
    # ============================================================
    def get(self, expression_id: str) -> ExpressionBase:
        """
        expression_id を指定して Expression インスタンスを取得する。

        戻り値:
        - ExpressionBase のインスタンス

        注意:
        - 未登録の場合は KeyError を投げる
        """

        try:
            expression_cls = self._registry[expression_id]
        except KeyError as e:
            raise KeyError(
                f"Expression not found: {expression_id}"
            ) from e

        # Expression は状態を持たない前提のため、
        # 取得時に毎回新しいインスタンスを生成する
        return expression_cls()

    # ============================================================
    # 補助メソッド
    # ============================================================
    def list_ids(self) -> list[str]:
        """
        登録されている expression_id の一覧を返す。
        """
        return list(self._registry.keys())

    def is_registered(self, expression_id: str) -> bool:
        """
        指定した expression_id が登録済みかどうかを返す。
        """
        return expression_id in self._registry


# ============================================================
# グローバル Registry
# ============================================================
#
# Expression はアプリケーション全体で共有されるため、
# Registry は 1 インスタンスを使い回す前提とする。
#
expression_registry = ExpressionRegistry()


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - registry に Expression のロジックを書かない
# - キャラ選択を if 文でやらない
# - ここを「便利クラス」にしない
#
# registry は
# 「登録簿」であり、
# 「司令塔」ではない。
#

__all__ = [
    "ExpressionRegistry",
    "expression_registry",
]
