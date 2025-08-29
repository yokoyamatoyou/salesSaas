from services.utils import escape_braces, mask_pii


def test_escape_braces():
    assert escape_braces('abc') == 'abc'
    assert escape_braces('{a}') == '{{a}}'
    assert escape_braces('a{b}c') == 'a{{b}}c'


def test_mask_pii():
    assert mask_pii('Contact user@example.com') == 'Contact ***'
    assert mask_pii('Call me at 090-1234-5678') == 'Call me at ***'
    assert mask_pii('John Doe logged in') == '*** logged in'
    assert mask_pii('山田太郎が参加') == '***が参加'
