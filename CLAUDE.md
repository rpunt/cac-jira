# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

cac-jira is a CLI tool for interacting with Jira, built on the `cac-core` framework. It follows a `jira <command> <action> [options]` pattern (e.g., `jira issue list`, `jira project show`).

## Development Commands

```bash
# Setup
uv sync                        # Install all dependencies
source .venv/bin/activate      # Activate virtual environment

# Testing
uv run pytest                  # Run all tests
uv run pytest tests/test_cli.py  # Run a single test file

# Linting & Formatting
ruff check --target-version=py310 .   # Lint
ruff format --diff .                  # Check formatting

# Type checking
mypy cac_jira/
```

## Architecture

### Command-Action Discovery

Commands and actions are **dynamically discovered** at runtime by scanning the filesystem — no registration needed. The CLI entry point (`cac_jira/cli/main.py`) scans `cac_jira/commands/` for subdirectories (commands) and their Python modules (actions).

### Class Naming Convention

Action classes **must** follow the pattern `{Command}{Action}` with each part capitalized. For example, a file at `commands/issue/create.py` must define a class named `IssueCreate`. The discovery system in `main.py` uses `f"{command.capitalize()}{action.capitalize()}"` to find the class.

### Class Hierarchy

```
Command (cac_core)
└── JiraCommand (cac_jira/commands/command.py)
    ├── JiraIssueCommand (cac_jira/commands/issue/__init__.py)
    │   └── Individual actions (create, list, show, update, begin, close, etc.)
    └── JiraProjectCommand (cac_jira/commands/project/__init__.py)
        └── Individual actions (list, show)
```

Each action must implement two abstract methods: `define_arguments(parser)` and `execute(args)`.

### Command Execution & Error Handling

`JiraCommand` uses a template method: the CLI entry point calls `command.run(args)` (a concrete method on `JiraCommand`), which invokes the subclass's `execute(args)` and maps any exception raised by the Jira client (`JIRAError` or otherwise) to a logged, non-zero exit code. Because of this:

- Actions implement `execute(args)` as straight-line logic. They may let client calls raise; they do **not** need their own try/except around `JiraClient` calls.
- `execute()` returns an int exit code — `0`/`None` for success, non-zero for the command's own validation failures (e.g. missing/invalid input, not-found guards).
- `main()` propagates that exit code, so `$?` reflects success/failure.

`JiraClient` (`cac_jira/core/client.py`) is a thin passthrough: each method returns the underlying `jira-python` result or **raises** (`JIRAError`, or `ValueError` for invalid arguments). It does not return sentinel values or swallow exceptions — the command layer decides how to present errors.

### Module Initialization

`cac_jira/__init__.py` exposes three module-level attributes used by `JiraCommand` and all actions: `CONFIG`, `JIRA_CLIENT`, and `log`. Initialization is split and lazy (via module `__getattr__`):

- `CONFIG` triggers `_initialize_config()` — loads the config file and runs first-run prompts (server, username, project). This is **network-free** and cheap, so it runs during argument parsing (including `--help`).
- `JIRA_CLIENT` triggers `_initialize_client()` — fetches the API token and connects to Jira. This only happens the first time a command actually needs the client (i.e. at execution time), so `--help` and argument parsing work offline without credentials.

`JiraCommand.__init__` loads `CONFIG` eagerly but exposes `jira_client` as a lazy property, so constructing a command (which the discovery loop does for every action) does not open a connection.

### Key Dependencies

- **cac-core**: Provides base `Command` class, config management (`cac.config.Config`), credential storage (`cac.credentialmanager.CredentialManager`), logging, output formatting (`cac.output.Output`), and update checking.
- **jira**: The `jira-python` library, wrapped by `JiraClient` (`cac_jira/core/client.py`).

### Adding a New Action

1. Create a new `.py` file in the appropriate command directory (e.g., `cac_jira/commands/issue/myaction.py`)
2. Define a class following the naming convention (e.g., `IssueMyaction`)
3. Inherit from the command's base class (e.g., `JiraIssueCommand`)
4. Implement `define_arguments()` and `execute()` — `execute()` returns an exit code (`0`/`None` on success, non-zero on failure) and may let `JiraClient` calls raise; the base `run()` wrapper handles the error mapping. Do not override `run()`.

### Configuration & Credentials

- Config file: `~/.config/cac_jira/config.yaml`
- Config template: `cac_jira/config/cac_jira.yaml`
- Credentials stored in system keyring (e.g., macOS Keychain) under `cac-jira`

## Code Style

- Python >=3.10 required (CI tests 3.10–3.14)
- Black formatting with 88-char line length
- isort with black-compatible profile
- Output formatting uses `cac_core.output.Output` (supports table and JSON formats)

## CI/CD

- Version is derived from git tags via `setuptools-scm` (no static version in `pyproject.toml`); no per-PR version bump is required
- Tests run on push and PR across Python 3.10–3.14 (`pytest.yaml`)
- Releases triggered by version tags (v*), published to PyPI (`create_artifacts_and_publish.yaml`)
