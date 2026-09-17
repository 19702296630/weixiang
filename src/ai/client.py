"""DeepSeek（OpenAI 兼容接口）客户端封装：统一超时/重试/JSON mode。"""
import json

from openai import OpenAI

from src.config import settings


def _extract_json(content: str) -> dict:
    """从模型返回内容里提取 JSON 对象，兼容可能包裹的 markdown 代码块。"""
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


class LLMClient:
    """封装 DeepSeek 调用，屏蔽 SDK 细节。

    上层（generate/recommend/...）只依赖 `complete_json`，不关心具体 SDK。
    """

    def __init__(self) -> None:
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            if not settings.deepseek_api_key:
                raise RuntimeError("DEEPSEEK_API_KEY 未配置，请检查 .env")
            # 网络超时/重试由 openai SDK 负责（参数来自 .env）
            self._client = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                timeout=settings.llm_timeout,
                max_retries=settings.llm_max_retries,
            )
        return self._client

    def _call(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content or ""

    def complete_json(self, system: str, user: str) -> dict:
        """发起一次对话并返回解析后的 JSON dict。

        非 JSON 输出会额外重试一次；仍失败则抛异常，由调用方决定降级。
        网络类错误由 openai SDK 内部按 max_retries 重试，之后直接抛出。
        """
        for _ in range(2):
            content = self._call(system, user)
            try:
                return _extract_json(content)
            except json.JSONDecodeError:
                continue
        raise ValueError("LLM 连续两次未返回有效 JSON")


# 模块级单例，全项目复用
llm_client = LLMClient()
