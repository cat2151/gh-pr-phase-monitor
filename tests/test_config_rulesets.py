"""
Tests for ruleset-based configuration resolution
"""

import pytest

from src.gh_pr_phase_monitor.config import resolve_execution_config_for_repo


class TestResolveExecutionConfigForRepo:
    """Test the resolve_execution_config_for_repo function"""

    def test_no_rulesets_uses_global_config(self):
        """When no rulesets are defined, use global configuration"""
        config = {
            "enable_execution_phase1_to_phase2": True,
            "enable_execution_phase2_to_phase3": False,
            "enable_execution_phase3_send_ntfy": True,
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert result["enable_execution_phase1_to_phase2"] is True
        assert result["enable_execution_phase2_to_phase3"] is False
        assert result["enable_execution_phase3_send_ntfy"] is True

    def test_empty_rulesets_uses_global_config(self):
        """When rulesets array is empty, use global configuration"""
        config = {
            "enable_execution_phase1_to_phase2": True,
            "enable_execution_phase2_to_phase3": False,
            "enable_execution_phase3_send_ntfy": True,
            "rulesets": [],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert result["enable_execution_phase1_to_phase2"] is True
        assert result["enable_execution_phase2_to_phase3"] is False
        assert result["enable_execution_phase3_send_ntfy"] is True

    def test_all_repository_matches_everything(self):
        """Ruleset with 'all' repository should match any repository"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "enable_execution_phase2_to_phase3": False,
            "enable_execution_phase3_send_ntfy": False,
            "rulesets": [
                {
                    "name": "Enable all for all repos",
                    "repositories": ["all"],
                    "enable_execution_phase1_to_phase2": True,
                    "enable_execution_phase2_to_phase3": True,
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner1", "repo1")
        assert result["enable_execution_phase1_to_phase2"] is True
        assert result["enable_execution_phase2_to_phase3"] is True
        assert result["enable_execution_phase3_send_ntfy"] is True
        
        result = resolve_execution_config_for_repo(config, "owner2", "repo2")
        assert result["enable_execution_phase1_to_phase2"] is True
        assert result["enable_execution_phase2_to_phase3"] is True
        assert result["enable_execution_phase3_send_ntfy"] is True

    def test_all_is_case_insensitive(self):
        """'all' keyword should be case-insensitive"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "repositories": ["ALL"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        assert result["enable_execution_phase1_to_phase2"] is True
        
        config["rulesets"][0]["repositories"] = ["All"]
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        assert result["enable_execution_phase1_to_phase2"] is True

    def test_exact_repository_match(self):
        """Ruleset should match specific repository by owner/name"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "name": "Enable for specific repo",
                    "repositories": ["owner1/repo1"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }
        
        # Should match
        result = resolve_execution_config_for_repo(config, "owner1", "repo1")
        assert result["enable_execution_phase1_to_phase2"] is True
        
        # Should not match
        result = resolve_execution_config_for_repo(config, "owner2", "repo2")
        assert result["enable_execution_phase1_to_phase2"] is False

    def test_repository_name_only_match(self):
        """Ruleset should match by repository name only"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }
        
        # Should match with any owner
        result = resolve_execution_config_for_repo(config, "owner1", "test-repo")
        assert result["enable_execution_phase1_to_phase2"] is True
        
        result = resolve_execution_config_for_repo(config, "owner2", "test-repo")
        assert result["enable_execution_phase1_to_phase2"] is True
        
        # Should not match different repo name
        result = resolve_execution_config_for_repo(config, "owner1", "other-repo")
        assert result["enable_execution_phase1_to_phase2"] is False

    def test_multiple_repositories_in_ruleset(self):
        """Ruleset should match multiple repositories"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "repositories": ["owner1/repo1", "owner2/repo2", "repo3"],
                    "enable_execution_phase1_to_phase2": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner1", "repo1")
        assert result["enable_execution_phase1_to_phase2"] is True
        
        result = resolve_execution_config_for_repo(config, "owner2", "repo2")
        assert result["enable_execution_phase1_to_phase2"] is True
        
        result = resolve_execution_config_for_repo(config, "any-owner", "repo3")
        assert result["enable_execution_phase1_to_phase2"] is True
        
        result = resolve_execution_config_for_repo(config, "owner3", "repo4")
        assert result["enable_execution_phase1_to_phase2"] is False

    def test_later_rulesets_override_earlier_ones(self):
        """Later rulesets in the array should override earlier ones"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "enable_execution_phase2_to_phase3": False,
            "enable_execution_phase3_send_ntfy": False,
            "rulesets": [
                {
                    "name": "First: enable all for all repos",
                    "repositories": ["all"],
                    "enable_execution_phase1_to_phase2": True,
                    "enable_execution_phase2_to_phase3": True,
                    "enable_execution_phase3_send_ntfy": True,
                },
                {
                    "name": "Second: disable for specific repo",
                    "repositories": ["owner/test-repo"],
                    "enable_execution_phase1_to_phase2": False,
                    "enable_execution_phase2_to_phase3": False,
                    "enable_execution_phase3_send_ntfy": False,
                },
            ],
        }
        
        # test-repo should be disabled (second ruleset overrides first)
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["enable_execution_phase1_to_phase2"] is False
        assert result["enable_execution_phase2_to_phase3"] is False
        assert result["enable_execution_phase3_send_ntfy"] is False
        
        # other repos should still be enabled (only first ruleset applies)
        result = resolve_execution_config_for_repo(config, "owner", "other-repo")
        assert result["enable_execution_phase1_to_phase2"] is True
        assert result["enable_execution_phase2_to_phase3"] is True
        assert result["enable_execution_phase3_send_ntfy"] is True

    def test_partial_override_preserves_other_settings(self):
        """Ruleset can override some flags while keeping others from previous rulesets"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "enable_execution_phase2_to_phase3": False,
            "enable_execution_phase3_send_ntfy": False,
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_execution_phase1_to_phase2": True,
                    "enable_execution_phase2_to_phase3": True,
                    "enable_execution_phase3_send_ntfy": True,
                },
                {
                    "repositories": ["owner/test-repo"],
                    "enable_execution_phase2_to_phase3": False,  # Only override this flag
                },
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        # phase1 and phase3 should remain True from first ruleset
        assert result["enable_execution_phase1_to_phase2"] is True
        # phase2 should be False from second ruleset
        assert result["enable_execution_phase2_to_phase3"] is False
        # phase3 should remain True from first ruleset
        assert result["enable_execution_phase3_send_ntfy"] is True

    def test_defaults_to_false_when_no_config(self):
        """When no configuration is provided, default to False"""
        config = {}
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert result["enable_execution_phase1_to_phase2"] is False
        assert result["enable_execution_phase2_to_phase3"] is False
        assert result["enable_execution_phase3_send_ntfy"] is False

    def test_handles_invalid_ruleset_gracefully(self):
        """Should handle invalid ruleset data gracefully"""
        config = {
            "enable_execution_phase1_to_phase2": True,
            "rulesets": [
                "invalid_string",  # Invalid type
                {"repositories": "not_a_list"},  # Invalid repositories type
                {"repositories": [123, 456]},  # Invalid repository name type
                None,  # Null value
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        # Should fall back to global config
        assert result["enable_execution_phase1_to_phase2"] is True

    def test_rulesets_not_list_uses_global_config(self):
        """When rulesets is not a list, use global configuration"""
        config = {
            "enable_execution_phase1_to_phase2": True,
            "rulesets": "not_a_list",
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        assert result["enable_execution_phase1_to_phase2"] is True

    def test_complex_override_scenario(self):
        """Test a complex scenario with multiple overrides"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "enable_execution_phase2_to_phase3": False,
            "enable_execution_phase3_send_ntfy": False,
            "rulesets": [
                {
                    "name": "Enable all for all repos",
                    "repositories": ["all"],
                    "enable_execution_phase1_to_phase2": True,
                },
                {
                    "name": "Enable phase2 for test repos",
                    "repositories": ["test-repo1", "test-repo2"],
                    "enable_execution_phase2_to_phase3": True,
                },
                {
                    "name": "Fully enable specific repo",
                    "repositories": ["owner/special-repo"],
                    "enable_execution_phase1_to_phase2": True,
                    "enable_execution_phase2_to_phase3": True,
                    "enable_execution_phase3_send_ntfy": True,
                },
                {
                    "name": "Disable phase1 for test-repo1",
                    "repositories": ["test-repo1"],
                    "enable_execution_phase1_to_phase2": False,
                },
            ],
        }
        
        # test-repo1: phase1=False (override), phase2=True, phase3=False
        result = resolve_execution_config_for_repo(config, "owner", "test-repo1")
        assert result["enable_execution_phase1_to_phase2"] is False
        assert result["enable_execution_phase2_to_phase3"] is True
        assert result["enable_execution_phase3_send_ntfy"] is False
        
        # test-repo2: phase1=True (from all), phase2=True, phase3=False
        result = resolve_execution_config_for_repo(config, "owner", "test-repo2")
        assert result["enable_execution_phase1_to_phase2"] is True
        assert result["enable_execution_phase2_to_phase3"] is True
        assert result["enable_execution_phase3_send_ntfy"] is False
        
        # special-repo: all True
        result = resolve_execution_config_for_repo(config, "owner", "special-repo")
        assert result["enable_execution_phase1_to_phase2"] is True
        assert result["enable_execution_phase2_to_phase3"] is True
        assert result["enable_execution_phase3_send_ntfy"] is True
        
        # other-repo: only phase1=True (from all)
        result = resolve_execution_config_for_repo(config, "owner", "other-repo")
        assert result["enable_execution_phase1_to_phase2"] is True
        assert result["enable_execution_phase2_to_phase3"] is False
        assert result["enable_execution_phase3_send_ntfy"] is False


