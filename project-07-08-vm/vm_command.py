"""Custom representation of a VM command."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class CommandType(Enum):
    """Type of a VM command."""
    ARITHMETIC = auto()
    PUSH = auto()
    POP = auto()
    BRANCHING = auto()
    FUNCTION = auto()

    @classmethod
    def from_string(cls, string: str) -> CommandType:
        """Construct a CommandType from a string."""
        match string:
            case "add" | "sub" | "neg" | "eq" | "gt" | "lt" | "and" | "or" | "not":
                return cls.ARITHMETIC
            case "push":
                return cls.PUSH
            case "pop":
                return cls.POP
            case "label" | "goto" | "if-goto":
                return cls.BRANCHING
            case "function" | "return" | "call":
                return cls.FUNCTION
            case _:
                raise ValueError(f"Unknown command type: {string}")


@dataclass
class VMCommand:
    """Representation of a VM command."""
    command: str
    type: CommandType = field(init=False)
    arg1: str | None = None
    arg2: int | None = None
    origin: str | None = None

    @classmethod
    def from_string(cls, string: str) -> VMCommand:
        """Construct a VMCommand from a string."""
        match string.split():
            case [command]:
                return cls(command)
            case [command, arg1]:
                return cls(command, arg1)
            case [command, arg1, arg2]:
                return cls(command, arg1, int(arg2))
            case _:
                raise ValueError(f"Invalid command: {string!r}")

    def __post_init__(self) -> None:
        self.type = CommandType.from_string(self.command)

    def __str__(self) -> str:
        s = str(self.command)
        if self.arg1 is not None:
            s += f" {self.arg1}"
        if self.arg2 is not None:
            s += f" {self.arg2}"
        return s
