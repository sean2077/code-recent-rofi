"""Read and normalize VS Code recently opened entries."""

from __future__ import annotations

import json
import os
import sqlite3
import urllib.parse
import urllib.request
from collections.abc import Iterable, Iterator, Mapping
from contextlib import closing
from pathlib import Path
from typing import Any

from .models import RecentItem

RECENT_KEY = "history.recentlyOpenedPathsList"
DEFAULT_PRODUCT_FILES = (
    Path("/usr/share/code/resources/app/product.json"),
    Path("/snap/code/current/usr/share/code/resources/app/product.json"),
)
DEFAULT_SCAN_BASES = (
    Path(".config/Code"),
    Path(".config"),
    Path(".vscode"),
)


def uri_obj_to_string(value: Any) -> str | None:
    """Convert VS Code's URI JSON shapes into a string URI."""
    if not value:
        return None

    if isinstance(value, str):
        return value

    if not isinstance(value, Mapping):
        return None

    external = value.get("external")
    if isinstance(external, str) and external:
        return external

    scheme = value.get("scheme")
    if not isinstance(scheme, str) or not scheme:
        return None

    raw_path = value.get("path") or value.get("fsPath") or ""
    path = raw_path if isinstance(raw_path, str) else ""
    authority_value = value.get("authority")
    authority = authority_value if isinstance(authority_value, str) else ""
    quoted_path = urllib.parse.quote(path)

    if scheme == "file":
        return f"file://{quoted_path}"

    if authority:
        return f"{scheme}://{authority}{quoted_path}"

    return f"{scheme}:{quoted_path}"


def target_from_entry(entry: Mapping[str, Any]) -> str | None:
    """Extract the openable target URI from one VS Code recent entry."""
    folder_uri = entry.get("folderUri")
    if folder_uri is not None:
        return uri_obj_to_string(folder_uri)

    file_uri = entry.get("fileUri")
    if file_uri is not None:
        return uri_obj_to_string(file_uri)

    workspace = entry.get("workspace")
    if isinstance(workspace, Mapping):
        return uri_obj_to_string(workspace.get("configPath"))

    return None


def file_uri_to_path(target: str) -> str:
    """Decode a file URI to a local filesystem path."""
    return urllib.request.url2pathname(urllib.parse.urlparse(target).path)


def display_label(entry: Mapping[str, Any], target: str) -> str:
    """Return the user-facing label for a recent entry."""
    label = entry.get("label")
    if isinstance(label, str) and label:
        return label

    if target.startswith("file://"):
        path = file_uri_to_path(target)
        return Path(path).name or path

    return target


def display_detail(target: str) -> str:
    """Return the detail text shown next to the label in rofi."""
    if target.startswith("file://"):
        return file_uri_to_path(target)
    return target


def recent_items_from_entries(entries: Iterable[Mapping[str, Any]]) -> list[RecentItem]:
    """Normalize VS Code recent entries into deduplicated rofi items."""
    items: list[RecentItem] = []
    seen_targets: set[str] = set()

    for entry in entries:
        target = target_from_entry(entry)
        if not target or target in seen_targets:
            continue

        seen_targets.add(target)
        items.append(
            RecentItem(
                label=display_label(entry, target),
                target=target,
                detail=display_detail(target),
            )
        )

    return items


def candidate_databases(
    *,
    home: Path | None = None,
    env: Mapping[str, str] | None = None,
    product_files: Iterable[Path] = DEFAULT_PRODUCT_FILES,
    scan_bases: Iterable[Path] = DEFAULT_SCAN_BASES,
) -> Iterator[Path]:
    """Yield plausible VS Code `state.vscdb` locations in priority order."""
    home_path = home or Path.home()
    environment = env or os.environ

    env_db = environment.get("VSCODE_RECENT_DB")
    if env_db:
        yield Path(env_db).expanduser()

    for product_file in product_files:
        try:
            product = json.loads(product_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(product, Mapping):
            continue

        for key in ("sharedDataFolderName", "dataFolderName"):
            folder_name = product.get(key)
            if not isinstance(folder_name, str) or not folder_name:
                continue

            yield home_path / folder_name / "sharedStorage" / "state.vscdb"
            yield home_path / ".config" / folder_name / "sharedStorage" / "state.vscdb"

    yield home_path / ".config/Code/User/globalStorage/state.vscdb"
    yield home_path / ".config/Code/sharedStorage/state.vscdb"
    yield home_path / ".vscode/sharedStorage/state.vscdb"

    for base in scan_bases:
        scan_root = home_path / base
        if scan_root.exists():
            yield from scan_root.glob("**/sharedStorage/state.vscdb")


def read_recent_entries(databases: Iterable[Path] | None = None) -> tuple[Path | None, list[Mapping[str, Any]]]:
    """Read raw recent entries from the first usable VS Code state database."""
    seen_databases: set[Path] = set()
    database_candidates = databases or candidate_databases()

    for database in database_candidates:
        db_path = database.expanduser()
        if db_path in seen_databases:
            continue
        seen_databases.add(db_path)

        if not db_path.exists():
            continue

        try:
            with closing(sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)) as connection:
                row = connection.execute(
                    "SELECT value FROM ItemTable WHERE key = ?",
                    (RECENT_KEY,),
                ).fetchone()
        except (OSError, sqlite3.Error):
            continue

        if not row:
            continue

        try:
            data = json.loads(row[0])
        except (TypeError, json.JSONDecodeError):
            continue

        if not isinstance(data, Mapping):
            continue

        entries = data.get("entries")
        if not isinstance(entries, list) or not entries:
            continue

        normalized_entries = [entry for entry in entries if isinstance(entry, Mapping)]
        if normalized_entries:
            return db_path, normalized_entries

    return None, []
