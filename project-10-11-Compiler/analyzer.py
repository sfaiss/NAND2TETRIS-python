"""Parse the semantics of the source code written in Jack language."""

import pathlib
import re
import sys
from collections.abc import Iterable
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent

from structural_element import StructuralElement
from token_parser import Parser
from tokenizer import tokenize
from tokens import Token, TokenStream


def remove_comments(jack_code: str) -> str:
    """Remove all comments from the source code."""
    line_comment =  r"\s*//.*?$"
    block_comment = r"\s*/\*.*?\*/"
    api_comment =   r"\s*/\*\*.*?\*/"

    return re.sub(
        pattern="|".join((line_comment, block_comment, api_comment)),
        repl="",
        string=jack_code,
        flags=re.DOTALL | re.MULTILINE,
    )


def create_token_tree(tokens: Iterable[Token]) -> ElementTree:
    """Create a formatted XML-tree containing token information."""
    tree = ElementTree()
    root = Element("tokens")
    root.text = "\n"
    root.tail = "\n"
    # this is a documented method, don't get startled by the leading underscore
    tree._setroot(root)  # type: ignore

    for token in tokens:
        element = SubElement(root, str(token.type))
        element.text = f" {token.value} "
        element.tail = "\n"

    return tree


def create_grammar_tree(grammar: StructuralElement) -> ElementTree:
    """Create a formatted XML-tree containing grammar information."""

    def _get_node(node: Token | StructuralElement) -> Element:
        if isinstance(node, Token):
            element = Element(str(node.type))
            element.text = f" {node.value} "
            element.tail = "\n"
            return element
        
        element = Element(str(node.type))
        if node.children:
            element.text = "\n"
        element.tail = "\n"

        for child in node.children:
            element.append(_get_node(child))

        return element

    root = _get_node(grammar)
    return ElementTree(root)


def analyze(jack_code: str) -> tuple[ElementTree, ElementTree]:
    """Build a XML-tree from Jack source code."""
    pure_code = remove_comments(jack_code)
    tokens = tuple(tokenize(pure_code))
    token_stream = TokenStream(tokens)
    parser = Parser(token_stream)
    grammar = parser.parse()
    return create_token_tree(tokens), create_grammar_tree(grammar)


def main(user_input: str) -> None:
    """Main entry point. Delegate user input to the analyzer."""
    # first user provided argument is either a file or a directory of asm-files
    path = pathlib.Path(user_input)

    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    if path.is_dir():
        jack_files = list(path.glob("*.jack"))
    else:
        jack_files = [path]

    for jack_file in jack_files:
        token_file = jack_file.parent / f"{jack_file.stem}T.xml"  # T for token
        grammar_file = jack_file.with_suffix(".xml")  # no suffix for grammar

        with open(jack_file) as f:
            jack_code = f.read()

        token_tree, grammar_tree = analyze(jack_code)
        token_tree.write(token_file)

        indent(grammar_tree, space="  ")
        grammar_tree.write(grammar_file)


if __name__ == "__main__":
    for jack_file in pathlib.Path(r"C:\Users\Simon\Desktop\nand2tetris-python\project-10-11-Compiler\tests\data").glob("**/*.jack"):
        main(jack_file)
    # main(r"project-10-11-Compiler\tests\data\10\ArrayTest\Main.jack")
    # main(sys.argv[1])
