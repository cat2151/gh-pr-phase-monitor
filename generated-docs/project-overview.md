Last updated: 2026-01-09

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエストを監視し、適切な通知やアクションを自動実行するPythonツールです。
- 認証済みGitHubユーザーの所有リポジトリを対象に、GraphQL APIを用いて効率的にPRのフェーズを自動判定します。
- ドライランモード、PRのReady化、自動コメント投稿、モバイル通知、自動マージ機能により、開発ワークフローを支援します。

## 技術スタック
- フロントエンド:
    - Selenium: ブラウザ自動操縦のためのPythonライブラリ。ウェブページ上の要素操作やイベントシミュレーションに使用されます。
    - Playwright: Seleniumの代替として設定可能なブラウザ自動操縦ライブラリ。モダンなウェブブラウザに対応します。
    - ブラウザドライバー: Edge、Chrome、Firefoxなどのブラウザを自動操縦するための実行環境（WebDriver）。
- 音楽・オーディオ: (直接的な音楽・オーディオ技術は使用されていませんが、通知機能があります)
    - ntfy.sh: モバイル端末へのプッシュ通知を送信するためのサービス。PRのレビュー準備完了通知などに利用されます。
- 開発ツール:
    - GitHub CLI (`gh`): GitHubアカウントの認証、APIアクセス、リポジトリ操作をコマンドラインから行うためのツール。
    - GitHub GraphQL API: 効率的にGitHubのPR情報、リポジトリ情報などを取得するためのクエリ言語。
    - GitHub Copilot, copilot-pull-request-reviewer, copilot-swe-agent: GitHub Copilotを基盤とした自動コード生成、コードレビュー、修正エージェントとの連携を前提としています。
- テスト:
    - pytest: Pythonのテストフレームワーク。プロジェクト内のユニットテストや結合テストの実行に用いられます。
- ビルドツール: (明示的なビルドツールは使用されていませんが、Pythonの依存関係管理があります)
    - pip: Pythonパッケージインストーラ。`requirements-automation.txt`に基づき依存パッケージを管理します。
- 言語機能:
    - Python 3.x: プロジェクトの主要なプログラミング言語。
    - TOML: 設定ファイル（`config.toml`）の記述に使用される人間が読みやすい設定ファイル形式。
    - ANSI カラーコード: コンソール出力に色付けを行い、視覚的な情報を豊かにするための標準規格。
- 自動化・CI/CD: (このツール自体が自動化を目的としています)
    - GitHub Actions: (READMEの自動生成などに使用されていますが、プロジェクトの主要な監視機能とは直接関係ありません)
- 開発標準:
    - .editorconfig: 異なるエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイル。
    - ruff: Pythonコードのリンティングとフォーマットを高速に行うツール。

## ファイル階層ツリー
```
cat-github-watcher/
├── cat-github-watcher.py
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py
│       ├── config.py
│       ├── github_client.py
│       ├── phase_detector.py
│       ├── comment_manager.py
│       ├── pr_actions.py
│       └── main.py
└── tests/
```

※提供されたプロジェクト情報では上記ツリーが省略されていたため、主要なもののみ記載。
詳細なファイル階層は以下の通りです。
```
cat-github-watcher/
├── .editorconfig
├── .gitignore
├── .vscode/
│   └── settings.json
├── LICENSE
├── MERGE_CONFIGURATION_EXAMPLES.md
├── PHASE3_MERGE_IMPLEMENTATION.md
├── README.ja.md
├── README.md
├── STRUCTURE.md
├── _config.yml
├── cat-github-watcher.py
├── config.toml.example
├── demo_automation.py
├── demo_comparison.py
├── docs/
│   ├── IMPLEMENTATION_SUMMARY.ja.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PR67_IMPLEMENTATION.md
│   ├── RULESETS.md
│   ├── VERIFICATION_GUIDE.en.md
│   ├── VERIFICATION_GUIDE.md
│   ├── browser-automation-approaches.en.md
│   └── browser-automation-approaches.md
├── generated-docs/
├── pytest.ini
├── requirements-automation.txt
├── ruff.toml
├── src/
│   ├── __init__.py
│   └── gh_pr_phase_monitor/
│       ├── __init__.py
│       ├── browser_automation.py
│       ├── colors.py
│       ├── comment_fetcher.py
│       ├── comment_manager.py
│       ├── config.py
│       ├── github_auth.py
│       ├── github_client.py
│       ├── graphql_client.py
│       ├── issue_fetcher.py
│       ├── main.py
│       ├── notifier.py
│       ├── phase_detector.py
│       ├── pr_actions.py
│       ├── pr_fetcher.py
│       └── repository_fetcher.py
└── tests/
    ├── test_no_change_timeout.py
    ├── test_browser_automation.py
    ├── test_config_rulesets.py
    ├── test_config_rulesets_features.py
    ├── test_elapsed_time_display.py
    ├── test_hot_reload.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_parsing.py
    ├── test_issue_fetching.py
    ├── test_no_open_prs_issue_display.py
    ├── test_notification.py
    ├── test_phase3_merge.py
    ├── test_phase_detection.py
    ├── test_post_comment.py
    ├── test_post_phase3_comment.py
    ├── test_pr_actions.py
    ├── test_pr_actions_rulesets_features.py
    ├── test_pr_actions_with_rulesets.py
    ├── test_status_summary.py
    └── test_verbose_config.py
```

