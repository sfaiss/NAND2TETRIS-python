import pytest

from assembler import CInstruction


@pytest.mark.parametrize("token, expected", [
    (CInstruction(0, 0, 0, 0), "1110000000000000"),
    (CInstruction(1, 0, 0, 0), "1111000000000000"),
    (CInstruction(0, 0b111111, 0, 0), "1110111111000000"),
    (CInstruction(0, 0, 0b111, 0), "1110000000111000"),
    (CInstruction(0, 0, 0, 0b111), "1110000000000111"),
])
def test_should_convert_to_string(token, expected):
    assert str(token) == expected


class TestFromSymbol():
    @pytest.mark.parametrize("symbol, expected", [
        ("A", CInstruction(0, 0b110000, 0, 0)),
        ("M", CInstruction(1, 0b110000, 0, 0)),
    ])
    def test_should_parse_c_instruction(self, symbol, expected):
        assert CInstruction.from_symbol(symbol) == expected

    @pytest.mark.parametrize("symbol, expected", [
        ("A=1", CInstruction(0, 0b111111, 0b100, 0)),
        ("D=1", CInstruction(0, 0b111111, 0b010, 0)),
        ("M=1", CInstruction(0, 0b111111, 0b001, 0)),
        ("ADM=1", CInstruction(0, 0b111111, 0b111, 0)),
    ])
    def test_should_parse_c_instruction_with_dest(self, symbol, expected):
        assert CInstruction.from_symbol(symbol) == expected
