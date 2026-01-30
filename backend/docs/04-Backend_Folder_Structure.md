Backend Folder Structure

本文書の位置づけ

本文書は ai-workbench Backend におけるディレクトリおよびファイル構成を定義する。

本構成は、実装時にそのままディレクトリを作成できることを前提とし、 Backend_Core_Concepts_and_Invariants.md に定義された責務分離および不変条件を 物理構造として保証するための設計である。

フォルダ構成は単なる整理ではなく、 「どこに何を書いてよいか」「どこに書いてはいけないか」を強制する役割を持つ。


---

設計方針

Backend のフォルダ構成は、以下の方針に基づいて設計されている。

責務ごとに階層を分離する

判断ロジックと表現ロジックを物理的に隔離する

API 層・ドメイン層・インフラ層を明確に分ける

将来の拡張時に既存構造を破壊しない


これらの方針は、Backend の長期保守性を最優先した結果である。


---

ルートディレクトリ構成

以下は Backend のルートディレクトリ構成である。

backend/
├─ app/
├─ api/
├─ core/
├─ domain/
├─ services/
├─ infra/
├─ tests/
└─ README.md

各ディレクトリは明確な責務を持ち、 異なる層のコードを混在させてはならない。


---

各ディレクトリの役割

app/

アプリケーションのエントリーポイントおよび 全体設定を配置するディレクトリである。

app/
├─ main.py      # FastAPI エントリーポイント
├─ config.py    # 環境変数・設定管理
└─ deps.py      # 依存関係定義（DI）

ルーティングロジックは配置しない

判断ロジックは配置しない



---

api/

外部からのリクエストを受け付ける API 層である。

api/
├─ chat.py
├─ workspace.py
└─ project.py

リクエスト検証とレスポンス整形のみを行う

判断処理は core 層に委譲する

データ永続化の詳細を直接扱わない



---

core/

Backend の判断中枢を構成するディレクトリである。

core/
├─ dev_engine.py
└─ workflow.py

Dev Engine（判断ロジック）を配置する

Backend の意思決定フローをここに集約する

キャラクター表現を一切含めない



---

domain/

Backend が扱う概念モデルを定義する層である。

domain/
├─ workspace_index.py
├─ snapshot.py
└─ diff.py

データ構造およびドメイン概念のみを定義する

外部サービスへの依存を持たない

ロジックは最小限に留める



---

services/

外部サービスや補助機能を扱う層である。

services/
├─ llm_service.py
└─ expression_service.py

LLM 呼び出しを抽象化する

Expression Layer の処理をここに集約する

core 層からのみ呼び出される



---

infra/

インフラ依存の実装を配置する層である。

infra/
├─ supabase.py
└─ logger.py

データベースや外部 API への接続を担当する

core 層に直接依存させない

差し替え可能であることを前提とする



---

tests/

Backend 全体のテストコードを配置するディレクトリである。

層ごとにテストを分離する

実装と同じ構造を保つ



---

README.md の役割

Backend 直下の README.md は、 Backend 単体の概要と起動方法を記載するために使用する。

設計思想や詳細仕様は、Documents 側の仕様書を正とする。


---

禁止事項

以下の行為は禁止とする。

core 層から api 層を直接参照する

domain 層にインフラ依存を持ち込む

services 層を判断ロジックとして使用する

フォルダ構成を理由なく変更する



---

本文書の変更について

本文書の変更は Backend 全体構造の変更を意味する

新規ディレクトリ追加時は、必ず本文書を更新する

実装側のみの変更は禁止とする



---

変更履歴

初版作成：ai-workbench Backend 設計フェーズ