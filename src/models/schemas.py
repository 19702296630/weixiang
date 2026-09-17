"""Pydantic 请求/响应模型（API 边界的数据校验）。"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    """创建任务请求体。"""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    tags: list[str] | None = None
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    """更新任务请求体（PATCH，所有字段可选，未传字段不覆盖）。"""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    tags: list[str] | None = None
    due_date: datetime | None = None


class TaskRead(BaseModel):
    """任务响应体，`from_attributes` 允许直接从 ORM 对象转换。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    tags: list[str] | None
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """任务列表响应，含分页元信息。"""

    items: list[TaskRead]
    total: int
    page: int
    page_size: int


# ===================== AI 功能 =====================


class GenerateRequest(BaseModel):
    """自然语言任务生成请求。"""

    text: str = Field(min_length=1, max_length=2000)


class TaskDraft(BaseModel):
    """自然语言生成的任务草稿（不落库），`source` 标记结果来源。"""

    title: str
    description: str | None
    priority: TaskPriority
    tags: list[str] | None
    due_date: datetime | None
    source: Literal["llm", "fallback"]


class RecommendRequest(BaseModel):
    """标签/优先级/分类推荐请求。"""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = None


class RecommendResponse(BaseModel):
    """标签/优先级/分类推荐响应。"""

    tags: list[str]
    priority: TaskPriority
    category: str
    source: Literal["llm", "fallback"]
