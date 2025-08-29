import streamlit as st
from services.settings_manager import SettingsManager

TRANSLATIONS = {
    "ja": {
        "app_title": "🏢 営業特化SaaS",
        "menu": "メニュー",
        "select_page": "ページを選択",
        "pre_advice": "事前アドバイス生成",
        "post_review": "商談後ふりかえり解析",
        "icebreaker": "アイスブレイク生成",
        "history": "履歴",
        "settings": "設定・カスタマイズ",
        "search_enhancement": "検索機能の高度化",
        "quickstart_mode": "クイックスタートモード",
        "quickstart_help": "必要最小限の入力項目のみ表示",

        "pre_advice_header": "事前アドバイス生成",
        "pre_advice_desc": "商談前の準備をサポートします。営業タイプ、業界、商品情報を入力してください。",
        "input_form_tab": "入力フォーム",
        "icebreaker_tab": "アイスブレイク",

        "post_review_header": "🔍 商談後ふりかえり解析",
        "post_review_desc": "商談後の議事録やメモを分析し、次回への改善点とアクションプランを生成します。",

        "icebreaker_header": "🎯 アイスブレイク生成",
        "icebreaker_desc": "営業タイプと業界に応じた、自然で親しみやすいアイスブレイクを生成します。",

        "history_header": "履歴（セッション一覧）",
        "history_desc": "保存された生成結果を参照・再利用できます。",
        "history_export_json": "JSONでダウンロード",
        "history_export_csv": "CSVでダウンロード",

        "search_enhancement_title": "🔍 検索機能の高度化",
        "search_enhancement_desc": "LLMの知識を活用して検索結果の品質向上とスコアリングアルゴリズムを改善します",

        "settings_page_title": "⚙️ 設定・カスタマイズ",
        "settings_page_desc": "アプリケーションの動作をカスタマイズできます。",
        "tab_llm": "🤖 LLM設定",
        "tab_search": "🔍 検索設定",
        "tab_ui": "🎨 UI設定",
        "tab_data": "💾 データ設定",
        "tab_import_export": "📁 インポート/エクスポート",
        "language_setting": "言語設定",
        "language_setting_help": "アプリケーションの表示言語",
    },
    "en": {
        "app_title": "🏢 Sales SaaS",
        "menu": "Menu",
        "select_page": "Select Page",
        "pre_advice": "Pre-Advice",
        "post_review": "Post Review",
        "icebreaker": "Icebreaker",
        "history": "History",
        "settings": "Settings & Customization",
        "search_enhancement": "Advanced Search",
        "quickstart_mode": "Quick Start Mode",
        "quickstart_help": "Display only essential inputs",

        "pre_advice_header": "Pre-Advice",
        "pre_advice_desc": "Support your preparation before meetings. Provide sales type, industry and product info.",
        "input_form_tab": "Input Form",
        "icebreaker_tab": "Icebreaker",

        "post_review_header": "🔍 Post Review Analysis",
        "post_review_desc": "Analyze meeting notes to generate improvements and next actions.",

        "icebreaker_header": "🎯 Icebreaker Generator",
        "icebreaker_desc": "Generate natural icebreakers based on sales type and industry.",

        "history_header": "History (Sessions)",
        "history_desc": "Browse and reuse saved outputs.",
        "history_export_json": "Download JSON",
        "history_export_csv": "Download CSV",

        "search_enhancement_title": "🔍 Search Enhancement",
        "search_enhancement_desc": "Leverage LLM knowledge to improve search quality and scoring.",

        "settings_page_title": "⚙️ Settings & Customization",
        "settings_page_desc": "Customize how the application works.",
        "tab_llm": "🤖 LLM Settings",
        "tab_search": "🔍 Search Settings",
        "tab_ui": "🎨 UI Settings",
        "tab_data": "💾 Data Settings",
        "tab_import_export": "📁 Import/Export",
        "language_setting": "Language",
        "language_setting_help": "Display language of the application",
    },
}


def get_language() -> str:
    if "language" in st.session_state:
        return st.session_state["language"]
    manager = SettingsManager()
    lang = manager.load_settings().language
    st.session_state["language"] = lang
    return lang


def t(key: str) -> str:
    lang = get_language()
    return TRANSLATIONS.get(lang, TRANSLATIONS["ja"]).get(key, key)
