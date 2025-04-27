"""Write VM code from tokens."""

import logging
from collections.abc import Container
from contextlib import suppress

from symbol_table import SymbolTable, SymbolType
from tokens import Token, TokenStream, TokenType
from vm_writer import VMWriter

Tokens = tuple[Token, ...]
VMCode = list[str]

LOG = logging.getLogger(__name__)


class CompilationEngine:
    def __init__(self, token_stream: TokenStream):
        self._token_stream = token_stream
        self._class_name = None
        self._symbol_table_class = None
        self._symbol_table_subroutine = None
        self._label_counter = {
            "if": 0,
            "while": 0,
        }

    def compile(self) -> VMCode:
        """Compile tokens left-to-right, leftmost derivation (LL)."""
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

    def _next_label(self, label: str) -> str:
        """Generate the next label."""
        current_count = self._label_counter[label.lower()]
        self._label_counter[label] += 1
        return f"{label.upper()}_{current_count}"

    def _get_symbol_table(self, name: str) -> SymbolTable:
        """Retrieve the symbol table containing the provided variable name."""
        if name in self._symbol_table_subroutine:
            return self._symbol_table_subroutine
        if name in self._symbol_table_class:
            return self._symbol_table_class
        raise LookupError(f"Symbol {name!r} not found.")

    def _class(self) -> VMCode:
        """Compile a `class`-structure."""
        self._symbol_table_class = SymbolTable()
        code = []
        self._expect(TokenType.KEYWORD, "class")
        self._class_name = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.SYMBOL, "{")
        while self._token_stream.current.value in ("static", "field"):
            self._class_var_dec()
        while self._token_stream.current.value in ("constructor", "function", "method"):
            code.extend(self._subroutine_dec())
        self._expect(TokenType.SYMBOL, "}")
        return code

    def _class_var_dec(self) -> None:
        """Compile class variable declarations."""
        match self._expect(TokenType.KEYWORD, ("static", "field")):
            case Token(TokenType.KEYWORD, "static"):
                kind = SymbolType.STATIC
            case Token(TokenType.KEYWORD, "field"):
                kind = SymbolType.FIELD
            case _:
                raise SyntaxError("Unexpected class variable declaration.")

        variable_type = self._variable_type().value
        self._symbol_table_class.define(
            self._expect(TokenType.IDENTIFIER).value,
            variable_type,
            kind,
        )

        try:
            while True:
                # multiple variable declarations
                self._expect(TokenType.SYMBOL, ",")
                self._symbol_table_class.define(
                    self._expect(TokenType.IDENTIFIER).value,
                    variable_type,
                    kind,
                )
        except SyntaxError:
            self._expect(TokenType.SYMBOL, ";")


    def _variable_type(self, include_void: bool = False) -> Token:
        """Compile a variable type."""
        built_in_types = ["int", "char", "boolean"]
        if include_void:
            built_in_types.append("void")
        try:
            # built-in types
            return self._expect(TokenType.KEYWORD, built_in_types)
        except SyntaxError:
            # custom types
            return self._expect(TokenType.IDENTIFIER)

    def _parameter_list(self) -> None:
        """Compile a parameter list (including paranthesis)."""
        self._expect(TokenType.SYMBOL, "(")
        while True:
            try:
                parameter_type = self._variable_type().value
            except SyntaxError:
                break  # no more parameters
            name = self._expect(TokenType.IDENTIFIER).value
            self._symbol_table_subroutine.define(
                name,
                parameter_type,
                SymbolType.ARG,
            )
            with suppress(SyntaxError):
                self._expect(TokenType.SYMBOL, ",")
        self._expect(TokenType.SYMBOL, ")")

    def _subroutine_dec(self) -> VMCode:
        """Compile subroutine declarations."""
        self._symbol_table_subroutine = SymbolTable()
        code = []
        subroutine_type = self._expect(TokenType.KEYWORD, ("constructor", "function", "method")).value
        return_type = self._variable_type(include_void=True)
        name = self._expect(TokenType.IDENTIFIER).value
        if subroutine_type == "method":
            # inject `this` pointer as first argument
            self._symbol_table_subroutine.define(
                "this",
                self._class_name,
                SymbolType.ARG,
            )
        self._parameter_list()
        body = self._subroutine_body()
        n_local_variables = self._symbol_table_subroutine.count(SymbolType.VAR)

        if subroutine_type == "constructor":
            code.extend(VMWriter.write_function(f"{self._class_name}.{name}", n_local_variables))
            code.extend(VMWriter.write_push("constant", self._symbol_table_class.count(SymbolType.FIELD)))
            code.extend(VMWriter.write_call("Memory.alloc", 1))
            code.extend(VMWriter.write_pop("pointer", 0))
        elif subroutine_type == "method":
            code.extend(VMWriter.write_function(f"{self._class_name}.{name}", n_local_variables))
            # inject `this` pointer as first argument
            code.extend(VMWriter.write_push("argument", 0))
            code.extend(VMWriter.write_pop("pointer", 0))
        else:
            # function
            code.extend(VMWriter.write_function(f"{self._class_name}.{name}", n_local_variables))

        code.extend(body)
        if return_type.value == "void":
            code.extend(VMWriter.write_push("constant", 0))
        code.extend(VMWriter.write_return())
        return code

    def _var_dec(self) -> None:
        """Compile variable declarations."""
        self._expect(TokenType.KEYWORD, "var")
        variable_type = self._variable_type().value
        self._symbol_table_subroutine.define(
            self._expect(TokenType.IDENTIFIER).value,
            variable_type,
            SymbolType.VAR,
        )
        try:
            while True:
                # multiple variable declarations
                self._expect(TokenType.SYMBOL, ",")
                self._symbol_table_subroutine.define(
                    self._expect(TokenType.IDENTIFIER).value,
                    variable_type,
                    SymbolType.VAR,
                )
        except SyntaxError:
            self._expect(TokenType.SYMBOL, ";")

    def _subroutine_body(self) -> VMCode:
        """Compile the body of a sub routine (including braces)."""
        code = []
        self._expect(TokenType.SYMBOL, "{")
        while self._token_stream.current == Token(TokenType.KEYWORD, "var"):
            self._var_dec()
        code.extend(self._statements())
        self._expect(TokenType.SYMBOL, "}")
        return code

    def _statements(self) -> VMCode:
        """Compile statements."""
        code = []
        while True:
            match self._token_stream.current:
                case Token(TokenType.KEYWORD, value="let"):
                    code.extend(self._let_statement())
                case Token(TokenType.KEYWORD, value="if"):
                    code.extend(self._if_statement())
                case Token(TokenType.KEYWORD, value="while"):
                    code.extend(self._while_statement())
                case Token(TokenType.KEYWORD, value="do"):
                    code.extend(self._do_statement())
                case Token(TokenType.KEYWORD, value="return"):
                    code.extend(self._return_statement())
                case _:
                    # no more statements
                    break
        return code

    def _let_statement(self) -> VMCode:
        """Compile a let statement."""
        code = []
        self._expect(TokenType.KEYWORD, "let")
        if self._token_stream.next == Token(TokenType.SYMBOL, "["):
            code.extend(self._array())
            self._expect(TokenType.SYMBOL, "=")
            code.extend(self._expression())
            code.extend(VMWriter.write_pop("temp", 0))
            code.extend(VMWriter.write_pop("pointer", 1))
            code.extend(VMWriter.write_push("temp", 0))
            code.extend(VMWriter.write_pop("that", 0))
        else:
            name = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.SYMBOL, "=")
            code.extend(self._expression())
            symbol_table = self._get_symbol_table(name)
            index = symbol_table.get_index(name)
            segment = symbol_table.get_segment(name)
            code.extend(VMWriter.write_pop(segment, index))
        self._expect(TokenType.SYMBOL, ";")
        return code

    def _if_statement(self) -> VMCode:
        """Parse an if statement."""
        label_1 = self._next_label("if")
        label_2 = self._next_label("if")

        code = []
        self._expect(TokenType.KEYWORD, "if")
        self._expect(TokenType.SYMBOL, "(")
        code.extend(self._expression())
        code.extend(VMWriter.write_arithmetic("not"))
        code.extend(VMWriter.write_if(label_1))
        self._expect(TokenType.SYMBOL, ")")
        self._expect(TokenType.SYMBOL, "{")
        code.extend(self._statements())
        code.extend(VMWriter.write_goto(label_2))
        self._expect(TokenType.SYMBOL, "}")
        code.extend(VMWriter.write_label(label_1))
        if self._token_stream.current == Token(TokenType.KEYWORD, "else"):
            self._token_stream.pop_current()
            self._expect(TokenType.SYMBOL, "{")
            code.extend(self._statements())
            self._expect(TokenType.SYMBOL, "}")
        code.extend(VMWriter.write_label(label_2))
        return code

    def _while_statement(self) -> VMCode:
        """Compile a while statement."""
        label_1 = self._next_label("while")
        label_2 = self._next_label("while")

        code = []
        self._expect(TokenType.KEYWORD, "while")
        code.extend(VMWriter.write_label(label_1))
        self._expect(TokenType.SYMBOL, "(")
        code.extend(self._expression())
        code.extend(VMWriter.write_arithmetic("not"))
        self._expect(TokenType.SYMBOL, ")")
        self._expect(TokenType.SYMBOL, "{")
        code.extend(VMWriter.write_if(label_2))
        code.extend(self._statements())
        code.extend(VMWriter.write_goto(label_1))
        code.extend(VMWriter.write_label(label_2))
        self._expect(TokenType.SYMBOL, "}")
        return code

    def _do_statement(self) -> VMCode:
        """Compile a do statement."""
        code = []
        self._expect(TokenType.KEYWORD, "do")
        code.extend(self._subroutine_call())
        self._expect(TokenType.SYMBOL, ";")
        code.extend(VMWriter.write_pop("temp", 0))  # void return value
        return code

    def _return_statement(self) -> VMCode:
        """Compile a return statement."""
        code = []
        self._expect(TokenType.KEYWORD, "return")
        with suppress(SyntaxError):
            code.extend(self._expression())
        self._expect(TokenType.SYMBOL, ";")
        return code

    def _subroutine_call(self) -> VMCode:
        """Compile a subroutine call."""
        code = []
        n_args = 0
        base_name = self._expect(TokenType.IDENTIFIER).value

        if self._token_stream.current != Token(TokenType.SYMBOL, "."):
            # own method
            fn_name = base_name
            base_name = self._class_name

            # inject reference to self as first argument
            n_args += 1
            code.extend(VMWriter.write_push("pointer", 0))
        elif base_name in self._symbol_table_class or base_name in self._symbol_table_subroutine:
            # method from instance variable
            self._token_stream.pop_current()
            fn_name = self._expect(TokenType.IDENTIFIER).value

            symbol_table = self._get_symbol_table(base_name)
            segment = symbol_table.get_segment(base_name)
            index = symbol_table.get_index(base_name)
            base_name = symbol_table.get_type(base_name)

            # inject reference to instance as first argument
            n_args += 1
            code.extend(VMWriter.write_push(segment, index))
        else:
            # function
            self._token_stream.pop_current()
            fn_name = self._expect(TokenType.IDENTIFIER).value

        expressions = self._expression_list()
        n_args += len(expressions)

        for expression in expressions:
            code.extend(expression)

        name = f"{base_name}.{fn_name}" if fn_name else base_name
        code.extend(VMWriter.write_call(name, n_args))
        return code

    def _expression(self) -> VMCode:
        """Compile an expression."""
        ops = ["+", "-", "*", "/", "&", "|", "<", ">", "="]
        op_to_vm = {
            "+": "add",
            "-": "sub",
            "*": "call Math.multiply 2",
            "/": "call Math.divide 2",
            "&": "and",
            "|": "or",
            "<": "lt",
            ">": "gt",
            "=": "eq",
        }
        terms = []
        term_1 = self._term()
        terms.extend(term_1)
        while True:
            try:
                op = self._expect(TokenType.SYMBOL, ops)
                term_2 = self._term()
                terms.extend(term_2)
                terms.append(op_to_vm[op.value])
            except SyntaxError:
                # no more operations
                break
        return terms

    def _term(self) -> VMCode:
        """Compile a term."""
        code = []

        if not self._token_stream.current:
            raise SyntaxError("Term cannot be empty.")

        match self._token_stream.current:
            case Token(TokenType.INTEGER_CONSTANT):
                code.extend(VMWriter.write_push("constant", self._token_stream.pop_current().value))
            case Token(TokenType.STRING_CONSTANT):
                string = self._token_stream.pop_current().value
                code.extend(VMWriter.write_push("constant", len(string)))
                code.extend(VMWriter.write_call("String.new", 1))
                for char in string:
                    code.extend(VMWriter.write_push("constant", ord(char)))
                    code.extend(VMWriter.write_call("String.appendChar", 2))
            case Token(TokenType.KEYWORD):
                match self._token_stream.pop_current().value:
                    case "true":
                        code.extend(VMWriter.write_push("constant", 1))
                        code.extend(VMWriter.write_arithmetic("neg"))
                    case "false" | "null":
                        code.extend(VMWriter.write_push("constant", 0))
                    case "this":
                        code.extend(VMWriter.write_push("pointer", 0))
                    case _:
                        raise SyntaxError(f"Unexpected keyword: {self._token_stream.current.value!r}")
            case Token(TokenType.IDENTIFIER):
                match self._token_stream.next:
                    case Token(TokenType.SYMBOL, "["):
                        code.extend(self._array())
                        code.extend(VMWriter.write_pop("pointer", 1))
                        code.extend(VMWriter.write_push("that", 0))
                    case Token(TokenType.SYMBOL, "(") | Token(TokenType.SYMBOL, "."):
                        code.extend(self._subroutine_call())
                    case _:
                        name = self._token_stream.pop_current().value
                        symbol_table = self._get_symbol_table(name)
                        index = symbol_table.get_index(name)
                        segment = symbol_table.get_segment(name)
                        code.extend(VMWriter.write_push(segment, index))
            case Token(TokenType.SYMBOL, "("):
                self._token_stream.pop_current()
                code.extend(self._expression())
                self._expect(TokenType.SYMBOL, ")")
            case Token(TokenType.SYMBOL, "-"):
                self._token_stream.pop_current()
                code.extend(self._term())
                code.extend(VMWriter.write_arithmetic("neg"))
            case Token(TokenType.SYMBOL, "~"):
                self._token_stream.pop_current()
                code.extend(self._term())
                code.extend(VMWriter.write_arithmetic("not"))
            case _:
                msg = f"Unexpected token for term: {self._token_stream.current.type}"
                raise SyntaxError(msg)
        return code

    def _array(self) -> VMCode:
        """Compile an array."""
        code = []
        name = self._expect(TokenType.IDENTIFIER).value
        symbol_table = self._get_symbol_table(name)
        index = symbol_table.get_index(name)
        segment = symbol_table.get_segment(name)
        code.extend(VMWriter.write_push(segment, index))

        self._expect(TokenType.SYMBOL, "[")
        code.extend(self._expression()),
        self._expect(TokenType.SYMBOL, "]")

        code.extend(VMWriter.write_arithmetic("add"))

        return code

    def _expression_list(self) -> list[VMCode]:
        """Compile an expression list (including paranthesis)."""
        self._expect(TokenType.SYMBOL, "(")
        expressions = []
        while True:
            try:
                expressions.append(self._expression())
            except SyntaxError:
                break  # no more expressions

            with suppress(SyntaxError):
                self._expect(TokenType.SYMBOL, ",")
        self._expect(TokenType.SYMBOL, ")")
        return expressions
