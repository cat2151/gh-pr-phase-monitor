# ブラウザ自動操縦実装サマリー

## 概要
このPRは、PR #65をベースに、cat-github-watcherツールの自動ブラウザボタンクリック機能を実装します。この機能により、ブラウザ起動後に「Assign to Copilot」と「Assign」ボタンを自動的にクリックすることができます。

## 実装内容

### 1. ブラウザ自動操縦モジュール
**ファイル**: `src/gh_pr_phase_monitor/browser_automation.py`

以下を提供する新しいモジュール:
- Selenium WebDriverベースのブラウザ自動操縦
- Edge、Chrome、Firefoxブラウザのサポート
- ボタンクリック前の待機時間設定
- ヘッドレスモード対応
- Seleniumが利用できない場合の自動フォールバック
- ボタン検出のための複数セレクター戦略
- 堅牢なエラーハンドリング

主要な関数:
- `is_selenium_available()`: Seleniumがインストールされているか確認
- `assign_issue_to_copilot_automated()`: メイン自動化関数
- `_create_browser_driver()`: ブラウザ初期化
- `_click_button()`: ボタン検出とクリック

### 2. Issue Fetcherの更新
**ファイル**: `src/gh_pr_phase_monitor/issue_fetcher.py`

既存の`assign_issue_to_copilot()`関数を拡張:
- オプションの`config`パラメータを受け入れ
- 手動モードと自動モードの両方をサポート
- 設定で`automated = true`の場合、Seleniumを自動使用
- Seleniumが利用できない場合は手動モードに優雅にフォールバック

### 3. 設定サポート
**ファイル**: `config.toml.example`

新しい設定オプションを追加:
```toml
[assign_to_copilot]
enabled = false          # 機能を有効化
automated = false        # ブラウザ自動操縦を有効化
wait_seconds = 10        # クリック前の待機時間（秒）
browser = "edge"         # ブラウザ: "edge", "chrome", "firefox"
headless = false         # ヘッドレスモードで実行
```

### 4. 依存関係
**ファイル**: `requirements-automation.txt`

ブラウザ自動操縦のためのオプション依存関係:
- selenium>=4.0.0
- webdriver-manager>=4.0.0

### 5. ドキュメント

**日本語**: `docs/browser-automation-approaches.md`
- 4つの異なる自動化アプローチの詳細分析
- 各方法のメリット・デメリット比較
- 推奨アプローチ（Selenium）
- 実装手順
- 重要な考慮事項

**英語**: `docs/browser-automation-approaches.en.md`
- 日本語ドキュメントの翻訳

**READMEファイル**: `README.ja.md`と`README.md`を更新
- Seleniumのインストール手順を追加
- 新しい設定オプションを文書化
- 自動モードの使用方法を説明

### 6. デモスクリプト
**ファイル**: `demo_automation.py`

以下を行うデモスクリプト:
- Seleniumが利用可能かチェック
- 設定例を表示
- 自動化の仕組みを説明
- 要件と使用方法をリスト

## 動作の仕組み

### 手動モード（デフォルト）
1. ツールが「good first issue」を発見
2. デフォルトブラウザでissue URLを開く
3. ユーザーが手動でボタンをクリック

### 自動モード（有効化時）
1. ツールが「good first issue」を発見
2. Selenium WebDriverを使ってブラウザを起動
3. issue URLに移動
4. 設定された時間待機（デフォルト: 10秒）
5. 「Assign to Copilot」ボタンを自動検出してクリック
6. 2秒待機
7. 「Assign」ボタンを自動検出してクリック
8. ブラウザを閉じる

## Windows互換性

このソリューションはWindows PCに完全対応:

1. **Edgeブラウザ**（Windows推奨）:
   - Windows 10/11にプリインストール
   - 追加のドライバーインストール不要
   - Seleniumをインストールするだけ: `pip install selenium webdriver-manager`

2. **Chromeブラウザ**:
   - ChromeDriverはwebdriver-managerによって自動ダウンロード

3. **Firefoxブラウザ**:
   - GeckoDriverはwebdriver-managerによって自動ダウンロード

## インストール

### 基本インストール（自動化なし）
変更不要 - ツールは以前と同様に手動モードで動作します。

### 自動化サポート付き
```bash
# SeleniumとWebDriver-Managerをインストール
pip install -r requirements-automation.txt

# または手動で:
pip install selenium webdriver-manager
```

### 設定
`config.toml`を編集:
```toml
[assign_to_copilot]
enabled = true           # 機能を有効化
automated = true         # 自動化を有効化
wait_seconds = 10        # クリック前の待機時間
browser = "edge"         # 使用するブラウザ（edge、chrome、firefox）
```

## テスト

既存のテストはすべて合格（142テスト）:
```bash
pytest tests/ -v
```

実装内容:
- ✅ 下位互換性を維持
- ✅ Seleniumが利用できない場合は優雅にフォールバック
- ✅ すべての既存テストに合格
- ✅ プロジェクトのコードスタイルに準拠（ruff）

## 利点

1. **自動化**: issue割り当ての手作業を削減
2. **柔軟性**: 設定で有効/無効を切り替え可能
3. **互換性**: Windows上でEdgeを使用（追加セットアップ不要）
4. **堅牢性**: 必要に応じて手動モードに優雅にフォールバック
5. **標準**: 業界標準のSelenium WebDriverを使用
6. **保守性**: よく文書化されテストされている

## 今後の拡張（オプション）

将来の改善案:
1. 既存のブラウザプロファイル使用のサポート（ログイン状態維持）
2. GitHubのUIが変更された場合のボタンセレクター設定
3. より多くのブラウザサポート
4. ヘッドレスモードの最適化
5. デバッグ用の失敗時スクリーンショット

## 制限事項

1. **ログイン必須**: ユーザーはブラウザでGitHubにログインしている必要があります
2. **UI変更**: GitHubがボタンテキストやHTML構造を変更した場合、セレクターの更新が必要になる可能性があります
3. **レート制限**: GitHubのレート制限を尊重する必要があります
4. **利用規約**: ユーザーはGitHubの利用規約に準拠していることを確認する必要があります

## 検討した代替アプローチ

詳細な分析は`docs/browser-automation-approaches.md`を参照:
1. Selenium WebDriver（選択 ✓）
2. Playwright
3. PyAutoGUI（非推奨）
4. AutoHotkey（Windows専用）

## 変更されたファイル

- `src/gh_pr_phase_monitor/browser_automation.py`（新規）
- `src/gh_pr_phase_monitor/issue_fetcher.py`（更新）
- `src/gh_pr_phase_monitor/main.py`（更新）
- `config.toml.example`（更新）
- `requirements-automation.txt`（新規）
- `README.ja.md`（更新）
- `README.md`（更新）
- `docs/browser-automation-approaches.md`（新規）
- `docs/browser-automation-approaches.en.md`（新規）
- `demo_automation.py`（新規）

## セキュリティ

- ✅ CodeQLスキャン完了（脆弱性0件）
- ✅ XPath インジェクション対策済み（ダブルクォート使用、定義済みテキストのみ）
- ✅ 型アノテーション追加済み
- ✅ コードレビュー完了、フィードバック対応済み

## まとめ

この実装は、「Assign to Copilot」ワークフローを自動化するための、堅牢でWindows互換性のあるソリューションを提供します。業界標準ツール（Selenium WebDriver）を使用し、下位互換性を維持し、設定で簡単に有効化または無効化できます。
