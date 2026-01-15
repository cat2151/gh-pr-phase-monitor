# Phase3 Merge Configuration Examples

This document provides practical configuration examples for the phase3 merge feature.

## Example 1: Basic CLI-based Merge (Recommended)

This is the simplest and most reliable configuration using the GitHub CLI.

```toml
# config.toml

# Enable phase3 merge globally
enable_execution_phase3_to_merge = true

# Merge configuration
[phase3_merge]
comment = "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。"
automated = false  # Use gh CLI (faster and more reliable)
```

**Result**: When a PR reaches phase3, the tool will:
1. Post comment: "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。"
2. Run: `gh pr merge --auto --squash [PR_URL]`

## Example 2: Browser Automation Merge

Use this if you need to interact with custom merge workflows or buttons.

```toml
# config.toml

enable_execution_phase3_to_merge = true

[phase3_merge]
comment = "🎉 レビュー指摘対応完了。自動マージします。"
automated = true  # Use browser automation
wait_seconds = 10
```

**Result**: When a PR reaches phase3, the tool will:
1. Post comment: "🎉 レビュー指摘対応完了。自動マージします。"
2. Open browser
3. Click "Merge pull request" button
4. Click "Confirm merge" button

## Example 3: Per-Repository Control

Enable merge only for specific test repositories.

```toml
# config.toml

# Disable globally by default
enable_execution_phase3_to_merge = false

[phase3_merge]
comment = "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。"

# Enable only for test repository
[[rulesets]]
name = "Enable merge for test repo"
repositories = ["your-username/test-repo"]
enable_execution_phase3_to_merge = true

# Keep disabled for production repo
[[rulesets]]
name = "Disable merge for production"
repositories = ["your-username/production-repo"]
enable_execution_phase3_to_merge = false
```

## Example 4: Different Settings for Different Repos

```toml
# config.toml

# Default: disabled
enable_execution_phase3_to_merge = false

[phase3_merge]

# Test repos: enable with automated merge
[[rulesets]]
name = "Test repositories"
repositories = ["test-repo-1", "test-repo-2"]
enable_execution_phase3_to_merge = true

# Staging repos: enable with CLI merge
[[rulesets]]
name = "Staging repositories"
repositories = ["staging-repo"]
enable_execution_phase3_to_merge = true

# Production repos: keep disabled (manual merge required)
[[rulesets]]
name = "Production repositories"
repositories = ["production-repo"]
enable_execution_phase3_to_merge = false
```

## Example 5: Headless Browser Automation

For running on servers without display.

```toml
# config.toml

enable_execution_phase3_to_merge = true

[phase3_merge]
comment = "CI passed. Merging automatically."
automated = true
wait_seconds = 15
```

## Example 6: Dry-run Testing

Test the feature without actually merging.

```toml
# config.toml

# Keep execution flag false for testing
enable_execution_phase3_to_merge = false

[phase3_merge]
comment = "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。"
automated = false
```

**Result**: Shows dry-run messages:
```
[phase3] PR Title
  URL: https://github.com/owner/repo/pull/123
  [DRY-RUN] Would merge PR (enable_execution_phase3_to_merge=false)
```

## Example 7: Custom Comment for Different Projects

```toml
# config.toml for Documentation Projects
enable_execution_phase3_to_merge = true

[phase3_merge]
comment = "📚 Documentation updated. Auto-merging to keep docs fresh!"
automated = false
```

```toml
# config.toml for Automated Testing Projects
enable_execution_phase3_to_merge = true

[phase3_merge]
comment = "✅ All 250 tests passed. Confidence level: High. Auto-merging."
automated = false
```

## Usage Tips

### 1. Start with Dry-run
Always test with `enable_execution_phase3_to_merge = false` first to see what would happen.

### 2. Use CLI Merge by Default
The CLI method (`automated = false`) is faster and more reliable than browser automation.

### 3. Browser Automation Use Cases
Only use browser automation (`automated = true`) if:
- You have custom merge workflows
- You need to click specific merge options
- You need to interact with custom merge buttons

### 4. Customize Comments
Make comments informative:
- ✅ Good: "All 50 tests passed. Coverage: 95%. Auto-merging."
- ❌ Bad: "merge"

### 5. Per-Repository Granularity
Use rulesets to:
- Enable for test repos
- Disable for production repos
- Different settings for different projects

## Troubleshooting

### Merge Not Happening
Check:
1. `enable_execution_phase3_to_merge = true` is set (either globally or in a ruleset for your repository)
2. PR is in phase3 (not phase1, phase2, or LLM working)
3. No error messages in console output

### Browser Automation Fails
Try:
1. Increase `wait_seconds` (e.g., 15 or 20)
2. Check if button screenshots are up to date
3. Ensure GitHub is logged in your default browser
4. Switch to CLI merge (`automated = false`)

### Comment Not Posted
Check:
1. `gh` CLI is authenticated: `gh auth status`
2. Comment text is not empty
3. PR URL is accessible

## Safety Notes

⚠️ **Important Safety Considerations:**

1. **Always test in dry-run mode first**
2. **Start with test repositories only**
3. **Monitor the first few automatic merges**
4. **Keep production repos on manual merge initially**
5. **Use ruleset system for gradual rollout**

Remember: You can always disable the feature by setting `enable_execution_phase3_to_merge = false` globally or per-repository.
