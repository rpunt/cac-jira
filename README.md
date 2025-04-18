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

`jiracli` references a default config:

```yaml
server: https://jira.atlassian.com
project: INVALID_DEFAULT
username: INVALID_DEFAULT
```

You'll need to set correct values for each config item in `~/.config/jiracli/config.yaml`.

### Example Configuration

```yaml
server: https://your-jira-instance.atlassian.net
project: YOUR_PROJECT_KEY
username: your.email@example.com
```

## Usage

The Jira CLI follows a command-action pattern for all operations:

```bash
jira <command> <action> [options]
```

### Global Options

- `--help`: Display help information for commands and actions.
- `--version`: Show the current version of the CLI.

### Examples

#### Issue Commands

List issues in a project:

```bash
jira issue list --project PROJECT_KEY
```

List issues with additional filtering:

```bash
jira issue list --project PROJECT_KEY --assignee "your.name" --status "In Progress"
```

Create a new issue:

```bash
jira issue create --project PROJECT_KEY --summary "Issue summary" --description "Detailed description"
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
