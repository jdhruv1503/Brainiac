"""Canonicalisation and structural fingerprinting of alphas.

Two alphas that differ only in variable names, argument order of commutative operators,
redundant parentheses, defaulted keyword arguments or legacy operator spellings are the
same alpha. Collapsing them to one canonical form gives us a cheap structural dedupe that
runs before any simulation, and a stable identity to key caches and databases on.
"""

from __future__ import annotations

import hashlib
from typing import Final

from brainiac.fastexpr.ast import (
    BinaryOp,
    BoolLiteral,
    Call,
    Expr,
    Identifier,
    Keyword,
    NumberLiteral,
    Program,
    StringLiteral,
    Ternary,
    UnaryOp,
)
from brainiac.fastexpr.operators import canonical_name, get_operator
from brainiac.fastexpr.parser import parse
from brainiac.fastexpr.printer import unparse

#: Function spellings that are exactly equivalent to an infix operator.
_FUNCTION_TO_OPERATOR: Final[dict[str, str]] = {
    "subtract": "-",
    "divide": "/",
    "less": "<",
    "greater": ">",
    "equal": "==",
    "and": "&&",
    "or": "||",
}
_COMMUTATIVE_OPERATORS: Final[frozenset[str]] = frozenset({"+", "*", "&&", "||", "==", "!="})
_COMMUTATIVE_CALLS: Final[frozenset[str]] = frozenset({"add", "multiply", "max", "min"})
_MAX_FOLD_MAGNITUDE: Final = 1e15


def canonicalize(node: Program | Expr) -> Program:
    """Return a semantically equivalent :class:`Program` in canonical form."""
    program = node if isinstance(node, Program) else Program(output=node)
    inlined = _inline_assignments(program)
    return Program(output=_rewrite(inlined))


def _inline_assignments(program: Program) -> Expr:
    """Substitute every assignment into the output expression."""
    bindings: dict[str, Expr] = {}
    for statement in program.statements:
        value = _substitute(statement.value, bindings)
        # A self-referential binding cannot be inlined; drop it and keep the identifier.
        if statement.target in _identifiers(value):
            bindings.pop(statement.target, None)
            continue
        bindings[statement.target] = value
    return _substitute(program.output, bindings)


def _identifiers(node: Expr) -> set[str]:
    found: set[str] = set()

    def visit(current: Expr) -> None:
        match current:
            case Identifier(name=name):
                found.add(name)
            case Call(args=args, kwargs=kwargs):
                for arg in args:
                    visit(arg)
                for keyword in kwargs:
                    visit(keyword.value)
            case UnaryOp(operand=operand):
                visit(operand)
            case BinaryOp(left=left, right=right):
                visit(left)
                visit(right)
            case Ternary(condition=condition, if_true=if_true, if_false=if_false):
                visit(condition)
                visit(if_true)
                visit(if_false)
            case _:
                return

    visit(node)
    return found


def _substitute(node: Expr, bindings: dict[str, Expr]) -> Expr:
    if not bindings:
        return node
    match node:
        case Identifier(name=name):
            return bindings.get(name, node)
        case Call(func=func, args=args, kwargs=kwargs):
            return Call(
                func=func,
                args=tuple(_substitute(arg, bindings) for arg in args),
                kwargs=tuple(
                    Keyword(name=kw.name, value=_substitute(kw.value, bindings)) for kw in kwargs
                ),
            )
        case UnaryOp(op=op, operand=operand):
            return UnaryOp(op=op, operand=_substitute(operand, bindings))
        case BinaryOp(op=op, left=left, right=right):
            return BinaryOp(
                op=op, left=_substitute(left, bindings), right=_substitute(right, bindings)
            )
        case Ternary(condition=condition, if_true=if_true, if_false=if_false):
            return Ternary(
                condition=_substitute(condition, bindings),
                if_true=_substitute(if_true, bindings),
                if_false=_substitute(if_false, bindings),
            )
        case _:
            return node


