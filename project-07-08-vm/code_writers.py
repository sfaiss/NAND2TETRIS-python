"""Generate assembly code from parsed VM commands."""

from vm_command import CommandType, VMCommand


class CodeWriter:
    """Generate assembly code from parsed VM commands."""

    SEGMENTS = {
        "local":    "LCL",
        "argument": "ARG",
        "this":     "THIS",
        "that":     "THAT",
    }

    def __init__(self) -> None:
        self.label_count_cmp = 0
        self.label_count_ret_addr = 0

    def write(self, command: VMCommand) -> list[str]:
        """Main method for generating assembly code."""
        # add a comment of the command for debugging purposes
        code = [f"// {command}"]

        # determine how to process the command
        match command.type:
            case CommandType.PUSH:
                processing_fn = self._push
            case CommandType.POP:
                processing_fn = self._pop
            case CommandType.ARITHMETIC:
                processing_fn = self._arithmetic
            case CommandType.BRANCHING:
                processing_fn = self._branching
            case CommandType.FUNCTION:
                processing_fn = self._function
            case _:
                raise ValueError(f"Unknown command: {command.command}")

        # generate and collect the code
        code.extend(processing_fn(command))

        return code

    def _push(self, vm_command: VMCommand) -> list[str]:
        """Push a value onto the stack."""
        segment, value = vm_command.arg1, vm_command.arg2
        assert value is not None, "Argument 2 must be provided."

        match segment:
            case "constant":
                prep = [f"@{value}", "D=A"]
            case "argument" | "local" | "this" | "that":
                segment_name = self.SEGMENTS[segment]
                prep = [f"@{segment_name}", "D=M", f"@{value}", "A=D+A", "D=M"]
            case "pointer":
                prep = [f"@{"THIS" if value == 0 else "THAT"}", "D=M"]
            case "temp":
                prep = [f"@{5 + value}", "D=M"]
            case "static":
                prep = [f"@{vm_command.origin}.{value}", "D=M"]
            case _:
                raise ValueError(f"Unknown segment: {segment}")

        return [
            *prep,
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    def _pop(self, vm_command: VMCommand) -> list[str]:
        """Pop a value from the stack."""
        segment, value = vm_command.arg1, vm_command.arg2
        assert value is not None, "Argument 2 must be provided."

        match segment:
            case "argument" | "local" | "this" | "that":
                prep = [f"@{self.SEGMENTS[segment]}", "D=M", f"@{value}", "D=D+A"]
            case "pointer":
                prep = [f"@{"THIS" if value == 0 else "THAT"}", "D=A"]
            case "temp":
                prep = [f"@{5 + value}", "D=A"]
            case "static":
                prep = [f"@{vm_command.origin}.{value}", "D=A"]
            case _:
                raise ValueError(f"Unknown segment: {segment}")

        return [
            *prep,
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

    def _arithmetic(self, vm_command: VMCommand) -> list[str]:
        """Compute an arithmetic operation."""
        match vm_command.command:
            case "neg":
                return ["@SP", "A=M-1", "M=-M"]
            case "not":
                return ["@SP", "A=M-1", "M=!M"]
            case "add":
                return ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D+M"]
            case "sub":
                return ["@SP", "AM=M-1", "D=M", "A=A-1", "M=M-D"]
            case "and":
                return ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D&M"]
            case "or":
                return ["@SP", "AM=M-1", "D=M", "A=A-1", "M=D|M"]
            case "eq" | "gt" | "lt":
                return self._compare(vm_command)
            case _:
                raise ValueError(f"Unknown command: {vm_command.command}")

    def _compare(self, vm_command: VMCommand) -> list[str]:
        """Compare two values."""
        self.label_count_cmp += 1
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "D=M-D",
            f"@CMP{self.label_count_cmp}_TRUE",
            f"D;J{vm_command.command.upper()}",
            "@SP",
            "A=M-1",
            "M=0",
            f"@CMP{self.label_count_cmp}_END",
            "0;JMP",
            f"(CMP{self.label_count_cmp}_TRUE)",
            "@SP",
            "A=M-1",
            "M=-1",
            f"(CMP{self.label_count_cmp}_END)",
        ]

    def _branching(self, vm_command: VMCommand) -> list[str]:
        """Handle branching commands."""
        match vm_command.command:
            case "label":
                return [f"({vm_command.arg1})"]
            case "goto":
                return [f"@{vm_command.arg1}", "0;JMP"]
            case "if-goto":
                return ["@SP", "AM=M-1", "D=M", f"@{vm_command.arg1}", "D;JNE"]
            case _:
                raise ValueError(f"Unknown command: {vm_command.command}")

    def _push_d(self) -> list[str]:
        """Push the current value of D onto the stack."""
        return [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ]

    def _function(self, vm_command: VMCommand) -> list[str]:
        """Handle function commands."""

        match vm_command.command:
            case "function":
                assert vm_command.arg2 is not None, "Argument 2 must be provided."
                return (
                    [f"({vm_command.arg1})"]
                    + self._push(VMCommand("push", "constant", 0)) * vm_command.arg2
                )
            case "call":
                self.label_count_ret_addr += 1
                return [
                    # push return address
                    f"@RETADDR_{self.label_count_ret_addr}",
                    "D=A",
                    *self._push_d(),
                    # save LCL
                    "@LCL",
                    "D=M",
                    *self._push_d(),
                    # save ARG
                    "@ARG",
                    "D=M",
                    *self._push_d(),
                    # save THIS
                    "@THIS",
                    "D=M",
                    *self._push_d(),
                    # save THAT
                    "@THAT",
                    "D=M",
                    *self._push_d(),
                    # reposition ARG
                    "@SP",
                    "D=M",
                    "@5",
                    "D=D-A",
                    f"@{vm_command.arg2}",
                    "D=D-A",
                    "@ARG",
                    "M=D",
                    # reposition LCL
                    "@SP",
                    "D=M",
                    "@LCL",
                    "M=D",
                    # transfer control to callee
                    f"@{vm_command.arg1}",
                    "0;JMP",
                    # create return address label
                    f"(RETADDR_{self.label_count_ret_addr})",
                ]
            case "return":
                return [
                    # get address at the end of the callers frame
                    "@LCL",
                    "D=M",
                    "@endFrame",
                    "M=D",
                    # get the return address
                    "@5",
                    "A=D-A",
                    "D=M",
                    "@returnAddress",
                    "M=D",
                    # put the return value in ARG[0]
                    "@SP",
                    "A=M-1",
                    "D=M",
                    "@ARG",
                    "A=M",
                    "M=D",
                    # reposition Stack Pointer
                    "@ARG",
                    "D=M+1",
                    "@SP",
                    "M=D",
                    # restore THAT
                    "@endFrame",
                    "AM=M-1",
                    "D=M",
                    "@THAT",
                    "M=D",
                    # restore THIS
                    "@endFrame",
                    "AM=M-1",
                    "D=M",
                    "@THIS",
                    "M=D",
                    # restore ARG
                    "@endFrame",
                    "AM=M-1",
                    "D=M",
                    "@ARG",
                    "M=D",
                    # restore LCL
                    "@endFrame",
                    "AM=M-1",
                    "D=M",
                    "@LCL",
                    "M=D",
                    # jump to return address
                    "@returnAddress",
                    "A=M",
                    "0;JMP",
                ]
            case _:
                raise ValueError(f"Unknown command: {vm_command.command}")

    def _bootstrap(self) -> list[str]:
        """Prepare the VM for execution."""
        code = [
            "// Set stack pointer",
            "@256",
            "D=A",
            "@SP",
            "M=D",
        ]
        code.extend(self.write(VMCommand("call", "Sys.init", 0)))
        return code
