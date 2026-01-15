"""
Tests for phase3_merge configuration validation (fail-fast on missing comment)
"""

import pytest

from src.gh_pr_phase_monitor.config import validate_phase3_merge_config_required


class TestValidatePhase3MergeConfigRequired:
    """Test validation of phase3_merge configuration when auto-merge is enabled"""

    def test_validation_passes_when_auto_merge_disabled(self):
        """Validation should pass when auto-merge is disabled"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": False,
                }
            ],
        }
        # Should not raise any exception
        validate_phase3_merge_config_required(config, "owner", "test-repo")

    def test_validation_passes_when_comment_is_configured(self):
        """Validation should pass when auto-merge is enabled and comment is configured"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                }
            ],
            "phase3_merge": {
                "comment": "Custom merge comment",
            },
        }
        # Should not raise any exception
        validate_phase3_merge_config_required(config, "owner", "test-repo")

    def test_validation_fails_when_phase3_merge_section_missing(self):
        """Validation should fail when auto-merge is enabled but [phase3_merge] section is missing"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                }
            ],
        }
        with pytest.raises(SystemExit) as exc_info:
            validate_phase3_merge_config_required(config, "owner", "test-repo")
        assert exc_info.value.code == 1

    def test_validation_fails_when_comment_field_missing(self):
        """Validation should fail when auto-merge is enabled but comment field is missing"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                }
            ],
            "phase3_merge": {
                "automated": False,
            },
        }
        with pytest.raises(SystemExit) as exc_info:
            validate_phase3_merge_config_required(config, "owner", "test-repo")
        assert exc_info.value.code == 1

    def test_validation_passes_for_non_matching_repository(self):
        """Validation should pass when auto-merge is enabled for different repository"""
        config = {
            "rulesets": [
                {
                    "repositories": ["other-repo"],
                    "enable_execution_phase3_to_merge": True,
                }
            ],
        }
        # Should not raise any exception because test-repo doesn't match
        validate_phase3_merge_config_required(config, "owner", "test-repo")

    def test_validation_with_all_repositories_wildcard(self):
        """Validation should work with 'all' repositories wildcard"""
        config = {
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_phase3_to_merge": True,
                }
            ],
            "phase3_merge": {
                "comment": "Merge comment",
            },
        }
        # Should not raise any exception
        validate_phase3_merge_config_required(config, "owner", "test-repo")

    def test_validation_fails_with_all_repositories_wildcard_no_comment(self):
        """Validation should fail with 'all' repositories wildcard when comment is missing"""
        config = {
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_phase3_to_merge": True,
                }
            ],
        }
        with pytest.raises(SystemExit) as exc_info:
            validate_phase3_merge_config_required(config, "owner", "test-repo")
        assert exc_info.value.code == 1

    def test_validation_with_multiple_rulesets(self):
        """Validation should work with multiple rulesets"""
        config = {
            "rulesets": [
                {
                    "repositories": ["other-repo"],
                    "enable_execution_phase3_to_merge": False,
                },
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                },
            ],
            "phase3_merge": {
                "comment": "Merge comment",
            },
        }
        # Should not raise any exception
        validate_phase3_merge_config_required(config, "owner", "test-repo")

    def test_validation_with_ruleset_override(self):
        """Validation should respect ruleset override order"""
        config = {
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_phase3_to_merge": True,
                },
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": False,
                },
            ],
        }
        # Should not raise any exception because test-repo overrides to false
        validate_phase3_merge_config_required(config, "owner", "test-repo")

    def test_validation_fails_when_phase3_merge_is_not_dict(self):
        """Validation should fail when phase3_merge is not a dictionary"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                }
            ],
            "phase3_merge": "not a dict",
        }
        with pytest.raises(SystemExit) as exc_info:
            validate_phase3_merge_config_required(config, "owner", "test-repo")
        assert exc_info.value.code == 1
