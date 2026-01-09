"""
Tests for ruleset-based phase3_merge and assign_to_copilot on/off flags
"""

from src.gh_pr_phase_monitor.config import resolve_execution_config_for_repo


class TestResolveExecutionConfigWithPhase3MergeFlag:
    """Test phase3_merge on/off flag in rulesets"""

    def test_phase3_merge_disabled_by_default(self):
        """phase3_merge should be None by default (use global settings)"""
        config = {}
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert result["enable_phase3_merge"] is None  # None means use global

    def test_ruleset_enables_phase3_merge(self):
        """Ruleset should enable phase3_merge for specific repository"""
        config = {
            "rulesets": [
                {
                    "name": "Enable merge for test-repo",
                    "repositories": ["test-repo"],
                    "enable_phase3_merge": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["enable_phase3_merge"] is True
        
        # Other repo should not be set (None means use global)
        result = resolve_execution_config_for_repo(config, "owner", "other-repo")
        assert result["enable_phase3_merge"] is None

    def test_multiple_rulesets_phase3_merge_override(self):
        """Later rulesets should override earlier ones for phase3_merge"""
        config = {
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_phase3_merge": True,
                },
                {
                    "repositories": ["test-repo"],
                    "enable_phase3_merge": False,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["enable_phase3_merge"] is False
        
        result = resolve_execution_config_for_repo(config, "owner", "other-repo")
        assert result["enable_phase3_merge"] is True

    def test_phase3_merge_flag_with_execution_flags(self):
        """phase3_merge flag works alongside execution flags"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": True,
                    "enable_phase3_merge": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["enable_execution_phase3_to_merge"] is True
        assert result["enable_phase3_merge"] is True


class TestResolveExecutionConfigWithAssignToCopilotFlag:
    """Test assign_to_copilot on/off flag in rulesets"""

    def test_assign_to_copilot_disabled_by_default(self):
        """assign_to_copilot should be None by default (use global settings)"""
        config = {}
        
        result = resolve_execution_config_for_repo(config, "owner", "repo")
        
        assert result["enable_assign_to_copilot"] is None  # None means use global

    def test_ruleset_enables_assign_to_copilot(self):
        """Ruleset should enable assign_to_copilot for specific repository"""
        config = {
            "rulesets": [
                {
                    "name": "Enable assign for test-repo",
                    "repositories": ["test-repo"],
                    "enable_assign_to_copilot": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["enable_assign_to_copilot"] is True
        
        # Other repo should not be set (None means use global)
        result = resolve_execution_config_for_repo(config, "owner", "other-repo")
        assert result["enable_assign_to_copilot"] is None

    def test_multiple_rulesets_assign_to_copilot_override(self):
        """Later rulesets should override earlier ones for assign_to_copilot"""
        config = {
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_assign_to_copilot": True,
                },
                {
                    "repositories": ["test-repo"],
                    "enable_assign_to_copilot": False,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        assert result["enable_assign_to_copilot"] is False
        
        result = resolve_execution_config_for_repo(config, "owner", "other-repo")
        assert result["enable_assign_to_copilot"] is True


class TestResolveExecutionConfigCombined:
    """Test combined phase3_merge and assign_to_copilot flags"""

    def test_both_features_in_same_ruleset(self):
        """Ruleset can enable both phase3_merge and assign_to_copilot"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_phase3_merge": True,
                    "enable_assign_to_copilot": True,
                }
            ],
        }
        
        result = resolve_execution_config_for_repo(config, "owner", "test-repo")
        
        assert result["enable_phase3_merge"] is True
        assert result["enable_assign_to_copilot"] is True

    def test_different_repos_different_flags(self):
        """Different repositories can have different feature flags"""
        config = {
            "rulesets": [
                {
                    "repositories": ["repo1"],
                    "enable_phase3_merge": True,
                },
                {
                    "repositories": ["repo2"],
                    "enable_assign_to_copilot": True,
                }
            ],
        }
        
        # repo1 should have merge enabled, assign not set (None)
        result1 = resolve_execution_config_for_repo(config, "owner", "repo1")
        assert result1["enable_phase3_merge"] is True
        assert result1["enable_assign_to_copilot"] is None  # Not set, use global
        
        # repo2 should have assign enabled, merge not set (None)
        result2 = resolve_execution_config_for_repo(config, "owner", "repo2")
        assert result2["enable_phase3_merge"] is None  # Not set, use global
        assert result2["enable_assign_to_copilot"] is True

    def test_all_repos_then_specific_override(self):
        """Can enable for all repos then disable for specific ones"""
        config = {
            "rulesets": [
                {
                    "repositories": ["all"],
                    "enable_phase3_merge": True,
                    "enable_assign_to_copilot": True,
                },
                {
                    "repositories": ["special-repo"],
                    "enable_phase3_merge": False,
                }
            ],
        }
        
        # Normal repo should have both enabled
        result1 = resolve_execution_config_for_repo(config, "owner", "normal-repo")
        assert result1["enable_phase3_merge"] is True
        assert result1["enable_assign_to_copilot"] is True
        
        # Special repo should have merge disabled but assign enabled
        result2 = resolve_execution_config_for_repo(config, "owner", "special-repo")
        assert result2["enable_phase3_merge"] is False
        assert result2["enable_assign_to_copilot"] is True

    def test_invalid_value_types_ignored(self):
        """Invalid value types should be ignored"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_phase3_merge": "true",  # String instead of boolean - should raise ValueError
                }
            ],
        }
        
        # This should raise ValueError due to validation
        try:
            resolve_execution_config_for_repo(config, "owner", "test-repo")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
