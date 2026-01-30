# backend/services/expression/nitori.py
"""
河城にとり Expression 実装

このファイルは、ai-workbench における
「河城にとり（nitori）」用の表現ルールを定義する。

重要な前提:
- ここでは「どう喋るか」だけを扱う
- 判断結果・意味・内容は一切変更しない
- 思考ロジックや LLM 呼び出しは禁止

にとりはあくまで
「表現フィルタ」
であり、
「思考主体」ではない。
"""

from __future__ import annotations

from typing import Any

from backend.services.expression.base import ExpressionBase


class NitoriExpression(ExpressionBase):
    """
    河城にとり用 Expression クラス。

    特徴（表現のみ）:
    - 技術寄り
    - 軽快で少し砕けた口調
    - 上から目線にならない
    - 断定しすぎない

    注意:
    - 情報を付け足さない
    - 内容を削らない
    - 判断結果を書き換えない
    """

    # ============================================================
    # 基本メタ情報
    # ============================================================
    @property
    def expression_id(self) -> str:
        """
        Registry で使用される識別子。
        """
        return "nitori"

    @property
    def display_name(self) -> str:
        """
        UI 等で表示されるキャラクター名。
        """
        return "河城にとり"

    # ============================================================
    # 表現変換
    # ============================================================
    def format(self, text: str, *, context: dict[str, Any] | None = None) -> str:
        """
        与えられたテキストを、にとり口調に整形する。

        ルール:
        - 文意は絶対に変えない
        - 技術説明はそのまま残す
        - 語尾や前置きを軽く調整するだけ

        context:
        - 現時点では未使用
        - 将来、表現強度調整などに使う余地はある
        """

        if not text:
            # 空文字はそのまま返す（無理に喋らせない）
            return text

        # --- 前置き（軽い導入） ---
        prefix = "ちょっと見てみたけど、"

        # --- 語尾（断定を避ける） ---
        suffix = "…って感じかな。"

        # すでに改行が多い場合は、前置きを控えめにする
        if "\n" in text:
            formatted = f"{prefix}\n{text}"
        else:
            formatted = f"{prefix}{text}"

        # 強い断定を避けるため、最後に柔らかい語尾を付ける
        if not formatted.endswith(("。", "！", "?", "？")):
            formatted = f"{formatted}{suffix}"

        return formatted


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - にとりに「判断」させない
# - Diff や結論を書き換えない
# - キャラ性を足しすぎない
#
# nitori は
# 「説明役・案内役」であり、
# 「決定者」ではない。
#
