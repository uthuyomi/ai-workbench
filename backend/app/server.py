# backend/app/server.py
"""
Application Entry Point

このファイルは、ai-workbench Backend の
「アプリケーション起動点（エントリポイント）」である。

この層の役割:
- FastAPI アプリケーションを生成する
- Router を登録する
- 設定・ログ初期化を行う
- ASGI サーバーから呼ばれる入口となる

やってはいけないこと:
- ビジネスロジックを書く
- Workflow / Engine を直接呼び出す
- infra / domain の中身に触る
- 設定値を勝手に書き換える

main.py は
「配線図の最終地点」であり、
「処理の実装場所」ではない。
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.app.config import Settings
from backend.app.deps import get_settings
from backend.api.chat import router as chat_router
from backend.api.workspace import router as workspace_router
from backend.api.project import router as project_router
from backend.api.snapshot import router as snapshot_router
from backend.infra.logger import get_logger
from dotenv import load_dotenv
load_dotenv()


# ============================================================
# Application Factory
# ============================================================
def create_app() -> FastAPI:
    """
    FastAPI アプリケーションを生成する。

    方針:
    - グローバルに app を生成しない
    - create_app() 経由で明示的に生成する
    - テスト・本番・将来の複数インスタンスを想定
    """

    # --------------------------------------------------------
    # Settings / Logging
    # --------------------------------------------------------
    settings: Settings = get_settings()

    logger = get_logger(__name__)
    logger.info("Starting ai-workbench backend")
    logger.info("App environment: %s", settings.app_env)

    # --------------------------------------------------------
    # FastAPI App
    # --------------------------------------------------------
    app = FastAPI(
        title="ai-workbench Backend",
        description="Backend API for ai-workbench",
        version="0.1.0",
    )

    # --------------------------------------------------------
    # Routers
    # --------------------------------------------------------
    #
    # ルータはここで一元登録する。
    # 各 API ファイルが勝手に app を触らない設計。
    #
    app.include_router(chat_router)
    app.include_router(workspace_router)
    app.include_router(project_router)
    app.include_router(snapshot_router)

    # --------------------------------------------------------
    # Health Check
    # --------------------------------------------------------
    @app.get("/health")
    def health_check() -> dict:
        """
        ヘルスチェック用エンドポイント。

        注意:
        - 依存確認は行わない
        - 軽量で即時応答できることを優先
        """
        return {
            "status": "ok",
            "env": settings.app_env,
        }

    logger.info("Application setup completed")

    return app


# ============================================================
# ASGI Entry Point
# ============================================================
#
# Uvicorn / Gunicorn などからは
# `backend.app.main:app` として参照される。
#
app = create_app()


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - main.py にロジックを足さない
# - Router 登録以外の処理を増やさない
# - 起動時副作用を最小限に保つ
#
# main.py は
# 「配線して起動するだけ」の存在であり、
# 「何かを決める場所」ではない。
#
