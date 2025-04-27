"""Write code for the virtual machine."""

VMCode = list[str]


class VMWriter:
    """Writes code in the VM language."""

    @staticmethod
    def write_push(segment: str, index: int) -> VMCode:
        """Write a push command to the output file."""
        return [f"push {segment} {index}"]

    @staticmethod
    def write_pop(segment: str, index: int) -> VMCode:
        """Write a pop command to the output file."""
        return [f"pop {segment} {index}"]

    @staticmethod
    def write_arithmetic(command: str) -> VMCode:
        """Write an arithmetic command to the output file."""
        return [command]

    @staticmethod
    def write_label(label: str) -> VMCode:
        """Write a label command to the output file."""
        return [f"label {label}"]

    @staticmethod
    def write_goto(label: str) -> VMCode:
        """Write a goto command to the output file."""
        return [f"goto {label}"]

    @staticmethod
    def write_if(label: str) -> VMCode:
        """Write an if-goto command to the output file."""
        return [f"if-goto {label}"]

    @staticmethod
    def write_call(name: str, n_args: int) -> VMCode:
        """Write a call command to the output file."""
        return [f"call {name} {n_args}"]

    @staticmethod
    def write_function(name: str, n_vars: int) -> VMCode:
        """Write a function command to the output file."""
        return [f"function {name} {n_vars}"]

    @staticmethod
    def write_return() -> VMCode:
        """Write a return command to the output file."""
        return ["return"]
