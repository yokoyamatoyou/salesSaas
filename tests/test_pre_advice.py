import sys
from pathlib import Path
import streamlit as st
sys.path.append(str(Path(__file__).resolve().parents[1] / "app"))
from pages.pre_advice import render_pre_advice_form
from core.models import SalesType


def test_step_progression(monkeypatch):
    st.session_state.clear()
    st.session_state.pre_form_step = 1
    monkeypatch.setattr(st, "rerun", lambda: None)

    def fake_submit(label, **kwargs):
        return True

    monkeypatch.setattr(st, "form_submit_button", fake_submit)
    render_pre_advice_form()
    assert st.session_state.pre_form_step == 2


def test_final_submission(monkeypatch):
    st.session_state.clear()
    st.session_state.pre_form_step = 3
    st.session_state.sales_type_select = SalesType.HUNTER
    st.session_state.industry_input = "IT"
    st.session_state.product_input = "SaaS"
    st.session_state.description_text = "desc"
    st.session_state.competitor_text = "comp"
    st.session_state.stage_select = "初期接触"
    st.session_state.purpose_input = "新規顧客獲得"
    st.session_state.constraints_input = "予算"

    def fake_submit(label, **kwargs):
        return label == "🚀 アドバイスを生成"

    monkeypatch.setattr(st, "form_submit_button", fake_submit)
    submitted, data = render_pre_advice_form()
    assert submitted is True
    assert data["industry"] == "IT"

