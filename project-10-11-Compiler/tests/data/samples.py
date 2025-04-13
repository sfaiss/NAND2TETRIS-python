from dataclasses import dataclass

from tokens import Token, TokenType


@dataclass
class Sample:
    code: str
    tokens: tuple[Token]


def class_tokens(
    name: str = "Main",
    class_var_dec: tuple[Token, ...] | None = None,
    subroutine_dec: tuple[Token, ...] | None = None,
) -> tuple[Token, ...]:
    tokens = [
        Token(TokenType.KEYWORD, "class"),
        Token(TokenType.IDENTIFIER, name),
        Token(TokenType.SYMBOL, "{"),
    ]
    if class_var_dec:
        tokens.extend(class_var_dec)
    if subroutine_dec:
        tokens.extend(subroutine_dec)
    tokens.append(Token(TokenType.SYMBOL, "}"))
    return tuple(tokens)


def class_var_dec_tokens(
    kind: str = "static",
    var_type: str = "int",
    names: list[str] = ["x"],
) -> tuple[Token, ...]:
    tokens = []
    tokens.append(Token(TokenType.KEYWORD, kind))
    if var_type in ("int", "boolean", "char"):
        tokens.append(Token(TokenType.KEYWORD, var_type))
    else:
        tokens.append(Token(TokenType.IDENTIFIER, var_type))
    for i, name in enumerate(names):
        if i > 0:
            tokens.append(Token(TokenType.SYMBOL, ","))
        tokens.append(Token(TokenType.IDENTIFIER, name))
    tokens.append(Token(TokenType.SYMBOL, ";"))
    return tuple(tokens)


def subroutine_dec_tokens(
    kind: str = "function",
    return_type: str = "void",
    name: str = "main",
    parameter_list: list[Token] | None = None,
    body: list[Token] | None = None,
) -> tuple[Token, ...]:
    tokens = []
    tokens.append(Token(TokenType.KEYWORD, kind))
    if return_type in ("void", "int", "boolean", "char"):
        tokens.append(Token(TokenType.KEYWORD, return_type))
    else:
        tokens.append(Token(TokenType.IDENTIFIER, return_type))
    tokens.append(Token(TokenType.IDENTIFIER, name))
    tokens.append(Token(TokenType.SYMBOL, "("))
    tokens.extend(parameter_list or [])
    tokens.append(Token(TokenType.SYMBOL, ")"))
    tokens.append(Token(TokenType.SYMBOL, "{"))
    tokens.extend(body or [])
    tokens.append(Token(TokenType.SYMBOL, "}"))
    return tuple(tokens)


MINIMALISTIC_CODE = Sample(
    code = """
        class Main {
            function void main() {
                return;
            }
        }
        """.strip(),
    tokens = class_tokens(
        subroutine_dec=subroutine_dec_tokens(
            body=[
                Token(TokenType.KEYWORD, "return"),
                Token(TokenType.SYMBOL, ";"),
            ]
        )
    )
)

SIMPLE_CODE = Sample(
    code = """
        function void main() {
            var int x;

            let x = 123;
            do Output.printString("Hello, world!");
            return;
        }
        """.strip(),
    tokens = subroutine_dec_tokens(
        body=(
            Token(TokenType.KEYWORD, "var"),
            Token(TokenType.KEYWORD, "int"),
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.SYMBOL, ";"),
            Token(TokenType.KEYWORD, "let"),
            Token(TokenType.IDENTIFIER, "x"),
            Token(TokenType.SYMBOL, "="),
            Token(TokenType.INTEGER_CONSTANT, "123"),
            Token(TokenType.SYMBOL, ";"),
            Token(TokenType.KEYWORD, "do"),
            Token(TokenType.IDENTIFIER, "Output"),
            Token(TokenType.SYMBOL, "."),
            Token(TokenType.IDENTIFIER, "printString"),
            Token(TokenType.SYMBOL, "("),
            Token(TokenType.STRING_CONSTANT, "Hello, world!"),
            Token(TokenType.SYMBOL, ")"),
            Token(TokenType.SYMBOL, ";"),
            Token(TokenType.KEYWORD, "return"),
            Token(TokenType.SYMBOL, ";"),
        )
    )
)
