"""Render Fast Expression ASTs back to source code."""

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
)
from brainiac.fastexpr.parser import BINARY_PRECEDENCE, RIGHT_ASSOCIATIVE, UNARY_PRECEDENCE

_TERNARY_PRECEDENCE = 0


def format_number(value: float, raw: str = "") -> str:
    """Render a numeric literal, preserving the author's spelling when it round-trips."""
    if raw:
        try:
            if float(raw) == value:
                return raw
        except ValueError:
            pass
    if float(value).is_integer() and abs(value) < 1e16:
        return str(int(value))
    return repr(value)


def _precedence(node: Expr) -> int:
    match node:
        case BinaryOp(op=op):
            return BINARY_PRECEDENCE[op]
        case UnaryOp():
            return UNARY_PRECEDENCE
        case Ternary():
            return _TERNARY_PRECEDENCE
        case _:
            return 100


def unparse(node: Node) -> str:
    """Render ``node`` as compact, re-parseable Fast Expression source."""
    match node:
        case Program(statements=statements, output=output):
            if not statements:
                return unparse(output)
            lines = [f"{stmt.target} = {unparse(stmt.value)};" for stmt in statements]
            # A trailing assignment already defines the output; don't repeat it.
            if isinstance(output, Identifier) and statements[-1].target == output.name:
                return "\n".join(lines)
            lines.append(unparse(output))
            return "\n".join(lines)
        case Assignment(target=target, value=value):
            return f"{target} = {unparse(value)}"
        case Keyword(name=name, value=value):
            return f"{name}={unparse(value)}"
        case NumberLiteral(value=value, raw=raw):
            return format_number(value, raw)
        case BoolLiteral(value=value):
            return "true" if value else "false"
        case StringLiteral(value=value):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        case Identifier(name=name):
            return name
        case Call(func=func, args=args, kwargs=kwargs):
            if func == "__index__" and len(args) == 2:
                return f"{unparse(args[0])}[{unparse(args[1])}]"
            rendered = [unparse(arg) for arg in args] + [unparse(kw) for kw in kwargs]
            return f"{func}({', '.join(rendered)})"
        case UnaryOp(op=op, operand=operand):
            inner = unparse(operand)
            if _precedence(operand) < UNARY_PRECEDENCE:
                inner = f"({inner})"
            return f"{op}{inner}"
        case BinaryOp(op=op, left=left, right=right):
            precedence = BINARY_PRECEDENCE[op]
            left_text = unparse(left)
            right_text = unparse(right)
            right_assoc = op in RIGHT_ASSOCIATIVE
            if _precedence(left) < precedence or (right_assoc and _precedence(left) == precedence):
                left_text = f"({left_text})"
            if _precedence(right) < precedence or (
                not right_assoc and _precedence(right) == precedence
            ):
                right_text = f"({right_text})"
            return f"{left_text} {op} {right_text}"
        case Ternary(condition=condition, if_true=if_true, if_false=if_false):
            cond = unparse(condition)
            if _precedence(condition) <= _TERNARY_PRECEDENCE:
                cond = f"({cond})"
            return f"{cond} ? {unparse(if_true)} : {unparse(if_false)}"
        case _:  # pragma: no cover - exhaustive over the AST
            raise TypeError(f"Cannot unparse node of type {type(node).__name__}")


def pretty(node: Node, indent: str = "    ", width: int = 88) -> str:
    """Render ``node`` with line breaks so deeply nested alphas stay readable."""

    def render(current: Node, level: int) -> str:
        flat = unparse(current)
        if len(flat) + len(indent) * level <= width or not isinstance(current, Call | Program):
            return flat
        pad = indent * (level + 1)
        if isinstance(current, Program):
            parts = [f"{stmt.target} = {render(stmt.value, level)};" for stmt in current.statements]
            if not (
                isinstance(current.output, Identifier)
                and current.statements
                and current.statements[-1].target == current.output.name
            ):
                parts.append(render(current.output, level))
            return "\n".join(parts)
        pieces = [render(arg, level + 1) for arg in current.args]
        pieces += [f"{kw.name}={render(kw.value, level + 1)}" for kw in current.kwargs]
        joined = (",\n" + pad).join(pieces)
        return f"{current.func}(\n{pad}{joined}\n{indent * level})"

    return render(node, 0)
