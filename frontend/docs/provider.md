ChatProvider State & Actions 仕様書

このドキュメントは、ai-workbench Frontend における ChatProvider が保持すべき state と actions を、人間・AI の双方が後から読んでも迷わないことを目的として 構造的に定義するものである。

本仕様は UI 実装よりも 先行して固定される背骨であり、 React / Next.js / Zustand / Context API など、 実装方式に依存しない概念設計として記述する。


---

1. ChatProvider の責務（再確認）

ChatProvider は以下の責務のみを持つ。

Backend API との通信状態を一元管理する

Chat 全体の状態（state）を保持する

UI から呼び出される操作（actions）を提供する


やってはいけないこと

表示ロジックを持つ

JSX / HTML を返す

UI コンポーネントの状態を直接操作する

Prompt や Diff の意味解釈を行う


ChatProvider は **「表示されない制御層」**である。


---

2. Provider が管理する State 一覧

2.1 基本識別情報

projectId: string

現在操作対象のプロジェクト ID

Backend のすべての API 呼び出しに付随する

UI から直接変更されることは基本的にない



---

2.2 チャット実行モード

mode: "dev" | "casual"

Workflow に渡される処理モード

ActionPanel から変更される

デフォルトは dev



---

2.3 実行ステータス

status: "idle" | "running" | "error"

idle    : 待機中

running : Backend 処理中（LLM 実行含む）

error   : 直近の処理でエラーが発生


UI はこの状態を 参照するだけで、変更してはいけない。


---

2.4 Snapshot（判断対象）

snapshot: Snapshot | null

Backend に送信される判断対象

Workspace Scan または事前生成済み Snapshot

Chat 実行前に必須


注意:

Provider は Snapshot を「作らない」

渡されたものを保持するだけ



---

2.5 Diff（最新の提案結果）

diff: Diff | null

Backend から返却された最新の Diff

ChatPanel が表示に使用する

Provider は内容を解釈しない



---

2.6 エラー情報

error: string | null

status === "error" の場合のみ意味を持つ

ユーザー表示用の最低限メッセージ

Stack trace や内部情報は保持しない



---

3. Provider が提供する Actions 一覧

3.1 Snapshot セット

setSnapshot(snapshot: Snapshot): void

Chat 実行前に Snapshot を登録する

Workspace Scan 後に呼ばれる想定

Snapshot が未設定の場合、chat 実行は失敗すべき



---

3.2 モード切替

setMode(mode: "dev" | "casual"): void

ActionPanel から呼ばれる

即座に state に反映される

Backend 呼び出しは発生しない



---

3.3 チャット実行（中核）

runChat(): Promise<void>

役割:

現在の snapshot / mode / existing diff を元に /chat API を呼び出す

実行中は status を running に変更

成功時は diff を更新し status を idle に戻す

失敗時は status を error にし error を設定


注意:

UI からは引数を渡させない

Provider 内の state を唯一の入力源とする



---

3.4 Diff クリア

clearDiff(): void

新しい判断を始める前のリセット用

UI 側から明示的に呼ばれる



---

3.5 エラーリセット

clearError(): void

status を idle に戻す

error を null にする

再実行前に使用



---

4. UI コンポーネントとの関係対応表

UI コンポーネント	参照する state	呼び出す action

ChatComposer	status	runChat
ChatPanel	diff, status	（なし）
ActionPanel	mode, status	setMode, clearDiff
Sidebar	projectId	（将来拡張）



---

5. 設計上の固定ルール（重要）

Provider は 1つだけ存在する

ネスト Provider を作らない

UI 側で Backend API を直接呼ばない

Provider に表示ロジックを足さない

state は「事実」、action は「操作」



---

6. 次フェーズへの接続点

この仕様が確定した時点で可能になること:

ChatProvider 実装（Context / Zustand どちらでも可）

Backend /chat API との実接続

ActionPanel の実動化

VSCode Extension との状態共有（将来）



---

このドキュメントは 変更履歴管理の対象とし、 state / action を追加する場合は必ずここを更新すること。