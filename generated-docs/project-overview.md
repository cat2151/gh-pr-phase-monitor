Last updated: 2026-01-04

# Project Overview

## プロジェクト概要
- GitHub Copilotが自動実装するPull Requestのフェーズを監視し、効率的な開発を支援するツールです。
- PRの状況に応じて自動で通知やアクションを実行し、開発者の負担を軽減します。
- 現在は、より柔軟な監視と制御を可能にするPython版として開発が進められています。

## 技術スタック
- フロントエンド: このプロジェクトはバックエンド処理が主であり、直接的なフロントエンド技術は使用していません。
- 音楽・オーディオ: 音楽やオーディオ関連の技術は使用していません。
- 開発ツール:
    - **Visual Studio Code (VS Code)**: `.vscode/settings.json`によって開発環境の統一された設定を提供します。
    - **Git / GitHub**: バージョン管理システムおよび主要な開発プラットフォームとして利用しています。
- テスト:
    - **pytest**: Pythonアプリケーションの単体テストや結合テストを記述、実行するためのフレームワークです。
- ビルドツール: このプロジェクトでは特定のビルドツールは明示されていませんが、Pythonの標準的なパッケージ管理（例: pip）を利用する可能性があります。
- 言語機能:
    - **Python**: プロジェクトの主要な開発言語です。GitHub APIとの連携やPR監視ロジックの実装に使用されます。
- 自動化・CI/CD:
    - このプロジェクト自体は監視ツールであり、GitHub Actionsは**過去に試みられた実装**でしたが、現在はPython版の開発に移行しています。Python版は、GitHub ActionsなどのCI/CDプラットフォーム上で実行されることを想定しています。
- 開発標準:
    - **EditorConfig**: `.editorconfig`ファイルにより、異なるエディタやIDE間でコードの整形スタイルを統一します。
    - **Ruff**: `ruff.toml`ファイルにより、Pythonコードのリンティングとフォーマットを高速に行い、コード品質と一貫性を維持します。

## ファイル階層ツリー
```
📄 .editorconfig
📄 .gitignore
📁 .vscode/
  📊 settings.json
📄 LICENSE
📖 README.ja.md
📖 README.md
📖 STRUCTURE.md
📄 _config.yml
📄 config.toml.example
📁 generated-docs/
📄 cat-github-watcher.py
📄 pytest.ini
📄 ruff.toml
📁 src/
  📄 __init__.py
  📁 gh_pr_phase_monitor/
    📄 __init__.py
    📄 colors.py
    📄 comment_manager.py
    📄 config.py
    📄 github_client.py
    📄 main.py
    📄 phase_detector.py
    📄 pr_actions.py
📁 tests/
  📄 test_interval_parsing.py
  📄 test_phase_detection.py
  📄 test_post_comment.py
  📄 test_pr_actions.py
```

