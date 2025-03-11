import pytest

from vm_command import VMCommand


@pytest.mark.parametrize("string, expected", [
    ("push constant 1",          VMCommand("push", "constant", 1)),
    ("pop local 0",              VMCommand("pop", "local", 0)),
    ("add",                      VMCommand("add")),
    ("label LABEL_1",            VMCommand("label", "LABEL_1")),
    ("goto LABEL_2",             VMCommand("goto", "LABEL_2")),
    ("if-goto LABEL_3",          VMCommand("if-goto", "LABEL_3")),
    ("function Some.Function 3", VMCommand("function", "Some.Function", 3)),
    ("return",                   VMCommand("return")),
    ("call Another.Function 2",  VMCommand("call", "Another.Function", 2)),
])
def test_should_convert_string_to_command(string, expected):
    assert VMCommand.from_string(string) == expected
