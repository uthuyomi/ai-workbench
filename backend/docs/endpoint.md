Backend API Endpoints & JSON Schema

本文書の目的

本書は ai-workbench Backend が提供するすべての API エンドポイントについて、 以下を一望できる形で定義する。

エンドポイント一覧

役割（何のための API か）

どの層と接続するか（Frontend / VSCode Extension）

リクエスト JSON 形式

レスポンス JSON 形式


この文書は Frontend 実装・VSCode Extension 実装・Backend 実装 の共通参照点とする。


---

API 全体マップ

Frontend / VSCode Extension
        ↓
     API Layer (FastAPI)
        ↓
   core / workflow
        ↓
 dev_engine / expression
        ↓
     infra / DB


---

1. POST /api/chat

役割

ユーザー入力を受け取るメインエンドポイント

開発チャット / 雑談チャットを共通で処理

character / mode を切り替え可能


接続元

Frontend（Web UI）

VSCode Extension



---

Request JSON

{
  "project_id": "string",
  "workspace_id": "string",
  "mode": "dev | casual",
  "character_id": "nitori",
  "message": "ユーザー入力テキスト",
  "context": {
    "branch": "optional",
    "reply_to": "optional"
  }
}

フィールド説明

フィールド	説明

project_id	プロジェクト識別子
workspace_id	Workspace Index の参照先
mode	処理モード（dev / casual）
character_id	表現キャラクター
message	ユーザー発話
context	分岐・並列会話用メタ情報



---

Response JSON

{
  "message_id": "uuid",
  "role": "assistant",
  "character_id": "nitori",
  "content": "生成された応答テキスト",
  "artifacts": {
    "diff": null,
    "files": []
  },
  "metadata": {
    "mode": "dev",
    "timestamp": "ISO8601"
  }
}


---

2. GET /api/workspace/index

役割

Workspace Index の取得

Backend が把握している構造の可視化


接続元

Frontend

VSCode Extension



---

Request

GET /api/workspace/index?workspace_id=xxx


---

Response JSON

{
  "workspace_id": "string",
  "files": [
    {
      "path": "src/app/page.tsx",
      "language": "typescript",
      "hash": "sha256"
    }
  ],
  "last_updated": "ISO8601"
}


---

3. POST /api/workspace/snapshot

役割

現在の Workspace 状態を Backend に送信

初回 or 差分検出の基準


接続元

VSCode Extension



---

Request JSON

{
  "workspace_id": "string",
  "files": [
    {
      "path": "src/index.ts",
      "content": "file content"
    }
  ]
}


---

Response JSON

{
  "status": "ok",
  "snapshot_id": "uuid"
}


---

4. POST /api/project/register

役割

Project 情報の登録

永続化単位の起点


接続元

Frontend



---

Request JSON

{
  "project_name": "string",
  "description": "string"
}


---

Response JSON

{
  "project_id": "uuid",
  "created_at": "ISO8601"
}


---

5. GET /api/characters

役割

利用可能なキャラクター一覧取得


接続元

Frontend



---

Response JSON

{
  "characters": [
    {
      "id": "nitori",
      "display_name": "河城にとり",
      "description": "技術寄り・軽快な語り口"
    }
  ]
}


---

各 API と Backend 内部の接続関係

API	接続先

/api/chat	core/workflow → dev_engine → expression
/api/workspace/index	domain/workspace_index
/api/workspace/snapshot	domain/snapshot → infra
/api/project/register	infra/supabase
/api/characters	services/expression/registry



---

設計上の注意点

API は 薄く保つ

判断は core でのみ行う

JSON 構造は破壊的変更を避ける

VSCode Extension は snapshot / index を主に使用



---

本書の位置づけ

実装時のチェックリスト

Frontend / Extension / Backend の共通契約

AI に渡す「安全な API 境界」


この文書が存在する限り、 Backend API は一貫性を失わない。