from __future__ import annotations


def escape_braces(text: str) -> str:
    """Escape curly braces in the given text for safe formatting.

    This replaces ``{"`` with ``"{{"`` and ``"}"`` with ``"}}"`` so that
    user provided values containing braces do not interfere with string
    formatting templates.
    """
    if not isinstance(text, str):
        return text
    return text.replace("{", "{{").replace("}", "}}")
