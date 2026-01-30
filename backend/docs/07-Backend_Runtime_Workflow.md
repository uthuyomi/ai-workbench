Backend Runtime Workflow

本文書の位置づけ

本文書は ai-workbench Backend における実行時の処理フローを定義する。

Backend_API_Spec.md で定義された各エンドポイントが呼び出された際に、 Backend 内部で どの順序で・どの責務が・どの条件で実行されるか を明文化することを目的とする。

本文書は、実装時・デバッグ時・改修時の 唯一の実行フロー基準 として扱う。


---

実行フロー設計方針

Backend の実行フローは以下の方針に従う。

処理は常に上位から下位へ流れる

分岐条件は明示的に定義する

暗黙の副作用を許可しない

途中状態は外部に漏らさない


実行フローは「速さ」よりも「追跡可能性」を優先する。


---

基本実行フロー（共通）

以下は、すべての API に共通する基本実行フローである。

[1] Request 受信
[2] リクエスト形式検証
[3] 認証・認可チェック
[4] Project 検証
[5] 処理分岐
[6] レスポンス生成
[7] Response 返却

各ステップは省略されず、必ず順番に実行される。


---

POST /api/chat 実行フロー

ステップ詳細

[1] POST /api/chat を受信
[2] Request Body を検証
[3] Project ID を検証
[4] mode を判定

ここから処理は mode に応じて分岐する。


---

dev モード実行フロー

[5] Workspace Index をロード
[6] 判断対象範囲を決定
[7] Snapshot をオンデマンド生成
[8] Dev Engine を起動
[9] LLM Service を呼び出し
[10] 判断結果を取得
[11] Diff を生成（Full Replace）
[12] 表示用メッセージを生成

Snapshot は必要最小範囲のみ生成する

判断ロジックは core/dev_engine.py に集約される



---

casual モード実行フロー

[5] 判断ロジックを実行しない
[6] Expression Layer を適用
[7] 表示用メッセージを生成

Workspace Index を参照しない

Snapshot を生成しない

Diff は生成されない



---

レスポンス返却

[13] レスポンス形式を構築
[14] Response を返却

レスポンスは Backend_API_Spec.md に定義された形式に従う。


---

Workspace Index 更新フロー

POST /api/workspace/index

[1] リクエスト受信
[2] Project 検証
[3] Workspace 走査
[4] Index 構築
[5] 永続化
[6] 完了レスポンス返却

Index 更新処理は、 判断ロジックとは独立して実行される。


---

エラーハンドリング方針

エラー発生時のフローは以下に従う。

[Error] 発生
  ↓
[原因特定]
  ↓
[安全なレスポンス生成]
  ↓
[Response 返却]

内部例外をそのまま外部に返却しない

実行途中の状態は破棄する

部分的な成功状態を残さない



---

ログ出力ポイント

以下のタイミングでログを出力することを推奨する。

API 受信時

mode 分岐時

Workspace Index ロード時

Snapshot 生成時

Dev Engine 実行前後

Diff 生成完了時


ログは 動作確認と追跡性確保 のために使用する。


---

本文書の変更について

実行フロー変更時は必ず本文書を更新する

実装先行の変更は禁止とする

フロー簡略化は原則行わない



---

変更履歴

初版作成：ai-workbench Backend 設計フェーズ