Last updated: 2026-01-06

# Project Overview

## プロジェクト概要
- GitHub Copilotが関わるPRのフェーズを自動監視し、適切なタイミングで通知やアクションを実行するPythonツールです。
- 認証済みGitHubユーザーの個人リポジトリを対象に、GraphQL APIを用いて効率的にPRの状態を検出します。
- Dry-runモードやモバイル通知、自動コメント投稿など豊富な機能を備え、AI主導開発のワークフローを支援します。

## 技術スタック
- フロントエンド: 該当なし (本プロジェクトはCUIベースのバックグラウンド監視ツールであり、ユーザーインターフェースとしてのフロントエンド技術は使用していません。)
- 音楽・オーディオ: 該当なし (音楽やオーディオ関連の機能は本プロジェクトの範囲外です。)
- 開発ツール:
    - GitHub CLI (gh): GitHubアカウントの認証やリポジトリ操作をコマンドラインから行うためのツール。プロジェクトがGitHub APIへアクセスする際の認証に利用されます。
    - pytest: Pythonで書かれたテストコードを実行するためのフレームワーク。プロジェクトの各機能が意図通りに動作するか検証するために使用されます。
    - Ruff: Pythonコードのリンティングおよびフォーマットツール。コードの品質、一貫性、保守性を高めるために活用されます。
    - EditorConfig: 異なるIDEやテキストエディタを使用する開発者間で、コーディングスタイル（インデント、改行コードなど）を統一するための設定ファイル形式。
- テスト:
    - pytest: プロジェクトの自動テストスイートの基盤として使用されており、機能の正確性と信頼性を担保します。
- ビルドツール:
    - Python 3.x: プロジェクトの主要な実装言語であり、コードの実行環境を提供します。Pythonスクリプトとして直接実行されるため、特定のビルドプロセスはありません。
- 言語機能:
    - Pythonの標準ライブラリ: ファイル操作、ネットワーク通信（HTTPリクエスト）、データ構造処理など、多様なコア機能に利用されます。
    - TOML: 設定ファイル（`config.toml`）の記述に採用されている、シンプルで人間が読みやすいマークアップ言語です。
    - GraphQL: GitHub APIとの通信において、必要なデータのみを効率的に取得するために使用されるクエリ言語です。
- 自動化・CI/CD:
    - Pythonスクリプトによる自動化: PRの自動監視、フェーズ判定、およびそれに続くアクション（コメント投稿、PRステータス変更、通知）といった一連のワークフローがPythonスクリプトによって自動実行されます。
    - GitHub Actions (過去の検討): かつてPR監視の手段として検討されましたが、現在のプロジェクトではPythonスクリプトによる実装に移行しています。
- 開発標準:
    - Ruff: コードの静的解析と自動整形により、プロジェクト全体で一貫したコーディングスタイルを維持し、潜在的なバグを防ぎます。
    - .editorconfig: プロジェクトに参加する複数の開発者の環境において、コードフォーマットの統一を強制し、マージコンフリクトを減らします。
- その他主要技術:
    - GitHub API (GraphQL): GitHub上のプルリクエスト、リポジトリ、コメントなどの情報を取得し、操作するための主要なインターフェースです。
    - ntfy.sh: モバイルデバイスへプッシュ通知を送信するためのサービス。PRのレビュー準備完了などの重要なイベントをユーザーに通知するために利用されます。
    - Selenium: オプション機能であるブラウザ自動操縦（例: IssueをCopilotに自動割り当て）を実現するために使用されるライブラリ。ウェブブラウザの操作を自動化します。

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

