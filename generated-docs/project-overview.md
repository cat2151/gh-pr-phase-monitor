Last updated: 2026-01-14

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装PRのフェーズを効率的に監視するPythonツールです。
- ユーザー所有リポジトリを対象に、GraphQL APIでPRの状態（Draft、レビュー指摘対応中、レビュー待ち、LLM作業中）を自動判定します。
- フェーズに応じたコメント投稿、PRのReady化、モバイル通知、issue表示、自動マージなどのアクションを実行できます。

## 技術スタック
- フロントエンド: なし（ブラウザ自動化として分離）
- 音楽・オーディオ: なし
- 開発ツール:
    - **Python 3.x**: このツールの主要な開発言語です。
    - **GitHub CLI (`gh`)**: GitHubへの認証とAPI連携のために使用されます。
    - **pytest**: プロジェクトのテストスイートを構築するためのPythonテストフレームワークです。
    - **Ruff**: Pythonコードのリンティングとフォーマットに使用され、コード品質と一貫性を保ちます。
- テスト:
    - **pytest**: Pythonアプリケーションの単体テスト、結合テストを記述・実行するためのフレームワークです。
- ビルドツール: なし（Pythonプロジェクトのため、通常は明示的なビルドプロセスはありません）
- 言語機能:
    - **Python**: 高レベルで汎用的なプログラミング言語。
    - **GraphQL API**: GitHub APIと連携し、効率的にプルリクエストやリポジトリのデータを取得するために使用されます。
- 自動化・CI/CD:
    - **ntfy.sh**: プルリクエストの特定フェーズ（レビュー待ちなど）をモバイルデバイスに通知するために利用される、シンプルなプッシュ通知サービスです。
- 開発標準:
    - **EditorConfig**: 異なる開発環境間でのコードスタイルを統一するための設定ファイルです。
    - **Ruff**: コードの品質とスタイルを自動でチェック・修正し、開発標準を維持します。
- ブラウザ自動化:
    - **Selenium**: Webブラウザを自動操作するためのフレームワークで、自動マージやissue割り当てなどの機能に使用されます。
    - **Playwright**: Microsoftが開発した、Webブラウザを自動化するためのライブラリで、Seleniumの代替として利用可能です。
    - **PyAutoGUI**: GUIをプログラムで制御するためのPythonライブラリで、画面上のボタン画像認識とクリックに使用されます。

## ファイル階層ツリー
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
├── screenshots/
│   ├── assign.png
│   └── assign_to_copilot.png
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
    ├── test_batteries_included_defaults.py
    ├── test_browser_automation.py
    ├── test_check_process_before_autoraise.py
    ├── test_config_rulesets.py
    ├── test_config_rulesets_features.py
    ├── test_elapsed_time_display.py
    ├── test_hot_reload.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_parsing.py
    ├── test_issue_fetching.py
    ├── test_max_llm_working_parallel.py
    ├── test_no_change_timeout.py
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

-   `.editorconfig`: 異なる開発環境間でのコードスタイルを統一するための設定ファイルです。
-   `.gitignore`: Gitによってバージョン管理されるべきではないファイルやディレクトリを指定します。
-   `.vscode/settings.json`: VS Codeエディタ固有の設定を定義し、プロジェクト開発環境を標準化します。
-   `LICENSE`: プロジェクトのライセンス情報（MIT License）を記述しています。
-   `MERGE_CONFIGURATION_EXAMPLES.md`: PR自動マージ機能の設定例と説明が記述されています。
-   `PHASE3_MERGE_IMPLEMENTATION.md`: PRのPhase3における自動マージ機能の実装詳細が記述されています。
-   `README.ja.md`: プロジェクトの日本語版概要、使い方、機能などの情報が記述されています。
-   `README.md`: プロジェクトの英語版概要、使い方、機能などの情報が記述されています。
-   `STRUCTURE.md`: プロジェクトの構造に関する追加情報が記述されています。
-   `_config.yml`: GitHub Pagesなどの静的サイトジェネレータの設定ファイルとして利用される可能性があります。
-   `cat-github-watcher.py`: プロジェクトのエントリーポイントとなるスクリプトで、メインの監視プロセスを起動します。
-   `config.toml.example`: ユーザーがカスタマイズできる設定ファイルのテンプレートです。
-   `demo_automation.py`: 自動化機能（ブラウザ操作など）のデモンストレーションやテストに使用されるスクリプトです。
-   `docs/`: プロジェクトに関する様々なドキュメントを格納するディレクトリです。
    -   `IMPLEMENTATION_SUMMARY.ja.md`: 実装概要の日本語版です。
    -   `IMPLEMENTATION_SUMMARY.md`: 実装概要の英語版です。
    -   `PR67_IMPLEMENTATION.md`: 特定のプルリクエスト（PR67）に関する実装詳細です。
    -   `RULESETS.md`: プロジェクト内のルールセット設定に関する詳細情報です。
    -   `VERIFICATION_GUIDE.en.md`: 検証ガイドの英語版です。
    -   `VERIFICATION_GUIDE.md`: 検証ガイドの日本語版です。
    -   `browser-automation-approaches.en.md`: ブラウザ自動化アプローチに関する英語版ドキュメントです。
    -   `browser-automation-approaches.md`: ブラウザ自動化アプローチに関する日本語版ドキュメントです。
-   `generated-docs/`: AI生成されたドキュメントやその他自動生成されたファイルを格納するディレクトリです。
-   `pytest.ini`: pytestテストフレームワークの設定ファイルです。
-   `requirements-automation.txt`: ブラウザ自動化機能に必要なPythonライブラリの依存関係がリストされています。
-   `ruff.toml`: Ruffリンター/フォーマッターの設定ファイルです。
-   `screenshots/`: ブラウザ自動化機能（PyAutoGUI）で使用されるボタンのスクリーンショット画像ファイルを格納します。
    -   `assign.png`: "Assign"ボタンのスクリーンショット。
    -   `assign_to_copilot.png`: "Assign to Copilot"ボタンのスクリーンショット。
