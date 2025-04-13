from itertools import chain, product

import pytest

from tokens import KEYWORDS, SYMBOLS, Token, TokenType

TOKEN_TYPES = ["KEYWORD", "SYMBOL", "INTEGER_CONSTANT", "STRING_CONSTANT", "IDENTIFIER"]


@pytest.mark.parametrize("token_type", TOKEN_TYPES)
def test_should_have_all_types(token_type):
    assert hasattr(TokenType, token_type)


class TestToken:
    @pytest.mark.parametrize("field", ["type", "value"])
    def test_should_have_mandatory_fields(self, field):
        assert field in Token.__annotations__

    @pytest.mark.parametrize(
        "token_type, value",
        chain(
            product([TokenType.KEYWORD],          KEYWORDS),
            product([TokenType.SYMBOL],           SYMBOLS),
            product([TokenType.INTEGER_CONSTANT], ["0", "12345", "32767"]),
            product([TokenType.STRING_CONSTANT],  ["a", "abc", "abc123"]),
            product([TokenType.IDENTIFIER],       ["foo", "_foo", "foo123", "foo_bar_1"]),
        ),
    )
    def test_should_accept_valid_input(self, token_type, value):
        try:
            Token(token_type, value)
        except:
            pytest.fail(f"Token creation failed for valid {token_type!r}: {value}")


class TestTokenMisuse:
    @pytest.mark.parametrize(
        "token_type, value",
        chain(
            product([TokenType.KEYWORD],          ["invalid_keyword"]),
            product([TokenType.SYMBOL],           ["X"]),
            product([TokenType.INTEGER_CONSTANT], ["-1", "32768", "3.141", "x"]),
            product([TokenType.STRING_CONSTANT],  ['foo"bar', "foo\nbar"]),
            product([TokenType.IDENTIFIER],       ["1_foo"]),
        ),
    )
    def test_should_raise_for_invalid_input(self, token_type, value):
        with pytest.raises(ValueError):
            Token(token_type, value)


class TestTokenType:
    def test_should_print_without_underscores_as_lowercase(self):
        assert str(TokenType.KEYWORD) == "keyword"

    def test_should_print_with_underscores_as_camelcase(self):
        assert str(TokenType.INTEGER_CONSTANT) == "integerConstant"


class TestTokenStream:
    def test_should_have_access_to_current_token(self, token_stream):
        assert token_stream.current == Token(TokenType.KEYWORD, "class")

    def test_should_have_access_to_next_token(self, token_stream):
        assert token_stream.next == Token(TokenType.IDENTIFIER, "Main")

    def test_should_be_able_to_pop_current_token(self, token_stream):
        assert token_stream.pop_current() == Token(TokenType.KEYWORD, "class")

    def test_should_advance_token_after_popping(self, token_stream):
        assert token_stream.current == Token(TokenType.KEYWORD, "class")
        _ = token_stream.pop_current()
        assert token_stream.current == Token(TokenType.IDENTIFIER, "Main")

    def test_should_return_none_if_there_is_no_current_token(self, token_stream):
        __ = [token_stream.pop_current() for _ in range(3)]
        assert token_stream.current is None

    def test_should_return_none_if_there_is_no_next_token(self, token_stream):
        __ = [token_stream.pop_current() for _ in range(2)]
        assert token_stream.next is None

    def test_should_return_none_if_there_is_no_token_to_pop(self, token_stream):
        __ = [token_stream.pop_current() for _ in range(3)]
        assert token_stream.pop_current() is None
