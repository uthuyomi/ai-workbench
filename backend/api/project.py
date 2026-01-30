# backend/api/project.py
"""
Project API 定義

このファイルは、ai-workbench Backend における
「Project（プロジェクト）」単位の管理 API を定義する。

Project とは:
- Workspace / Snapshot / Chat を束ねる論理的な単位
- メタ情報（名前・説明・作成日時など）を持つ存在

この層の役割:
- Project の作成・取得・一覧取得の入口を提供する
- 永続化は infra 層（Supabase）に委ねる
- API 境界として最低限の検証のみ行う

やってはいけないこと:
- Workspace / Snapshot / Diff を扱う
- 思考・判断・生成を行う
- Project の意味解釈を行う

Project API は
「箱を管理するだけ」であり、
「中身を触る場所」ではない。
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.deps import get_supabase_client
from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# Router
# ============================================================
router = APIRouter(
    prefix="/project",
    tags=["project"],
)


# ============================================================
# Request / Response Models
# ============================================================
class ProjectCreateRequest(BaseModel):
    """
    Project 作成リクエスト。

    注意:
    - API 層では ID を生成しない
    - 永続化層（DB）が ID を決める前提
    """

    name: str = Field(
        description="プロジェクト名",
        min_length=1,
    )
    description: Optional[str] = Field(
        default=None,
        description="プロジェクト説明",
    )


class ProjectResponse(BaseModel):
    """
    Project 単体レスポンス。

    注意:
    - Workspace / Snapshot 情報は含めない
    """

    project_id: str
    name: str
    description: Optional[str]


class ProjectListResponse(BaseModel):
    """
    Project 一覧レスポンス。
    """

    projects: List[ProjectResponse]


# ============================================================
# Endpoints
# ============================================================
@router.post(
    "",
    response_model=ProjectResponse,
)
def create_project(
    request: ProjectCreateRequest,
    supabase=Depends(get_supabase_client),
) -> ProjectResponse:
    """
    Project を新規作成する。

    注意:
    - 実際の INSERT 処理は infra/supabase 側に委ねる
    - ここでは「作成要求」を受けるだけ
    """

    logger.info("Project create requested: name=%s", request.name)

    try:
        # NOTE:
        # 現段階では Supabase 側の Project テーブル定義が
        # 固まっていないため仮実装。
        # infra/supabase.py に Project 用 API が追加され次第、
        # ここは差し替える。
        raise NotImplementedError("Project creation is not implemented yet")
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Project creation failed")
        raise HTTPException(
            status_code=500,
            detail="Project creation failed",
        ) from e


@router.get(
    "",
    response_model=ProjectListResponse,
)
def list_projects(
    supabase=Depends(get_supabase_client),
) -> ProjectListResponse:
    """
    Project 一覧を取得する。

    注意:
    - 並び順・ページングは後続フェーズで検討
    """

    logger.info("Project list requested")

    try:
        # NOTE:
        # Supabase 実装待ち
        raise NotImplementedError("Project listing is not implemented yet")
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Project listing failed")
        raise HTTPException(
            status_code=500,
            detail="Project listing failed",
        ) from e


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: str,
    supabase=Depends(get_supabase_client),
) -> ProjectResponse:
    """
    Project 単体を取得する。

    注意:
    - 存在確認のみ
    - 関連データは返さない
    """

    logger.info("Project fetch requested: project_id=%s", project_id)

    try:
        # NOTE:
        # Supabase 実装待ち
        raise NotImplementedError("Project fetch is not implemented yet")
    except NotImplementedError as e:
        raise HTTPException(
            status_code=501,
            detail=str(e),
        )
    except Exception as e:
        logger.exception("Project fetch failed")
        raise HTTPException(
            status_code=500,
            detail="Project fetch failed",
        ) from e


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - Project API に Workspace / Snapshot を混ぜない
# - Project を「便利なまとめ役」にしない
# - メタ情報以上の責務を持たせない
#
# api/project.py は
# 「箱の管理」だけを行い、
# 「中身」には触れない。
#

__all__ = [
    "router",
]
