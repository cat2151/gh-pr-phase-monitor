# Selenium vs Playwright 検証ガイド

このドキュメントは、SeleniumとPlaywrightの両方のブラウザ自動化バックエンドを実際に検証するためのガイドです。

## 実装内容

PR 67に関連して、以下の機能を実装しました：

1. **Playwright バックエンドの追加**: Seleniumに加えて、Playwrightも使用できるようになりました
2. **設定可能なバックエンド**: `automation_backend` 設定で使用するバックエンドを選択可能
3. **比較ツール**: `demo_comparison.py` で両方のバックエンドを比較できます

## セットアップ

### 1. Selenium のインストール（すでにインストール済みの場合はスキップ）

```bash
pip install -r requirements-automation.txt
```

または個別にインストール：

```bash
pip install selenium webdriver-manager
```

### 2. Playwright のインストール

```bash
pip install playwright
playwright install
```

`playwright install` コマンドは、Chromium、Firefox、WebKitのブラウザを自動的にダウンロードします。

## 使い方

### 比較デモの実行

両方のバックエンドの機能と特性を比較するには：

```bash
python demo_comparison.py
```

このスクリプトは以下を表示します：
- 各バックエンドの利用可能性
- 機能比較表
- 推奨事項

### 基本デモの実行

現在のセットアップを確認するには：

```bash
python demo_automation.py
```

## 設定

`config.toml` に以下の設定を追加：

### Selenium を使用する場合

```toml
[assign_to_copilot]
enabled = true
automated = true
automation_backend = "selenium"  # "selenium" を指定
wait_seconds = 10
browser = "edge"                  # "edge", "chrome", または "firefox"
headless = false
```

### Playwright を使用する場合

```toml
[assign_to_copilot]
enabled = true
automated = true
automation_backend = "playwright"  # "playwright" を指定
wait_seconds = 10
browser = "chromium"                # "chromium", "firefox", または "webkit"
headless = false
```

## 比較ポイント

### Selenium の特徴

**利点：**
- ✅ 業界標準で成熟している（2004年から）
- ✅ 豊富なドキュメントとコミュニティサポート
- ✅ 実際のブラウザインストールを使用
- ✅ 広範なトラブルシューティングリソース

**欠点：**
- ❌ ドライバーの個別管理が必要
- ❌ 要素の待機を手動で設定
- ❌ セットアップがやや複雑

**推奨される場合：**
- 最大限の安定性とコミュニティサポートが必要
- 実際のブラウザインストールを使用したい
- チームがすでにSeleniumに慣れている

### Playwright の特徴

**利点：**
- ✅ モダンで高速（2020年リリース）
- ✅ ブラウザの自動管理
- ✅ 自動待機機能
- ✅ より良いAPI設計とエラーハンドリング
- ✅ 複数のブラウザエンジンをサポート

**欠点：**
- ❌ 比較的新しい（コミュニティは小さい）
- ❌ トラブルシューティング資料が少ない

**推奨される場合：**
- より速い実行速度が必要
- 自動ブラウザ管理を好む
- モダンなAPI設計と自動待機機能を重視
- 複数のブラウザエンジンのサポートが必要

## 検証手順

### ステップ 1: 両方のバックエンドをインストール

```bash
# Selenium
pip install selenium webdriver-manager

# Playwright
pip install playwright
playwright install
```

### ステップ 2: 比較デモを実行

```bash
python demo_comparison.py
```

### ステップ 3: 実際の使用で検証

1. `config.toml` で Selenium を設定して実行
2. 動作、速度、安定性を確認
3. `config.toml` で Playwright を設定して実行
4. 同じ指標で評価
5. 結果を比較

### ステップ 4: 評価基準

以下の基準で評価することをお勧めします：

1. **セットアップの容易さ**
   - インストールの簡単さ
   - 設定の複雑さ
   - ブラウザドライバーの管理

2. **実行速度**
   - ページの読み込み時間
   - ボタンクリックの応答時間
   - 全体的な実行時間

3. **安定性**
   - 成功率
   - エラーの頻度
   - エラーメッセージの分かりやすさ

4. **保守性**
   - コードの読みやすさ
   - デバッグの容易さ
   - ドキュメントの質

## 結論

このPRの目的は、両方のバックエンドを実装し、実際の使用を通じてどちらがこのプロジェクトの目的により適しているかを検証できるようにすることです。

**次のステップ：**
1. 両方のバックエンドを実際の環境でテスト
2. 上記の評価基準に基づいて結果を比較
3. プロジェクトに最適なバックエンドを決定
4. 必要に応じて設定とドキュメントを更新

## トラブルシューティング

### Selenium の一般的な問題

**問題：** "WebDriver not found"
**解決策：** `pip install webdriver-manager` を実行

**問題：** ブラウザが起動しない
**解決策：** ブラウザとドライバーのバージョンを確認

### Playwright の一般的な問題

**問題：** "Browser not found"
**解決策：** `playwright install` を実行

**問題：** 権限エラー
**解決策：** 管理者権限で `playwright install` を実行

## 参考資料

- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [Playwright Documentation](https://playwright.dev/python/)
- [browser-automation-approaches.md](docs/browser-automation-approaches.md)
- [browser-automation-approaches.en.md](docs/browser-automation-approaches.en.md)
