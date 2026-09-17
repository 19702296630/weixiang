"""LLM 输出解析与校验：把不可靠的模型输出转成可靠的 Pydantic 对象。

对每个字段做宽松处理：单字段非法时取默认值，而不是整体失败，
这样 LLM 输出略有瑕疵时仍能保住有效信息。
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from src.models.task import TaskPriority


def _to_naive(dt: datetime) -> datetime:
    """去掉时区信息，统一存本地朴素时间（MVP 约定，见 DEVELOPMENT_PLAN §6/§8）。"""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def _parse_due_date(value) -> datetime | None:
    """尽力把 LLM 返回的时间字符串解析为朴素 datetime，失败返回 None。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return _to_naive(value)
    if not isinstance(value, str):
        return None
    s = value.strip().replace("Z", "+00:00")
    for fmt in (
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            return _to_naive(datetime.strptime(s, fmt))
        except ValueError:
            continue
    return None


class GenerateOutput(BaseModel):
    """自然语言抽取的原始结果（宽松校验）。"""

    model_config = ConfigDict(extra="ignore")

    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    priority: TaskPriority | None = None
    tags: list[str] = []

    @field_validator("title", "description", mode="before")
    @classmethod
    def _clean_str(cls, v):
        return v.strip() if isinstance(v, str) and v.strip() else None

    @field_validator("priority", mode="before")
    @classmethod
    def _coerce_priority(cls, v):
        if v is None or isinstance(v, TaskPriority):
            return v
        try:
            return TaskPriority(str(v).strip().lower())
        except ValueError:
            return None

    @field_validator("tags", mode="before")
    @classmethod
    def _coerce_tags(cls, v):
        if v is None:
            return []
        if isinstance(v, list):
            return [str(t).strip() for t in v if str(t).strip()]
        return []

    @field_validator("due_date", mode="before")
    @classmethod
    def _coerce_due_date(cls, v):
        return _parse_due_date(v)


def parse_generate_output(data: dict) -> GenerateOutput:
    """把 LLM 返回的 dict 校验为 GenerateOutput。"""
    return GenerateOutput.model_validate(data)
