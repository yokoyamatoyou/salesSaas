import streamlit as st
from translations import t


def _update(src: str, dest: str) -> None:
    """セッションステートにフォーム入力を保存"""
    st.session_state.lead_form_data[dest] = st.session_state.get(src)



def render_form():
    """リード情報入力フォームを段階的に表示"""
    step_titles = ["基本情報", "詳細情報"]
    total_steps = len(step_titles)
    if "lead_form_step" not in st.session_state:
        st.session_state.lead_form_step = 1
    if "lead_form_data" not in st.session_state:
        st.session_state.lead_form_data = {}

    step = st.session_state.lead_form_step
    st.progress(step / total_steps)
    st.markdown(f"### {step_titles[step - 1]} ({step}/{total_steps})")

    submitted = False

    if step == 1:
        with st.form("lead_step1"):
            st.text_input("名前", key="lead_name", on_change=_update, args=("lead_name", "name"))
            st.text_input("メール", key="lead_email", on_change=_update, args=("lead_email", "email"))
            col1, col2, col3 = st.columns(3)
            with col1:
                later = st.form_submit_button(t("fill_later"), use_container_width=True)
            with col2:
                skip = st.form_submit_button(t("skip"), use_container_width=True)
            with col3:
                next_clicked = st.form_submit_button("次へ", type="primary", use_container_width=True)
        if later or skip or next_clicked:
            st.session_state.lead_form_step = 2
            st.rerun()

    elif step == 2:
        with st.form("lead_step2"):
            st.text_input("会社", key="lead_company", on_change=_update, args=("lead_company", "company"))
            st.text_area("メモ", key="lead_notes", on_change=_update, args=("lead_notes", "notes"))
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                back_clicked = st.form_submit_button("戻る")
            with col2:
                later = st.form_submit_button(t("fill_later"), use_container_width=True)
            with col3:
                skip = st.form_submit_button(t("skip"), use_container_width=True)
            with col4:
                submit = st.form_submit_button("保存", type="primary", use_container_width=True)
        if back_clicked:
            st.session_state.lead_form_step = 1
            st.rerun()
        if later or skip or submit:
            submitted = True

    return submitted, st.session_state.lead_form_data
