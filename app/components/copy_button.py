import json
import streamlit as st


def copy_button(text: str, *, key: str | None = None, label: str = "📋 コピー", use_container_width: bool = False) -> None:
    """Render a button that copies text to the clipboard using JavaScript."""
    if st.button(label, key=key, use_container_width=use_container_width):
        escaped = json.dumps(text)
        st.markdown(
            f"<script>navigator.clipboard.writeText({escaped});</script>",
            unsafe_allow_html=True,
        )
        st.success("✅ クリップボードにコピーしました")

