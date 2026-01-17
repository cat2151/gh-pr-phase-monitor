Last updated: 2026-01-18

# Project Overview

## プロジェクト概要
- GitHub Copilotによる自動実装フェーズのプルリクエスト(PR)を効率的に監視するツールです。
- 認証済みGitHubユーザーが所有するリポジトリを対象に、PRの状態変化を自動で検知します。
- PRのフェーズに応じた通知、コメント投稿、PRのReady化、自動マージなどのアクションを実行します。

## 技術スタック
プロジェクトで使用されている主な技術スタックは以下の通りです。

- フロントエンド: このプロジェクトはGUIを持たず、コマンドラインで動作します。ブラウザの自動操作には後述の`PyAutoGUI`が利用されます。
- 音楽・オーディオ: 該当する技術はありません。
- 開発ツール:
    - **GitHub CLI (`gh`)**: GitHubの認証とAPI操作に利用されます。
    - **TOML**: `config.toml`ファイル形式で設定情報を管理します。
    - **Ruff**: Pythonコードのリンティングおよびフォーマットを行うことで、コード品質と一貫性を保ちます。
    - **.editorconfig**: 異なるエディタやIDE間でコードの書式設定を統一するためのファイルです。
- テスト:
    - **pytest**: Python用の強力なテストフレームワークで、プロジェクトの各機能が正しく動作することを確認するために使用されます。
    - **Pillow**: Python Imaging Libraryのフォークであり、`PyAutoGUI`が画像認識を行うための依存ライブラリです。
- ビルドツール: このプロジェクトはPythonスクリプトとして直接実行されるため、特定のビルドツールは使用していません。
- 言語機能:
    - **Python 3.x**: プロジェクトの主要な開発言語です。
    - **GraphQL API**: GitHubのAPIと効率的に連携し、必要なPRやリポジトリの情報を取得するために使用されます。
- 自動化・CI/CD:
    - **PyAutoGUI**: スクリーンショットによる画像認識とマウス・キーボード操作を用いて、Webブラウザ上のボタンクリックなどのUI操作を自動化します。
    - **ntfy.sh**: モバイルデバイスへのプッシュ通知を送信するためのサービスで、PRの重要な状態変化をリアルタイムで通知します。
- 開発標準:
    - **Ruff**: コードの自動整形と静的解析により、プロジェクト全体のコード品質基準を維持します。
    - **.editorconfig**: 開発環境の違いによるコードスタイルの差異を吸収し、一貫したコーディングスタイルを強制します。

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
プロジェクトの主要なファイルとその役割は以下の通りです。

