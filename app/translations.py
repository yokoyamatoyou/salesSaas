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
        "sidebar_toggle_help": "サイドバーを表示/非表示",
        "tab_navigation_hint": "ページ切替は下のタブから行えます",
        "fill_later": "後で入力する",
        "later_help": "必須項目以外は後から編集できます",

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
        "tab_crm": "🔗 CRM連携",
        "language_setting": "言語設定",
        "language_setting_help": "アプリケーションの表示言語",
        "pre_advice_industry_label": "業界 *",
        "pre_advice_product_label": "商品・サービス *",
        "pre_advice_product_label_optional": "商品・サービス",
        "post_review_industry_label": "業界 *",
        "post_review_product_label": "商品・サービス *",
        "import_from_crm": "CRMから読み込む",
        "crm_section_title": "🔗 CRM連携",
        "crm_customer_id": "CRM顧客ID",
        "crm_import_success": "CRMデータを読み込みました",
        "crm_import_failed": "CRMデータの取得に失敗しました",
        "crm_enable": "CRM連携を有効化",
        "crm_enable_help": "CRMから顧客情報を読み込む機能を有効にします",
        "crm_api_key_missing": "CRM APIキーが設定されていません。環境変数CRM_API_KEYを設定してください。",
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
        "sidebar_toggle_help": "Show or hide sidebar",
        "tab_navigation_hint": "Use the tabs below to switch pages",
        "fill_later": "Fill later",
        "later_help": "Optional fields can be edited later",

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
        "tab_crm": "🔗 CRM Integration",
        "language_setting": "Language",
        "language_setting_help": "Display language of the application",
        "pre_advice_industry_label": "Industry *",
        "pre_advice_product_label": "Product/Service *",
        "pre_advice_product_label_optional": "Product/Service",
        "post_review_industry_label": "Industry *",
        "post_review_product_label": "Product/Service *",
        "import_from_crm": "Import from CRM",
        "crm_section_title": "🔗 CRM Integration",
        "crm_customer_id": "CRM Customer ID",
        "crm_import_success": "CRM data loaded",
        "crm_import_failed": "Failed to fetch CRM data",
        "crm_enable": "Enable CRM integration",
        "crm_enable_help": "Enable loading customer info from CRM",
        "crm_api_key_missing": "CRM API key not set. Please set CRM_API_KEY environment variable.",
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
