"""Tests for rofi menu behavior."""

from __future__ import annotations

from code_recent_rofi.models import RecentItem
from code_recent_rofi.rofi import menu_input, selected_item


def test_menu_input_uses_exact_menu_text() -> None:
    items = [
        RecentItem(label="App", target="file:///workspace/app", detail="/workspace/app"),
        RecentItem(label="API", target="vscode-remote://dev/api", detail="vscode-remote://dev/api"),
    ]

    assert menu_input(items) == "App    /workspace/app\nAPI    vscode-remote://dev/api"


def test_selected_item_matches_rofi_stdout() -> None:
    item = RecentItem(label="App", target="file:///workspace/app", detail="/workspace/app")

    assert selected_item([item], "App    /workspace/app\n") == item
    assert selected_item([item], "") is None


def test_selected_item_uses_custom_input_as_open_or_focus_target() -> None:
    assert selected_item([], "~/workspace/new-app\n") == RecentItem(
        label="~/workspace/new-app",
        target="~/workspace/new-app",
        detail="~/workspace/new-app",
    )
