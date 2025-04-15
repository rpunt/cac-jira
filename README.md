# Jira CLI

A command-line interface for interacting with Jira.

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management.

```bash
# Clone the repository
git clone https://github.com/yourusername/jiracli.git
cd jiracli

# Install with Poetry
poetry install
```

## Usage

The Jira CLI follows a command-action pattern for all operations:

```bash
jira <command> <action> [options]
```

### Examples

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

List projects:
```bash
jira project list
```

Include archived projects in listing:
```bash
jira project list --archived
```

### Authentication

The CLI supports the following authentication methods:

1. Command-line arguments:
```bash
jira issue list --server https://jira.example.com --username your_username --password your_api_token
```

2. Environment variables:
```bash
export JIRA_SERVER=https://jira.example.com
export JIRA_USERNAME=your_username
export JIRA_PASSWORD=your_api_token
jira issue list
```

## Development

### Setup development environment

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

1. Create a new action module in the appropriate command directory
2. Define a class that inherits from the command's base class
3. Implement `define_arguments()` and `execute()` methods
