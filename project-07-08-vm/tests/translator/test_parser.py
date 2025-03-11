import pytest
from pyfakefs.fake_filesystem import FakeFilesystem
from pyfakefs.fake_file import FakeFile

from parser import Parser, VMCommand


@pytest.fixture
def vmfile(fs: FakeFilesystem) -> FakeFile:
    contents = "push constant 1\npush constant 2\nadd"
    return fs.create_file("path/to/file.vm", contents=contents)


@pytest.fixture
def parser(vmfile: FakeFile) -> Parser:
    return Parser(path=vmfile.path)


@pytest.mark.parametrize("str_command, vm_command", [
    ("push constant 1",          VMCommand("push", "constant", 1,          origin="file")),
    ("pop local 0",              VMCommand("pop", "local", 0,              origin="file")),
    ("add",                      VMCommand("add",                          origin="file")),
    ("label NAME",               VMCommand("label", "NAME",                origin="file")),
    ("goto LABEL",               VMCommand("goto", "LABEL",                origin="file")),
    ("if-goto LABEL",            VMCommand("if-goto", "LABEL",             origin="file")),
    ("function Some.Function 3", VMCommand("function", "Some.Function", 3, origin="file")),
    ("return",                   VMCommand("return",                       origin="file")),
    ("call Another.Function 2",  VMCommand("call", "Another.Function", 2,  origin="file")),
])
def test_should_convert_string_to_command(str_command: str, vm_command: VMCommand, parser: Parser):
    assert parser._convert(str_command) == vm_command

def test_should_store_filename(parser: Parser):
    assert parser._filename == "file"

def test_should_store_commands(parser: Parser):
    assert parser.commands == (
        VMCommand("push", "constant", 1, origin="file"),
        VMCommand("push", "constant", 2, origin="file"),
        VMCommand("add",                 origin="file"),
    )

def test_should_provide_access_to_commands(parser: Parser):
    assert parser.commands[0] == VMCommand("push", "constant", 1, origin="file")
    assert parser.commands[1] == VMCommand("push", "constant", 2, origin="file")
    assert parser.commands[2] == VMCommand("add",                 origin="file")
