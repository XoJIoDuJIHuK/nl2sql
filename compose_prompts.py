#!/usr/bin/env python3
"""
Script to compose full system prompts from modular components.

Usage:
    python compose_prompts.py              # Compose all prompts
    python compose_prompts.py --sql        # Compose only SQL prompt
    python compose_prompts.py --graphql    # Compose only GraphQL prompt
"""

import os
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(BASE_DIR, "system_prompts")


def read_file(filename):
    """Read file content safely."""
    filepath = os.path.join(PROMPTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def compose_sql_prompt():
    """Compose SQL-specific full prompt from Common + SQL-specific parts."""
    common = read_file("CommonPrompt.md")
    sql_specific = read_file("SQLSpecificPrompt.md")

    # Remove the header from common since it's already included
    common_lines = common.split("\n")
    if common_lines[0].startswith("# ***Математическая модель"):
        common = "\n".join(common_lines[1:]).lstrip()

    return f"""# ***Математическая модель Промышленного кластера***

{common}

{sql_specific}
"""


def compose_graphql_prompt():
    """Compose GraphQL-specific full prompt from Common + GraphQL-specific parts."""
    common = read_file("CommonPrompt.md")
    graphql_specific = read_file("GraphQLSpecificPrompt.md")

    # Remove the header from common since it's already included
    common_lines = common.split("\n")
    if common_lines[0].startswith("# ***Математическая модель"):
        common = "\n".join(common_lines[1:]).lstrip()

    return f"""# ***Математическая модель Промышленного кластера***

{common}

{graphql_specific}
"""


def write_prompt(filename, content):
    """Write composed prompt to file."""
    filepath = os.path.join(PROMPTS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Written: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Compose system prompts from modular components"
    )
    parser.add_argument("--sql", action="store_true", help="Compose only SQL prompt")
    parser.add_argument(
        "--graphql", action="store_true", help="Compose only GraphQL prompt"
    )
    args = parser.parse_args()

    if args.sql:
        print("Composing SQL prompt...")
        content = compose_sql_prompt()
        write_prompt("SystemPrompt.md", content)
    elif args.graphql:
        print("Composing GraphQL prompt...")
        content = compose_graphql_prompt()
        write_prompt("GraphQLSystemPrompt.md", content)
    else:
        print("Composing all prompts...")
        content = compose_sql_prompt()
        write_prompt("SystemPrompt.md", content)

        content = compose_graphql_prompt()
        write_prompt("GraphQLSystemPrompt.md", content)

    print("\n✓ Done!")


if __name__ == "__main__":
    main()
