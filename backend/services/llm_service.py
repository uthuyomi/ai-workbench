# backend/services/llm_service.py
"""
LLM Service 定義

このファイルは、ai-workbench Backend における
「LLM（大規模言語モデル）との唯一の接点」を定義する。

この層の役割は明確である。

やること:
- 外部 LLM API を呼び出す
- モデル設定・パラメータを管理する
- 「問い合わせ → 応答」を抽象化する

やってはいけないこと:
- 判断ロジックを持つ
- プロンプトの内容を組み立てる
- 応答結果を解釈・加工する
- Diff / Snapshot / Mode を知る

この層は、
「賢くなるほど危険」な場所であるため、
あえて **薄く・鈍く** 作る。
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from openai import OpenAI

from backend.infra.logger import get_logger


# ============================================================
# Logger
# ============================================================
logger = get_logger(__name__)


# ============================================================
# LLM 設定デフォルト
# ============================================================
#
# - あくまで「初期値」
# - 実運用では環境変数・上位層から上書きされる想定
#
DEFAULT_MODEL = "gpt-4.1"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 2048


# ============================================================
# LLM Service
# ============================================================
class LLMService:
    """
    LLM 呼び出しを担当するサービスクラス。

    注意:
    - このクラスは状態を持たない
    - 会話履歴を保持しない
    - セッション管理を行わない

    「毎回同じ入力には、同じ問い合わせを投げる」
    それ以上の責務を与えてはいけない。
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> None:
        """
        LLMService を初期化する。

        引数:
        - client       : OpenAI クライアント（DI 用）
        - model        : 使用するモデル名
        - temperature  : 応答の揺らぎ
        - max_tokens   : 最大トークン数
        """

        # 外部依存はここで閉じる
        self._client = client or OpenAI()

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens

        logger.info(
            "LLMService initialized: model=%s temperature=%s max_tokens=%s",
            model,
            temperature,
            max_tokens,
        )

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        LLM に問い合わせを行い、応答テキストを返す。

        引数:
        - system_prompt : system ロール用プロンプト
        - user_prompt   : user ロール用プロンプト
        - extra_params  : モデル固有の追加パラメータ

        戻り値:
        - LLM の生テキスト応答

        注意:
        - 応答の解釈は行わない
        - JSON である保証もしない
        - 失敗時は例外をそのまま上位に投げる
        """

        logger.debug("Sending request to LLM")

        params: Dict[str, Any] = {
            "model": self._model,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        # 追加パラメータがある場合のみマージ
        if extra_params:
            params.update(extra_params)

        response = self._client.chat.completions.create(**params)

        # この層では「最初のメッセージを返す」以上のことはしない
        content = response.choices[0].message.content

        logger.debug("Received response from LLM")

        return content


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - services 層以外で OpenAI Client を直接触らない
# - LLMService にロジックを足さない
# - 「便利だから」という理由で post-processing を入れない
#
# LLMService は「外部脳との電話機」であり、
# 思考そのものではない。
#

__all__ = [
    "LLMService",
]
