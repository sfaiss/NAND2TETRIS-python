import pytest

from code_writers import CodeWriter
from parser import VMCommand


class TestComment:
    @pytest.mark.parametrize(
        "command",
        [
            "push constant 7",
            "pop local 0",
            "push static 2",
            "add",
            "label LOOP",
            "if-goto END",
            "function Foo.bar 2",
            "call Foo.bar 2",
            "return",
        ],
    )
    def test_should_create_comment_of_original_command(self, command):
        vm_command = VMCommand.from_string(command)
        comment, *_ = CodeWriter().write(vm_command)
        assert comment == f"// {command}"


class TestPush:
    def test_should_push_constant(self):
        vm_command = VMCommand.from_string("push constant 7")
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            "@7",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    @pytest.mark.parametrize("segment, value, expected", [
        ("local",    0, "@LCL"),
        ("argument", 1, "@ARG"),
        ("this",     2, "@THIS"),
        ("that",     3, "@THAT"),
    ])
    def test_should_push_to_segment(self, segment, value, expected):
        vm_command = VMCommand("push", segment, value)
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            expected,
            "D=M",
            f"@{value}",
            "A=D+A",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    @pytest.mark.parametrize("segment, value, expected", [
        ("pointer", 0, "@THIS"),
        ("pointer", 1, "@THAT"),
    ])
    def test_should_push_pointer(self, segment, value, expected):
        vm_command = VMCommand("push", segment, value)
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            expected,
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    def test_should_push_temp(self):
        vm_command = VMCommand("push", "temp", 0)
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            "@5",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]


class TestPop:
    @pytest.mark.parametrize("segment, value, expected", [
        ("local",    0, "@LCL"),
        ("argument", 1, "@ARG"),
        ("this",     2, "@THIS"),
        ("that",     3, "@THAT"),
    ])
    def test_should_pop_to_segment(self, segment, value, expected):
        vm_command = VMCommand("pop", segment, value)
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            expected,
            "D=M",
            f"@{value}",
            "D=D+A",
            "@R13",
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]

    @pytest.mark.parametrize("segment, value, expected", [
        ("pointer", 0, "@THIS"),
        ("pointer", 1, "@THAT"),
    ])
    def test_should_pop_pointer(self, segment, value, expected):
        vm_command = VMCommand("pop", segment, value)
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            expected,
            "D=A",
            "@R13",
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]

    def test_should_pop_temp(self):
        vm_command = VMCommand("pop", "temp", 0)
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            "@5",
            "D=A",
            "@R13",
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]


class TestArithmetic:
    @pytest.mark.parametrize("command, expected", [
        ("add", ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D+M"]),
        ("sub", ["@SP", "AM=M-1", "D=M", "A=A-1", "M=M-D"]),
        ("neg", ["@SP", "A=M-1", "M=-M"]),
        ("and", ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D&M"]),
        ("or",  ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D|M"]),
        ("not", ["@SP", "A=M-1", "M=!M"]),
    ])
    def test_should_use_native_commands(self, command, expected):
        vm_command = VMCommand(command)
        _, *code = CodeWriter().write(vm_command)
        assert code == expected

    @pytest.mark.parametrize("command", ["eq", "lt", "gt"])
    def test_should_compare_values(self, command,):
        vm_command = VMCommand(command)
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "D=M-D",
            "@CMP1_TRUE",
            f"D;J{command.upper()}",
            "@SP",
            "A=M-1",
            "M=0",
            "@CMP1_END",
            "0;JMP",
            "(CMP1_TRUE)",
            "@SP",
            "A=M-1",
            "M=-1",
            "(CMP1_END)",
        ]

    def test_should_create_unique_labels(self):
        vm_command = VMCommand("eq")
        labels: list[set[str]] = []
        writer = CodeWriter()
        for _ in range(2):
            _, *code = writer.write(vm_command)
            labels.append(set(l for l in code if l.startswith("(CMP")))
        assert labels[0].isdisjoint(labels[1])


class TestStatic:
    def test_should_push_static(self):
        vm_command = VMCommand("push", "static", 2, origin="file")
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            "@file.2",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    def test_should_pop_static(self):
        vm_command = VMCommand("pop", "static", 3, origin="file")
        _, *code = CodeWriter().write(vm_command)
        assert code == [
            "@file.3",
            "D=A",
            "@R13",
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@R13",
            "A=M",
            "M=D",
        ]


class TestBranching:
    def test_should_create_label(self):
        vm_command = VMCommand("label", "LABEL_1")
        _, *code = CodeWriter().write(vm_command)
        assert code == ["(LABEL_1)"]

    def test_should_create_unconditional_jump(self):
        vm_command = VMCommand("goto", "LABEL_2")
        _, *code = CodeWriter().write(vm_command)
        assert code == ["@LABEL_2", "0;JMP"]

    def test_should_create_conditional_jump(self):
        vm_command = VMCommand("if-goto", "LABEL_3")
        _, *code = CodeWriter().write(vm_command)
        assert code == ["@SP", "AM=M-1", "D=M", "@LABEL_3", "D;JNE"]


class TestFunction:
    def test_should_create_label(self):
        vm_command = VMCommand("function", "Some.function", 2)
        _, *code = CodeWriter().write(vm_command)
        assert code[0] == "(Some.function)"

    @pytest.mark.parametrize("n_args", [1, 2, 3])
    def test_should_initialize_local_variables(self, n_args):
        vm_command = VMCommand("function", "Some.function", n_args)
        _, *code = CodeWriter().write(vm_command)
        assert code.count("@0") == n_args
