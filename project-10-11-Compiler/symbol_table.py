"""Symbol Table to keep track of variables and their types."""

from collections import Counter
from dataclasses import dataclass
from enum import Enum


class SymbolType(Enum):
    STATIC = "static"
    FIELD = "this"
    ARG = "argument"
    VAR = "local"
    NONE = "none"


@dataclass(frozen=True)
class Symbol:
    name: str
    type: str
    kind: SymbolType
    index: int


class SymbolTable:
    def __init__(self):
        self.symbols: set[Symbol] = set()
        self._counter = Counter()

    def __contains__(self, name: str) -> bool:
        """Membership testing using the `in` operator."""
        return any(symbol.name == name for symbol in self.symbols)

    def define(self, name: str, type: str, kind: SymbolType) -> None:
        """Define a new variable."""
        symbol = Symbol(name, type, kind, self._counter[kind])
        self.symbols.add(symbol)
        self._counter[kind] += 1

    def get_symbol(self, name: str) -> Symbol:
        """Get a symbol by name."""
        for symbol in self.symbols:
            if symbol.name == name:
                return symbol
        raise LookupError(f"Symbol {name!r} not found.")

    def get_type(self, name: str) -> str:
        """Get the type of a variable."""
        return self.get_symbol(name).type

    def get_segment(self, name: str) -> str:
        """Get the segment of a variable according to the standard mapping."""
        return self.get_symbol(name).kind.value

    def get_index(self, name: str) -> int:
        """Get the index of a variable."""
        return self.get_symbol(name).index

    def count(self, kind: SymbolType) -> int:
        """Count the number of variables of a given kind."""
        return self._counter[kind]
