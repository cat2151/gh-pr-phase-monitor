# gh-pr-phase-monitor

**GitHub Copilotによる自動実装フェーズのPR監視ツール**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

※このドキュメントは大部分がAI生成です。issueをagentに投げて生成させました。

## Quick Links
| 項目 | リンク |
|------|--------|
| 📊 GitHub Repository | [cat2151/gh-pr-phase-monitor](https://github.com/cat2151/gh-pr-phase-monitor) |

## 概要

GitHub Copilotが自動実装を行うPRのフェーズを監視し、適切なタイミングで通知やアクションを実行するGitHub Actionsワークフローのコレクションです。

## 特徴

- Copilotによる実装完了を自動検知して通知
- Copilotのレビュー完了時に自動で変更を適用
- Draft PRを自動的にReady状態に変更
- GitHub Actionsによる完全自動化

## ワークフローの詳細

このプロジェクトには、GitHub Copilotとの連携を強化するための3つのワークフローが含まれています：

### 1. notify-copilot-done.yml - Copilot実装完了通知

**目的**: CopilotがPRへの変更を完了したときに、PR作成者に自動通知します。

**トリガー**:
- PRへの新しいコミット（Push）を検知（`synchronize`イベント）

**実行条件**:
1. PRがDraft状態ではない（Ready状態である）
2. PushしたユーザーがBotである
3. そのBot名に'copilot'が含まれる

**動作**:
- PR作成者に対して「🎁レビューお願いします🎁 : Copilot has finished applying the changes. Please review the updates.」というコメントを投稿します

**権限**:
- `pull-requests: write` - PRにコメントを投稿するため
- `contents: read` - PRの内容を読み取るため

### 2. auto-copilot-implement.yml - Copilotへの自動実装依頼

**目的**: Copilot（Bot）がレビューを完了したときに、自動的に変更の適用を依頼します。

**トリガー**:
- PRレビューが送信されたとき（`pull_request_review`イベントの`submitted`タイプ）

**実行条件**:
1. レビューしたユーザーがBotである
2. そのBot名に'copilot'が含まれる

**動作**:
- Copilotに対して「@copilot apply changes based on the comments in [this thread](レビューURL)」というコメントを投稿し、レビューコメントに基づいた変更の適用を依頼します
- レビューURLは`github.event.review.html_url`から自動的に取得されます

**権限**:
- `pull-requests: write` - PRにコメントを投稿するため
- `contents: read` - PRの内容を読み取るため

### 3. auto_ready_for_review.yml - Draft PRの自動Ready化

**目的**: BotによるDraft PRがレビューリクエストされたときに、自動的にReady状態に変更します。

**トリガー**:
- レビューがリクエストされたとき（`review_requested`イベント）

**実行条件**:
1. PRがDraft状態である
2. PRの作成者がBotである

**動作**:
- `gh pr ready`コマンドを実行してPRをReady状態に変更します

**権限**:
- `pull-requests: write` - PRの状態を変更するため
- `contents: read` - PRの内容を読み取るため

## 使い方

### セットアップ

1. このリポジトリをテンプレートとして使用するか、ワークフローファイルを既存のリポジトリの`.github/workflows/`ディレクトリにコピーします。

2. 必要な権限が設定されていることを確認します（各ワークフローファイルに記載されている`permissions`を参照）。

3. GitHub Copilotを有効にし、PRでCopilotを使用します。

### ワークフロー

1. **Issue作成**: 実装したい機能や修正したいバグをIssueとして作成
2. **Copilotに依頼**: Issueに対してCopilotに実装を依頼
3. **自動監視開始**: Copilotが作業を開始すると、各ワークフローが自動的に監視を開始
4. **実装完了通知**: Copilotが変更をPushすると、`notify-copilot-done.yml`が作成者に通知
5. **レビュー**: 人間がレビューを実施
6. **自動適用**: Copilotのレビューコメントがある場合、`auto-copilot-implement.yml`が自動的に変更適用を依頼
7. **Ready化**: 必要に応じて`auto_ready_for_review.yml`がDraft PRをReady状態に変更

## 注意事項

- これらのワークフローはGitHub Copilotとの連携を前提としています
- ワークフローが正しく動作するには、適切な権限（`GITHUB_TOKEN`）が必要です
- 各ワークフローの条件（`if`節）は、不要なトリガーを避けるために慎重に設定されています

## ライセンス

MIT License - 詳細はLICENSEファイルを参照してください

※英語版README.mdは、README.ja.mdを元にGeminiの翻訳でGitHub Actionsにより自動生成しています

*GitHub Copilot watches your PR phases. Now you can focus on coding. 🤖*
