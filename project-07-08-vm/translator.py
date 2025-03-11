"""Translate VM code to Hack assembly code."""

import pathlib

from .code_writers import CodeWriter
from .parser import Parser


def translate(vm_path: str | pathlib.Path) -> str:
    """Translate VM code to Hack assembly code."""
    vm = pathlib.Path(vm_path)
    code_writer = CodeWriter()

    if vm.is_dir():
        translated = []
        translated.extend(code_writer._bootstrap())
        for vm_file in vm.glob("*.vm"):
            translated.extend(_translate_file(code_writer, Parser(vm_file)))
    else:
        translated = _translate_file(code_writer, Parser(vm))

    return "\n".join(translated)


def _translate_file(cw: CodeWriter, p: Parser) -> list[str]:
    """Translate a single VM program."""
    translated = []
    for command in p.commands:
        translated.extend(cw.write(command))
    return translated


if __name__ == "__main__":
    import pathlib
    import sys

    # first user provided argument is either a file or a directory of asm-files
    user_input = pathlib.Path(sys.argv[1])

    if not user_input.exists():
        raise FileNotFoundError(f"{user_input} not found")

    if user_input.is_dir():
        with open(user_input / (user_input.name + ".asm"), mode="w") as f:
            f.write(translate(user_input))
    else:
        with open(user_input.with_suffix(".asm"), mode="w") as f:
            f.write(translate(user_input))
