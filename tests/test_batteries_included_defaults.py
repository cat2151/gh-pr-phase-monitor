"""
Tests for batteries-included default configuration values
Tests that phase3_merge and assign_to_copilot work with defaults when TOML sections are missing
"""

from src.gh_pr_phase_monitor.config import (
    DEFAULT_ASSIGN_TO_COPILOT_CONFIG,
    DEFAULT_PHASE3_MERGE_CONFIG,
    get_assign_to_copilot_config,
    get_phase3_merge_config,
)


class TestPhase3MergeDefaults:
    """Test phase3_merge default configuration"""

    def test_empty_config_returns_defaults(self):
        """When config has no phase3_merge section, return defaults"""
        config = {}
        result = get_phase3_merge_config(config)

        assert result == DEFAULT_PHASE3_MERGE_CONFIG
        assert result["comment"] == "agentによって、レビュー指摘対応が完了したと判断します。userの責任のもと、userレビューは省略します。PRをMergeします。"
        assert result["automated"] is False
        assert result["automation_backend"] == "playwright"
        assert result["wait_seconds"] == 10
        assert result["browser"] == "chromium"
        assert result["headless"] is False

    def test_partial_config_merges_with_defaults(self):
        """When config has partial phase3_merge section, merge with defaults"""
        config = {
            "phase3_merge": {
                "comment": "Custom merge comment",
                "automated": True,
            }
        }
        result = get_phase3_merge_config(config)

        # User values should override defaults
        assert result["comment"] == "Custom merge comment"
        assert result["automated"] is True

        # Missing values should use defaults
        assert result["automation_backend"] == "playwright"
        assert result["wait_seconds"] == 10
        assert result["browser"] == "chromium"
        assert result["headless"] is False

    def test_full_config_overrides_all_defaults(self):
        """When config has full phase3_merge section, use all user values"""
        config = {
            "phase3_merge": {
                "comment": "Custom comment",
                "automated": True,
                "automation_backend": "selenium",
                "wait_seconds": 20,
                "browser": "firefox",
                "headless": True,
            }
        }
        result = get_phase3_merge_config(config)

        # All values should be from user config
        assert result["comment"] == "Custom comment"
        assert result["automated"] is True
        assert result["automation_backend"] == "selenium"
        assert result["wait_seconds"] == 20
        assert result["browser"] == "firefox"
        assert result["headless"] is True

    def test_invalid_config_section_returns_defaults(self):
        """When phase3_merge is not a dict, return defaults"""
        config = {"phase3_merge": "not a dict"}
        result = get_phase3_merge_config(config)

        assert result == DEFAULT_PHASE3_MERGE_CONFIG


class TestAssignToCopilotDefaults:
    """Test assign_to_copilot default configuration"""

    def test_empty_config_returns_defaults(self):
        """When config has no assign_to_copilot section, return defaults"""
        config = {}
        result = get_assign_to_copilot_config(config)

        assert result == DEFAULT_ASSIGN_TO_COPILOT_CONFIG
        assert result["automation_backend"] == "playwright"
        assert result["wait_seconds"] == 10
        assert result["browser"] == "chromium"
        assert result["headless"] is False

    def test_partial_config_merges_with_defaults(self):
        """When config has partial assign_to_copilot section, merge with defaults"""
        config = {
            "assign_to_copilot": {
                "browser": "firefox",
            }
        }
        result = get_assign_to_copilot_config(config)

        # User values should override defaults
        assert result["browser"] == "firefox"

        # Missing values should use defaults
        assert result["automation_backend"] == "playwright"
        assert result["wait_seconds"] == 10
        assert result["headless"] is False

    def test_full_config_overrides_all_defaults(self):
        """When config has full assign_to_copilot section, use all user values"""
        config = {
            "assign_to_copilot": {
                "automation_backend": "selenium",
                "wait_seconds": 15,
                "browser": "edge",
                "headless": True,
            }
        }
        result = get_assign_to_copilot_config(config)

        # All values should be from user config
        assert result["automation_backend"] == "selenium"
        assert result["wait_seconds"] == 15
        assert result["browser"] == "edge"
        assert result["headless"] is True

    def test_invalid_config_section_returns_defaults(self):
        """When assign_to_copilot is not a dict, return defaults"""
        config = {"assign_to_copilot": "not a dict"}
        result = get_assign_to_copilot_config(config)

        assert result == DEFAULT_ASSIGN_TO_COPILOT_CONFIG


class TestDefaultConstantsAreSensible:
    """Test that the default constants have sensible values"""

    def test_phase3_merge_defaults_are_safe(self):
        """phase3_merge defaults should be safe (not automated)"""
        assert DEFAULT_PHASE3_MERGE_CONFIG["automated"] is False
        assert DEFAULT_PHASE3_MERGE_CONFIG["wait_seconds"] >= 10
        assert DEFAULT_PHASE3_MERGE_CONFIG["comment"] != ""

    def test_assign_to_copilot_defaults_are_safe(self):
        """assign_to_copilot defaults should be safe (reasonable wait time)"""
        assert DEFAULT_ASSIGN_TO_COPILOT_CONFIG["wait_seconds"] >= 10

    def test_both_defaults_use_playwright(self):
        """Both features should default to playwright backend"""
        assert DEFAULT_PHASE3_MERGE_CONFIG["automation_backend"] == "playwright"
        assert DEFAULT_ASSIGN_TO_COPILOT_CONFIG["automation_backend"] == "playwright"

    def test_both_defaults_use_chromium(self):
        """Both features should default to chromium browser"""
        assert DEFAULT_PHASE3_MERGE_CONFIG["browser"] == "chromium"
        assert DEFAULT_ASSIGN_TO_COPILOT_CONFIG["browser"] == "chromium"
