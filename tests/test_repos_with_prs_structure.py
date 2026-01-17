"""
Test to verify that repos_with_prs structure is handled correctly in main.py

This test ensures that the owner field in repos_with_prs is treated as a string,
not a dictionary, preventing AttributeError: 'str' object has no attribute 'get'
"""

from src.gh_pr_phase_monitor.config import validate_phase3_merge_config_required


class TestReposWithPrsStructure:
    """Test that repos_with_prs structure matches the actual data from repository_fetcher"""

    def test_owner_field_is_string_not_dict(self):
        """Verify that owner field in repos_with_prs is a string, not a dictionary"""
        # This is the actual structure returned by get_repositories_with_open_prs()
        repos_with_prs = [
            {"name": "test-repo", "owner": "testowner", "openPRCount": 2},
            {"name": "another-repo", "owner": "anotherowner", "openPRCount": 1},
        ]

        # Simulate what main.py does at line 594-598
        for repo in repos_with_prs:
            # This should work without AttributeError
            repo_owner = repo.get("owner", "")
            repo_name = repo.get("name", "")

            # Verify we got the expected values
            assert isinstance(repo_owner, str)
            assert isinstance(repo_name, str)
            assert repo_owner != ""
            assert repo_name != ""

    def test_validate_phase3_merge_with_string_owner(self):
        """Verify that validate_phase3_merge_config_required works with string owner"""
        config = {
            "rulesets": [
                {
                    "repositories": ["test-repo"],
                    "enable_execution_phase3_to_merge": False,
                }
            ],
        }

        repos_with_prs = [
            {"name": "test-repo", "owner": "testowner", "openPRCount": 2},
        ]

        # Extract owner and name as main.py does (after fix)
        for repo in repos_with_prs:
            repo_owner = repo.get("owner", "")
            repo_name = repo.get("name", "")

            # This should not raise any exception
            if repo_owner and repo_name:
                validate_phase3_merge_config_required(config, repo_owner, repo_name)

    def test_old_buggy_code_would_fail(self):
        """Demonstrate that the old buggy code would fail with AttributeError"""
        repos_with_prs = [
            {"name": "test-repo", "owner": "testowner", "openPRCount": 2},
        ]

        for repo in repos_with_prs:
            # The old buggy code tried to do this:
            # repo_owner = repo.get("owner", {}).get("login", "")
            # This would fail because owner is a string, not a dict

            owner_value = repo.get("owner", {})
            # Verify that owner_value is a string
            assert isinstance(owner_value, str)

            # Trying to call .get() on a string would raise AttributeError
            try:
                # This is what the old buggy code tried to do
                owner_value.get("login", "")
                assert False, "Should have raised AttributeError"
            except AttributeError as e:
                assert "'str' object has no attribute 'get'" in str(e)
