# backend/infra/supabase.py
"""
Supabase 接続・永続化インフラ定義

このファイルは、ai-workbench Backend における
「永続化（DB）」との接続を担当する infra 層の実装である。

ここで扱うのはあくまで:
- Supabase への接続
- データの保存・取得
- DB という「外界」との境界処理

重要な前提:
- 判断ロジックを一切含めない
- ドメインモデルを勝手に変形しない
- DB を「便利な状態保存場所」として扱わない

この層は、
domain / core / services を汚さないための
“防波堤”として存在する。
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from supabase import Client, create_client

from backend.domain.workspace_index import WorkspaceIndex
from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# 環境変数キー定義
# ============================================================
#
# 環境変数名をハードコードで散らばらせないため、
# ここで一元管理する。
#
SUPABASE_URL_ENV = "SUPABASE_URL"
SUPABASE_KEY_ENV = "SUPABASE_SERVICE_ROLE_KEY"


# ============================================================
# Supabase Client 生成
# ============================================================
def create_supabase_client() -> Client:
    """
    Supabase Client を生成する。

    注意:
    - Client はシングルトン的に使われる想定
    - この関数内で再生成されてもよいが、
      state（状態）を持たせてはいけない
    """

    url = os.getenv(SUPABASE_URL_ENV)
    key = os.getenv(SUPABASE_KEY_ENV)

    if not url or not key:
        # ここでは例外を握りつぶさない。
        # 起動時に明示的に失敗させる。
        raise RuntimeError(
            "Supabase の接続情報が環境変数に設定されていません"
        )

    return create_client(url, key)


# ============================================================
# Workspace Index 永続化
# ============================================================
def save_workspace_index(
    client: Client,
    workspace_index: WorkspaceIndex,
) -> None:
    """
    Workspace Index を Supabase に保存する。

    保存方針:
    - 最新の Index を「正」とする
    - 過去の Index は履歴用途として保持可能
    - Update / Upsert の詳細は DB 側設計に委ねる

    注意:
    - Workspace Index の構造を改変してはいけない
    - JSON 化は Pydantic に委ねる
    """

    logger.info(
        "Saving workspace index: project_id=%s version=%s",
        workspace_index.project_id,
        workspace_index.index_version,
    )

    data: Dict[str, Any] = {
        "project_id": workspace_index.project_id,
        "index_version": workspace_index.index_version,
        "index_data": workspace_index.model_dump(),
    }

    # テーブル名は Backend_Data_Models.md に準拠
    client.table("workspace_indexes").insert(data).execute()


def get_latest_workspace_index(
    client: Client,
    project_id: str,
) -> Optional[WorkspaceIndex]:
    """
    指定された Project の最新 Workspace Index を取得する。

    戻り値:
    - WorkspaceIndex が存在する場合はそれを返す
    - 存在しない場合は None を返す

    注意:
    - ここで「なければ作る」などの判断をしてはいけない
    - 取得できなかった場合の対応は上位層の責務
    """

    logger.debug(
        "Fetching latest workspace index: project_id=%s",
        project_id,
    )

    response = (
        client.table("workspace_indexes")
        .select("index_data")
        .eq("project_id", project_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    index_data = response.data[0]["index_data"]

    # Pydantic によるバリデーションを必ず通す
    return WorkspaceIndex.model_validate(index_data)


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - infra 層以外から Supabase Client を直接生成してはいけない
# - domain モデルを dict にバラして操作してはいけない
# - DB スキーマ変更時は Documents を先に更新する
#
# このファイルは「薄く」「鈍く」保つ。
# 賢くなり始めたら、それは設計違反の兆候である。
#

__all__ = [
    "create_supabase_client",
    "save_workspace_index",
    "get_latest_workspace_index",
]
