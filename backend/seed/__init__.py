"""Seed package. Phase 0: no-op placeholder. Phase 1+ adds real seeding."""
from __future__ import annotations

import typer

app = typer.Typer(add_completion=False, no_args_is_help=False)


@app.command()
def run(phase0: bool = typer.Option(False, "--phase0", help="Phase 0 placeholder mode.")) -> None:
    if phase0:
        typer.secho("[seed] Phase 0 — no seed data yet.", fg=typer.colors.CYAN)
        return
    typer.secho("[seed] Seeding not implemented until Phase 1+.", fg=typer.colors.YELLOW)


if __name__ == "__main__":
    app()