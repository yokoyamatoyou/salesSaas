from __future__ import annotations

import re


def escape_braces(text: str) -> str:
    """Escape curly braces in the given text for safe formatting.

    This replaces ``{"`` with ``"{{"`` and ``"}"`` with ``"}}"`` so that
    user provided values containing braces do not interfere with string
    formatting templates.
    """
    if not isinstance(text, str):
        return text
    return text.replace("{", "{{").replace("}", "}}")


EMAIL_REGEX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_REGEX = re.compile(r"\+?\d[\d\-\s]{9,}\d")
NAME_REGEX = re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b|[\u4e00-\u9fff]{3,}")


def mask_pii(text: str) -> str:
    """Mask common personally identifiable information in the given text.

    This function replaces email addresses, phone numbers, and personal names
    with asterisks (``***``) to prevent accidental logging of sensitive data.
    """

    if not isinstance(text, str):
        text = str(text)

    text = EMAIL_REGEX.sub("***", text)
    text = PHONE_REGEX.sub("***", text)
    text = NAME_REGEX.sub("***", text)
    return text
