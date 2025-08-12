import streamlit as st
import json
import uuid
from datetime import datetime
from core.models import SalesType
from services.icebreaker import IcebreakerService

def show_icebreaker_page():
    st.header("🎯 アイスブレイク生成")
    st.write("営業タイプと業界に応じた、自然で親しみやすいアイスブレイクを生成します。")
    
    # 履歴からの即時再生成（オートラン）の処理
    if st.session_state.get("icebreaker_autorun"):
        st.info("履歴から即時再生成を実行しています...")
        # 自動的にフォームを送信
        st.session_state["icebreaker_autorun"] = False
        st.session_state["autorun_session_id"] = None
    
    # 入力フォーム
    with st.form("icebreaker_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 履歴からの再生成に対応
            default_sales_type = st.session_state.get("icebreaker_sales_type", list(SalesType)[0])
            sales_type = st.selectbox(
                "営業タイプ",
                options=list(SalesType),
                index=list(SalesType).index(default_sales_type) if default_sales_type in list(SalesType) else 0,
                format_func=lambda x: f"{x.value} ({get_sales_type_emoji(x)})"
            )
            
            default_industry = st.session_state.get("icebreaker_industry", "")
            industry = st.text_input(
                "業界", 
                value=default_industry,
                placeholder="例: IT、製造業、金融業、医療、小売",
                help="業界を入力すると、関連する最新ニュースを活用したアイスブレイクが生成されます"
            )
        
        with col2:
            default_company_hint = st.session_state.get("icebreaker_company_hint", "")
            company_hint = st.text_input(
                "会社ヒント（任意）",
                value=default_company_hint,
                placeholder="例: 大手企業、スタートアップ、伝統企業",
                help="会社の特徴があれば入力してください（より適切なアイスブレイク生成に活用）"
            )
            
            default_search_enabled = st.session_state.get("icebreaker_search_enabled", True)
            search_enabled = st.checkbox(
                "業界ニュースを活用",
                value=default_search_enabled,
                help="業界の最新ニュースを活用してアイスブレイクを生成します"
            )
        
        # 履歴からの再生成の場合、自動的にフォームを送信
        if st.session_state.get("icebreaker_autorun"):
            st.info("履歴から再生成を実行しています...")
            # フォームの値を更新
            st.session_state["icebreaker_sales_type"] = sales_type
            st.session_state["icebreaker_industry"] = industry
            st.session_state["icebreaker_company_hint"] = company_hint
            st.session_state["icebreaker_search_enabled"] = search_enabled
        
        # 生成ボタンを中央に配置
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("❄️ アイスブレイクを生成", type="primary", use_container_width=True)
    
    # フォーム送信後の処理
    if submitted:
        # 必須フィールドのチェック
        if not industry:
            st.error("業界を入力してください")
            return
        
        # アイスブレイク生成
        try:
            with st.spinner("アイスブレイクを生成中..."):
                # 設定マネージャーを初期化
                from services.settings_manager import SettingsManager
                settings_manager = SettingsManager()
                
                service = IcebreakerService(settings_manager)
                icebreakers = service.generate_icebreakers(
                    sales_type=sales_type,
                    industry=industry,
                    company_hint=company_hint,
                    search_enabled=search_enabled
                )
            
            # 結果表示
            display_icebreakers(sales_type, industry, icebreakers, search_enabled, company_hint)
            
            # 履歴からの即時再生成の場合、セッション状態をクリア
            if st.session_state.get("icebreaker_autorun"):
                st.session_state["icebreaker_autorun"] = False
                st.session_state["autorun_session_id"] = None
                # 入力フィールドもクリア
                st.session_state["icebreaker_sales_type"] = None
                st.session_state["icebreaker_industry"] = ""
                st.session_state["icebreaker_company_hint"] = ""
                st.session_state["icebreaker_search_enabled"] = True
            
        except Exception as e:
            st.error(f"アイスブレイク生成に失敗しました: {e}")
            st.info("フォールバック用の基本的なアイスブレイクが表示されます。")

def get_sales_type_emoji(sales_type: SalesType) -> str:
    """営業タイプに対応する絵文字を取得"""
    emojis = {
        SalesType.HUNTER: "🏹",
        SalesType.CLOSER: "🔒",
        SalesType.RELATION: "🤝",
        SalesType.CONSULTANT: "🧭",
        SalesType.CHALLENGER: "⚡",
        SalesType.STORYTELLER: "📖",
        SalesType.ANALYST: "📊",
        SalesType.PROBLEM_SOLVER: "🧩",
        SalesType.FARMER: "🌾"
    }
    return emojis.get(sales_type, "👤")

def display_icebreakers(sales_type: SalesType, industry: str, icebreakers: list, search_enabled: bool, company_hint: str = None):
    """アイスブレイク結果を表示"""
    st.success("✅ アイスブレイクが生成されました！")
    
    # 営業タイプと業界の情報
    st.subheader(f"🎯 {sales_type.value} ({get_sales_type_emoji(sales_type)}) - {industry}業界")
    if company_hint:
        st.info(f"会社ヒント: {company_hint}")
    
    # 生成されたアイスブレイク
    st.subheader("💬 生成されたアイスブレイク")
    
    # モバイル対応のレイアウト
    for i, icebreaker in enumerate(icebreakers, 1):
        with st.container():
            # アイスブレイクテキストとコピーボタンを横並びで表示
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{i}. {icebreaker}**")
            
            with col2:
                # コピーボタン
                if st.button(f"📋 コピー", key=f"copy_{i}", use_container_width=True):
                    st.write("✅ コピーしました！")
                    # クリップボードにコピー（Streamlitでは表示のみ）
                    st.session_state[f"copied_{i}"] = True
            
            # 使用シーン別のアドバイス（モバイル対応）
            with st.expander(f"使用シーン {i}", expanded=False):
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    st.write("**📞 電話**")
                    st.write("自然な流れで導入")
                with col2:
                    st.write("**🏢 訪問**")
                    st.write("場の雰囲気を読む")
                with col3:
                    st.write("**📧 メール**")
                    st.write("件名や導入で活用")
            
            st.divider()
    
    # 営業タイプ別の使用アドバイス
    st.subheader("💡 営業タイプ別の使用アドバイス")
    
    advice = get_sales_type_advice(sales_type)
    with st.expander("使用上のポイント", expanded=False):
        for point in advice:
            st.write(f"• {point}")
    
    # 業界ニュースの活用状況
    if search_enabled:
        st.subheader("📰 業界ニュース活用状況")
        st.info("業界の最新ニュースを活用して、時事的で親しみやすいアイスブレイクを生成しました。")
    else:
        st.subheader("📰 業界ニュース活用状況")
        st.warning("業界ニュースの活用を無効にしているため、一般的なアイスブレイクを生成しました。")
    
    # 保存セクション
    st.subheader("💾 アイスブレイクの保存")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 セッションに保存", use_container_width=True):
            save_icebreakers(sales_type, industry, icebreakers, company_hint, search_enabled)
            st.success("アイスブレイクをセッションに保存しました！セッションID: {session_id[:8]}...")
    
    with col2:
        if st.button("📥 JSONでダウンロード", use_container_width=True):
            download_icebreakers_json(sales_type, industry, icebreakers, company_hint, search_enabled)

def get_sales_type_advice(sales_type: SalesType) -> list:
    """営業タイプ別の使用アドバイスを取得"""
    advice = {
        SalesType.HUNTER: [
            "前向きで行動促進的なトーンを保つ",
            "簡潔で分かりやすい表現を使用",
            "顧客の関心を素早く引きつける"
        ],
        SalesType.CLOSER: [
            "価値訴求から始めて締めの一言で終わる",
            "顧客の課題解決への意欲を高める",
            "具体的なメリットを提示する"
        ],
        SalesType.RELATION: [
            "共感を示し、親近感を醸成する",
            "顧客の近況に興味を示す",
            "柔らかく親しみやすい口調を使用"
        ],
        SalesType.CONSULTANT: [
            "顧客の課題を仮説として提示する",
            "問いかけ形式で顧客の思考を促進する",
            "専門性と親しみやすさのバランスを取る"
        ],
        SalesType.CHALLENGER: [
            "従来の常識に疑問を投げかける",
            "新しい視点やアプローチを提示する",
            "顧客の思考を刺激する内容にする"
        ],
        SalesType.STORYTELLER: [
            "具体的な事例や物語を交える",
            "顧客がイメージしやすい内容にする",
            "感情に訴える要素を含める"
        ],
        SalesType.ANALYST: [
            "事実やデータに基づく内容にする",
            "論理的で分かりやすい説明を心がける",
            "顧客の理解を促進する"
        ],
        SalesType.PROBLEM_SOLVER: [
            "顧客が直面している課題に焦点を当てる",
            "解決への道筋を明確にする",
            "次の一歩を具体的に提示する"
        ],
        SalesType.FARMER: [
            "長期的な関係構築を意識する",
            "顧客の成長や発展を支援する姿勢を示す",
            "紹介や紹介の機会を創出する"
        ]
    }
    
    return advice.get(sales_type, [
        "顧客の反応を見ながら適切に調整する",
        "自然な流れで商談に導入する",
        "顧客の関心を引きつける内容にする"
    ])

def save_icebreakers(sales_type: SalesType, industry: str, icebreakers: list, company_hint: str = None, search_enabled: bool = True):
    """アイスブレイク結果をセッションに保存"""
    try:
        # セッションIDを生成
        session_id = str(uuid.uuid4())
        
        # 保存データを構築
        session_data = {
            "session_id": session_id,
            "type": "icebreaker",
            "created_at": datetime.now().isoformat(),
            "sales_type": sales_type.value,
            "industry": industry,
            "company_hint": company_hint,
            "search_enabled": search_enabled,
            "icebreakers": icebreakers,
            "emoji": get_sales_type_emoji(sales_type)
        }
        
        # セッション状態に保存
        if "icebreaker_sessions" not in st.session_state:
            st.session_state.icebreaker_sessions = {}
        
        st.session_state.icebreaker_sessions[session_id] = session_data
        
        # 成功メッセージ
        st.success(f"アイスブレイクをセッションに保存しました！セッションID: {session_id[:8]}...")
        
        # 履歴ページで表示できるように、LocalStorageProviderにも保存
        try:
            from providers.storage_local import LocalStorageProvider
            provider = LocalStorageProvider(data_dir="./data")
            
            # 入力データと出力データを分けて保存
            input_data = {
                "sales_type": sales_type.value,
                "industry": industry,
                "company_hint": company_hint,
                "search_enabled": search_enabled
            }
            
            output_data = {
                "type": "icebreaker",
                "icebreakers": icebreakers,
                "emoji": get_sales_type_emoji(sales_type),
                "sales_type": sales_type.value,
                "industry": industry
            }
            
            # セッションを保存
            provider.save_session(
                session_id=session_id,
                input_data=input_data,
                output_data=output_data,
                tags=[f"{sales_type.value}", f"{industry}業界"]
            )
            
            st.success("履歴にも保存しました！履歴ページで確認できます。")
            
        except Exception as storage_error:
            st.warning(f"履歴への保存に失敗しました: {storage_error}")
        
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")

def download_icebreakers_json(sales_type: SalesType, industry: str, icebreakers: list, company_hint: str = None, search_enabled: bool = True):
    """アイスブレイク結果をJSONファイルでダウンロード"""
    try:
        # ダウンロードデータを構築
        download_data = {
            "type": "icebreaker",
            "created_at": datetime.now().isoformat(),
            "sales_type": sales_type.value,
            "industry": industry,
            "company_hint": company_hint,
            "search_enabled": search_enabled,
            "icebreakers": icebreakers,
            "emoji": get_sales_type_emoji(sales_type)
        }
        
        # JSONファイルとしてダウンロード
        import io
        json_str = json.dumps(download_data, ensure_ascii=False, indent=2)
        
        st.download_button(
            label="📥 JSONファイルをダウンロード",
            data=json_str,
            file_name=f"icebreaker_{industry}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"ダウンロードに失敗しました: {e}")
