"""Adding project directory to sys.path for easier imports."""

import pathlib
import sys

import pytest

script_dir = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir.parent))

from tokens import Token, TokenStream, TokenType


@pytest.fixture
def token_stream():
    tokens = (
        Token(TokenType.KEYWORD, "class"),
        Token(TokenType.IDENTIFIER, "Main"),
        Token(TokenType.SYMBOL, "{"),
    )
    return TokenStream(tokens)
