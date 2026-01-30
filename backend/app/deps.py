# backend/app/deps.py
"""
Dependency Provider 定義（DI 集約点）

このファイルは、ai-workbench Backend における
「依存性注入（Dependency Injection）」を一元管理する。

この層の役割:
- 各サービス・エンジン・ワークフローの生成を集約する
- FastAPI などのフレームワークから利用される依存関数を提供する
- 「どこで何が生成されるか」を一目で追えるようにする

やってはいけないこと:
- ビジネスロジックを実装する
- 判断・分岐を行う
- ファイル操作・DB操作を行う
- グローバル状態を隠蔽する

deps.py は
「組み立てる場所」であって
「考える場所」ではない。
"""

from __future__ import annotations

from functools import lru_cache

from backend.app.config import Settings
from backend.core.mode_router import ModeRouter
from backend.core.dev_engine import DevEngine
from backend.core.workflow import Workflow
from backend.services.llm_service import LLMService
from backend.services.prompt_builder import PromptBuilder
from backend.infra.logger import get_logger
from backend.infra.supabase import create_supabase_client


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# Settings
# ============================================================
@lru_cache
def get_settings() -> Settings:
    """
    Settings を取得する。

    方針:
    - 起動中は同一インスタンスを使い回す
    - 設定変更が必要な場合はプロセス再起動を前提とする
    """
    logger.info("Loading application settings")
    return Settings.from_env()


# ============================================================
# Infra Layer
# ============================================================
@lru_cache
def get_supabase_client():
    """
    Supabase Client を取得する。

    注意:
    - infra/supabase.py が唯一の生成責務を持つ
    - この関数は「参照点」として存在する
    """
    logger.info("Creating Supabase client")
    return create_supabase_client()


# ============================================================
# Services Layer
# ============================================================
def get_llm_service() -> LLMService:
    """
    LLMService を生成する。

    注意:
    - Settings からモデル設定を受け取る
    - LLMService 自体は状態を持たないためキャッシュしない
    """
    settings = get_settings()

    return LLMService(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )


def get_prompt_builder() -> PromptBuilder:
    """
    PromptBuilder を生成する。

    注意:
    - 状態を持たないため、毎回新規生成で問題ない
    """
    return PromptBuilder()


# ============================================================
# Core Layer
# ============================================================
def get_mode_router() -> ModeRouter:
    """
    ModeRouter を生成する。

    注意:
    - 状態を持たないためキャッシュ不要
    """
    return ModeRouter()


def get_dev_engine() -> DevEngine:
    """
    DevEngine を生成する。

    注意:
    - 依存するサービスはすべてここで注入する
    - DevEngine 自身は状態を持たない
    """
    return DevEngine(
        llm_service=get_llm_service(),
        prompt_builder=get_prompt_builder(),
    )


def get_workflow() -> Workflow:
    """
    Workflow を生成する。

    注意:
    - Workflow は Backend 実行フローの唯一の入口
    - ここで組み立てた構成が「正」となる
    """
    return Workflow(
        mode_router=get_mode_router(),
        dev_engine=get_dev_engine(),
    )


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - deps.py を「便利 import ハブ」にしない
# - 新しい依存が増えた場合は、必ずこのファイルに追加する
# - 各層が勝手にインスタンス生成を始めたら設計崩壊
#
# deps.py は
# 「組み立て図」であり、
# 「処理の中身」ではない。
#

__all__ = [
    "get_settings",
    "get_supabase_client",
    "get_llm_service",
    "get_prompt_builder",
    "get_mode_router",
    "get_dev_engine",
    "get_workflow",
]