## ファイル詳細説明
- **`.editorconfig`**: コードエディタやIDE間でプロジェクトのコーディングスタイル（インデント、改行コードなど）を統一するための設定ファイルです。
- **`.gitignore`**: Gitバージョン管理システムが無視すべきファイルやディレクトリ（例: ビルド生成物、ログファイル、一時ファイル）を指定するファイルです。
- **`.vscode/settings.json`**: Visual Studio Codeエディタのプロジェクト固有の設定（例: リンターの有効化、フォーマット設定）が記述されています。
- **`cat-github-watcher.py`**: このプロジェクトの主要なエントリーポイントとなるPythonスクリプトです。プログラムの起動時に最初に実行され、監視ロジックを呼び出します。
- **`config.toml.example`**: ユーザーが監視ツールの設定をカスタマイズするためのテンプレートファイルです。監視間隔、各種アクションの有効/無効、通知設定などが含まれます。
- **`demo_automation.py`**: ブラウザ自動操縦機能のデモンストレーションまたはテストに使用される可能性のあるスクリプトです。
- **`demo_comparison.py`**: 異なるアプローチや機能の比較検討に使用される可能性のあるスクリプトです。
- **`docs/`**: プロジェクトに関する詳細なドキュメントが格納されているディレクトリです。
    - **`IMPLEMENTATION_SUMMARY.ja.md`**, **`IMPLEMENTATION_SUMMARY.md`**: プロジェクトの実装概要をまとめたドキュメント（日本語版と英語版）です。
    - **`PR67_IMPLEMENTATION.md`**: 特定のプルリクエスト（PR67）に関する実装の詳細を記述したドキュメントです。
    - **`RULESETS.md`**: プロジェクト内で使用されるルールセットやポリシーに関するドキュメントです。
    - **`VERIFICATION_GUIDE.en.md`**, **`VERIFICATION_GUIDE.md`**: 機能の検証手順を説明するガイドドキュメント（英語版と日本語版）です。
    - **`browser-automation-approaches.en.md`**, **`browser-automation-approaches.md`**: ブラウザ自動化のアプローチや検討事項に関するドキュメント（英語版と日本語版）です。
- **`generated-docs/`**: 自動生成されたドキュメントが格納されることを意図したディレクトリです。
- **`LICENSE`**: プロジェクトのライセンス情報（MIT License）が記載されているファイルです。
- **`pytest.ini`**: pytestテストフレームワークの設定ファイルで、テスト実行時のオプションや振る舞いを定義します。
- **`README.ja.md`**, **`README.md`**: プロジェクトの概要、特徴、セットアップ方法、使い方、注意事項などを説明するメインドキュメント（日本語版と英語版）です。
- **`requirements-automation.txt`**: Seleniumを使ったブラウザ自動操縦機能に必要なPythonライブラリ（`selenium`, `webdriver-manager`など）がリストアップされています。
- **`ruff.toml`**: Pythonリンター/フォーマッターであるRuffの設定ファイルです。コードの静的解析ルールや自動整形ルールが定義されています。
- **`STRUCTURE.md`**: プロジェクトの全体的な構造やアーキテクチャについて詳細に説明するドキュメントです。
- **`src/gh_pr_phase_monitor/`**: プロジェクトの主要なビジネスロジックがモジュールとして整理され、格納されているディレクトリです。
    - **`__init__.py`**: Pythonパッケージであることを示すファイルです。
    - **`browser_automation.py`**: Seleniumライブラリを用いて、ウェブブラウザを自動的に操作する機能を提供します。特定のボタンのクリックなどを自動化するために使用されます。
    - **`colors.py`**: ターミナル出力にANSIカラーコードを適用し、ログやメッセージの視認性を高めるためのユーティリティ関数を提供します。
    - **`comment_fetcher.py`**: GitHubのプルリクエストからコメントを効率的に取得するロジックを実装しています。
    - **`comment_manager.py`**: プルリクエストに対してコメントを投稿したり、既存のコメントを管理したりする機能を提供します。
    - **`config.py`**: `config.toml`ファイルから設定を読み込み、解析し、アプリケーション全体で利用可能な設定オブジェクトとして提供します。
    - **`github_auth.py`**: GitHub CLI (`gh`) を利用してGitHubへの認証を行い、APIアクセスに必要なトークンを取得・管理する機能を提供します。
    - **`github_client.py`**: GitHub API（主にGraphQL）と連携し、リポジトリやプルリクエストに関する高レベルな操作を行うためのクライアントモジュールです。
    - **`graphql_client.py`**: GitHubのGraphQL APIに直接クエリを送信し、そのレスポンスを処理する低レベルなクライアント機能を提供します。
    - **`issue_fetcher.py`**: GitHubリポジトリからIssue情報を取得するための機能を提供します。オープンPRがないリポジトリのIssue表示などに利用されます。
    - **`main.py`**: 監視ツールのメイン実行ループを制御するスクリプトです。設定の初期化、定期的なPR監視、フェーズ判定、およびアクションの実行を統括します。
    - **`notifier.py`**: ntfy.shサービスを利用して、モバイルデバイスへプッシュ通知を送信する機能を提供します。
    - **`phase_detector.py`**: プルリクエストの現在の状態を分析し、`phase1`から`LLM working`までの定義されたいずれかのフェーズを判定するロジックを実装しています。
    - **`pr_actions.py`**: プルリクエストに対する具体的なアクション（例: ドラフトPRをレビュー可能状態にする、ブラウザでPRページを開く）を実行する機能を提供します。
    - **`pr_fetcher.py`**: GitHubからオープンなプルリクエストのリストと詳細情報を取得するロジックを実装しています。
    - **`repository_fetcher.py`**: 認証済みユーザーが所有するGitHubリポジトリのリストを取得する機能を提供します。
