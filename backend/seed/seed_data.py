"""Entry point for `python -m seed.seed_data`.

Phase 0: prints a friendly message. Real seeding arrives in Phase 1+.
"""
from __future__ import annotations

import typer

from seed import app


if __name__ == "__main__":
    app()