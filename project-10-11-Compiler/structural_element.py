"""Custom data structure representing an individual structural element."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from tokens import Token


class StructuralElementType(Enum):
    """Structural elements of the Jack language."""
    def __str__(self) -> str:
        """Convert name to lowercase or camelCase if it has underscores."""
        parts = self.name.lower().split("_")
        return parts[0] + "".join(word.capitalize() for word in parts[1:])


class ProgramStructureType(StructuralElementType):
    """Main program structure"""
    CLASS = auto()
    CLASS_VAR_DEC = auto()
    TYPE = auto()
    SUBROUTINE_DEC = auto()
    PARAMETER_LIST = auto()
    SUBROUTINE_BODY = auto()
    VAR_DEC = auto()
    CLASS_NAME = auto()
    SUBROUTINE_NAME = auto()
    VAR_NAME = auto()


class StatementsType(StructuralElementType):
    """Main statements"""
    STATEMENTS = auto()
    STATEMENT = auto()
    LET_STATEMENT = auto()
    IF_STATEMENT = auto()
    WHILE_STATEMENT = auto()
    DO_STATEMENT = auto()
    RETURN_STATEMENT = auto()


class ExpressionsType(StructuralElementType):
    """Main expressions"""
    EXPRESSION = auto()
    TERM = auto()
    SUBROUTINE_CALL = auto()
    EXPRESSION_LIST = auto()
    OP = auto()
    UNARY_OP = auto()
    KEYWORD_CONSTANT = auto()


@dataclass(frozen=True, slots=True)
class StructuralElement:
    """Single element of a grammatical structure."""
    type: StructuralElementType
    children: tuple[StructuralElement | Token, ...] = field(default_factory=tuple)

    def __post_init__(self):
        # convert children to tuple
        if not isinstance(self.children, tuple):
            # bypass `frozen=True`
            object.__setattr__(self, "children", tuple(self.children))
