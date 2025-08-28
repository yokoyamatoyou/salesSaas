import pytest
from unittest.mock import Mock, patch, MagicMock
from providers.llm_openai import OpenAIProvider

class TestOpenAIProvider:
    """OpenAIプロバイダーのテスト"""
    
    def test_init_without_api_key(self):
        """APIキーなしでの初期化テスト"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEYが設定されていません"):
                OpenAIProvider()
    
    def test_init_with_api_key(self):
        """APIキーありでの初期化テスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                provider = OpenAIProvider()
                assert provider.client is not None
                mock_openai.assert_called_once_with(api_key='test-key')
    
    def test_call_llm_speed_mode(self):
        """speedモードでのLLM呼び出しテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                # モックレスポンスの設定
                mock_response = Mock()
                mock_choice = Mock()
                mock_message = Mock()
                mock_message.content = "プレーンテキストレスポンス"
                mock_choice.message = mock_message
                mock_response.choices = [mock_choice]
                mock_client.chat.completions.create.return_value = mock_response
                
                provider = OpenAIProvider()
                result = provider.call_llm("テストプロンプト", "speed")
                
                # 呼び出しパラメータの検証
                mock_client.chat.completions.create.assert_called_once()
                call_args = mock_client.chat.completions.create.call_args[1]
                assert call_args["temperature"] == 0.3
                assert call_args["max_tokens"] == 1200
                assert "top_p" in call_args
                
                # 結果の検証（JSONスキーマなしの場合はcontentキーで返される）
                assert result == {"content": "プレーンテキストレスポンス"}
    
    def test_call_llm_deep_mode(self):
        """deepモードでのLLM呼び出しテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_response = Mock()
                mock_choice = Mock()
                mock_message = Mock()
                mock_message.content = "プレーンテキストレスポンス"
                mock_choice.message = mock_message
                mock_response.choices = [mock_choice]
                mock_client.chat.completions.create.return_value = mock_response
                
                provider = OpenAIProvider()
                result = provider.call_llm("分析プロンプト", "deep")
                
                call_args = mock_client.chat.completions.create.call_args[1]
                assert call_args["temperature"] == 0.2
                assert call_args["max_tokens"] == 2000
                assert "top_p" not in call_args
                
                assert result == {"content": "プレーンテキストレスポンス"}
    
    def test_call_llm_with_json_schema(self):
        """JSONスキーマ指定でのLLM呼び出しテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_response = Mock()
                mock_choice = Mock()
                mock_message = Mock()
                mock_message.content = '{"structured": "data"}'
                mock_choice.message = mock_message
                mock_response.choices = [mock_choice]
                mock_client.chat.completions.create.return_value = mock_response
                
                provider = OpenAIProvider()
                schema = {"type": "object", "required": ["structured"]}
                result = provider.call_llm("構造化プロンプト", "creative", schema)

                call_args = mock_client.chat.completions.create.call_args[1]
                assert call_args["response_format"] == {
                    "type": "json_schema",
                    "json_schema": schema,
                    "strict": True,
                }
                
                # JSONスキーマ指定時は直接パースされたレスポンスが返される
                assert result == {"structured": "data"}
    
    def test_call_llm_without_json_schema(self):
        """JSONスキーマなしでのLLM呼び出しテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_response = Mock()
                mock_choice = Mock()
                mock_message = Mock()
                mock_message.content = "プレーンテキストレスポンス"
                mock_choice.message = mock_message
                mock_response.choices = [mock_choice]
                mock_client.chat.completions.create.return_value = mock_response
                
                provider = OpenAIProvider()
                result = provider.call_llm("テキストプロンプト", "speed")
                
                call_args = mock_client.chat.completions.create.call_args[1]
                assert "response_format" not in call_args
                
                assert result == {"content": "プレーンテキストレスポンス"}
    
    def test_call_llm_invalid_json_response(self):
        """無効なJSONレスポンスのテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_response = Mock()
                mock_choice = Mock()
                mock_message = Mock()
                mock_message.content = "無効なJSON"
                mock_choice.message = mock_message
                mock_response.choices = [mock_choice]
                mock_client.chat.completions.create.return_value = mock_response
                
                provider = OpenAIProvider()
                schema = {"type": "object"}
                
                with pytest.raises(ValueError, match="LLMの応答をJSONとしてパースできませんでした"):
                    provider.call_llm("プロンプト", "speed", schema)
    
    def test_call_llm_schema_validation_failure(self):
        """スキーマ検証失敗のテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_response = Mock()
                mock_choice = Mock()
                mock_message = Mock()
                mock_message.content = '{"field1": "value1"}'  # requiredフィールドが不足
                mock_choice.message = mock_message
                mock_response.choices = [mock_choice]
                mock_client.chat.completions.create.return_value = mock_response
                
                provider = OpenAIProvider()
                schema = {"type": "object", "required": ["field1", "field2"]}

                with pytest.raises(ValueError, match="LLMの応答が期待されるスキーマに従っていません"):
                    provider.call_llm("プロンプト", "speed", schema)

                call_args = mock_client.chat.completions.create.call_args[1]
                assert call_args["response_format"] == {
                    "type": "json_schema",
                    "json_schema": schema,
                    "strict": True,
                }
    
    def test_validate_schema(self):
        """スキーマ検証のテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            provider = OpenAIProvider()
            
            # 正常なスキーマ
            schema = {
                "type": "object",
                "required": ["field1", "field2"]
            }
            response = {"field1": "value1", "field2": "value2"}
            assert provider.validate_schema(response, schema) == True
            
            # 必須フィールド不足
            response = {"field1": "value1"}
            assert provider.validate_schema(response, schema) == False
            
            # 辞書以外のレスポンス
            response = "not a dict"
            assert provider.validate_schema(response, schema) == False
    
    def test_error_handling_rate_limit(self):
        """レート制限エラーのテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_client.chat.completions.create.side_effect = Exception("rate_limit exceeded")
                
                provider = OpenAIProvider()
                
                with pytest.raises(Exception, match="APIレート制限に達しました"):
                    provider.call_llm("プロンプト", "speed")
    
    def test_error_handling_quota(self):
        """クォータ不足エラーのテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_client.chat.completions.create.side_effect = Exception("quota exceeded")
                
                provider = OpenAIProvider()
                
                with pytest.raises(Exception, match="APIクォータが不足しています"):
                    provider.call_llm("プロンプト", "speed")
    
    def test_error_handling_invalid_api_key(self):
        """無効なAPIキーエラーのテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_client.chat.completions.create.side_effect = Exception("invalid_api_key")
                
                provider = OpenAIProvider()
                
                with pytest.raises(Exception, match="無効なAPIキーです"):
                    provider.call_llm("プロンプト", "speed")
    
    def test_error_handling_generic(self):
        """一般的なエラーのテスト"""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            with patch('providers.llm_openai.OpenAI') as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                
                mock_client.chat.completions.create.side_effect = Exception("network error")
                
                provider = OpenAIProvider()
                
                with pytest.raises(Exception, match="LLM呼び出しでエラーが発生しました"):
                    provider.call_llm("プロンプト", "speed")
