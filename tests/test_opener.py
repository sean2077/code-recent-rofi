"""Tests for VS Code launch command construction."""

from __future__ import annotations

import json
from pathlib import Path

from code_recent_rofi.opener import candidate_window_state_files, code_command_for_target


def write_window_state(
    tmp_path: Path,
    windows: list[dict[str, object]],
    *,
    last_active_window: dict[str, object] | None = None,
) -> Path:
    state_file = tmp_path / "storage.json"
    windows_state: dict[str, object] = {"openedWindows": windows}
    if last_active_window is not None:
        windows_state["lastActiveWindow"] = last_active_window
    state_file.write_text(json.dumps({"windowsState": windows_state}), encoding="utf-8")
    return state_file


def test_code_command_for_local_file_uri() -> None:
    assert code_command_for_target("file:///workspace/My%20Project", window_state_files=[]) == [
        "code",
        "--new-window",
        "--",
        "/workspace/My Project",
    ]


def test_code_command_for_remote_uri() -> None:
    target = "vscode-remote://ssh-remote+devbox/workspace/app"

    assert code_command_for_target(target, window_state_files=[]) == ["code", "--new-window", "--folder-uri", target]


def test_code_command_for_plain_target() -> None:
    assert code_command_for_target("/workspace/app", code_command="codium", window_state_files=[]) == [
        "codium",
        "--new-window",
        "--",
        "/workspace/app",
    ]


def test_code_command_for_plain_target_expands_home(monkeypatch) -> None:
    monkeypatch.setenv("HOME", "/home/dev")

    assert code_command_for_target("~/workspace/new-app", window_state_files=[]) == [
        "code",
        "--new-window",
        "--",
        "/home/dev/workspace/new-app",
    ]


def test_code_command_for_open_plain_target_focuses_existing_window(tmp_path: Path) -> None:
    state_file = write_window_state(tmp_path, [{"folder": "file:///workspace/app"}])

    assert code_command_for_target("/workspace/app", window_state_files=[state_file]) == [
        "code",
        "--",
        "/workspace/app",
    ]


def test_code_command_for_last_active_target_focuses_existing_window(tmp_path: Path) -> None:
    state_file = write_window_state(tmp_path, [], last_active_window={"folder": "file:///workspace/app"})

    assert code_command_for_target("/workspace/app", window_state_files=[state_file]) == [
        "code",
        "--",
        "/workspace/app",
    ]


def test_code_command_for_open_workspace_file_focuses_existing_window(tmp_path: Path) -> None:
    state_file = write_window_state(
        tmp_path,
        [{"workspaceIdentifier": {"configURIPath": "file:///workspace/app.code-workspace"}}],
    )

    assert code_command_for_target("file:///workspace/app.code-workspace", window_state_files=[state_file]) == [
        "code",
        "--",
        "/workspace/app.code-workspace",
    ]


def test_code_command_for_open_remote_uri_focuses_existing_window(tmp_path: Path) -> None:
    target = "vscode-remote://ssh-remote+devbox/workspace/app"
    state_file = write_window_state(tmp_path, [{"folder": target}])

    assert code_command_for_target(target, window_state_files=[state_file]) == ["code", "--folder-uri", target]


def test_code_command_for_plain_target_uses_separator_for_dash_path() -> None:
    assert code_command_for_target("-n", window_state_files=[]) == [
        "code",
        "--new-window",
        "--",
        "-n",
    ]


def test_candidate_window_state_files_follow_code_command(tmp_path: Path) -> None:
    assert list(candidate_window_state_files(home=tmp_path, env={}, code_command="codium")) == [
        tmp_path / ".config/VSCodium/User/globalStorage/storage.json",
    ]
    assert list(candidate_window_state_files(home=tmp_path, env={}, code_command="/usr/bin/code-insiders")) == [
        tmp_path / ".config/Code - Insiders/User/globalStorage/storage.json",
    ]
