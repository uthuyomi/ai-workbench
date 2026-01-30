Backend API Specification

本文書の位置づけ

本文書は ai-workbench Backend が提供する API の仕様を定義する。

本書は、Backend_Module_Responsibilities.md で定義された責務分離を前提とし、 外部（Frontend / VSCode Extension）との通信契約を明確化するための文書である。

本文書に記載された API 仕様は、 実装・テスト・クライアント側実装のすべてにおいて一次情報として扱う。


---

API 設計方針

Backend API は以下の方針に従って設計されている。

REST 形式を採用する

JSON を唯一の通信フォーマットとする

明示的で予測可能なレスポンスを返す

内部構造を外部に漏らさない


API は便利さよりも 安全性と説明可能性 を優先する。


---

共通仕様

Base URL

/api


---

認証・認可

すべての API は Project 単位で操作される

認証情報は Header により提供される

認可の詳細は infra 層で処理される


本文書では、認証方式の詳細には立ち入らない。


---

共通レスポンス形式

{
  "success": true,
  "data": {},
  "error": null
}

エラー発生時は success を false とし、 error に詳細情報を含める。


---

API 一覧

POST /api/chat

概要

ユーザーからのチャット入力を受け付け、 Backend 内部で処理を行い、結果を返却する。


---

Request

{
  "project_id": "string",
  "mode": "dev" | "casual",
  "message": "string"
}

project_id：対象プロジェクト識別子

mode：チャット種別

dev：開発モード（Dev Engine 使用）

casual：雑談モード（Expression Layer のみ使用）


message：ユーザー入力テキスト



---

処理内容

1. リクエスト内容を検証する


2. Project の存在を確認する


3. mode に応じて処理を分岐する



dev モードの場合

Workspace Index をロードする

必要な範囲の Snapshot を生成する

Dev Engine を実行する

Diff を生成する


casual モードの場合

判断ロジックを実行しない

Expression Layer のみを適用する



---

Response

{
  "success": true,
  "data": {
    "messages": [
      {
        "role": "assistant",
        "content": "string"
      }
    ],
    "diff": null | {
      "files": []
    }
  },
  "error": null
}

messages：フロントエンド表示用メッセージ

diff：dev モード時のみ返却される変更差分



---

GET /api/workspace/index

概要

指定された Project の Workspace Index を取得する。


---

Request

Query Parameters:

project_id: string



---

処理内容

Workspace Index を読み込む

Index 情報を返却する



---

Response

{
  "success": true,
  "data": {
    "workspace_index": {}
  },
  "error": null
}


---

POST /api/workspace/index

概要

Workspace Index の再構築または更新を要求する。


---

Request

{
  "project_id": "string"
}


---

処理内容

対象 Project の Workspace を走査する

Index を再構築する

永続化する



---

Response

{
  "success": true,
  "data": {
    "status": "updated"
  },
  "error": null
}


---

GET /api/project

概要

Project 情報を取得する。


---

Request

Query Parameters:

project_id: string



---

Response

{
  "success": true,
  "data": {
    "project": {}
  },
  "error": null
}


---

API 仕様の変更について

API 仕様の変更は必ず本文書を先に更新する

破壊的変更の場合は理由を明記する

実装のみの変更は禁止とする



---

変更履歴

初版作成：ai-workbench Backend 設計フェーズ