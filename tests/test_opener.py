"""Tests for VS Code launch command construction."""

from __future__ import annotations

from code_recent_rofi.opener import code_command_for_target


def test_code_command_for_local_file_uri() -> None:
    assert code_command_for_target("file:///workspace/My%20Project") == [
        "code",
        "--reuse-window",
        "/workspace/My Project",
    ]


def test_code_command_for_remote_uri() -> None:
    target = "vscode-remote://ssh-remote+devbox/workspace/app"

    assert code_command_for_target(target) == ["code", "--folder-uri", target]


def test_code_command_for_plain_target() -> None:
    assert code_command_for_target("/workspace/app", code_command="codium") == [
        "codium",
        "--reuse-window",
        "/workspace/app",
    ]


def test_code_command_for_plain_target_expands_home(monkeypatch) -> None:
    monkeypatch.setenv("HOME", "/home/dev")

    assert code_command_for_target("~/workspace/new-app") == [
        "code",
        "--reuse-window",
        "/home/dev/workspace/new-app",
    ]