def _rewrite(node: Expr) -> Expr:
    match node:
        case Call(func=func, args=args, kwargs=kwargs):
            return _rewrite_call(func, args, kwargs)
        case UnaryOp(op=op, operand=operand):
            inner = _rewrite(operand)
            if op == "-":
                if isinstance(inner, NumberLiteral):
                    return NumberLiteral(-inner.value)
                if isinstance(inner, UnaryOp) and inner.op == "-":
                    return inner.operand
            if op == "!" and isinstance(inner, UnaryOp) and inner.op == "!":
                return inner.operand
            return UnaryOp(op=op, operand=inner)
        case BinaryOp(op=op, left=left, right=right):
            return _rewrite_binary(op, _rewrite(left), _rewrite(right))
        case Ternary(condition=condition, if_true=if_true, if_false=if_false):
            return Call(
                func="if_else",
                args=(_rewrite(condition), _rewrite(if_true), _rewrite(if_false)),
            )
        case NumberLiteral(value=value):
            return NumberLiteral(value)
        case _:
            return node


def _rewrite_call(func: str, args: tuple[Expr, ...], kwargs: tuple[Keyword, ...]) -> Expr:
    name = canonical_name(func)
    new_args = tuple(_rewrite(arg) for arg in args)

    if name in _FUNCTION_TO_OPERATOR and len(new_args) == 2 and not kwargs:
        return _rewrite_binary(_FUNCTION_TO_OPERATOR[name], new_args[0], new_args[1])
    if name == "not" and len(new_args) == 1 and not kwargs:
        return _rewrite(UnaryOp(op="!", operand=new_args[0]))
    if name == "reverse" and len(new_args) == 1 and not kwargs:
        return _rewrite(UnaryOp(op="-", operand=new_args[0]))
    if name in {"add", "multiply"} and len(new_args) == 2 and _keywords_are_defaults(name, kwargs):
        return _rewrite_binary("+" if name == "add" else "*", new_args[0], new_args[1])

    new_kwargs = _canonical_keywords(name, kwargs)
    if name in _COMMUTATIVE_CALLS and not new_kwargs:
        new_args = tuple(sorted(new_args, key=unparse))
    return Call(func=name, args=new_args, kwargs=new_kwargs)


def _keywords_are_defaults(func: str, kwargs: tuple[Keyword, ...]) -> bool:
    return not _canonical_keywords(func, kwargs)


def _canonical_keywords(func: str, kwargs: tuple[Keyword, ...]) -> tuple[Keyword, ...]:
    """Drop keyword arguments that restate the operator default, then sort by name."""
    spec = get_operator(func)
    kept: list[Keyword] = []
    for keyword in kwargs:
        value = _rewrite(keyword.value)
        parameter = spec.kwargs.get(keyword.name) if spec else None
        if parameter is not None and parameter.default is not None:
            literal = _literal_value(value)
            if literal is not None and _defaults_equal(literal, parameter.default):
                continue
        kept.append(Keyword(name=keyword.name, value=value))
    return tuple(sorted(kept, key=lambda kw: kw.name))


def _literal_value(node: Expr) -> object | None:
    match node:
        case NumberLiteral(value=value):
            return value
        case BoolLiteral(value=value):
            return value
        case StringLiteral(value=value):
            return value
        case _:
            return None


def _defaults_equal(literal: object, default: object) -> bool:
    if isinstance(literal, bool) or isinstance(default, bool):
        return bool(literal) is bool(default)
    if isinstance(literal, int | float) and isinstance(default, int | float):
        return float(literal) == float(default)
    return str(literal) == str(default)


