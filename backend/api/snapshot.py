# backend/api/snapshot.py
"""
Snapshot API Route

このファイルは、ai-workbench Backend における
「Snapshot 生成専用 API エンドポイント」を定義する。

役割:
- WorkspaceIndex を受け取る
- SnapshotBuilder を使って Snapshot を生成する
- Snapshot をそのまま返却する

重要:
- 判断ロジックを持たない
- Diff / Workflow / LLM を呼ばない
- Snapshot の中身を解釈しない

この API は
「WorkspaceIndex → Snapshot」変換の
唯一の HTTP 入口である。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.app.deps import get_snapshot_builder
from backend.domain.workspace_index import WorkspaceIndex
from backend.domain.snapshot import Snapshot
from backend.infra.snapshot_builder import SnapshotBuilder


# ============================================================
# Router
# ============================================================
router = APIRouter(
    prefix="/api/snapshot",
    tags=["snapshot"],
)


# ============================================================
# Request Model
# ============================================================
class SnapshotBuildRequest(BaseModel):
    """
    SnapshotBuildRequest

    Snapshot 生成に必要な最小入力。

    注意:
    - WorkspaceIndex は「すでに生成済み」であることを前提とする
    - root_path は実ファイルが存在するディレクトリ
    """

    # WorkspaceIndex（ファイル構造メタ情報）
    workspace: WorkspaceIndex

    # Workspace の実体が存在するルートディレクトリ
    root_path: str = Field(min_length=1)

    # Snapshot に含める対象パス（省略可）
    #
    # None の場合:
    # - WorkspaceIndex に含まれる全ファイルを対象にする
    target_paths: list[str] | None = None

    model_config = {
        "extra": "forbid",
    }


# ============================================================
# Endpoint
# ============================================================
@router.post(
    "/build",
    response_model=Snapshot,
    summary="Build Snapshot from WorkspaceIndex",
)
def build_snapshot(
    req: SnapshotBuildRequest,
    snapshot_builder: SnapshotBuilder = Depends(get_snapshot_builder),
) -> Snapshot:
    """
    Snapshot を生成する。

    処理内容:
    1. SnapshotBuilder に WorkspaceIndex を渡す
    2. 実ファイルを読み取り Snapshot を構築
    3. Snapshot をそのまま返却

    注意:
    - この関数は「判断」しない
    - 読めないファイルは SnapshotBuilder 側でスキップされる
    - 失敗時は例外をそのまま FastAPI に委ねる
    """

    snapshot = snapshot_builder.build(
        workspace=req.workspace,
        root_path=req.root_path,
        target_paths=req.target_paths,
    )

    return snapshot


# ============================================================
# export 制御
# ============================================================
__all__ = [
    "router",
]