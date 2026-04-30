"""Tests for application orchestration."""

from __future__ import annotations

from code_recent_rofi import app as recent_app
from code_recent_rofi.models import RecentItem
from code_recent_rofi.vscode_recent import file_uri_to_path


def test_run_returns_no_data_when_recent_list_is_empty(monkeypatch) -> None:
    notified = False

    def fake_read_recent_entries(databases):
        return None, []

    def fake_choose_item(items, *, prompt, rofi_command):
        assert items == []

    def fake_notify_no_recent() -> None:
        nonlocal notified
        notified = True

    monkeypatch.setattr(recent_app, "read_recent_entries", fake_read_recent_entries)
    monkeypatch.setattr(recent_app, "choose_item", fake_choose_item)
    monkeypatch.setattr(recent_app, "notify_no_recent", fake_notify_no_recent)

    assert recent_app.run() == 1
    assert notified is True


def test_run_opens_custom_target_when_recent_list_is_empty(monkeypatch) -> None:
    opened: list[str] = []
    custom_item = RecentItem(label="New App", target="~/workspace/new-app", detail="~/workspace/new-app")

    def fake_read_recent_entries(databases):
        return None, []

    def fake_choose_item(items, *, prompt, rofi_command):
        assert items == []
        return custom_item

    def fake_open_target(target, *, code_command):
        opened.append(f"{code_command}:{target}")

    monkeypatch.setattr(recent_app, "read_recent_entries", fake_read_recent_entries)
    monkeypatch.setattr(recent_app, "choose_item", fake_choose_item)
    monkeypatch.setattr(recent_app, "open_target", fake_open_target)

    assert recent_app.run(code_command="codium") == 0
    assert opened == ["codium:~/workspace/new-app"]


def test_run_opens_selected_target(monkeypatch) -> None:
    opened: list[str] = []
    target = "file:///workspace/app"
    item = RecentItem(label="App", target=target, detail=file_uri_to_path(target))

    def fake_read_recent_entries(databases):
        return None, [{"folderUri": target, "label": "App"}]

    def fake_choose_item(items, *, prompt, rofi_command):
        assert items == [item]
        assert prompt == "Code"
        assert rofi_command == "fake-rofi"
        return item

    def fake_open_target(target, *, code_command):
        opened.append(f"{code_command}:{target}")

    monkeypatch.setattr(recent_app, "read_recent_entries", fake_read_recent_entries)
    monkeypatch.setattr(recent_app, "choose_item", fake_choose_item)
    monkeypatch.setattr(recent_app, "open_target", fake_open_target)

    assert recent_app.run(prompt="Code", rofi_command="fake-rofi", code_command="codium") == 0
    assert opened == [f"codium:{target}"]


def test_run_exits_cleanly_when_rofi_is_cancelled(monkeypatch) -> None:
    def fake_read_recent_entries(databases):
        return None, [{"folderUri": "file:///workspace/app", "label": "App"}]

    def fake_choose_item(items, *, prompt, rofi_command):
        assert items
        assert prompt == "VS Code"
        assert rofi_command == "rofi"

    monkeypatch.setattr(recent_app, "read_recent_entries", fake_read_recent_entries)
    monkeypatch.setattr(recent_app, "choose_item", fake_choose_item)

    assert recent_app.run() == 0