-   **`.editorconfig`**: コーディングスタイル（インデント、改行コードなど）を定義し、プロジェクト全体のコードの一貫性を保ちます。
-   **`.gitignore`**: Gitが追跡しないファイルやディレクトリを指定します。
-   **`.vscode/settings.json`**: Visual Studio Code用の設定ファイルで、開発環境を統一します。
-   **`LICENSE`**: プロジェクトのライセンス情報（MIT License）を定義しています。
-   **`README.ja.md` / `README.md`**: プロジェクトの概要、使い方、機能などを説明するドキュメントです（日本語版と英語版）。
-   **`cat-github-watcher.py`**: プロジェクトのメインエントリーポイントとなるスクリプトです。ここからツールが起動されます。
-   **`config.toml.example`**: ユーザーが独自の監視設定を行うための、TOML形式の設定ファイルのテンプレートです。
-   **`pytest.ini`**: `pytest`テストランナーの設定ファイルです。
-   **`requirements-automation.txt`**: PyAutoGUIなどブラウザ自動化に必要な追加のPythonライブラリをリストアップしています。
-   **`ruff.toml`**: `ruff`リンター/フォーマッターの設定ファイルです。
-   **`screenshots/`**: ブラウザ自動化（PyAutoGUI）で使用される、クリック対象となるボタンのスクリーンショット画像が格納されます。
-   **`src/gh_pr_phase_monitor/__init__.py`**: Pythonパッケージとして認識させるための空ファイルです。
-   **`src/gh_pr_phase_monitor/browser_automation.py`**: PyAutoGUIを用いてブラウザのUI操作（ボタンクリックなど）を自動化する機能を提供します。
-   **`src/gh_pr_phase_monitor/colors.py`**: ターミナル出力にANSIカラーコードを適用し、視認性を高めます。
-   **`src/gh_pr_phase_monitor/comment_fetcher.py`**: GitHub APIからプルリクエストのコメント履歴を取得します。
-   **`src/gh_pr_phase_monitor/comment_manager.py`**: プルリクエストへのコメント投稿や、特定のコメントの存在確認を管理します。
-   **`src/gh_pr_phase_monitor/config.py`**: `config.toml`ファイルから設定を読み込み、アプリケーション内で利用可能な形にパースします。
-   **`src/gh_pr_phase_monitor/display.py`**: 監視結果や状態をターミナルに整形して表示する役割を担います。
-   **`src/gh_pr_phase_monitor/github_auth.py`**: GitHub CLI (`gh`) を使用してGitHub認証トークンを取得・管理します。
-   **`src/gh_pr_phase_monitor/github_client.py`**: GitHub GraphQL APIと連携し、リポジトリやプルリクエストの情報を取得したり、PRの状態を更新したりする低レベルな操作を扱います。
-   **`src/gh_pr_phase_monitor/graphql_client.py`**: GraphQLクエリを実行するための汎用的なクライアントを提供します。
-   **`src/gh_pr_phase_monitor/issue_fetcher.py`**: GitHubからissue情報を取得する機能を提供します。
-   **`src/gh_pr_phase_monitor/main.py`**: プロジェクトのメイン実行ループと、各モジュールを連携させるオーケストレーションを担います。`cat-github-watcher.py`から呼び出されます。
-   **`src/gh_pr_phase_monitor/monitor.py`**: 実際の監視ロジックと、状態変化に応じたアクションの実行フローを制御します。
-   **`src/gh_pr_phase_monitor/notifier.py`**: `ntfy.sh`サービスを通じて、モバイルデバイスへ通知を送信する機能を提供します。
-   **`src/gh_pr_phase_monitor/phase_detector.py`**: プルリクエストの現在の状態を分析し、「phase1」から「LLM working」までの定義されたフェーズを判定する中心的なロジックを含みます。
-   **`src/gh_pr_phase_monitor/pr_actions.py`**: プルリクエストの「Ready for review」化、ブラウザでのPRページ起動、自動マージなどの具体的なアクションを実行します。
-   **`src/gh_pr_phase_monitor/pr_fetcher.py`**: 特定のリポジトリからプルリクエストのリストとその詳細情報を取得します。
-   **`src/gh_pr_phase_monitor/repository_fetcher.py`**: 認証済みユーザーが所有するリポジトリのリストを取得します。
-   **`src/gh_pr_phase_monitor/state_tracker.py`**: プルリクエストやリポジトリの過去の状態を記憶し、状態変化の有無を判断することで、省電力モードへの移行などを管理します。
-   **`src/gh_pr_phase_monitor/time_utils.py`**: 時間間隔のパースや変換など、時間に関連するユーティリティ機能を提供します。
-   **`src/gh_pr_phase_monitor/wait_handler.py`**: 監視間隔の管理、省電力モードへの移行、次回の実行タイミングの計算など、待機時間に関する処理を制御します。
-   **`tests/`**: プロジェクトの様々な機能に対するユニットテストおよび結合テストが格納されており、コードの品質と信頼性を保証します。

## 関数詳細説明
このプロジェクトでは、主要なモジュールごとに以下のような役割を持つ関数が実装されています。

-   **`main.py` 内の関数**:
    -   `run_monitor()`: メインの監視ループを開始し、一定間隔でリポジトリとPRの状態をチェックする処理全体を統括します。
    -   `parse_args()`: コマンドライン引数を解析し、設定ファイルのパスなどを取得します。
-   **`config.py` 内の関数**:
    -   `load_config(config_path: str) -> dict`: 指定されたパスからTOML形式の設定ファイルを読み込み、解析してディクショナリ形式で返します。
    -   `validate_config(config: dict)`: 読み込まれた設定が正しい形式であり、必要な項目が欠けていないかなどを検証します。
-   **`github_client.py` 内の関数**:
    -   `fetch_repositories(viewer_login: str) -> list`: 認証済みユーザーが所有するリポジトリのリストをGitHub GraphQL APIから取得します。
    -   `fetch_pull_requests(repo_id: str) -> list`: 指定されたリポジトリのオープンなプルリクエストの詳細情報を取得します。
    -   `post_comment(pr_id: str, body: str) -> bool`: 指定されたプルリクエストにコメントを投稿します。
    -   `mark_pr_as_ready(pr_id: str) -> bool`: ドラフト状態のプルリクエストを「レビュー準備完了」状態に変更します。
-   **`phase_detector.py` 内の関数**:
    -   `detect_pr_phase(pr_data: dict, config: dict) -> str`: プルリクエストの各種情報（状態、レビューコメント、ラベルなど）を分析し、「phase1」「phase2」「phase3」「LLM working」のいずれかのフェーズを判定します。
-   **`comment_manager.py` 内の関数**:
    -   `post_phase2_comment(pr_id: str) -> bool`: `phase2`（レビュー指摘対応中）のPRに対して、Copilotに変更を促すコメントを自動投稿します。
    -   `check_comment_exists(pr_id: str, author: str, keyword: str) -> bool`: 特定の作者による特定のキーワードを含むコメントがPRに存在するかを確認します。
