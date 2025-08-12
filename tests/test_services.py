import pytest
from unittest.mock import Mock, patch
from core.models import SalesInput, SalesType
from services.pre_advisor import PreAdvisorService
from services.post_analyzer import PostAnalyzerService

def test_pre_advisor_service():
    """事前アドバイスサービスのテスト"""
    with patch('services.settings_manager.SettingsManager') as mock_settings_manager, \
         patch('services.pre_advisor.OpenAIProvider') as mock_provider:
        mock_settings = Mock()
        mock_settings.load_settings.return_value.temperature = 0.7
        mock_settings.load_settings.return_value.max_tokens = 1000
        mock_settings_manager.return_value = mock_settings
        
        mock_llm = Mock()
        mock_llm.call_llm.return_value = {
            "short_term": {
                "openers": {"call": "テスト", "visit": "テスト", "email": "テスト"},
                "discovery": ["質問1"],
                "differentiation": [{"vs": "競合", "talk": "差別化"}],
                "objections": [{"type": "価格", "script": "対応"}],
                "next_actions": ["アクション1"],
                "kpi": {"next_meeting_rate": "50%", "poc_rate": "20%"},
                "summary": "テストサマリー"
            },
            "mid_term": {"plan_weeks_4_12": ["計画1"]}
        }
        mock_provider.return_value = mock_llm
        
        service = PreAdvisorService()
        input_data = SalesInput(
            sales_type=SalesType.HUNTER,
            industry="IT",
            product="SaaS",
            description="テスト商品",
            stage="初期",
            purpose="売上向上"
        )
        
        result = service.generate_advice(input_data)
        assert "short_term" in result
        assert "mid_term" in result

def test_post_analyzer_service():
    """商談後ふりかえり解析サービスのテスト"""
    with patch('services.settings_manager.SettingsManager') as mock_settings_manager, \
         patch('services.post_analyzer.OpenAIProvider') as mock_provider:
        mock_settings = Mock()
        mock_settings.load_settings.return_value.temperature = 0.7
        mock_settings.load_settings.return_value.max_tokens = 1000
        mock_settings_manager.return_value = mock_settings
        
        mock_llm = Mock()
        mock_llm.call_llm.return_value = {
            "summary": "テスト要約",
            "bant": {"budget": "100万", "authority": "あり", "need": "あり", "timeline": "3ヶ月"},
            "champ": {"challenges": "課題", "authority": "権限者", "money": "予算", "prioritization": "高"},
            "objections": [{"theme": "価格", "details": "詳細", "counter": "対応"}],
            "risks": [{"type": "停滞", "prob": "medium", "reason": "理由", "mitigation": "対策"}],
            "next_actions": ["アクション1"],
            "followup_email": {"subject": "件名", "body": "本文"},
            "metrics_update": {"stage": "次のステージ", "win_prob_delta": "+10%"}
        }
        mock_provider.return_value = mock_llm
        
        service = PostAnalyzerService()
        
        result = service.analyze_meeting(
            meeting_content="テスト議事録",
            sales_type=SalesType.HUNTER,
            industry="IT",
            product="SaaS"
        )
        assert "summary" in result
        assert "bant" in result
        assert "next_actions" in result

