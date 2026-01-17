"""
Wait and countdown handling with hot reload support
"""

import time
from typing import Any, Dict, Tuple

import tomli

from .config import get_config_mtime, load_config, parse_interval, print_config
from .time_utils import format_elapsed_time


def wait_with_countdown(
    interval_seconds: int, interval_str: str, config_path: str = "", last_config_mtime: float = 0.0
) -> Tuple[Dict[str, Any], int, str, float]:
    """Wait for the specified interval with a live countdown display and hot reload support

    This function checks the config file's modification timestamp every second during the wait.
    If the config file has been modified, it reloads the configuration and updates the interval.

    Note: The filesystem check every second is intentional per the issue requirements for
    hot reload functionality during the wait state.

    Args:
        interval_seconds: Number of seconds to wait
        interval_str: Human-readable interval string (e.g., "1m", "30s")
        config_path: Path to the configuration file (empty string disables hot reload)
        last_config_mtime: Last known modification time of the config file

    Returns:
        Tuple of (config, interval_seconds, interval_str, new_config_mtime)
    """
    print(f"\n{'=' * 50}")
    print(f"Waiting {interval_str} until next check...")
    print(f"{'=' * 50}")

    # Current config values (may be updated during wait)
    current_config = {}
    current_interval_seconds = interval_seconds
    current_interval_str = interval_str
    current_mtime = last_config_mtime

    # Track actual elapsed time from the start of wait
    wait_start_time = time.time()

    # Display countdown with updates every second using ANSI escape sequences
    while True:
        # Calculate actual elapsed time
        actual_elapsed = time.time() - wait_start_time

        # Check if we've waited long enough
        if actual_elapsed >= interval_seconds:
            break

        # Calculate remaining time
        remaining = interval_seconds - actual_elapsed
        remaining_str = format_elapsed_time(remaining)
        # Print countdown on same line using carriage return
        print(f"\rWaiting {remaining_str}     ", end="", flush=True)
        sleep_duration = min(1, remaining)
        time.sleep(sleep_duration)

        # Check if config file has been modified (only if config_path is provided)
        # Note: This check happens every second as per hot reload requirements
        if config_path:
            try:
                new_mtime = get_config_mtime(config_path)
                if new_mtime != current_mtime:
                    # Config file has been modified, reload it
                    print(f"\n\n{'=' * 50}")
                    print("設定ファイルの変更を検知しました。再読み込みします...")
                    print(f"{'=' * 50}")

                    try:
                        new_config = load_config(config_path)
                        new_interval_str = new_config.get("interval", "1m")
                        new_interval_seconds = parse_interval(new_interval_str)

                        # Update current values
                        current_config = new_config
                        current_interval_seconds = new_interval_seconds
                        current_interval_str = new_interval_str
                        current_mtime = new_mtime

                        print("設定を再読み込みしました。")
                        print(f"新しい監視間隔: {new_interval_str} ({new_interval_seconds}秒)")

                        # Print config if verbose mode is enabled
                        if new_config.get("verbose", False):
                            print_config(new_config)

                        print(f"{'=' * 50}")
                        print(f"Waiting {current_interval_str} until next check...")
                        print(f"{'=' * 50}")

                    except (ValueError, tomli.TOMLDecodeError) as e:
                        # Config file has invalid format (TOML parsing error or invalid interval)
                        # Update mtime to avoid repeatedly trying to reload the same broken config
                        current_mtime = new_mtime
                        print(f"設定ファイルの再読み込みに失敗しました: {e}")
                        print("前の設定を使い続けます。")
                        print(f"{'=' * 50}")
                        print(f"Waiting {current_interval_str} until next check...")
                        print(f"{'=' * 50}")

            except FileNotFoundError:
                # Config file was deleted, continue with current config
                pass
            except (OSError, PermissionError):
                # File system errors (e.g., permission issues), ignore and continue
                pass

    # Final update - show countdown complete (0 remaining)
    final_str = format_elapsed_time(0)
    print(f"\rWaiting {final_str}     ", flush=True)
    print()  # New line after countdown completes

    return current_config, current_interval_seconds, current_interval_str, current_mtime
