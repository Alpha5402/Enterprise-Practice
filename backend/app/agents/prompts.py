"""Prompt loading utilities for analysis agents."""

from functools import lru_cache
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


@lru_cache
def load_prompt(name: str) -> str:
    """Load a prompt file by stem name."""
    path = PROMPT_DIR / f"{name}_prompt.md"
    return path.read_text(encoding="utf-8")

