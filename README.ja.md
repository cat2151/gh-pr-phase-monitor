# cat-github-watcher

**GitHub Copilotによる自動実装フェーズのPR監視ツール**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

※このドキュメントは大部分がAI生成です。issueをagentに投げて生成させました。

## 状況
- ドッグフーディング中です。
- 大きなバグを一通り取りました。
- 破壊的変更が頻繁にあります。
- 備忘
  - 当初はGitHub Actionsで実装を試みましたが、PR監視という目的には適さないことが判明したため、Python版に移行しました。
  - Python版は、認証済みGitHubユーザーのユーザー所有リポジトリを監視し、PRのフェーズに応じた通知やアクションを実行します。

## Quick Links
| 項目 | リンク |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## 概要

GitHub Copilotが自動実装を行うPRのフェーズを監視し、適切なタイミングで通知やアクションを実行するPythonツールです。
認証済みGitHubユーザーのユーザー所有リポジトリを対象に、GraphQL APIを利用して効率的にPRを監視します。

## 特徴

- **全リポジトリ自動監視**: 認証済みGitHubユーザーのユーザー所有リポジトリのPRを自動監視
- **GraphQL API活用**: 効率的なデータ取得で高速監視を実現
- **フェーズ検知**: PRの状態（phase1: Draft状態、phase2: レビュー指摘対応中、phase3: レビュー待ち、LLM working: コーディングエージェント作業中）を自動判定
- **Dry-runモード**: デフォルトでは監視のみ行い、実際のアクション（コメント投稿、PR Ready化、通知送信）は実行しない。明示的に有効化することで安全に運用可能
- **自動コメント投稿**: フェーズに応じて適切なコメントを自動投稿（要：設定ファイルで有効化）
- **Draft PR自動Ready化**: phase2でのレビュー指摘対応のため、Draft PRを自動的にReady状態に変更（要：設定ファイルで有効化）
- **モバイル通知**: ntfy.shを利用してphase3（レビュー待ち）を検知したらモバイル端末に通知（要：設定ファイルで有効化）
- **issue一覧表示**: 全PRが「LLM working」の場合、オープンPRのないリポジトリのissue上位10件を表示

## アーキテクチャ

このツールは、単一責任の原則(SRP)に従ってモジュール化されたPythonアプリケーションです。

### ディレクトリ構成

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

### フェーズ判定ロジック

ツールは以下の4つのフェーズを判定します：

1. **phase1 (Draft状態)**: PRがDraft状態で、レビューリクエストがある場合
2. **phase2 (レビュー指摘対応中)**: copilot-pull-request-reviewerがレビューコメントを投稿し、修正が必要な場合
3. **phase3 (レビュー待ち)**: copilot-swe-agentが修正を完了し、人間のレビュー待ちの場合
4. **LLM working (コーディングエージェント作業中)**: 上記のいずれにも該当しない場合（Copilotが実装中など）

## 使い方

### 前提条件

- Python 3.x がインストールされている
- GitHub CLI (`gh`) がインストールされ、認証済みである
  ```bash
  gh auth login
  ```

### セットアップ

1. このリポジトリをクローン：
   ```bash
   git clone https://github.com/cat2151/cat-github-watcher.git
   cd cat-github-watcher
   ```

2. 設定ファイルを作成（オプション）：
   ```bash
   cp config.toml.example config.toml
   ```

3. `config.toml` を編集して、監視間隔や実行モード、ntfy.sh通知、Copilot自動割り当て、自動マージを設定（オプション）：
   ```toml
   # チェック間隔（"30s", "1m", "5m", "1h", "1d"など）
   interval = "1m"
   
   # 実行制御フラグ - [[rulesets]]セクション内でのみ指定可能
   # グローバルフラグはサポートされなくなりました
   # 全リポジトリに設定を適用するには 'repositories = ["all"]' を使用してください
   
   # ルールセット設定例:
   # [[rulesets]]
   # name = "全リポジトリのデフォルト - dry-runモード"
   # repositories = ["all"]  # "all" は全リポジトリにマッチします
   # enable_execution_phase1_to_phase2 = false  # trueにするとdraft PRをready化
   # enable_execution_phase2_to_phase3 = false  # trueにするとphase2コメント投稿
   # enable_execution_phase3_send_ntfy = false  # trueにするとntfy通知送信
   # enable_execution_phase3_to_merge = false   # trueにするとphase3 PRをマージ
   
   # ntfy.sh通知設定（オプション）
   # 通知にはPRを開くためのクリック可能なアクションボタンが含まれます
   [ntfy]
   enabled = false  # trueにすると通知を有効化
   topic = "<ここにntfy.shのトピック名を書く>"  # 誰でも読み書きできるので、推測されない文字列にしてください
   message = "PR is ready for review: {url}"  # メッセージテンプレート
   priority = 4  # 通知の優先度（1=最低、3=デフォルト、4=高、5=最高）
   
   # Phase3自動マージ設定（オプション）
   # PRがphase3（レビュー待ち）に達したら自動的にマージします
   # マージ前に、以下で定義したコメントがPRに投稿されます
   # マージ成功後、自動的にfeature branchが削除されます
   [phase3_merge]
   enabled = false  # trueにすると自動マージを有効化（rulesetsでenable_execution_phase3_to_merge = trueも必要）
   comment = "All checks passed. Merging PR."  # マージ前に投稿するコメント
   automated = false  # trueにするとブラウザ自動操縦でマージボタンをクリック
   automation_backend = "selenium"  # 自動操縦バックエンド: "selenium" または "playwright"
   wait_seconds = 10  # ブラウザ起動後、ボタンクリック前の待機時間（秒）
   browser = "edge"  # 使用するブラウザ: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
   headless = false  # ヘッドレスモードで実行（ウィンドウを表示しない）
   
   # "good first issue"のissueをCopilotに自動割り当て（オプション）
   # 有効にすると、issueをブラウザで開き、"Assign to Copilot"ボタンを押すよう促します
   # automated = true にすると、ブラウザ自動操縦でボタンを自動的にクリックします（Selenium必要）
   [assign_to_copilot]
   enabled = false  # trueにすると自動割り当て機能を有効化
   automated = false  # trueにするとブラウザ自動操縦を有効化（要：pip install selenium webdriver-manager）
   wait_seconds = 10  # ブラウザ起動後、ボタンクリック前の待機時間（秒）
   browser = "edge"  # 使用するブラウザ（"edge", "chrome", "firefox"）
   ```

