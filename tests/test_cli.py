"""Tests for CLI module."""

from __future__ import annotations

from typer.testing import CliRunner

from code_recent_rofi.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert "code-recent-rofi" in result.stdout


def test_cli_delegates_to_app_run(monkeypatch) -> None:
    calls: list[tuple[str, str, str]] = []

    def fake_run(*, database, prompt, rofi_command, code_command):
        assert database is None
        calls.append((prompt, rofi_command, code_command))
        return 0

    monkeypatch.setattr("code_recent_rofi.cli.run", fake_run)

    result = runner.invoke(app, ["--prompt", "Code", "--rofi-command", "fake-rofi", "--code-command", "codium"])

    assert result.exit_code == 0
    assert calls == [("Code", "fake-rofi", "codium")]
