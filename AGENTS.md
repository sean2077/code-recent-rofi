# Agent Guidelines

## Environment

- Use `uv run <cmd>` or activate `.venv` before running commands
- Prefix shell commands with a space to prevent truncation

## Code Quality

All code changes must pass the configured quality checks:

- **Linting & Formatting**: `poe format` and `poe lint` (ruff)
- **Type Checking**: `poe type-check` (ty)
- **Dependency Check**: `poe deptry`

Run `poe check` to execute all checks before committing.

## Conventions

- Write comments and documentation in English
- Follow [CONTRIBUTING.md](CONTRIBUTING.md) for commit message format
