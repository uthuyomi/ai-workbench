"""
App Config 定義（環境変数・デフォルト設定）

このファイルは、ai-workbench Backend における
「環境変数」と「デフォルト設定」を一元管理する。

この層の役割:
- 環境変数キー名の定義（散らばらせない）
- デフォルト値の定義（統一する）
- 実行時に Settings を構築して返す

やってはいけないこと:
- Supabase や LLM のクライアント生成（deps の責務）
- 例外の握りつぶし
- ここでの判断ロジック（mode 分岐など）

このファイルは「設定の唯一の出典」であり、
他の層が勝手に env を直接読むのを防ぐための防波堤。
"""

from __future__ import annotations

import os
from dataclasses import dataclass

# ============================================================
# .env 読み込み（起動時に一度だけ）
# ============================================================
#
# 方針:
# - .env を「ここでだけ」読み込む
# - 他の層で dotenv を触らせない
# - os.getenv を使う既存設計はそのまま維持
#
# 注意:
# - .env が存在しなくても例外にはしない
#   （本番では OS 環境変数を使う前提のため）
#
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # python-dotenv 未導入 or .env 不在でも黙って進む
    pass


# ============================================================
# 環境変数キー（ここに集約）
# ============================================================
#
# 重要:
# - infra/supabase.py 等も「文字列直書き」を避け、
#   可能な限りこの定義を参照するのが理想だが、
#   既存実装との整合は段階的に行う前提。
#
ENV_LOG_LEVEL = "LOG_LEVEL"

ENV_SUPABASE_URL = "SUPABASE_URL"
ENV_SUPABASE_SERVICE_ROLE_KEY = "SUPABASE_SERVICE_ROLE_KEY"

ENV_OPENAI_API_KEY = "OPENAI_API_KEY"  # OpenAI SDK が参照するための代表キー

ENV_LLM_MODEL = "LLM_MODEL"
ENV_LLM_TEMPERATURE = "LLM_TEMPERATURE"
ENV_LLM_MAX_TOKENS = "LLM_MAX_TOKENS"

ENV_APP_ENV = "APP_ENV"  # "local" / "prod" 等（厳密な運用は main/app 側で扱う）


# ============================================================
# デフォルト値（ここに集約）
# ============================================================
DEFAULT_LOG_LEVEL = "INFO"

# LLM の初期値（上位から上書きされる前提）
DEFAULT_LLM_MODEL = "gpt-4.1"
DEFAULT_LLM_TEMPERATURE = 0.2
DEFAULT_LLM_MAX_TOKENS = 2048

DEFAULT_APP_ENV = "local"


# ============================================================
# Settings（読み取り専用の設定オブジェクト）
# ============================================================
@dataclass(frozen=True)
class Settings:
    """
    Backend 設定の不変オブジェクト。

    注意:
    - これは「設定値の入れ物」であり、ロジックを持たせない
    - 生成後は不変（frozen）として扱い、差し替えは再生成で行う
    """

    # 実行環境（local / prod 等）
    app_env: str

    # ログレベル（"DEBUG" / "INFO" / ...）
    log_level: str

    # Supabase 接続情報
    supabase_url: str
    supabase_service_role_key: str

    # LLM 設定
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int

    # OpenAI API キー（SDK が環境変数から読むことが多いが、確認用として保持）
    openai_api_key: str

    # --------------------------------------------------------
    # Factory
    # --------------------------------------------------------
    @staticmethod
    def from_env() -> "Settings":
        """
        環境変数から Settings を構築する。

        方針:
        - 必須値が欠けている場合は明示的に失敗させる
        - 型変換に失敗する場合も明示的に失敗させる

        注意:
        - ここで「fallback で黙って進む」ことはしない
          （後で原因追跡が困難になるため）
        """

        app_env = os.getenv(ENV_APP_ENV, DEFAULT_APP_ENV)
        log_level = os.getenv(ENV_LOG_LEVEL, DEFAULT_LOG_LEVEL)

        supabase_url = os.getenv(ENV_SUPABASE_URL)
        supabase_key = os.getenv(ENV_SUPABASE_SERVICE_ROLE_KEY)

        openai_api_key = os.getenv(ENV_OPENAI_API_KEY)

        if not supabase_url:
            raise RuntimeError(f"{ENV_SUPABASE_URL} が設定されていません")
        if not supabase_key:
            raise RuntimeError(f"{ENV_SUPABASE_SERVICE_ROLE_KEY} が設定されていません")
        if not openai_api_key:
            raise RuntimeError(f"{ENV_OPENAI_API_KEY} が設定されていません")

        llm_model = os.getenv(ENV_LLM_MODEL, DEFAULT_LLM_MODEL)

        # 数値系は「型として正しいこと」を強制する
        llm_temperature = _get_float_env(
            ENV_LLM_TEMPERATURE,
            DEFAULT_LLM_TEMPERATURE,
        )
        llm_max_tokens = _get_int_env(
            ENV_LLM_MAX_TOKENS,
            DEFAULT_LLM_MAX_TOKENS,
        )

        return Settings(
            app_env=app_env,
            log_level=log_level,
            supabase_url=supabase_url,
            supabase_service_role_key=supabase_key,
            llm_model=llm_model,
            llm_temperature=llm_temperature,
            llm_max_tokens=llm_max_tokens,
            openai_api_key=openai_api_key,
        )


# ============================================================
# 内部ユーティリティ（設定読み取り補助）
# ============================================================
def _get_int_env(key: str, default: int) -> int:
    """
    環境変数を int として読み取る。

    注意:
    - 失敗時に黙って default に戻すのではなく、例外を投げる
      （設定ミスを早期に露出させる）
    """
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as e:
        raise RuntimeError(
            f"{key} は int である必要があります: value={raw!r}"
        ) from e


def _get_float_env(key: str, default: float) -> float:
    """
    環境変数を float として読み取る。

    注意:
    - 失敗時に黙って default に戻すのではなく、例外を投げる
    """
    raw = os.getenv(key)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError as e:
        raise RuntimeError(
            f"{key} は float である必要があります: value={raw!r}"
        ) from e


__all__ = [
    "Settings",
    # env keys
    "ENV_LOG_LEVEL",
    "ENV_SUPABASE_URL",
    "ENV_SUPABASE_SERVICE_ROLE_KEY",
    "ENV_OPENAI_API_KEY",
    "ENV_LLM_MODEL",
    "ENV_LLM_TEMPERATURE",
    "ENV_LLM_MAX_TOKENS",
    "ENV_APP_ENV",
    # defaults
    "DEFAULT_LOG_LEVEL",
    "DEFAULT_LLM_MODEL",
    "DEFAULT_LLM_TEMPERATURE",
    "DEFAULT_LLM_MAX_TOKENS",
    "DEFAULT_APP_ENV",
]