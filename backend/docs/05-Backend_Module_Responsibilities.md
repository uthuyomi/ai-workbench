Backend Module Responsibilities

本文書の位置づけ

本文書は ai-workbench Backend における各ディレクトリおよび主要ファイルの責務を定義する。

Backend_Folder_Structure.md にて定義された物理構造に対し、 本文書は「論理的な責務境界」を与える役割を持つ。

本文書の目的は、

実装時にどこへ何を書くべきかを明確にする

責務越境やロジック混入を防止する

AI 実装時の誤解を最小化する


ことである。


---

責務分離の原則

Backend におけるすべてのモジュールは、以下の原則に従う。

1ファイル1責務を基本とする

判断ロジックと補助ロジックを混在させない

上位層から下位層への一方向依存を守る


この原則に反する実装は、機能的に正しく動作していても不正とみなす。


---

app 層の責務

app/main.py

FastAPI アプリケーションの起動点とする

ルーティング登録を行う

ミドルウェア設定を行う


以下の処理は禁止する。

判断ロジックの記述

ドメインロジックの実装



---

app/config.py

環境変数の読み込み

Backend 全体設定の定義


設定値の解釈や判断を行ってはならない。


---

app/deps.py

依存関係（DI）の定義

インスタンス生成の責務


ビジネスロジックを含めてはならない。


---

api 層の責務

api/chat.py

チャット入力の受付

リクエストバリデーション

レスポンス形式の整形


以下は禁止する。

Dev Engine の内部ロジック実装

Workspace Index の直接操作



---

api/workspace.py

Workspace Index に関する API の提供

状態参照および更新要求の受付


永続化処理の詳細は infra 層へ委譲する。


---

api/project.py

Project 単位の操作 API を提供する

Project ID の検証を行う


判断処理を含めてはならない。


---

core 層の責務

core/dev_engine.py

Backend における 唯一の判断ロジック中枢 である。

ユーザー入力をもとに判断を行う

Workspace Index を参照する

LLM Service を統括する

Diff を生成する


以下は禁止する。

キャラクター表現の処理

API レスポンス整形



---

core/workflow.py

Backend 内部の処理フローを定義する

ステップの順序制御を行う


個別判断ロジックは含めない。


---

domain 層の責務

domain/workspace_index.py

Workspace Index のデータ構造定義

Index の構築・更新ルール定義


外部サービスへの依存は禁止する。


---

domain/snapshot.py

Snapshot の概念定義

必要最小範囲の参照モデルを表現する



---

domain/diff.py

Diff 構造の定義

Full Replace 方式を前提とする



---

services 層の責務

services/llm_service.py

LLM 呼び出しの抽象化

モデル切り替えや設定管理


判断ロジックは含めない。


---

services/expression_service.py

出力文の構文・言い回しの変換

キャラクター表現の適用


以下は禁止する。

判断結果の変更

Diff 内容の改変



---

infra 層の責務

infra/supabase.py

Supabase との通信処理

永続化処理の実装


ドメインロジックを含めてはならない。


---

infra/logger.py

Backend 用ログ出力処理

デバッグおよび動作確認用ログ



---

tests 層の責務

各層に対応するテストを配置する

テスト構造は実装構造と対応させる



---

責務違反時の扱い

責務違反が確認された場合、 それはバグではなく設計違反として扱う。

実装修正の前に、本文書との整合性を確認すること。


---

変更履歴

初版作成：ai-workbench Backend 設計フェーズ