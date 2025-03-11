"""Parser for programs written in the VM language."""

import pathlib
import re

from vm_command import VMCommand


class Parser:
    """Read and parse VM commands from a file."""

    def __init__(self, path: str):
        self._filename = pathlib.Path(path).stem
        with open(path) as f:
            self._content = f.read()
        self.commands = self._parse()

    def _parse(self) -> tuple[VMCommand, ...]:
        """Parse full VM program into its lexical elements."""
        pattern = re.compile(
            r"""
                ^\s*         # optional whitespaces
                ([\w-]+      # command type
                \ ?          # optional space
                [\w.]+?      # optional first argument
                \ ?          # optional space
                (?:[\w]+)?)  # optional second argument
                \s*          # optional whitespaces
                (?://.*)?    # optional comment
                $            # end of line
            """,
            flags=re.MULTILINE | re.VERBOSE,
        )
        return tuple(self._convert(m) for m in pattern.findall(self._content))

    def _convert(self, command: str) -> VMCommand:
        """Build a VMCommand object from a tuple of strings."""
        vm_command = VMCommand.from_string(command)
        vm_command.origin = self._filename
        return vm_command
