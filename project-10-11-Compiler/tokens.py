"""Custom data structure representing an individual token."""

from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, auto

KEYWORDS = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]  # noqa
SYMBOLS = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]  # noqa


class TokenType(Enum):
    """Lexical elements of the Jack language."""
    KEYWORD = auto()
    SYMBOL = auto()
    INTEGER_CONSTANT = auto()
    STRING_CONSTANT = auto()
    IDENTIFIER = auto()

    def __str__(self) -> str:
        """Convert name to lowercase or camelCase if it has underscores."""
        parts = self.name.lower().split("_")
        return parts[0] + "".join(word.capitalize() for word in parts[1:])


@dataclass(frozen=True, slots=True)
class Token:
    """Atomic lexical element."""
    type: TokenType
    value: str

    def __post_init__(self):
        # validation of token values
        match self.type:
            case TokenType.KEYWORD:
                if self.value not in KEYWORDS:
                    raise ValueError(f"Invalid keyword: {self.value}")
            case TokenType.SYMBOL:
                if self.value not in SYMBOLS:
                    raise ValueError(f"Invalid symbol: {self.value}")
            case TokenType.INTEGER_CONSTANT:
                if not self.value.isdigit() or not (0 <= int(self.value) <= 32767):
                    raise ValueError(f"Invalid integer constant: {self.value}")
            case TokenType.STRING_CONSTANT:
                if '"' in self.value or "\n" in self.value:
                    raise ValueError(f"Invalid string constant: {self.value}")
            case TokenType.IDENTIFIER:
                if self.value[0].isdigit():
                    raise ValueError(f"Invalid identifier: {self.value}")
            case _:
                raise ValueError(f"Invalid token type: {self.type}")


class TokenStream:
    """Provide access to tokens including lookaead."""
    def __init__(self, tokens: Iterable[Token]):
        self._tokens = deque(tokens)

    @property
    def current(self) -> Token | None:
        """Access to current (i.e. the first) token."""
        try:
            return self._tokens[0]
        except IndexError:
            return None

    @property
    def next(self) -> Token | None:
        """Access to next (i.e. the second) token."""
        try:
            return self._tokens[1]
        except IndexError:
            return None

    def pop_current(self) -> Token | None:
        """Retrieve the current token and advance the stream."""
        try:
            return self._tokens.popleft()
        except IndexError:
            return None
