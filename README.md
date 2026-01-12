# cat-github-watcher

**PR monitoring tool for GitHub Copilot's automated implementation phase**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

*This document is largely AI-generated. Issues were fed to an agent for generation.*

## Status
- Currently dogfooding.
- Most major bugs have been addressed.
- Frequent breaking changes occur.
- Notes
  - Initially, implementation was attempted with GitHub Actions, but it was found to be unsuitable for the purpose of PR monitoring, so it was migrated to a Python version.
  - The Python version monitors user-owned repositories of an authenticated GitHub user and performs notifications and actions based on the PR's phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of Pull Requests where GitHub Copilot performs automated implementation, and executes appropriate notifications and actions at the right time.
It targets user-owned repositories of an authenticated GitHub user, leveraging the GraphQL API for efficient PR monitoring.

## Features

- **Automatic monitoring of all repositories**: Automatically monitors PRs in all user-owned repositories of an authenticated GitHub user.
- **Leveraging GraphQL API**: Achieves fast monitoring by efficiently retrieving data.
- **Phase Detection**: Automatically determines the PR's status (phase1: Draft, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent in progress).
- **Dry-run Mode**: By default, only monitors and does not perform actual actions (posting comments, marking PR as Ready, sending notifications). Can be safely operated by explicit enablement.
- **Automatic Comment Posting**: Automatically posts appropriate comments depending on the phase (requires enablement in configuration file).
- **Automatic Draft PR Readying**: Automatically changes Draft PRs to a Ready state for addressing review comments in phase2 (requires enablement in configuration file).
- **Mobile Notifications**: Uses ntfy.sh to send notifications to mobile devices when phase3 (awaiting review) is detected (requires enablement in configuration file).
  - Notifies when individual PRs enter phase3.
  - Notifies when all PRs enter phase3 (message configurable in toml).
- **Issue List Display**: If all PRs are in "LLM working" state, displays the top 10 issues for repositories with no open PRs.

## Architecture

This tool is a modular Python application adhering to the Single Responsibility Principle (SRP).

### Directory Structure