## ファイル詳細説明
- **`.editorconfig`**: コーディングスタイル設定ファイル。IDEやエディタ間でコードの整形ルール（インデント、改行コードなど）を統一するために使用されます。
- **`.gitignore`**: Gitが追跡しないファイルやディレクトリを指定するファイル。一時ファイル、ログ、環境固有の設定などが含まれます。
- **`.vscode/settings.json`**: VS Codeエディタのワークスペース固有の設定ファイル。リンターやフォーマッター、Pythonインタプリタの設定などが含まれます。
- **`LICENSE`**: プロジェクトのライセンス情報（MIT License）が記載されています。
- **`MERGE_CONFIGURATION_EXAMPLES.md`**: マージ設定に関する追加の例や情報を提供するドキュメントです。
- **`PHASE3_MERGE_IMPLEMENTATION.md`**: フェーズ3でのPR自動マージ機能の実装に関する詳細な説明ドキュメントです。
- **`README.ja.md` / `README.md`**: プロジェクトの概要、機能、使い方、アーキテクチャなどが日本語と英語で記述された主要ドキュメントです。
- **`STRUCTURE.md`**: プロジェクトの全体的な構造や設計に関するドキュメントです。
- **`_config.yml`**: GitHub Pagesなどの静的サイトジェネレータで使用される設定ファイル。
- **`cat-github-watcher.py`**: プロジェクトのエントリーポイントとなるスクリプト。通常、`src/gh_pr_phase_monitor/main.py`の機能を呼び出してツールを起動します。
- **`config.toml.example`**: 設定ファイル`config.toml`のサンプル。監視間隔、通知設定、自動マージ設定などのテンプレートが提供されます。
- **`demo_automation.py`**: ブラウザ自動操縦機能のデモンストレーション用スクリプト。
- **`demo_comparison.py`**: 異なるブラウザ自動操縦ライブラリ（Selenium, Playwright）の比較デモンストレーション用スクリプト。
- **`docs/`**: プロジェクトに関する追加のドキュメントが格納されているディレクトリ。
    - **`IMPLEMENTATION_SUMMARY.ja.md` / `IMPLEMENTATION_SUMMARY.md`**: 実装の概要を日本語と英語で説明するドキュメント。
    - **`PR67_IMPLEMENTATION.md`**: 特定のプルリクエスト（PR67）に関連する実装の詳細を記述したドキュメント。
    - **`RULESETS.md`**: ルールセット機能に関する説明ドキュメント。
    - **`VERIFICATION_GUIDE.en.md` / `VERIFICATION_GUIDE.md`**: 動作検証ガイド。ツールの設定や機能が正しく動作するかを確認するための手順が記述されています。
    - **`browser-automation-approaches.en.md` / `browser-automation-approaches.md`**: ブラウザ自動操縦のアプローチに関する説明ドキュメント。
