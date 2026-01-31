# backend/api/workspace.py
"""
Workspace API 定義

このファイルは、ai-workbench Backend における
「Workspace（作業空間）」に関する API エンドポイントを定義する。

この層の役割:
- Workspace の読み取り・登録・更新の入口を提供する
- infra 層（WorkspaceScanner 等）を呼び出す起点になる
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
from backend.infra.workspace_scanner import WorkspaceScanner
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
# Dependencies
# ============================================================
def get_workspace_scanner() -> WorkspaceScanner:
    """
    WorkspaceScanner を生成する Dependency。

    注意:
    - Scanner は状態を持たないため、毎回生成して問題ない
    - API 層は「生成と呼び出し」までに責務を限定する
    """
    return WorkspaceScanner()


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
    scanner: WorkspaceScanner = Depends(get_workspace_scanner),
) -> WorkspaceResponse:
    """
    Workspace をスキャンして WorkspaceIndex を生成する。

    処理内容:
    - 指定された path を WorkspaceScanner に渡す
    - 実ファイル構造を走査する
    - WorkspaceIndex をそのまま返す

    注意:
    - Snapshot 生成は行わない
    - Diff 計算は行わない
    - 保存処理は行わない
    """

    logger.info(
        "Workspace scan requested: project_id=%s path=%s",
        request.project_id,
        request.path,
    )

    try:
        workspace = scanner.scan(
            project_id=request.project_id,
            root_path=request.path,
        )
    except Exception as e:
        # infra 層の例外は API 層で HTTP エラーに変換する
        logger.exception("Workspace scan failed")
        raise HTTPException(
            status_code=500,
            detail="Workspace scan failed",
        ) from e

    logger.info(
        "Workspace scan completed: project_id=%s files=%d",
        request.project_id,
        len(workspace.files),
    )

    return WorkspaceResponse(workspace=workspace)


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
        # 現時点では WorkspaceIndex の永続化は未実装。
        # infra/supabase.py 側で取得処理が定義されるまでは 501 を返す。
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
# - Workspace API に Snapshot / Diff / Workflow を混ぜない
# - スキャン結果の意味解釈をしない
# - IO は infra 層に委ね、API 層は制御に徹する
#
# api/workspace.py は
# 「現実の構造を返す窓口」であり、
# 「思考の入口」ではない。
#

__all__ = [
    "router",
]