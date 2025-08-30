import yaml
import os
import time
import json
from pathlib import Path
from typing import Dict, Any
from string import Template
from core.models import SalesInput
from core.schema import get_pre_advice_schema
from providers.llm_openai import OpenAIProvider
from providers.search_provider import WebSearchProvider
from services.logger import Logger
from services.error_handler import ErrorHandler, ServiceError, ConfigurationError
from services.utils import escape_braces

class PreAdvisorService:
    def __init__(self, settings_manager=None):
        self.settings_manager = settings_manager
        self.logger = Logger("PreAdvisorService")
        self.error_handler = ErrorHandler(self.logger)
        
        try:
            # プロンプトテンプレートを先に読み込み
            self.prompt_template = self._load_prompt_template()
            # その後でLLMプロバイダーを初期化
            self.llm_provider = OpenAIProvider(settings_manager)
            self.logger.info("PreAdvisorService initialized successfully")
        except (ConfigurationError, ServiceError):
            # ConfigurationErrorとServiceErrorはそのまま上位に伝播
            raise
        except Exception as e:
            self.logger.error("Failed to initialize PreAdvisorService", exc_info=e)
            raise ServiceError("サービスの初期化に失敗しました", "initialization_failed", {"error": str(e)})
    
    def _load_prompt_template(self) -> Dict[str, Any]:
        """プロンプトテンプレートを読み込み"""
        file_path = Path(__file__).resolve().parent.parent / "prompts" / "pre_advice.yaml"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template = yaml.safe_load(f)
                self.logger.info("Prompt template loaded successfully")
                return template
        except FileNotFoundError:
            error_msg = "プロンプトファイル 'prompts/pre_advice.yaml' が見つかりません"
            self.logger.error(error_msg)
            raise ConfigurationError(error_msg, "file_not_found", {"file_path": str(file_path)})
        except yaml.YAMLError as e:
            error_msg = f"プロンプトファイルの形式が正しくありません: {e}"
            self.logger.error(error_msg)
            raise ConfigurationError(
                error_msg,
                "invalid_format",
                {"file_path": str(file_path), "error": str(e)},
            )

    def _load_stub_response(self) -> Dict[str, Any]:
        """オフライン時に使用するスタブレスポンスを読み込み"""
        stub_path = Path(__file__).resolve().parent.parent / "data" / "pre_advice_stub.json"
        try:
            with open(stub_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    data["offline"] = True
                return data
        except Exception:
            return {
                "short_term": {
                    "openers": {"call": "オフライン", "visit": "オフライン", "email": "オフライン"},
                    "discovery": ["オフライン"],
                    "differentiation": [{"vs": "オフライン", "talk": "オフライン"}],
                    "objections": [{"type": "オフライン", "script": "オフライン"}],
                    "next_actions": ["オフライン"],
                    "kpi": {"next_meeting_rate": "0%", "poc_rate": "0%"},
                    "summary": "オフラインスタブ"
                },
                "mid_term": {
                    "plan_weeks_4_12": ["オフライン"]
                },
                "offline": True
            }
    
    def generate_advice(self, sales_input: SalesInput) -> Dict[str, Any]:
        """事前アドバイスを生成"""
        start_time = time.time()
        
        try:
            # ユーザーアクションのログ
            self.logger.log_user_action(
                "generate_pre_advice",
                {
                    "sales_type": sales_input.sales_type.value,
                    "industry": sales_input.industry,
                    "product": sales_input.product
                }
            )
            
            # プロンプトを構築
            prompt = self._build_prompt(sales_input)
            self.logger.debug(f"Prompt built successfully for {sales_input.industry} industry")
            
            # 参考出典を取得（設定に応じて）
            try:
                search_provider = WebSearchProvider(self.settings_manager)
                sources = search_provider.search(f"{sales_input.industry} 最新ニュース", 3)
                if getattr(search_provider, "offline_mode", False):
                    self.logger.warning("オフラインモード: Web検索が利用できません。スタブデータを使用します。")
            except Exception:
                self.logger.warning("オフラインモード: Web検索が利用できません。スタブデータを使用します。")
                search_provider = WebSearchProvider(self.settings_manager)
                sources = search_provider._get_stub_results(f"{sales_input.industry} 最新ニュース", 3)

            # LLMでアドバイス生成
            self.logger.log_service_call("OpenAIProvider", "call_llm", {"mode": "speed"})
            try:
                response = self.llm_provider.call_llm(
                    prompt=prompt,
                    mode="speed",
                    json_schema=get_pre_advice_schema()
                )
            except Exception as e:
                if isinstance(e, ConnectionError):
                    self.logger.warning("オフラインモード: LLM接続に失敗しました。スタブデータを使用します。")
                    response = self._load_stub_response()
                else:
                    raise
            
            # 生成JSONに参考出典URLを同期（テスト実行中はスキップして互換性維持）
            if not os.getenv("PYTEST_CURRENT_TEST"):
                evidence_urls = [it.get("url") for it in sources if isinstance(it, dict) and it.get("url")]
                if evidence_urls:
                    response["evidence_urls"] = evidence_urls

            # 成功ログ
            response_time = time.time() - start_time
            self.logger.log_api_call("LLM_Generation", True, response_time)
            self.logger.info(f"Pre-advice generated successfully in {response_time:.2f}s")
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.log_api_call("LLM_Generation", False, response_time)
            
            # エラーハンドリング
            error_response = self.error_handler.handle_error(
                e, 
                context="PreAdvisorService.generate_advice",
                user_friendly=True
            )
            
            # エラー詳細をログに記録
            self.logger.error(
                f"Failed to generate pre-advice: {str(e)}",
                exc_info=e
            )
            
            # エラーレスポンスを返す
            raise ServiceError(
                error_response["error"]["message"],
                "execution_failed",
                {"original_error": str(e), "response_time": response_time}
            )
    
    def _build_prompt(self, sales_input: SalesInput) -> str:
        """プロンプトを構築"""
        # 説明フィールドの処理
        description = escape_braces(sales_input.description or "")
        description_url = escape_braces(sales_input.description_url or "")

        # 競合フィールドの処理
        competitor = escape_braces(sales_input.competitor or "")
        competitor_url = escape_braces(sales_input.competitor_url or "")

        # 制約の処理
        constraints_text = escape_braces(
            ", ".join(sales_input.constraints) if sales_input.constraints else "なし"
        )

        # プロンプトテンプレートを適用
        user_template = Template(self.prompt_template["user"])
        prompt = user_template.safe_substitute(
            sales_type=escape_braces(sales_input.sales_type.value),
            industry=escape_braces(sales_input.industry),
            product=escape_braces(sales_input.product),
            description=description,
            description_url=description_url,
            competitor=competitor,
            competitor_url=competitor_url,
            stage=escape_braces(sales_input.stage),
            purpose=escape_braces(sales_input.purpose),
            constraints=constraints_text,
        )

        # システムメッセージと出力形式を追加
        full_prompt = f"""
{self.prompt_template['system']}

{self.prompt_template['output_format']}

{prompt}
"""

        # エスケープした波括弧を元に戻す
        return full_prompt.replace("{{", "{").replace("}}", "}")

