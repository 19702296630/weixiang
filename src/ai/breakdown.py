"""任务拆解：复杂任务 → 子任务列表。"""
import logging

from src.ai import prompts
from src.ai.client import llm_client
from src.ai.parsers import parse_breakdown_output
from src.models.schemas import BreakdownResponse, Subtask
from src.models.task import Task, TaskPriority

logger = logging.getLogger(__name__)


def breakdown_task(task: Task) -> BreakdownResponse:
    """把一个任务拆成子任务列表。

    拆解没有可靠的规则兜底，LLM 失败时返回空列表（`source="fallback"`），
    由调用方根据 source 判断。
    """
    try:
        data = llm_client.complete_json(
            prompts.BREAKDOWN_SYSTEM, prompts.breakdown_user(task.title, task.description)
        )
        out = parse_breakdown_output(data)
        subtasks = [
            Subtask(title=item.title, priority=item.priority or TaskPriority.medium)
            for item in out.subtasks
            if item.title
        ]
        if not subtasks:
            raise ValueError("LLM 未返回有效子任务")
        return BreakdownResponse(task_id=task.id, subtasks=subtasks, source="llm")
    except Exception as exc:  # noqa: BLE001 — 降级：拆解无规则兜底，返回空列表
        logger.warning("LLM 拆解失败，返回空列表：%s", exc)
        return BreakdownResponse(task_id=task.id, subtasks=[], source="fallback")
