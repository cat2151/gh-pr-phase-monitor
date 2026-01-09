# Phase3 Merge Feature Implementation Summary

## Overview
Implemented automatic PR merging functionality for phase3 (ready for review) PRs as requested in the issue. The feature allows PRs to be automatically merged when they reach phase3, with a configurable comment posted before merging.

## What Was Implemented

### 1. Configuration (TOML)
Added new configuration options in `config.toml.example`:

```toml
# Global execution flag
enable_execution_phase3_to_merge = false   # Set to true to enable phase3 PR merging

# Merge configuration section
[phase3_merge]
enabled = false  # Must be true along with enable_execution_phase3_to_merge
comment = "All checks passed. Merging PR."  # Comment to post before merging
automated = false  # Use browser automation to click merge button (requires Selenium/Playwright)
automation_backend = "selenium"  # Backend: "selenium" or "playwright"
wait_seconds = 10  # Wait time before clicking buttons (automated mode)
browser = "edge"  # Browser to use
headless = false  # Run browser in headless mode
```

The configuration also works with rulesets for per-repository control:
```toml
[[rulesets]]
name = "Enable merge for test repo"
repositories = ["test-repo"]
enable_execution_phase3_to_merge = true
```

### 2. Merge Methods
Two merge methods are available:

#### A. CLI-based merge (default, `automated = false`)
- Uses `gh pr merge --squash --delete-branch` command
- Automatically deletes the feature branch after merge
- Faster and more reliable
- Recommended for most use cases

#### B. Browser automation (`automated = true`)
- Opens PR in browser and clicks "Merge pull request", "Confirm merge", and "Delete branch" buttons
- Automatically deletes the feature branch after merge
- Uses Selenium or Playwright (same system as "Assign to Copilot")
- Useful if custom merge workflows require manual steps

### 3. Pre-merge Comment
Before merging, a configurable comment is posted to the PR:
- Comment text is defined in `phase3_merge.comment` configuration
- Default: "All checks passed. Merging PR."
- Can be customized to match your workflow

### 4. Branch Deletion
After a successful merge, the feature branch is automatically deleted:
- **CLI-based merge**: Uses the `--delete-branch` flag to delete both local and remote branches
- **Browser automation**: Clicks the "Delete branch" button that appears after merge confirmation
- Helps keep the repository clean by removing merged branches

### 5. Safety Features
- **Dry-run mode by default**: Must explicitly enable both `enable_execution_phase3_to_merge = true` and `phase3_merge.enabled = true`
- **Single merge per PR**: Tracks merged PRs to prevent duplicate merge attempts
- **Phase3 only**: Merge only happens when PR reaches phase3 (ready for review)
- **Per-repository control**: Can enable/disable merge for specific repositories using rulesets

## Files Modified

1. **config.toml.example**: Added merge configuration examples
2. **src/gh_pr_phase_monitor/config.py**: Added `enable_execution_phase3_to_merge` to config resolution
3. **src/gh_pr_phase_monitor/comment_manager.py**: Added `post_phase3_comment()` function
4. **src/gh_pr_phase_monitor/pr_actions.py**: 
   - Added `merge_pr()` function for CLI-based merge
   - Integrated merge logic into `process_pr()` function
   - Added merge tracking
5. **src/gh_pr_phase_monitor/browser_automation.py**:
   - Added `merge_pr_automated()` function
   - Added `_merge_pr_with_selenium()` and `_merge_pr_with_playwright()` implementations
6. **README.ja.md**: Updated documentation with merge feature description

## Files Added

1. **tests/test_phase3_merge.py**: Comprehensive tests for merge functionality (7 tests)
2. **tests/test_post_phase3_comment.py**: Tests for pre-merge comment posting (5 tests)

## Test Results
- **220 tests passed**
- 1 pre-existing test failure (not related to this change)
- All new merge functionality tests pass

## How to Use

### Basic Setup (CLI-based merge)
```toml
# Enable phase3 merge for all repositories
enable_execution_phase3_to_merge = true

[phase3_merge]
enabled = true
comment = "All checks passed. Merging this PR automatically."
automated = false  # Use gh CLI
```

### Advanced Setup (Browser automation)
```toml
enable_execution_phase3_to_merge = true

[phase3_merge]
enabled = true
comment = "🎉 All checks passed! Merging automatically."
automated = true  # Use browser automation
automation_backend = "selenium"
wait_seconds = 10
browser = "edge"
headless = false
```

### Per-repository Control
```toml
# Disable globally
enable_execution_phase3_to_merge = false

# Enable only for specific repository
[[rulesets]]
name = "Auto-merge for test repo"
repositories = ["your-username/test-repo"]
enable_execution_phase3_to_merge = true
```

## Dry-run Mode
By default, the feature shows what it would do without actually doing it:
```
[phase3] PR Title
  URL: https://github.com/owner/repo/pull/123
  [DRY-RUN] Would merge PR (enable_execution_phase3_to_merge=false)
```

Enable execution to perform actual merge:
```toml
enable_execution_phase3_to_merge = true
[phase3_merge]
enabled = true
```

## Future Enhancements
Potential improvements for future consideration:
- Support for different merge strategies (rebase, merge commit, etc.)
- Conditional merge based on CI status or approval count
- Custom merge commit messages
- Integration with GitHub auto-merge feature
