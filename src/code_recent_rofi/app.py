"""Application orchestration for code-recent-rofi."""

from __future__ import annotations

import subprocess  # noqa: S404
from pathlib import Path

from .opener import open_target
from .rofi import DEFAULT_PROMPT, choose_item
from .vscode_recent import read_recent_entries, recent_items_from_entries

NO_RECENT_MESSAGE = "No VS Code recent project data found."


def notify_no_recent(*, notify_command: str = "notify-send") -> None:
    """Show a best-effort desktop notification for an empty recent list."""
    try:
        subprocess.run(  # noqa: S603
            [notify_command, "VS Code Recent", NO_RECENT_MESSAGE],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return


def run(
    *,
    database: Path | None = None,
    prompt: str = DEFAULT_PROMPT,
    rofi_command: str = "rofi",
    code_command: str = "code",
) -> int:
    """Run the read -> rofi -> open workflow."""
    databases = [database] if database else None
    _, entries = read_recent_entries(databases)
    items = recent_items_from_entries(entries)

    selected = choose_item(items, prompt=prompt, rofi_command=rofi_command)
    if selected is None:
        if not items:
            notify_no_recent()
            return 1
        return 0

    open_target(selected.target, code_command=code_command)
    return 0
