# ブラウザ自動操縦によるボタン押下の実現方法

## 要件
PR 65をもとに、以下の機能を実現する：
1. ブラウザを起動する
2. 10秒待つ
3. 自動操縦で2つのボタンを押す：
   - "Assign to Copilot" ボタン
   - "Assign" ボタン

**対象環境**: Windows PC

## 検討する方法

### 方法1: Selenium WebDriver（推奨）

**概要**: ブラウザ自動化の業界標準ツール

**メリット**:
- ✅ Windows対応（Chrome, Edge, Firefoxなど）
- ✅ 安定性が高い
- ✅ 豊富なドキュメントとコミュニティサポート
- ✅ 要素の待機や検出が容易
- ✅ GitHubのログイン状態を維持可能（既存のプロファイルを使用）

**デメリット**:
- ❌ 追加の依存関係が必要（selenium, webdriver）
- ❌ ブラウザドライバー（ChromeDriver, EdgeDriverなど）のインストールが必要

**実装例**:
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def assign_issue_to_copilot_automated(issue_url):
    # Edgeを使用（Windowsに標準搭載）
    options = webdriver.EdgeOptions()
    # 既存のユーザープロファイルを使用してログイン状態を維持
    # options.add_argument("user-data-dir=C:\\Users\\<username>\\AppData\\Local\\Microsoft\\Edge\\User Data")
    
    driver = webdriver.Edge(options=options)
    
    try:
        # issueを開く
        driver.get(issue_url)
        
        # 10秒待つ
        time.sleep(10)
        
        # "Assign to Copilot" ボタンを探してクリック
        wait = WebDriverWait(driver, 10)
        assign_to_copilot_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Assign to Copilot')]"))
        )
        assign_to_copilot_btn.click()
        
        # 少し待つ
        time.sleep(2)
        
        # "Assign" ボタンを探してクリック
        assign_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Assign')]"))
        )
        assign_btn.click()
        
        print("✓ Successfully assigned issue to Copilot")
        
        # ブラウザを閉じるかどうかはオプション
        time.sleep(2)
        driver.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to automate button clicks: {e}")
        driver.quit()
        return False
```

**必要な依存関係**:
```
selenium>=4.0.0
webdriver-manager  # ドライバーの自動管理
```

### 方法2: Playwright（モダンな代替案）

**概要**: マイクロソフト製の最新ブラウザ自動化ツール

**メリット**:
- ✅ Windows対応
- ✅ より高速で安定
- ✅ ブラウザドライバーの自動管理
- ✅ モダンなAPI設計
- ✅ 既存のブラウザコンテキストを使用可能

**デメリット**:
- ❌ 追加の依存関係が必要
- ❌ Seleniumよりも新しく、採用例が少ない

**実装例**:
```python
from playwright.sync_api import sync_playwright
import time

def assign_issue_to_copilot_automated(issue_url):
    with sync_playwright() as p:
        # Chromiumを起動（またはchrome, edge, firefox）
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # issueを開く
            page.goto(issue_url)
            
            # 10秒待つ
            time.sleep(10)
            
            # "Assign to Copilot" ボタンをクリック
            page.click("button:has-text('Assign to Copilot')")
            
            # 少し待つ
            time.sleep(2)
            
            # "Assign" ボタンをクリック
            page.click("button:has-text('Assign')")
            
            print("✓ Successfully assigned issue to Copilot")
            
            time.sleep(2)
            browser.close()
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to automate button clicks: {e}")
            browser.close()
            return False
```

**必要な依存関係**:
```
playwright>=1.40.0
```

インストール後：
```bash
playwright install chromium
```

### 方法3: PyAutoGUI（画面座標ベース）

**概要**: 画面座標やキーボード/マウス操作を直接制御

**メリット**:
- ✅ Windows対応
- ✅ シンプルな実装

**デメリット**:
- ❌ 画面解像度やウィンドウ位置に依存
- ❌ ボタンの位置が変わると動作しない
- ❌ 非常に不安定
- ❌ 推奨されない方法

**実装例**（参考のみ）:
```python
import pyautogui
import time
import webbrowser

