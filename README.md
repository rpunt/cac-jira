# Jira CLI

A command-line interface for interacting with Jira.

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

[cac_core](https://github.com/rpunt/cac_core) is also required.

### Steps to Install

```bash
# Clone the repositories
git clone https://github.com/rpunt/cac_core.git
git clone https://github.com/rpunt/jiracli.git

# Install with Poetry
cd cac_core; poetry build; poetry install
cd ../jiracli; poetry build; poetry install
```

## Authentication

1. [Create a Jira API token](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create a keychain item in the following format:
   - **Name**: `jiracli`
   - **Kind**: `application password`
   - **Account**: your Jira Cloud username (probably your e-mail address)
   - **Password**: your API token

## Configuration

Create a configuration file at `~/.config/jiracli/config.yaml`:

```yaml
server: https://your-jira-instance.atlassian.net
project: YOUR_PROJECT_KEY  # Optional default project
username: your.email@example.com
```

## Usage

The Jira CLI follows a command-action pattern for all operations:

```bash
jira <command> <action> [options]
```

### Global Options

- `--verbose`: Enable debug output
- `--output [table|json]`: Control output format
<!-- --suppress-output: Hide command output -->
<!-- --version: Display version information -->
- `--help`: Show command help

### Examples

#### Issue Commands

List issues in a project:

```bash
jira issue list --project PROJ
```

List issues with additional filtering:

```bash
jira issue list --project PROJ
```

Create a new issue:

```bash
jira issue create --project PROJ --type Task --title "Fix login bug" --description "Users can't log in"
```

Create and assign to yourself:

```bash
jira issue create --project PROJ --type Bug --title "Server crash" --assign
```

Create and immediately start work:

```bash
jira issue create --project PROJ --type Story --title "Add login feature" --begin
```

Add an issue to an epic:

```bash
jira issue create --project PROJ --type Task --title "Subtask" --epic PROJ-100
```

Transition an issue:

```bash
jira issue begin PROJ-123   # Start work
jira issue done PROJ-123    # Mark as complete
```

#### Project Commands

List projects:

```bash
jira project list
```

Include archived projects in listing:

```bash
jira project list --archived
```

#### Advanced Examples

Update an issue's status:

```bash
jira issue update --issue ISSUE_KEY --status "Done"
```

Add a comment to an issue:

```bash
jira issue comment --issue ISSUE_KEY --comment "This is a comment."
```

## Development

### Setup Development Environment

```bash
# Install dependencies including dev dependencies
poetry install

# Run tests
poetry run pytest
```

### Project Structure

- `jiracli/commands/` - Command implementations
  - `issue/` - Issue-related commands
  - `project/` - Project-related commands
- `jiracli/cli/` - CLI entry point and argument parsing

### Adding New Commands

1. Create a new action module in the appropriate command directory.
2. Define a class that inherits from the command's base class.
3. Implement `define_arguments()` and `execute()` methods.
