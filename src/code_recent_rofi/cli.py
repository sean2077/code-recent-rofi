"""Command-line interface for code-recent-rofi."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .app import run


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="code-recent-rofi",
        description="Open VS Code recent projects from a rofi menu.",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show version and exit.",
    )
    parser.add_argument(
        "--database",
        "-d",
        type=Path,
        help="Use an explicit VS Code state.vscdb path.",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default="VS Code",
        help="rofi prompt text.",
    )
    parser.add_argument(
        "--rofi-command",
        default="rofi",
        help="rofi executable name or path.",
    )
    parser.add_argument(
        "--code-command",
        default="code",
        help="VS Code executable name or path.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Open VS Code recent projects from a rofi menu."""
    args = build_parser().parse_args(argv)

    exit_code = run(
        database=args.database,
        prompt=args.prompt,
        rofi_command=args.rofi_command,
        code_command=args.code_command,
    )
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
