"""Tokenizer for WorldQuant Fast Expression source code."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Final

from brainiac.fastexpr.errors import LexError, SourceSpan


class TokenKind(Enum):
    NUMBER = auto()
    STRING = auto()
    IDENT = auto()
    BOOL = auto()
    OP = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    ASSIGN = auto()
    QUESTION = auto()
    COLON = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    kind: TokenKind
    text: str
    span: SourceSpan

    def __str__(self) -> str:
        return f"{self.kind.name}({self.text!r})"


# Longest-first so that ``<=`` wins over ``<`` and ``==`` over the assignment ``=``.
_OPERATORS: Final[tuple[str, ...]] = (
    "<=",
    ">=",
    "==",
    "!=",
    "&&",
    "||",
    ":=",
    "<",
    ">",
    "+",
    "-",
    "*",
    "/",
    "^",
    "!",
)

_NUMBER_RE: Final = re.compile(
    r"\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+(?:[eE][+-]?\d+)?"
)
_IDENT_RE: Final = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
_BOOL_LITERALS: Final = frozenset({"true", "false", "True", "False"})


class Lexer:
    """Converts Fast Expression source text into a flat token stream.

    Comments start with ``#`` or ``//`` and run to the end of the line, matching what the
    BRAIN editor accepts.
    """

    def __init__(self, source: str) -> None:
        self.source = source
        self._pos = 0
        self._line = 1
        self._line_start = 0

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            self._skip_trivia()
            if self._pos >= len(self.source):
                tokens.append(Token(TokenKind.EOF, "", self._span(self._pos, self._pos)))
                return tokens
            tokens.append(self._next_token())

    def _span(self, start: int, end: int) -> SourceSpan:
        return SourceSpan(
            start=start, end=end, line=self._line, column=start - self._line_start + 1
        )

    def _skip_trivia(self) -> None:
        src = self.source
        while self._pos < len(src):
            ch = src[self._pos]
            if ch == "\n":
                self._pos += 1
                self._line += 1
                self._line_start = self._pos
            elif ch.isspace():
                self._pos += 1
            elif ch == "#" or src.startswith("//", self._pos):
                newline = src.find("\n", self._pos)
                self._pos = len(src) if newline == -1 else newline
            else:
                return

    def _next_token(self) -> Token:
        src = self.source
        start = self._pos
        ch = src[start]

        if ch.isdigit() or (ch == "." and start + 1 < len(src) and src[start + 1].isdigit()):
            match = _NUMBER_RE.match(src, start)
            assert match is not None
            self._pos = match.end()
            return Token(TokenKind.NUMBER, match.group(), self._span(start, self._pos))

        if ch.isalpha() or ch == "_":
            match = _IDENT_RE.match(src, start)
            assert match is not None
            self._pos = match.end()
            text = match.group()
            kind = TokenKind.BOOL if text in _BOOL_LITERALS else TokenKind.IDENT
            return Token(kind, text, self._span(start, self._pos))

        if ch in "\"'":
            return self._read_string(start, quote=ch)

        simple = {
            "(": TokenKind.LPAREN,
            ")": TokenKind.RPAREN,
            "[": TokenKind.LBRACKET,
            "]": TokenKind.RBRACKET,
            ",": TokenKind.COMMA,
            ";": TokenKind.SEMICOLON,
            "?": TokenKind.QUESTION,
            ":": TokenKind.COLON,
        }
        if ch in simple and not src.startswith(":=", start):
            self._pos += 1
            return Token(simple[ch], ch, self._span(start, self._pos))

        for op in _OPERATORS:
            if src.startswith(op, start):
                self._pos += len(op)
                kind = TokenKind.ASSIGN if op == ":=" else TokenKind.OP
                return Token(kind, op, self._span(start, self._pos))

        if ch == "=":
            self._pos += 1
            return Token(TokenKind.ASSIGN, "=", self._span(start, self._pos))

        raise LexError(f"Unexpected character {ch!r}", self._span(start, start + 1))

    def _read_string(self, start: int, quote: str) -> Token:
        src = self.source
        pos = start + 1
        chunks: list[str] = []
        while pos < len(src):
            ch = src[pos]
            if ch == "\\" and pos + 1 < len(src):
                chunks.append(src[pos + 1])
                pos += 2
                continue
            if ch == quote:
                self._pos = pos + 1
                return Token(TokenKind.STRING, "".join(chunks), self._span(start, self._pos))
            if ch == "\n":
                break
            chunks.append(ch)
            pos += 1
        raise LexError("Unterminated string literal", self._span(start, min(pos, len(src))))


def tokenize(source: str) -> list[Token]:
    """Tokenize ``source``, raising :class:`LexError` on malformed input."""
    return Lexer(source).tokenize()
