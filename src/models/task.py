"""任务数据模型：SQLAlchemy ORM 映射（对应 DEVELOPMENT_PLAN §6.1）。"""
import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class TaskStatus(str, enum.Enum):
    """任务状态枚举。"""

    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskPriority(str, enum.Enum):
    """任务优先级枚举。"""

    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    """任务表。

    `tags` 用 JSON 列存储字符串数组（与挑战要求的 `tags: string[]` 对齐）。
    取舍说明见 DEVELOPMENT_PLAN §6：v1 优先简单，标签若成为核心查询维度再规范化。
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status", values_callable=lambda e: [m.value for m in e]),
        default=TaskStatus.pending,
        index=True,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="task_priority", values_callable=lambda e: [m.value for m in e]),
        default=TaskPriority.medium,
        index=True,
    )
    tags: Mapped[list[str] | None] = mapped_column(JSON)
    due_date: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
