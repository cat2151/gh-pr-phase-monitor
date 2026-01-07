Last updated: 2026-01-08

# Project Overview

## プロジェクト概要
- GitHub Copilotが関与するPull Requestの自動実装フェーズを監視し、進行状況を可視化するツールです。
- PRのフェーズ（Draft、レビュー指摘対応中、レビュー待ちなど）を自動判定し、状況に応じた通知やアクションを実行します。
- 認証済みGitHubユーザーの全リポジトリを対象にGraphQL APIで効率的に監視を行い、開発ワークフローを支援します。

## 技術スタック
- フロントエンド: (本プロジェクトはCUIベースであり、GUIとしてのフロントエンド技術は使用していません。ブラウザ自動操縦は後述の「自動化・CI/CD」に分類されます。)
- 音楽・オーディオ: (本プロジェクトは音楽・オーディオ関連の機能を提供していません。)
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHub認証やAPI操作の基盤として利用されます。
    - **Git**: ソースコードのバージョン管理に使用されます。
    - **Visual Studio Code (.vscode/settings.json)**: 開発環境としてVisual Studio Codeが使用され、その設定ファイルが含まれています。
- テスト:
    - **pytest**: Pythonアプリケーションのテストフレームワークとして利用され、機能テストを記述・実行します。
- ビルドツール: (Pythonスクリプトであるため、専用のビルドツールは使用していません。)
- 言語機能:
    - **Python 3.x**: プロジェクトの主要な実装言語です。
    - **TOML**: 設定ファイル（`config.toml`）の記述形式として使用されます。
- 自動化・CI/CD:
    - **ntfy.sh**: モバイル端末への通知送信サービスとして利用されます。
    - **Selenium**: ブラウザ自動操縦のバックエンドとして、PRのマージボタンクリックなどの自動化アクションに利用されます。
    - **Playwright**: Seleniumと同様に、ブラウザ自動操縦のバックエンドとして利用可能です。
    - **GitHub Actions**: READMEの翻訳など、一部のドキュメント生成プロセスで自動化に利用されています。
- 開発標準:
    - **Ruff**: Pythonコードの整形とリンティング（構文チェック、スタイルガイド準拠）に使用されます。
    - **.editorconfig**: 異なるエディタやIDE間でのコードスタイルの統一を支援します。
    - **Markdown**: プロジェクトドキュメント（README、ガイド、説明ファイルなど）の記述形式として広く使用されています。

## ファイル階層ツリー
```
cat-github-watcher/
├── cat-github-watcher.py    # エントリーポイント
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py         # ANSI カラーコードと色付け
│       ├── config.py         # 設定の読み込みと解析
│       ├── github_client.py  # GitHub API 連携
│       ├── phase_detector.py # PRフェーズ判定ロジック
│       ├── comment_manager.py # コメント投稿と確認
│       ├── pr_actions.py     # PRアクション（Ready化、ブラウザ起動）
│       └── main.py           # メイン実行ループ
└── tests/                    # テストファイル
```

## ファイル詳細説明