- **`tests/`**: プロジェクトのテストコードが格納されているディレクトリです。
    - **`test_browser_automation.py`**: ブラウザ自動操縦機能のテストコードです。
    - **`test_config_rulesets.py`**: 設定ファイルにおけるルールセットの動作を検証するテストコードです。
    - **`test_integration_issue_fetching.py`**: Issue情報取得機能の統合テストコードです。
    - **`test_interval_parsing.py`**: 監視間隔の設定値のパース処理を検証するテストコードです。
    - **`test_issue_fetching.py`**: Issue情報取得の単体テストコードです。
    - **`test_no_open_prs_issue_display.py`**: オープンなPRがない場合にIssueが表示される動作を検証するテストコードです。
    - **`test_notification.py`**: 通知機能のテストコードです。
    - **`test_phase_detection.py`**: PRフェーズ判定ロジックのテストコードです。
    - **`test_post_comment.py`**: コメント投稿機能のテストコードです。
    - **`test_pr_actions.py`**: プルリクエストに対するアクション機能のテストコードです。
    - **`test_pr_actions_with_rulesets.py`**: ルールセットを適用した際のPRアクションの動作を検証するテストコードです。

## 関数詳細説明
- **`main()`** (src/gh_pr_phase_monitor/main.py):
    - **役割**: アプリケーションのメインエントリポイントであり、監視ループ全体を制御します。設定の読み込み、リポジトリとPRの定期的なフェッチ、フェーズ判定、およびそれに基づくアクションの実行を調整します。
    - **引数**: `config_path: str` (オプション) - 設定ファイル`config.toml`へのパス。指定されない場合はデフォルトのパスが使用されます。
    - **戻り値**: なし。
    - **機能**: 設定された間隔（例: 1分ごと）でGitHubリポジトリとプルリクエストの状態をポーリングし、各PRのフェーズを判定して適切なアクションを実行します。プログラムはCtrl+Cが押されるまで継続的に実行されます。
- **`fetch_repositories(github_token: str)`** (src/gh_pr_phase_monitor/repository_fetcher.py または github_client.py):
    - **役割**: 認証済みのGitHubユーザーが所有するすべてのリポジトリのリストをGitHub GraphQL API経由で取得します。
    - **引数**: `github_token: str` - GitHub APIへのアクセスに使用する認証トークン。
    - **戻り値**: `List[Repository]` - 検出されたリポジトリ情報を表すオブジェクトのリスト。
    - **機能**: ユーザーのGitHubアカウントに紐づくリポジトリを効率的に取得し、その後のPR監視の対象とします。
- **`fetch_pull_requests(repo_owner: str, repo_name: str, github_token: str)`** (src/gh_pr_phase_monitor/pr_fetcher.py または github_client.py):
    - **役割**: 指定されたリポジトリ内のすべてのオープンなプルリクエストと関連する詳細情報（ステータス、コメント、レビューなど）を取得します。
    - **引数**: `repo_owner: str` - リポジトリの所有者のGitHubユーザー名、`repo_name: str` - 対象リポジトリの名前、`github_token: str` - GitHub APIへの認証トークン。
    - **戻り値**: `List[PullRequest]` - 取得されたプルリクエスト情報を表すオブジェクトのリスト。
    - **機能**: 各プルリクエストの最新の状態を取得し、フェーズ判定のための基礎データを提供します。
