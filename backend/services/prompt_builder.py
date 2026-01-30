# backend/services/prompt_builder.py
"""
Prompt Builder 定義

このファイルは、ai-workbench Backend における
「LLM に渡すプロンプトを組み立てる」役割のみを担う。

この層の役割は非常に限定されている。

やること:
- system / user プロンプトの構造を組み立てる
- 上位層から渡された情報を、LLM が理解しやすい形に整形する

やってはいけないこと:
- 判断・推論を行う
- LLM を呼び出す
- 応答を解釈する
- mode（dev / casual 等）を内部で分岐する

Prompt Builder は
「何を考えるか」ではなく
「どう聞くか」だけを担当する。
"""

from __future__ import annotations

from typing import Optional

from backend.domain.snapshot import Snapshot
from backend.domain.diff import Diff
from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# Prompt Builder
# ============================================================
class PromptBuilder:
    """
    プロンプト生成専用クラス。

    注意:
    - 状態を持たない
    - LLM の種類を知らない
    - 応答形式を前提にしない

    「渡された情報を、文章構造に変換するだけ」
    それ以上の責務を与えてはいけない。
    """

    # --------------------------------------------------------
    # System Prompt
    # --------------------------------------------------------
    def build_system_prompt(self) -> str:
        """
        system ロール用のプロンプトを生成する。

        ここでは:
        - LLM に求める振る舞い
        - 出力に対する基本姿勢

        だけを定義する。

        注意:
        - タスク固有の指示を書いてはいけない
        - JSON 形式強制などはここで行わない
        """

        logger.debug("Building system prompt")

        return (
            "You are an assistant that helps with software development tasks.\n"
            "Follow the given instructions carefully and respond accurately.\n"
            "Do not make assumptions beyond the provided information."
        )

    # --------------------------------------------------------
    # User Prompt
    # --------------------------------------------------------
    def build_user_prompt(
        self,
        snapshot: Snapshot,
        diff: Optional[Diff] = None,
    ) -> str:
        """
        user ロール用のプロンプトを生成する。

        引数:
        - snapshot : 判断対象となる Snapshot
        - diff     : 既存 Diff（再生成・修正時のみ使用）

        戻り値:
        - user プロンプト文字列

        注意:
        - Snapshot の内容を改変してはいけない
        - Diff の有無による「判断」は行わない
        """

        logger.debug(
            "Building user prompt: project_id=%s files=%d",
            snapshot.project_id,
            len(snapshot.files),
        )

        lines: list[str] = []

        # ----------------------------------------------------
        # Snapshot 情報
        # ----------------------------------------------------
        lines.append("The following files are provided as context:\n")

        for file in snapshot.files:
            lines.append(f"--- FILE: {file.path} ---")
            lines.append(file.content)
            lines.append(f"--- END FILE: {file.path} ---\n")

        # ----------------------------------------------------
        # 既存 Diff がある場合（再生成・修正用）
        # ----------------------------------------------------
        if diff:
            lines.append("An existing proposed diff is shown below:\n")

            for diff_file in diff.files:
                lines.append(f"--- DIFF TARGET: {diff_file.path} ---")
                lines.append("<<< BEFORE >>>")
                lines.append(diff_file.before)
                lines.append("<<< AFTER >>>")
                lines.append(diff_file.after)
                lines.append(f"--- END DIFF: {diff_file.path} ---\n")

        # ----------------------------------------------------
        # 最終指示
        # ----------------------------------------------------
        lines.append(
            "Based on the context above, perform the requested task."
        )

        return "\n".join(lines)


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - Prompt Builder は services 層専用
# - LLMService と統合してはいけない
# - プロンプトの内容に「判断結果」を混ぜない
#
# Prompt Builder は
# 「聞き方を整える係」であり、
# 「考える係」ではない。
#

__all__ = [
    "PromptBuilder",
]
