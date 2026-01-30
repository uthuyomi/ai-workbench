# backend/core/workflow.py
"""
Workflow 定義

このファイルは、ai-workbench Backend における
「実行フロー全体の統合・制御」を担当する core 層の実装である。

Workflow の役割:
- 外部リクエストを受け取る
- 処理モードを決定する
- Snapshot を受け取り思考エンジンを実行する
- 結果（Diff）を上位へ返す

重要:
Workflow 自身は「考えない」「作らない」「書き換えない」。

やること:
- 各コンポーネントを正しい順序で呼び出す
- 責務の境界を越えないように制御する

やってはいけないこと:
- 判断ロジックを実装する
- LLM を直接呼び出す
- ファイル操作・DB操作を行う
- 表現（UI / 文体）を決める

Workflow は
「指揮者」であって
「演奏者」ではない。
"""

from __future__ import annotations

from typing import Optional

from backend.domain.snapshot import Snapshot
from backend.domain.diff import Diff
from backend.core.mode_router import Mode, ModeRouter
from backend.core.dev_engine import DevEngine
from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# Workflow
# ============================================================
class Workflow:
    """
    Backend 実行フロー統合クラス。

    このクラスは、
    - ModeRouter
    - DevEngine

    を束ねて、
    Backend 処理の「流れ」だけを定義する。

    注意:
    - 状態を保持しない
    - 毎回同じ入力は同じ経路を通る
    """

    def __init__(
        self,
        mode_router: ModeRouter,
        dev_engine: DevEngine,
    ) -> None:
        """
        Workflow を初期化する。

        引数:
        - mode_router : 処理モード判定担当
        - dev_engine  : Dev 思考エンジン

        すべて外部から注入する（DI）
        """

        self._mode_router = mode_router
        self._dev_engine = dev_engine

        logger.info("Workflow initialized")

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------
    def execute(
        self,
        snapshot: Snapshot,
        requested_mode: Optional[str] = None,
        existing_diff: Optional[Diff] = None,
    ) -> Diff:
        """
        Backend 処理フローを実行する。

        引数:
        - snapshot        : 判断対象 Snapshot
        - requested_mode  : 外部から指定された mode
        - existing_diff   : 既存 Diff（再生成・修正用）

        戻り値:
        - Diff（変更提案）

        注意:
        - ここでは例外を握りつぶさない
        - 上位層（API）がハンドリングする前提
        """

        logger.info(
            "Workflow execution started: project_id=%s",
            snapshot.project_id,
        )

        # ----------------------------------------------------
        # Mode 解決
        # ----------------------------------------------------
        mode = self._mode_router.resolve_mode(requested_mode)

        logger.info("Workflow mode resolved: %s", mode.value)

        # ----------------------------------------------------
        # Mode ごとの処理分岐
        # ----------------------------------------------------
        if mode == Mode.DEV:
            # 開発支援モード
            diff = self._dev_engine.run(
                snapshot=snapshot,
                existing_diff=existing_diff,
            )

        elif mode == Mode.CASUAL:
            # CASUAL モードは Phase 3（表現層）で扱う想定。
            # 現段階では DEV と同一フローを通す。
            logger.info("CASUAL mode currently falls back to DEV flow")
            diff = self._dev_engine.run(
                snapshot=snapshot,
                existing_diff=existing_diff,
            )

        else:
            # Mode Enum が増えた際の安全装置
            raise RuntimeError(f"Unhandled mode: {mode}")

        logger.info(
            "Workflow execution completed: diff_files=%d",
            len(diff.files),
        )

        return diff


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - Workflow に判断ロジックを足さない
# - 各モードの中身は engine / services 側で実装する
# - Workflow を「便利ハブ」にしない
#
# Workflow は
# 「順番を守らせる存在」であり、
# 「考える存在」ではない。
#

__all__ = [
    "Workflow",
]
