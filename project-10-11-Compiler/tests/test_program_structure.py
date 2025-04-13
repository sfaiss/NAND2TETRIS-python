from itertools import product

import pytest

from data.samples import class_tokens, class_var_dec_tokens, subroutine_dec_tokens
from structural_element import (
    ProgramStructureType as PST,
    StatementsType as ST,
    StructuralElement as SE,
)
from token_parser import Parser
from tokens import (
    Token as T,
    TokenStream as TS,
    TokenType as TT,
)


class TestClass:
    def test_should_parse_minimalistic(self):
        tokens = class_tokens()
        parser = Parser(TS(tokens))
        assert parser._class() == SE(PST.CLASS, tokens)

    def test_should_parse_class_var_dec(self):
        tokens = class_tokens(class_var_dec=class_var_dec_tokens())
        parser = Parser(TS(tokens))
        assert parser._class() == (
            SE(PST.CLASS, children=(
                T(TT.KEYWORD, "class"),
                T(TT.IDENTIFIER, "Main"),
                T(TT.SYMBOL, "{"),
                SE(PST.CLASS_VAR_DEC, children=class_var_dec_tokens()),
                T(TT.SYMBOL, "}"),
            ))
        )

    def test_should_parse_subroutine_dec(self):
        tokens = class_tokens(subroutine_dec=subroutine_dec_tokens(body=[T(TT.KEYWORD, "return"), T(TT.SYMBOL, ";")]))
        parser = Parser(TS(tokens))
        assert parser._class() == (
            SE(PST.CLASS, children=(
                T(TT.KEYWORD, "class"),
                T(TT.IDENTIFIER, "Main"),
                T(TT.SYMBOL, "{"),
                SE(PST.SUBROUTINE_DEC, children=(
                    T(TT.KEYWORD, "function"),
                    T(TT.KEYWORD, "void"),
                    T(TT.IDENTIFIER, "main"),
                    T(TT.SYMBOL, "("),
                    SE(PST.PARAMETER_LIST),
                    T(TT.SYMBOL, ")"),
                    SE(PST.SUBROUTINE_BODY, children=(
                        T(TT.SYMBOL, "{"),
                        SE(ST.STATEMENTS, children=(
                            SE(ST.RETURN_STATEMENT, children=(
                                T(TT.KEYWORD, "return"),
                                T(TT.SYMBOL, ";"),
                            )),
                        )),
                        T(TT.SYMBOL, "}"),
                    ))
                )),
                T(TT.SYMBOL, "}"),
            ))
        )


class TestClassVarDec:
    @pytest.mark.parametrize(
        "kind, var_type",
        list(product(["static", "field"], ["int", "char", "boolean"])),
    )
    def test_should_parse_minimalistic(self, kind, var_type):
        tokens = class_var_dec_tokens(kind, var_type)
        parser = Parser(TS(tokens))
        assert parser._class_var_dec() == SE(PST.CLASS_VAR_DEC, children=tokens)

    def test_should_parse_single_class_var_dec_with_custom_type(self):
        tokens = class_var_dec_tokens(var_type="Point", names=["p"])
        parser = Parser(TS(tokens))
        assert parser._class_var_dec() == SE(PST.CLASS_VAR_DEC, children=tokens)

    def test_should_parse_multiple_class_var_decs(self):
        tokens = class_var_dec_tokens(names=["x", "y", "z"])
        parser = Parser(TS(tokens))
        assert parser._class_var_dec() == SE(PST.CLASS_VAR_DEC, children=tokens)