def _rewrite_binary(op: str, left: Expr, right: Expr) -> Expr:
    folded = _fold_constants(op, left, right)
    if folded is not None:
        return folded

    # ``a - -b`` -> ``a + b`` and ``a + -b`` -> ``a - b`` keep sign handling in one place.
    if op == "-" and isinstance(right, UnaryOp) and right.op == "-":
        return _rewrite_binary("+", left, right.operand)
    if op == "+" and isinstance(right, UnaryOp) and right.op == "-":
        return _rewrite_binary("-", left, right.operand)

    if op in _COMMUTATIVE_OPERATORS:
        left, right = sorted((left, right), key=unparse)
    return BinaryOp(op=op, left=left, right=right)


def _fold_constants(op: str, left: Expr, right: Expr) -> Expr | None:
    if not (isinstance(left, NumberLiteral) and isinstance(right, NumberLiteral)):
        return None
    a, b = left.value, right.value
    try:
        match op:
            case "+":
                value = a + b
            case "-":
                value = a - b
            case "*":
                value = a * b
            case "/":
                if b == 0:
                    return None
                value = a / b
            case "^":
                value = a**b
            case _:
                return None
    except (OverflowError, ValueError, ZeroDivisionError):
        return None
    if abs(value) > _MAX_FOLD_MAGNITUDE:
        return None
    return NumberLiteral(float(value))


def canonical_source(source: str | Program | Expr) -> str:
    """Canonical single-line source form of an alpha."""
    program = parse(source) if isinstance(source, str) else source
    return unparse(canonicalize(program))


def structural_hash(source: str | Program | Expr) -> str:
    """Stable 64-hex-character fingerprint of an alpha's canonical structure."""
    return hashlib.sha256(canonical_source(source).encode("utf-8")).hexdigest()


def shape_hash(source: str | Program | Expr) -> str:
    """Fingerprint that also ignores numeric constants.

    Useful for detecting families of alphas that differ only in tuned lookback windows,
    which almost always end up highly correlated with one another.
    """
    program = parse(source) if isinstance(source, str) else source
    canonical = canonicalize(program)
    blanked = _blank_numbers(canonical.output)
    return hashlib.sha256(unparse(blanked).encode("utf-8")).hexdigest()


def _blank_numbers(node: Expr) -> Expr:
    match node:
        case NumberLiteral():
            return Identifier("?")
        case Call(func=func, args=args, kwargs=kwargs):
            return Call(
                func=func,
                args=tuple(_blank_numbers(arg) for arg in args),
                kwargs=tuple(
                    Keyword(name=kw.name, value=_blank_numbers(kw.value)) for kw in kwargs
                ),
            )
        case UnaryOp(op=op, operand=operand):
            return UnaryOp(op=op, operand=_blank_numbers(operand))
        case BinaryOp(op=op, left=left, right=right):
            return BinaryOp(op=op, left=_blank_numbers(left), right=_blank_numbers(right))
        case Ternary(condition=condition, if_true=if_true, if_false=if_false):
            return Ternary(
                condition=_blank_numbers(condition),
                if_true=_blank_numbers(if_true),
                if_false=_blank_numbers(if_false),
            )
        case _:
            return node


def used_fields(source: str | Program | Expr, *, known_operators: bool = True) -> frozenset[str]:
    """Identifiers referenced by an alpha that are not operator names or local variables."""
    program = parse(source) if isinstance(source, str) else source
    if isinstance(program, Program):
        locals_ = {statement.target for statement in program.statements}
        expression = program.output
        nodes = [statement.value for statement in program.statements] + [expression]
    else:
        locals_ = set()
        nodes = [program]
    names: set[str] = set()
    for node in nodes:
        names |= _identifiers(node)
    names -= locals_
    if known_operators:
        names -= {"?"}
    return frozenset(names)


def statement_of(source: str) -> Program:
    """Parse and canonicalise in one step; convenient in tests and the CLI."""
    return canonicalize(parse(source))


def _assignment_targets(program: Program) -> tuple[str, ...]:
    return tuple(statement.target for statement in program.statements)


__all__ = [
    "canonical_source",
    "canonicalize",
    "shape_hash",
    "structural_hash",
    "used_fields",
]
