Last updated: 2026-01-16

# Project Overview

## プロジェクト概要
- GitHub Copilotが自動生成するPull Requestのフェーズを監視し、その状態に応じたアクションを自動化するPythonツールです。
- 認証済みGitHubユーザーのリポジトリを対象に、GraphQL APIを用いて効率的にPRのドラフト、レビュー待ち、作業中などのフェーズを判定します。
- 必要に応じて通知、コメント投稿、PRのReady化、自動マージ、Issue割り当てといった処理を安全なドライランモードと実行モードで提供します。

## 技術スタック
- フロントエンド: CLIベースのアプリケーションのため特定のフレームワークは使用していません。ブラウザ自動化に`PyAutoGUI`を使用し、GUI操作を模倣します。
- 音楽・オーディオ: 該当する技術は使用していません。
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHub認証およびAPI操作のためのコマンドラインツール。
    - **pytest**: Pythonアプリケーションのテストフレームワーク。
- ビルドツール: Pythonの標準的な実行環境を使用しており、特定のビルドツールは使用していません。依存関係は`pip`で管理されます。
- 言語機能:
    - **Python 3.x**: プロジェクトの主要なプログラミング言語。
    - **GraphQL**: GitHub APIとの効率的なデータ取得に利用されるクエリ言語。
    - **TOML**: 設定ファイル（`config.toml`）の記述に用いられるシンプルな設定ファイル形式。
- 自動化・CI/CD:
    - **ntfy.sh**: モバイルデバイスへのプッシュ通知を送信するためのサービス。
    - **PyAutoGUI**: マウスやキーボードの操作を自動化し、ブラウザ上でのボタンクリックなどを実行。
    - **GitHub Actions**: READMEの自動翻訳など、CI/CDの一部機能に利用。
- 開発標準:
    - **ruff**: 高速なPythonリンターおよびフォーマッター。
    - **.editorconfig**: 異なるエディタやIDE間で一貫したコーディングスタイルを維持するための設定ファイル。

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

