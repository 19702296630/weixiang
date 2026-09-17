"""任务摘要：代码统计精确数字 + LLM 生成自然语言描述。

设计要点（§8.5）：数字由代码精确统计，LLM 只负责转成自然语言，避免模型幻觉编数字。
"""
import logging
from datetime import datetime, time, timedelta

from src.ai import prompts
from src.ai.client import llm_client
from src.ai.parsers import parse_summary_output
from src.models.schemas import SummaryResponse, SummaryStats
from src.models.task import Task, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)

_PERIOD_LABEL = {"day": "今日", "week": "本周"}


def period_start(now: datetime, period: str) -> datetime:
    """计算统计时间窗口起点：day=今日 0 点；week=本周一 0 点。"""
    if period == "day":
        return datetime.combine(now.date(), time.min)
    monday = now.date() - timedelta(days=now.weekday())
    return datetime.combine(monday, time.min)


def compute_stats(tasks: list[Task], now: datetime) -> SummaryStats:
    """用代码统计精确数字（避免 LLM 幻觉）。"""
    total = len(tasks)
    high_priority = sum(
        1 for t in tasks
        if t.priority == TaskPriority.high and t.status != TaskStatus.completed
    )
    completed = sum(1 for t in tasks if t.status == TaskStatus.completed)
    overdue = sum(
        1 for t in tasks
        if t.due_date is not None and t.due_date < now and t.status != TaskStatus.completed
    )
    return SummaryStats(
        total=total, high_priority=high_priority, completed=completed, overdue=overdue
    )


def _rule_summary(label: str, stats: SummaryStats) -> str:
    """规则兜底：按模板拼出确定性的摘要文案。"""
    return (
        f"{label}共有 {stats.total} 个任务，其中 {stats.high_priority} 个高优先级待处理，"
        f"已完成 {stats.completed} 个，逾期 {stats.overdue} 个。"
    )


def summarize_tasks(
    tasks: list[Task], period: str, now: datetime | None = None
) -> SummaryResponse:
    """生成每日/每周任务摘要。LLM 失败时回退到规则模板。"""
    label = _PERIOD_LABEL.get(period, period)
    now = now or datetime.now()
    stats = compute_stats(tasks, now)
    try:
        data = llm_client.complete_json(prompts.SUMMARY_SYSTEM, prompts.summary_user(label, stats))
        out = parse_summary_output(data)
        if not out.summary:
            raise ValueError("LLM 未返回摘要")
        return SummaryResponse(period=period, stats=stats, summary=out.summary, source="llm")
    except Exception as exc:  # noqa: BLE001 — 降级：回退到规则模板文案
        logger.warning("LLM 摘要失败，回退规则模板：%s", exc)
        return SummaryResponse(
            period=period, stats=stats, summary=_rule_summary(label, stats), source="fallback"
        )
