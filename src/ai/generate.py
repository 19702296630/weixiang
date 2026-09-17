"""自然语言 → 结构化任务草稿（不落库，用户确认后再创建）。"""
import logging

from src.ai import prompts
from src.ai.client import llm_client
from src.ai.parsers import parse_generate_output
from src.models.schemas import TaskDraft
from src.models.task import TaskPriority

logger = logging.getLogger(__name__)


def generate_task_draft(text: str) -> TaskDraft:
    """把一句自然语言转成任务草稿。

    返回 TaskDraft，`source` 标记结果来自 LLM 还是降级规则。
    任何 LLM 异常（超时/网络/解析失败）都会回退到简单规则，保证有可用结果。
    """
    text = text.strip()
    if not text:
        raise ValueError("输入文本不能为空")

    try:
        data = llm_client.complete_json(prompts.GENERATE_SYSTEM, prompts.generate_user(text))
        out = parse_generate_output(data)
        return TaskDraft(
            title=out.title or text,
            description=out.description,
            priority=out.priority or TaskPriority.medium,
            tags=out.tags or None,
            due_date=out.due_date,
            source="llm",
        )
    except Exception as exc:  # noqa: BLE001 — 降级：LLM 异常统一回退到规则方案
        logger.warning("LLM 生成失败，回退到规则方案：%s", exc)
        return TaskDraft(
            title=text,
            description=None,
            priority=TaskPriority.medium,
            tags=None,
            due_date=None,
            source="fallback",
        )