-   **`pr_actions.py` 内の関数**:
    -   `perform_pr_actions(pr: dict, phase: str, config: dict)`: プルリクエストのフェーズと設定に基づいて、コメント投稿、PRのReady化、通知送信、ブラウザ起動、自動マージなどの具体的なアクションを実行します。
    -   `open_pr_in_browser(pr_url: str)`: 指定されたPRのURLをWebブラウザで開きます。
    -   `merge_pr(pr_url: str, config: dict) -> bool`: 設定に基づいて、`phase3`のPRを自動的にマージする処理を実行します（ブラウザ自動化を含む）。
-   **`browser_automation.py` 内の関数**:
    -   `click_button_by_image(image_path: str, confidence: float) -> bool`: 指定された画像（ボタンのスクリーンショット）を画面上で認識し、その場所をクリックします。
    -   `open_url_in_browser(url: str)`: 指定されたURLをシステムのデフォルトブラウザで開きます。
-   **`notifier.py` 内の関数**:
    -   `send_notification(topic: str, message: str, priority: int, actions: list = None) -> bool`: `ntfy.sh`サービスを利用して、指定されたトピックへメッセージを通知として送信します。PRへのリンクなど、アクションボタンを付加することも可能です。
-   **`state_tracker.py` 内の関数**:
    -   `update_state(current_prs: list)`: 各PRの現在の状態を記録し、前回の監視時からの変化を検出します。
    -   `has_state_changed() -> bool`: 前回の監視からPRの状態に変化があったかどうかを返します。
-   **`wait_handler.py` 内の関数**:
    -   `calculate_next_interval(has_changed: bool, config: dict) -> int`: PRの状態変化の有無と設定に基づいて、次の監視間隔（省電力モードなど）を計算します。
    -   `wait_for_next_check(interval_seconds: int)`: 指定された秒数だけ処理を一時停止します。

## 関数呼び出し階層ツリー
提供された情報から具体的な関数呼び出し階層ツリーを直接図解することはできませんでしたが、プロジェクトの実行フローに基づいた高レベルな呼び出し関係は以下のようになります。

```
cat-github-watcher.py (エントリーポイント)
└── src.gh_pr_phase_monitor.main.run_monitor()
    ├── src.gh_pr_phase_monitor.config.load_config()
    ├── src.gh_pr_phase_monitor.github_auth.get_github_token()
    ├── (ループ開始)
    │   ├── src.gh_pr_phase_monitor.repository_fetcher.fetch_repositories()
    │   │   └── src.gh_pr_phase_monitor.github_client.execute_graphql_query()
    │   ├── (各リポジトリについて)
    │   │   ├── src.gh_pr_phase_monitor.pr_fetcher.fetch_pull_requests()
    │   │   │   └── src.gh_pr_phase_monitor.github_client.execute_graphql_query()
    │   │   ├── (各PRについて)
    │   │   │   ├── src.gh_pr_phase_monitor.phase_detector.detect_pr_phase()
    │   │   │   ├── src.gh_pr_phase_monitor.pr_actions.perform_pr_actions()
    │   │   │   │   ├── src.gh_pr_phase_monitor.comment_manager.post_phase2_comment() (条件による)
    │   │   │   │   │   └── src.gh_pr_phase_monitor.github_client.post_comment()
    │   │   │   │   ├── src.gh_pr_phase_monitor.github_client.mark_pr_as_ready() (条件による)
    │   │   │   │   ├── src.gh_pr_phase_monitor.notifier.send_notification() (条件による)
    │   │   │   │   ├── src.gh_pr_phase_monitor.browser_automation.open_url_in_browser() (条件による)
    │   │   │   │   ├── src.gh_pr_phase_monitor.pr_actions.merge_pr() (条件による)
    │   │   │   │   │   ├── src.gh_pr_phase_monitor.comment_manager.post_comment() (マージ前コメント)
    │   │   │   │   │   └── src.gh_pr_phase_monitor.browser_automation.click_button_by_image()
    │   │   ├── src.gh_pr_phase_monitor.state_tracker.update_state()
    │   │   ├── src.gh_pr_phase_monitor.state_tracker.has_state_changed()
    │   │   ├── src.gh_pr_phase_monitor.issue_fetcher.fetch_issues() (条件による)
    │   │   ├── src.gh_pr_phase_monitor.pr_actions.assign_issue_to_copilot() (条件による)
    │   │   │   └── src.gh_pr_phase_monitor.browser_automation.click_button_by_image()
    │   ├── src.gh_pr_phase_monitor.wait_handler.calculate_next_interval()
    │   ├── src.gh_pr_phase_monitor.display.update_status_summary()
    │   └── src.gh_pr_phase_monitor.wait_handler.wait_for_next_check()
    └── (ループ終了)

---
Generated at: 2026-01-18 07:01:47 JST
