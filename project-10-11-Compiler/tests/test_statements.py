import pytest

from structural_element import (
    ExpressionsType as ET,
    StatementsType as ST,
    StructuralElement as SE,
)
from token_parser import Parser
from tokens import (
    Token as T,
    TokenStream as TS,
    TokenType as TT,
)


class TestLetStatement:
    @pytest.mark.parametrize("term", [
        T(TT.INTEGER_CONSTANT, "123"),
        T(TT.STRING_CONSTANT, "abc"),
        T(TT.KEYWORD, "true"),
        T(TT.IDENTIFIER, "bar"),
    ])
    def test_should_parse_simple_assignment(self, term):
        tokens = (T(TT.KEYWORD, "let"), T(TT.IDENTIFIER, "foo"), T(TT.SYMBOL, "="), term, T(TT.SYMBOL, ";"))
        parser = Parser(TS(tokens))
        assert parser._let_statement() == (
            SE(ST.LET_STATEMENT, children=(
                T(TT.KEYWORD, "let"),
                T(TT.IDENTIFIER, "foo"),
                T(TT.SYMBOL, "="),
                SE(ET.EXPRESSION, children=[SE(ET.TERM, children=[term])]),
                T(TT.SYMBOL, ";")
            ))
        )

    def test_should_parse_array_assignment(self):
        tokens = (
            T(TT.KEYWORD, "let"),
            T(TT.IDENTIFIER, "foo"),
            T(TT.SYMBOL, "["),
            T(TT.INTEGER_CONSTANT, "0"),
            T(TT.SYMBOL, "]"),
            T(TT.SYMBOL, "="),
            T(TT.INTEGER_CONSTANT, "123"),
            T(TT.SYMBOL, ";"),
        )
        parser = Parser(TS(tokens))
        assert parser._let_statement() == (
            SE(ST.LET_STATEMENT, children=(
                T(TT.KEYWORD, "let"),
                T(TT.IDENTIFIER, "foo"),
                T(TT.SYMBOL, "["),
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.INTEGER_CONSTANT, "0")]),
                ]),
                T(TT.SYMBOL, "]"),
                T(TT.SYMBOL, "="),
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.INTEGER_CONSTANT, "123")]),
                ]),
                T(TT.SYMBOL, ";")
            ))
        )


class TestIfStatement:
    def test_should_parse_if_statement(self):
        tokens = (
            T(TT.KEYWORD, "if"),
            T(TT.SYMBOL, "("),
            T(TT.IDENTIFIER, "x"),
            T(TT.SYMBOL, ")"),
            T(TT.SYMBOL, "{"),
            T(TT.SYMBOL, "}"),
        )
        parser = Parser(TS(tokens))
        assert parser._if_statement() == (
            SE(ST.IF_STATEMENT, children=(
                T(TT.KEYWORD, "if"),
                T(TT.SYMBOL, "("),
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")])
                ]),
                T(TT.SYMBOL, ")"),
                T(TT.SYMBOL, "{"),
                SE(ST.STATEMENTS),
                T(TT.SYMBOL, "}"),
            ))
        )

    def test_should_parse_if_else_statement(self):
        tokens = (
            T(TT.KEYWORD, "if"),
            T(TT.SYMBOL, "("),
            T(TT.IDENTIFIER, "x"),
            T(TT.SYMBOL, ")"),
            T(TT.SYMBOL, "{"),
            T(TT.SYMBOL, "}"),
            T(TT.KEYWORD, "else"),
            T(TT.SYMBOL, "{"),
            T(TT.SYMBOL, "}"),
        )
        parser = Parser(TS(tokens))
        assert parser._if_statement() == (
            SE(ST.IF_STATEMENT, children=(
                T(TT.KEYWORD, "if"),
                T(TT.SYMBOL, "("),
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")])
                ]),
                T(TT.SYMBOL, ")"),
                T(TT.SYMBOL, "{"),
                SE(ST.STATEMENTS),
                T(TT.SYMBOL, "}"),
                T(TT.KEYWORD, "else"),
                T(TT.SYMBOL, "{"),
                SE(ST.STATEMENTS),
                T(TT.SYMBOL, "}"),
            ))
        )


class TestWhileStatement:
    def test_should_parse_while_statement(self):
        tokens = (
            T(TT.KEYWORD, "while"),
            T(TT.SYMBOL, "("),
            T(TT.IDENTIFIER, "x"),
            T(TT.SYMBOL, ")"),
            T(TT.SYMBOL, "{"),
            T(TT.SYMBOL, "}"),
        )
        parser = Parser(TS(tokens))
        assert parser._while_statement() == (
            SE(ST.WHILE_STATEMENT, children=(
                T(TT.KEYWORD, "while"),
                T(TT.SYMBOL, "("),
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")])
                ]),
                T(TT.SYMBOL, ")"),
                T(TT.SYMBOL, "{"),
                SE(ST.STATEMENTS),
                T(TT.SYMBOL, "}"),
            ))
        )


class TestDoStatement:
    def test_should_parse_subroutine_call(self):
        tokens = (T(TT.KEYWORD, "do"), T(TT.IDENTIFIER, "foo"), T(TT.SYMBOL, "("), T(TT.SYMBOL, ")"), T(TT.SYMBOL, ";"))
        parser = Parser(TS(tokens))
        assert parser._do_statement() == (
            SE(ST.DO_STATEMENT, children=(
                T(TT.KEYWORD, "do"),
                T(TT.IDENTIFIER, "foo"),
                T(TT.SYMBOL, "("),
                SE(ET.EXPRESSION_LIST),
                T(TT.SYMBOL, ")"),
                T(TT.SYMBOL, ";"),
            ))
        )


class TestReturnStatement:
    def test_should_parse_empty_return(self):
        tokens = (T(TT.KEYWORD, "return"), T(TT.SYMBOL, ";"))
        parser = Parser(TS(tokens))
        assert parser._return_statement() == SE(ST.RETURN_STATEMENT, children=tokens)

    def test_should_parse_return_variable(self):
        tokens = (T(TT.KEYWORD, "return"), T(TT.IDENTIFIER, "x"), T(TT.SYMBOL, ";"))
        parser = Parser(TS(tokens))
        assert parser._return_statement() == (
            SE(ST.RETURN_STATEMENT, children=(
                T(TT.KEYWORD, "return"),
                SE(ET.EXPRESSION, children=[
                    SE(ET.TERM, children=[T(TT.IDENTIFIER, "x")]),
                ]),
                T(TT.SYMBOL, ";")
            ))
        )