4. （オプション）ブラウザ自動操縦を使用する場合は、Seleniumをインストール：
   ```bash
   pip install -r requirements-automation.txt
   ```
   または
   ```bash
   pip install selenium webdriver-manager
   ```
   
   さらに、使用するブラウザのドライバーが必要です：
   - **Edge**: Windows 10/11に標準搭載（追加インストール不要）
   - **Chrome**: ChromeDriverが自動的にダウンロードされます
   - **Firefox**: GeckoDriverが自動的にダウンロードされます
   ```

### 実行

ツールを起動して監視を開始：

```bash
python3 cat-github-watcher.py [config.toml]
```

または、Pythonモジュールとして直接実行：

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### 動作の流れ

1. **起動**: ツールを起動すると、認証済みGitHubユーザーのユーザー所有リポジトリの監視を開始
2. **PR検知**: オープンPRを持つリポジトリを自動検出
3. **フェーズ判定**: 各PRのフェーズを判定（phase1/2/3、LLM working）
4. **アクション実行**:
   - **phase1**: デフォルトはDry-run（`enable_execution_phase1_to_phase2 = true`でDraft PRをReady状態に変更）
   - **phase2**: デフォルトはDry-run（`enable_execution_phase2_to_phase3 = true`でCopilotに変更適用を依頼するコメントを投稿）
   - **phase3**: ブラウザでPRページを開く（`enable_execution_phase3_send_ntfy = true`でntfy.sh通知も送信、`enable_execution_phase3_to_merge = true`でPRを自動マージ）
   - **LLM working**: 待機（全PRがこの状態の場合、オープンPRのないリポジトリのissueを表示）
5. **繰り返し**: 設定された間隔で監視を継続

### Dry-runモード

デフォルトでは、ツールは**Dry-runモード**で動作し、実際のアクションは実行しません。これにより、安全に動作を確認できます。

- **Phase1（Draft → Ready化）**: `[DRY-RUN] Would mark PR as ready for review` と表示されるが、実際には何もしない
- **Phase2（コメント投稿）**: `[DRY-RUN] Would post comment for phase2` と表示されるが、実際には何もしない
- **Phase3（ntfy通知）**: `[DRY-RUN] Would send ntfy notification` と表示されるが、実際には何もしない
- **Phase3（マージ）**: `[DRY-RUN] Would merge PR` と表示されるが、実際には何もしない

実際のアクションを有効にするには、`config.toml`で以下のフラグを`true`に設定します：
```toml
enable_execution_phase1_to_phase2 = true  # Draft PRをReady化
enable_execution_phase2_to_phase3 = true  # Phase2コメント投稿
enable_execution_phase3_send_ntfy = true  # ntfy通知送信
enable_execution_phase3_to_merge = true   # Phase3 PRをマージ
```

### 停止

`Ctrl+C` で監視を停止できます。

## 注意事項

- GitHub CLI (`gh`) がインストールされ、認証済みである必要があります
- GitHub Copilot (特に copilot-pull-request-reviewer と copilot-swe-agent) との連携を前提としています
- 認証済みユーザーの**ユーザー所有リポジトリのみ**が監視対象になります。ツールをシンプルかつ集中させるため、Organizationリポジトリは含まれません（YAGNI原則）
- GraphQL APIを使用するため、APIレート制限に注意してください
- ntfy.sh通知を使用する場合は、事前に[ntfy.sh](https://ntfy.sh/)でトピックを設定してください

## テスト

プロジェクトにはpytestを使用したテストスイートが含まれています：

```bash
pytest tests/
```

## ライセンス

MIT License - 詳細はLICENSEファイルを参照してください

※英語版README.mdは、README.ja.mdを元にGeminiの翻訳でGitHub Actionsにより自動生成しています

*Big Brother is watching your repositories. Now it’s the cat.* 🐱
