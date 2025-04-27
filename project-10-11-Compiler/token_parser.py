"""Parse tokens according to the grammar of the Jack language."""

from collections.abc import Container
from contextlib import suppress

from structural_element import (
    ExpressionsType,
    ProgramStructureType,
    StatementsType,
    StructuralElement,
)
from tokens import Token, TokenStream, TokenType

Tokens = tuple[Token, ...]


class Parser:
    def __init__(self, token_stream: TokenStream):
        self._token_stream = token_stream

    def parse(self) -> StructuralElement:
        """Parse tokens left-to-right, leftmost derivation (LL)."""
        while current := self._token_stream.current:
            match current:
                case Token(type=TokenType.KEYWORD, value="class"):
                    return self._class()
                case _:
                    raise SyntaxError(f"Unexpected token: {current!r}")

    def _expect(
        self,
        token_type: TokenType | Container[TokenType],
        value: str | Container[str] | None = None,
    ) -> Token:
        """Make sure the current token is what you think it is."""
        current = self._token_stream.current
        if not current:
            msg = f"Unexpected end of input. Expected: {(token_type, value)!r}"
            raise SyntaxError(msg)
        if isinstance(token_type, TokenType) and (current.type != token_type):
            msg = f"Unexpected type of token: {current.type} != {token_type}"
            raise SyntaxError(msg)
        if isinstance(token_type, Container) and (current.type not in token_type):
            msg = f"Unexpected type of token: {current.type} not in {token_type!r}"
            raise SyntaxError(msg)
        if value and isinstance(value, str) and current.value != value:
            msg = f"Unexpected value of token: {current.value!r} != {value!r}"
            raise SyntaxError(msg)
        if value and isinstance(value, Container) and current.value not in value:
            msg = f"Unexpected value of token: {current.value!r} not in {value!r}"
            raise SyntaxError(msg)
        return self._token_stream.pop_current()

    def _class(self) -> StructuralElement:
        """Parse a `class`-structure."""
        children=[
            self._expect(TokenType.KEYWORD, "class"),
            self._expect(TokenType.IDENTIFIER),
            self._expect(TokenType.SYMBOL, "{"),
        ]

        while self._token_stream.current.value in ("static", "field"):
            children.append(self._class_var_dec())

        while self._token_stream.current.value in ("constructor", "function", "method"):
            children.append(self._subroutine_dec())

        children.append(self._expect(TokenType.SYMBOL, "}"))

        return StructuralElement(ProgramStructureType.CLASS, children)

    def _class_var_dec(self) -> StructuralElement:
        """Parse class variable declarations."""
        children = [
            self._expect(TokenType.KEYWORD, ("static", "field")),
            self._variable_type(),
            self._expect(TokenType.IDENTIFIER),
        ]

        try:
            while True:
                # multiple variable declarations
                children.append(self._expect(TokenType.SYMBOL, ","))
                children.append(self._expect(TokenType.IDENTIFIER))
        except SyntaxError:
            children.append(self._expect(TokenType.SYMBOL, ";"))

        return StructuralElement(ProgramStructureType.CLASS_VAR_DEC, children)

    def _variable_type(self, include_void: bool = False) -> Token:
        """Parse a variable type."""
        built_in_types = ["int", "char", "boolean"]
        if include_void:
            built_in_types.append("void")
        try:
            # built-in types
            return self._expect(TokenType.KEYWORD, built_in_types)
        except SyntaxError:
            # custom types
            return self._expect(TokenType.IDENTIFIER)

    def _subroutine_dec(self) -> StructuralElement:
        """Parse subroutine declarations."""
        children = [
            self._expect(TokenType.KEYWORD, ("constructor", "function", "method")),
            self._variable_type(include_void=True),
            self._expect(TokenType.IDENTIFIER),
        ]

        children.extend(self._parameter_list())
        children.append(self._subroutine_body())

        return StructuralElement(ProgramStructureType.SUBROUTINE_DEC, children)

    def _parameter_list(self) -> Tokens:
        """Parse a parameter list (including paranthesis)."""
        opening_parenthesis = self._expect(TokenType.SYMBOL, "(")
        children = []
        while True:
            try:
                children.append(self._variable_type())
            except SyntaxError:
                break  # no more parameters

            children.append(self._expect(TokenType.IDENTIFIER))
            with suppress(SyntaxError):
                children.append(self._expect(TokenType.SYMBOL, ","))
        closing_parenthesis = self._expect(TokenType.SYMBOL, ")")
        return (
            opening_parenthesis,
            StructuralElement(ProgramStructureType.PARAMETER_LIST, children),
            closing_parenthesis,
        )

    def _subroutine_body(self) -> StructuralElement:
        """Parse the body of a sub routine (including braces)."""
        children = []
        children.append(self._expect(TokenType.SYMBOL, "{"))
        while self._token_stream.current == Token(TokenType.KEYWORD, "var"):
            children.append(self._var_dec())
        children.append(self._statements())
        children.append(self._expect(TokenType.SYMBOL, "}"))
        return StructuralElement(ProgramStructureType.SUBROUTINE_BODY, children)

    def _var_dec(self) -> StructuralElement:
        """Parse variable declarations."""
        children = [
            self._expect(TokenType.KEYWORD, "var"),
            self._variable_type(),
            self._expect(TokenType.IDENTIFIER),
        ]

        try:
            while True:
                # multiple variable declarations
                children.append(self._expect(TokenType.SYMBOL, ","))
                children.append(self._expect(TokenType.IDENTIFIER))
        except SyntaxError:
            children.append(self._expect(TokenType.SYMBOL, ";"))

        return StructuralElement(ProgramStructureType.VAR_DEC, children)

    def _statements(self) -> StructuralElement:
        """Parse statements."""
        children = []
        while True:
            match self._token_stream.current:
                case Token(TokenType.KEYWORD, value="let"):
                    children.append(self._let_statement())
                case Token(TokenType.KEYWORD, value="if"):
                    children.append(self._if_statement())
                case Token(TokenType.KEYWORD, value="while"):
                    children.append(self._while_statement())
                case Token(TokenType.KEYWORD, value="do"):
                    children.append(self._do_statement())
                case Token(TokenType.KEYWORD, value="return"):
                    children.append(self._return_statement())
                case _:
                    # no more statements
                    break
        return StructuralElement(StatementsType.STATEMENTS, children)

    def _let_statement(self) -> StructuralElement:
        """Parse a let statement."""
        children = []
        children.append(self._expect(TokenType.KEYWORD, "let"))
        if self._token_stream.next == Token(TokenType.SYMBOL, "["):
            children.extend(self._array())
        else:
            children.append(self._expect(TokenType.IDENTIFIER))
        children.append(self._expect(TokenType.SYMBOL, "="))
        children.append(self._expression())
        children.append(self._expect(TokenType.SYMBOL, ";"))
        return StructuralElement(StatementsType.LET_STATEMENT, children)

    def _if_statement(self) -> StructuralElement:
        """Parse an if statement."""
        children = []
        children.append(self._expect(TokenType.KEYWORD, "if"))
        children.append(self._expect(TokenType.SYMBOL, "("))
        children.append(self._expression())
        children.append(self._expect(TokenType.SYMBOL, ")"))
        children.append(self._expect(TokenType.SYMBOL, "{"))
        children.append(self._statements())
        children.append(self._expect(TokenType.SYMBOL, "}"))
        if self._token_stream.current == Token(TokenType.KEYWORD, "else"):
            children.append(self._token_stream.pop_current())
            children.append(self._expect(TokenType.SYMBOL, "{"))
            children.append(self._statements())
            children.append(self._expect(TokenType.SYMBOL, "}"))
        return StructuralElement(StatementsType.IF_STATEMENT, children)

    def _while_statement(self) -> StructuralElement:
        """Parse a while statement."""
        children = []
        children.append(self._expect(TokenType.KEYWORD, "while"))
        children.append(self._expect(TokenType.SYMBOL, "("))
        children.append(self._expression())
        children.append(self._expect(TokenType.SYMBOL, ")"))
        children.append(self._expect(TokenType.SYMBOL, "{"))
        children.append(self._statements())
        children.append(self._expect(TokenType.SYMBOL, "}"))
        return StructuralElement(StatementsType.WHILE_STATEMENT, children)

    def _do_statement(self) -> StructuralElement:
        """Parse a do statement."""
        children = []
        children.append(self._expect(TokenType.KEYWORD, "do"))
        children.extend(self._subroutine_call())
        children.append(self._expect(TokenType.SYMBOL, ";"))
        return StructuralElement(StatementsType.DO_STATEMENT, children)

    def _return_statement(self) -> StructuralElement:
        """Parse a return statement."""
        children = []
        children.append(self._expect(TokenType.KEYWORD, "return"))
        with suppress(SyntaxError):
            children.append(self._expression())
        children.append(self._expect(TokenType.SYMBOL, ";"))
        return StructuralElement(StatementsType.RETURN_STATEMENT, children)

    def _expression(self) -> StructuralElement:
        """Parse an expression."""
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        term = [self._term()]
        while True:
            try:
                term.append(self._expect(TokenType.SYMBOL, ops))
                term.append(self._term())
            except SyntaxError:
                # no more operations
                break
        return StructuralElement(
            ExpressionsType.EXPRESSION,
            children=term,
        )

    def _term(self) -> StructuralElement:
        """Parse a term."""
        children = []

        if not self._token_stream.current:
            raise SyntaxError("Term cannot be empty.")

        match self._token_stream.current:
            case Token(TokenType.INTEGER_CONSTANT | TokenType.STRING_CONSTANT | TokenType.KEYWORD):
                children.append(self._token_stream.pop_current())
            case Token(TokenType.IDENTIFIER):
                match self._token_stream.next:
                    case Token(TokenType.SYMBOL, "["):
                        children.extend(self._array())
                    case Token(TokenType.SYMBOL, "(") | Token(TokenType.SYMBOL, "."):
                        children.extend(self._subroutine_call())
                    case _:
                        children.append(self._token_stream.pop_current())
            case Token(TokenType.SYMBOL, "("):
                children.append(self._token_stream.pop_current())
                children.append(self._expression())
                children.append(self._expect(TokenType.SYMBOL, ")"))
            case Token(TokenType.SYMBOL, "-" | "~"):
                children.append(self._token_stream.pop_current())
                children.append(self._term())
            case _:
                msg = f"Unexpected token for term: {self._token_stream.current.type}"
                raise SyntaxError(msg)
        return StructuralElement(ExpressionsType.TERM, children)

    def _array(self) -> Tokens:
        """Parse an array."""
        return (
            self._expect(TokenType.IDENTIFIER),
            self._expect(TokenType.SYMBOL, "["),
            self._expression(),
            self._expect(TokenType.SYMBOL, "]"),
        )

    def _subroutine_call(self) -> Tokens:
        """Parse a subroutine call."""
        tokens = []
        tokens.append(self._expect(TokenType.IDENTIFIER))
        if self._token_stream.current == Token(TokenType.SYMBOL, "."):
            tokens.append(self._token_stream.pop_current())
            tokens.append(self._expect(TokenType.IDENTIFIER))
        tokens.extend(self._expression_list())
        return tuple(tokens)

    def _expression_list(self) -> Tokens:
        """Parse an expression list (including paranthesis)."""
        opening_parenthesis = self._expect(TokenType.SYMBOL, "(")
        children = []
        while True:
            try:
                children.append(self._expression())
            except SyntaxError:
                break  # no more expressions

            with suppress(SyntaxError):
                children.append(self._expect(TokenType.SYMBOL, ","))
        closing_parenthesis = self._expect(TokenType.SYMBOL, ")")
        return (
            opening_parenthesis,
            StructuralElement(ExpressionsType.EXPRESSION_LIST, children),
            closing_parenthesis,
        )