## ファイル詳細説明
-   `.editorconfig`: さまざまなエディタやIDEで、インデントスタイル、文字コード、行末などの基本的なコード整形ルールを定義し、プロジェクト全体で一貫したコーディングスタイルを維持します。
-   `.gitignore`: Gitによるバージョン管理から除外するファイルやディレクトリ（例: ビルド成果物、ログファイル、一時ファイルなど）を指定します。
-   `LICENSE`: プロジェクトのソフトウェアライセンス情報（MIT License）を記述しています。これにより、プロジェクトの利用、配布、改変に関する条件が明示されます。
-   `README.ja.md`: プロジェクトの日本語版の概要、目的、特徴、セットアップ方法、使い方、注意事項などが詳細に記述されています。
-   `README.md`: プロジェクトの英語版の概要ドキュメントです。
-   `STRUCTURE.md`: プロジェクトの構造に関する追加情報を提供するドキュメントです。
-   `_config.yml`: プロジェクトで利用される可能性のある設定ファイルの一つです。YAML形式でアプリケーションの設定を管理します。
-   `config.toml.example`: アプリケーションの設定の例を示すTOML形式のファイルです。これをコピーして実際の環境に合わせて設定をカスタマイズすることが想定されます。
-   `generated-docs/`: 自動生成されたドキュメントファイルを格納するためのディレクトリです。
-   `cat-github-watcher.py`: プロジェクトの主要な実行スクリプト、またはメインのエントリポイントとなるファイルです。全体の監視プロセスを開始します。
-   `pytest.ini`: pytestテストフレームワークの設定ファイルです。テストの発見方法、実行オプションなどを定義します。
-   `ruff.toml`: Ruffリンターの設定ファイルです。Pythonコードの静的解析ルールや自動フォーマットに関する設定を定義し、コード品質を向上させます。
-   `src/__init__.py`: `src`ディレクトリがPythonパッケージであることを示す初期化ファイルです。
-   `src/gh_pr_phase_monitor/__init__.py`: `gh_pr_phase_monitor`ディレクトリがPythonサブパッケージであることを示す初期化ファイルです。
-   `src/gh_pr_phase_monitor/colors.py`: ターミナル出力などに色付けを行うためのユーティリティ関数を提供するモジュールです。
-   `src/gh_pr_phase_monitor/comment_manager.py`: GitHub Pull Requestにコメントを投稿したり、既存のコメントを管理したりする機能を提供するモジュールです。
-   `src/gh_pr_phase_monitor/config.py`: アプリケーションの各種設定（APIキー、監視間隔など）を読み込み、管理するためのモジュールです。
-   `src/gh_pr_phase_monitor/github_client.py`: GitHub APIと連携するためのクライアントライブラリをラップし、PR情報の取得、ステータス更新、コメント投稿などの機能を提供するモジュールです。
-   `src/gh_pr_phase_monitor/main.py`: `gh_pr_phase_monitor`パッケージのメインロジックを含むファイルです。監視ループや全体の処理フローを定義します。
-   `src/gh_pr_phase_monitor/phase_detector.py`: GitHub Pull Requestの特定のフェーズ（例: Copilotによる実装完了、レビュー完了）を検知するためのロジックを提供するモジュールです。
-   `src/gh_pr_phase_monitor/pr_actions.py`: PRのフェーズ検知に基づいて実行される具体的なアクション（例: 通知、変更適用依頼、PRのReady化）を定義するモジュールです。
-   `tests/test_interval_parsing.py`: 監視間隔のパース機能に関するテストを記述したファイルです。
-   `tests/test_phase_detection.py`: `phase_detector.py`モジュール内のフェーズ検知ロジックに関するテストを記述したファイルです。
-   `tests/test_post_comment.py`: コメント投稿機能に関するテストを記述したファイルです。
-   `tests/test_pr_actions.py`: `pr_actions.py`モジュール内のPRアクション機能に関するテストを記述したファイルです。

## 関数詳細説明
-   **`main.py` 内の関数**
    -   `main()`:
        -   **役割**: プロジェクトのメインエントリポイントであり、PR監視プロセスの全体を統括します。設定の読み込み、GitHubクライアントの初期化、監視ループの開始などを担当します。
        -   **引数**: なし、またはコマンドライン引数（例: 設定ファイルのパス）。
        -   **戻り値**: 実行結果を示す整数ステータスコード。

-   **`github_client.py` 内の関数/メソッド**
    -   `GitHubClient.__init__(token)`:
        -   **役割**: GitHub APIと対話するためのクライアントオブジェクトを初期化します。
        -   **引数**: `token` (str): GitHub APIへの認証に使用するパーソナルアクセストークン。
        -   **戻り値**: なし。
    -   `GitHubClient.get_pull_request_info(repository, pr_number)`:
        -   **役割**: 指定されたリポジトリとPR番号に基づいて、Pull Requestの詳細情報をGitHub APIから取得します。
        -   **引数**: `repository` (str): リポジトリ名 (例: "owner/repo")、`pr_number` (int): Pull Requestの番号。
        -   **戻り値**: `dict`: Pull Requestの詳細情報を含む辞書。
    -   `GitHubClient.post_comment(repository, pr_number, comment_body)`:
        -   **役割**: 指定されたPull Requestに新しいコメントを投稿します。
        -   **引数**: `repository` (str), `pr_number` (int), `comment_body` (str): 投稿するコメントの内容。
        -   **戻り値**: `bool`: コメント投稿の成功/失敗。
    -   `GitHubClient.update_pr_status(repository, pr_number, new_state)`:
        -   **役割**: Pull Requestのステータス（例: "draft" から "open" / "ready for review" へ）を更新します。
        -   **引数**: `repository` (str), `pr_number` (int), `new_state` (str): 更新後のPRステータス (例: "open", "closed")。
        -   **戻り値**: `bool`: ステータス更新の成功/失敗。
    -   `GitHubClient.is_bot_user(username)`:
        -   **役割**: 指定されたユーザー名がBotアカウントであるかどうかを判定します。
        -   **引数**: `username` (str): チェックするユーザー名。
        -   **戻り値**: `bool`: BotであればTrue、そうでなければFalse。

