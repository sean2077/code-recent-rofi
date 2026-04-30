"""VS Code launch helpers."""

from __future__ import annotations

import subprocess  # noqa: S404
from pathlib import Path

from .vscode_recent import file_uri_to_path


def code_command_for_target(target: str, *, code_command: str = "code") -> list[str]:
    """Build the `code` command for a normalized recent target."""
    if target.startswith("file://"):
        return [code_command, "--reuse-window", file_uri_to_path(target)]

    if target.startswith(("vscode-remote://", "vscode://")):
        return [code_command, "--folder-uri", target]

    return [code_command, "--reuse-window", str(Path(target).expanduser())]


def open_target(target: str, *, code_command: str = "code") -> subprocess.Popen[bytes]:
    """Launch VS Code for the selected target."""
    return subprocess.Popen(code_command_for_target(target, code_command=code_command))  # noqa: S603
