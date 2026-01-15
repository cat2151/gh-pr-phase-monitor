# cat-github-watcher

**GitHub Copilotによる自動実装フェーズのPR監視ツール**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
  <a href="https://deepwiki.com/cat2151/cat-github-watcher"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
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
  - 個別のPRがphase3になったときに通知
  - すべてのPRがphase3になったときにも通知（メッセージはtomlで設定可能）
- **issue一覧表示**: 全PRが「LLM working」の場合、オープンPRのないリポジトリのissue上位N件を表示（デフォルト: 10件、`issue_display_limit`で変更可能）
- **省電力モード**: 状態変化がない場合、API使用量を削減するため監視間隔を自動的に延長（`no_change_timeout`と`reduced_frequency_interval`で設定可能）
- **Verboseモード**: 起動時と実行中に詳細な設定情報を表示し、設定ミスの検出を支援（`verbose`で有効化）

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
   
   # PRのないリポジトリから表示するissue数の上限
   # デフォルトは10ですが、任意の正の数（例: 5, 15, 20）に変更可能
   issue_display_limit = 10
   
   # 状態変更なしのタイムアウト時間
   # 全PRの状態（各PRのフェーズ）がこの時間変化しない場合、
   # 監視間隔が省電力モード（下記のreduced_frequency_interval）に切り替わります
   # 空文字列 "" を設定すると無効化されます
   # サポートされる形式: "30s", "1m", "5m", "30m", "1h", "1d"
   # デフォルト: "30m" (30分 - 安定性優先)
   no_change_timeout = "30m"
   
   # 省電力モード時の監視間隔
   # no_change_timeout期間で状態変化が検知されない場合、
   # 監視間隔がこの間隔に切り替わりAPI使用量を削減します
   # 変化が検知されると、通常の監視間隔に戻ります
   # サポートされる形式: "30s", "1m", "5m", "30m", "1h", "1d"
   # デフォルト: "1h" (1時間)
   reduced_frequency_interval = "1h"
   
   # Verboseモード - 詳細な設定情報を表示
   # 有効にすると、起動時に全設定を表示し、実行中にリポジトリ毎の設定も表示します
   # 設定ミスの検出に役立ちます
   # デフォルト: false
   verbose = false
   
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
   
   # [[rulesets]]
   # name = "シンプル: good first issueをCopilotに自動割り当て"
   # repositories = ["my-repo"]
   # assign_good_first_old = true  # これだけでOK！ [assign_to_copilot]セクションは不要です
   #                               # デフォルト動作: ブラウザでissueを開いて手動割り当て
   
   # ntfy.sh通知設定（オプション）
   # 通知にはPRを開くためのクリック可能なアクションボタンが含まれます
   [ntfy]
   enabled = false  # trueにすると通知を有効化
   topic = "<ここにntfy.shのトピック名を書く>"  # 誰でも読み書きできるので、推測されない文字列にしてください
   message = "PR is ready for review: {url}"  # メッセージテンプレート
   priority = 4  # 通知の優先度（1=最低、3=デフォルト、4=高、5=最高）
   all_phase3_message = "All PRs are now in phase3 (ready for review)"  # すべてのPRがphase3になったときのメッセージ
   
   # Phase3自動マージ設定（オプション）
   # PRがphase3（レビュー待ち）に達したら自動的にマージします
   # マージ前に、以下で定義したコメントがPRに投稿されます
   # マージ成功後、自動的にfeature branchが削除されます
   # 重要: 安全のため、この機能はデフォルトで無効です
   # リポジトリごとにrulesetsで enable_execution_phase3_to_merge = true を指定して明示的に有効化する必要があります
   # 重要：自動マージが有効な場合、commentフィールドを明示的に設定する必要があります
   [phase3_merge]
   comment = "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。"  # マージ前に投稿するコメント（自動マージ有効時は必須）
   automated = false  # trueにするとブラウザ自動操縦でマージボタンをクリック
   wait_seconds = 10  # ブラウザ起動後、ボタンクリック前の待機時間（秒）
   debug_dir = "debug_screenshots"  # 画像認識失敗時のデバッグ情報保存先（デフォルト: "debug_screenshots"）
   
   # issueをCopilotに自動割り当て（完全にオプション！このセクション全体がオプションです）
   # 
   # シンプルな使い方: rulesetsで assign_good_first_old = true とするだけ（上記の例を参照）
   # このセクションは、デフォルト動作をカスタマイズしたい場合のみ定義してください。
   # 
   # 割り当て動作はrulesetのフラグで制御します:
   # - assign_good_first_old: 最も古い"good first issue"を割り当て（issue番号順、デフォルト: false）
   # - assign_old: 最も古いissueを割り当て（issue番号順、ラベル不問、デフォルト: false）
   # 両方がtrueの場合、"good first issue"を優先
   # 
   # デフォルト動作（このセクションが定義されていない場合）:
   # - ブラウザ自動操縦で自動的にボタンをクリック
   # - PyAutoGUIを使用
   # - wait_seconds = 10
   # 
   # 必須: PyAutoGUIのインストールが必要（pip install pyautogui pillow）
   # 
   # 重要: 安全のため、この機能はデフォルトで無効です
   # リポジトリごとにrulesetsで assign_good_first_old または assign_old を指定して明示的に有効化する必要があります
   [assign_to_copilot]
   wait_seconds = 10  # ブラウザ起動後、ボタンクリック前の待機時間（秒）
   debug_dir = "debug_screenshots"  # 画像認識失敗時のデバッグ情報保存先（デフォルト: "debug_screenshots"）
   ```

4. **ボタンスクリーンショットの準備（自動化を使用する場合のみ）**:
   
   自動化機能（`automated = true` または `assign_to_copilot` / `phase3_merge` の有効化）を使用する場合、
   PyAutoGUIがクリックするボタンのスクリーンショットが必要です。
   
   **必要なスクリーンショット:**
   
   issueの自動割り当て用（`assign_to_copilot` 機能）:
   - `assign_to_copilot.png` - "Assign to Copilot" ボタンのスクリーンショット
   - `assign.png` - "Assign" ボタンのスクリーンショット
   
   PRの自動マージ用（`phase3_merge` 機能で `automated = true` の場合）:
   - `merge_pull_request.png` - "Merge pull request" ボタンのスクリーンショット
   - `confirm_merge.png` - "Confirm merge" ボタンのスクリーンショット
   - `delete_branch.png` - "Delete branch" ボタンのスクリーンショット（オプション）
   
   **スクリーンショットの撮り方:**
   
   a. GitHubのissueまたはPRをブラウザで開く
   b. 自動化したいボタンを見つける
   c. **ボタンだけ**のスクリーンショットを撮る（画面全体ではなく）
   d. PNG形式で `screenshots` ディレクトリに保存する
   e. 上記の正確なファイル名を使用する
   
   **ヒント:**
   - スクリーンショットはボタンのみを含め、小さな余白を含める
   - OSのスクリーンショットツールを使用する（Windows: Snipping Tool、Mac: Cmd+Shift+4）
   - ボタンがはっきり見え、隠れていないことを確認
   - ボタンの見た目が変わる場合（テーマ変更など）、スクリーンショットを更新する必要があります
   - 画像認識の信頼度を調整する場合は `confidence` 設定を使用（DPI scalingやテーマによる）
   
   **デバッグ情報の自動保存:**
   - 画像認識が失敗した場合、自動的にデバッグ情報が保存されます
   - 保存先：`debug_screenshots/` ディレクトリ（デフォルト）
   - 保存内容：
     - スクリーンショット（失敗時の画面全体）: `{button_name}_fail_{timestamp}.png`
     - 失敗情報JSON: `{button_name}_fail_{timestamp}.json`
       - ボタン名、タイムスタンプ、信頼度閾値、スクリーンショットパス、テンプレート画像パス
   - デバッグディレクトリは設定で変更可能：`debug_dir` オプション（`assign_to_copilot` または `phase3_merge` セクション内）
   
   **重要な要件:**
   - デフォルトブラウザで**GitHubに既にログイン済み**である必要があります
   - 自動化は既存のブラウザセッションを使用します（新しい認証は行いません）
   - ボタンクリック時に正しいGitHubウィンドウ/タブがフォーカスされ、画面に表示されていることを確認してください
   - 複数のGitHubページが開いている場合、最初に見つかったボタンがクリックされます
   
   **スクリーンショットディレクトリの作成:**
   ```bash
   mkdir screenshots
   ```

5. PyAutoGUIをインストール（自動化を使用する場合のみ）：
   
   ```bash
   pip install -r requirements-automation.txt
   ```
   または
   ```bash
   pip install pyautogui pillow
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
   - **phase1**: デフォルトはDry-run（rulesetsで`enable_execution_phase1_to_phase2 = true`とするとDraft PRをReady状態に変更）
   - **phase2**: デフォルトはDry-run（rulesetsで`enable_execution_phase2_to_phase3 = true`とするとCopilotに変更適用を依頼するコメントを投稿）
   - **phase3**: ブラウザでPRページを開く
     - rulesetsで`enable_execution_phase3_send_ntfy = true`とするとntfy.sh通知も送信
     - rulesetsで`enable_execution_phase3_to_merge = true`とするとPRを自動マージ（グローバル`[phase3_merge]`設定を使用）
   - **LLM working**: 待機（全PRがこの状態の場合、オープンPRのないリポジトリのissueを表示）
