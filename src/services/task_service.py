"""任务业务逻辑：CRUD、筛选、排序、分页。

与 AI 层解耦：本模块只关心任务持久化，不 import 任何 LLM 客户端。
"""
import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models.schemas import TaskCreate, TaskUpdate
from src.models.task import Task, TaskPriority, TaskStatus

# 允许排序的字段白名单（防止任意列名注入）
_SORT_COLUMNS = {
    "created_at": Task.created_at,
    "updated_at": Task.updated_at,
    "due_date": Task.due_date,
    "priority": Task.priority,
}


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: TaskCreate) -> Task:
        task = Task(**payload.model_dump())
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)

    def list(
        self,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        tag: str | None = None,
        sort: str = "created_at",
        order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Task], int]:
        stmt = select(Task)
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        if tag is not None:
            # tags 是 JSON 数组，用 MySQL 的 JSON_CONTAINS 判断「包含」
            # （注意：此为 MySQL 专属函数，单元测试走 SQLite 时该路径需单独验证）
            stmt = stmt.where(func.json_contains(Task.tags, json.dumps(tag)))

        # 先统计总量（不含排序/分页）
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        sort_col = _SORT_COLUMNS.get(sort, Task.created_at)
        stmt = stmt.order_by(sort_col.desc() if order == "desc" else sort_col.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        rows = list(self.db.scalars(stmt).all())
        return rows, total

    def update(self, task_id: int, payload: TaskUpdate) -> Task | None:
        task = self.get(task_id)
        if task is None:
            return None
        # exclude_unset：只更新请求里显式出现的字段
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get(task_id)
        if task is None:
            return False
        self.db.delete(task)
        self.db.commit()
        return True
