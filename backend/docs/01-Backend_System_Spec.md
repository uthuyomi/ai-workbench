Backend System Specification

この文書の役割

この文書は ai-workbench Backend の最上位仕様書である。

本 Backend は、ChatGPT Projects の Documents に保存された設計文書を前提として、 人間および AI が共同で実装・改修・検証できることを目的に設計されている。

本書は Backend 全体の「入口」として機能し、 以降に定義されるすべての Backend 関連文書の 読み順・前提関係・優先順位 を定義する。


---

Backend の定義範囲

本 Backend は以下を責務範囲とする。

チャット入力の受付

開発モード / 雑談モードの切り分け

Workspace Index の管理および参照

LLM を用いた変更案（Diff）の生成

VSCode Extension へ適用可能な情報の提供


以下は責務範囲外とする。

実ファイルの直接編集

VSCode API の直接操作

自律的タスク実行（エージェント化）



---

設計思想の最上位原則

本 Backend は以下の原則に基づいて設計・実装される。

1. 判断主体は常に人間である


2. AI は判断補助を行うが、決定を行わない


3. 設計文書はコードと同等の一次成果物である



これらの原則は、後続のすべての仕様および実装に優先される。


---

前提ドキュメント一覧（必読順）

Backend を実装・改修する際は、必ず以下の文書を上から順に参照すること。

1. Backend_Overview_and_Purpose.md

Backend が存在する理由と背景



2. Backend_Core_Concepts_and_Invariants.md

不変条件および破ってはならない設計契約



3. Backend_Folder_Structure.md

ディレクトリおよびファイル構成



4. Backend_Module_Responsibilities.md

各モジュールの責務境界



5. Backend_API_Spec.md

エンドポイント仕様



6. Backend_Runtime_Workflow.md

実行時の処理フロー



7. Backend_Data_Models.md

データ構造・永続モデル



8. Backend_Non_Goals_and_Constraints.md

やらないこと・制約事項





---

本文書の扱いについて

本文書は Backend 全体の仕様変更が発生した場合のみ更新される

個別機能の変更では更新しない

本文書に反する実装は、他文書の記述内容に関わらず無効とする



---

実装時の使用方法

実装フェーズでは、以下のような指示形式を想定する。

「Backend_System_Spec.md を前提に Backend を実装する」

「Backend_System_Spec.md に違反していないかを確認する」


本 Backend において、本文書は 最上位の仕様的拘束力 を持つ。


---

変更履歴

初版作成：ai-workbench Backend 設計フェーズ