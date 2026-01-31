# backend/core/dev_engine.py
"""
Dev Engine 定義

このファイルは、ai-workbench Backend における
「開発支援用 思考エンジン」の中核実装である。

Dev Engine の役割:
- WorkspaceIndex から Snapshot を生成する（内部的に）
- Snapshot を入力として受け取る
- Prompt を組み立て、LLM に問い合わせる
- その結果を「Diff（変更提案）」として生成する

重要:
Dev Engine は「実装する」のではない。
Dev Engine は「提案する」だけである。

やってはいけないこと:
- ファイルを書き換える
- Diff を適用する
- 人間の承認をスキップする
- 状態を内部に保持する

このエンジンは、
Backend の「思考」を司るが、
Backend の「手」ではない。
"""

from __future__ import annotations

from typing import Optional

from backend.domain.snapshot import Snapshot
from backend.domain.workspace_index import WorkspaceIndex
from backend.domain.diff import Diff, DiffFile

from backend.infra.snapshot_builder import SnapshotBuilder
from backend.infra.logger import get_logger

from backend.services.llm_service import LLMService
from backend.services.prompt_builder import PromptBuilder


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# Dev Engine
# ============================================================
class DevEngine:
    """
    開発支援用 思考エンジン。

    このクラスは、
    - WorkspaceIndex
    - SnapshotBuilder
    - PromptBuilder
    - LLMService

    を組み合わせて、
    「変更提案（Diff）」を生成する責務のみを持つ。

    注意:
    - 状態を保持しない
    - キャッシュを持たない
    - 再実行は常に再思考
    """

    def __init__(
        self,
        llm_service: LLMService,
        prompt_builder: PromptBuilder,
        snapshot_builder: SnapshotBuilder,
    ) -> None:
        """
        DevEngine を初期化する。

        引数:
        - llm_service      : LLM 呼び出し担当
        - prompt_builder  : プロンプト構築担当
        - snapshot_builder: Snapshot 構築担当（infra）

        ※ 依存はすべて外から注入する（DI）
        """

        self._llm_service = llm_service
        self._prompt_builder = prompt_builder
        self._snapshot_builder = snapshot_builder

        logger.info("DevEngine initialized")

    # --------------------------------------------------------
    # Public API（Workspace 入口）
    # --------------------------------------------------------
    def run_from_workspace(
        self,
        workspace: WorkspaceIndex,
        root_path: str,
        existing_diff: Optional[Diff] = None,
    ) -> Diff:
        """
        WorkspaceIndex から Snapshot を生成し、
        Dev 思考を実行して Diff を生成する。

        このメソッドは、
        API / Controller 層から呼ばれることを想定する。

        引数:
        - workspace      : WorkspaceIndex（scan 済み）
        - root_path     : 実ファイルのルートパス
        - existing_diff : 既存 Diff（再生成・修正用）

        戻り値:
        - Diff（変更提案）
        """

        logger.info(
            "DevEngine run_from_workspace started: project_id=%s files=%d",
            workspace.project_id,
            len(workspace.files),
        )

        # ----------------------------------------------------
        # Snapshot 構築（ここが今回の接続ポイント）
        # ----------------------------------------------------
        snapshot = self._snapshot_builder.build(
            workspace=workspace,
            root_path=root_path,
            target_paths=None,  # 現段階では全体 Snapshot
        )

        # Snapshot を元に通常の run を呼び出す
        return self.run(
            snapshot=snapshot,
            existing_diff=existing_diff,
        )

    # --------------------------------------------------------
    # Public API（Snapshot 入口）
    # --------------------------------------------------------
    def run(
        self,
        snapshot: Snapshot,
        existing_diff: Optional[Diff] = None,
    ) -> Diff:
        """
        Snapshot を元に Dev 思考を実行し、Diff を生成する。

        引数:
        - snapshot       : 判断対象の Snapshot
        - existing_diff  : 既存 Diff（再生成・修正用）

        戻り値:
        - Diff（変更提案）

        注意:
        - ここでは Diff の「構造」を作るだけ
        - 内容の正当性保証は行わない
        """

        logger.info(
            "DevEngine run started: project_id=%s files=%d",
            snapshot.project_id,
            len(snapshot.files),
        )

        # ----------------------------------------------------
        # プロンプト生成
        # ----------------------------------------------------
        system_prompt = self._prompt_builder.build_system_prompt()
        user_prompt = self._prompt_builder.build_user_prompt(
            snapshot=snapshot,
            diff=existing_diff,
        )

        # ----------------------------------------------------
        # LLM 呼び出し
        # ----------------------------------------------------
        llm_response = self._llm_service.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        # ----------------------------------------------------
        # Diff 生成（暫定）
        # ----------------------------------------------------
        #
        # 注意:
        # - この時点では LLM 応答は「生テキスト」
        # - JSON 前提にしない
        # - パース・検証は後続フェーズの責務
        #
        diff = self._build_diff_from_response(
            snapshot=snapshot,
            response_text=llm_response,
        )

        logger.info(
            "DevEngine run completed: diff_files=%d",
            len(diff.files),
        )

        return diff

    # --------------------------------------------------------
    # 内部処理
    # --------------------------------------------------------
    def _build_diff_from_response(
        self,
        snapshot: Snapshot,
        response_text: str,
    ) -> Diff:
        """
        LLM 応答テキストから Diff 構造を組み立てる。

        現段階では:
        - 全ファイルを「変更対象候補」として扱う
        - BEFORE は Snapshot の内容
        - AFTER は LLM 応答全文（暫定）

        ※ ここは将来的に段階的に精密化される想定。
        """

        diff_files: list[DiffFile] = []

        for file in snapshot.files:
            diff_files.append(
                DiffFile(
                    path=file.path,
                    before=file.content,
                    after=response_text,
                )
            )

        return Diff(
            project_id=snapshot.project_id,
            files=diff_files,
        )


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - DevEngine に IO（ファイル操作）を入れない
# - Diff 適用ロジックを入れない
# - 「賢く」しすぎない
#
# DevEngine は「思考装置」であり、
# 「実行装置」ではない。
#

__all__ = [
    "DevEngine",
]