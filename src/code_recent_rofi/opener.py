"""VS Code launch helpers."""

from __future__ import annotations

import json
import os
import subprocess  # noqa: S404
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any

from .vscode_recent import file_uri_to_path

WINDOW_STATE_ENV = "VSCODE_WINDOW_STATE"
WINDOW_STATE_FILES_BY_COMMAND = {
    "code": (Path(".config/Code/User/globalStorage/storage.json"),),
    "code-insiders": (Path(".config/Code - Insiders/User/globalStorage/storage.json"),),
    "codium": (Path(".config/VSCodium/User/globalStorage/storage.json"),),
    "vscodium": (Path(".config/VSCodium/User/globalStorage/storage.json"),),
    "code-oss": (Path(".config/Code - OSS/User/globalStorage/storage.json"),),
}
DEFAULT_WINDOW_STATE_FILES = tuple(
    state_file for state_files in WINDOW_STATE_FILES_BY_COMMAND.values() for state_file in state_files
)


def candidate_window_state_files(
    *,
    home: Path | None = None,
    env: Mapping[str, str] | None = None,
    code_command: str | None = None,
) -> Iterator[Path]:
    """Yield plausible VS Code window-state storage files."""
    home_path = home or Path.home()
    environment = env or os.environ

    env_state = environment.get(WINDOW_STATE_ENV)
    if env_state:
        yield Path(env_state).expanduser()

    command_name = Path(code_command).name if code_command else ""
    state_files = WINDOW_STATE_FILES_BY_COMMAND.get(command_name, DEFAULT_WINDOW_STATE_FILES)
    for state_file in state_files:
        yield home_path / state_file


def normalized_target_key(target: str) -> tuple[str, str]:
    """Return a comparable key for local paths and URI targets."""
    if target.startswith("file://"):
        return ("file", str(Path(file_uri_to_path(target)).expanduser().resolve()))

    if target.startswith(("vscode-remote://", "vscode://")):
        return ("uri", target)

    return ("file", str(Path(target).expanduser().resolve()))


def local_path_for_target(target: str) -> str:
    """Return the local filesystem path for a file URI or plain path target."""
    if target.startswith("file://"):
        return file_uri_to_path(target)

    return str(Path(target).expanduser())


def local_folder_uri_for_target(target: str) -> str | None:
    """Return a file URI when the target is an existing local directory."""
    path = Path(local_path_for_target(target)).expanduser()
    if not path.is_dir():
        return None

    if target.startswith("file://"):
        return target

    return path.resolve().as_uri()


def code_command_for_folder_uri(*, code_command: str, folder_uri: str, target_is_open: bool) -> list[str]:
    """Build a VS Code folder URI command for an open or missing folder."""
    if target_is_open:
        return [code_command, "--folder-uri", folder_uri]

    return [code_command, "--new-window", "--folder-uri", folder_uri]


def window_state_targets(state: Mapping[str, Any]) -> Iterator[str]:
    """Yield folder/workspace targets from VS Code's persisted window state."""
    windows_state = state.get("windowsState")
    if not isinstance(windows_state, Mapping):
        return

    windows: list[Any] = []
    last_active_window = windows_state.get("lastActiveWindow")
    if isinstance(last_active_window, Mapping):
        windows.append(last_active_window)

    opened_windows = windows_state.get("openedWindows")
    if isinstance(opened_windows, list):
        windows.extend(opened_windows)

    for window in windows:
        if not isinstance(window, Mapping):
            continue

        folder = window.get("folder")
        if isinstance(folder, str) and folder:
            yield folder

        workspace_identifier = window.get("workspaceIdentifier")
        if isinstance(workspace_identifier, Mapping):
            config_path = workspace_identifier.get("configURIPath")
            if isinstance(config_path, str) and config_path:
                yield config_path


def is_target_open(
    target: str,
    *,
    window_state_files: Iterable[Path] | None = None,
    code_command: str | None = None,
) -> bool:
    """Return whether VS Code window state already lists the selected target."""
    target_key = normalized_target_key(target)
    state_files = (
        candidate_window_state_files(code_command=code_command) if window_state_files is None else window_state_files
    )

    for state_file in state_files:
        try:
            state = json.loads(state_file.expanduser().read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(state, Mapping):
            continue

        for open_target in window_state_targets(state):
            if normalized_target_key(open_target) == target_key:
                return True

    return False


def code_command_for_target(
    target: str,
    *,
    code_command: str = "code",
    window_state_files: Iterable[Path] | None = None,
) -> list[str]:
    """Build the `code` command for a normalized recent target."""
    target_is_open = is_target_open(target, window_state_files=window_state_files, code_command=code_command)

    if target.startswith(("vscode-remote://", "vscode://")):
        return code_command_for_folder_uri(code_command=code_command, folder_uri=target, target_is_open=target_is_open)

    folder_uri = local_folder_uri_for_target(target)
    if folder_uri:
        return code_command_for_folder_uri(
            code_command=code_command,
            folder_uri=folder_uri,
            target_is_open=target_is_open,
        )

    path = local_path_for_target(target)
    return [code_command, "--", path] if target_is_open else [code_command, "--new-window", "--", path]


def open_target(target: str, *, code_command: str = "code") -> subprocess.Popen[bytes]:
    """Launch VS Code for the selected target."""
    return subprocess.Popen(code_command_for_target(target, code_command=code_command))  # noqa: S603
