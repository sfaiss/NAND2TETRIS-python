"""Tokenize source code into keywords, symbols, integers, strings and identifiers."""

import re
from collections.abc import Generator
from typing import cast

from tokens import KEYWORDS, SYMBOLS, Token, TokenType


def escape_for_bracket_expression(symbol: str) -> str:
    """Escape special characters for use in regex bracket expressions.

      - `]` is closing the bracket expression
      - `-` defines a range of characters (e.g. `0-9)`
    """
    if symbol in "]-":
        symbol = rf"\{symbol}"
    return symbol


def tokenize(code: str) -> Generator[Token, None, None]:
    """Convert source code into its corresponding tokens."""
    pattern = re.compile(
        rf"""
               (?P<KEYWORD>\b(?:{"|".join(KEYWORDS)})\b)
            | "(?P<STRING_CONSTANT>[^"]*?)"
            |  (?P<IDENTIFIER>\b[a-zA-Z_]\w*)
            |  (?P<SYMBOL>[{"".join(map(escape_for_bracket_expression, SYMBOLS))}])
            |  (?P<INTEGER_CONSTANT>\d+)
            |  (?P<WHITESPACE>\s+)
            |  (?P<MISMATCH>.)  # catch invalid character
        """,
        flags=re.VERBOSE,
    )

    for m in pattern.finditer(code):
        kind = cast(str, m.lastgroup)

        if kind == "WHITESPACE":
            continue

        if kind == "MISMATCH":
            raise ValueError(f"Unexpected character: {m.group()}")

        token_type = TokenType[kind]
        value = m.group(token_type.name)
        yield Token(token_type, value)
