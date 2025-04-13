import pytest

from structural_element import (
    ExpressionsType as ET,
    StructuralElement as SE,
)
from token_parser import Parser
from tokens import (
    Token as T,
    TokenStream as TS,
    TokenType as TT,
)


class TestArray:
    @pytest.mark.parametrize("term", [
        T(TT.INTEGER_CONSTANT, "123"),
        T(TT.STRING_CONSTANT, "abc"),
        T(TT.IDENTIFIER, "bar"),
    ])
    def test_should_parse_simple_array(self, term):
        tokens = (T(TT.IDENTIFIER, "arr"), T(TT.SYMBOL, "["), term, T(TT.SYMBOL, "]"))
        parser = Parser(TS(tokens))
        assert parser._term() == (
            SE(ET.TERM, children=(
                T(TT.IDENTIFIER, "arr"),
                T(TT.SYMBOL, "["),
                SE(ET.EXPRESSION, children=[SE(ET.TERM, children=[term])]),
                T(TT.SYMBOL, "]")
            ))
        )

    def test_should_parse_expression_as_array_key(self):
        tokens = (T(TT.IDENTIFIER, "arr"), T(TT.SYMBOL, "["), T(TT.IDENTIFIER, "x"), T(TT.SYMBOL, "+"), T(TT.INTEGER_CONSTANT, "1"), T(TT.SYMBOL, "]"))
        parser = Parser(TS(tokens))
        assert parser._term() == (
            SE(ET.TERM, children=(
                T(TT.IDENTIFIER, "arr"),
                T(TT.SYMBOL, "["),
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")]),
                    T(TT.SYMBOL, "+"),
                    SE(ET.TERM, children=[T(TT.INTEGER_CONSTANT, "1")]),
                ]),
                T(TT.SYMBOL, "]")
            ))
        )