-   **`phase_detector.py` 内の関数**
    -   `detect_copilot_completion(pr_info, commits)`:
        -   **役割**: Pull Requestの最新のコミット履歴やPR情報に基づいて、GitHub Copilotによる実装が完了したフェーズを検知します。
        -   **引数**: `pr_info` (dict): Pull Request情報、`commits` (list): コミット履歴のリスト。
        -   **戻り値**: `bool`: Copilotの完了が検知されればTrue、そうでなければFalse。
    -   `detect_review_status(pr_reviews)`:
        -   **役割**: Pull Requestに提出されたレビューの状況を分析し、特定のレビュー（例: Copilotによるレビュー）が完了したかなどを検知します。
        -   **引数**: `pr_reviews` (list): Pull Requestのレビュー履歴のリスト。
        -   **戻り値**: `dict`: レビュー状況に関する情報（例: Copilotレビューが完了したか、そのURLなど）。

-   **`pr_actions.py` 内の関数**
    -   `notify_pr_creator(pr_info, comment_manager)`:
        -   **役割**: Pull Request作成者に対して、特定のイベント（例: Copilot実装完了）を通知するコメントを投稿します。
        -   **引数**: `pr_info` (dict): Pull Request情報、`comment_manager` (CommentManager): コメント管理オブジェクト。
        -   **戻り値**: `bool`: 通知の成功/失敗。
    -   `request_copilot_apply_changes(pr_info, review_url, comment_manager)`:
        -   **役割**: Copilotのレビューコメントに基づいて変更を適用するよう、Copilotに対してコメントで依頼します。
        -   **引数**: `pr_info` (dict): Pull Request情報、`review_url` (str): レビューコメントのスレッドURL、`comment_manager` (CommentManager): コメント管理オブジェクト。
        -   **戻り値**: `bool`: 依頼の成功/失敗。
    -   `set_pr_ready_for_review(pr_info, github_client)`:
        -   **役割**: Draft状態のPull Requestを「Ready for review」状態に変更します。
        -   **引数**: `pr_info` (dict): Pull Request情報、`github_client` (GitHubClient): GitHubクライアントオブジェクト。
        -   **戻り値**: `bool`: 状態変更の成功/失敗。

-   **`comment_manager.py` 内の関数/メソッド**
    -   `CommentManager.post_notification(pr_id, message)`:
        -   **役割**: 特定のPull Requestに通知用のコメントを投稿します。
        -   **引数**: `pr_id` (int/str): Pull Requestの識別子、`message` (str): 投稿する通知メッセージ。
        -   **戻り値**: `bool`: 投稿の成功/失敗。
    -   `CommentManager.post_action_request(pr_id, message)`:
        -   **役割**: 特定のPull Requestに、アクションを要求するコメントを投稿します。
        -   **引数**: `pr_id` (int/str): Pull Requestの識別子、`message` (str): 投稿するアクション要求メッセージ。
        -   **戻り値**: `bool`: 投稿の成功/失敗。

-   **`config.py` 内の関数**
    -   `load_config(config_path)`:
        -   **役割**: 指定されたパスから設定ファイルを読み込み、アプリケーション全体で利用可能な設定オブジェクトを返します。
        -   **引数**: `config_path` (str): 設定ファイルのパス。
        -   **戻り値**: `dict`: 読み込まれた設定を含む辞書。
    -   `get_setting(key, default=None)`:
        -   **役割**: 読み込まれた設定から指定されたキーの値を取得します。
        -   **引数**: `key` (str): 取得する設定のキー、`default` (any): キーが存在しない場合のデフォルト値。
        -   **戻り値**: `any`: 設定値。

-   **`colors.py` 内の関数**
    -   `colorize(text, color_code)`:
        -   **役割**: ターミナル出力用のテキストに指定された色コードを適用し、色付きの文字列を生成します。
        -   **引数**: `text` (str): 色を適用するテキスト、`color_code` (str/int): 色を示すコード。
        -   **戻り値**: `str`: 色コードが付加されたテキスト。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした

---
Generated at: 2026-01-04 07:01:53 JST