- **`generated-docs/`**: 自動生成されたドキュメントが格納される可能性のあるディレクトリ。
- **`pytest.ini`**: Pythonのテストフレームワークであるpytestの設定ファイル。テストの発見ルールやオプションが記述されています。
- **`requirements-automation.txt`**: ブラウザ自動操縦機能（Selenium, Playwrightなど）に必要なPythonライブラリの依存関係リスト。
- **`ruff.toml`**: PythonコードのリンティングおよびフォーマットツールであるRuffの設定ファイル。コードの品質と一貫性を保ちます。
- **`src/`**: プロジェクトの主要なソースコードが格納されているディレクトリ。
    - **`gh_pr_phase_monitor/`**: PR監視ロジックの主要なモジュールをまとめたPythonパッケージ。
        - **`__init__.py`**: Pythonパッケージとして認識させるためのファイル。
        - **`browser_automation.py`**: SeleniumやPlaywrightを利用してブラウザを自動操縦し、特定のGitHubアクションを実行するロジックが含まれます。
        - **`colors.py`**: コンソール出力にANSIカラーコードを適用するためのユーティリティ関数を提供します。
        - **`comment_fetcher.py`**: GitHub APIを通じてPRのコメント履歴を取得する機能を提供します。
        - **`comment_manager.py`**: PRにコメントを投稿したり、既存のコメントを確認・管理するロジックが含まれます。
        - **`config.py`**: `config.toml`から設定を読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトを提供するモジュールです。
        - **`github_auth.py`**: GitHub CLI (`gh`) を利用してGitHub認証情報を取得・管理する機能を提供します。
        - **`github_client.py`**: GitHub REST APIおよびGraphQL APIとの連携を抽象化し、リポジトリやPR情報などの取得機能を提供します。
        - **`graphql_client.py`**: GitHub GraphQL APIに特化した低レベルのクエリ実行機能を提供します。
        - **`issue_fetcher.py`**: GitHub APIを通じてリポジトリのIssue情報を取得する機能を提供します。
        - **`main.py`**: ツールのメイン実行ループ、監視ロジックのオーケストレーション、および各モジュールの呼び出しを担当する主要なスクリプトです。
        - **`notifier.py`**: ntfy.shサービスを利用してモバイル端末へ通知を送信する機能を提供します。
        - **`phase_detector.py`**: プルリクエストの現在の状態（フェーズ1, 2, 3, LLM working）を判定するロジックが含まれます。
        - **`pr_actions.py`**: PRをReady状態にする、特定のコメントを投稿する、PRをマージする、ブラウザでPRページを開くといった具体的なアクションを実行する機能を提供します。
        - **`pr_fetcher.py`**: GitHub APIを通じて特定のPRの情報を取得する機能を提供します。
        - **`repository_fetcher.py`**: GitHub APIを通じて認証済みユーザーが所有するリポジトリの一覧を取得する機能を提供します。
- **`tests/`**: プロジェクトのテストスイートが格納されているディレクトリ。
    - **`test_*.py`**: 各モジュールや機能に対応するテストスクリプト。設定の読み込み、フェーズ判定、通知、PRアクションなどの動作を検証します。

## 関数詳細説明
このプロジェクトは単一責任の原則に基づきモジュール化されているため、各ファイルが特定の役割を果たす関数群を持っています。以下に主要な機能とその役割を担うと思われる関数の説明を概説します。具体的な引数や戻り値はソースコードに依存しますが、一般的な役割を記述します。

- **`main.py`**
    - `run_monitoring_loop()`:
        - **役割**: ツールのメイン監視ループを開始し、設定された間隔でリポジトリとPRの監視、フェーズ判定、アクション実行を繰り返します。
        - **機能**: `config.py`から設定を読み込み、`repository_fetcher.py`からリポジトリを取得、各リポジトリで`pr_fetcher.py`と`phase_detector.py`を呼び出し、結果に基づいて`pr_actions.py`、`comment_manager.py`、`notifier.py`の関数を呼び出します。
- **`config.py`**
    - `load_config(config_path: str) -> Config` (仮称):
        - **役割**: 指定されたパスからTOML形式の設定ファイルを読み込み、パースして設定オブジェクトを返します。
        - **機能**: ファイルの存在確認、TOML形式のパース、デフォルト値の適用、設定値のバリデーションを行います。
- **`repository_fetcher.py`**
    - `fetch_user_repositories(github_client: GitHubClient) -> List[Repository]` (仮称):
        - **役割**: 認証済みのGitHubユーザーが所有するリポジトリのリストを取得します。
        - **機能**: `github_client`を介してGraphQL APIを呼び出し、リポジトリ名、ID、URLなどの情報を取得します。
- **`pr_fetcher.py`**
    - `fetch_open_pull_requests(github_client: GitHubClient, repo_id: str) -> List[PullRequest]` (仮称):
        - **役割**: 指定されたリポジトリのオープンなプルリクエストのリストを取得します。
        - **機能**: `github_client`を介してGraphQL APIを呼び出し、PRのタイトル、ボディ、ステータス、コメントなどの詳細情報を取得します。
