# backend/core/mode_router.py
"""
Mode Router 定義

このファイルは、ai-workbench Backend における
「処理モードの分岐」を担当する core 層の実装である。

Mode Router の役割は明確である。

やること:
- 実行リクエストから「どのモードで処理するか」を決定する
- 上位フロー（workflow）に対して分岐結果を返す

やってはいけないこと:
- 判断・推論を行う
- LLM を呼び出す
- Diff や Snapshot を生成する
- 処理内容を実行する

Mode Router は
「思考の中身」ではなく
「どの思考ルートに入るか」だけを決める存在である。
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# Mode 定義
# ============================================================
class Mode(str, Enum):
    """
    Backend が扱う処理モード定義。

    新しいモードを追加する場合は、
    - まずこの Enum に追加する
    - 次に workflow 側で明示的に対応させる

    注意:
    - mode 名は API / Frontend と共有される前提
    - 曖昧な命名は禁止
    """

    DEV = "dev"
    CASUAL = "casual"


# ============================================================
# Mode Router
# ============================================================
class ModeRouter:
    """
    処理モードを決定するためのルーター。

    注意:
    - このクラスは状態を持たない
    - 毎回「入力 → 出力」のみを返す
    """

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------
    def resolve_mode(self, requested_mode: Optional[str]) -> Mode:
        """
        リクエストされた mode 文字列から、
        Backend 内部で使用する Mode を決定する。

        引数:
        - requested_mode : 外部から渡された mode（None 可）

        戻り値:
        - Mode Enum

        方針:
        - None または不正な値の場合は DEV にフォールバック
        - ここでエラーにはしない（上位フローで制御する）
        """

        logger.debug("Resolving mode: requested_mode=%s", requested_mode)

        if not requested_mode:
            logger.info("No mode specified. Fallback to DEV mode.")
            return Mode.DEV

        try:
            mode = Mode(requested_mode)
            logger.info("Resolved mode: %s", mode.value)
            return mode
        except ValueError:
            # 不正な mode 指定は警告に留める
            logger.warning(
                "Invalid mode specified: %s. Fallback to DEV mode.",
                requested_mode,
            )
            return Mode.DEV


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - Mode Router に if/else の処理分岐を増やさない
# - mode ごとの処理内容は workflow / engine 側で扱う
# - mode を「人格」や「性格」と結びつけない
#
# Mode は単なる「処理経路の識別子」であり、
# 思考内容そのものではない。
#

__all__ = [
    "Mode",
    "ModeRouter",
]
