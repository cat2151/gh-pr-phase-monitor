Last updated: 2026-01-04

# 開発状況生成プロンプト（開発者向け）

## 生成するもの：
- 現在openされているissuesを3行で要約する
- 次の一手の候補を3つlistする
- 次の一手の候補3つそれぞれについて、極力小さく分解して、その最初の小さな一歩を書く

## 生成しないもの：
- 「今日のissue目標」などuserに提案するもの
  - ハルシネーションの温床なので生成しない
- ハルシネーションしそうなものは生成しない（例、無価値なtaskや新issueを勝手に妄想してそれをuserに提案する等）
- プロジェクト構造情報（来訪者向け情報のため、別ファイルで管理）

## 「Agent実行プロンプト」生成ガイドライン：
「Agent実行プロンプト」作成時は以下の要素を必ず含めてください：

### 必須要素
1. **対象ファイル**: 分析/編集する具体的なファイルパス
2. **実行内容**: 具体的な分析や変更内容（「分析してください」ではなく「XXXファイルのYYY機能を分析し、ZZZの観点でmarkdown形式で出力してください」）
3. **確認事項**: 変更前に確認すべき依存関係や制約
4. **期待する出力**: markdown形式での結果や、具体的なファイル変更

### Agent実行プロンプト例

**良い例（上記「必須要素」4項目を含む具体的なプロンプト形式）**:
```
対象ファイル: `.github/workflows/translate-readme.yml`と`.github/workflows/call-translate-readme.yml`

実行内容: 対象ファイルについて、外部プロジェクトから利用する際に必要な設定項目を洗い出し、以下の観点から分析してください：
1) 必須入力パラメータ（target-branch等）
2) 必須シークレット（GEMINI_API_KEY）
3) ファイル配置の前提条件（README.ja.mdの存在）
4) 外部プロジェクトでの利用時に必要な追加設定

確認事項: 作業前に既存のworkflowファイルとの依存関係、および他のREADME関連ファイルとの整合性を確認してください。

期待する出力: 外部プロジェクトがこの`call-translate-readme.yml`を導入する際の手順書をmarkdown形式で生成してください。具体的には：必須パラメータの設定方法、シークレットの登録手順、前提条件の確認項目を含めてください。
```

**避けるべき例**:
- callgraphについて調べてください
- ワークフローを分析してください
- issue-noteの処理フローを確認してください

## 出力フォーマット：
以下のMarkdown形式で出力してください：

```markdown
# Development Status

## 現在のIssues
[以下の形式で3行でオープン中のissuesを要約。issue番号を必ず書く]
- [1行目の説明]
- [2行目の説明]
- [3行目の説明]

## 次の一手候補
1. [候補1のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```

