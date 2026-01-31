# backend/api/chat.py
"""
Chat API 定義

このファイルは、ai-workbench Backend における
「チャット系リクエスト」を受け取る API エンドポイントを定義する。

API 層の責務:
- 外部入力を受け取る
- 最低限のバリデーションを行う
- Workflow に処理を委譲する
- 結果をそのまま返却する

重要:
- API 層は「入口と出口」のみを扱う
- Snapshot / Diff / LLM の意味解釈は禁止
- 思考ロジックは一切持たない
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.deps import get_workflow
from backend.core.workflow import Workflow
from backend.domain.workspace_index import WorkspaceIndex
from backend.domain.snapshot import Snapshot
from backend.domain.diff import Diff
from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# Router
# ============================================================
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)


# ============================================================
# Request / Response Models
# ============================================================
class ChatFromWorkspaceRequest(BaseModel):
    """
    WorkspaceIndex 起点の Chat リクエスト。

    想定利用元:
    - Frontend（Workspace Scan → Chat）
    - 初期 UI 操作

    注意:
    - Snapshot はここでは受け取らない
    - Snapshot 構築は Workflow / DevEngine 側の責務
    """

    workspace: WorkspaceIndex = Field(
        description="scan 済み WorkspaceIndex"
    )

    root_path: str = Field(
        description="実ファイルのルートパス（Snapshot 構築用）"
    )

    mode: Optional[str] = Field(
        default=None,
        description="処理モード（dev / casual 等）",
    )

    existing_diff: Optional[Diff] = Field(
        default=None,
        description="既存 Diff（再生成・修正用）",
    )


class ChatFromSnapshotRequest(BaseModel):
    """
    Snapshot 起点の Chat リクエスト。

    想定利用元:
    - Frontend（Snapshot API 経由）
    - VSCode Extension
    - 将来の自動実行フロー

    注意:
    - Snapshot は「生成済み前提」
    - API 層では Snapshot を加工しない
    """

    snapshot: Snapshot = Field(
        description="生成済み Snapshot"
    )

    mode: Optional[str] = Field(
        default=None,
        description="処理モード（dev / casual 等）",
    )

    existing_diff: Optional[Diff] = Field(
        default=None,
        description="既存 Diff（再生成・修正用）",
    )


class ChatResponse(BaseModel):
    """
    Chat API 共通レスポンス。

    注意:
    - Diff は「変更提案そのもの」
    - API 層では解釈しない
    """

    diff: Diff


# ============================================================
# Endpoint: Workspace 起点
# ============================================================
@router.post(
    "",
    response_model=ChatResponse,
    summary="Chat from WorkspaceIndex",
)
def chat_from_workspace(
    request: ChatFromWorkspaceRequest,
    workflow: Workflow = Depends(get_workflow),
) -> ChatResponse:
    """
    WorkspaceIndex 起点の Chat 実行。

    処理内容:
    - WorkspaceIndex を受け取る
    - Workflow に処理を委譲する
    - Diff をそのまま返却する
    """

    logger.info(
        "Chat(workspace) request received: project_id=%s files=%d",
        request.workspace.project_id,
        len(request.workspace.files),
    )

    try:
        diff = workflow.execute_from_workspace(
            workspace=request.workspace,
            root_path=request.root_path,
            requested_mode=request.mode,
            existing_diff=request.existing_diff,
        )
    except Exception as e:
        logger.exception("Chat workflow (workspace) failed")
        raise HTTPException(
            status_code=500,
            detail="Chat processing from workspace failed",
        ) from e

    logger.info(
        "Chat(workspace) completed: diff_files=%d",
        len(diff.files),
    )

    return ChatResponse(diff=diff)


# ============================================================
# Endpoint: Snapshot 起点
# ============================================================
@router.post(
    "/snapshot",
    response_model=ChatResponse,
    summary="Chat from Snapshot",
)
def chat_from_snapshot(
    request: ChatFromSnapshotRequest,
    workflow: Workflow = Depends(get_workflow),
) -> ChatResponse:
    """
    Snapshot 起点の Chat 実行。

    処理内容:
    - Snapshot を受け取る
    - Workflow に処理を委譲する
    - Diff をそのまま返却する

    注意:
    - Snapshot は「生成済み前提」
    - API 層で Snapshot を触らない
    """

    logger.info(
        "Chat(snapshot) request received: project_id=%s files=%d",
        request.snapshot.project_id,
        len(request.snapshot.files),
    )

    try:
        diff = workflow.execute_from_snapshot(
            snapshot=request.snapshot,
            requested_mode=request.mode,
            existing_diff=request.existing_diff,
        )
    except Exception as e:
        logger.exception("Chat workflow (snapshot) failed")
        raise HTTPException(
            status_code=500,
            detail="Chat processing from snapshot failed",
        ) from e

    logger.info(
        "Chat(snapshot) completed: diff_files=%d",
        len(diff.files),
    )

    return ChatResponse(diff=diff)


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - API 層で Snapshot を生成しない
# - WorkspaceIndex / Snapshot の意味解釈をしない
# - Diff を加工しない
#
# api/chat.py は
# 「外界との窓口」であり、
# 「思考の場」ではない。
#

__all__ = [
    "router",
]