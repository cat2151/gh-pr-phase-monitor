"""
GraphQL client module for executing queries via GitHub CLI
"""

import json
import subprocess
from typing import Any, Dict


def execute_graphql_query(query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute a GraphQL query using gh CLI

    Args:
        query: GraphQL query string
        variables: Optional dictionary of GraphQL variables

    Returns:
        Parsed JSON response from GitHub API

    Raises:
        RuntimeError: If the query execution fails
        json.JSONDecodeError: If the response cannot be parsed
    """
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]

    # Add variables to command if provided
    if variables:
        for key, value in variables.items():
            cmd.extend(["-F", f"{key}={value}"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            error_message = f"Error parsing JSON response from gh CLI: {e}\nRaw output from gh:\n{result.stdout}"
            print(error_message)
            raise RuntimeError(error_message) from e

    except subprocess.CalledProcessError as e:
        error_message = f"Error executing GraphQL query: {e}"
        print(error_message)
        if e.stderr:
            print(f"stderr: {e.stderr}")
        raise RuntimeError(error_message) from e
