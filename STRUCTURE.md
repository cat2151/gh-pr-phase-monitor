# Source Code Structure

This document describes the refactored source code structure following the Single Responsibility Principle (SRP).

## Directory Structure

```
cat-github-watcher/
├── cat-github-watcher.py    # Entry point script
├── src/
│   └── gh_pr_phase_monitor/
│       ├── __init__.py          # Package initialization and exports
│       ├── browser_automation.py # Browser automation (Selenium/Playwright)
│       ├── colors.py            # ANSI color codes and colorization
│       ├── comment_fetcher.py   # Comment fetching operations
│       ├── comment_manager.py   # Comment posting and checking
│       ├── config.py            # Configuration loading and parsing
│       ├── display.py           # Status display and UI functions
│       ├── github_auth.py       # GitHub authentication
│       ├── github_client.py     # GitHub API re-exports (compatibility layer)
│       ├── graphql_client.py    # GraphQL query execution
│       ├── issue_fetcher.py     # Issue fetching and assignment
│       ├── main.py              # Main execution loop (212 lines)
│       ├── monitor.py           # Monitoring and frequency adjustment
│       ├── notifier.py          # ntfy.sh notifications
│       ├── phase_detector.py    # PR phase determination logic
│       ├── pr_actions.py        # PR actions (mark ready, merge, browser)
│       ├── pr_fetcher.py        # PR fetching operations
│       ├── repository_fetcher.py # Repository fetching operations
│       ├── state_tracker.py     # PR state tracking
│       ├── time_utils.py        # Time formatting utilities
│       └── wait_handler.py      # Countdown and hot reload handling
└── tests/                       # Test files (360 tests)
    ├── test_batteries_included_defaults.py
    ├── test_browser_automation.py
    ├── test_check_process_before_autoraise.py
    ├── test_config_rulesets.py
    ├── test_config_rulesets_features.py
    ├── test_elapsed_time_display.py
    ├── test_hot_reload.py
    ├── test_integration_issue_fetching.py
    ├── test_interval_contamination_bug.py
    ├── test_interval_parsing.py
    ├── test_issue_fetching.py
    ├── test_max_llm_working_parallel.py
    ├── test_no_change_timeout.py
    ├── test_no_open_prs_issue_display.py
    ├── test_notification.py
    ├── test_phase3_merge.py
    ├── test_phase_detection.py
    ├── test_post_comment.py
    ├── test_post_phase3_comment.py
    ├── test_pr_actions.py
    ├── test_pr_actions_rulesets_features.py
    ├── test_pr_actions_with_rulesets.py
    ├── test_repos_with_prs_structure.py
    ├── test_status_summary.py
    ├── test_validate_phase3_merge_config.py
    └── test_verbose_config.py
```

## Module Responsibilities

### Entry Point
- **cat-github-watcher.py**: Simple entry point that imports and calls the main function

### Core Modules

#### colors.py
- `Colors` class: ANSI color code constants
- `colorize_phase()`: Add color to phase string for terminal output

#### config.py
- `parse_interval()`: Parse interval strings (e.g., "1m", "30s") to seconds
- `load_config()`: Load configuration from TOML file
- `get_phase3_merge_config()`: Get phase3_merge configuration with defaults
- `get_assign_to_copilot_config()`: Get assign_to_copilot configuration
- `resolve_execution_config_for_repo()`: Resolve execution config for specific repo
- `validate_phase3_merge_config_required()`: Validate phase3_merge configuration

#### time_utils.py
- `format_elapsed_time()`: Format elapsed time in Japanese style (e.g., "3分20秒")

#### wait_handler.py
- `wait_with_countdown()`: Wait with live countdown and hot reload support

#### state_tracker.py
- `cleanup_old_pr_states()`: Clean up PR state tracking
- `get_pr_state_time()`: Get timestamp when PR entered specific phase
- `set_pr_state_time()`: Record timestamp for PR phase
- `get_last_state()`: Get last recorded overall PR state
- `set_last_state()`: Set last recorded overall PR state
- `is_reduced_frequency_mode()`: Check if in reduced frequency mode
- `set_reduced_frequency_mode()`: Set monitoring frequency mode

#### monitor.py
- `check_no_state_change_timeout()`: Check if PR state unchanged for too long and switch to reduced frequency mode

#### display.py
- `display_status_summary()`: Display concise summary of current PR status
- `display_issues_from_repos_without_prs()`: Display issues from repos with no open PRs
- `_resolve_assign_to_copilot_config()`: Resolve assign_to_copilot config for specific issue's repo

