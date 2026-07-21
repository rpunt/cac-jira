# Jira CLI

A command-line interface for interacting with Jira.

This project uses [UV](https://github.com/astral-sh/uv) for dependency management.

## Installation

```bash
pip install cac-jira
```

## Authentication

On first-run, you'll be prompted for a Jira API token; generate one [here](https://id.atlassian.com/manage-profile/security/api-tokens). This will be stored in your system credential store (e.g. Keychain on Mac OS) in an item called `cac-jira`.

## Configuration

On first-run, a configuration file will be generated at `~/.config/cac_jira/config.yaml`. In this file you'll need to replace the values of `server` and `username` with appropriate values.

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

- `--verbose`: Enable debug output (includes a traceback for unexpected errors)
- `--output [table|json]`: Control output format (default table)
- `--help`: Show command help
<!-- --suppress-output: Hide command output -->
<!-- --version: Display version information -->

Commands exit `0` on success and non-zero on failure (invalid input, a
not-found issue/project, or a Jira API error), so they compose safely in
scripts. `--help` and argument parsing work offline and do not require
credentials — the Jira connection is only established when a command runs.

### Examples

#### Issue Commands

List issues in a project:

```bash
jira issue list --project PROJ
```

List only issues assigned to you (and optionally include completed ones):

```bash
jira issue list --project PROJ --mine
jira issue list --project PROJ --done   # include issues that are resolved
```

Create a new issue:

```bash
jira issue create --project PROJ --type Task --title "Fix login bug" --description "Users can't log in"
```

Create a new issue of a type that requires custom fields:

```bash
#
# This assumes the name of the custom fields is "Custom Field One" and "Custom Field Two";
# the field name will be swapped to lower-case, and spaces replaced with underscores
#
jira issue create --project PROJ --type Custom\ Issue\ Type --title "Issue Title" --description "Issue description" \
  --field custom_field_one custom_field_value \
  --field custom_field_two custom_field_value
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

Label an issue:

```bash
jira issue label --issue ISSUE_KEY --labels label1,label2
```

Transition an issue:

```bash
jira issue begin --issue ISSUE_KEY    # Start work
jira issue block --issue ISSUE_KEY    # Mark as blocked
jira issue close --issue ISSUE_KEY    # Mark as complete
```

Delete an issue (prompts for confirmation; pass `--force` to skip it, e.g. in scripts):

```bash
jira issue delete --issue ISSUE_KEY
jira issue delete --issue ISSUE_KEY --force
```

#### Project Commands

List all projects:

```bash
jira project list
```

Filter projects by name or key (case-insensitive, partial match):

```bash
jira project list --name "Core"
jira project list --key COR
```

Show a single project by its key:

```bash
jira project show PROJ
```

#### Advanced Examples

Update an issue's title or description:

```bash
jira issue update --issue ISSUE_KEY --title "New issue title" --description "new issue description"
```

Add a comment to an issue:

```bash
jira issue comment --issue ISSUE_KEY --comment "This is a comment."
```

List all issue IDs matching a label:

```bash
jira issue list --output json | jq -r '.[] | select(.Labels | contains("production")) | .ID'
```

## Shell Completion

`jira` supports tab-completion of commands, actions, and options via
[argcomplete](https://kislyuk.github.io/argcomplete/).

### Enabling completion

The recommended approach is per-command registration. Add the appropriate line
to your shell startup file:

```bash
# bash (~/.bashrc) or zsh (~/.zshrc)
eval "$(register-python-argcomplete jira)"
```

Then restart your shell (or `source` the file). Tab-completion works
immediately:

```bash
jira <TAB>                 # -> issue  project
jira issue <TAB>           # -> assign attach begin ... show update
jira issue show --<TAB>    # -> --issue --output --project --verbose
```

<details>
<summary>Alternative: global activation</summary>

To enable argcomplete for every marker-tagged program at once (instead of
per-command), run this once and restart your shell:

```bash
activate-global-python-argcomplete
```

</details>

## Development

### Setup Development Environment

```bash
# Install dependencies including dev dependencies
uv sync

# Activate the venv
source .venv/bin/activate

# Run tests
uv run pytest
```

### Project Structure

- `cac_jira/__init__.py` - Module init: the `CONFIG`/`JIRA_CLIENT` globals and
  the `main` console-script entry point (`main = make_main("cac_jira", "jira", ...)`)
- `cac_jira/commands/` - Command implementations (auto-discovered at runtime)
  - `issue/` - Issue-related commands
  - `project/` - Project-related commands
- `cac_jira/core/client.py` - Thin wrapper around the `jira` Python client

Command discovery, argument parsing, shell completion, and dispatch are all
provided by the shared runner in [`cac-core`](https://github.com/rpunt/cac-core)
(`cac_core.cli.run` / `make_main`); this project only supplies the `commands/`
tree and its Jira client.

### Adding New Commands

1. Create a new action module in the appropriate command directory.
2. Define a class that inherits from the command's base class, following the
   `{Command}{Action}` naming convention (e.g. `commands/issue/create.py` →
   `IssueCreate`).
3. Implement `define_arguments()` and `execute()` methods.

`execute()` contains the command's logic and returns an exit code (`0`/`None`
for success, non-zero for validation failures). It does not need to wrap Jira
calls in try/except: the shared `run()` template (from `cac-core`) catches
errors and maps them to a non-zero exit code, and `JiraCommand.handle_exception`
renders `JIRAError`s using their human-readable Jira message.
