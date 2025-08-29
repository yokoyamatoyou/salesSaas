import json
from datetime import datetime

import streamlit as st

from components.copy_button import copy_button
from components.sales_type import get_sales_type_emoji
from core.models import SalesInput, SalesType
from core.validation import (
    validate_industry,
    validate_product,
    validate_purpose,
    validate_sales_input,
)
from services.icebreaker import IcebreakerService
from services.pre_advisor import PreAdvisorService
from services.storage_service import get_storage_provider


def update_form_data(src_key: str, dest_key: str) -> None:
    """セッションに入力値を保存"""
    st.session_state.pre_advice_form_data[dest_key] = st.session_state.get(src_key)


def render_pre_advice_form():
    """事前アドバイス入力フォームを段階的に表示"""
    total_steps = 3
    if "pre_form_step" not in st.session_state:
        st.session_state.pre_form_step = 1
    if "pre_advice_form_data" not in st.session_state:
        st.session_state.pre_advice_form_data = {}

    step = st.session_state.pre_form_step
    st.progress(step / total_steps)
    st.markdown(f"### ステップ {step}/{total_steps}")

    submitted = False

    if step == 1:
        with st.form("pre_advice_step1"):
            st.selectbox(
                "営業タイプ *",
                options=list(SalesType),
                format_func=lambda x: f"{x.value} ({get_sales_type_emoji(x)})",
                help="営業スタイルを選択してください",
                key="sales_type_select",
                on_change=update_form_data,
                args=("sales_type_select", "sales_type"),
            )

            industry = st.text_input(
                "業界 *",
                placeholder="例: IT、製造業、金融業",
                help="対象となる業界を入力してください（2文字以上）",
                key="industry_input",
                on_change=update_form_data,
                args=("industry_input", "industry"),
            )

            if industry:
                industry_errors = validate_industry(industry)
                if industry_errors:
                    for error in industry_errors:
                        st.error(f"⚠️ {error}")
                else:
                    st.success("✅ 業界名が有効です")

            product = st.text_input(
                "商品・サービス *",
                placeholder="例: SaaS、コンサルティング",
                help="提供する商品・サービスを入力してください（2文字以上）",
                key="product_input",
                on_change=update_form_data,
                args=("product_input", "product"),
            )

            if product:
                product_errors = validate_product(product)
                if product_errors:
                    for error in product_errors:
                        st.error(f"⚠️ {error}")
                else:
                    st.success("✅ 商品名が有効です")

            next_clicked = st.form_submit_button(
                "次へ", type="primary", use_container_width=True
            )

        if next_clicked:
            st.session_state.pre_form_step = 2
            st.rerun()

    elif step == 2:
        with st.form("pre_advice_step2"):
            description_type = st.radio(
                "説明の入力方法",
                ["テキスト", "URL"],
                help="商品・サービスの説明をテキストで入力するか、URLで指定するかを選択してください",
                key="description_type",
                on_change=update_form_data,
                args=("description_type", "description_type"),
            )
            if description_type == "テキスト":
                st.session_state["description_url"] = None
                st.session_state.pre_advice_form_data["description_url"] = None
                st.text_area(
                    "説明",
                    placeholder="商品・サービスの詳細説明",
                    help="商品・サービスの特徴や価値を詳しく説明してください",
                    key="description_text",
                    on_change=update_form_data,
                    args=("description_text", "description"),
                )
            else:
                st.session_state["description_text"] = None
                st.session_state.pre_advice_form_data["description"] = None
                st.text_input(
                    "説明URL",
                    placeholder="https://example.com",
                    help="商品・サービスの説明が記載されているWebページのURLを入力してください",
                    key="description_url",
                    on_change=update_form_data,
                    args=("description_url", "description_url"),
                )

            competitor_type = st.radio(
                "競合の入力方法",
                ["テキスト", "URL"],
                help="競合情報をテキストで入力するか、URLで指定するかを選択してください",
                key="competitor_type",
                on_change=update_form_data,
                args=("competitor_type", "competitor_type"),
            )
            if competitor_type == "テキスト":
                st.session_state["competitor_url"] = None
                st.session_state.pre_advice_form_data["competitor_url"] = None
                st.text_input(
                    "競合",
                    placeholder="例: 競合A、競合B",
                    help="主要な競合企業やサービスを入力してください",
                    key="competitor_text",
                    on_change=update_form_data,
                    args=("competitor_text", "competitor"),
                )
            else:
                st.session_state["competitor_text"] = None
                st.session_state.pre_advice_form_data["competitor"] = None
                st.text_input(
                    "競合URL",
                    placeholder="https://competitor.com",
                    help="競合情報が記載されているWebページのURLを入力してください",
                    key="competitor_url",
                    on_change=update_form_data,
                    args=("competitor_url", "competitor_url"),
                )

            is_mobile = st.session_state.get("screen_width", 1000) < 600
            if is_mobile:
                back_clicked = st.form_submit_button(
                    "戻る", use_container_width=True
                )
                next_clicked = st.form_submit_button(
                    "次へ", type="primary", use_container_width=True
                )
            else:
                back_col, next_col = st.columns(2)
                with back_col:
                    back_clicked = st.form_submit_button(
                        "戻る", use_container_width=True
                    )
                with next_col:
                    next_clicked = st.form_submit_button(
                        "次へ", type="primary", use_container_width=True
                    )

        if back_clicked:
            st.session_state.pre_form_step = 1
            st.rerun()
        elif next_clicked:
            st.session_state.pre_form_step = 3
            st.rerun()

    else:  # step == 3
        with st.form("pre_advice_step3"):
            st.selectbox(
                "商談ステージ *",
                ["初期接触", "ニーズ発掘", "提案", "商談", "クロージング"],
                help="現在の商談の進行段階を選択してください",
                key="stage_select",
                on_change=update_form_data,
                args=("stage_select", "stage"),
            )

            purpose = st.text_input(
                "目的 *",
                placeholder="例: 新規顧客獲得、既存顧客拡大",
                help="この商談の目的を具体的に入力してください（5文字以上）",
                key="purpose_input",
                on_change=update_form_data,
                args=("purpose_input", "purpose"),
            )

            if purpose:
                purpose_errors = validate_purpose(purpose)
                if purpose_errors:
                    for error in purpose_errors:
                        st.error(f"⚠️ {error}")
                else:
                    st.success("✅ 目的が有効です")

            st.text_area(
                "制約",
                placeholder="例: 予算制限、期間制限、技術制約（改行で区切って入力）",
                help="商談や提案における制約事項があれば入力してください（各制約は3文字以上）",
                key="constraints_input",
                on_change=update_form_data,
                args=("constraints_input", "constraints_input"),
            )

            is_mobile = st.session_state.get("screen_width", 1000) < 600
            if is_mobile:
                back_clicked = st.form_submit_button(
                    "戻る", use_container_width=True
                )
                submitted = st.form_submit_button(
                    "🚀 アドバイスを生成",
                    type="primary",
                    use_container_width=True,
                )
            else:
                back_col, submit_col = st.columns(2)
                with back_col:
                    back_clicked = st.form_submit_button(
                        "戻る", use_container_width=True
                    )
                with submit_col:
                    submitted = st.form_submit_button(
                        "🚀 アドバイスを生成",
                        type="primary",
                        use_container_width=True,
                    )

        if back_clicked:
            st.session_state.pre_form_step = 2
            st.rerun()

    form_data = {
        "sales_type": st.session_state.pre_advice_form_data.get("sales_type")
        or st.session_state.get("sales_type_select"),
        "industry": st.session_state.pre_advice_form_data.get("industry")
        or st.session_state.get("industry_input"),
        "product": st.session_state.pre_advice_form_data.get("product")
        or st.session_state.get("product_input"),
        "description": st.session_state.pre_advice_form_data.get("description")
        or st.session_state.get("description_text"),
        "description_url": st.session_state.pre_advice_form_data.get("description_url")
        or st.session_state.get("description_url"),
        "competitor": st.session_state.pre_advice_form_data.get("competitor")
        or st.session_state.get("competitor_text"),
        "competitor_url": st.session_state.pre_advice_form_data.get("competitor_url")
        or st.session_state.get("competitor_url"),
        "stage": st.session_state.pre_advice_form_data.get("stage")
        or st.session_state.get("stage_select"),
        "purpose": st.session_state.pre_advice_form_data.get("purpose")
        or st.session_state.get("purpose_input"),
        "constraints_input": st.session_state.pre_advice_form_data.get(
            "constraints_input"
        )
        or st.session_state.get("constraints_input"),
    }
    return submitted, form_data


