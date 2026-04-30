"""Tests for CLI module."""

from __future__ import annotations

from pathlib import Path

import pytest

from code_recent_rofi import cli


def test_version(capsys) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--version"])

    assert exit_info.value.code == 0
    assert "code-recent-rofi" in capsys.readouterr().out


def test_cli_delegates_to_app_run(monkeypatch) -> None:
    calls: list[tuple[Path | None, str, str, str]] = []

    def fake_run(*, database, prompt, rofi_command, code_command):
        calls.append((database, prompt, rofi_command, code_command))
        return 0

    monkeypatch.setattr(cli, "run", fake_run)

    with pytest.raises(SystemExit) as exit_info:
        cli.main([
            "--database",
            "/workspace/state.vscdb",
            "--prompt",
            "Code",
            "--rofi-command",
            "fake-rofi",
            "--code-command",
            "codium",
        ])

    assert exit_info.value.code == 0
    assert calls == [(Path("/workspace/state.vscdb"), "Code", "fake-rofi", "codium")]
