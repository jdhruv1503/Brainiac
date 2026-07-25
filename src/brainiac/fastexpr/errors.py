"""Error types raised while lexing, parsing and validating Fast Expression code."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceSpan:
    """A half-open ``[start, end)`` character range inside a source string."""

    start: int
    end: int
    line: int
    column: int

    def __str__(self) -> str:
        return f"line {self.line}, column {self.column}"


class FastExprError(Exception):
    """Base class for every Fast Expression failure."""


class LexError(FastExprError):
    def __init__(self, message: str, span: SourceSpan) -> None:
        super().__init__(f"{message} (at {span})")
        self.message = message
        self.span = span


class ParseError(FastExprError):
    def __init__(self, message: str, span: SourceSpan) -> None:
        super().__init__(f"{message} (at {span})")
        self.message = message
        self.span = span


class EvaluationError(FastExprError):
    """Raised when a syntactically valid expression cannot be evaluated."""
