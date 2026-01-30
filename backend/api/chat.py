# backend/api/chat.py
"""
Chat API 定義

このファイルは、ai-workbench Backend における
「チャット系リクエスト」を受け取る API エンドポイントを定義する。

この層の役割:
- 外部（Frontend / Client）からの入力を受け取る
- 入力を最低限バリデーションする
- Workflow に処理を委譲する
- 結果をそのままレスポンスとして返す

やってはいけないこと:
- 判断・推論を行う
- LLM を直接呼び出す
- Snapshot を生成する
- Diff を加工・解釈する

API 層は
「入口と出口」を管理するだけであり、
「中身」を知ってはいけない。
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.deps import get_workflow
from backend.core.workflow import Workflow
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
class ChatRequest(BaseModel):
    """
    /chat エンドポイントのリクエストモデル。

    注意:
    - Snapshot は「完成済みのもの」を受け取る
    - API 層では Snapshot を組み立てない
    """

    snapshot: Snapshot = Field(
        description="判断対象となる Snapshot"
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
    /chat エンドポイントのレスポンスモデル。

    注意:
    - Diff は「提案結果そのもの」
    - API 層では意味解釈しない
    """

    diff: Diff


# ============================================================
# Endpoint
# ============================================================
@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    workflow: Workflow = Depends(get_workflow),
) -> ChatResponse:
    """
    チャット処理エンドポイント。

    処理内容:
    - リクエストを受け取る
    - Workflow に処理を委譲する
    - 結果をそのまま返す

    注意:
    - ここでは try/except で握りつぶさない
    - 想定外例外は FastAPI に任せる
    """

    logger.info(
        "Chat request received: project_id=%s",
        request.snapshot.project_id,
    )

    try:
        diff = workflow.execute(
            snapshot=request.snapshot,
            requested_mode=request.mode,
            existing_diff=request.existing_diff,
        )
    except Exception as e:
        # API 層として最低限の文脈だけを付与する
        logger.exception("Chat workflow execution failed")
        raise HTTPException(
            status_code=500,
            detail="Chat processing failed",
        ) from e

    logger.info(
        "Chat request completed: diff_files=%d",
        len(diff.files),
    )

    return ChatResponse(diff=diff)


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - API 層にロジックを足さない
# - Snapshot / Diff の意味を解釈しない
# - エンドポイントを増やす場合は責務単位で分ける
#
# api/chat.py は
# 「外界との窓口」であり、
# 「思考の場」ではない。
#

__all__ = [
    "router",
]
