# cat-github-watcher

**PR Monitoring Tool for GitHub Copilot's Automated Implementation Phase**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

*This document is largely AI-generated. Issues were submitted to an agent for generation.*

## Current Status
- Currently dogfooding.
- Major bugs have been addressed.
- Frequent breaking changes are expected.
- Memo
  - Initially, we attempted implementation with GitHub Actions, but it proved unsuitable for PR monitoring, so we transitioned to a Python version.
  - The Python version monitors user-owned repositories for authenticated GitHub users and performs notifications and actions based on PR phases.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of Pull Requests (PRs where GitHub Copilot performs automated implementation) and executes appropriate notifications and actions at the right time.
It targets user-owned repositories of an authenticated GitHub user, utilizing the GraphQL API for efficient PR monitoring.

## Features

- **Automatic Monitoring of All Repositories**: Automatically monitors PRs in user-owned repositories for authenticated GitHub users.
- **GraphQL API Utilization**: Achieves fast monitoring through efficient data retrieval.
- **Phase Detection**: Automatically determines PR states (phase1: Draft, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent working).
- **Automated Comment Posting**: Automatically posts appropriate comments based on the PR phase.
- **Automated Draft PR Readying**: Automatically changes Draft PRs to "Ready for review" status for addressing review comments in phase2.
- **Mobile Notifications**: Uses ntfy.sh to notify mobile devices when phase3 (awaiting review) is detected.
- **Issue List Display**: If all PRs are "LLM working", displays the top 10 issues for repositories with no open PRs.

## Architecture

This tool is a Python application modularized according to the Single Responsibility Principle (SRP).

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
│       ├── pr_actions.py     # PR actions (readying, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool detects the following four phases:

1.  **phase1 (Draft state)**: When the PR is in Draft state and has review requests.
2.  **phase2 (Addressing review comments)**: When `copilot-pull-request-reviewer` has posted review comments and corrections are needed.
3.  **phase3 (Awaiting review)**: When `copilot-swe-agent` has completed corrections and is awaiting human review.
4.  **LLM working (Coding agent working)**: If none of the above apply (e.g., Copilot is implementing).

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

3.  Edit `config.toml` to set the monitoring interval and ntfy.sh notifications (optional):
    ```toml
    # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
    interval = "1m"
    
    # ntfy.sh notification settings (optional)
    # Notifications include a clickable action button to open the PR.
    [ntfy]
    enabled = false  # Set to true to enable notifications
    topic = "<Enter your ntfy.sh topic name here>"  # Anyone can read/write, so use an unguessable string
    message = "PR is ready for review: {url}"  # Message template
    priority = 4  # Notification priority (1=min, 3=default, 4=high, 5=max)
    ```

### Execution

Start the tool to begin monitoring:

```bash
python3 cat-github-watcher.py [config.toml]
```

Or, run directly as a Python module:

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### Workflow

1.  **Start**: When the tool starts, it begins monitoring user-owned repositories for the authenticated GitHub user.
2.  **PR Detection**: Automatically detects repositories with open PRs.
3.  **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4.  **Action Execution**:
    - **phase1**: Does nothing (waits in Draft state).
    - **phase2**: Changes the Draft PR to "Ready for review" and posts a comment requesting Copilot to apply changes.
    - **phase3**: Notifies that it's "Awaiting review" (mobile notification if ntfy.sh is configured, opens PR page in browser).
    - **LLM working**: Waits (if all PRs are in this state, displays issues for repositories with no open PRs).
5.  **Repeat**: Continues monitoring at the configured interval.

### Stopping

You can stop monitoring by pressing `Ctrl+C`.

## Important Notes

- GitHub CLI (`gh`) must be installed and authenticated.
- This tool is designed to integrate with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
- Only **user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
- Be mindful of the API rate limits when using the GraphQL API.
- If using ntfy.sh notifications, configure a topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details.

*The English README.md is automatically generated from README.ja.md using Gemini's translation via GitHub Actions.*

*GitHub Copilot watches your PR phases. Now you can focus on coding. 🤖*