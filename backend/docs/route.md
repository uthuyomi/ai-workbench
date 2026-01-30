Backend Folder Structure (Complete) with Character System

本文書の位置づけ

本文書は ai-workbench Backend のフォルダ構成を「完全版」として定義する。

Backend_Folder_Structure.md を拡張・詳細化した文書である

すべてのディレクトリ・主要ファイルについて

何をするか

何をしないか

将来どう拡張されるか を明示する



特に本書では、 キャラクター（Expression Layer）を将来いくつでも追加できる構造を Backend 側でどのように扱うかを正式に定義する。


---

設計の大前提

判断ロジックとキャラクターは完全に分離する

キャラクターは「人格」ではなく「表現ルール集合」である

Backend はキャラクターを 選択・適用 するが 思考させない

新キャラクター追加時に core / api を修正しない



---

Backend ルート構成（完全版）

backend/
├─ app/
│   ├─ main.py
│   ├─ config.py
│   └─ deps.py
│
├─ api/
│   ├─ chat.py
│   ├─ workspace.py
│   └─ project.py
│
├─ core/
│   ├─ dev_engine.py
│   ├─ workflow.py
│   └─ mode_router.py
│
├─ domain/
│   ├─ workspace_index.py
│   ├─ snapshot.py
│   ├─ diff.py
│   ├─ message.py
│   └─ character.py
│
├─ services/
│   ├─ llm_service.py
│   ├─ expression/
│   │   ├─ base.py
│   │   ├─ registry.py
│   │   ├─ nitori.py
│   │   └─ __init__.py
│   └─ prompt_builder.py
│
├─ infra/
│   ├─ supabase.py
│   ├─ logger.py
│   └─ file_loader.py
│
├─ tests/
│   ├─ core/
│   ├─ services/
│   └─ api/
│
└─ README.md


---

app/（アプリケーション層）

app/main.py

FastAPI アプリケーションの起動点

ルーティング登録

ミドルウェア設定


禁止事項

ビジネスロジックの記述

キャラクター処理



---

app/config.py

環境変数の読み込み

Backend 全体設定

デフォルトキャラクター ID などの定義



---

app/deps.py

DI（依存性注入）定義

Service / Infra のインスタンス生成



---

api/（API 層）

api/chat.py

チャット入力の受付

mode（dev / casual）と character_id の受理

workflow 呼び出し


ここでやること

入力検証

出力整形


やらないこと

判断

キャラクター表現適用



---

api/workspace.py

Workspace Index の取得・更新 API



---

api/project.py

Project 情報の取得

Project 単位の検証



---

core/（判断・制御層）

core/mode_router.py

mode に応じた処理ルート選択

dev / casual / 将来拡張用モードの分岐



---

core/workflow.py

Backend の実行フロー定義

Snapshot / Dev Engine / Expression 適用の順序制御



---

core/dev_engine.py

唯一の判断ロジック中枢

LLM 呼び出し統括

Diff 生成


禁止事項

キャラクター表現

文体制御



---

domain/（概念モデル層）

domain/message.py

内部メッセージ構造定義

role / content / metadata



---

domain/character.py

Character 定義のデータモデル


Character
- id
- display_name
- description
- expression_profile
- forbidden_rules

※ 思考ロジックは一切含まない


---

services/（機能提供層）

services/llm_service.py

LLM API 抽象化

モデル切替・設定管理



---

services/prompt_builder.py

判断用プロンプト構築

Expression Layer とは独立



---

services/expression/（キャラクターシステム）

base.py

Expression 基底クラス

入力：判断済みメッセージ

出力：表現変換後メッセージ



---

registry.py

利用可能キャラクターの登録・取得

character_id → Expression 実装の解決



---

nitori.py（例：東方・にとり）

にとり専用の表現ルール

文構造の並び替え

口調・強調・比喩の適用


禁止事項

判断結果の変更

Diff の改変



---

キャラクター追加手順（Backend）

1. services/expression/ に新ファイルを追加


2. ExpressionBase を継承


3. registry.py に登録


4. domain/character.py に定義を追加



core / api の修正は不要。


---

infra/（インフラ層）

infra/supabase.py

DB 接続

永続化処理



---

infra/logger.py

Backend 動作確認用ログ

workflow / dev_engine のトレース



---

infra/file_loader.py

Workspace ファイル取得

Snapshot 用の実ファイルロード



---

tests/

層ごとにテストを分離

キャラクター表現は単体テスト対象



---

README.md

Backend 起動方法

簡易構成説明

詳細設計は Documents を正とする



---

本構成の特徴（まとめ）

Backend の思考は常に 1 系統

キャラクターは完全に差し替え可能

キャラ追加で設計が壊れない

touhou-talk 系キャラ追加と親和性が高い


このフォルダ構成は、 長期運用とキャラクター拡張を前提とした最終形である。