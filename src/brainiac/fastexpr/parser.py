"""Recursive-descent / precedence-climbing parser for Fast Expression."""

from __future__ import annotations

from typing import Final

from brainiac.fastexpr.ast import (
    Assignment,
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
from brainiac.fastexpr.errors import ParseError, SourceSpan
from brainiac.fastexpr.lexer import Token, TokenKind, tokenize

# Higher binds tighter. Comparison sits below arithmetic so ``a + b > c`` parses as expected.
BINARY_PRECEDENCE: Final[dict[str, int]] = {
    "||": 1,
    "&&": 2,
    "==": 3,
    "!=": 3,
    "<": 4,
    "<=": 4,
    ">": 4,
    ">=": 4,
    "+": 5,
    "-": 5,
    "*": 6,
    "/": 6,
    "^": 7,
}
RIGHT_ASSOCIATIVE: Final[frozenset[str]] = frozenset({"^"})
UNARY_PRECEDENCE: Final[int] = 8

MAX_PARSE_DEPTH: Final[int] = 120


class Parser:
    """Parses a token stream into a :class:`~brainiac.fastexpr.ast.Program`."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._index = 0
        self._depth = 0

    # -- token helpers -------------------------------------------------

    @property
    def _current(self) -> Token:
        return self._tokens[self._index]

    def _advance(self) -> Token:
        token = self._tokens[self._index]
        if token.kind is not TokenKind.EOF:
            self._index += 1
        return token

    def _check(self, kind: TokenKind, text: str | None = None) -> bool:
        token = self._current
        return token.kind is kind and (text is None or token.text == text)

    def _match(self, kind: TokenKind, text: str | None = None) -> Token | None:
        if self._check(kind, text):
            return self._advance()
        return None

    def _expect(self, kind: TokenKind, description: str) -> Token:
        if not self._check(kind):
            raise ParseError(
                f"Expected {description} but found {self._current.text or 'end of input'!r}",
                self._current.span,
            )
        return self._advance()

    # -- grammar -------------------------------------------------------

    def parse_program(self) -> Program:
        statements: list[Assignment] = []
        last: Expr | Assignment | None = None

        while not self._check(TokenKind.EOF):
            statement = self._parse_statement()
            if last is not None and isinstance(last, Assignment):
                statements.append(last)
            elif last is not None:
                raise ParseError(
                    "Only the final statement may be a bare expression; "
                    "earlier statements must assign to a variable",
                    self._current.span,
                )
            last = statement
            if not self._match(TokenKind.SEMICOLON) and not self._check(TokenKind.EOF):
                raise ParseError(
                    f"Expected ';' between statements but found {self._current.text!r}",
                    self._current.span,
                )

        if last is None:
            raise ParseError("Empty expression", SourceSpan(0, 0, 1, 1))
        if isinstance(last, Assignment):
            # BRAIN treats a trailing assignment as the alpha output.
            statements.append(last)
            return Program(statements=tuple(statements), output=Identifier(last.target))
        return Program(statements=tuple(statements), output=last)

    def _parse_statement(self) -> Expr | Assignment:
        if self._current.kind is TokenKind.IDENT and self._tokens[self._index + 1].kind is (
            TokenKind.ASSIGN
        ):
            name = self._advance().text
            self._advance()  # '=' or ':='
            return Assignment(target=name, value=self._parse_expression(0))
        return self._parse_expression(0)

    def _parse_expression(self, min_precedence: int) -> Expr:
        self._depth += 1
        if self._depth > MAX_PARSE_DEPTH:
            raise ParseError("Expression nests too deeply", self._current.span)
        try:
            left = self._parse_unary()
            while True:
                token = self._current
                if token.kind is not TokenKind.OP:
                    break
                precedence = BINARY_PRECEDENCE.get(token.text)
                if precedence is None or precedence < min_precedence:
                    break
                self._advance()
                next_min = precedence if token.text in RIGHT_ASSOCIATIVE else precedence + 1
                left = BinaryOp(op=token.text, left=left, right=self._parse_expression(next_min))

            if min_precedence <= 0 and self._match(TokenKind.QUESTION):
                if_true = self._parse_expression(0)
                self._expect(TokenKind.COLON, "':' in ternary expression")
                if_false = self._parse_expression(0)
                return Ternary(condition=left, if_true=if_true, if_false=if_false)
            return left
        finally:
            self._depth -= 1

    def _parse_unary(self) -> Expr:
        token = self._current
        if token.kind is TokenKind.OP and token.text in {"-", "+", "!"}:
            self._advance()
            operand = self._parse_expression(UNARY_PRECEDENCE)
            if token.text == "+":
                return operand
            if token.text == "-" and isinstance(operand, NumberLiteral):
                return NumberLiteral(-operand.value, f"-{operand.raw}" if operand.raw else "")
            return UnaryOp(op=token.text, operand=operand)
        return self._parse_postfix()

    def _parse_postfix(self) -> Expr:
        expr = self._parse_primary()
        # Vector field subscripts such as ``mdl_data[3]`` appear in a few BRAIN datasets.
        while self._match(TokenKind.LBRACKET):
            index = self._parse_expression(0)
            self._expect(TokenKind.RBRACKET, "']'")
            expr = Call(func="__index__", args=(expr, index))
        return expr

    def _parse_primary(self) -> Expr:
        token = self._current

        if token.kind is TokenKind.NUMBER:
            self._advance()
            return NumberLiteral(float(token.text), token.text)
        if token.kind is TokenKind.STRING:
            self._advance()
            return StringLiteral(token.text)
        if token.kind is TokenKind.BOOL:
            self._advance()
            return BoolLiteral(token.text.lower() == "true")
        if token.kind is TokenKind.LPAREN:
            self._advance()
            inner = self._parse_expression(0)
            self._expect(TokenKind.RPAREN, "')'")
            return inner
        if token.kind is TokenKind.IDENT:
            self._advance()
            if self._check(TokenKind.LPAREN):
                return self._parse_call(token.text)
            return Identifier(token.text)

        raise ParseError(
            f"Unexpected token {token.text or 'end of input'!r}",
            token.span,
        )

    def _parse_call(self, func: str) -> Call:
        self._expect(TokenKind.LPAREN, "'('")
        args: list[Expr] = []
        kwargs: list[Keyword] = []

        if not self._check(TokenKind.RPAREN):
            while True:
                if self._current.kind is TokenKind.IDENT and self._tokens[self._index + 1].kind is (
                    TokenKind.ASSIGN
                ):
                    name = self._advance().text
                    self._advance()
                    kwargs.append(Keyword(name=name, value=self._parse_expression(0)))
                else:
                    if kwargs:
                        raise ParseError(
                            "Positional argument follows a named argument",
                            self._current.span,
                        )
                    args.append(self._parse_expression(0))
                if not self._match(TokenKind.COMMA):
                    break
                if self._check(TokenKind.RPAREN):  # tolerate a trailing comma
                    break
        self._expect(TokenKind.RPAREN, f"')' to close call to {func!r}")
        return Call(func=func, args=tuple(args), kwargs=tuple(kwargs))


def parse(source: str) -> Program:
    """Parse a full alpha (possibly multi-statement) into a :class:`Program`."""
    return Parser(tokenize(source)).parse_program()


def parse_expression(source: str) -> Expr:
    """Parse a single expression, rejecting assignments and statement separators."""
    program = parse(source)
    if program.statements:
        raise ParseError("Expected a single expression without assignments", SourceSpan(0, 0, 1, 1))
    return program.output
