import pytest

from data.samples import Sample, MINIMALISTIC_CODE, SIMPLE_CODE
from tokenizer import Token, TokenType, tokenize


@pytest.mark.parametrize("sample", [MINIMALISTIC_CODE, SIMPLE_CODE])
def test_should_tokenize_source_code(sample: Sample):
    assert tuple(tokenize(sample.code)) == sample.tokens


def test_should_raise_on_invalid_character():
    with pytest.raises(ValueError):
        tuple(tokenize("@"))


def test_should_not_confuse_keyword_withing_identifier():
    # contains keyword "do", but that's just a coincidence
    assert tuple(tokenize("double")) == (Token(TokenType.IDENTIFIER, "double"),)
