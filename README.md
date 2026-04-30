# code-recent-rofi

Open VS Code recent projects, files, and workspaces from a rofi popup.

The intended desktop workflow is:

```text
keyboard shortcut -> code-recent-rofi
                  -> rofi popup
                  -> select a recent VS Code target
                  -> code opens the selection
```

## Requirements

- Linux desktop session with `rofi`
- VS Code CLI available as `code`
- Python 3.12+

The tool reads VS Code's `history.recentlyOpenedPathsList` value from `state.vscdb`
in read-only SQLite mode. It checks common VS Code locations, VS Code product
metadata, and `$VSCODE_RECENT_DB` when set.

## Install

After the package is published to PyPI, run it directly with `uvx`:

```bash
uvx code-recent-rofi
```

Or install it as a persistent user-level tool:

```bash
uv tool install code-recent-rofi
```

Before the first PyPI release, install the command from this repository checkout:

```bash
uv tool install . --force
```

If your desktop shortcut editor requires an absolute command path, resolve the
installed command from your current environment instead of hard-coding one:

```bash
command -v code-recent-rofi
```

For editable development:

```bash
uv sync
uv run code-recent-rofi
```

## Usage

Run the default workflow:

```bash
code-recent-rofi
```

Use a specific VS Code database, useful for debugging or tests:

```bash
code-recent-rofi --database ~/.config/Code/sharedStorage/state.vscdb
```

Override desktop command names:

```bash
code-recent-rofi --rofi-command rofi --code-command code
```

Show the installed version:

```bash
code-recent-rofi --version
```

## Behavior

- Local `file://` targets open with `code --reuse-window <path>`.
- `vscode-remote://` and `vscode://` targets open with `code --folder-uri <uri>`.
- Duplicate recent targets are hidden while preserving VS Code's recency order.
- Cancelling rofi exits without opening anything.
- If no recent data is found, the tool sends a best-effort desktop notification.

## Development

Install dependencies:

```bash
uv sync
```

Run the full quality gate:

```bash
uv run poe check
```

Individual commands:

```bash
uv run poe format
uv run poe lint
uv run poe type-check
uv run poe test
uv run poe deptry
```

Build and validate the PyPI distributions:

```bash
uv run poe build
uv run poe dist-check
```

## Publishing

PyPI publishing is wired through `.github/workflows/release.yml` using Trusted
Publishing, so no long-lived PyPI token is needed in GitHub Actions.

For the first upload, create a pending publisher in PyPI with:

- PyPI project name: `code-recent-rofi`
- Owner: `sean2077`
- Repository name: `code-recent-rofi`
- Workflow filename: `release.yml`
- Environment name: `pypi`

Publishing follows the same shape as `jsonpath-python`: push conventional commits
to `main`, wait for CI to pass, and the release workflow runs from the successful
CI run. `semantic-release` updates the version first, builds the distributions
from that updated version, creates the GitHub release, and only then publishes
the built artifacts to PyPI.

If a Git tag already exists for a version that was not uploaded to PyPI, publish
the next release version instead of trying to reuse the existing tag.

Manual local publishing remains possible when you have a PyPI token:

```bash
uv run poe build
uv run poe dist-check
UV_PUBLISH_TOKEN=... uv publish
```

## License

MIT
