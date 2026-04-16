"""LLM service with intelligent model routing."""

from collections.abc import AsyncGenerator

import httpx
from openai import AsyncOpenAI

from app.config import (
    LLM_CONFIGS,
    TASK_MODEL_MAPPING,
    ModelType,
    get_settings,
)


class LLMService:
    """
    LLM service with smart model routing.

    Routes tasks to appropriate models:
    - Fast model (deepseek-chat): Simple Q&A, summaries
    - Reasoning model (deepseek-reasoner): Deep analysis, recommendations
    """

    def __init__(self, provider: str | None = None):
        settings = get_settings()
        self.provider = provider or settings.llm_provider
        self.config = LLM_CONFIGS.get(self.provider, LLM_CONFIGS["deepseek"])

        api_key = settings.get_api_key(self.provider)
        if not api_key:
            raise ValueError(f"API key not found for provider: {self.provider}")

        # 与 ttfund_fetcher 一致：不走系统 SOCKS/HTTP 代理，避免本机代理未就绪时 LLM 请求失败→500
        _http = httpx.AsyncClient(
            trust_env=False,
            timeout=httpx.Timeout(120.0, connect=30.0),
        )
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.config["base_url"],
            http_client=_http,
        )

    def get_model_config(self, task_type: str) -> dict:
        """Get model configuration based on task type."""
        model_type = TASK_MODEL_MAPPING.get(task_type, ModelType.FAST)
        return self.config["models"][model_type.value]

    async def generate(
        self,
        task_type: str,
        messages: list[dict],
        stream: bool = False,
        **kwargs,
    ):
        """
        Generate response with automatic model routing.

        Args:
            task_type: Task type for model selection
            messages: Chat messages
            stream: Whether to stream response
            **kwargs: Additional parameters for the API

        Returns:
            Chat completion response or async generator if streaming
        """
        model_config = self.get_model_config(task_type)

        params = {
            "model": model_config["name"],
            "messages": messages,
            "temperature": kwargs.get("temperature", model_config["temperature"]),
            "stream": stream,
        }

        # Add optional parameters
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]

        response = await self._client.chat.completions.create(**params)
        return response

    async def generate_stream(
        self,
        task_type: str,
        messages: list[dict],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response.

        Yields:
            String chunks of the response
        """
        response = await self.generate(
            task_type=task_type,
            messages=messages,
            stream=True,
            **kwargs,
        )

        async for chunk in response:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            text = getattr(delta, "content", None) if delta else None
            if text:
                yield text

    async def detect_intent(self, message: str) -> str:
        """
        Detect user intent for smart routing.

        Returns:
            Intent type: simple_qa, deep_analysis, compare, advice
        """
        response = await self.generate(
            task_type="intent_detect",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "判断用户意图类型，只返回以下一个词：\n"
                        "- simple_qa: 简单事实问题（什么时候成立、费率多少等）\n"
                        "- deep_analysis: 需要深度分析（值不值得买、风险如何等）\n"
                        "- compare: 基金对比（哪只更好等）\n"
                        "- advice: 投资建议（适不适合我等）"
                    ),
                },
                {"role": "user", "content": message},
            ],
            max_tokens=20,
        )

        raw = response.choices[0].message.content
        intent = (raw or "").strip().lower()

        # Normalize intent
        valid_intents = ["simple_qa", "deep_analysis", "compare", "advice"]
        if intent not in valid_intents:
            # Default to simple_qa for unknown intents
            return "simple_qa"

        return intent

    async def smart_chat(
        self,
        message: str,
        context_messages: list[dict],
        fund_context: dict,
        user_profile: dict | None = None,
        stream: bool = False,
    ):
        """
        Smart chat with automatic intent detection and model routing.

        Args:
            message: User message
            context_messages: Previous chat history
            fund_context: Fund data context
            user_profile: Optional user investment profile
            stream: Whether to stream response

        Returns:
            Response or async generator if streaming
        """
        # Detect intent
        intent = await self.detect_intent(message)

        # Map intent to task type
        intent_to_task = {
            "simple_qa": "simple_qa",
            "deep_analysis": "deep_analysis",
            "compare": "compare_funds",
            "advice": "profile_matching",
        }
        task_type = intent_to_task.get(intent, "simple_qa")

        # Build system message with context
        system_content = self._build_chat_system_prompt(fund_context, user_profile)

        messages = [{"role": "system", "content": system_content}]
        messages.extend(context_messages)
        messages.append({"role": "user", "content": message})

        if stream:
            return self.generate_stream(task_type, messages)
        else:
            response = await self.generate(task_type, messages)
            raw = response.choices[0].message.content
            return (raw or "").strip()

    async def smart_chat_stream(
        self,
        message: str,
        context_messages: list[dict],
        fund_context: dict,
        user_profile: dict | None = None,
    ) -> AsyncGenerator[str, None]:
        """流式对话：单一路径 async for，避免 await 返回 async generator 的边缘问题。"""
        intent = await self.detect_intent(message)
        intent_to_task = {
            "simple_qa": "simple_qa",
            "deep_analysis": "deep_analysis",
            "compare": "compare_funds",
            "advice": "profile_matching",
        }
        task_type = intent_to_task.get(intent, "simple_qa")
        system_content = self._build_chat_system_prompt(fund_context, user_profile)
        msgs = [{"role": "system", "content": system_content}]
        msgs.extend(context_messages)
        msgs.append({"role": "user", "content": message})
        async for chunk in self.generate_stream(task_type, msgs):
            yield chunk

    def _build_chat_system_prompt(
        self,
        fund_context: dict,
        user_profile: dict | None = None,
    ) -> str:
        """Build system prompt for chat with context."""
        prompt_parts = [
            "你是一位专业的基金投资顾问，正在与客户进行一对一咨询。",
            "",
            "## 当前基金信息",
        ]

        if fund_context:
            prompt_parts.append(f"- 基金代码: {fund_context.get('code', 'N/A')}")
            prompt_parts.append(f"- 基金名称: {fund_context.get('name', 'N/A')}")
            prompt_parts.append(f"- 基金类型: {fund_context.get('type', 'N/A')}")

            if fund_context.get("metrics"):
                metrics = fund_context["metrics"]
                prompt_parts.append("")
                prompt_parts.append("## 业绩指标")
                if metrics.get("return_1y"):
                    prompt_parts.append(f"- 近1年收益: {metrics['return_1y']}%")
                if metrics.get("return_3y"):
                    prompt_parts.append(f"- 近3年收益: {metrics['return_3y']}%")
                if metrics.get("max_drawdown"):
                    prompt_parts.append(f"- 最大回撤: {metrics['max_drawdown']}%")
                if metrics.get("sharpe_ratio"):
                    prompt_parts.append(f"- 夏普比率: {metrics['sharpe_ratio']}")

        if user_profile:
            prompt_parts.append("")
            prompt_parts.append("## 用户画像")

            risk_map = {
                "conservative": "保守型",
                "stable": "稳健型",
                "balanced": "平衡型",
                "aggressive": "进取型",
                "radical": "激进型",
            }
            purpose_map = {
                "savings": "闲钱理财",
                "retirement": "养老储备",
                "growth": "资产增值",
                "education": "教育金",
                "other": "其他",
            }
            horizon_map = {
                "short": "短期(<1年)",
                "medium": "中期(1-3年)",
                "long": "长期(>3年)",
            }

            prompt_parts.append(f"- 风险偏好: {risk_map.get(user_profile.get('risk_level'), '未知')}")
            prompt_parts.append(f"- 投资目的: {purpose_map.get(user_profile.get('purpose'), '未知')}")
            prompt_parts.append(f"- 投资期限: {horizon_map.get(user_profile.get('horizon'), '未知')}")

        prompt_parts.extend(
            [
                "",
                "---",
                "请根据用户的问题给出专业、个性化的投资建议。",
                "",
                "注意：",
                "1. 结合用户的风险偏好评估基金匹配度",
                "2. 如果基金不适合用户，坦诚说明并推荐替代方案",
                "3. 使用简洁易懂的语言，避免过多专业术语",
                "4. 可以使用 emoji 使回复更友好",
                "5. 如有必要，主动询问更多信息以提供更精准的建议",
            ]
        )

        return "\n".join(prompt_parts)


# Singleton instance
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """Get singleton LLM service instance."""
    global _llm_service
    if _llm_service is None:
        try:
            _llm_service = LLMService()
        except ValueError:
            # If no API key configured, return None
            return None
    return _llm_service
