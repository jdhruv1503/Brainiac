"""A complete front end for WorldQuant Fast Expression.

Lex, parse, print, canonicalise, fingerprint, validate and mutate alphas locally so that
remote simulation capacity is only ever spent on expressions that can actually run.
"""

from __future__ import annotations

from brainiac.fastexpr.ast import (
    Assignment,
    BinaryOp,
    BoolLiteral,
    Call,
    Expr,
    Identifier,
    Keyword,
    Node,
    NumberLiteral,
    Program,
    StringLiteral,
    Ternary,
    UnaryOp,
    depth,
    size,
    walk,
)
from brainiac.fastexpr.canonical import (
    canonical_source,
    canonicalize,
    shape_hash,
    structural_hash,
    used_fields,
)
from brainiac.fastexpr.errors import (
    EvaluationError,
    FastExprError,
    LexError,
    ParseError,
    SourceSpan,
)
from brainiac.fastexpr.operators import (
    Category,
    Kind,
    OperatorSpec,
    get_operator,
    iter_operators,
    operator_names,
)
from brainiac.fastexpr.parser import parse, parse_expression
from brainiac.fastexpr.printer import pretty, unparse
from brainiac.fastexpr.validate import (
    Diagnostic,
    Severity,
    ValidationReport,
    ValidationSettings,
    validate,
    validate_source,
)

__all__ = [
    "Assignment",
    "BinaryOp",
    "BoolLiteral",
    "Call",
    "Category",
    "Diagnostic",
    "EvaluationError",
    "Expr",
    "FastExprError",
    "Identifier",
    "Keyword",
    "Kind",
    "LexError",
    "Node",
    "NumberLiteral",
    "OperatorSpec",
    "ParseError",
    "Program",
    "Severity",
    "SourceSpan",
    "StringLiteral",
    "Ternary",
    "UnaryOp",
    "ValidationReport",
    "ValidationSettings",
    "canonical_source",
    "canonicalize",
    "depth",
    "get_operator",
    "iter_operators",
    "operator_names",
    "parse",
    "parse_expression",
    "pretty",
    "shape_hash",
    "size",
    "structural_hash",
    "unparse",
    "used_fields",
    "validate",
    "validate_source",
    "walk",
]
