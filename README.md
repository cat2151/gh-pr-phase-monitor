# cat-github-watcher

**PR monitoring tool for the automated implementation phase by GitHub Copilot**

<p align="left">
  <a href="README.ja.md"><img src="https://img.shields.io/badge/🇯🇵-Japanese-red.svg" alt="Japanese"></a>
  <a href="README.md"><img src="https://img.shields.io/badge/🇺🇸-English-blue.svg" alt="English"></a>
</p>

*This document is largely AI-generated. I threw issues at the agent and had it generate the content.*

## Status
- Currently dogfooding.
- Most major bugs have been addressed.
- Frequent breaking changes are expected.
- Memo
  - Initially, we attempted to implement this with GitHub Actions, but it proved unsuitable for the purpose of PR monitoring, so we transitioned to a Python version.
  - The Python version monitors user-owned repositories for authenticated GitHub users and performs notifications and actions based on the PR's phase.

## Quick Links
| Item | Link |
|------|--------|
| 📊 GitHub Repository | [cat2151/cat-github-watcher](https://github.com/cat2151/cat-github-watcher) |

## Overview

This Python tool monitors the phases of Pull Requests where GitHub Copilot performs automated implementations, executing appropriate notifications and actions at the right time.
It targets user-owned repositories of authenticated GitHub users and efficiently monitors PRs using the GraphQL API.

## Features

- **Automated Monitoring of All Repositories**: Automatically monitors PRs in user-owned repositories for authenticated GitHub users.
- **GraphQL API Utilization**: Achieves high-speed monitoring through efficient data retrieval.
- **Phase Detection**: Automatically determines PR states (phase1: Draft status, phase2: Addressing review comments, phase3: Awaiting review, LLM working: Coding agent at work).
- **Automated Comment Posting**: Automatically posts appropriate comments based on the detected phase.
- **Automated Draft PR Readying**: Automatically changes Draft PRs to a Ready state to address review comments in phase2.
- **Mobile Notifications**: Uses ntfy.sh to notify mobile devices when phase3 (awaiting review) is detected.
- **Issue List Display**: If all PRs are in "LLM working" state, displays the top 10 issues for repositories with no open PRs.

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

The tool detects the following four phases:

1. **phase1 (Draft status)**: The PR is in Draft status and has review requests.
2. **phase2 (Addressing review comments)**: `copilot-pull-request-reviewer` has posted review comments, and corrections are needed.
3. **phase3 (Awaiting review)**: `copilot-swe-agent` has completed corrections and is awaiting human review.
4. **LLM working (Coding agent at work)**: None of the above apply (e.g., Copilot is currently implementing).

## Usage

### Prerequisites

- Python 3.x is installed.
- GitHub CLI (`gh`) is installed and authenticated.
  ```bash
  gh auth login
  ```

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/cat2151/cat-github-watcher.git
   cd cat-github-watcher
   ```

2. Create a configuration file (optional):
   ```bash
   cp config.toml.example config.toml
   ```

3. Edit `config.toml` to set the monitoring interval, ntfy.sh notifications, and Copilot auto-assignment (optional):
   ```toml
   # Check interval ("30s", "1m", "5m", "1h", "1d", etc.)
   interval = "1m"
   
   # ntfy.sh notification settings (optional)
   # Notifications include a clickable action button to open the PR
   [ntfy]
   enabled = false  # Set to true to enable notifications
   topic = "<Write your ntfy.sh topic name here>"  # Anyone can read/write, so use an unguessable string
   message = "PR is ready for review: {url}"  # Message template
   priority = 4  # Notification priority (1=lowest, 3=default, 4=high, 5=highest)
   
   # Auto-assign "good first issue" issues to Copilot (optional)
   # When enabled, opens the issue in a browser and prompts to click "Assign to Copilot" button
   [assign_to_copilot]
   enabled = false  # Set to true to enable auto-assignment feature
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

### Operation Flow

1. **Startup**: When the tool starts, it begins monitoring user-owned repositories for the authenticated GitHub user.
2. **PR Detection**: Automatically detects repositories with open PRs.
3. **Phase Determination**: Determines the phase of each PR (phase1/2/3, LLM working).
4. **Action Execution**:
   - **phase1**: Does nothing (waits in Draft state).
   - **phase2**: Changes Draft PRs to a Ready state and posts a comment requesting Copilot to apply changes.
   - **phase3**: Notifies that a review is needed (mobile notification if ntfy.sh is configured, opens PR page in browser).
   - **LLM working**: Waits (if all PRs are in this state, displays issues for repositories with no open PRs).
5. **Repeat**: Continues monitoring at the configured interval.

### Stopping

You can stop monitoring by pressing `Ctrl+C`.

## Notes

- GitHub CLI (`gh`) must be installed and authenticated.
- This tool assumes integration with GitHub Copilot (specifically `copilot-pull-request-reviewer` and `copilot-swe-agent`).
- **Only user-owned repositories** of the authenticated user are monitored. Organization repositories are not included to keep the tool simple and focused (YAGNI principle).
- Be mindful of API rate limits when using the GraphQL API.
- If using ntfy.sh notifications, please configure a topic on [ntfy.sh](https://ntfy.sh/) beforehand.

## Testing

The project includes a test suite using pytest:

```bash
pytest tests/
```

## License

MIT License - See the LICENSE file for details

*The English README.md is automatically generated from README.ja.md via GitHub Actions using Gemini's translation.*

*Big Brother is watching your repositories. Now it’s the cat.* 🐱