def render_icebreaker_section():
    """アイスブレイク生成セクションを表示"""
    st.markdown("---")
    st.markdown("### ❄️ アイスブレイク生成（任意）")

    if st.session_state.get("screen_width", 1000) < 800:
        ib_col1, ib_col2, ib_col3 = st.columns([1, 1, 1])
    else:
        ib_col1, ib_col2, ib_col3 = st.columns([2, 1, 1])

    with ib_col1:
        st.text_input(
            "会社ヒント",
            placeholder="例: 〇〇グループ、最近M&Aあり、採用強化中 など",
            help="相手企業に関するヒントがあれば入力してください",
            key="company_hint_input",
            on_change=update_form_data,
            args=("company_hint_input", "company_hint"),
        )
    with ib_col2:
        st.checkbox(
            "業界ニュースを使用",
            value=True,
            key="use_news_checkbox",
            on_change=update_form_data,
            args=("use_news_checkbox", "use_news_checkbox"),
        )
    with ib_col3:
        generate_icebreak = st.button(
            "❄️ アイスブレイクを生成", use_container_width=True, type="primary"
        )

    if "icebreakers" not in st.session_state:
        st.session_state.icebreakers = []
    if "selected_icebreaker" not in st.session_state:
        st.session_state.selected_icebreaker = None

    sales_type_val = st.session_state.pre_advice_form_data.get("sales_type")
    industry_val = st.session_state.pre_advice_form_data.get("industry")

    if sales_type_val and industry_val and generate_icebreak:
        try:
            from services.settings_manager import SettingsManager

            settings_manager = SettingsManager()
            ice_service = IcebreakerService(settings_manager)
            with st.spinner("❄️ アイスブレイク生成中..."):
                st.session_state.icebreakers = ice_service.generate_icebreakers(
                    sales_type=sales_type_val,
                    industry=industry_val,
                    company_hint=st.session_state.pre_advice_form_data.get("company_hint")
                    or None,
                    search_enabled=st.session_state.pre_advice_form_data.get(
                        "use_news_checkbox", True
                    ),
                )
            st.success("✅ アイスブレイクを生成しました！")
            st.session_state.icebreak_last_news = getattr(
                ice_service, "last_news_items", []
            )
        except Exception as e:
            st.warning(
                f"アイスブレイク生成に失敗しました（フォールバックを表示）: {e}"
            )
            try:
                ice_service = IcebreakerService(None)
                st.session_state.icebreakers = ice_service._generate_fallback_icebreakers(
                    sales_type=sales_type_val,
                    industry=industry_val,
                    tone=ice_service._get_tone_for_type(sales_type_val),
                )
            except Exception:
                st.session_state.icebreakers = []

    if st.session_state.icebreakers:
        st.markdown("#### 🎯 アイスブレイク候補")
        for idx, line in enumerate(st.session_state.icebreakers, 1):
            with st.container():
                if st.session_state.selected_icebreaker == line:
                    st.markdown(
                        f"""
                    <div style="
                        border: 2px solid #00ff88;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 0;
                        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    ">
                        <h4 style="margin: 0 0 10px 0; color: #0369a1;">🎯 選択中: {line}</h4>
                        <p style="margin: 0; color: #0c4a6e;">このアイスブレイクが選択されています</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                    <div style="
                        border: 1px solid #e5e7eb;
                        border-radius: 10px;
                        padding: 15px;
                        margin: 10px 0;
                        background: white;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    ">
                        <h4 style="margin: 0 0 10px 0; color: #374151;">{idx}. {line}</h4>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                col1, col2, col3 = st.columns([1, 1, 1])

                with col1:
                    if st.button(
                        f"🎯 選択",
                        key=f"select_{idx}",
                        use_container_width=True,
                        type="primary"
                        if st.session_state.selected_icebreaker == line
                        else "secondary",
                    ):
                        st.session_state.selected_icebreaker = line
                        st.rerun()

                with col2:
                    copy_button(line, key=f"copy_{idx}", use_container_width=True)

                with col3:
                    if st.button(
                        f"👁️ 詳細",
                        key=f"detail_{idx}",
                        use_container_width=True,
                    ):
                        st.info(f"**アイスブレイク詳細：**\n\n{line}")

                st.markdown("---")

        if st.session_state.selected_icebreaker:
            st.markdown("### ❄️ 選択中のアイスブレイク")
            st.markdown(
                f"""
            <div style="
                border: 3px solid #00ff88;
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                box-shadow: 0 8px 16px rgba(0, 255, 136, 0.2);
            ">
                <h3 style="margin: 0 0 15px 0; color: #166534; text-align: center;">🎯 選択済みアイスブレイク</h3>
                <p style="margin: 0; color: #166534; line-height: 1.6;">
                    {st.session_state.selected_icebreaker}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )
            copy_button(
                st.session_state.selected_icebreaker,
                key="selected_icebreaker_copy",
                use_container_width=True,
            )


