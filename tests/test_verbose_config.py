"""
Tests for verbose configuration printing functionality
"""

import io
from contextlib import redirect_stdout

from src.gh_pr_phase_monitor.config import print_config, print_repo_execution_config


def test_print_config_basic():
    """Test basic configuration printing"""
    config = {
        "interval": "1m",
        "issue_display_limit": 10,
        "no_change_timeout": "",
        "verbose": True,
    }
    
    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        print_config(config)
    output = f.getvalue()
    
    # Verify key sections are present
    assert "Configuration Settings:" in output
    assert "[Main Settings]" in output
    assert "interval: 1m" in output
    assert "verbose: True" in output


def test_print_config_with_rulesets():
    """Test configuration printing with rulesets"""
    config = {
        "interval": "1m",
        "verbose": True,
        "enable_execution_phase1_to_phase2": False,
        "rulesets": [
            {
                "name": "Test Ruleset",
                "repositories": ["owner/repo1", "repo2"],
                "enable_execution_phase1_to_phase2": True,
                "enable_execution_phase2_to_phase3": True,
            }
        ],
    }
    
    f = io.StringIO()
    with redirect_stdout(f):
        print_config(config)
    output = f.getvalue()
    
    assert "[Rulesets]" in output
    assert "Ruleset #1:" in output
    assert "Test Ruleset" in output
    assert "['owner/repo1', 'repo2']" in output
    assert "enable_execution_phase1_to_phase2: True" in output


def test_print_config_with_ntfy():
    """Test configuration printing with ntfy settings"""
    config = {
        "interval": "1m",
        "verbose": True,
        "enable_execution_phase1_to_phase2": False,
        "ntfy": {
            "enabled": True,
            "topic": "test-topic",
            "message": "PR is ready: {url}",
            "priority": 4,
        },
    }
    
    f = io.StringIO()
    with redirect_stdout(f):
        print_config(config)
    output = f.getvalue()
    
    assert "[ntfy.sh Notification Settings]" in output
    assert "enabled: True" in output
    assert "topic: test-topic" in output
    assert "message: PR is ready: {url}" in output
    assert "priority: 4" in output


def test_print_config_with_phase3_merge():
    """Test configuration printing with phase3_merge settings"""
    config = {
        "interval": "1m",
        "verbose": True,
        "enable_execution_phase1_to_phase2": False,
        "phase3_merge": {
            "enabled": True,
            "comment": "Merging PR",
            "automated": True,
            "automation_backend": "selenium",
            "wait_seconds": 10,
            "browser": "edge",
            "headless": False,
        },
    }
    
    f = io.StringIO()
    with redirect_stdout(f):
        print_config(config)
    output = f.getvalue()
    
    assert "[Phase3 Merge Settings]" in output
    assert "enabled: True" in output
    assert "comment: Merging PR" in output
    assert "automated: True" in output
    assert "automation_backend: selenium" in output


def test_print_config_with_assign_to_copilot():
    """Test configuration printing with assign_to_copilot settings"""
    config = {
        "interval": "1m",
        "verbose": True,
        "enable_execution_phase1_to_phase2": False,
        "assign_to_copilot": {
            "enabled": True,
            "automated": True,
            "automation_backend": "playwright",
            "wait_seconds": 15,
            "browser": "chromium",
            "headless": True,
        },
    }
    
    f = io.StringIO()
    with redirect_stdout(f):
        print_config(config)
    output = f.getvalue()
    
    assert "[Auto-assign to Copilot Settings]" in output
    assert "enabled: True" in output
    assert "automated: True" in output
    assert "automation_backend: playwright" in output


def test_print_repo_execution_config():
    """Test printing per-repository execution config"""
    exec_config = {
        "enable_execution_phase1_to_phase2": True,
        "enable_execution_phase2_to_phase3": False,
        "enable_execution_phase3_send_ntfy": True,
        "enable_execution_phase3_to_merge": False,
    }
    
    f = io.StringIO()
    with redirect_stdout(f):
        print_repo_execution_config("owner", "repo", exec_config)
    output = f.getvalue()
    
    assert "[Execution Config for repo]" in output
    assert "enable_execution_phase1_to_phase2: True" in output
    assert "enable_execution_phase2_to_phase3: False" in output
    assert "enable_execution_phase3_send_ntfy: True" in output
    assert "enable_execution_phase3_to_merge: False" in output


def test_print_config_no_rulesets():
    """Test configuration printing when no rulesets are defined"""
    config = {
        "interval": "1m",
        "verbose": True,
        "enable_execution_phase1_to_phase2": False,
    }
    
    f = io.StringIO()
    with redirect_stdout(f):
        print_config(config)
    output = f.getvalue()
    
    assert "[Rulesets]" in output
    assert "No rulesets configured" in output


def test_print_config_defaults():
    """Test configuration printing with default values"""
    config = {}

    f = io.StringIO()
    with redirect_stdout(f):
        print_config(config)
    output = f.getvalue()

    # Should still print configuration with defaults
    assert "Configuration Settings:" in output
    assert "[Main Settings]" in output
    # Check default values are shown
    assert "interval: 1m" in output
    assert "issue_display_limit: 10" in output
    assert "verbose: False" in output


def test_print_config_with_assign_lowest_number_issue():
    """Test configuration printing with assign_lowest_number_issue setting"""
    config = {
        "interval": "1m",
        "verbose": True,
        "assign_to_copilot": {
            "enabled": True,
            "assign_lowest_number_issue": True,
            "automated": False,
        },
    }

    f = io.StringIO()
    with redirect_stdout(f):
        print_config(config)
    output = f.getvalue()

    assert "[Auto-assign to Copilot Settings]" in output
    assert "enabled: True" in output
    assert "assign_lowest_number_issue: True" in output
