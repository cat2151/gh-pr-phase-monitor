# Ruleset-based Configuration

## Overview

The ruleset-based configuration feature allows fine-grained control over automatic execution features on a per-repository or per-group basis. All execution control flags must be specified inside `[[rulesets]]` sections - global flags are no longer supported.

## Features

- **Per-repository control**: Enable or disable features for specific repositories
- **Pattern matching**: Use "all" to match all repositories, or specify by repository name
- **Override mechanism**: Later rulesets override earlier ones, allowing flexible configuration
- **Ruleset-only**: Execution flags can ONLY be specified in rulesets (global flags are deprecated)

## Configuration Format

Rulesets are defined in the `config.toml` file using the `[[rulesets]]` array syntax:

```toml
[[rulesets]]
name = "Ruleset name (optional)"
repositories = ["repo-name", "another-repo", "all"]
enable_execution_phase1_to_phase2 = true
enable_execution_phase2_to_phase3 = true
enable_execution_phase3_send_ntfy = true
enable_execution_phase3_to_merge = true
```

### Fields

- **name** (optional): A descriptive name for the ruleset for documentation purposes
- **repositories** (required): An array of repository patterns to match:
  - `"all"` - Matches all repositories (case-insensitive)
  - `"repo-name"` - Matches any repository with this name
- **enable_execution_phase1_to_phase2** (optional): Enable automatic PR ready marking
- **enable_execution_phase2_to_phase3** (optional): Enable automatic comment posting
- **enable_execution_phase3_send_ntfy** (optional): Enable ntfy notifications
- **enable_execution_phase3_to_merge** (optional): Enable automatic PR merging

## Resolution Order

Rulesets are applied in the following order:

1. **Default to false**: All execution flags default to false when no rulesets match
2. **Rulesets in order**: Apply each matching ruleset in the order they appear
3. **Later overrides earlier**: If multiple rulesets match, later ones override earlier ones
4. **Partial updates**: Rulesets can specify only some flags, leaving others unchanged

## Examples

### Example 1: Disable all by default, enable for specific repos

```toml
# Disable all by default
[[rulesets]]
name = "Default - all disabled"
repositories = ["all"]
enable_execution_phase1_to_phase2 = false
enable_execution_phase2_to_phase3 = false
enable_execution_phase3_send_ntfy = false
enable_execution_phase3_to_merge = false

# Enable full automation for a specific repository
[[rulesets]]
name = "Full automation for my-app"
repositories = ["my-app"]
enable_execution_phase1_to_phase2 = true
enable_execution_phase2_to_phase3 = true
enable_execution_phase3_send_ntfy = true
enable_execution_phase3_to_merge = true

# Enable only notifications for production repositories
[[rulesets]]
name = "Production repos - notifications only"
repositories = ["prod-api", "prod-web"]
enable_execution_phase3_send_ntfy = true
```

### Example 2: Enable all by default, disable for specific repos

```toml
# Enable full automation for all repositories by default
[[rulesets]]
name = "Enable all by default"
repositories = ["all"]
enable_execution_phase1_to_phase2 = true
enable_execution_phase2_to_phase3 = true
enable_execution_phase3_send_ntfy = true
enable_execution_phase3_to_merge = true

# Disable automation for experimental repositories
[[rulesets]]
name = "Disable for experimental repos"
repositories = ["experimental-1", "experimental-2"]
enable_execution_phase1_to_phase2 = false
enable_execution_phase2_to_phase3 = false
enable_execution_phase3_send_ntfy = false
enable_execution_phase3_to_merge = false
```

### Example 3: Different settings for different repository groups

```toml
# Test repositories: Full automation
[[rulesets]]
name = "Test repositories"
repositories = ["test-repo-1", "test-repo-2", "test-repo-3"]
enable_execution_phase1_to_phase2 = true
enable_execution_phase2_to_phase3 = true
enable_execution_phase3_send_ntfy = true
enable_execution_phase3_to_merge = true

# Production repositories: Only phase1 and notifications
[[rulesets]]
name = "Production repositories"
repositories = ["prod-api", "prod-web"]
enable_execution_phase1_to_phase2 = true
enable_execution_phase3_send_ntfy = true

# Personal repositories: Everything enabled
[[rulesets]]
name = "Personal projects"
repositories = ["personal-project-1", "personal-project-2"]
enable_execution_phase1_to_phase2 = true
enable_execution_phase2_to_phase3 = true
enable_execution_phase3_send_ntfy = true
```

### Example 4: Override with partial settings

```toml
# Start with all disabled
enable_execution_phase1_to_phase2 = false
enable_execution_phase2_to_phase3 = false
enable_execution_phase3_send_ntfy = false

# Enable everything for all repositories
[[rulesets]]
name = "Enable all features for all repos"
repositories = ["all"]
enable_execution_phase1_to_phase2 = true
enable_execution_phase2_to_phase3 = true
enable_execution_phase3_send_ntfy = true

# Disable only phase2 for a specific repo (phase1 and phase3 remain enabled)
[[rulesets]]
name = "Special case: disable phase2 only"
repositories = ["special-repo"]
enable_execution_phase2_to_phase3 = false
```

## Migration Guide

If you have an existing configuration with only global flags:

```toml
enable_execution_phase1_to_phase2 = true
enable_execution_phase2_to_phase3 = true
enable_execution_phase3_send_ntfy = true
```

This configuration will continue to work as before. The global flags are used as defaults when no rulesets match a repository.

To migrate to rulesets while maintaining the same behavior:

```toml
# Keep global flags as defaults
enable_execution_phase1_to_phase2 = true
enable_execution_phase2_to_phase3 = true
enable_execution_phase3_send_ntfy = true

# Optionally add rulesets for specific exceptions
[[rulesets]]
name = "Disable for experimental repo"
repositories = ["experimental"]
enable_execution_phase1_to_phase2 = false
enable_execution_phase2_to_phase3 = false
enable_execution_phase3_send_ntfy = false
```

## Best Practices

1. **Start with safe defaults**: Set global flags to `false` and explicitly enable for specific repositories
2. **Use descriptive names**: Add a `name` field to each ruleset for documentation
3. **Order matters**: Place more general rules first (like "all") and specific overrides later
4. **Test with dry-run**: Test your configuration first with dry-run mode to ensure correct behavior
5. **Use repository names only**: Specify repositories by name only (e.g., `"my-repo"`)

## Troubleshooting

If features are not enabled/disabled as expected:

1. Check the order of rulesets - later ones override earlier ones
2. Verify repository name format - use repository name only
3. Check for typos in repository names
4. Remember that `"all"` is case-insensitive
5. Use the test suite to validate configuration: `pytest tests/test_config_rulesets.py -v`
