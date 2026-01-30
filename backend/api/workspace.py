# backend/api/workspace.py
"""
Workspace API 定義

このファイルは、ai-workbench Backend における
「Workspace（作業空間）」に関する API エンドポイントを定義する。

この層の役割:
- Workspace の読み取り・登録・更新の入口を提供する
- infra 層（将来実装）を呼び出す起点になる
- 結果をそのままレスポンスとして返す

やってはいけないこと:
- Snapshot を組み立てる
- Diff / Workflow / LLM を呼び出す
- ファイルの意味解釈を行う
- 判断・思考ロジックを書く

Workspace API は
「現実（ファイル構造）を返すだけ」の層であり、
「考える層」ではない。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.deps import get_supabase_client
from backend.domain.workspace_index import WorkspaceIndex
from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# Router
# ============================================================
router = APIRouter(
    prefix="/workspace",
    tags=["workspace"],
)


# ============================================================
# Request / Response Models
# ============================================================
class WorkspaceScanRequest(BaseModel):
    """
    Workspace スキャン要求。

    注意:
    - path は「サーバー側で許可された範囲」である前提
    - API 層ではパス妥当性の深い検証は行わない
    """

    project_id: str = Field(description="対象プロジェクトID")
    path: str = Field(description="スキャン対象のルートパス")


class WorkspaceResponse(BaseModel):
    """
    Workspace API の共通レスポンス。

    注意:
    - WorkspaceIndex は「現状の写像」
    - 解釈・加工はしない
    """

    workspace: WorkspaceIndex


# ============================================================
# Endpoints
# ============================================================
@router.post(
    "/scan",
    response_model=WorkspaceResponse,
)
def scan_workspace(
    request: WorkspaceScanRequest,
    supabase=Depends(get_supabase_client),
) -> WorkspaceResponse:
    """
    Workspace をスキャンして WorkspaceIndex を生成する。

    現フェーズでは未実装。

    理由:
    - create.md にて WorkspaceScanner は未定義
    - infra 層の責務が確定していないため

    注意:
    - 本エンドポイントは「存在のみ保証」する
    - 実処理は Phase 以降で実装する
    """

    logger.info(
        "Workspace scan requested (not implemented yet): project_id=%s path=%s",
        request.project_id,
        request.path,
    )

    raise HTTPException(
        status_code=501,
        detail="Workspace scan is not implemented yet",
    )


@router.get(
    "/{project_id}",
    response_model=WorkspaceResponse,
)
def get_workspace(
    project_id: str,
    supabase=Depends(get_supabase_client),
) -> WorkspaceResponse:
    """
    既存 WorkspaceIndex を取得する。

    注意:
    - 保存形式・取得方法は infra 層に委ねる
    - API 層では加工しない
    """

    logger.info("Workspace fetch requested: project_id=%s", project_id)

    try:
        # NOTE:
        # 現時点では Supabase からの取得処理は未実装。
        # infra/supabase.py 側で定義されるまで 501 を返す。
        raise NotImplementedError("Workspace fetch is not implemented yet")
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Workspace fetch failed")
        raise HTTPException(
            status_code=500,
            detail="Workspace fetch failed",
        ) from e


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - Workspace API に Snapshot / Diff を混ぜない
# - スキャン結果の意味解釈をしない
# - 未実装機能は 501 で明示的に落とす
#
# api/workspace.py は
# 「現実の構造を返す窓口」であり、
# 「思考の入口」ではない。
#

__all__ = [
    "router",
]
