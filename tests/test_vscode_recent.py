"""Tests for VS Code recent-entry parsing."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from code_recent_rofi.vscode_recent import (
    RECENT_KEY,
    candidate_databases,
    file_uri_to_path,
    read_recent_entries,
    recent_items_from_entries,
    target_from_entry,
    uri_obj_to_string,
)


def test_uri_obj_to_string_supports_file_uri() -> None:
    result = uri_obj_to_string({"scheme": "file", "path": "/workspace/My Project"})

    assert result == "file:///workspace/My%20Project"
    assert file_uri_to_path(result) == str(Path("/workspace/My Project"))


def test_uri_obj_to_string_supports_remote_uri() -> None:
    result = uri_obj_to_string({
        "scheme": "vscode-remote",
        "authority": "ssh-remote+devbox",
        "path": "/workspace/project",
    })

    assert result == "vscode-remote://ssh-remote+devbox/workspace/project"


def test_target_from_entry_supports_workspace_config_path() -> None:
    entry = {"workspace": {"configPath": {"scheme": "file", "path": "/workspace/app.code-workspace"}}}

    assert target_from_entry(entry) == "file:///workspace/app.code-workspace"


def test_recent_items_are_deduplicated_and_display_local_paths() -> None:
    entries = [
        {"label": "App", "folderUri": {"scheme": "file", "path": "/workspace/app"}},
        {"label": "Duplicate", "folderUri": {"scheme": "file", "path": "/workspace/app"}},
        {"folderUri": "vscode-remote://ssh-remote+devbox/workspace/api"},
    ]

    items = recent_items_from_entries(entries)

    assert [item.label for item in items] == ["App", "vscode-remote://ssh-remote+devbox/workspace/api"]
    assert [item.detail for item in items] == [
        str(Path("/workspace/app")),
        "vscode-remote://ssh-remote+devbox/workspace/api",
    ]


def test_candidate_databases_prioritizes_env_and_product_metadata(tmp_path: Path) -> None:
    product_file = tmp_path / "product.json"
    product_file.write_text(json.dumps({"sharedDataFolderName": ".vscode-test"}), encoding="utf-8")
    home = tmp_path / "home"

    candidates = list(
        candidate_databases(
            home=home,
            env={"VSCODE_RECENT_DB": str(tmp_path / "override.vscdb")},
            product_files=[product_file],
            scan_bases=[],
        )
    )

    assert candidates[:3] == [
        tmp_path / "override.vscdb",
        home / ".vscode-test/sharedStorage/state.vscdb",
        home / ".config/.vscode-test/sharedStorage/state.vscdb",
    ]


def test_read_recent_entries_reads_first_valid_database(tmp_path: Path) -> None:
    database = tmp_path / "state.vscdb"
    payload = {
        "entries": [
            {"label": "App", "folderUri": {"scheme": "file", "path": "/workspace/app"}},
        ]
    }

    with closing(sqlite3.connect(database)) as connection:
        connection.execute("CREATE TABLE ItemTable (key TEXT PRIMARY KEY, value TEXT)")
        connection.execute("INSERT INTO ItemTable VALUES (?, ?)", (RECENT_KEY, json.dumps(payload)))
        connection.commit()

    source, entries = read_recent_entries([tmp_path / "missing.vscdb", database])

    assert source == database
    assert entries == payload["entries"]
