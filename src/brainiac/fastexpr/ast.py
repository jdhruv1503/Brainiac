"""Abstract syntax tree for WorldQuant Fast Expression.

Nodes are frozen dataclasses so they can be hashed, cached and safely shared between the
validator, the local evaluator and the genetic search.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field, replace
from typing import TypeAlias

__all__ = [
    "Assignment",
    "BinaryOp",
    "BoolLiteral",
    "Call",
    "Expr",
    "Identifier",
    "Keyword",
    "Node",
    "NumberLiteral",
    "Program",
    "StringLiteral",
    "Ternary",
    "UnaryOp",
    "children",
    "replace_at",
    "walk",
]


@dataclass(frozen=True)
class Node:
    """Base class for all AST nodes."""


@dataclass(frozen=True)
class NumberLiteral(Node):
    value: float
    raw: str = ""

    @property
    def is_integral(self) -> bool:
        return float(self.value).is_integer()


@dataclass(frozen=True)
class BoolLiteral(Node):
    value: bool


@dataclass(frozen=True)
class StringLiteral(Node):
    value: str


@dataclass(frozen=True)
class Identifier(Node):
    name: str


@dataclass(frozen=True)
class Keyword(Node):
    """A named argument such as ``dense=true`` inside a call."""

    name: str
    value: Expr


@dataclass(frozen=True)
class Call(Node):
    func: str
    args: tuple[Expr, ...] = ()
    kwargs: tuple[Keyword, ...] = ()


@dataclass(frozen=True)
class UnaryOp(Node):
    op: str
    operand: Expr


@dataclass(frozen=True)
class BinaryOp(Node):
    op: str
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Ternary(Node):
    condition: Expr
    if_true: Expr
    if_false: Expr


@dataclass(frozen=True)
class Assignment(Node):
    target: str
    value: Expr


Expr: TypeAlias = (
    NumberLiteral | BoolLiteral | StringLiteral | Identifier | Call | UnaryOp | BinaryOp | Ternary
)


@dataclass(frozen=True)
class Program(Node):
    """A full alpha: zero or more assignments followed by the output expression."""

    statements: tuple[Assignment, ...] = ()
    output: Expr = field(default_factory=lambda: NumberLiteral(0.0, "0"))


def children(node: Node) -> tuple[Node, ...]:
    """Return the direct child nodes of ``node``."""
    match node:
        case Program(statements=statements, output=output):
            return (*statements, output)
        case Assignment(value=value):
            return (value,)
        case Keyword(value=value):
            return (value,)
        case Call(args=args, kwargs=kwargs):
            return (*args, *kwargs)
        case UnaryOp(operand=operand):
            return (operand,)
        case BinaryOp(left=left, right=right):
            return (left, right)
        case Ternary(condition=condition, if_true=if_true, if_false=if_false):
            return (condition, if_true, if_false)
        case _:
            return ()


def walk(node: Node) -> Iterator[Node]:
    """Yield ``node`` and every descendant in pre-order."""
    yield node
    for child in children(node):
        yield from walk(child)


def size(node: Node) -> int:
    """Number of nodes in the subtree rooted at ``node``."""
    return sum(1 for _ in walk(node))


def depth(node: Node) -> int:
    """Longest root-to-leaf path length of the subtree rooted at ``node``."""
    kids = children(node)
    return 1 + max((depth(child) for child in kids), default=0)


def _with_children(node: Node, new_children: Sequence[Node]) -> Node:
    """Rebuild ``node`` with ``new_children`` in the same order :func:`children` returns."""
    match node:
        case Program(statements=statements):
            count = len(statements)
            stmts = tuple(child for child in new_children[:count] if isinstance(child, Assignment))
            output = new_children[count]
            assert not isinstance(output, Program | Assignment | Keyword)
            return Program(statements=stmts, output=output)
        case Assignment(target=target):
            value = new_children[0]
            assert not isinstance(value, Program | Assignment | Keyword)
            return Assignment(target=target, value=value)
        case Keyword(name=name):
            value = new_children[0]
            assert not isinstance(value, Program | Assignment | Keyword)
            return Keyword(name=name, value=value)
        case Call(func=func, args=args):
            count = len(args)
            new_args = tuple(child for child in new_children[:count] if _is_expr(child))
            new_kwargs = tuple(k for k in new_children[count:] if isinstance(k, Keyword))
            return Call(func=func, args=new_args, kwargs=new_kwargs)
        case UnaryOp(op=op):
            operand = new_children[0]
            assert _is_expr(operand)
            return UnaryOp(op=op, operand=operand)
        case BinaryOp(op=op):
            left, right = new_children
            assert _is_expr(left) and _is_expr(right)
            return BinaryOp(op=op, left=left, right=right)
        case Ternary():
            condition, if_true, if_false = new_children
            assert _is_expr(condition) and _is_expr(if_true) and _is_expr(if_false)
            return Ternary(condition=condition, if_true=if_true, if_false=if_false)
        case _:
            return replace(node)  # type: ignore[type-var]


def _is_expr(node: Node) -> bool:
    return not isinstance(node, Program | Assignment | Keyword)


def enumerate_positions(root: Node) -> list[tuple[int, ...]]:
    """List every node position in ``root`` as a tuple of child indices from the root."""
    positions: list[tuple[int, ...]] = []

    def visit(node: Node, path: tuple[int, ...]) -> None:
        positions.append(path)
        for index, child in enumerate(children(node)):
            visit(child, (*path, index))

    visit(root, ())
    return positions


def node_at(root: Node, path: Sequence[int]) -> Node:
    """Fetch the node reached by following child indices ``path`` from ``root``."""
    node = root
    for index in path:
        node = children(node)[index]
    return node


def replace_at(root: Node, path: Sequence[int], new_node: Node) -> Node:
    """Return a copy of ``root`` with the node at ``path`` replaced by ``new_node``."""
    if not path:
        return new_node
    kids = list(children(root))
    index = path[0]
    kids[index] = replace_at(kids[index], path[1:], new_node)
    return _with_children(root, kids)