class TestSubRoutineDec:
    @pytest.mark.parametrize(
        "kind, return_type",
        list(product(
            ["constructor", "function", "method"],
            ["void", "int", "char", "boolean", "Array"],
        )),
    )
    def test_should_parse_empty_subroutine(self, kind, return_type):
        built_in_return_types = ("void", "int", "boolean", "char")
        tokens = subroutine_dec_tokens(kind, return_type)
        parser = Parser(TS(tokens))
        assert parser._subroutine_dec() == (
            SE(PST.SUBROUTINE_DEC, children=(
                T(TT.KEYWORD, kind),
                T(TT.KEYWORD if return_type in built_in_return_types else TT.IDENTIFIER, return_type),
                T(TT.IDENTIFIER, "main"),
                T(TT.SYMBOL, "("),
                SE(PST.PARAMETER_LIST),
                T(TT.SYMBOL, ")"),
                SE(PST.SUBROUTINE_BODY, children=(
                    T(TT.SYMBOL, "{"),
                    SE(ST.STATEMENTS),
                    T(TT.SYMBOL, "}"),
                )),
            ))
        )

    @pytest.mark.parametrize("plist", [
        (T(TT.KEYWORD, "int"), T(TT.IDENTIFIER, "x")),
        (T(TT.IDENTIFIER, "Point"), T(TT.IDENTIFIER, "p")),
    ])
    def test_should_parse_single_parameter(self, plist):
        tokens = subroutine_dec_tokens(parameter_list=plist)
        parser = Parser(TS(tokens))
        assert parser._subroutine_dec() == (
            SE(PST.SUBROUTINE_DEC, children=(
                T(TT.KEYWORD, "function"),
                T(TT.KEYWORD, "void"),
                T(TT.IDENTIFIER, "main"),
                T(TT.SYMBOL, "("),
                SE(PST.PARAMETER_LIST, children=plist),
                T(TT.SYMBOL, ")"),
                SE(PST.SUBROUTINE_BODY, children=(
                    T(TT.SYMBOL, "{"),
                    SE(ST.STATEMENTS),
                    T(TT.SYMBOL, "}"),
                )),
            ))
        )

    def test_should_parse_multiple_parameters(self):
        plist = (
            T(TT.KEYWORD, "int"),
            T(TT.IDENTIFIER, "x"),
            T(TT.SYMBOL, ","),
            T(TT.KEYWORD, "boolean"),
            T(TT.IDENTIFIER, "flag"),
            T(TT.SYMBOL, ","),
            T(TT.IDENTIFIER, "Array"),
            T(TT.IDENTIFIER, "a"),
        )
        tokens = subroutine_dec_tokens(parameter_list=plist)
        parser = Parser(TS(tokens))
        assert parser._subroutine_dec() == (
            SE(PST.SUBROUTINE_DEC, children=(
                T(TT.KEYWORD, "function"),
                T(TT.KEYWORD, "void"),
                T(TT.IDENTIFIER, "main"),
                T(TT.SYMBOL, "("),
                SE(PST.PARAMETER_LIST, children=plist),
                T(TT.SYMBOL, ")"),
                SE(PST.SUBROUTINE_BODY, children=(
                    T(TT.SYMBOL, "{"),
                    SE(ST.STATEMENTS),
                    T(TT.SYMBOL, "}"),
                )),
            ))
        )


class TestVarDec:
    @pytest.mark.parametrize("var_type", ["int", "char", "boolean"])
    def test_should_parse_built_in_type(self, var_type):
        tokens = (T(TT.KEYWORD, "var"), T(TT.KEYWORD, var_type), T(TT.IDENTIFIER, "x"), T(TT.SYMBOL, ";"))
        parser = Parser(TS(tokens))
        assert parser._var_dec() == SE(PST.VAR_DEC, children=tokens)

    def test_should_parse_custom_type(self):
        tokens = (T(TT.KEYWORD, "var"), T(TT.IDENTIFIER, "Array"), T(TT.IDENTIFIER, "a"), T(TT.SYMBOL, ";"))
        parser = Parser(TS(tokens))
        assert parser._var_dec() == SE(PST.VAR_DEC, children=tokens)

    def test_should_parse_multiple_parameters(self):
        tokens = (
            T(TT.KEYWORD, "var"),
            T(TT.KEYWORD, "int"),
            T(TT.IDENTIFIER, "first"),
            T(TT.SYMBOL, ","),
            T(TT.IDENTIFIER, "second"),
            T(TT.SYMBOL, ","),
            T(TT.IDENTIFIER, "third"),
            T(TT.SYMBOL, ";"),
        )
        parser = Parser(TS(tokens))
        assert parser._var_dec() == SE(PST.VAR_DEC, children=tokens)
