# backend/core/workflow.py
"""
Workflow 定義

このファイルは、ai-workbench Backend における
「実行フロー全体の統合・制御」を担当する core 層の実装である。

Workflow の役割:
- 外部リクエストを受け取る
- 処理モードを決定する
- WorkspaceIndex / Snapshot を入口として思考エンジンを実行する
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
from backend.domain.workspace_index import WorkspaceIndex
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
    # Public API（Workspace 起点）
    # --------------------------------------------------------
    def execute_from_workspace(
        self,
        workspace: WorkspaceIndex,
        root_path: str,
        requested_mode: Optional[str] = None,
        existing_diff: Optional[Diff] = None,
    ) -> Diff:
        """
        WorkspaceIndex を入口として Backend 処理フローを実行する。

        引数:
        - workspace       : scan 済み WorkspaceIndex
        - root_path       : 実ファイルのルートパス
        - requested_mode  : 外部から指定された mode
        - existing_diff   : 既存 Diff（再生成・修正用）

        戻り値:
        - Diff（変更提案）

        注意:
        - Snapshot 構築は DevEngine 側に委譲する
        - Workflow は順序制御のみを行う
        """

        logger.info(
            "Workflow execution (workspace) started: project_id=%s files=%d",
            workspace.project_id,
            len(workspace.files),
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
            diff = self._dev_engine.run_from_workspace(
                workspace=workspace,
                root_path=root_path,
                existing_diff=existing_diff,
            )

        elif mode == Mode.CASUAL:
            # 現段階では DEV フローにフォールバック
            logger.info("CASUAL mode currently falls back to DEV flow")
            diff = self._dev_engine.run_from_workspace(
                workspace=workspace,
                root_path=root_path,
                existing_diff=existing_diff,
            )

        else:
            raise RuntimeError(f"Unhandled mode: {mode}")

        logger.info(
            "Workflow execution (workspace) completed: diff_files=%d",
            len(diff.files),
        )

        return diff

    # --------------------------------------------------------
    # Public API（Snapshot 起点：既存互換）
    # --------------------------------------------------------
    def execute(
        self,
        snapshot: Snapshot,
        requested_mode: Optional[str] = None,
        existing_diff: Optional[Diff] = None,
    ) -> Diff:
        """
        Snapshot を入口として Backend 処理フローを実行する。

        ※ 既存 API / テスト互換のため残す。
        """

        logger.info(
            "Workflow execution (snapshot) started: project_id=%s",
            snapshot.project_id,
        )

        mode = self._mode_router.resolve_mode(requested_mode)
        logger.info("Workflow mode resolved: %s", mode.value)

        if mode == Mode.DEV:
            diff = self._dev_engine.run(
                snapshot=snapshot,
                existing_diff=existing_diff,
            )

        elif mode == Mode.CASUAL:
            logger.info("CASUAL mode currently falls back to DEV flow")
            diff = self._dev_engine.run(
                snapshot=snapshot,
                existing_diff=existing_diff,
            )

        else:
            raise RuntimeError(f"Unhandled mode: {mode}")

        logger.info(
            "Workflow execution (snapshot) completed: diff_files=%d",
            len(diff.files),
        )

        return diff


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - Workflow に判断ロジックを足さない
# - Snapshot 構築をここで行わない
# - Workspace / Snapshot の両入口を許容する
#
# Workflow は
# 「順番を守らせる存在」であり、
# 「考える存在」ではない。
#

__all__ = [
    "Workflow",
]