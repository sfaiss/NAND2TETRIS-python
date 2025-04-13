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



class TestExpression:
    @pytest.mark.parametrize("term", [
        T(TT.INTEGER_CONSTANT, "123"),
        T(TT.STRING_CONSTANT, "abc"),
        T(TT.KEYWORD, "true"),
        T(TT.IDENTIFIER, "bar"),
    ])
    def test_should_parse_simple_expression(self, term):
        tokens = (term,)
        parser = Parser(TS(tokens))
        assert parser._expression() == SE(ET.EXPRESSION, children=[SE(ET.TERM, tokens)])

    def test_should_parse_single_operation(self):
        tokens = (T(TT.IDENTIFIER, "x"), T(TT.SYMBOL, "+"), T(TT.INTEGER_CONSTANT, "1"))
        parser = Parser(TS(tokens))
        assert parser._expression() == (
            SE(ET.EXPRESSION, children=(
                SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")]),
                T(TT.SYMBOL, "+"),
                SE(ET.TERM, children=[T(TT.INTEGER_CONSTANT, "1")]),
            ))
        )

    def test_should_parse_multiple_operations(self):
        tokens = (T(TT.IDENTIFIER, "x"), T(TT.SYMBOL, "+"), T(TT.INTEGER_CONSTANT, "1"), T(TT.SYMBOL, "*"), T(TT.INTEGER_CONSTANT, "2"))
        parser = Parser(TS(tokens))
        assert parser._expression() == (
            SE(ET.EXPRESSION, children=(
                SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")]),
                T(TT.SYMBOL, "+"),
                SE(ET.TERM, children=[T(TT.INTEGER_CONSTANT, "1")]),
                T(TT.SYMBOL, "*"),
                SE(ET.TERM, children=[T(TT.INTEGER_CONSTANT, "2")]),
            ))
        )


class TestTerm:
    @pytest.mark.parametrize("tokens", [
        [],                   # no tokens
        [T(TT.SYMBOL, "]")],  # empty array index
    ])
    def test_should_raise_on_empty_term(self, tokens):
        parser = Parser(TS(tokens))
        with pytest.raises(SyntaxError):
            _ = parser._term()

    def test_should_parse_expression_in_parenthesis(self):
        tokens = (T(TT.SYMBOL, "("), T(TT.IDENTIFIER, "x"), T(TT.SYMBOL, ")"))
        parser = Parser(TS(tokens))
        assert parser._term() == (
            SE(ET.TERM, children=(
                T(TT.SYMBOL, "("),
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")]),
                ]),
                T(TT.SYMBOL, ")"),
            ))
        )

    @pytest.mark.parametrize("unary_op", [T(TT.SYMBOL, "-"), T(TT.SYMBOL, "~")])
    def test_should_parse_unary_operation(self, unary_op):
        tokens = (unary_op, T(TT.IDENTIFIER, "x"))
        parser = Parser(TS(tokens))
        assert parser._term() == (
            SE(ET.TERM, children=(
                unary_op,
                SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")]),
            ))
        )


class TestSubroutineCall:
    @pytest.mark.parametrize("tokens", (
        (T(TT.IDENTIFIER, "foo"), T(TT.SYMBOL, "("), T(TT.SYMBOL, ")")),
        (T(TT.IDENTIFIER, "Foo"), T(TT.SYMBOL, "."), T(TT.IDENTIFIER, "bar"), T(TT.SYMBOL, "("), T(TT.SYMBOL, ")")),
        (T(TT.IDENTIFIER, "foo"), T(TT.SYMBOL, "."), T(TT.IDENTIFIER, "bar"), T(TT.SYMBOL, "("), T(TT.SYMBOL, ")"),),
    ))
    def test_should_parse_call(self, tokens):
        parser = Parser(TS(tokens))
        assert parser._subroutine_call() == (
            *tokens[:-1],
            SE(ET.EXPRESSION_LIST),
            tokens[-1],
        )


class TestExpressionList:
    def test_should_parse_empty_expression_list(self):
        tokens = (
            T(TT.SYMBOL, "("),
            T(TT.SYMBOL, ")"),
        )
        parser = Parser(TS(tokens))
        assert parser._expression_list() == (
            T(TT.SYMBOL, "("),
            SE(ET.EXPRESSION_LIST),
            T(TT.SYMBOL, ")"),
        )

    def test_should_parse_expression_list_with_single_item(self):
        tokens = (
            T(TT.SYMBOL, "("),
            T(TT.INTEGER_CONSTANT, "42"),
            T(TT.SYMBOL, ")"),
        )
        parser = Parser(TS(tokens))
        assert parser._expression_list() == (
            T(TT.SYMBOL, "("),
            SE(ET.EXPRESSION_LIST, children=[
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.INTEGER_CONSTANT, "42")]),
                ]),
            ]),
            T(TT.SYMBOL, ")"),
        )

    def test_should_parse_expression_list_with_multiple_items(self):
        tokens = (
            T(TT.SYMBOL, "("),
            T(TT.INTEGER_CONSTANT, "42"),
            T(TT.SYMBOL, ","),
            T(TT.STRING_CONSTANT, "foo"),
            T(TT.SYMBOL, ","),
            T(TT.IDENTIFIER, "bar"),
            T(TT.SYMBOL, ")"),
        )
        parser = Parser(TS(tokens))
        assert parser._expression_list() == (
            T(TT.SYMBOL, "("),
            SE(ET.EXPRESSION_LIST, children=(
                SE(ET.EXPRESSION, children=[SE(ET.TERM, children=[T(TT.INTEGER_CONSTANT, "42")])]),
                T(TT.SYMBOL, ","),
                SE(ET.EXPRESSION, children=[SE(ET.TERM, children=[T(TT.STRING_CONSTANT, "foo")])]),
                T(TT.SYMBOL, ","),
                SE(ET.EXPRESSION, children=[SE(ET.TERM, children=[T(TT.IDENTIFIER, "bar")])]),
            )),
            T(TT.SYMBOL, ")"),
        )
