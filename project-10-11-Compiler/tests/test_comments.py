from analyzer import remove_comments


def test_should_remove_line_comments():
    code = """
foo  // This is the first line comment
bar  // Here is another line comment
// without code
    """.strip()
    assert remove_comments(code) == "foo\nbar"

def test_should_remove_block_comments():
    code = """
foo
/* Block
comment
*/
bar
    """.strip()
    assert remove_comments(code) == "foo\nbar"

def test_should_remove_api_comments():
    code = """
foo
/** API comment */
bar
    """.strip()
    assert remove_comments(code) == "foo\nbar"
