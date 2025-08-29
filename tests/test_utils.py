from services.utils import escape_braces


def test_escape_braces():
    assert escape_braces('abc') == 'abc'
    assert escape_braces('{a}') == '{{a}}'
    assert escape_braces('a{b}c') == 'a{{b}}c'
