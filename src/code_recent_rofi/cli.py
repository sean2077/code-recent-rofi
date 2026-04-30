"""Command-line interface for code-recent-rofi."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from . import __version__
from .app import run

app = typer.Typer(
    name="code-recent-rofi",
    help="Open VS Code recent projects from a rofi menu.",
    add_completion=False,
    no_args_is_help=False,
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    *,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            is_eager=True,
        ),
    ] = False,
    database: Annotated[
        Path | None,
        typer.Option(
            "--database",
            "-d",
            exists=False,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Use an explicit VS Code state.vscdb path.",
        ),
    ] = None,
    prompt: Annotated[
        str,
        typer.Option(
            "--prompt",
            "-p",
            help="rofi prompt text.",
        ),
    ] = "VS Code",
    rofi_command: Annotated[
        str,
        typer.Option(
            "--rofi-command",
            help="rofi executable name or path.",
        ),
    ] = "rofi",
    code_command: Annotated[
        str,
        typer.Option(
            "--code-command",
            help="VS Code executable name or path.",
        ),
    ] = "code",
) -> None:
    """Open VS Code recent projects from a rofi menu."""
    if version:
        typer.echo(f"code-recent-rofi {__version__}")
        raise typer.Exit

    if ctx.invoked_subcommand is not None:
        return

    exit_code = run(
        database=database,
        prompt=prompt,
        rofi_command=rofi_command,
        code_command=code_command,
    )
    raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()