*   **.editorconfig**: プロジェクト全体のコードスタイル（インデント、改行コードなど）を定義し、異なるエディタ間での一貫性を保ちます。
*   **.gitignore**: Gitのバージョン管理から除外するファイルやディレクトリを指定します。
*   **.vscode/settings.json**: Visual Studio Codeのワークスペース固有の設定を定義し、開発環境を統一します。
*   **LICENSE**: プロジェクトのライセンス情報（MIT License）が記述されています。
*   **MERGE_CONFIGURATION_EXAMPLES.md**: マージ設定に関する具体的な使用例が記載されたドキュメントです。
*   **PHASE3_MERGE_IMPLEMENTATION.md**: Phase3での自動マージ機能の実装詳細について説明するドキュメントです。
*   **README.ja.md**: プロジェクトの概要、特徴、使い方などが日本語で記述されたメインドキュメントです。
*   **README.md**: プロジェクトの概要、特徴、使い方などが英語で記述されたメインドキュメントです。
*   **STRUCTURE.md**: プロジェクトの構造や設計に関する概要が記述されたドキュメントです。
*   **_config.yml**: Jekyllなどの静的サイトジェネレータで使用される設定ファイルで、ドキュメントサイトの構築に利用される可能性があります。
*   **cat-github-watcher.py**: プロジェクトのトップレベルのエントリーポイントとなるスクリプトで、監視ツールを起動します。
*   **config.toml.example**: ユーザーが設定を行うための`config.toml`ファイルのテンプレートです。
*   **demo_automation.py**: ブラウザ自動操縦機能のデモンストレーションを行うスクリプトです。
*   **demo_comparison.py**: 異なる機能やアプローチの比較デモンストレーションを行うスクリプトです。
*   **docs/**: プロジェクトに関する追加ドキュメントが格納されているディレクトリです。
    *   **IMPLEMENTATION_SUMMARY.ja.md**: 実装の概要を日本語でまとめたドキュメントです。
    *   **IMPLEMENTATION_SUMMARY.md**: 実装の概要を英語でまとめたドキュメントです。
    *   **PR67_IMPLEMENTATION.md**: 特定のプルリクエスト（PR67）に関連する実装の詳細を記述したドキュメントです。
    *   **RULESETS.md**: ルールセットの設定と機能について説明するドキュメントです。
    *   **VERIFICATION_GUIDE.en.md**: 検証ガイドの英語版です。
    *   **VERIFICATION_GUIDE.md**: 機能の検証方法を説明するドキュメントです。
    *   **browser-automation-approaches.en.md**: ブラウザ自動操縦のアプローチに関する英語のドキュメントです。
    *   **browser-automation-approaches.md**: ブラウザ自動操縦のアプローチに関するドキュメントです。
*   **generated-docs/**: 自動生成されたドキュメントが格納されるディレクトリです。
*   **pytest.ini**: pytestの設定ファイルで、テストの実行方法やオプションを定義します。
*   **requirements-automation.txt**: ブラウザ自動操縦（Seleniumなど）に必要なPythonパッケージのリストです。
*   **ruff.toml**: Pythonコードリンター「Ruff」の設定ファイルです。
*   **src/**: プロジェクトの主要なソースコードが格納されているディレクトリです。
    *   **gh_pr_phase_monitor/**: GitHub Pull Request監視ロジックのコア部分が格納されているパッケージです。
        *   **\_\_init\_\_.py**: Pythonパッケージであることを示すファイルです。
        *   **browser_automation.py**: SeleniumやPlaywrightを用いたブラウザ自動操縦に関する機能を提供します。
        *   **colors.py**: コンソール出力にANSIカラーコードを適用し、視認性を向上させる機能を提供します。
        *   **comment_fetcher.py**: GitHub Pull Requestのコメント情報を取得する機能を提供します。
        *   **comment_manager.py**: Pull Requestに対するコメントの投稿や管理を行う機能を提供します。
        *   **config.py**: `config.toml`ファイルから設定を読み込み、解析する機能を提供します。
        *   **github_auth.py**: GitHub APIへの認証処理を管理する機能を提供します。
        *   **github_client.py**: GitHub API（RESTまたはGraphQL）と連携するための高レベルなクライアント機能を提供します。
        *   **graphql_client.py**: GitHub GraphQL APIに特化したクエリ実行機能を提供します。
        *   **issue_fetcher.py**: GitHub Issueの情報を取得する機能を提供します。
        *   **main.py**: 監視ツールのメイン実行ループを含み、各モジュールを連携させて監視処理を統括します。
        *   **notifier.py**: ntfy.shなどのサービスを利用して通知を送信する機能を提供します。
        *   **phase_detector.py**: Pull Requestの状態に基づいてフェーズ（Phase1, Phase2, Phase3, LLM working）を判定するロジックを提供します。
        *   **pr_actions.py**: Pull RequestをReady状態にする、ブラウザで開く、自動マージするなどのアクションを実行する機能を提供します。
        *   **pr_fetcher.py**: GitHubからPull Requestのリストや詳細情報を取得する機能を提供します。
        *   **repository_fetcher.py**: 認証済みユーザーが所有するGitHubリポジトリの情報を取得する機能を提供します。
*   **tests/**: プロジェクトのテストスクリプトが格納されているディレクトリです。各ファイルは特定の機能やコンポーネントのテストを担当します。
    *   **test_all_phase3_timeout.py**: Phase3のタイムアウトに関連するテストです。
    *   **test_browser_automation.py**: ブラウザ自動操縦機能のテストです。
    *   **test_config_rulesets.py**: 設定ファイルのルールセット機能のテストです。
    *   **test_config_rulesets_features.py**: ルールセット機能の特定のフィーチャーに関するテストです。
    *   **test_elapsed_time_display.py**: 経過時間表示機能のテストです。
    *   **test_hot_reload.py**: 設定のホットリロード機能のテストです。
    *   **test_integration_issue_fetching.py**: Issue取得の統合テストです。
    *   **test_interval_parsing.py**: 監視間隔の解析機能のテストです。
    *   **test_issue_fetching.py**: Issue取得機能のテストです。
    *   **test_no_open_prs_issue_display.py**: オープンPRがない場合 इश्यू表示機能のテストです。
    *   **test_notification.py**: 通知機能のテストです。
    *   **test_phase3_merge.py**: Phase3での自動マージ機能のテストです。
    *   **test_phase_detection.py**: PRフェーズ判定機能のテストです。
    *   **test_post_comment.py**: コメント投稿機能のテストです。
    *   **test_post_phase3_comment.py**: Phase3でのコメント投稿機能のテストです。
    *   **test_pr_actions.py**: PRアクション機能のテストです。
    *   **test_pr_actions_rulesets_features.py**: ルールセットにおけるPRアクションのテストです。
    *   **test_pr_actions_with_rulesets.py**: ルールセットを適用したPRアクションのテストです。
    *   **test_status_summary.py**: ステータスサマリー表示機能のテストです。
    *   **test_verbose_config.py**: verbose設定のテストです。

## 関数詳細説明
提供されたプロジェクト情報からは、具体的な関数名、引数、戻り値の詳細は特定できませんでした。しかし、上記「ファイル詳細説明」で述べた各モジュールの役割に基づき、それぞれのファイルが提供するであろう主要な機能について説明します。これらの機能は、各モジュール内の関数群によって実現されています。

*   **cat-github-watcher.py**:
    *   役割: 監視ツールの初期化とメイン処理の開始。
    *   機能: 設定ファイルの読み込み、監視ループの起動、エラーハンドリングなどのエントリーポイントとしての機能を提供します。
*   **src/gh_pr_phase_monitor/browser_automation.py**:
    *   役割: Webブラウザをプログラム的に操作するための機能。
    *   機能: SeleniumやPlaywrightを用いて、指定されたURLのブラウザを開く、特定の要素をクリックするなどの自動操縦操作を提供します。
*   **src/gh_pr_phase_monitor/colors.py**:
    *   役割: コンソール出力に色を付けるためのユーティリティ機能。
    *   機能: ANSIエスケープシーケンスを使用して、テキストの色付けやスタイル変更を行う関数群を提供します。
*   **src/gh_pr_phase_monitor/comment_fetcher.py**:
    *   役割: GitHub Pull Requestのコメントを取得する機能。
    *   機能: 特定のPull Requestに関連するコメント（特にCopilotエージェントからのレビューコメントなど）をAPI経由で取得します。
*   **src/gh_pr_phase_monitor/comment_manager.py**:
    *   役割: GitHub Pull Requestにコメントを投稿・管理する機能。
    *   機能: 特定のフェーズ（例: Phase2）に達した際に、定義済みのコメントをPull Requestに投稿します。
*   **src/gh_pr_phase_monitor/config.py**:
    *   役割: プロジェクトの設定を読み込み、解析する機能。
    *   機能: `config.toml`ファイルから監視間隔、実行フラグ、通知設定、自動マージ設定などを読み込み、アプリケーションが利用可能な形式で提供します。
*   **src/gh_pr_phase_monitor/github_auth.py**:
    *   役割: GitHub APIへの認証を管理する機能。
    *   機能: GitHub CLI (`gh`) を利用して認証トークンを取得・管理し、APIリクエストに必要な認証情報を提供します。
*   **src/gh_pr_phase_monitor/github_client.py**:
    *   役割: GitHub APIとの高レベルな連携機能。
    *   機能: GraphQLクライアントや認証機能を活用し、リポジトリ、Pull Request、Issueなどの情報を一貫したインターフェースで取得・操作する基盤を提供します。
*   **src/gh_pr_phase_monitor/graphql_client.py**:
    *   役割: GitHub GraphQL APIに特化したクエリ実行機能。
    *   機能: 定義されたGraphQLクエリをGitHub APIエンドポイントに送信し、その結果を処理する機能を提供します。
*   **src/gh_pr_phase_monitor/issue_fetcher.py**:
    *   役割: GitHub Issue情報を取得する機能。
    *   機能: 特定のリポジトリやユーザーに関連するオープンなIssueのリストや詳細情報を取得します。
*   **src/gh_pr_phase_monitor/main.py**:
    *   役割: 監視ツールのメイン実行ロジック。
    *   機能: 設定された間隔でリポジトリとPull Requestを繰り返しフェッチし、各PRのフェーズを判定し、それに応じたアクション（通知、コメント投稿、PR Ready化、自動マージなど）を実行する監視ループを管理します。
*   **src/gh_pr_phase_monitor/notifier.py**:
    *   役割: 外部サービス（ntfy.sh）を介した通知機能。
    *   機能: 特定のイベント（例: Phase3到達）が発生した際に、設定されたntfy.shトピックにメッセージを送信し、モバイル端末などへ通知します。
*   **src/gh_pr_phase_monitor/phase_detector.py**:
    *   役割: Pull Requestの現在のフェーズを判定するロジック。
    *   機能: PRのドラフト状態、レビューリクエスト、レビューコメントの有無、Copilotエージェントの活動状況などに基づき、Phase1、Phase2、Phase3、LLM workingのいずれかを判定します。
*   **src/gh_pr_phase_monitor/pr_actions.py**:
    *   役割: Pull Requestに対する具体的なアクションを実行する機能。
    *   機能: Draft PRをReady for reviewにする、PRページをブラウザで開く、特定の条件でPRを自動マージするなどの操作を提供します。
*   **src/gh_pr_phase_monitor/pr_fetcher.py**:
    *   役割: GitHubからPull Requestの情報を取得する機能。
    *   機能: 特定のリポジトリ内のオープンなPull Requestのリストや、個々のPRの詳細（タイトル、状態、レビュー状況など）を取得します。
*   **src/gh_pr_phase_monitor/repository_fetcher.py**:
    *   役割: 認証済みユーザーが所有するGitHubリポジトリの情報を取得する機能。
    *   機能: 監視対象となるユーザー所有リポジトリのリストを取得し、その情報を他のモジュールに提供します。

## 関数呼び出し階層ツリー
```
提供されたプロジェクト情報からは、具体的な関数の呼び出し階層を分析できませんでした。

---
Generated at: 2026-01-08 07:01:59 JST
