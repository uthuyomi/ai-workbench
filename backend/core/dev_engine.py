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

    設計上の重要点:
    - DevEngine 自体は状態を一切持たない
    - Snapshot は「外部から渡される判断材料」
    - DevEngine は Snapshot の内容を保存しない

    再実行は常に「再思考」として扱う。
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

        ※ 依存はすべて外部から注入する（DI）
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
        - Workspace Scan → DevEngine 実行
        という「一気通貫ルート」で使用される。

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
        # Snapshot 構築
        # ----------------------------------------------------
        #
        # ここが Workspace → Snapshot の変換点。
        # DevEngine 自身はファイル IO を行わない。
        #
        snapshot = self._snapshot_builder.build(
            workspace=workspace,
            root_path=root_path,
            target_paths=None,  # 現段階では全体 Snapshot
        )

        logger.info(
            "Snapshot built for DevEngine: project_id=%s snapshot_files=%d",
            snapshot.project_id,
            len(snapshot.files),
        )

        # Snapshot を元に、共通の run() を呼び出す
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

        このメソッドは、
        - Frontend から Snapshot を直接渡す場合
        - API 経由で Snapshot を生成済みの場合

        の共通入口として扱う。

        引数:
        - snapshot       : 判断対象の Snapshot
        - existing_diff  : 既存 Diff（再生成・修正用）

        戻り値:
        - Diff（変更提案）

        注意:
        - Snapshot の中身をここで解釈しない
        - Diff の正当性保証は行わない
        """

        logger.info(
            "DevEngine run started: project_id=%s snapshot_files=%d",
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
        # Diff 生成（暫定実装）
        # ----------------------------------------------------
        #
        # 現段階では:
        # - LLM 応答は「生テキスト」
        # - JSON 前提にしない
        # - 厳密なパースは後続フェーズの責務
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

        現段階の方針:
        - Snapshot に含まれる全ファイルを対象にする
        - BEFORE は Snapshot の生データ
        - AFTER は LLM 応答全文（仮）

        ※ この処理は将来的に段階的に分離・精密化される。
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
# - DevEngine にファイル IO を追加しない
# - Diff 適用ロジックを追加しない
# - Snapshot を内部保存しない
#
# DevEngine は「思考装置」であり、
# 「実行装置」ではない。
#

__all__ = [
    "DevEngine",
]