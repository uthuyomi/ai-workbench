# backend/infra/logger.py
"""
Backend Logger 定義

このファイルは、ai-workbench Backend における
「ログ出力」の共通基盤を定義する。

ここでいう Logger の役割は、
- デバッグのためだけの print 代替
- なんとなく状況を眺めるためのログ

ではない。

目的は以下に集約される。

- Backend の実行フローを追跡可能にする
- 判断が「どの段階まで進んだか」を説明できるようにする
- 将来、設計違反・逸脱が起きたときに原因を辿れるようにする

重要な前提:
- Logger は判断しない
- Logger は状態を持たない
- Logger は実行フローを変えてはいけない

ログは「観測」であり、「介入」ではない。
"""

from __future__ import annotations

import logging
from typing import Optional


# ============================================================
# ログレベル方針
# ============================================================
#
# DEBUG   : 内部フロー追跡・開発時の詳細情報
# INFO    : 正常系の重要イベント（API受信、モード分岐など）
# WARNING : 想定外だが致命的ではない状態
# ERROR   : 処理継続不能なエラー
#
# Backend の思想として、
# INFO / DEBUG を多めに出し、
# 「後から読んで流れが分かる」ことを重視する。
#

DEFAULT_LOG_LEVEL = logging.INFO


# ============================================================
# Logger 生成関数
# ============================================================
def get_logger(
    name: str,
    level: Optional[int] = None,
) -> logging.Logger:
    """
    Backend 用の Logger を取得する。

    この関数は、
    - 各モジュールで logger = get_logger(__name__) の形で使用する
    - Logger の設定を一元化する

    ことを目的とする。

    注意:
    - ロガーごとに独自設定をしてはいけない
    - handler を勝手に追加してはいけない
    - 出力形式をモジュール側で変更してはいけない
    """

    logger = logging.getLogger(name)

    # ログレベル設定
    logger.setLevel(level or DEFAULT_LOG_LEVEL)

    # すでに handler が設定されている場合は追加しない
    #
    # FastAPI / Uvicorn 環境では、
    # 二重に handler を追加するとログが重複するため
    if not logger.handlers:
        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            fmt=(
                "[%(asctime)s] "
                "[%(levelname)s] "
                "[%(name)s] "
                "%(message)s"
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # 親ロガーへの伝播を無効化
    #
    # → ログが二重に出力されるのを防ぐ
    logger.propagate = False

    return logger


# ============================================================
# 使用上の注意（設計固定）
# ============================================================
#
# - Logger は infra 層にのみ定義する
# - domain 層で直接 import して使ってはいけない
# - core / api / services 層から参照されることを想定
#
# ログに出してよいもの:
# - 処理の開始 / 終了
# - mode 分岐
# - Snapshot 生成有無
# - Diff 生成完了
#
# ログに出してはいけないもの:
# - ユーザーの機密情報
# - API キー・トークン
# - LLM の生レスポンス全文
#
# Logger は「説明可能性の補助線」であり、
# 主役はあくまで設計と実装である。
#

__all__ = [
    "get_logger",
]