2. [候補2のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```

3. [候補3のタイトル。issue番号を必ず書く]
   - 最初の小さな一歩: [具体的で実行可能な最初のアクション]
   - Agent実行プロンプト:
     ```
     対象ファイル: [分析/編集する具体的なファイルパス]

     実行内容: [具体的な分析や変更内容を記述]

     確認事項: [変更前に確認すべき依存関係や制約]

     期待する出力: [markdown形式での結果や、具体的なファイル変更の説明]
     ```
```


# 開発状況情報
- 以下の開発状況情報を参考にしてください。
- Issue番号を記載する際は、必ず [Issue #番号](../issue-notes/番号.md) の形式でMarkdownリンクとして記載してください。

## プロジェクトのファイル一覧
- .editorconfig
- .github/actions-tmp/.github/workflows/call-callgraph.yml
- .github/actions-tmp/.github/workflows/call-daily-project-summary.yml
- .github/actions-tmp/.github/workflows/call-issue-note.yml
- .github/actions-tmp/.github/workflows/call-rust-windows-check.yml
- .github/actions-tmp/.github/workflows/call-translate-readme.yml
- .github/actions-tmp/.github/workflows/callgraph.yml
- .github/actions-tmp/.github/workflows/check-recent-human-commit.yml
- .github/actions-tmp/.github/workflows/daily-project-summary.yml
- .github/actions-tmp/.github/workflows/issue-note.yml
- .github/actions-tmp/.github/workflows/rust-windows-check.yml
- .github/actions-tmp/.github/workflows/translate-readme.yml
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/callgraph.ql
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/codeql-pack.lock.yml
- .github/actions-tmp/.github_automation/callgraph/codeql-queries/qlpack.yml
- .github/actions-tmp/.github_automation/callgraph/config/example.json
- .github/actions-tmp/.github_automation/callgraph/docs/callgraph.md
- .github/actions-tmp/.github_automation/callgraph/presets/callgraph.js
- .github/actions-tmp/.github_automation/callgraph/presets/style.css
- .github/actions-tmp/.github_automation/callgraph/scripts/analyze-codeql.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/callgraph-utils.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/check-codeql-exists.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/check-node-version.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/common-utils.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/copy-commit-results.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/extract-sarif-info.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/find-process-results.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/generate-html-graph.cjs
- .github/actions-tmp/.github_automation/callgraph/scripts/generateHTML.cjs
- .github/actions-tmp/.github_automation/check_recent_human_commit/scripts/check-recent-human-commit.cjs
- .github/actions-tmp/.github_automation/project_summary/docs/daily-summary-setup.md
- .github/actions-tmp/.github_automation/project_summary/prompts/development-status-prompt.md
- .github/actions-tmp/.github_automation/project_summary/prompts/project-overview-prompt.md
- .github/actions-tmp/.github_automation/project_summary/scripts/ProjectSummaryCoordinator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/DevelopmentStatusGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/GitUtils.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/development/IssueTracker.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/generate-project-summary.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/CodeAnalyzer.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectAnalysisOrchestrator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectDataCollector.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectDataFormatter.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/overview/ProjectOverviewGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/BaseGenerator.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/FileSystemUtils.cjs
- .github/actions-tmp/.github_automation/project_summary/scripts/shared/ProjectFileUtils.cjs
- .github/actions-tmp/.github_automation/translate/docs/TRANSLATION_SETUP.md
- .github/actions-tmp/.github_automation/translate/scripts/translate-readme.cjs
- .github/actions-tmp/.gitignore
- .github/actions-tmp/.vscode/settings.json
- .github/actions-tmp/LICENSE
- .github/actions-tmp/README.ja.md
- .github/actions-tmp/README.md
- .github/actions-tmp/_config.yml
- .github/actions-tmp/generated-docs/callgraph.html
- .github/actions-tmp/generated-docs/callgraph.js
- .github/actions-tmp/generated-docs/development-status-generated-prompt.md
- .github/actions-tmp/generated-docs/development-status.md
- .github/actions-tmp/generated-docs/project-overview-generated-prompt.md
- .github/actions-tmp/generated-docs/project-overview.md
- .github/actions-tmp/generated-docs/style.css
- .github/actions-tmp/googled947dc864c270e07.html
- .github/actions-tmp/issue-notes/10.md
- .github/actions-tmp/issue-notes/11.md
- .github/actions-tmp/issue-notes/12.md
- .github/actions-tmp/issue-notes/13.md
- .github/actions-tmp/issue-notes/14.md
- .github/actions-tmp/issue-notes/15.md
- .github/actions-tmp/issue-notes/16.md
- .github/actions-tmp/issue-notes/17.md
- .github/actions-tmp/issue-notes/18.md
- .github/actions-tmp/issue-notes/19.md
- .github/actions-tmp/issue-notes/2.md
- .github/actions-tmp/issue-notes/20.md
- .github/actions-tmp/issue-notes/21.md
- .github/actions-tmp/issue-notes/22.md
- .github/actions-tmp/issue-notes/23.md
- .github/actions-tmp/issue-notes/24.md
- .github/actions-tmp/issue-notes/25.md
- .github/actions-tmp/issue-notes/26.md
- .github/actions-tmp/issue-notes/27.md
- .github/actions-tmp/issue-notes/28.md
- .github/actions-tmp/issue-notes/29.md
- .github/actions-tmp/issue-notes/3.md
- .github/actions-tmp/issue-notes/30.md
- .github/actions-tmp/issue-notes/4.md
- .github/actions-tmp/issue-notes/7.md
- .github/actions-tmp/issue-notes/8.md
- .github/actions-tmp/issue-notes/9.md
- .github/actions-tmp/package-lock.json
- .github/actions-tmp/package.json
- .github/actions-tmp/src/main.js
- .github/workflows/call-daily-project-summary.yml
- .github/workflows/call-issue-note.yml
- .github/workflows/call-translate-readme.yml
- .gitignore
- .vscode/settings.json
- LICENSE
- README.ja.md
- README.md
- STRUCTURE.md
- _config.yml
- config.toml.example
- generated-docs/project-overview-generated-prompt.md
- cat-github-watcher.py
- pytest.ini
- ruff.toml
- src/__init__.py
- src/gh_pr_phase_monitor/__init__.py
- src/gh_pr_phase_monitor/colors.py
- src/gh_pr_phase_monitor/comment_manager.py
- src/gh_pr_phase_monitor/config.py
- src/gh_pr_phase_monitor/github_client.py
- src/gh_pr_phase_monitor/main.py
- src/gh_pr_phase_monitor/phase_detector.py
- src/gh_pr_phase_monitor/pr_actions.py
- tests/test_interval_parsing.py
- tests/test_phase_detection.py
- tests/test_post_comment.py
- tests/test_pr_actions.py

## 現在のオープンIssues
## [Issue #34](../issue-notes/34.md): Display issues from repos without open PRs when all PRs are in LLM working phase
When all monitored PRs are in "LLM working" phase, users need visibility into what to work on next. This PR adds automatic discovery and display of issues from repositories that have no open PRs.

## Changes

### New GraphQL queries (`github_client.py`)
- `get_all_repositories()` - Fetches all user ...
ラベル: 
--- issue-notes/34.md の内容 ---

```markdown

```

## [Issue #33](../issue-notes/33.md): すべてがLLM workingのとき、ghで認証済みのGitHubアカウント（つまり自分）の「全リポジトリ」のうち「openなprがなく、openなissueのあるリポジトリ」を得て、そのリポジトリ群のissueのtimestamp降順sortで先頭10件を表示する

ラベル: 
--- issue-notes/33.md の内容 ---

```markdown

```

## [Issue #32](../issue-notes/32.md): 「Posting comment for phase2... / Comment already exists, skipping / Comment posted successfully」と表示され、userが混乱する。skippingのあとはpostedを表示しないようにする

ラベル: 
--- issue-notes/32.md の内容 ---

```markdown

```

## [Issue #21](../issue-notes/21.md): pyについて、前回とまったく同じ表示内容かつLLM workingであれば、表示内容を変更し、「現在、検知してから3分20秒経過」のような表示をする。さらに、その表示時と、待ち時間中は1秒ごと、エスケープシーケンスを利用し、前回の「3分19秒経過」を消して「3分20秒経過」のように書き換える

ラベル: 
--- issue-notes/21.md の内容 ---

```markdown

```

## [Issue #7](../issue-notes/7.md): リポジトリ名を cat-github-pr-watcher にする。cat-file-watcher同様、最初は範囲を絞った名前で、中身が多少今後拡大しても許容とするつもり

ラベル: 
--- issue-notes/7.md の内容 ---

```markdown

```

## ドキュメントで言及されているファイルの内容
### .github/actions-tmp/issue-notes/2.md
```md
{% raw %}
# issue GitHub Actions「関数コールグラフhtmlビジュアライズ生成」を共通ワークフロー化する #2
[issues #2](https://github.com/cat2151/github-actions/issues/2)


# prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlファイルを、以下の2つのファイルに分割してください。
1. 共通ワークフロー       cat2151/github-actions/.github/workflows/callgraph_enhanced.yml
2. 呼び出し元ワークフロー cat2151/github-actions/.github/workflows/call-callgraph_enhanced.yml
まずplanしてください
```

# 結果
- indent
    - linter？がindentのエラーを出しているがyml内容は見た感じOK
    - テキストエディタとagentの相性問題と判断する
    - 別のテキストエディタでsaveしなおし、テキストエディタをreload
    - indentのエラーは解消した
- LLMレビュー
    - agent以外の複数のLLMにレビューさせる
    - prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
以下の2つのファイルをレビューしてください。最優先で、エラーが発生するかどうかだけレビューしてください。エラー以外の改善事項のチェックをするかわりに、エラー発生有無チェックに最大限注力してください。

--- 共通ワークフロー

# GitHub Actions Reusable Workflow for Call Graph Generation
name: Generate Call Graph

# TODO Windowsネイティブでのtestをしていた名残が残っているので、今後整理していく。今はWSL act でtestしており、Windowsネイティブ環境依存問題が解決した
#  ChatGPTにレビューさせるとそこそこ有用そうな提案が得られたので、今後それをやる予定
#  agentに自己チェックさせる手も、セカンドオピニオンとして選択肢に入れておく

on:
  workflow_call:

jobs:
  check-commits:
    runs-on: ubuntu-latest
    outputs:
      should-run: ${{ steps.check.outputs.should-run }}
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 50 # 過去のコミットを取得

      - name: Check for user commits in last 24 hours
        id: check
        run: |
          node .github/scripts/callgraph_enhanced/check-commits.cjs

  generate-callgraph:
    needs: check-commits
    if: needs.check-commits.outputs.should-run == 'true'
    runs-on: ubuntu-latest
    permissions:
      contents: write
      security-events: write
      actions: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set Git identity
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

      - name: Remove old CodeQL packages cache
        run: rm -rf ~/.codeql/packages

      - name: Check Node.js version
        run: |
          node .github/scripts/callgraph_enhanced/check-node-version.cjs

      - name: Install CodeQL CLI
        run: |
          wget https://github.com/github/codeql-cli-binaries/releases/download/v2.22.1/codeql-linux64.zip
          unzip codeql-linux64.zip
          sudo mv codeql /opt/codeql
          echo "/opt/codeql" >> $GITHUB_PATH

      - name: Install CodeQL query packs
        run: |
          /opt/codeql/codeql pack install .github/codeql-queries

      - name: Check CodeQL exists
        run: |
          node .github/scripts/callgraph_enhanced/check-codeql-exists.cjs

      - name: Verify CodeQL Configuration
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs verify-config

      - name: Remove existing CodeQL DB (if any)
        run: |
          rm -rf codeql-db

      - name: Perform CodeQL Analysis
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs analyze

      - name: Check CodeQL Analysis Results
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs check-results

      - name: Debug CodeQL execution
        run: |
          node .github/scripts/callgraph_enhanced/analyze-codeql.cjs debug

      - name: Wait for CodeQL results
        run: |
          node -e "setTimeout(()=>{}, 10000)"

      - name: Find and process CodeQL results
        run: |
          node .github/scripts/callgraph_enhanced/find-process-results.cjs

      - name: Generate HTML graph
        run: |
          node .github/scripts/callgraph_enhanced/generate-html-graph.cjs

      - name: Copy files to generated-docs and commit results
        run: |
          node .github/scripts/callgraph_enhanced/copy-commit-results.cjs

--- 呼び出し元
# 呼び出し元ワークフロー: call-callgraph_enhanced.yml
name: Call Call Graph Enhanced

on:
  schedule:
    # 毎日午前5時(JST) = UTC 20:00前日
    - cron: '0 20 * * *'
  workflow_dispatch:

jobs:
  call-callgraph-enhanced:
    # uses: cat2151/github-actions/.github/workflows/callgraph_enhanced.yml
    uses: ./.github/workflows/callgraph_enhanced.yml # ローカルでのテスト用
```

# レビュー結果OKと判断する
- レビュー結果を人力でレビューした形になった

# test
- #4 同様にローカル WSL + act でtestする
- エラー。userのtest設計ミス。
  - scriptの挙動 : src/ がある前提
  - 今回の共通ワークフローのリポジトリ : src/ がない
  - 今回testで実現したいこと
    - 仮のソースでよいので、関数コールグラフを生成させる
  - 対策
    - src/ にダミーを配置する
- test green
  - ただしcommit pushはしてないので、html内容が0件NG、といったケースの検知はできない
  - もしそうなったら別issueとしよう

# test green

# commit用に、yml 呼び出し元 uses をlocal用から本番用に書き換える

# closeとする
- もしhtml内容が0件NG、などになったら、別issueとするつもり

{% endraw %}
```

### .github/actions-tmp/issue-notes/21.md
```md
{% raw %}
# issue project-summary の development-status 生成時、project-overviewが生成済みのproject-overview.mdもpromptに添付、を試す #21
[issues #21](https://github.com/cat2151/github-actions/issues/21)

# 何が困るの？
- project-overview.mdがpromptに添付されていたほうが、Geminiの生成品質が改善できる可能性がある。
    - メリットは、ファイル一覧、関数一覧、をGeminiにわたせること

# 検討事項
- 課題、その一覧に付記されている「ファイルや関数の要約」は、Geminiが「ファイル名や関数名を元に生成しただけ」で、「ファイル内容や関数内容を参照せずに生成した」可能性が高い
    - 対策、project-overview.mdに依存しない。
        - 方法、新規関数をagentに実装させる
            - 新規関数で、ファイル一覧と関数一覧を生成する
        - 根拠、そのほうが、シンプルに目的を達成できる可能性が高そう。
        - 根拠、project-overview.mdだと、不具合として.github 配下のymlがlistに含まれておらず、ymlに関するissue、に関する生成、をするとき不具合の可能性がありそう。そういった、別機能の不具合に影響されがち。
- 課題、早期に実施したほうが毎日好影響が出る可能性がある
    - 対策、上記検討事項の対処は後回しにして、先に実装してみる
    - agentに投げる
- 課題、ProjectSummaryCoordinator をみたところ、並列処理されている
    - なので、project-overview.mdを参照したいときに、まだ生成されていない、という可能性が高い
    - 対策、前述の、新規関数で、ファイル一覧と関数一覧を生成させる

# agentに投げるための整理
- 編集対象ファイル
    - prompt
        - .github_automation/project_summary/prompts/development-status-prompt.md
        - 編集内容
            - projectのファイル一覧を埋め込む用の、プレースホルダーを追加する
    - source
        - .github_automation/project_summary/scripts/development/DevelopmentStatusGenerator.cjs
        - 編集内容
            - projectのファイル一覧を生成する関数、を実装し、
            - それを前述のプレースホルダーに埋め込む

# agentに投げて実装させた

# test結果
- 以下が不要
    - .git/
    - node_modules/

# どうする？
- agentに上記を変更させた
- testする

# 結果
- test greenとなった

# まとめ
- issueのtitleからは仕様変更した。
    - projectのfile一覧をpromptに含める、とした。
    - そのほうがpromptとして、よい生成結果が期待できる、と判断した。
- test greenとなった

# closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/3.md
```md
{% raw %}
# issue GitHub Actions「issue note生成」を共通ワークフロー化する #3
[issues #3](https://github.com/cat2151/github-actions/issues/3)

- 前提
  - userは、translateのworkflowを共通ワークフロー化し、動くようにしたので、共通ワークフロー化の知識がある
  - よって、今回は、promptでplanさせ、そのplanをuserがレビューし、planの改善を指示できるので、ハルシネーションのリスクを下げることができる

- prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlはまだ共通ワークフロー化されず、
呼び出し元からコピーされたままの状態です。
このymlファイル名のまま、
中身を共通ワークフロー化してください。
呼び出し元ymlは別途書きますので気にしないでください。
まずplanしてください
```

- plan 生成結果
```
共通ワークフロー化のためのplanは以下の通りです。

1. 目的
現在の issue-note.yml を「共通ワークフロー」として再設計し、他リポジトリや他ワークフローから workflow_call で呼び出せるようにする。
2. 主な変更点
on: トリガーを workflow_call に変更（直接イベントで起動しない）。
必要な入力（inputs）やシークレット（secrets）を workflow_call セクションで定義。
github.event.issue などのイベント依存部分を、inputs経由で受け取る形に修正。
既存の処理（issueノート生成、コミット、issue body更新）はそのまま活かすが、パラメータ化する。
3. 具体的な修正内容
on: issues: → on: workflow_call: に変更。
inputs で必要な値（例: issue_title, issue_number, issue_body, issue_url など）を受け取る。
スクリプト内の ${{ github.event.issue.xxx }} を ${{ inputs.xxx }} に置換。
github-script ステップも同様にinputsを参照。
必要に応じて secrets も workflow_call で受け取れるようにする。
4. ファイル名・配置
ファイル名はそのまま issue-note.yml。
配置場所は workflows でOK（共通ワークフローとしてもこの場所で良い）。
5. 呼び出し元への影響
呼び出し元ワークフローで uses: <repo>/.github/workflows/issue-note.yml@main のように参照し、inputsを渡す形になる。
このplanで進めます。次に、実際の共通ワークフロー化のためのyml修正案を作成しますか？
```

- userがplanレビューし、OKを出した
- agentに生成結果ymlをレビューさせた、OKとなった
  - userはこのレビューは認知負荷が高いのでskipとする（単純な細かい間違い探し作業になるので、それはagentに任せた）
-  エラー。呼び出し元ymlのエラーがあり修正。共通ワークフローのエラー指摘があり、共通ワークフロー側の修正が必要となった
```
原因の分析：

呼び出し元（tonejs-mml-to-jsonのissue-note.yml）は、reusable workflow（cat2151/github-actions/.github/workflows/issue-note.yml@main）をusesで呼び出し、inputsをwithで渡しています。
共通ワークフロー（reusable workflow）は inputs を workflow_call で受け取り、各ステップで ${{ inputs.xxx }} で参照しています。
しかし、エラーが発生したのは actions/github-script@v7 の script 内です。
エラーの本質的な原因：

actions/github-script の script: で ${{ inputs.issue_number }} のような式を直接 JavaScript テンプレートリテラル内で使っていますが、これはサポートされていません。
script: の中は JavaScript であり、YAMLの ${{ ... }} は展開されません（または意図通りに展開されません）。
そのため、inputs 変数は script 内の JavaScript で未定義となり、ReferenceError になります。
正しい書き方：

actions/github-script の script: でワークフローの inputs を使いたい場合は、with: で input を environment 変数や script の引数として渡し、JavaScript で process.env から取得するか、github-script の input 機能を使う必要があります。
例（修正版）：

このように、inputs の値を env で渡し、script 内では process.env で参照してください。

まとめ：

actions/github-script の script 内で ${{ inputs.xxx }} を直接使うと ReferenceError になる
env: で値を渡し、process.env で参照するのが正しい
修正が必要です。修正版のワークフローが必要な場合はお知らせください。
```

- test green
- closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/4.md
```md
{% raw %}
# issue GitHub Actions「project概要生成」を共通ワークフロー化する #4
[issues #4](https://github.com/cat2151/github-actions/issues/4)

# prompt
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
このymlファイルを、以下の2つのファイルに分割してください。
1. 共通ワークフロー       cat2151/github-actions/.github/workflows/daily-project-summary.yml
2. 呼び出し元ワークフロー cat2151/github-actions/.github/workflows/call-daily-project-summary.yml
まずplanしてください
```

# 結果、あちこちハルシネーションのあるymlが生成された
- agentの挙動があからさまにハルシネーション
    - インデントが修正できない、「失敗した」という
    - 構文誤りを認識できない
- 人力で修正した

# このagentによるセルフレビューが信頼できないため、別のLLMによるセカンドオピニオンを試す
```
あなたはGitHub Actionsと共通ワークフローのスペシャリストです。
以下の2つのファイルをレビューしてください。最優先で、エラーが発生するかどうかだけレビューてください。エラー以外の改善事項のチェックをするかわりに、エラー発生有無チェックに最大限注力してください。

--- 呼び出し元

name: Call Daily Project Summary

on:
  schedule:
    # 日本時間 07:00 (UTC 22:00 前日)
    - cron: '0 22 * * *'
  workflow_dispatch:

jobs:
  call-daily-project-summary:
    uses: cat2151/github-actions/.github/workflows/daily-project-summary.yml
    secrets:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

--- 共通ワークフロー
name: Daily Project Summary
on:
  workflow_call:

jobs:
  generate-summary:
    runs-on: ubuntu-latest

    permissions:
      contents: write
      issues: read
      pull-requests: read

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0  # 履歴を取得するため

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          # 一時的なディレクトリで依存関係をインストール
          mkdir -p /tmp/summary-deps
          cd /tmp/summary-deps
          npm init -y
          npm install @google/generative-ai @octokit/rest
          # generated-docsディレクトリを作成
          mkdir -p $GITHUB_WORKSPACE/generated-docs

      - name: Generate project summary
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          NODE_PATH: /tmp/summary-deps/node_modules
        run: |
          node .github/scripts/generate-project-summary.cjs

      - name: Check for generated summaries
        id: check_summaries
        run: |
          if [ -f "generated-docs/project-overview.md" ] && [ -f "generated-docs/development-status.md" ]; then
            echo "summaries_generated=true" >> $GITHUB_OUTPUT
          else
            echo "summaries_generated=false" >> $GITHUB_OUTPUT
          fi

      - name: Commit and push summaries
        if: steps.check_summaries.outputs.summaries_generated == 'true'
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          # package.jsonの変更のみリセット（generated-docsは保持）
          git restore package.json 2>/dev/null || true
          # サマリーファイルのみを追加
          git add generated-docs/project-overview.md
          git add generated-docs/development-status.md
          git commit -m "Update project summaries (overview & development status)"
          git push

      - name: Summary generation result
        run: |
          if [ "${{ steps.check_summaries.outputs.summaries_generated }}" == "true" ]; then
            echo "✅ Project summaries updated successfully"
            echo "📊 Generated: project-overview.md & development-status.md"
          else
            echo "ℹ️ No summaries generated (likely no user commits in the last 24 hours)"
          fi
```

# 上記promptで、2つのLLMにレビューさせ、合格した

# 細部を、先行する2つのymlを参照に手直しした

# ローカルtestをしてからcommitできるとよい。方法を検討する
- ローカルtestのメリット
    - 素早く修正のサイクルをまわせる
    - ムダにgit historyを汚さない
        - これまでの事例：「実装したつもり」「エラー。修正したつもり」「エラー。修正したつもり」...（以降エラー多数）
- 方法
    - ※検討、WSL + act を環境構築済みである。test可能であると判断する
    - 呼び出し元のURLをコメントアウトし、相対パス記述にする
    - ※備考、テスト成功すると結果がcommit pushされる。それでよしとする
- 結果
    - OK
    - secretsを簡略化できるか試した、できなかった、現状のsecrets記述が今わかっている範囲でベストと判断する
    - OK

# test green

# commit用に、yml 呼び出し元 uses をlocal用から本番用に書き換える

# closeとする

{% endraw %}
```

### .github/actions-tmp/issue-notes/7.md
```md
{% raw %}
# issue issue note生成できるかのtest用 #7
[issues #7](https://github.com/cat2151/github-actions/issues/7)

- 生成できた
- closeとする

{% endraw %}
```

### src/gh_pr_phase_monitor/github_client.py
```py
{% raw %}
"""
GitHub API client for interacting with repositories, PRs, and comments
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

# Cache for current user to avoid repeated subprocess calls
_current_user_cache = None


def get_current_user() -> str:
    """Get the current authenticated GitHub user's login

    Returns:
        The login name of the current authenticated user

    Raises:
        RuntimeError: If unable to retrieve the current user (authentication failure)
    """
    global _current_user_cache

    # Return cached value if available (only cache successful authentication)
    if _current_user_cache is not None and _current_user_cache != "":
        return _current_user_cache

    cmd = ["gh", "api", "user", "--jq", ".login"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        _current_user_cache = result.stdout.strip()
        return _current_user_cache
    except subprocess.CalledProcessError as e:
        error_msg = (
            "Failed to retrieve current GitHub user via `gh api user`. "
            "GitHub CLI authentication is required for phase3 comments. "
            "Please run `gh auth login` or `gh auth status` to check your authentication."
        )
        print(f"\n[ERROR] {error_msg}")
        if e.stderr:
            print(f"Details: {e.stderr}")
        raise RuntimeError(error_msg) from e


def get_repositories_with_open_prs() -> List[Dict[str, Any]]:
    """Get all repositories with open PR counts using GraphQL (Phase 1)

    Returns:
        List of repositories with name and open PR count
        Example: [{"name": "repo1", "owner": "user", "openPRCount": 2}, ...]
    """
    current_user = get_current_user()

    # GraphQL query to get all repositories with open PR counts
    # Only includes user-owned repos (not organization repos)
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: [OWNER]) {
          nodes {
            name
            owner {
              login
            }
            pullRequests(states: OPEN) {
              totalCount
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
    """

    repos_with_prs = []
    has_next_page = True
    end_cursor = None

    while has_next_page:
        # Build query with pagination using proper string formatting
        if end_cursor:
            # Use parameterized query for pagination
            query_with_pagination = query.replace(
                "repositories(first: 100, ownerAffiliations: [OWNER])",
                f'repositories(first: 100, ownerAffiliations: [OWNER], after: "{end_cursor}")',
            )
        else:
            query_with_pagination = query

        # Execute GraphQL query using gh CLI
        cmd = ["gh", "api", "graphql", "-f", f"query={query_with_pagination}", "-F", f"login={current_user}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                error_message = f"Error parsing JSON response from gh CLI: {e}\nRaw output from gh:\n{result.stdout}"
                print(error_message)
                raise RuntimeError(error_message) from e

            repositories = data.get("data", {}).get("user", {}).get("repositories", {})
            nodes = repositories.get("nodes", [])
            page_info = repositories.get("pageInfo", {})

            # Filter repositories with open PRs
            for repo in nodes:
                pr_count = repo.get("pullRequests", {}).get("totalCount", 0)
                if pr_count > 0:
                    repos_with_prs.append(
                        {"name": repo.get("name"), "owner": repo.get("owner", {}).get("login"), "openPRCount": pr_count}
                    )

            has_next_page = page_info.get("hasNextPage", False)
            end_cursor = page_info.get("endCursor")

        except subprocess.CalledProcessError as e:
            error_message = f"Error fetching repositories: {e}"
            print(error_message)
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise RuntimeError(error_message) from e

    return repos_with_prs


def get_pr_details_batch(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get PR details for multiple repositories in a single GraphQL query (Phase 2)

    Args:
        repos: List of repository dicts with 'name' and 'owner' keys

    Returns:
        List of PR data matching the format expected by determine_phase()
    """
    if not repos:
        return []

    # Build GraphQL query with aliases for multiple repositories
    # Limit to 10 repos per query to avoid overly complex queries
    batch_size = 10
    all_prs = []

    for i in range(0, len(repos), batch_size):
        batch = repos[i : i + batch_size]

        # Build query fragments for each repository
        repo_queries = []
        for idx, repo in enumerate(batch):
            alias = f"repo{idx}"
            repo_name = repo["name"]
            owner = repo["owner"]

            # Escape values to prevent GraphQL injection
            owner_literal = json.dumps(owner)
            repo_name_literal = json.dumps(repo_name)

            # Note: We intentionally fetch a single page of open PRs and rely on GitHub's
            # maximum page size (first: 100). Repositories with >100 open PRs will be
            # truncated; add pagination here if full coverage is required.
            repo_query = f"""
            {alias}: repository(owner: {owner_literal}, name: {repo_name_literal}) {{
              name
              owner {{
                login
              }}
              pullRequests(first: 100, states: OPEN, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{
                nodes {{
                  title
                  url
                  isDraft
                  author {{
                    login
                  }}
                  reviews(last: 50) {{
                    nodes {{
                      author {{
                        login
                      }}
                      state
                      body
                    }}
                  }}
                  latestReviews(first: 50) {{
                    nodes {{
                      author {{
                        login
                      }}
                      state
                    }}
                  }}
                  reviewRequests(first: 10) {{
                    nodes {{
                      requestedReviewer {{
                        ... on User {{
                          login
                        }}
                        ... on Team {{
                          name
                        }}
                      }}
                    }}
                  }}
                  comments(last: 10) {{
                    totalCount
                    nodes {{
                      reactionGroups {{
                        content
                        users {{
                          totalCount
                        }}
                      }}
                    }}
                  }}
                  commits(last: 1) {{
                    totalCount
                  }}
                  autoMergeRequest {{
                    enabledAt
                  }}
                  mergeable
                  reviewDecision
                  state
                }}
              }}
            }}
            """
            repo_queries.append(repo_query)

        # Combine all repository queries
        full_query = f"""
        query {{
          {" ".join(repo_queries)}
          rateLimit {{
            cost
            remaining
            resetAt
          }}
        }}
        """

        # Execute GraphQL query
        cmd = ["gh", "api", "graphql", "-f", f"query={full_query}"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Failed to parse JSON from 'gh api graphql' output. Raw output was:\n{result.stdout}"
                ) from e

            # Extract PR data from response
            for idx, repo in enumerate(batch):
                alias = f"repo{idx}"
                repo_data = data.get("data", {}).get(alias, {})

                if repo_data:
                    prs = repo_data.get("pullRequests", {}).get("nodes", [])
                    repo_name = repo_data.get("name", repo["name"])
                    owner = repo_data.get("owner", {}).get("login", repo["owner"])

                    # Transform GraphQL data to match expected format
                    for pr in prs:
                        # Transform reviews - handle null authors
                        reviews = []
                        for review in pr.get("reviews", {}).get("nodes", []):
                            author_data = review.get("author")
                            if author_data is None:
                                # Deleted account - use placeholder
                                author = {"login": "[deleted]"}
                            else:
                                author = {"login": author_data.get("login", "")}
                            reviews.append(
                                {"author": author, "state": review.get("state", ""), "body": review.get("body", "")}
                            )

                        # Transform latestReviews - handle null authors
                        latest_reviews = []
                        for review in pr.get("latestReviews", {}).get("nodes", []):
                            author_data = review.get("author")
                            if author_data is None:
                                # Deleted account - use placeholder
                                author = {"login": "[deleted]"}
                            else:
                                author = {"login": author_data.get("login", "")}
                            latest_reviews.append({"author": author, "state": review.get("state", "")})

                        # Transform reviewRequests
                        review_requests = []
                        for req in pr.get("reviewRequests", {}).get("nodes", []):
                            reviewer = req.get("requestedReviewer", {})
                            login = reviewer.get("login") or reviewer.get("name", "")
                            if login:
                                review_requests.append({"login": login})

                        # Handle null PR author
                        author_data = pr.get("author")
                        if author_data is None:
                            # Deleted account - use placeholder
                            author = {"login": "[deleted]"}
                        else:
                            author = {"login": author_data.get("login", "")}

                        # Extract comment nodes with reactionGroups
                        comments_data = pr.get("comments", {})
                        comment_nodes = comments_data.get("nodes", [])

                        # Add repository info to PR
                        pr_with_repo = {
                            "title": pr.get("title", ""),
                            "url": pr.get("url", ""),
                            "isDraft": pr.get("isDraft", False),
                            "author": author,
                            "reviews": reviews,
                            "latestReviews": latest_reviews,
                            "reviewRequests": review_requests,
                            "comments": comments_data.get("totalCount", 0),
                            "commentNodes": comment_nodes,
                            "commits": pr.get("commits", {}).get("totalCount", 0),
                            "autoMergeRequest": pr.get("autoMergeRequest"),
                            "mergeable": pr.get("mergeable", ""),
                            "reviewDecision": pr.get("reviewDecision"),
                            "state": pr.get("state", ""),
                            "repository": {"name": repo_name, "owner": owner},
                        }
                        all_prs.append(pr_with_repo)

            # Print rate limit info
            rate_limit = data.get("data", {}).get("rateLimit", {})
            if rate_limit:
                print(f"  GraphQL API - Cost: {rate_limit.get('cost')}, Remaining: {rate_limit.get('remaining')}")

        except subprocess.CalledProcessError as e:
            error_message = f"Error fetching PR details: {e}"
            print(error_message)
            if e.stderr:
                print(f"stderr: {e.stderr}")
            # Re-raise to avoid silently skipping batches and to inform the caller of incomplete data
            raise RuntimeError(error_message) from e

    return all_prs


def get_pr_data(repo_dir: Path) -> List[Dict[str, Any]]:
    """Get PR data from GitHub CLI (Legacy function - kept for compatibility)

    This function is no longer used in the main flow but kept for potential
    backwards compatibility or testing purposes.

    Args:
        repo_dir: Repository directory path

    Returns:
        List of PR data dictionaries
    """
    cmd = [
        "gh",
        "pr",
        "list",
        "--json",
        "author,autoMergeRequest,comments,commits,isDraft,latestReviews,mergeable,reviewDecision,reviewRequests,reviews,state,statusCheckRollup,title,url",
    ]

    result = subprocess.run(
        cmd, cwd=repo_dir, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True
    )

    return json.loads(result.stdout)


def get_existing_comments(pr_url: str, repo_dir: Path = None) -> List[Dict[str, Any]]:
    """Get existing comments on a PR

    Args:
        pr_url: URL of the PR
        repo_dir: Repository directory (optional, not used when working with URLs)

    Returns:
        List of comment dictionaries
    """
    cmd = ["gh", "pr", "view", pr_url, "--json", "comments"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        data = json.loads(result.stdout)
        return data.get("comments", [])
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []

{% endraw %}
```

## 最近の変更（過去7日間）
### コミット履歴:
021765b Merge pull request #31 from cat2151/copilot/update-llm-working-detection
18eb34c Fix type annotation to reflect backward compatibility support
ac8b1a7 Fix backward compatibility and terminology issues from PR review
1bac686 Address code review feedback - clarify docstrings and comments
c188ef6 Fix linting issues in phase_detector.py
7b9f5d2 Add reactionGroups detection for LLM working phase
0a5972e Initial plan
807dab4 Merge pull request #30 from cat2151/copilot/open-browser-in-phase3
a292aef Fix: Browser now opens only for phase3, not phase1 or phase2
eb0e70a Initial plan

### 変更されたファイル:
.github/workflows/auto-copilot-implement.yml
.github/workflows/auto_ready_for_review.yml
.github/workflows/notify-copilot-done.yml
STRUCTURE.md
config.toml.example
gh-pr-phase-monitor.py
gh_pr_phase_monitor.py
src/__init__.py
src/gh_pr_phase_monitor/__init__.py
src/gh_pr_phase_monitor/colors.py
src/gh_pr_phase_monitor/comment_manager.py
src/gh_pr_phase_monitor/config.py
src/gh_pr_phase_monitor/github_client.py
src/gh_pr_phase_monitor/main.py
src/gh_pr_phase_monitor/phase_detector.py
src/gh_pr_phase_monitor/pr_actions.py
tests/test_interval_parsing.py
tests/test_phase_detection.py
tests/test_post_comment.py
tests/test_pr_actions.py


---
Generated at: 2026-01-04 07:01:23 JST