- **`detect_phase(pr: PullRequest)`** (src/gh_pr_phase_monitor/phase_detector.py):
    - **役割**: 特定のプルリクエストの状態を分析し、`phase1` (Draft状態)、`phase2` (レビュー指摘対応中)、`phase3` (レビュー待ち)、または`LLM working` (コーディングエージェント作業中) のいずれかのフェーズを判定します。
    - **引数**: `pr: PullRequest` - 判定対象のプルリクエストオブジェクト。
    - **戻り値**: `str` - 判定されたフェーズ名（例: "phase1", "LLM working"）。
    - **機能**: PRがドラフトか、特定のレビューコメントがあるか、レビューが完了しているかなど、複数の条件に基づいてPRの現在の進捗状況を自動的に識別します。
- **`post_comment(pr_id: str, body: str, github_token: str)`** (src/gh_pr_phase_monitor/comment_manager.py):
    - **役割**: 指定されたプルリクエストに対して、プログラムが生成したコメントを投稿します。
    - **引数**: `pr_id: str` - コメントを投稿するプルリクエストのグローバルID、`body: str` - 投稿するコメントのテキスト内容、`github_token: str` - GitHub APIへの認証トークン。
    - **戻り値**: `bool` - コメント投稿が成功した場合は`True`、それ以外は`False`。
    - **機能**: `phase2`でCopilotに対する修正依頼コメントを自動投稿するなど、特定のフェーズで必要なコミュニケーションを自動化します。
- **`mark_pr_ready_for_review(pr_id: str, github_token: str)`** (src/gh_pr_phase_monitor/pr_actions.py):
    - **役割**: Draft状態のプルリクエストを「レビュー可能」（Ready for review）な状態に切り替えます。
    - **引数**: `pr_id: str` - 状態を変更するプルリクエストのグローバルID、`github_token: str` - GitHub APIへの認証トークン。
    - **戻り値**: `bool` - 状態変更が成功した場合は`True`、それ以外は`False`。
    - **機能**: `phase1`から`phase2`への移行時など、ドラフト状態のPRを自動的にレビュー対象とすることで、開発ワークフローを加速します。
- **`send_notification(topic: str, message: str, url: str, priority: int)`** (src/gh_pr_phase_monitor/notifier.py):
    - **役割**: ntfy.shサービスを利用して、指定されたトピックにプッシュ通知メッセージを送信します。
    - **引数**: `topic: str` - ntfy.shの通知トピック名、`message: str` - 送信する通知メッセージ、`url: str` - 通知に含めるURL（クリック可能なアクションボタンとして機能）、`priority: int` - 通知の優先度（1=最低、5=最高）。
    - **戻り値**: `bool` - 通知送信が成功した場合は`True`、それ以外は`False`。
    - **機能**: `phase3`（人間のレビュー待ち）のPRが検出された際に、ユーザーのモバイルデバイスへ通知を送り、迅速なレビューを促します。
- **`assign_issue_to_copilot(issue_url: str, browser_type: str, automated: bool)`** (src/gh_pr_phase_monitor/browser_automation.py):
    - **役割**: 特定のGitHub IssueをGitHub Copilotに自動割り当てするために、ウェブブラウザを起動し、必要に応じて「Assign to Copilot」ボタンを自動的にクリックします。
    - **引数**: `issue_url: str` - 割り当て対象のIssueのURL、`browser_type: str` - 使用するブラウザの種類（例: "edge", "chrome", "firefox"）、`automated: bool` - ブラウザ自動操縦を有効にするか（`True`の場合、ボタンを自動クリック）。
    - **戻り値**: なし。
    - **機能**: Seleniumライブラリを活用し、GitHubのウェブインターフェース上での手動操作をシミュレートすることで、IssueのCopilotへの割り当てプロセスを自動化または簡素化します。

## 関数呼び出し階層ツリー
```
関数呼び出し階層を分析できませんでした。

---
Generated at: 2026-01-06 07:02:16 JST