```
cat-github-watcher/
├── cat-github-watcher.py    # Entry point
├── src/
│   └── gh_pr_phase_monitor/
│       ├── colors.py         # ANSI color codes and coloring
│       ├── config.py         # Configuration loading and parsing
│       ├── github_client.py  # GitHub API integration
│       ├── phase_detector.py # PR phase detection logic
│       ├── comment_manager.py # Comment posting and verification
│       ├── pr_actions.py     # PR actions (Readying, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1.  **phase1 (Draft state)**: PR is in Draft state and has review requests.
2.  **phase2 (Addressing review comments)**: `copilot-pull-request-reviewer` has posted review comments and fixes are needed.
3.  **phase3 (Awaiting review)**: `copilot-swe-agent` has completed fixes and is awaiting human review.
4.  **LLM working (Coding agent in progress)**: None of the above apply (e.g., Copilot is implementing).

## Usage

### Prerequisites

- Python 3.x is installed.
- GitHub CLI (`gh`) is installed and authenticated.
  ```bash
  gh auth login
  ```

### Setup

1.  Clone this repository:
    ```bash
    git clone https://github.com/cat2151/cat-github-watcher.git
    cd cat-github-watcher
    ```

2.  Create a configuration file (optional):
    ```bash
    cp config.toml.example config.toml
    ```

3.  Edit `config.toml` to configure monitoring interval, execution mode, ntfy.sh notifications, Copilot auto-assignment, and auto-merge (optional):
    ```toml
    # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
    interval = "1m"
    
    # Execution control flags - can only be specified within [[rulesets]] sections
    # Global flags are no longer supported
    # To apply settings to all repositories, use 'repositories = ["all"]'
    
    # Example ruleset configuration:
    # [[rulesets]]
    # name = "Default for all repositories - dry-run mode"
    # repositories = ["all"]  # "all" matches all repositories
    # enable_execution_phase1_to_phase2 = false  # Set to true to ready draft PRs
    # enable_execution_phase2_to_phase3 = false  # Set to true to post phase2 comments
    # enable_execution_phase3_send_ntfy = false  # Set to true to send ntfy notifications
    # enable_execution_phase3_to_merge = false   # Set to true to merge phase3 PRs
    
    # [[rulesets]]
    # name = "Simple: auto-assign good first issue to Copilot"
    # repositories = ["my-repo"]
    # assign_good_first_old = true  # This alone is enough! No [assign_to_copilot] section needed
    #                               # Default behavior: Opens issue in browser for manual assignment
    
    # ntfy.sh notification settings (optional)
    # Notifications include a clickable action button to open the PR
    [ntfy]
    enabled = false  # Set to true to enable notifications
    topic = "<Enter your ntfy.sh topic name here>"  # Make it an unguessable string as anyone can read/write to it
    message = "PR is ready for review: {url}"  # Message template
    priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
    all_phase3_message = "All PRs are now in phase3 (ready for review)"  # Message when all PRs are in phase3
    
    # Phase3 auto-merge settings (optional)
    # Automatically merges the PR when it reaches phase3 (awaiting review)
    # Before merging, the comment defined below will be posted to the PR
    # After successful merge, the feature branch will be automatically deleted
    # IMPORTANT: For safety, this feature is disabled by default
    # You must explicitly enable it by specifying enable_execution_phase3_to_merge = true in rulesets for each repository
    [phase3_merge]
    comment = "All checks passed. Merging PR."  # Comment to post before merging
    automated = false  # Set to true for browser automation to click merge button
    automation_backend = "selenium"  # Automation backend: "selenium" or "playwright"
    wait_seconds = 10  # Wait time (seconds) after browser launch, before clicking button
    browser = "edge"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
    headless = false  # Run in headless mode (do not display window)
    
    # Auto-assign issue to Copilot (completely optional! This entire section is optional)
    # 
    # Simple usage: just set assign_good_first_old = true in rulesets (see example above)
    # Define this section ONLY if you want to customize the default behavior.
    # 
    # Assignment behavior is controlled by ruleset flags:
    # - assign_good_first_old: Assigns the oldest "good first issue" (by issue number, default: false)
    # - assign_old: Assigns the oldest issue (by issue number, any label, default: false)
    # If both are true, "good first issue" takes precedence.
    # 
    # Default behavior (if this section is not defined):
    # - Automatically clicks button with browser automation
    # - Uses Playwright + Chromium
    # - wait_seconds = 10
    # - headless = false
    # 
    # REQUIRED: Selenium or Playwright installation is necessary
    # 
    # IMPORTANT: For safety, this feature is disabled by default
    # You must explicitly enable it by specifying assign_good_first_old or assign_old in rulesets for each repository
    [assign_to_copilot]
    automation_backend = "playwright"  # Automation backend: "selenium" or "playwright"
    wait_seconds = 10  # Wait time (seconds) after browser launch, before clicking button
    browser = "chromium"  # Browser to use: Selenium: "edge", "chrome", "firefox" / Playwright: "chromium", "firefox", "webkit"
    headless = false  # Run in headless mode (do not display window)
    ```

4.  **Prepare Button Screenshots (Only if using automation)**:

    If you plan to use automation features (`automated = true` or enabling `assign_to_copilot` / `phase3_merge`),
    PyAutoGUI requires screenshots of the buttons it needs to click.

    **Required Screenshots:**

    For issue auto-assignment (`assign_to_copilot` feature):
    - `assign_to_copilot.png` - Screenshot of the "Assign to Copilot" button
    - `assign.png` - Screenshot of the "Assign" button

    For PR auto-merge (`phase3_merge` feature when `automated = true`):
    - `merge_pull_request.png` - Screenshot of the "Merge pull request" button
    - `confirm_merge.png` - Screenshot of the "Confirm merge" button
    - `delete_branch.png` - Screenshot of the "Delete branch" button (optional)

    **How to take screenshots:**

    a. Open a GitHub issue or PR in your browser.
    b. Locate the button you want to automate.
    c. Take a screenshot of **only the button** (not the whole screen).
    d. Save it as a PNG file in the `screenshots` directory.
    e. Use the exact filenames listed above.

    **Tips:**
    - Screenshots should include only the button, with a small margin.
    - Use your OS's screenshot tool (Windows: Snipping Tool, Mac: Cmd+Shift+4).
    - Ensure the button is clearly visible and not obscured.
    - If the button's appearance changes (e.g., theme change), you'll need to update the screenshots.
    - Use the `confidence` setting to adjust image recognition reliability (due to DPI scaling or themes).

    **Important Requirements:**
    - You must already be **logged into GitHub** in your default browser.
    - Automation uses existing browser sessions (it does not perform new authentication).
    - Ensure the correct GitHub window/tab is in focus and visible on screen when buttons are clicked.
    - If multiple GitHub pages are open, the first found button will be clicked.

    **Create screenshots directory:**
    ```bash
    mkdir screenshots
    ```

5.  Install PyAutoGUI (Only if using automation):

    ```bash
    pip install -r requirements-automation.txt
    ```
    or
    ```bash
    pip install pyautogui pillow
    ```

### Running

Start the tool to begin monitoring:

```bash
python3 cat-github-watcher.py [config.toml]
```

Or, run directly as a Python module:

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### Operation Flow

1.  **Start**: Upon launch, the tool begins monitoring user-owned repositories of the authenticated GitHub user.
2.  **PR Detection**: Automatically detects repositories with open PRs.
3.  **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4.  **Action Execution**:
    -   **phase1**: Default is Dry-run (if `enable_execution_phase1_to_phase2 = true` in rulesets, Draft PRs are marked as Ready).
    -   **phase2**: Default is Dry-run (if `enable_execution_phase2_to_phase3 = true` in rulesets, a comment is posted requesting Copilot to apply changes).
    -   **phase3**: Opens the PR page in the browser.
        -   If `enable_execution_phase3_send_ntfy = true` in rulesets, ntfy.sh notifications are also sent.
        -   If `enable_execution_phase3_to_merge = true` in rulesets, the PR is automatically merged (using global `[phase3_merge]` settings).
    -   **LLM working**: Waits (if all PRs are in this state, displays issues for repositories with no open PRs).
5.  **Issue Auto-Assignment**: If all PRs are in "LLM working" state and there are repositories with no open PRs:
    -   If `assign_good_first_old = true` in rulesets, the oldest "good first issue" is automatically assigned (by issue number order).
    -   If `assign_old = true` in rulesets, the oldest issue is automatically assigned (by issue number order, regardless of label).
    -   If both are true, "good first issue" takes precedence.
    -   Default behavior: Automatically clicks buttons with PyAutoGUI (no `[assign_to_copilot]` section required).
    -   REQUIRED: PyAutoGUI must be installed, and button screenshots must be prepared.
6.  **Repeat**: Monitoring continues at the configured interval.

### Dry-run Mode

By default, the tool operates in **Dry-run Mode** and does not perform actual actions. This allows you to safely verify its operation.

-   **Phase1 (Draft → Ready)**: Displays `[DRY-RUN] Would mark PR as ready for review` but does nothing actually.
-   **Phase2 (Comment Posting)**: Displays `[DRY-RUN] Would post comment for phase2` but does nothing actually.
-   **Phase3 (ntfy Notification)**: Displays `[DRY-RUN] Would send ntfy notification` but does nothing actually.
-   **Phase3 (Merge)**: Displays `[DRY-RUN] Would merge PR` but does nothing actually.

To enable actual actions, set the following flags to `true` in the `[[rulesets]]` section of `config.toml`:
```toml
[[rulesets]]
name = "Enable automation for a specific repository"
repositories = ["test-repo"]  # Or ["all"] for all repositories
enable_execution_phase1_to_phase2 = true  # Ready Draft PRs
enable_execution_phase2_to_phase3 = true  # Post Phase2 comments
enable_execution_phase3_send_ntfy = true  # Send ntfy notifications
enable_execution_phase3_to_merge = true   # Merge Phase3 PRs
assign_good_first_old = true              # Auto-assign good first issues
```

### Stopping

You can stop monitoring by pressing `Ctrl+C`.

## Notes

-   GitHub CLI (`gh`) must be installed and authenticated.
-   Assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
-   Only **user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
-   Be mindful of API rate limits as it uses the GraphQL API.
-   If using ntfy.sh notifications, please set up a topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details.

*The English README.md is automatically generated via GitHub Actions using Gemini's translation of README.ja.md.*

*Big Brother is watching your repositories. Now it’s the cat. 🐱*