#### github_client.py (Re-export Layer)
- Re-exports functions from specialized modules for backward compatibility
- `get_current_user()`: From github_auth
- `get_repositories_with_open_prs()`: From repository_fetcher
- `get_pr_details_batch()`: From pr_fetcher
- `get_issues_from_repositories()`: From issue_fetcher
- `assign_issue_to_copilot()`: From issue_fetcher
- `get_existing_comments()`: From comment_fetcher

#### github_auth.py
- `get_current_user()`: Get authenticated GitHub user's login

#### graphql_client.py
- `execute_graphql_query()`: Execute GraphQL query via `gh` CLI

#### repository_fetcher.py
- `get_all_repositories()`: Get all repositories for authenticated user
- `get_repositories_with_open_prs()`: Get repositories with open PRs
- `get_repositories_with_no_prs_and_open_issues()`: Get repos with no PRs but with open issues

#### pr_fetcher.py
- `get_pr_details_batch()`: Get detailed PR information for multiple repos
- `get_pr_data()`: Legacy function for backward compatibility

#### issue_fetcher.py
- `get_issues_from_repositories()`: Get issues from repositories
- `assign_issue_to_copilot()`: Assign issue to Copilot using browser automation

#### comment_fetcher.py
- `get_existing_comments()`: Get existing comments on a PR

#### phase_detector.py
- `determine_phase()`: Determine which phase (phase1/2/3 or LLM working) a PR is in
- `has_comments_with_reactions()`: Check if comments have reactions
- `has_unresolved_review_threads()`: Check for unresolved review threads
- `has_inline_review_comments()`: (Deprecated) Check if review body indicates inline comments

#### comment_manager.py
- `has_copilot_apply_comment()`: Check if @copilot apply comment exists
- `post_phase2_comment()`: Post comment when phase2 is detected
- `post_phase3_comment()`: Post comment when phase3 is detected

#### pr_actions.py
- `mark_pr_ready()`: Mark a draft PR as ready for review
- `merge_pr()`: Merge a PR using gh CLI
- `open_browser()`: Open URL in browser
- `process_pr()`: Process a single PR (main processing logic)
- `process_repository()`: Legacy function for backward compatibility

#### browser_automation.py
- `merge_pr_automated()`: Merge PR using browser automation
- `_can_open_browser()`: Check if browser can be opened (cooldown)
- `_should_autoraise_window()`: Determine if window should be raised
- `_record_browser_open()`: Record browser open timestamp

#### notifier.py
- `send_phase3_notification()`: Send notification via ntfy.sh

#### main.py (Simplified - 212 lines)
- `main()`: Main execution function with monitoring loop
  - Configuration loading
  - Signal handling
  - Repository and PR monitoring
  - Issue display
  - Status summary and state tracking

## Benefits of This Structure

1. **Single Responsibility**: Each module has a clear, focused purpose
2. **Better Testability**: Modules can be tested independently (360 tests)
3. **Easier Maintenance**: Changes to one area don't affect others
4. **Improved Readability**: Smaller files are easier to understand
5. **Better Code Organization**: Related functionality is grouped together
6. **Reduced Hallucination Risk**: AI tools have clearer context about what each module does
7. **Reduced main.py**: From 699 lines to 212 lines (70% reduction)

## Module Dependencies

```
main.py
├── config.py
├── display.py
│   ├── colors.py
│   ├── config.py
│   ├── github_client.py
│   │   ├── github_auth.py
│   │   ├── repository_fetcher.py
│   │   │   └── graphql_client.py
│   │   ├── pr_fetcher.py
│   │   │   └── graphql_client.py
│   │   ├── issue_fetcher.py
│   │   │   ├── graphql_client.py
│   │   │   └── browser_automation.py
│   │   └── comment_fetcher.py
│   ├── state_tracker.py
│   └── time_utils.py
├── github_client.py
├── monitor.py
│   ├── config.py
│   ├── state_tracker.py
│   └── time_utils.py
├── phase_detector.py
├── pr_actions.py
│   ├── browser_automation.py
│   ├── colors.py
│   ├── comment_manager.py
│   ├── config.py
│   ├── notifier.py
│   └── phase_detector.py
└── wait_handler.py
    ├── config.py
    └── time_utils.py
```

## Usage

Run the tool using the entry point script:

```bash
python3 cat-github-watcher.py [config.toml]
```

Or directly with Python module syntax:

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

All 360 tests pass successfully after the refactoring.
