# backend/services/expression/base.py
"""
Expression 基底クラス定義

このファイルは、ai-workbench における
「キャラクター・表現層」の最小単位を定義する。

Expression とは:
- 思考結果（文章・Diff 等）を
- キャラクター固有の「話し方・表現」に変換するための層

重要:
- Expression は「考えない」
- Expression は「判断しない」
- Expression は「生成しない」

あくまで
「与えられたテキストを、どう見せるか」
だけを責務とする。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ExpressionBase(ABC):
    """
    Expression の基底クラス。

    全キャラクター表現は、必ずこのクラスを継承する。

    このクラスが定義するのは:
    - 表現変換のインターフェース
    - キャラクター識別子
    - 表現層としての禁止事項

    このクラスが定義しないもの:
    - 思考ロジック
    - 状態管理
    - 外部 I/O
    """

    # ============================================================
    # 基本メタ情報
    # ============================================================
    @property
    @abstractmethod
    def expression_id(self) -> str:
        """
        Expression を一意に識別する ID。

        例:
        - "nitori"
        - "default"
        - "assistant_formal"

        registry から取得する際のキーになる。
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        表示用のキャラクター名。

        UI やログ等で利用される想定。
        """
        raise NotImplementedError

    # ============================================================
    # 表現変換インターフェース
    # ============================================================
    @abstractmethod
    def format(self, text: str, *, context: dict[str, Any] | None = None) -> str:
        """
        与えられたテキストを、キャラクター表現に変換する。

        引数:
        - text:
            元となるテキスト（思考結果・説明文など）
        - context:
            表現補助用の追加情報（省略可）
            ※ 解釈・判断には使わないこと

        戻り値:
        - 表現変換後の文字列

        注意:
        - text の意味を変えてはいけない
        - 情報を付け足してはいけない
        - 削除・要約は禁止
        """
        raise NotImplementedError

    # ============================================================
    # 禁止事項（設計上の注意）
    # ============================================================
    #
    # 以下のような処理は、このクラスおよび派生クラスでは禁止。
    #
    # - LLM 呼び出し
    # - 思考結果の生成
    # - 条件分岐による判断ロジック
    # - 外部サービスアクセス
    # - 状態の保持・変更
    #
    # Expression は
    # 「表現変換器」であって、
    # 「人格エンジン」ではない。
    #

    def __repr__(self) -> str:
        """
        デバッグ・ログ用の簡易表現。
        """
        return f"<Expression id={self.expression_id} name={self.display_name}>"
