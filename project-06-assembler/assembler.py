"""Convert Hack assembly code to machine code."""

from __future__ import annotations

import re
from abc import ABC
from dataclasses import dataclass, field

import lookup


class Instruction(ABC):
    """Generic Instruction class in the Hack assembly language."""


@dataclass
class AInstruction(Instruction):
    """Represent an A-instruction in the Hack assembly language."""
    opcode: int = field(default=0, init=False)
    address: int

    @classmethod
    def from_symbol(cls, symbol: str) -> AInstruction:
        """Create an A-instruction from a symbol."""
        return cls(int(symbol[1:]))

    def __str__(self):
          """Return the binary representation of the A-instruction."""
          return f"{self.opcode}{self.address:015b}"


@dataclass
class CInstruction(Instruction):
    """Represent a C-instruction in the Hack assembly language."""
    opcode: int = field(default=1, init=False)
    stuffing: int = field(default=0b11, init=False)
    a: int
    comp: int
    dest: int
    jump: int

    @classmethod
    def from_symbol(cls, symbol: str) -> CInstruction:
        """Create a C-instruction from a symbol."""
        if m := re.match(r"^(?:(.+)=)?(.+?)(?:;(.+))?$", symbol):
            d, c, j = m.groups()
        else:
            raise ValueError(f"Invalid C-instruction: {symbol}")

        if d:
            dest = 0b100 * ("A" in d) + 0b010 * ("D" in d) + 0b001 * ("M" in d)

        return cls(
            0 if "M" not in c else 1,
            lookup.mnemonic[c],
            dest if d else 0,
            lookup.jump[j] if j else 0,
        )

    def __str__(self):
        """Return the binary representation of the C-instruction."""
        o = self.opcode
        s = self.stuffing
        a = self.a
        c = self.comp
        d = self.dest
        j = self.jump
        return f"{o}{s:b}{a}{c:06b}{d:03b}{j:03b}"


def extract_pseudo_code(program: str) -> list[str]:
    """Remove whitespace and comments from the program."""
    return re.findall(r"^\s*([^\s/]+).*?$", program, flags=re.MULTILINE)


def resolve_labels(
    pseudo_code: list[str],
    symbol_table: dict[str, int],
) -> list[str]:
    """Remove labels from the program and update the symbol table."""
    pure_code: list[str] = []
    line_number = 0
    for symbol in pseudo_code:
        if symbol.startswith("("):
            symbol_table[symbol[1:-1]] = line_number
        else:
            pure_code.append(symbol)
            line_number += 1
    return pure_code


def resolve_variables(
    pure_code: list[str],
    symbol_table: dict[str, int],
) -> None:
    """Replace variables with their memory addresses."""
    address_offset = 16
    for symbol in pure_code:
        if not symbol.startswith("@"):
            continue
        if symbol[1:].isnumeric():
            continue
        if symbol[1:] in symbol_table:
            continue
        symbol_table[symbol[1:]] = address_offset
        address_offset += 1


def preprocess(program: str, symbol_table: dict[str, int]) -> list[str]:
    """Prepare the program for assembly."""
    pseudo_code = extract_pseudo_code(program)
    pure_code = resolve_labels(pseudo_code, symbol_table)
    resolve_variables(pure_code, symbol_table)
    return pure_code


def assemble(program: str) -> str:
    """Convert Hack assembly code to machine code."""
    assembled: list[str] = []
    symbol_table = lookup.predefined.copy()
    pure_code = preprocess(program, symbol_table)
    token: Instruction

    for symbol in pure_code:
        if symbol.startswith("@") and symbol[1:].isnumeric():
            token = AInstruction.from_symbol(symbol)
        elif symbol.startswith("@"):
            token = AInstruction(symbol_table[symbol[1:]])
        else:
            token = CInstruction.from_symbol(symbol)
        assembled.append(str(token))
    return "\n".join(assembled)


if __name__ == "__main__":
    import pathlib
    import sys

    # first user provided argument is either a file or a directory of asm-files
    user_input = pathlib.Path(sys.argv[1])

    if not user_input.exists():
        raise FileNotFoundError(f"{user_input} not found")

    if user_input.is_dir():
        asm_files = list(user_input.glob("*.asm"))
    else:
        asm_files = [user_input]

    for asm_file in asm_files:
        hack_file = asm_file.with_suffix(".hack")

        with asm_file.open() as f_in, hack_file.open(mode="w") as f_out:
            f_out.write(assemble(f_in.read()))
