"""Shared value objects for code-recent-rofi."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RecentItem:
    """A VS Code recent entry ready to be displayed and opened."""

    label: str
    target: str
    detail: str

    @property
    def menu_text(self) -> str:
        """Return the exact text shown in rofi."""
        return f"{self.label}    {self.detail}"