-   **`.editorconfig`**: 各エディタがこのプロジェクトで推奨されるコーディングスタイル（インデント、改行コードなど）を使用するように設定します。
-   **`.gitignore`**: Gitが追跡しないファイルやディレクトリ（例: ログファイル、キャッシュ、Pythonのバイトコード）を指定します。
-   **`.vscode/settings.json`**: Visual Studio Code用のワークスペース設定ファイル。特定の拡張機能の設定や、Pythonパスの指定などを含みます。
-   **`LICENSE`**: プロジェクトのライセンス情報（MIT License）が記載されています。
-   **`MERGE_CONFIGURATION_EXAMPLES.md`**: マージに関する設定例や利用方法が記載されたドキュメント。
-   **`PHASE3_MERGE_IMPLEMENTATION.md`**: Phase3におけるPR自動マージ機能の実装詳細に関するドキュメント。
-   **`README.ja.md`**: プロジェクトの日本語版説明書。
-   **`README.md`**: プロジェクトの英語版説明書。
-   **`STRUCTURE.md`**: プロジェクトの全体的な構造や設計に関するドキュメント。
-   **`_config.yml`**: おそらくGitHub Pagesなどの静的サイトジェネレータで使用される設定ファイル。
-   **`cat-github-watcher.py`**: プロジェクトの主要なエントリーポイント。このスクリプトを実行することで、監視ツールが起動します。
-   **`config.toml.example`**: ユーザーが設定を行うための`config.toml`ファイルのサンプル。監視間隔、通知設定、自動化ルールなどが記述されています。
-   **`demo_automation.py`**: ブラウザ自動化機能のデモンストレーション用スクリプト。
-   **`docs/`**: プロジェクトに関する追加のドキュメントが格納されているディレクトリ。
    -   **`IMPLEMENTATION_SUMMARY.ja.md`**: 実装概要の日本語版。
    -   **`IMPLEMENTATION_SUMMARY.md`**: 実装概要の英語版。
    -   **`PR67_IMPLEMENTATION.md`**: 特定のPull Request (PR #67) の実装に関する詳細ドキュメント。
    -   **`RULESETS.md`**: `rulesets`機能の詳細な説明ドキュメント。
    -   **`VERIFICATION_GUIDE.en.md`**: 検証ガイドの英語版。
    -   **`VERIFICATION_GUIDE.md`**: 検証ガイドの日本語版。
    -   **`browser-automation-approaches.en.md`**: ブラウザ自動化のアプローチに関する英語版ドキュメント。
    -   **`browser-automation-approaches.md`**: ブラウザ自動化のアプローチに関する日本語版ドキュメント。
-   **`generated-docs/`**: 自動生成されたドキュメントが格納される可能性のあるディレクトリ。
-   **`pytest.ini`**: `pytest`テストランナーの設定ファイル。
-   **`requirements-automation.txt`**: `PyAutoGUI`など、ブラウザ自動化機能を使用するために必要なPythonライブラリをリストアップしたファイル。
-   **`ruff.toml`**: `ruff`リンター/フォーマッターの設定ファイル。コード品質とスタイルを維持するために使用されます。
-   **`screenshots/`**: ブラウザ自動化で使用されるボタンのスクリーンショット画像（例: `assign.png`, `assign_to_copilot.png`）を格納するディレクトリ。
-   **`src/gh_pr_phase_monitor/__init__.py`**: Pythonパッケージとして`gh_pr_phase_monitor`ディレクトリを認識させるためのファイル。
-   **`src/gh_pr_phase_monitor/browser_automation.py`**: `PyAutoGUI`ライブラリを使用して、Webブラウザ上の特定のボタン（マージボタン、アサインボタンなど）をクリックするなどのGUI操作を自動化する機能を提供します。
-   **`src/gh_pr_phase_monitor/colors.py`**: ターミナル出力に色を付けるためのANSIエスケープコードを定義し、ログの視認性を向上させます。
-   **`src/gh_pr_phase_monitor/comment_fetcher.py`**: GitHub APIを通じてPRのコメントを取得する機能を提供します。
-   **`src/gh_pr_phase_monitor/comment_manager.py`**: GitHub PRにコメントを投稿したり、既存のコメントを確認したりするロジックを管理します。
-   **`src/gh_pr_phase_monitor/config.py`**: `config.toml`ファイルから設定を読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトとして提供します。設定のバリデーションも行います。
-   **`src/gh_pr_phase_monitor/github_auth.py`**: GitHub CLI (`gh`) を利用して、GitHub認証トークンを取得・管理する機能を提供します。
-   **`src/gh_pr_phase_monitor/github_client.py`**: GitHubのGraphQL APIと連携し、クエリの実行やデータ取得を担当する高レベルなインターフェースを提供します。
-   **`src/gh_pr_phase_monitor/graphql_client.py`**: 汎用的なGraphQLクライアントとして機能し、GitHub APIへのリクエストを構築し実行します。
-   **`src/gh_pr_phase_monitor/issue_fetcher.py`**: GitHubリポジトリからIssue情報を取得する機能を提供します。
-   **`src/gh_pr_phase_monitor/main.py`**: メインの監視ループと、各モジュールを連携させてPRの監視とアクション実行を行う主要なロジックを管理します。`cat-github-watcher.py`から呼び出されます。
-   **`src/gh_pr_phase_monitor/notifier.py`**: `ntfy.sh`サービスを通じて、PRのステータス変更などをモバイルデバイスに通知する機能を提供します。
-   **`src/gh_pr_phase_monitor/phase_detector.py`**: Pull Requestの状態（Draft、レビュー指摘対応中、レビュー待ち、LLM working）を判定するコアロジックを実装しています。
-   **`src/gh_pr_phase_monitor/pr_actions.py`**: PRをReady状態に変更する、ブラウザでPRページを開く、自動マージを実行する、といった具体的なPRに対するアクションを定義・実行します。
-   **`src/gh_pr_phase_monitor/pr_fetcher.py`**: GitHubリポジトリからPull Requestのリストや詳細情報を取得する機能を提供します。
-   **`src/gh_pr_phase_monitor/repository_fetcher.py`**: 認証済みユーザーが所有するリポジトリの一覧を取得する機能を提供します。
-   **`tests/`**: プロジェクトのテストコードが格納されているディレクトリ。各モジュールや機能の単体テスト、結合テストが含まれます。

## 関数詳細説明

このプロジェクトはモジュール化されており、各ファイルが特定の役割を持つ関数群を提供します。具体的な関数名はコードに依存しますが、ここでは各モジュールが提供する主要な機能について抽象的に説明します。

-   **`main.py`**
    -   **`run_monitor()`**: メインの監視ループを開始・管理します。設定された間隔でGitHub APIを呼び出し、PRの状態をチェックし、必要に応じてアクションをトリガーします。引数として設定オブジェクトを受け取ります。
    -   **`display_status_summary()`**: 現在監視しているPRやリポジトリのステータスをコンソールに表示します。
-   **`config.py`**
    -   **`load_config(path: str) -> Config`**: 指定されたパスから`config.toml`ファイルを読み込み、解析して設定オブジェクトを返します。設定のバリデーションも行います。
    -   **`parse_interval(interval_str: str) -> int`**: "1m", "30s"のような文字列形式の時間間隔を秒単位の整数に変換します。
-   **`github_client.py`**
    -   **`query_github_api(query: str, variables: Dict) -> Dict`**: GitHub GraphQL APIにクエリを送信し、その結果を返します。
    -   **`get_user_repositories() -> List[Repository]`**: 認証ユーザーが所有するリポジトリのリストを取得します。
    -   **`get_pull_requests(repo_id: str) -> List[PullRequest]`**: 指定されたリポジトリのオープンなPRのリストを取得します。
    -   **`post_comment(pr_id: str, body: str)`**: 指定されたPRにコメントを投稿します。
-   **`phase_detector.py`**
    -   **`detect_phase(pr: PullRequest) -> Phase`**: Pull Requestオブジェクトの情報を解析し、そのPRがどのフェーズ（phase1, phase2, phase3, LLM working）にあるかを判定し、対応するフェーズを返します。
-   **`comment_manager.py`**
    -   **`post_phase2_comment(pr_id: str)`**: phase2（レビュー指摘対応中）のPRに対して、Copilotに変更適用を促すコメントを投稿します。
    -   **`has_specific_comment(pr_id: str, keyword: str) -> bool`**: 特定のキーワードを含むコメントがPRに存在するかどうかを確認します。
-   **`pr_actions.py`**
    -   **`mark_pr_ready_for_review(pr_id: str)`**: Draft状態のPRをReady状態に変更します。
    -   **`open_pr_in_browser(pr_url: str)`**: 指定されたURLのPRをデフォルトブラウザで開きます。
    -   **`merge_pull_request(pr_id: str, comment: str, automated: bool)`**: PRをマージします。`automated`が`True`の場合はブラウザ自動化を利用します。
-   **`notifier.py`**
    -   **`send_ntfy_notification(topic: str, message: str, url: str, priority: int)`**: `ntfy.sh`サービスを通じて、指定されたトピックに通知を送信します。
-   **`browser_automation.py`**
    -   **`click_button_by_image(image_path: str, confidence: float) -> bool`**: `PyAutoGUI`を使用し、スクリーンショット画像に一致する画面上のボタンをクリックします。
    -   **`open_url_and_wait(url: str, wait_seconds: int)`**: 指定されたURLをブラウザで開き、指定秒数待機します。
-   **`issue_fetcher.py`**
    -   **`get_assignable_issues(repo_id: str, limit: int, good_first_issue_only: bool) -> List[Issue]`**: 指定されたリポジトリから割り当て可能なIssueを取得します。`good_first_issue_only`でフィルタリングも可能です。

## 関数呼び出し階層ツリー
```
cat-github-watcher.py (エントリーポイント)
└── src/gh_pr_phase_monitor/main.py (メイン監視ループ)
    ├── src/gh_pr_phase_monitor/config.py (設定の読み込み)
    ├── src/gh_pr_phase_monitor/github_auth.py (GitHub認証)
    ├── src/gh_pr_phase_monitor/repository_fetcher.py (ユーザーリポジトリの取得)
    └── (ループ内で各リポジトリとPRを処理)
        ├── src/gh_pr_phase_monitor/pr_fetcher.py (Pull Requestの取得)
        ├── src/gh_pr_phase_monitor/phase_detector.py (PRフェーズの判定)
        ├── src/gh_pr_phase_monitor/pr_actions.py (PRに対するアクションの実行)
        │   ├── src/gh_pr_phase_monitor/comment_manager.py (コメントの投稿と確認)
        │   │   └── src/gh_pr_phase_monitor/comment_fetcher.py (コメントの取得)
        │   ├── src/gh_pr_phase_monitor/notifier.py (ntfy通知の送信)
        │   └── src/gh_pr_phase_monitor/browser_automation.py (ブラウザ自動操作 - 自動マージ等)
        └── src/gh_pr_phase_monitor/issue_fetcher.py (未解決Issueの取得 - LLM workingフェーズ時)

---
Generated at: 2026-01-16 07:02:03 JST