def assign_issue_to_copilot_automated(issue_url):
    # ブラウザを開く
    webbrowser.open(issue_url)
    
    # 10秒待つ
    time.sleep(10)
    
    # 画面上のボタンを探してクリック（非推奨）
    # ボタンの画像認識が必要
    try:
        location = pyautogui.locateOnScreen('assign_to_copilot_button.png')
        if location:
            pyautogui.click(location)
    except:
        pass
```

### 方法4: AutoHotkey（Windows専用）

**概要**: Windows専用の自動化スクリプト言語

**メリット**:
- ✅ Windows専用で最適化
- ✅ キーボード/マウス操作が得意

**デメリット**:
- ❌ Python統合が複雑
- ❌ HTML要素の検出が困難
- ❌ 別言語の学習が必要

## 推奨案

### 実装状況: 両方のバックエンドをサポート

現在、両方のブラウザ自動化バックエンド（SeleniumとPlaywright）が実装されており、設定で選択可能です。

### Selenium WebDriver（方法1）

**特徴**：
1. **安定性**: 業界標準で長年の実績
2. **Windows対応**: Edge（Windows標準ブラウザ）を使用可能
3. **要素検出**: HTML要素を確実に検出してクリック
4. **保守性**: 豊富なドキュメントとサンプルコード
5. **既存実装との統合**: 現在の`assign_issue_to_copilot()`関数を拡張可能

### Playwright（方法2）

**特徴**：
1. **速度**: より高速な実行
2. **簡単なセットアップ**: ブラウザが自動管理される
3. **モダンAPI**: 自動待機機能を持つ最新のAPI設計
4. **複数ブラウザエンジン**: Chromium、Firefox、WebKitをサポート

### 実装手順

1. **依存関係の追加**（いずれかまたは両方）:
   ```
   # Selenium
   selenium>=4.0.0
   webdriver-manager>=4.0.0
   
   # Playwright
   playwright>=1.40.0
   ```

2. **設定オプションの追加**（config.toml）:
   ```toml
   [assign_to_copilot]
   enabled = false
   automated = false              # 自動ボタンクリックを有効化
   automation_backend = "selenium" # バックエンド: "selenium" または "playwright"
   wait_seconds = 10               # クリック前の待機時間
   browser = "edge"                # Selenium: "edge", "chrome", "firefox"
                                   # Playwright: "chromium", "firefox", "webkit"
   headless = false                # ヘッドレスモード（ウィンドウを表示しない）
   ```

3. **使用方法**:
   - `automation_backend`を"selenium"または"playwright"に設定
   - 両方をインストールして比較することも可能
   - デフォルトはSelenium

4. **エラーハンドリング**:
   - バックエンドが利用できない場合は、従来の手動方式にフォールバック
   - ログイン状態のチェック
   - ボタンが見つからない場合の処理

### 比較と検証

両方のバックエンドを実装したことで、以下が可能になりました：

1. **パフォーマンス比較**: `demo_comparison.py`スクリプトで両者を比較
2. **安定性検証**: 実際の環境で両方をテスト
3. **使いやすさ評価**: セットアップと保守性を比較

**比較デモの実行**:
```bash
python demo_comparison.py
```

## 注意事項

1. **GitHubのログイン状態**:
   - 自動化にはGitHubへのログインが必要
   - ユーザープロファイルを使用するか、認証情報を設定

2. **セキュリティ**:
   - 認証情報をコードに埋め込まない
   - 既存のブラウザセッションを利用推奨

3. **GitHubの利用規約**:
   - 自動化がGitHubのToSに違反しないことを確認
   - 過度なリクエストを避ける

4. **保守性**:
   - GitHubのUIが変更された場合、セレクターの更新が必要

## 次のステップ

1. ✅ 方法の調査と文書化（完了）
2. ✅ Selenium WebDriverを使用したプロトタイプの実装（完了）
3. ✅ Playwrightバックエンドの実装（完了）
4. ✅ 設定オプションの追加（完了）
5. ✅ 既存コードとの統合（完了）
6. ✅ テストとドキュメント更新（完了）
7. 🔄 実際の環境でのテストと検証
8. 🔄 どちらがより適しているかの評価
