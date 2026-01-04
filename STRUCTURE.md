# Source Code Structure

This document describes the refactored source code structure following the Single Responsibility Principle (SRP).

## Directory Structure

```
cat-github-watcher/
├── cat-github-watcher.py    # Entry point script
├── src/
│   └── gh_pr_phase_monitor/
│       ├── __init__.py       # Package initialization
│       ├── colors.py         # ANSI color codes and colorization
│       ├── config.py         # Configuration loading and parsing
│       ├── github_client.py  # GitHub API interactions
│       ├── phase_detector.py # PR phase determination logic
│       ├── comment_manager.py # Comment posting and checking
│       ├── pr_actions.py     # PR actions (mark ready, browser)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
    ├── test_interval_parsing.py
    ├── test_phase_detection.py
    └── test_post_comment.py
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

#### github_client.py
- `get_current_user()`: Get authenticated GitHub user's login
- `get_repositories_with_open_prs()`: Get all repositories with open PRs
- `get_pr_details_batch()`: Get detailed PR information for multiple repos
- `get_pr_data()`: Legacy function for backward compatibility
- `get_existing_comments()`: Get existing comments on a PR

#### phase_detector.py
- `has_inline_review_comments()`: Check if review body indicates inline comments
- `determine_phase()`: Determine which phase (phase1/2/3 or LLM working) a PR is in

#### comment_manager.py
- `has_copilot_apply_comment()`: Check if @copilot apply comment exists
- `has_phase3_review_comment()`: Check if phase3 review comment exists
- `post_phase2_comment()`: Post comment when phase2 is detected
- `post_phase3_comment()`: Post comment when phase3 is detected

#### pr_actions.py
- `mark_pr_ready()`: Mark a draft PR as ready for review
- `open_browser()`: Open URL in browser
- `process_pr()`: Process a single PR (main processing logic)
- `process_repository()`: Legacy function for backward compatibility

#### main.py
- `main()`: Main execution function with monitoring loop

## Benefits of This Structure

1. **Single Responsibility**: Each module has a clear, focused purpose
2. **Better Testability**: Modules can be tested independently
3. **Easier Maintenance**: Changes to one area don't affect others
4. **Improved Readability**: Smaller files are easier to understand
5. **Better Code Organization**: Related functionality is grouped together
6. **Reduced Hallucination Risk**: AI tools have clearer context about what each module does

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

All 58 tests pass successfully after the refactoring.
