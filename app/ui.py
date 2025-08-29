import os
import streamlit as st
from dotenv import load_dotenv
from streamlit_javascript import st_javascript
from translations import t

# 環境変数を読み込み
load_dotenv()


def main():
    st.set_page_config(
        page_title=t("app_title"),
        page_icon="🏢",
        layout="wide",
    )

    # モバイルUI最適化（レスポンシブCSS + サイドバー非表示）
    st.markdown(
        """
        <style>
        @media (max-width: 640px) {
          .block-container { padding-left: 0.6rem; padding-right: 0.6rem; }
          .stButton>button { width: 100%; }
          .stTextInput>div>div>input, textarea, select { font-size: 16px; }
          section[data-testid="stSidebar"] { display: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 画面幅を取得してセッションステートに保存
    if "screen_width" not in st.session_state:
        width = st_javascript("return window.innerWidth;")
        if width is None:
            params = st.experimental_get_query_params()
            try:
                width = int(params.get("width", [1000])[0])
            except (ValueError, TypeError):
                width = 1000
        st.session_state.screen_width = width

    st.title(t("app_title"))
    st.markdown("---")

    is_mobile = st.session_state.get("screen_width", 1000) < 700

    # 環境変数の確認
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ OPENAI_API_KEYが設定されていません。一部機能が制限されます。")

    if is_mobile:
        # サイドバーの代わりにタブでページ切り替え
        st.checkbox(
            t("quickstart_mode"),
            help=t("quickstart_help"),
            key="quickstart_mode",
        )
        page_keys = [
            "pre_advice",
            "post_review",
            "icebreaker",
            "history",
            "settings",
            "search_enhancement",
        ]
        page_labels = {k: t(k) for k in page_keys}
        tabs = st.tabs([page_labels[k] for k in page_keys])
        with tabs[0]:
            from pages.pre_advice import show_pre_advice_page

            show_pre_advice_page()
        with tabs[1]:
            from pages.post_review import show_post_review_page

            show_post_review_page()
        with tabs[2]:
            from pages.icebreaker import show_icebreaker_page

            show_icebreaker_page()
        with tabs[3]:
            from pages.history import show_history_page

            show_history_page()
        with tabs[4]:
            from pages.settings import show_settings_page

            show_settings_page()
        with tabs[5]:
            from pages.search_enhancement import show_enhanced_search_page

            show_enhanced_search_page()
    else:
        # デスクトップでは従来どおりサイドバーを使用
        st.sidebar.title(t("menu"))
        if "page_select" not in st.session_state:
            st.session_state.page_select = "pre_advice"

        page_keys = [
            "pre_advice",
            "post_review",
            "icebreaker",
            "history",
            "settings",
            "search_enhancement",
        ]
        page_labels = {k: t(k) for k in page_keys}

        page = st.sidebar.selectbox(
            t("select_page"),
            options=page_keys,
            format_func=lambda x: page_labels[x],
            key="page_select",
        )

        st.sidebar.checkbox(
            t("quickstart_mode"),
            help=t("quickstart_help"),
            key="quickstart_mode",
        )

        if page == "pre_advice":
            from pages.pre_advice import show_pre_advice_page

            show_pre_advice_page()
        elif page == "post_review":
            from pages.post_review import show_post_review_page

            show_post_review_page()
        elif page == "icebreaker":
            from pages.icebreaker import show_icebreaker_page

            show_icebreaker_page()
        elif page == "settings":
            from pages.settings import show_settings_page

            show_settings_page()
        elif page == "history":
            from pages.history import show_history_page

            show_history_page()
        elif page == "search_enhancement":
            from pages.search_enhancement import show_enhanced_search_page

            show_enhanced_search_page()


if __name__ == "__main__":
    main()

