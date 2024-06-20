# Jira module for DC Commander

Interact with Jira stories. For a list of commands, run `cac jira`.

Please note that a local install of `libsodium` is required.

## Configuration

Update the content of `~/.config/cac/cac.yaml` as follows.

```yaml
cac:
  jira:
    OPTIONS
```

### Available options

| Option | Default | Example |
| --- | --- | --- |
| `site` | `https://MYSITE.atlassian.net` | |
| `context_path` | `/` | |
| `project` | `INVALID_DEFAULT` | Set this to your preferred Jira project |
| `username` | `INVALID_DEFAULT` | Set this to your Jira username |

## Local development

Clone [cac-core](https://github.com/rpunt/cac-core) locally, then configure bundler to use your local copy:

```bash
bundle config set --local.cac-core ~/path/to/cac-core
bundle config set --local with 'development'
bundle install
bundle exec cac jira
```