def render_save_section(sales_input: SalesInput, advice: dict):
    """結果保存ボタンと処理"""
    if st.button("💾 生成結果を保存", use_container_width=False):
        try:
            session_id = save_pre_advice(
                sales_input=sales_input,
                advice=advice,
                selected_icebreaker=st.session_state.get("selected_icebreaker"),
            )
            st.session_state.pre_advice_session_id = session_id

            st.success("✅ 結果を保存しました！")

            st.markdown("---")
            st.markdown(
                """
                <div style="
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    padding: 25px;
                    border-radius: 15px;
                    margin: 20px 0;
                    text-align: center;
                    color: white;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                ">
                    <h3 style="margin: 0; color: white; font-size: 1.5em;">💾 保存完了</h3>
                    <p style="margin: 15px 0; opacity: 0.9; font-size: 1.1em;">セッションが正常に保存されました</p>
                    <div style="
                        background: rgba(255, 255, 255, 0.2);
                        padding: 15px;
                        border-radius: 10px;
                        margin: 15px 0;
                        font-family: monospace;
                        font-size: 1.2em;
                        letter-spacing: 1px;
                    ">
                        <strong>セッションID:</strong> {session_id}
                    </div>
                    <p style="margin: 10px 0 0 0; opacity: 0.8; font-size: 0.9em;">
                        📁 保存場所: data/sessions/{session_id}.json
                    </p>
                </div>
                """.format(session_id=session_id),
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button(
                    "📚 履歴ページで確認", key="view_history", use_container_width=True
                ):
                    st.switch_page("pages/history.py")
            with col2:
                if st.button(
                    "🔄 新しいアドバイスを生成", key="new_advice", use_container_width=True
                ):
                    st.session_state.pre_advice_form_data = {}
                    st.session_state.pop("pre_advice_session_id", None)
                    st.rerun()
            with col3:
                if st.button(
                    "📥 JSONダウンロード", key="download_json", use_container_width=True
                ):
                    download_data = {
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "type": "pre_advice",
                        "input": sales_input.dict(),
                        "output": {
                            "advice": advice,
                            "selected_icebreaker": st.session_state.get(
                                "selected_icebreaker"
                            ),
                        },
                    }
                    json_str = json.dumps(download_data, ensure_ascii=False, indent=2)
                    st.download_button(
                        label="📥 ダウンロード開始",
                        data=json_str,
                        file_name=f"pre_advice_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_button",
                        use_container_width=True,
                    )

            st.info(
                "💡 **次のステップ**: 履歴ページで保存されたセッションを確認したり、新しいアドバイスを生成したりできます。"
            )
        except Exception as e:
            st.error(f"❌ 保存に失敗しました: {str(e)}")
            st.info(
                "しばらく時間をおいて再度お試しください。問題が続く場合は管理者にお問い合わせください。"
            )


def show_pre_advice_page():
    """事前アドバイスページを表示"""
    st.header("事前アドバイス生成")
    st.write("商談前の準備をサポートします。営業タイプ、業界、商品情報を入力してください。")

    provider = get_storage_provider()
    csv_data = provider.export_sessions_to_csv()
    st.download_button(
        "📄 CSVエクスポート",
        data=csv_data.encode("utf-8"),
        file_name="sessions.csv",
        mime="text/csv",
    )

    if "pre_advice_form_data" not in st.session_state:
        st.session_state.pre_advice_form_data = {}

    submitted, form_data = render_pre_advice_form()
    render_icebreaker_section()

    autorun = st.session_state.pop("pre_advice_autorun", False)
    if submitted or autorun:
        constraints_input = form_data.get("constraints_input")
        constraints = [c.strip() for c in constraints_input.split("\n") if c.strip()] if constraints_input else []

        sales_input = SalesInput(
            sales_type=form_data["sales_type"],
            industry=form_data["industry"],
            product=form_data["product"],
            description=form_data["description"],
            description_url=form_data["description_url"],
            competitor=form_data["competitor"],
            competitor_url=form_data["competitor_url"],
            stage=form_data["stage"],
            purpose=form_data["purpose"],
            constraints=constraints,
        )

        validation_errors = validate_sales_input(sales_input)
        if validation_errors:
            st.error("❌ 入力内容に問題があります。以下を確認してください：")
            for error in validation_errors:
                st.error(f"• {error}")
            return

        try:
            with st.spinner("🤖 AIがアドバイスを生成中..."):
                from services.settings_manager import SettingsManager

                settings_manager = SettingsManager()
                service = PreAdvisorService(settings_manager)
                advice = service.generate_advice(sales_input)

            st.success("✅ アドバイスの生成が完了しました！")

            if st.session_state.selected_icebreaker:
                st.markdown("### ❄️ アイスブレイク（選択中）")
                st.markdown(f"> {st.session_state.selected_icebreaker}")

            display_advice(advice)

            sources = st.session_state.get("icebreak_last_news", [])
            if sources:
                st.markdown("### 🔍 参考出典")
                for item in sources:
                    title = item.get("title") or "出典"
                    url = item.get("url") or ""
                    src = item.get("source") or "web"
                    score = item.get("score")
                    reasons = ", ".join(item.get("reasons", [])) if isinstance(item.get("reasons"), list) else None
                    meta = []
                    if src:
                        meta.append(src)
                    if score is not None:
                        meta.append(f"score: {score}")
                    if reasons:
                        meta.append(reasons)
                    meta_str = f"（{' / '.join(meta)}）" if meta else ""
                    if url:
                        st.markdown(f"- [{title}]({url}) {meta_str}")
                    else:
                        st.markdown(f"- {title} {meta_str}")

            render_save_section(sales_input, advice)
        except Exception as e:
            st.error(f"❌ アドバイスの生成に失敗しました: {str(e)}")
            st.info(
                "しばらく時間をおいて再度お試しください。問題が続く場合は管理者にお問い合わせください。"
            )

def _legacy_show_pre_advice_page():
    st.header("事前アドバイス生成")
    st.write("商談前の準備をサポートします。営業タイプ、業界、商品情報を入力してください。")
    
    # レスポンシブ対応のための画面幅推定
    # Streamlitのカラムレイアウトで自動的にレスポンシブ対応
    
    # セッション状態の初期化
    if 'pre_advice_form_data' not in st.session_state:
        st.session_state.pre_advice_form_data = {}
    
    # 入力フォーム
    with st.form("pre_advice_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sales_type = st.selectbox(
                "営業タイプ *",
                options=list(SalesType),
                format_func=lambda x: f"{x.value} ({get_sales_type_emoji(x)})",
                help="営業スタイルを選択してください",
                key="sales_type_select"
            )
            
            industry = st.text_input(
                "業界 *", 
                placeholder="例: IT、製造業、金融業",
                help="対象となる業界を入力してください（2文字以上）",
                key="industry_input"
            )
            
            # 業界のリアルタイムバリデーション
            if industry:
                industry_errors = validate_industry(industry)
                if industry_errors:
                    for error in industry_errors:
                        st.error(f"⚠️ {error}")
                else:
                    st.success("✅ 業界名が有効です")
            
            product = st.text_input(
                "商品・サービス *", 
                placeholder="例: SaaS、コンサルティング",
                help="提供する商品・サービスを入力してください（2文字以上）",
                key="product_input"
            )
            
            # 商品名のリアルタイムバリデーション
            if product:
                product_errors = validate_product(product)
                if product_errors:
                    for error in product_errors:
                        st.error(f"⚠️ {error}")
                else:
                    st.success("✅ 商品名が有効です")
            
            # 説明フィールド（テキストまたはURL）
            description_type = st.radio(
                "説明の入力方法", 
                ["テキスト", "URL"],
                help="商品・サービスの説明をテキストで入力するか、URLで指定するかを選択してください",
                key="description_type"
            )
            if description_type == "テキスト":
                description = st.text_area(
                    "説明", 
                    placeholder="商品・サービスの詳細説明",
                    help="商品・サービスの特徴や価値を詳しく説明してください",
                    key="description_text"
                )
                description_url = None
            else:
                description = None
                description_url = st.text_input(
                    "説明URL", 
                    placeholder="https://example.com",
                    help="商品・サービスの説明が記載されているWebページのURLを入力してください",
                    key="description_url"
                )
        
        with col2:
            # 競合フィールド（テキストまたはURL）
            competitor_type = st.radio(
                "競合の入力方法", 
                ["テキスト", "URL"],
                help="競合情報をテキストで入力するか、URLで指定するかを選択してください",
                key="competitor_type"
            )
            if competitor_type == "テキスト":
                competitor = st.text_input(
                    "競合", 
                    placeholder="例: 競合A、競合B",
                    help="主要な競合企業やサービスを入力してください",
                    key="competitor_text"
                )
                competitor_url = None
            else:
                competitor = None
                competitor_url = st.text_input(
                    "競合URL", 
                    placeholder="https://competitor.com",
                    help="競合情報が記載されているWebページのURLを入力してください",
                    key="competitor_url"
                )
            
            stage = st.selectbox(
                "商談ステージ *",
                ["初期接触", "ニーズ発掘", "提案", "商談", "クロージング"],
                help="現在の商談の進行段階を選択してください",
                key="stage_select"
            )
            
            purpose = st.text_input(
                "目的 *", 
                placeholder="例: 新規顧客獲得、既存顧客拡大",
                help="この商談の目的を具体的に入力してください（5文字以上）",
                key="purpose_input"
            )
            
            # 目的のリアルタイムバリデーション
            if purpose:
                purpose_errors = validate_purpose(purpose)
                if purpose_errors:
                    for error in purpose_errors:
                        st.error(f"⚠️ {error}")
                else:
                    st.success("✅ 目的が有効です")
            
            constraints_input = st.text_area(
                "制約",
                placeholder="例: 予算制限、期間制限、技術制約（改行で区切って入力）",
                help="商談や提案における制約事項があれば入力してください（各制約は3文字以上）",
                key="constraints_input"
            )
        
        # アドバイス生成ボタン
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 アドバイスを生成", 
                type="primary",
                use_container_width=True
            )
    
    # フォーム送信後の処理
    # アイスブレイクUI（フォーム外）
    st.markdown("---")
    st.markdown("### ❄️ アイスブレイク生成（任意）")
    
    # モバイル対応：狭い画面では縦並びに
    if st.session_state.get('screen_width', 1000) < 800:
        ib_col1, ib_col2, ib_col3 = st.columns([1, 1, 1])
    else:
        ib_col1, ib_col2, ib_col3 = st.columns([2, 1, 1])
    
    with ib_col1:
        company_hint = st.text_input(
            "会社ヒント",
            placeholder="例: 〇〇グループ、最近M&Aあり、採用強化中 など",
            help="相手企業に関するヒントがあれば入力してください",
            key="company_hint_input"
        )
    with ib_col2:
        use_news = st.checkbox("業界ニュースを使用", value=True, key="use_news_checkbox")
    with ib_col3:
        generate_icebreak = st.button("❄️ アイスブレイクを生成", use_container_width=True, type="primary")

    # アイスブレイク生成ステート
    if 'icebreakers' not in st.session_state:
        st.session_state.icebreakers = []
    if 'selected_icebreaker' not in st.session_state:
        st.session_state.selected_icebreaker = None

    if 'pre_advice_form_data' in st.session_state:
        # 再利用
        pass

    if 'constraints_input' not in locals():
        constraints_input = ""

    # フォーム外の操作なのでセッションから主要入力を参照
    sales_type_val = st.session_state.get("sales_type_select")
    industry_val = st.session_state.get("industry_input")

    if sales_type_val and industry_val:
        if generate_icebreak:
            try:
                from services.settings_manager import SettingsManager
                settings_manager = SettingsManager()
                ice_service = IcebreakerService(settings_manager)
                with st.spinner("❄️ アイスブレイク生成中..."):
                    st.session_state.icebreakers = ice_service.generate_icebreakers(
                        sales_type=sales_type_val,
                        industry=industry_val,
                        company_hint=st.session_state.get("company_hint_input") or None,
                        search_enabled=st.session_state.get("use_news_checkbox", True),
                    )
                st.success("✅ アイスブレイクを生成しました！")
                # 出典をセッションへ保存（UIで後段表示）
                st.session_state.icebreak_last_news = getattr(ice_service, 'last_news_items', [])
            except Exception as e:
                st.warning(f"アイスブレイク生成に失敗しました（フォールバックを表示）: {e}")
                try:
                    # フォールバック
                    ice_service = IcebreakerService(None)
                    st.session_state.icebreakers = ice_service._generate_fallback_icebreakers(
                        sales_type=sales_type_val, industry=industry_val, tone=ice_service._get_tone_for_type(sales_type_val)
                    )
                except Exception:
                    st.session_state.icebreakers = []

    if st.session_state.icebreakers:
        st.markdown("#### 🎯 アイスブレイク候補")
        
        # アイスブレイク候補をカード形式で表示
        for idx, line in enumerate(st.session_state.icebreakers, 1):
            # カード形式のコンテナ
            with st.container():
                # 選択状態に応じてスタイルを変更
                if st.session_state.selected_icebreaker == line:
                    st.markdown(f"""
                    <div style="
                        border: 2px solid #00ff88; 
                        border-radius: 10px; 
                        padding: 15px; 
                        margin: 10px 0; 
                        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    ">
                        <h4 style="margin: 0 0 10px 0; color: #0369a1;">🎯 選択中: {line}</h4>
                        <p style="margin: 0; color: #0c4a6e;">このアイスブレイクが選択されています</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #e5e7eb; 
                        border-radius: 10px; 
                        padding: 15px; 
                        margin: 10px 0; 
                        background: white;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    ">
                        <h4 style="margin: 0 0 10px 0; color: #374151;">{idx}. {line}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                
                # ボタン配置（Streamlitが自動的にレスポンシブ対応）
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col1:
                    # 選択ボタン
                    if st.button(f"🎯 選択", key=f"select_{idx}", use_container_width=True, 
                               type="primary" if st.session_state.selected_icebreaker == line else "secondary"):
                        st.session_state.selected_icebreaker = line
                        st.rerun()
                
                with col2:
                    copy_button(line, key=f"copy_{idx}", use_container_width=True)
                
                with col3:
                    # 詳細表示ボタン
                    if st.button(f"👁️ 詳細", key=f"detail_{idx}", use_container_width=True):
                        st.info(f"**アイスブレイク詳細：**\n\n{line}")
                
                st.markdown("---")
        
        # 選択中のアイスブレイクを強調表示
        if st.session_state.selected_icebreaker:
            st.markdown("### ❄️ 選択中のアイスブレイク")

            # コピーしやすい形式で表示（改善版）
            st.markdown(f"""
            <div style="
                border: 3px solid #00ff88;
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                box-shadow: 0 8px 16px rgba(0, 255, 136, 0.2);
            ">
                <h3 style="margin: 0 0 15px 0; color: #166534; text-align: center;">🎯 選択済みアイスブレイク</h3>
                <p style="margin: 0; color: #166534; line-height: 1.6;">
                    {st.session_state.selected_icebreaker}
                </p>
            </div>
            """, unsafe_allow_html=True)
            copy_button(
                st.session_state.selected_icebreaker,
                key="selected_icebreaker_copy2",
                use_container_width=True,
            )

    # 検索出典の表示（IcebreakerServiceが直近ニュースを保持）
    try:
        from services.icebreaker import IcebreakerService as _IS
        # 既存のサービスインスタンスは保持していないため、軽く再取得
        # 表示用のみに利用（実際の生成は上で実行済み）
        if 'last_news_displayed' not in st.session_state:
            st.session_state.last_news_displayed = []
        if 'icebreak_last_news' in st.session_state:
            news_items = st.session_state.icebreak_last_news
        else:
            news_items = []
        # 生成直後にsession_stateへ入れる
    except Exception:
        news_items = []

    # アドバイス生成処理
    autorun = st.session_state.pop("pre_advice_autorun", False)
    if submitted or autorun:
        # 制約をリストに変換
        constraints = [c.strip() for c in constraints_input.split('\n') if c.strip()] if constraints_input else []
        
        # SalesInputオブジェクトを作成
        sales_input = SalesInput(
            sales_type=sales_type,
            industry=industry,
            product=product,
            description=description,
            description_url=description_url,
            competitor=competitor,
            competitor_url=competitor_url,
            stage=stage,
            purpose=purpose,
            constraints=constraints
        )
        
        # 包括的なバリデーション
        validation_errors = validate_sales_input(sales_input)
        if validation_errors:
            st.error("❌ 入力内容に問題があります。以下を確認してください：")
            for error in validation_errors:
                st.error(f"• {error}")
            return
        
        # アドバイス生成
        try:
            with st.spinner("🤖 AIがアドバイスを生成中..."):
                # 設定マネージャーを初期化
                from services.settings_manager import SettingsManager
                settings_manager = SettingsManager()
                
                service = PreAdvisorService(settings_manager)
                advice = service.generate_advice(sales_input)
            
            # 成功メッセージ
            st.success("✅ アドバイスの生成が完了しました！")

            # アイスブレイクが選択されていれば併記
            if st.session_state.selected_icebreaker:
                st.markdown("### ❄️ アイスブレイク（選択中）")
                st.markdown(f"> {st.session_state.selected_icebreaker}")
            
            # 結果表示
            display_advice(advice)

            # 検索出典の表示
            sources = st.session_state.get('icebreak_last_news', [])
            if sources:
                st.markdown("### 🔍 参考出典")
                for item in sources:
                    title = item.get('title') or '出典'
                    url = item.get('url') or ''
                    src = item.get('source') or 'web'
                    score = item.get('score')
                    reasons = ", ".join(item.get('reasons', [])) if isinstance(item.get('reasons'), list) else None
                    meta = []
                    if src: meta.append(src)
                    if score is not None: meta.append(f"score: {score}")
                    if reasons: meta.append(reasons)
                    meta_str = f"（{' / '.join(meta)}）" if meta else ""
                    if url:
                        st.markdown(f"- [{title}]({url}) {meta_str}")
                    else:
                        st.markdown(f"- {title} {meta_str}")

            # 保存機能（PostReviewと同一フロー：sessions保存 + Session ID表示）
            if st.button("💾 生成結果を保存", use_container_width=False):
                try:
                    session_id = save_pre_advice(
                        sales_input=sales_input,
                        advice=advice,
                        selected_icebreaker=st.session_state.get("selected_icebreaker")
                    )
                    # セッションIDをセッション状態に保存
                    st.session_state.pre_advice_session_id = session_id
                    
                    # 保存成功時の詳細なフィードバック
                    st.success("✅ 結果を保存しました！")
                    
                    # セッション情報の詳細表示
                    st.markdown("---")
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        padding: 25px;
                        border-radius: 15px;
                        margin: 20px 0;
                        text-align: center;
                        color: white;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    ">
                        <h3 style="margin: 0; color: white; font-size: 1.5em;">💾 保存完了</h3>
                        <p style="margin: 15px 0; opacity: 0.9; font-size: 1.1em;">セッションが正常に保存されました</p>
                        <div style="
                            background: rgba(255, 255, 255, 0.2);
                            padding: 15px;
                            border-radius: 10px;
                            margin: 15px 0;
                            font-family: monospace;
                            font-size: 1.2em;
                            letter-spacing: 1px;
                        ">
                            <strong>セッションID:</strong> {session_id}
                        </div>
                        <p style="margin: 10px 0 0 0; opacity: 0.8; font-size: 0.9em;">
                            📁 保存場所: data/sessions/{session_id}.json
                        </p>
                    </div>
                    """.format(session_id=session_id), unsafe_allow_html=True)
                    
                    # アクションボタン
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("📚 履歴ページで確認", key="view_history", use_container_width=True):
                            st.switch_page("pages/history.py")
                    with col2:
                        if st.button("🔄 新しいアドバイスを生成", key="new_advice", use_container_width=True):
                            # フォームをクリア
                            st.session_state.pre_advice_form_data = {}
                            st.session_state.pop('pre_advice_session_id', None)
                            st.rerun()
                    with col3:
                        if st.button("📥 JSONダウンロード", key="download_json", use_container_width=True):
                            # JSONファイルのダウンロード
                            import json
                            from datetime import datetime
                            
                            # ダウンロード用のデータ構造
                            download_data = {
                                "session_id": session_id,
                                "timestamp": datetime.now().isoformat(),
                                "type": "pre_advice",
                                "input": sales_input.dict(),
                                "output": {
                                    "advice": advice,
                                    "selected_icebreaker": st.session_state.get("selected_icebreaker")
                                }
                            }
                            
                            # JSONファイルとしてダウンロード
                            json_str = json.dumps(download_data, ensure_ascii=False, indent=2)
                            st.download_button(
                                label="📥 ダウンロード開始",
                                data=json_str,
                                file_name=f"pre_advice_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json",
                                key="download_button",
                                use_container_width=True
                            )
                    
                    # 次のステップのガイダンス
                    st.info("💡 **次のステップ**: 履歴ページで保存されたセッションを確認したり、新しいアドバイスを生成したりできます。")
                    
                except Exception as e:
                    st.error(f"❌ 保存に失敗しました: {str(e)}")
                    st.info("しばらく時間をおいて再度お試しください。問題が続く場合は管理者にお問い合わせください。")
                    
        except Exception as e:
            st.error(f"❌ アドバイスの生成に失敗しました: {str(e)}")
            st.info("しばらく時間をおいて再度お試しください。問題が続く場合は管理者にお問い合わせください。")