class TestBooleanValidation:
    """Test validation of boolean configuration values"""

    def test_rejects_string_value_in_global_config(self):
        """Should raise ValueError when global config has string instead of boolean"""
        config = {
            "enable_execution_phase1_to_phase2": "true",  # String instead of boolean
        }
        
        with pytest.raises(ValueError) as exc_info:
            resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert "must be a boolean" in str(exc_info.value)
        assert "enable_execution_phase1_to_phase2" in str(exc_info.value)

    def test_rejects_integer_value_in_global_config(self):
        """Should raise ValueError when global config has integer instead of boolean"""
        config = {
            "enable_execution_phase2_to_phase3": 1,  # Integer instead of boolean
        }
        
        with pytest.raises(ValueError) as exc_info:
            resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert "must be a boolean" in str(exc_info.value)
        assert "enable_execution_phase2_to_phase3" in str(exc_info.value)

    def test_rejects_string_value_in_ruleset(self):
        """Should raise ValueError when ruleset has string instead of boolean"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase1_to_phase2": "yes",  # String instead of boolean
                }
            ],
        }
        
        with pytest.raises(ValueError) as exc_info:
            resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert "must be a boolean" in str(exc_info.value)
        assert "enable_execution_phase1_to_phase2" in str(exc_info.value)

    def test_rejects_integer_value_in_ruleset(self):
        """Should raise ValueError when ruleset has integer instead of boolean"""
        config = {
            "enable_execution_phase3_send_ntfy": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_send_ntfy": 0,  # Integer instead of boolean
                }
            ],
        }
        
        with pytest.raises(ValueError) as exc_info:
            resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert "must be a boolean" in str(exc_info.value)
        assert "enable_execution_phase3_send_ntfy" in str(exc_info.value)

    def test_accepts_valid_boolean_values(self):
        """Should accept proper boolean values"""
        config = {
            "enable_execution_phase1_to_phase2": True,
            "enable_execution_phase2_to_phase3": False,
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase1_to_phase2": False,
                    "enable_execution_phase2_to_phase3": True,
                    "enable_execution_phase3_send_ntfy": True,
                }
            ],
        }
        
        # Should not raise any exception
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["enable_execution_phase1_to_phase2"] is False
        assert result["enable_execution_phase2_to_phase3"] is True
        assert result["enable_execution_phase3_send_ntfy"] is True

    def test_validation_does_not_affect_non_matching_rulesets(self):
        """Validation should only occur for rulesets that match the repository"""
        config = {
            "enable_execution_phase1_to_phase2": False,
            "rulesets": [
                {
                    "repositories": ["other-repo"],
                    "enable_execution_phase1_to_phase2": "invalid",  # Invalid but won't be checked
                },
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase1_to_phase2": True,  # Valid
                },
            ],
        }
        
        # Should not raise error because first ruleset doesn't match
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["enable_execution_phase1_to_phase2"] is True
