import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))
from components.copy_button import copy_button

def test_copy_button_renders(monkeypatch):
    called = {}
    monkeypatch.setattr(st, "button", lambda *args, **kwargs: True)
    monkeypatch.setattr(st, "markdown", lambda content, **kwargs: called.setdefault("content", content))
    messages = []
    monkeypatch.setattr(st, "success", lambda msg: messages.append(msg))

    copy_button("hello", key="test")

    assert "navigator.clipboard.writeText" in called["content"]
    assert any("コピー" in m for m in messages)