def display_advice(advice: dict):
    """アドバイスの表示"""
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        text-align: center;
        color: white;
    ">
        <h2 style="margin: 0; color: white;">🎯 生成されたアドバイス</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">営業戦略とアクションプランをご確認ください</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 短期戦略
    if "short_term" in advice:
        st.markdown("### 📅 短期戦略（1-2週間）")
        short_term = advice["short_term"]
        
        # 開幕スクリプト
        if "openers" in short_term:
            st.markdown("#### 🎭 開幕スクリプト")
            openers = short_term["openers"]
            
            # レスポンシブ対応のタブ表示
            # モバイルでは縦並び、デスクトップでは横並び
            tab1, tab2, tab3 = st.tabs(["📞 電話", "🚪 訪問", "📧 メール"])
            
            with tab1:
                if "call" in openers and openers["call"]:
                    st.markdown("**電話での開幕スクリプト：**")
                    # レスポンシブ対応のカード表示
                    st.markdown(f"""
                    <div style="
                        background: #f8fafc;
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        position: relative;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                    ">
                        <div style="
                            position: absolute;
                            top: 10px;
                            right: 10px;
                            background: #3b82f6;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 12px;
                            white-space: nowrap;
                        ">
                            📞 電話用
                        </div>
                        <p style="
                            margin: 0; 
                            line-height: 1.6; 
                            color: #1e293b;
                            padding-right: 80px;
                            word-break: break-word;
                        ">{openers["call"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # レスポンシブ対応のボタンレイアウト
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        copy_button(openers["call"], key="copy_call", use_container_width=True)
                    with col2:
                        # モバイルでのスペース確保
                        st.write("")
                else:
                    st.info("電話用のスクリプトは生成されていません")
            
            with tab2:
                if "visit" in openers and openers["visit"]:
                    st.markdown("**訪問時の開幕スクリプト：**")
                    st.markdown(f"""
                    <div style="
                        background: #f0fdf4;
                        border: 1px solid #bbf7d0;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        position: relative;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                    ">
                        <div style="
                            position: absolute;
                            top: 10px;
                            right: 10px;
                            background: #16a34a;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 12px;
                            white-space: nowrap;
                        ">
                            🚪 訪問用
                        </div>
                        <p style="
                            margin: 0; 
                            line-height: 1.6; 
                            color: #166534;
                            padding-right: 80px;
                            word-break: break-word;
                        ">{openers["visit"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        copy_button(openers["visit"], key="copy_visit", use_container_width=True)
                    with col2:
                        st.write("")
                else:
                    st.info("訪問用のスクリプトは生成されていません")
            
            with tab3:
                if "email" in openers and openers["email"]:
                    st.markdown("**メールでの開幕スクリプト：**")
                    st.markdown(f"""
                    <div style="
                        background: #fef3c7;
                        border: 1px solid #fcd34d;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        position: relative;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                    ">
                        <div style="
                            position: absolute;
                            top: 10px;
                            right: 10px;
                            background: #d97706;
                            color: white;
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 12px;
                            white-space: nowrap;
                        ">
                            📧 メール用
                        </div>
                        <p style="
                            margin: 0; 
                            line-height: 1.6; 
                            color: #92400e;
                            padding-right: 80px;
                            word-break: break-word;
                        ">{openers["email"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        copy_button(openers["email"], key="copy_email", use_container_width=True)
                    with col2:
                        st.write("")
                else:
                    st.info("メール用のスクリプトは生成されていません")
        
        # 探索質問
        if "discovery" in short_term and short_term["discovery"]:
            st.markdown("#### 🔍 探索質問")
            for i, question in enumerate(short_term["discovery"], 1):
                st.markdown(f"""
                <div style="
                    background: #f1f5f9;
                    border-left: 4px solid #3b82f6;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 0 8px 8px 0;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                ">
                    <p style="
                        margin: 0; 
                        font-weight: 500; 
                        color: #1e293b;
                        word-break: break-word;
                        line-height: 1.6;
                    ">{i}. {question}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # レスポンシブ対応のボタンレイアウト
                col1, col2 = st.columns([3, 1])
                with col1:
                    copy_button(question, key=f"copy_discovery_{i}", use_container_width=True)
                with col2:
                    st.write("")
        
        # 差別化ポイント
        if "differentiation" in short_term and short_term["differentiation"]:
            st.markdown("#### 🎯 競合との差別化ポイント")
            for i, diff in enumerate(short_term["differentiation"], 1):
                if isinstance(diff, dict) and "vs" in diff and "talk" in diff:
                    st.markdown(f"**vs {diff['vs']}：**")
                    st.markdown(f"""
                    <div style="
                        background: #fef3c7;
                        border: 1px solid #fbbf24;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                    ">
                        <p style="
                            margin: 0; 
                            line-height: 1.6; 
                            color: #92400e;
                            word-break: break-word;
                        ">{diff["talk"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        copy_button(diff["talk"], key=f"copy_diff_{i}", use_container_width=True)
                    with col2:
                        st.write("")
                else:
                    st.markdown(f"""
                    <div style="
                        background: #f1f5f9;
                        border-left: 4px solid #10b981;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 0 8px 8px 0;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                    ">
                        <p style="
                            margin: 0; 
                            line-height: 1.6; 
                            color: #1e293b;
                            word-break: break-word;
                        ">{diff}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        copy_button(diff, key=f"copy_diff_{i}", use_container_width=True)
                    with col2:
                        st.write("")
        
        # 反論対応
        if "objections" in short_term and short_term["objections"]:
            st.markdown("#### 🛡️ 反論対応")
            for i, objection in enumerate(short_term["objections"], 1):
                if isinstance(objection, dict) and "type" in objection and "script" in objection:
                    st.markdown(f"**{objection['type']}への対応：**")
                    st.markdown(f"""
                    <div style="
                        background: #fef2f2;
                        border: 1px solid #fca5a5;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 10px 0;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                    ">
                        <p style="
                            margin: 0; 
                            line-height: 1.6; 
                            color: #991b1b;
                            word-break: break-word;
                        ">{objection["script"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        copy_button(objection["script"], key=f"copy_objection_{i}", use_container_width=True)
                    with col2:
                        st.write("")
                else:
                    st.markdown(f"""
                    <div style="
                        background: #fef2f2;
                        border-left: 4px solid #ef4444;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 0 8px 8px 0;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                    ">
                        <p style="
                            margin: 0; 
                            line-height: 1.6; 
                            color: #991b1b;
                            word-break: break-word;
                        ">{objection}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        copy_button(objection, key=f"copy_objection_{i}", use_container_width=True)
                    with col2:
                        st.write("")
        
        # 次アクション
        if "next_actions" in short_term and short_term["next_actions"]:
            st.markdown("#### 🚀 次のアクション")
            for i, action in enumerate(short_term["next_actions"], 1):
                st.markdown(f"""
                <div style="
                    background: #f0f9ff;
                    border-left: 4px solid #0ea5e9;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 0 8px 8px 0;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                ">
                    <p style="
                        margin: 0; 
                        color: #0c4a6e;
                        word-break: break-word;
                        line-height: 1.6;
                    ">{i}. {action}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    copy_button(action, key=f"copy_action_{i}", use_container_width=True)
                with col2:
                    st.write("")
        
        # KPI
        if "kpi" in short_term and short_term["kpi"]:
            st.markdown("#### 📊 KPI目標")
            kpi = short_term["kpi"]
            
            # レスポンシブ対応のカラムレイアウト
            # モバイルでは縦並び、デスクトップでは横並び
            if "next_meeting_rate" in kpi and "poc_rate" in kpi:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("次の商談設定率", kpi["next_meeting_rate"])
                with col2:
                    st.metric("POC実施率", kpi["poc_rate"])
            else:
                # 単一のKPIの場合は中央配置
                if "next_meeting_rate" in kpi:
                    st.metric("次の商談設定率", kpi["next_meeting_rate"])
                if "poc_rate" in kpi:
                    st.metric("POC実施率", kpi["poc_rate"])
    
    # 中期計画（4-12週）
    if "mid_term" in advice and advice["mid_term"]:
        st.markdown("#### 📅 中期計画（4-12週）")
        mid_term = advice["mid_term"]
        
        if "plan_weeks_4_12" in mid_term and mid_term["plan_weeks_4_12"]:
            for i, plan in enumerate(mid_term["plan_weeks_4_12"], 1):
                st.markdown(f"""
                <div style="
                    background: #fdf4ff;
                    border-left: 4px solid #a855f7;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 0 8px 8px 0;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                ">
                    <p style="
                        margin: 0; 
                        color: #581c87;
                        word-break: break-word;
                        line-height: 1.6;
                    ">{i}. {plan}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # レスポンシブ対応のボタンレイアウト
                col1, col2 = st.columns([3, 1])
                with col1:
                    copy_button(plan, key=f"copy_mid_plan_{i}", use_container_width=True)
                with col2:
                    st.write("")
    
    # 全体的なアドバイス（フォールバック用）
    if "overall_advice" in advice:
        st.markdown("### 💡 全体的なアドバイス")
        st.info(advice["overall_advice"])
    
    # 成功指標（フォールバック用）
    if "success_metrics" in advice:
        st.markdown("### 📈 成功指標")
        metrics = advice["success_metrics"]
        for metric in metrics:
            st.markdown(f"• {metric}")
    
    # 全体的なコピーボタン
    st.markdown("---")
    st.markdown("""
    <div style="
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    ">
        <h4 style="margin: 0 0 15px 0; color: #1e293b;">📋 全体をコピー</h4>
        <p style="margin: 0 0 15px 0; color: #64748b; font-size: 0.9em;">
            生成されたアドバイスの全体をJSON形式でコピーできます
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # レスポンシブ対応のボタンレイアウト
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        formatted_json = json.dumps(advice, ensure_ascii=False, indent=2)
        copy_button(formatted_json, key="copy_all", label="📋 全体コピー", use_container_width=True)
    
    # 保存成功時のセッション情報表示
    if 'pre_advice_session_id' in st.session_state:
        st.markdown("---")
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            text-align: center;
            color: white;
        ">
            <h3 style="margin: 0; color: white;">💾 保存完了</h3>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">セッションID: {}</p>
        </div>
        """.format(st.session_state.pre_advice_session_id), unsafe_allow_html=True)
        
        # レスポンシブ対応のボタンレイアウト
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📚 履歴ページで確認", key="view_history", use_container_width=True):
                st.switch_page("pages/history.py")
        with col2:
            if st.button("🔄 新しいアドバイスを生成", key="new_advice", use_container_width=True):
                # フォームをクリア
                st.session_state.pre_advice_form_data = {}
                st.session_state.pop('pre_advice_session_id', None)
                st.rerun()

def save_pre_advice(*, sales_input: SalesInput, advice: dict, selected_icebreaker: str | None) -> str:
    """事前アドバイスの結果をセッション形式で保存し、Session IDを返す"""
    try:
        from services.storage_service import get_storage_provider

        provider = get_storage_provider()
        payload = {
            "type": "pre_advice",
            "input": sales_input.dict(),
            "output": {
                "advice": advice,
                "selected_icebreaker": selected_icebreaker,
            },
        }
        session_id = provider.save_session(payload)
        return session_id
    except Exception as e:
        st.error(f"保存に失敗しました: {str(e)}")
        raise

