# backend/domain/message.py
"""
Message ドメインモデル定義

このファイルは、ai-workbench Backend 内部で扱う
「メッセージ」という最小単位の概念モデルを定義する。

重要:
- このファイルは「判断ロジック」を一切持たない
- 表現（キャラクター）にも依存しない
- API / LLM / DB などの外部要素を知らない

あくまで、
「Backend 内部でメッセージとは何か」を定義するためだけの層である。

後から人間・AI のどちらが見ても、
・なぜ存在するのか
・どこまで責務を持つのか
・どこから先はやってはいけないのか
が分かるように記述する。
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


# -----------------------------
# MessageRole
# -----------------------------
# メッセージの発話者種別を表す型。
#
# - "user"      : ユーザーからの入力
# - "assistant" : Backend / AI 側からの出力
#
# これ以外の値を許可しないことで、
# role の意味が実装者ごとにズレることを防ぐ。
MessageRole = Literal["user", "assistant"]


# -----------------------------
# Message
# -----------------------------
class Message(BaseModel):
    """
    Backend 内部で扱うメッセージの最小モデル。

    このクラスは以下の用途で使用される想定である。

    - LLM への入力メッセージ表現
    - Backend 内部フローでのメッセージ受け渡し
    - Expression Layer に渡す前の中立的メッセージ表現

    注意:
    - 判断ロジックは一切含めない
    - キャラクター表現・口調変換は行わない
    - 永続化を前提としない（必要なら別モデルを定義する）
    """

    # 発話者の種別
    role: MessageRole

    # メッセージ本文
    #
    # 空文字を許可する理由:
    # - システムメッセージ
    # - 表現変換前のプレースホルダ
    # - 将来の拡張
    #
    # を妨げないため
    content: str = Field(min_length=0)

    # 付随情報（メタデータ）
    #
    # 使用例:
    # - branch / reply_to などの会話分岐情報
    # - 内部処理用のタグ
    # - 表示制御用の補助情報
    #
    # 注意:
    # - 判断結果そのものを入れてはいけない
    # - ロジック分岐の根拠として使ってはいけない
    metadata: Optional[Dict[str, Any]] = None

    # -----------------------------
    # Pydantic 設定
    # -----------------------------
    model_config = {
        # 定義されていないフィールドの混入を禁止する。
        # これにより、設計文書にない概念が
        # 勝手に追加されることを防ぐ。
        "extra": "forbid",

        # frozen=True によりイミュータブル化する。
        #
        # メッセージは「状態」ではなく「値」として扱うため、
        # 後から内容を書き換える設計は取らない。
        #
        # 変更が必要な場合は、新しい Message を生成する。
        "frozen": True,
    }

    # -----------------------------
    # ヘルパーメソッド
    # -----------------------------
    def with_metadata(self, **updates: Any) -> "Message":
        """
        metadata を更新した新しい Message インスタンスを返す。

        frozen=True のため、既存インスタンスは変更せず、
        常にコピーを生成する。

        使用例:
            msg = Message(role="user", content="hello")
            msg2 = msg.with_metadata(branch="A")

        注意:
        - ここで判断ロジックを入れてはいけない
        - metadata の内容解釈は上位層の責務
        """
        base: Dict[str, Any] = dict(self.metadata or {})
        base.update(updates)
        return Message(
            role=self.role,
            content=self.content,
            metadata=base,
        )


# -----------------------------
# export 制御
# -----------------------------
# 明示的に公開するシンボルを限定することで、
# このモジュールの責務範囲を固定する。
__all__ = [
    "MessageRole",
    "Message",
]
