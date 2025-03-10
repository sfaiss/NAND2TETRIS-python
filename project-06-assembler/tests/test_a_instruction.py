import pytest

from assembler import AInstruction


@pytest.mark.parametrize("symbol, expected", [
    ("@0", AInstruction(0)),
    ("@1", AInstruction(1)),
])
def test_should_parse_a_instruction(symbol, expected):
    assert AInstruction.from_symbol(symbol) == expected


@pytest.mark.parametrize("token, expected", [
    (AInstruction(0), "0000000000000000"),
    (AInstruction(1), "0000000000000001"),
])
def test_should_convert_to_string(token, expected):
    assert str(token) == expected
