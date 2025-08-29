import os
import streamlit as st
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()


def main():
    st.set_page_config(
        page_title="営業特化SaaS",
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
        st.session_state.screen_width = 1000
    st.markdown(
        """
        <script>
        function updateScreenWidth() {
            const width = window.innerWidth;
            const input = window.parent.document.querySelector('input[id="screen_width"]');
            if (input) {
                input.value = width;
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
        updateScreenWidth();
        window.addEventListener('resize', updateScreenWidth);
        </script>
        <style>input#screen_width{display:none;}</style>
        """,
        unsafe_allow_html=True,
    )
    st.text_input("", key="screen_width")

    st.title("🏢 営業特化SaaS")
    st.markdown("---")

    is_mobile = st.session_state.get("screen_width", 1000) < 700

    # 環境変数の確認
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ OPENAI_API_KEYが設定されていません。一部機能が制限されます。")

    if is_mobile:
        # サイドバーの代わりにタブでページ切り替え
        st.checkbox(
            "クイックスタートモード",
            help="必要最小限の入力項目のみ表示",
            key="quickstart_mode",
        )
        tabs = st.tabs(
            [
                "事前アドバイス生成",
                "商談後ふりかえり解析",
                "アイスブレイク生成",
                "履歴",
                "設定・カスタマイズ",
                "検索機能の高度化",
            ]
        )
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
        st.sidebar.title("メニュー")
        if "page_select" not in st.session_state:
            st.session_state.page_select = "事前アドバイス生成"

        page = st.sidebar.selectbox(
            "ページを選択",
            [
                "事前アドバイス生成",
                "商談後ふりかえり解析",
                "アイスブレイク生成",
                "履歴",
                "設定・カスタマイズ",
                "検索機能の高度化",
            ],
            key="page_select",
        )

        st.sidebar.checkbox(
            "クイックスタートモード",
            help="必要最小限の入力項目のみ表示",
            key="quickstart_mode",
        )

        if page == "事前アドバイス生成":
            from pages.pre_advice import show_pre_advice_page

            show_pre_advice_page()
        elif page == "商談後ふりかえり解析":
            from pages.post_review import show_post_review_page

            show_post_review_page()
        elif page == "アイスブレイク生成":
            from pages.icebreaker import show_icebreaker_page

            show_icebreaker_page()
        elif page == "設定・カスタマイズ":
            from pages.settings import show_settings_page

            show_settings_page()
        elif page == "履歴":
            from pages.history import show_history_page

            show_history_page()
        elif page == "検索機能の高度化":
            from pages.search_enhancement import show_enhanced_search_page

            show_enhanced_search_page()


if __name__ == "__main__":
    main()

