"""Access to the bundled BRAIN knowledge base (operator docs and dataset exports)."""

from __future__ import annotations

from pathlib import Path

__all__ = ["knowledge_path", "read_operator_reference"]


def _knowledge_root() -> Path:
    """Locate the ``knowledge`` directory both in a source checkout and in a wheel."""
    packaged = Path(__file__).parent
    if (packaged / "datasets").is_dir():
        return packaged
    repo_root = Path(__file__).resolve().parents[3]
    candidate = repo_root / "knowledge"
    if candidate.is_dir():
        return candidate
    raise FileNotFoundError(
        "Could not locate the Brainiac knowledge directory. Expected it next to the "
        f"package at {packaged} or at {candidate}."
    )


def knowledge_path(*parts: str) -> Path:
    """Return a path inside the bundled knowledge directory."""
    return _knowledge_root().joinpath(*parts)


def read_operator_reference() -> str:
    """The Fast Expression operator cheat sheet used in LLM prompts."""
    return knowledge_path("fastexpr_operators.md").read_text(encoding="utf-8", errors="replace")
