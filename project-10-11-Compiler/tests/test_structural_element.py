from itertools import chain, product

import pytest

from structural_element import (
    ExpressionsType,
    ProgramStructureType,
    StatementsType,
    StructuralElement,
)

ELEMENT_TYPES = {
    ProgramStructureType: ("CLASS", "CLASS_VAR_DEC", "TYPE", "SUBROUTINE_DEC", "PARAMETER_LIST", "SUBROUTINE_BODY", "VAR_DEC", "CLASS_NAME", "SUBROUTINE_NAME", "VAR_NAME"),
    StatementsType: ("STATEMENTS", "STATEMENT", "LET_STATEMENT", "IF_STATEMENT", "WHILE_STATEMENT", "DO_STATEMENT", "RETURN_STATEMENT"),
    ExpressionsType: ("EXPRESSION", "TERM", "SUBROUTINE_CALL", "EXPRESSION_LIST", "OP", "UNARY_OP", "KEYWORD_CONSTANT"),
}


class TestStructualElementType:
    @pytest.mark.parametrize(
        "element_type, value",
        chain(*(product([k], ELEMENT_TYPES[k]) for k in ELEMENT_TYPES.keys())),
    )
    def test_should_have_all_types(self, element_type, value):
        assert hasattr(element_type, value)

    @pytest.mark.parametrize(
        "element_type, str_output",
        [
            (ProgramStructureType.CLASS, "class"),
            (StatementsType.STATEMENTS,  "statements"),
            (ExpressionsType.EXPRESSION, "expression"),
        ],
    )
    def test_should_print_without_underscores_as_lowercase(self, element_type, str_output):
        assert str(element_type) == str_output

    @pytest.mark.parametrize(
        "element_type, str_output",
        (
            (ProgramStructureType.CLASS_VAR_DEC, "classVarDec"),
            (StatementsType.LET_STATEMENT,       "letStatement"),
            (ExpressionsType.SUBROUTINE_CALL,    "subroutineCall"),
        ),
    )
    def test_should_print_with_underscores_as_camelcase(self, element_type, str_output):
        assert str(element_type) == str_output



class TestStructuralElement:
    @pytest.mark.parametrize("field", ["type", "children"])
    def test_should_have_mandatory_fields(self, field):
        assert field in StructuralElement.__annotations__

    def test_should_convert_children_to_tuple(self):
        assert isinstance(
            StructuralElement(ProgramStructureType.CLASS, children=[]).children,
            tuple,
        )
