from xml.etree.ElementTree import ElementTree

from pytest_mock import MockerFixture

from analyzer import analyze
from tokens import Token, TokenStream, TokenType


def test_should_return_elementtrees():
    trees = analyze("")
    assert len(trees) == 2
    for tree in trees:
        assert isinstance(tree, ElementTree)


def test_should_strip_comments_before_tokenizing(mocker: MockerFixture):
    code_1 = "code with comments"
    code_2 = "code without comments"
    mocked_remove_comments = mocker.patch("analyzer.remove_comments", return_value=code_2)
    mocked_tokenize = mocker.patch("analyzer.tokenize")

    analyze(code_1)

    mocked_remove_comments.assert_called_once_with(code_1)
    mocked_tokenize.assert_called_once_with(code_2)


def test_should_tokenize_before_parsing(mocker: MockerFixture):
    code = "return"
    tokens = (Token(TokenType.KEYWORD, "return"),)
    token_generator = (token for token in tokens)
    mocked_tokenize = mocker.patch("analyzer.tokenize", return_value=token_generator)
    mocked_token_stream = mocker.patch("analyzer.TokenStream", side_effect=lambda *args, **kwargs: TokenStream(*args, **kwargs))
    mocked_parse = mocker.patch("analyzer.Parser.parse")

    analyze(code)

    mocked_tokenize.assert_called_once_with(code)
    mocked_token_stream.assert_called_once_with(tokens)  # generator should be converted to tuple
    mocked_parse.assert_called_once()