-   `src/gh_pr_phase_monitor/`: プロジェクトの主要なPythonモジュールとロジックを格納するパッケージです。
    -   `__init__.py`: Pythonパッケージであることを示します。
    -   `browser_automation.py`: Selenium、Playwright、PyAutoGUIを用いたブラウザ自動操縦のロジックを含みます。
    -   `colors.py`: ターミナル出力にANSIカラーコードを適用するためのユーティリティ関数を提供します。
    -   `comment_fetcher.py`: GitHubのプルリクエストコメントを取得するための機能を提供します。
    -   `comment_manager.py`: プルリクエストへのコメント投稿や、既存コメントの確認に関するロジックを管理します。
    -   `config.py`: `config.toml`ファイルから設定を読み込み、解析するための機能を提供します。
    -   `github_auth.py`: GitHub CLI (`gh`) を使用してGitHub APIへの認証を行う機能を提供します。
    -   `github_client.py`: GitHub API (RESTおよびGraphQL) との連携を抽象化し、データ取得やアクション実行のための共通インターフェースを提供します。
    -   `graphql_client.py`: GitHubのGraphQL APIに対してクエリを実行するための低レベルなクライアント機能を提供します。
    -   `issue_fetcher.py`: GitHubリポジトリからissue情報を取得する機能を提供します。
    -   `main.py`: プログラムのメイン実行ループと、プルリクエスト監視のオーケストレーションを管理します。
    -   `notifier.py`: ntfy.shサービスを利用してモバイル通知を送信する機能を提供します。
    -   `phase_detector.py`: プルリクエストの現在の状態を分析し、対応するフェーズ（例: Draft, レビュー待ち）を判定するロジックを実装します。
    -   `pr_actions.py`: プルリクエストをReady状態にする、ブラウザで開く、自動マージするなどの特定のアクションを実行します。
    -   `pr_fetcher.py`: 指定されたリポジトリからプルリクエストのリストと詳細情報を取得します。
    -   `repository_fetcher.py`: 認証済みユーザーが所有するGitHubリポジトリのリストを取得します。
-   `tests/`: プロジェクトの各種機能に対するpytestテストファイルが含まれています。

## 関数詳細説明

本プロジェクトでは、各モジュールが単一責任の原則に基づいて設計されており、以下のような主要な役割を持つ関数群で構成されています。具体的な引数や戻り値は、実装によって多岐にわたりますが、ここではその主な機能に焦点を当てて説明します。

-   **監視ループ管理関数**:
    -   `main.py` に含まれる関数群は、GitHubリポジトリとPRを定期的に監視するためのメインループを構築し、他のモジュールからの情報を統合してアクションを決定します。省電力モードやverboseモードの制御も行います。
-   **設定読み込み・解析関数**:
    -   `config.py` に含まれる関数群は、`config.toml` ファイルを読み込み、プロジェクト全体の設定やリポジトリごとのルールセットを解析して、プログラムで利用可能な形式に変換します。
-   **GitHubデータ取得関数**:
    -   `github_client.py`, `graphql_client.py`, `repository_fetcher.py`, `pr_fetcher.py`, `issue_fetcher.py`, `comment_fetcher.py` に含まれる関数群は、GitHub API (GraphQLを中心に) を利用して、ユーザーのリポジトリ、プルリクエスト、issue、コメントなどの各種情報を効率的に取得します。
-   **認証関連関数**:
    -   `github_auth.py` に含まれる関数群は、`gh` CLIツールを介してGitHubへの認証を行い、APIアクセスのためのトークン管理などを行います。
-   **フェーズ判定関数**:
    -   `phase_detector.py` に含まれる関数群は、取得したプルリクエストのステータス、ドラフト状態、レビューコメントなどを分析し、そのPRがどのフェーズ（phase1, phase2, phase3, LLM working）にあるかを正確に判定します。
-   **アクション実行関数**:
    -   `pr_actions.py`, `comment_manager.py` に含まれる関数群は、判定されたフェーズに基づいて様々なアクションを実行します。具体的には、PRのReady状態への変更、特定のコメントの投稿、PRの自動マージ、ブラウザでPRページを開くなどが含まれます。
-   **通知関数**:
    -   `notifier.py` に含まれる関数群は、ntfy.shサービスを利用して、PRが特定のフェーズに達した際にモバイルデバイスへ通知を送信します。
-   **ブラウザ自動化関数**:
    -   `browser_automation.py` に含まれる関数群は、Selenium、Playwright、PyAutoGUIといったツールを活用し、GitHubのWebインターフェースを自動的に操作して、issueの自動割り当てやPRの自動マージなどのタスクを実行します。
-   **ユーティリティ関数**:
    -   `colors.py` などに含まれる関数は、ターミナル出力の視認性を高めるために、テキストに色を付けるなどの補助的な機能を提供します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層は提供されたプロジェクト情報から詳細に分析できませんでした。
しかし、プロジェクトの主要な実行フローは `src/gh_pr_phase_monitor/main.py` に集約されており、
そこから `config.py` (設定読み込み), `github_client.py` (API連携), `repository_fetcher.py` (リポジトリ取得),
`pr_fetcher.py` (PR取得), `phase_detector.py` (フェーズ判定), `pr_actions.py` (アクション実行),
`comment_manager.py` (コメント管理), `notifier.py` (通知), `browser_automation.py` (ブラウザ自動化) など、
各モジュールの機能が協調して呼び出される構造となっています。

---
Generated at: 2026-01-14 07:02:21 JST
