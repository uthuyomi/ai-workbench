Backend Data Models

本文書の位置づけ

本文書は ai-workbench Backend において使用されるデータモデルを定義する。

ここで定義されるデータ構造は、

Workspace Index

Snapshot

Diff

永続化データ（Supabase）


のすべてに共通する 唯一の正とする仕様 である。

実装は本文書に従って行われなければならず、 本文書に存在しないフィールドや意味付けを独自に追加してはならない。


---

データ設計方針

Backend のデータモデルは以下の方針に基づいて設計されている。

構造を明示する

推論に依存しない

永続データと一時データを明確に分離する

人間が読んで意味を追える形にする


これにより、 AI による誤解釈や実装逸脱を最小限に抑える。


---

Project モデル

Project は Backend における最上位の作業単位である。

{
  "id": "string",
  "owner_id": "string",
  "name": "string",
  "created_at": "timestamp"
}

Project は Workspace Index や履歴データの紐付け単位として使用される。


---

Workspace Index モデル

Workspace Index は、コードベース全体の構造情報を保持するデータである。

目的

ファイル構成の把握

参照範囲決定の高速化

Snapshot 対象の限定


Workspace Index は コード内容を保持しない。


---

構造定義

{
  "project_id": "string",
  "index_version": "string",
  "generated_at": "timestamp",
  "files": [
    {
      "path": "string",
      "language": "string",
      "hash": "string",
      "imports": ["string"],
      "exports": ["string"],
      "dependencies": ["string"]
    }
  ]
}

path：ファイルパス

language：判定された言語

hash：内容識別用ハッシュ

imports / exports：静的解析結果

dependencies：参照関係



---

Snapshot モデル

Snapshot は、判断に必要な最小限の実データ集合である。

特性

オンデマンド生成

永続化しない

判断完了後に破棄可能



---

構造定義

{
  "project_id": "string",
  "files": [
    {
      "path": "string",
      "content": "string"
    }
  ]
}

Snapshot は Workspace Index を元に生成される。


---

Diff モデル

Diff は Backend が生成する唯一の変更成果物である。

原則

常に Full Replace

ファイル単位で差分を表現



---

構造定義

{
  "project_id": "string",
  "files": [
    {
      "path": "string",
      "before": "string",
      "after": "string"
    }
  ]
}

before：変更前の全文

after：変更後の全文



---

チャットメッセージモデル

Backend がフロントエンドへ返却するメッセージ構造である。

{
  "role": "assistant" | "user",
  "content": "string"
}


---

永続化データ（Supabase）

workspace_indexes テーブル

{
  "id": "string",
  "project_id": "string",
  "index_version": "string",
  "index_data": "jsonb",
  "created_at": "timestamp"
}

最新 Index を正とする

過去 Index は履歴用途のみ



---

データ変更ルール

データ構造変更時は本文書を先に更新する

フィールドの意味変更は禁止する

暗黙のデータ拡張を行わない



---

本文書の変更について

本文書の変更は、 Backend 全体のデータ整合性に直接影響する。

変更理由と影響範囲を必ず明記すること。


---

変更履歴

初版作成：ai-workbench Backend 設計フェーズ