5. **Issue自動割り当て**: 全PRが「LLM working」かつオープンPRのないリポジトリがある場合：
   - rulesetsで`assign_good_first_old = true`とすると最も古い"good first issue"を自動割り当て（issue番号順）
   - rulesetsで`assign_old = true`とすると最も古いissueを自動割り当て（issue番号順、ラベル不問）
   - 両方がtrueの場合、"good first issue"を優先
   - デフォルト動作: PyAutoGUIで自動的にボタンをクリック（`[assign_to_copilot]`セクションは不要）
   - 必須: PyAutoGUIのインストールとボタンスクリーンショットの準備が必要
6. **繰り返し**: 設定された間隔で監視を継続
   - 状態変化がない状態が`no_change_timeout`で設定された時間だけ続いた場合、自動的に省電力モード（`reduced_frequency_interval`）に切り替わりAPI使用量を削減
   - 変化が検知されると通常の監視間隔に戻る

### Dry-runモード

デフォルトでは、ツールは**Dry-runモード**で動作し、実際のアクションは実行しません。これにより、安全に動作を確認できます。

- **Phase1（Draft → Ready化）**: `[DRY-RUN] Would mark PR as ready for review` と表示されるが、実際には何もしない
- **Phase2（コメント投稿）**: `[DRY-RUN] Would post comment for phase2` と表示されるが、実際には何もしない
- **Phase3（ntfy通知）**: `[DRY-RUN] Would send ntfy notification` と表示されるが、実際には何もしない
- **Phase3（マージ）**: `[DRY-RUN] Would merge PR` と表示されるが、実際には何もしない

実際のアクションを有効にするには、`config.toml`の`[[rulesets]]`セクションで以下のフラグを`true`に設定します：
```toml
[[rulesets]]
name = "特定のリポジトリで自動化を有効化"
repositories = ["test-repo"]  # または ["all"] で全リポジトリ
enable_execution_phase1_to_phase2 = true  # Draft PRをReady化
enable_execution_phase2_to_phase3 = true  # Phase2コメント投稿
enable_execution_phase3_send_ntfy = true  # ntfy通知送信
enable_execution_phase3_to_merge = true   # Phase3 PRをマージ
assign_good_first_old = true              # good first issueを自動割り当て
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