- **`phase_detector.py`**
    - `detect_pr_phase(pr_data: PullRequest, rulesets: List[Ruleset]) -> PRPhase` (仮称):
        - **役割**: プルリクエストのデータに基づいて、現在のフェーズ（phase1, 2, 3, LLM working）を判定します。
        - **機能**: PRのドラフト状態、レビューリクエスト、特定のコメントの有無などを確認し、定義されたルールに基づいてフェーズを決定します。
- **`pr_actions.py`**
    - `mark_pr_ready_for_review(github_client: GitHubClient, pr_id: str)` (仮称):
        - **役割**: 指定されたプルリクエストをドラフト状態からレビュー可能状態に切り替えます。
        - **機能**: GitHub APIを呼び出してPRのステータスを変更します。
    - `merge_pr(github_client: GitHubClient, pr_id: str, comment: str, automation_config: dict)` (仮称):
        - **役割**: 指定されたプルリクエストをマージし、必要に応じて自動ブラウザ操作でマージボタンをクリックします。
        - **機能**: GitHub APIでマージを実行、または`browser_automation.py`の関数を呼び出しブラウザを操作します。
- **`comment_manager.py`**
    - `post_comment(github_client: GitHubClient, pr_id: str, body: str)` (仮称):
        - **役割**: 指定されたプルリクエストにコメントを投稿します。
        - **機能**: GitHub APIを呼び出してコメントを作成します。
    - `check_for_specific_comment(github_client: GitHubClient, pr_id: str, keyword: str) -> bool` (仮称):
        - **役割**: PRのコメント履歴を検索し、特定のキーワードやパターンを含むコメントが存在するかを確認します。
        - **機能**: `comment_fetcher.py`を通じてコメントを取得し、文字列検索を行います。
- **`notifier.py`**
    - `send_ntfy_notification(topic: str, message: str, url: str, priority: int)` (仮称):
        - **役割**: ntfy.shサービスを利用してモバイル端末に通知を送信します。
        - **機能**: ntfy.shのAPIエンドポイントにHTTP POSTリクエストを送信し、PRのURLを含むメッセージを通知します。
- **`browser_automation.py`**
    - `open_pr_in_browser(pr_url: str, browser_config: dict)` (仮称):
        - **役割**: 指定されたPRのURLをウェブブラウザで開きます。
        - **機能**: SeleniumやPlaywrightなどのライブラリを使用してブラウザを起動し、URLにアクセスします。
    - `click_assign_to_copilot_button(issue_url: str, browser_config: dict)` (仮称):
        - **役割**: 指定されたIssueページで「Assign to Copilot」ボタンを自動的にクリックします。
        - **機能**: SeleniumやPlaywrightを使用してブラウザを操作し、特定要素を検索してクリックします。

## 関数呼び出し階層ツリー
```
main.py: run_monitoring_loop()
  ├── config.py: load_config()
  ├── repository_fetcher.py: fetch_user_repositories()
  │   └── github_client.py: execute_graphql_query()
  │       └── graphql_client.py: run_query()
  ├── pr_fetcher.py: fetch_open_pull_requests()
  │   └── github_client.py: execute_graphql_query()
  │       └── graphql_client.py: run_query()
  ├── phase_detector.py: detect_pr_phase()
  ├── pr_actions.py: mark_pr_ready_for_review()
  │   └── github_client.py: execute_graphql_mutation()
  │       └── graphql_client.py: run_mutation()
  ├── pr_actions.py: post_action_comment()  (※実体はcomment_managerが担当)
  │   └── comment_manager.py: post_comment()
  │       └── github_client.py: execute_graphql_mutation()
  │           └── graphql_client.py: run_mutation()
  ├── pr_actions.py: merge_pr()
  │   ├── github_client.py: execute_graphql_mutation()
  │   │   └── graphql_client.py: run_mutation()
  │   └── browser_automation.py: click_merge_button() (仮称)
  ├── notifier.py: send_ntfy_notification()
  │   └── (requests.postなどのHTTPクライアントライブラリ)
  ├── issue_fetcher.py: fetch_top_issues() (※全PRがLLM workingの場合に呼び出し)
  │   └── github_client.py: execute_graphql_query()
  │       └── graphql_client.py: run_query()
  └── browser_automation.py: open_pr_in_browser()

---
Generated at: 2026-01-09 07:02:12 JST
