Backend Implementation Order

本文書の目的

本文書は ai-workbench Backend を実装する際の 推奨実装順序（連番付き） を定義する。

目的は以下の通り：

実装時に迷わない

途中で設計が破綻しない

AI に実装を委譲しても順序が崩れない

「今どこを作っているか」を常に把握できる


本書は チェックリスト兼ロードマップ として使用する。


---

実装の基本原則

下位層から上位層へ積み上げる

依存関係が少ないものから作る

実行可能性よりも「構造の正しさ」を優先する



---

実装フェーズ全体像

Phase 1: 基盤（Domain / Infra）
Phase 2: 思考中枢（Core / Services）
Phase 3: 外部接続（API / App）
Phase 4: 表現・拡張（Character / Expression）
Phase 5: 動作確認・補助


---

Phase 1：基盤層の実装（最優先）

① domain/message.py

内部メッセージモデル定義

role / content / metadata



---

② domain/character.py

Character データモデル

Expression Layer の前提構造



---

③ domain/workspace_index.py

Workspace Index 構造

ファイル情報・依存関係モデル



---

④ domain/snapshot.py

Snapshot データモデル

一時データとしての扱い定義



---

⑤ domain/diff.py

Diff 構造定義

Full Replace 原則の実装



---

⑥ infra/logger.py

Backend 動作確認用ログ

workflow / dev_engine のトレース



---

⑦ infra/supabase.py

DB 接続抽象

workspace_index 永続化



---

⑧ infra/file_loader.py

VSCode Extension からのファイル取得

Snapshot 生成補助



---

Phase 2：思考・制御層の実装

⑨ services/llm_service.py

LLM API 抽象化

モデル切替・設定管理



---

⑩ services/prompt_builder.py

判断用プロンプト生成

Expression 非依存



---

⑪ core/mode_router.py

dev / casual 分岐

将来モード拡張用の骨組み



---

⑫ core/dev_engine.py

判断ロジック中枢

LLM 呼び出しと Diff 生成



---

⑬ core/workflow.py

Backend 実行フロー統合

Snapshot → Dev Engine → Expression



---

Phase 3：API / App 層の実装

⑭ app/config.py

環境変数

デフォルト設定



---

⑮ app/deps.py

依存性注入

Service / Infra 初期化



---

⑯ api/chat.py

メインチャット API

入力検証・出力整形



---

⑰ api/workspace.py

Workspace Index 取得・更新 API



---

⑱ api/project.py

Project 登録・取得 API



---

⑲ app/main.py

FastAPI 起動点

ルーティング登録



---

Phase 4：キャラクター・表現層

⑳ services/expression/base.py

Expression 基底クラス



---

㉑ services/expression/registry.py

キャラクター登録管理



---

㉒ services/expression/nitori.py

河城にとり表現ルール実装



---

Phase 5：仕上げ・補助

㉓ tests/（最低限）

domain / core の単体テスト



---

㉔ README.md

起動方法

設計文書へのリンク



---

実装時の運用ルール

連番を飛ばして実装しない

各フェーズ完了時に動作確認ログを出す

仕様変更時は Documents を先に更新



---

本書の使い方

実装中は常に本書を開く

今どの番号を実装しているかを明示する

AI に実装を委譲する際は番号を指定する



---

まとめ

この順序に従えば、 Backend は 最短距離かつ安全に完成する。

本書は、 未来の自分と AI のための実装ナビゲーションである。