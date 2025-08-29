import os
import json
from typing import Literal, Dict, Any, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

MODEL_TOKEN_LIMIT = 4000

class OpenAIProvider:
    def __init__(self, settings_manager=None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEYが設定されていません")
        self.client = OpenAI(api_key=api_key)
        self.settings_manager = settings_manager
    
    def _get_default_modes(self):
        """設定からデフォルトモードを取得、設定がない場合はデフォルト値を使用"""
        if self.settings_manager:
            try:
                settings = self.settings_manager.load_settings()
                base_temp = max(0.0, min(2.0, settings.temperature))
                base_tokens = max(1, min(MODEL_TOKEN_LIMIT, settings.max_tokens))
                return {
                    "speed": {
                        "temperature": base_temp,
                        "top_p": 0.9,
                        "max_tokens": base_tokens
                    },
                    "deep": {
                        "temperature": max(0.0, min(2.0, base_temp * 0.8)),
                        "max_tokens": min(int(base_tokens * 2), MODEL_TOKEN_LIMIT)
                    },
                    "creative": {
                        "temperature": max(0.0, min(2.0, base_temp * 1.5)),
                        "max_tokens": min(int(base_tokens * 0.8), MODEL_TOKEN_LIMIT)
                    }
                }
            except Exception:
                pass
        
        # デフォルト値
        return {
            "speed": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 1200
            },
            "deep": {
                "temperature": 0.2,
                "max_tokens": 2000
            },
            "creative": {
                "temperature": 0.7,
                "max_tokens": 800
            }
        }
    
    @property
    def MODES(self):
        return self._get_default_modes()
    
    def call_llm(self, prompt: str, mode: Literal["speed", "deep", "creative"], json_schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """LLMを呼び出してJSON形式で応答を取得"""
        mode_config = self.MODES[mode]
        
        try:
            # システムメッセージを構築
            system_message = "あなたは日本のトップ営業コーチです。"
            if json_schema:
                system_message += "指定されたJSONスキーマに厳密に従って回答してください。"
            
            # リクエストパラメータを構築
            request_params = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "temperature": mode_config["temperature"],
                "max_tokens": mode_config["max_tokens"]
            }
            
            # top_pが設定されている場合のみ追加
            if "top_p" in mode_config:
                request_params["top_p"] = mode_config["top_p"]
            
            # JSONスキーマが指定されている場合は厳密な検証を有効化
            if json_schema:
                request_params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": json_schema,
                    "strict": True,
                }
            
            response = self.client.chat.completions.create(**request_params)
            
            content = response.choices[0].message.content
            
            # JSONスキーマが指定されている場合はパース
            if json_schema and content:
                try:
                    parsed_response = json.loads(content)
                    # スキーマ検証
                    if self.validate_schema(parsed_response, json_schema):
                        return parsed_response
                    else:
                        raise ValueError("LLMの応答が期待されるスキーマに従っていません")
                except json.JSONDecodeError as e:
                    raise ValueError(f"LLMの応答をJSONとしてパースできませんでした: {e}")
            
            # JSONスキーマが指定されていない場合はプレーンテキストとして返す
            return {"content": content}
            
        except ValueError as e:
            # バリデーションエラーはそのまま再発生
            raise e
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise Exception("APIレート制限に達しました。しばらく待ってから再試行してください。")
            elif "quota" in str(e).lower():
                raise Exception("APIクォータが不足しています。")
            elif "invalid_api_key" in str(e).lower():
                raise Exception("無効なAPIキーです。OPENAI_API_KEYを確認してください。")
            else:
                raise Exception(f"LLM呼び出しでエラーが発生しました: {e}")
    
    def validate_schema(self, response: Dict[str, Any], expected_schema: Dict[str, Any]) -> bool:
        """レスポンスが期待されるスキーマに従っているかを検証"""
        # 基本的なスキーマ検証（簡易版）
        if not isinstance(response, dict):
            return False
        
        # 必須フィールドのチェック
        required_fields = expected_schema.get("required", [])
        for field in required_fields:
            if field not in response:
                return False
        
        return True

