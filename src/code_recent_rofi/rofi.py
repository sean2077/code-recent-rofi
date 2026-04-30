"""rofi menu integration."""

from __future__ import annotations

import subprocess  # noqa: S404
from collections.abc import Sequence

from .models import RecentItem

DEFAULT_PROMPT = "VS Code"


def menu_input(items: Sequence[RecentItem]) -> str:
    """Build stdin text for `rofi -dmenu`."""
    return "\n".join(item.menu_text for item in items)


def selected_item(items: Sequence[RecentItem], selected_text: str) -> RecentItem | None:
    """Resolve rofi stdout to a recent item or a custom open-or-focus target."""
    selected = selected_text.strip()
    if not selected:
        return None

    for item in items:
        if item.menu_text == selected:
            return item

    return RecentItem(label=selected, target=selected, detail=selected)


def choose_item(
    items: Sequence[RecentItem],
    *,
    prompt: str = DEFAULT_PROMPT,
    rofi_command: str = "rofi",
) -> RecentItem | None:
    """Show a rofi dmenu and return the selected item, if any."""
    rofi = subprocess.run(  # noqa: S603
        [rofi_command, "-dmenu", "-i", "-p", prompt],
        input=menu_input(items),
        text=True,
        stdout=subprocess.PIPE,
        check=False,
    )
    return selected_item(items, rofi.stdout)
