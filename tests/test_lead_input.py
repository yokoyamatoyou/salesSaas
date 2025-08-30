import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))
from pages.lead_input import render_form


def test_skip_progression(monkeypatch):
    st.session_state.clear()
    st.session_state.lead_form_step = 1
    monkeypatch.setattr(st, "rerun", lambda: None)

    responses = iter([False, True, False])
    monkeypatch.setattr(st, "form_submit_button", lambda *args, **kwargs: next(responses))

    render_form()
    assert st.session_state.lead_form_step == 2


def test_final_submission_with_skip(monkeypatch):
    st.session_state.clear()
    st.session_state.lead_form_step = 2
    st.session_state.lead_form_data = {}
    monkeypatch.setattr(st, "rerun", lambda: None)

    responses = iter([False, False, True, False])
    monkeypatch.setattr(st, "form_submit_button", lambda *args, **kwargs: next(responses))

    submitted, data = render_form()
    assert submitted is True
    assert data == {}
