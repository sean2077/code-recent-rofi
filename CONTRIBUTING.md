# Contributing to code-recent-rofi

Thank you for your interest in contributing!

## Quick Start

1. Fork and clone the repository
2. Install dependencies: `uv sync --extra dev`
3. Make your changes
4. Run checks: `poe check && poe test`
5. Submit a pull request

## Pull Request Process

1. **Create your branch** from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Commit** using conventional commit format (see below)
6. **Push** and create a pull request

## Commit Message Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/) for automatic versioning and changelog generation.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

**Description rules:**
- Use imperative mood: "add feature" not "added feature"
- Start with lowercase letter
- No period at the end
- Keep it under 72 characters

### Core Types

#### `feat` - New Feature

A commit that introduces a new capability or behavior.

**Examples:**
```bash
feat: add persistent configuration
feat(client): support lazy connection
```

#### `fix` - Fixes and Improvements

A commit that fixes, improves, or supplements existing code. This covers:
- Bug fixes and error corrections
- Improvements and refinements to existing features
- Minor enhancements that don't warrant a new feature

**Examples:**
```bash
fix: correct connection timeout handling
fix(http): handle SSL certificate errors
fix: improve state tracking accuracy
```

#### `perf` - Performance Improvements

A commit that improves performance metrics without changing the external API.

**Examples:**
```bash
perf: cache parsed state to reduce CPU usage
perf: lazy load modules to improve startup time
```

### Supporting Types

These types do not trigger a release or appear in the changelog:

- **docs**: Documentation-only changes
- **style**: Code formatting only (whitespace, semicolons, quotes)
- **refactor**: Internal code restructuring with no external behavior change
- **test**: Adding or updating tests
- **build**: Changes to build system or tooling
- **ci**: Changes to CI configuration
- **chore**: Maintenance tasks (dependency updates, config cleanup)

### Breaking Changes

Add `!` after type or include `BREAKING CHANGE:` in footer:

```bash
feat!: redesign client API
fix!: rename `connect()` parameter
```

### Version Mapping

| Type                              | Version Bump      | Changelog |
| --------------------------------- | ----------------- | --------- |
| `feat`                            | MINOR (x.**Y**.0) | Yes       |
| `fix`                             | PATCH (x.y.**Z**) | Yes       |
| `perf`                            | PATCH (x.y.**Z**) | Yes       |
| `!` or `BREAKING CHANGE`          | MAJOR (**X**.0.0) | Yes       |
| Others (`docs`, `refactor`, etc.) | No release        | No        |

## Code Style

This project uses [ruff](https://docs.astral.sh/ruff/) for formatting and linting:

- **Line length**: 120 characters
- **Formatter**: ruff format
- **Linter**: ruff check
- **Type hints**: Required for public APIs
- **Docstrings**: Google style for public functions/classes

## Development Commands

All development tasks use [poethepoet](https://github.com/nat-n/poethepoet):

```bash
poe format      # Format code and organize imports
poe lint        # Run linter
poe type-check  # Run type checker
poe test        # Run tests
poe check       # Run all checks (format, lint, type-check)
poe docs        # Start documentation server (if mkdocs enabled)
```

## Testing

- Write tests for new features
- Mark slow tests: `@pytest.mark.slow`
- Ensure all tests pass before submitting

## Need Help?

- Check [existing issues](https://github.com/sean2077/code-recent-rofi/issues)
- Open a new issue for questions or problems

## License

By contributing, you agree that your contributions will be licensed under the project's license.
