"""标签/优先级/分类推荐（LLM 主路 + 规则降级）。"""
import logging

from src.ai import prompts
from src.ai.client import llm_client
from src.ai.fallback import (
    recommend_category as rule_category,
)
from src.ai.fallback import (
    recommend_priority as rule_priority,
)
from src.ai.fallback import (
    recommend_tags as rule_tags,
)
from src.ai.parsers import parse_recommend_output
from src.models.schemas import RecommendResponse

logger = logging.getLogger(__name__)


def recommend_metadata(title: str, description: str | None = None) -> RecommendResponse:
    """根据标题 + 描述推荐标签、优先级与分类。

    LLM 失败时回退到规则引擎；`source` 标记来源。
    """
    title = title.strip()
    try:
        data = llm_client.complete_json(
            prompts.RECOMMEND_SYSTEM, prompts.recommend_user(title, description)
        )
        out = parse_recommend_output(data)
        return RecommendResponse(
            tags=out.tags,
            priority=out.priority or rule_priority(title, description),
            category=out.category or rule_category(title, description),
            source="llm",
        )
    except Exception as exc:  # noqa: BLE001 — 降级：LLM 异常统一回退到规则引擎
        logger.warning("LLM 推荐失败，回退到规则引擎：%s", exc)
        return RecommendResponse(
            tags=rule_tags(title, description),
            priority=rule_priority(title, description),
            category=rule_category(title, description),
            source="fallback",
        )
