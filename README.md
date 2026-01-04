# cat-github-watcher

**PR Monitoring Tool for Automated Implementation Phases by GitHub Copilot**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

*This document is largely AI-generated, produced by feeding an issue to an agent.*

## Status

**The Python version development is complete and it is currently in operation.**

Initially, implementation was attempted with GitHub Actions, but it was found to be unsuitable for the purpose of PR monitoring, so we transitioned to the Python version.
The Python version monitors all user-owned repositories of an authenticated GitHub user and performs notifications and actions according to the PR's phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This is a Python tool that monitors the phases of PRs where GitHub Copilot performs automated implementation, executing notifications and actions at appropriate times.
It efficiently monitors PRs across all user-owned repositories of an authenticated GitHub user, leveraging the GraphQL API.

## Features

- **Automatic Monitoring of All Repositories**: Automatically monitors PRs across all user-owned repositories of an authenticated GitHub user
- **GraphQL API Utilization**: Achieves high-speed monitoring through efficient data retrieval
- **Phase Detection**: Automatically determines the PR's status (phase1: Draft state, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent in progress)
- **Automatic Comment Posting**: Automatically posts appropriate comments based on the phase
- **Automatic Draft PR Readying**: Automatically changes Draft PRs to a Ready state for addressing review comments in phase2
- **Mobile Notification**: Notifies mobile devices via ntfy.sh when phase3 (awaiting review) is detected
- **Issue List Display**: If all PRs are "LLM working", displays the top 10 issues from repositories without open PRs

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
│       ├── pr_actions.py     # PR actions (Readying, browser launch)
│       └── main.py           # Main execution loop
└── tests/                    # Test files
```

### Phase Detection Logic

The tool identifies the following four phases:

1.  **phase1 (Draft state)**: When the PR is in Draft state and has review requests
2.  **phase2 (Addressing review comments)**: When `copilot-pull-request-reviewer` has posted review comments and corrections are needed
3.  **phase3 (Awaiting review)**: When `copilot-swe-agent` has completed corrections and is awaiting human review
4.  **LLM working (Coding agent in progress)**: When none of the above apply (e.g., Copilot is implementing)

## Usage

### Prerequisites

- Python 3.x is installed
- GitHub CLI (`gh`) is installed and authenticated
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

3.  Edit `config.toml` to configure the monitoring interval and ntfy.sh notifications (optional):
    ```toml
    # Check interval (e.g., "30s", "1m", "5m", "1h", "1d")
    interval = "1m"
    
    # ntfy.sh notification settings (optional)
    # Notifications include clickable action buttons to open the PR
    [ntfy]
    enabled = false  # Set to true to enable notifications
    topic = "cat-github-watcher"  # ntfy.sh topic name
    message = "PR is ready for review: {url}"  # Message template
    priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
    ```

### Execution

Start the tool to begin monitoring:

```bash
python3 cat-github-watcher.py [config.toml]
```

Alternatively, run directly as a Python module:

```bash
python3 -m src.gh_pr_phase_monitor.main [config.toml]
```

### Operation Flow

1.  **Start**: Upon launching, the tool begins monitoring all user-owned repositories of the authenticated GitHub user.
2.  **PR Detection**: Automatically detects repositories with open PRs.
3.  **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4.  **Action Execution**:
    -   **phase1**: Does nothing (awaits in Draft state)
    -   **phase2**: Changes Draft PRs to a Ready state and posts a comment requesting Copilot to apply changes.
    -   **phase3**: Notifies of awaiting review (mobile notification if ntfy.sh is configured, opens PR page in browser).
    -   **LLM working**: Awaits (if all PRs are in this state, displays issues from repositories without open PRs).
5.  **Repeat**: Continues monitoring at the configured interval.

### Stopping

Monitoring can be stopped with `Ctrl+C`.

## Important Notes

- GitHub CLI (`gh`) must be installed and authenticated.
- It relies on integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
- **Only user-owned repositories** will be monitored. Organization repositories are NOT included to keep the tool simple and focused (YAGNI principle).
- Be aware of API rate limits, as it uses the GraphQL API.
- If using ntfy.sh notifications, configure a topic on [ntfy.sh](https://ntfy.sh/) in advance.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details

*The English README.md is automatically generated by GitHub Actions using Gemini's translation based on README.ja.md.*

*GitHub Copilot watches your PR phases. Now you can focus on coding. 🤖*