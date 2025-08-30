import os
import json
import logging
from typing import Literal, Dict, Any, Optional
from openai import (
    OpenAI,
    RateLimitError,
    BadRequestError,
    AuthenticationError,
    APIError,
)
from tenacity import retry, stop_after_attempt, wait_exponential
from jsonschema import validate as jsonschema_validate, ValidationError
from services.error_handler import LLMError
from services.usage_meter import UsageMeter


logger = logging.getLogger(__name__)

MODEL_TOKEN_LIMIT = 4000

class OpenAIProvider:
    def __init__(self, settings_manager=None):
        api_key = os.getenv("OPENAI_API_KEY")

        # Secret Managerから取得 (環境変数が未設定の場合)
        if not api_key:
            secret_name = os.getenv("OPENAI_API_SECRET_NAME")
            project_id = os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT")
            if secret_name and project_id:
                try:
                    from google.cloud import secretmanager

                    client = secretmanager.SecretManagerServiceClient()
                    secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                    response = client.access_secret_version(name=secret_path)
                    api_key = response.payload.data.decode("UTF-8")
                except Exception:
                    api_key = None

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
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def call_llm(
        self,
        prompt: str,
        mode: Literal["speed", "deep", "creative"],
        json_schema: Optional[Dict[str, Any]] = None,
        user_id: str = "default",
    ) -> Dict[str, Any]:
        """LLMを呼び出してJSON形式で応答を取得"""
        mode_config = self.MODES[mode]

        # pre-call usage check
        if UsageMeter.get_tokens(user_id) >= UsageMeter.get_limit(user_id):
            raise LLMError("使用上限に達しました", error_code="rate_limit")
        
        try:
            # システムメッセージを構築
            system_message = "あなたは日本のトップ営業コーチです。"
            if json_schema:
                system_message += "指定されたJSONスキーマに厳密に従って回答してください。"

            # リクエストパラメータを構築
            model_name = os.getenv("OPENAI_MODEL")
            if not model_name and self.settings_manager:
                try:
                    settings = self.settings_manager.load_settings()
                    model_name = getattr(settings, "openai_model", None)
                except Exception:
                    model_name = None
            if not model_name:
                model_name = "gpt-4o-mini"

            request_params = {
                "model": model_name,
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

            # update usage based on response tokens
            usage_info = getattr(response, "usage", None)
            tokens_used = getattr(usage_info, "total_tokens", 0)
            if not isinstance(tokens_used, int):
                tokens_used = 0
            total = UsageMeter.add_tokens(user_id, tokens_used)
            if total > UsageMeter.get_limit(user_id):
                raise LLMError("使用上限に達しました", error_code="rate_limit")

            choice = response.choices[0]
            finish_reason = getattr(choice, "finish_reason", "stop")
            refusal = getattr(getattr(choice, "message", None), "refusal", None)
            if finish_reason != "stop" or refusal:
                logger.error(
                    "LLM call not completed: finish_reason=%s refusal=%s",
                    finish_reason,
                    refusal,
                )
                raise LLMError("モデルがリクエストを完了できませんでした")

            content = choice.message.content
            
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
        except RateLimitError as e:
            logger.error("Rate limit exceeded", exc_info=e)
            raise LLMError("APIレート制限に達しました。しばらく待ってから再試行してください。") from e
        except BadRequestError as e:
            logger.error("Quota exceeded", exc_info=e)
            raise LLMError("APIクォータが不足しています。") from e
        except AuthenticationError as e:
            logger.error("Invalid API key", exc_info=e)
            raise LLMError("無効なAPIキーです。OPENAI_API_KEYを確認してください。") from e
        except APIError as e:
            logger.error("OpenAI API error", exc_info=e)
            raise LLMError(f"LLM呼び出しでエラーが発生しました: {e}") from e
        except Exception as e:
            logger.error("Unexpected error during LLM call", exc_info=e)
            raise LLMError(f"LLM呼び出しでエラーが発生しました: {e}") from e
    
    def validate_schema(self, response: Dict[str, Any], expected_schema: Dict[str, Any]) -> bool:
        """レスポンスが期待されるスキーマに従っているかを検証"""
        try:
            jsonschema_validate(instance=response, schema=expected_schema)
            return True
        except ValidationError:
            return False
        except Exception:
            return False

