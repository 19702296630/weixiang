"""AI 智能功能路由。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.ai.breakdown import breakdown_task
from src.ai.generate import generate_task_draft
from src.ai.recommend import recommend_metadata
from src.ai.summarize import period_start, summarize_tasks
from src.db import get_db
from src.models.schemas import (
    BreakdownResponse,
    GenerateRequest,
    RecommendRequest,
    RecommendResponse,
    SummaryResponse,
    TaskDraft,
)
from src.services.task_service import TaskService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/generate", response_model=TaskDraft)
def generate(request: GenerateRequest) -> TaskDraft:
    """自然语言 → 任务草稿（不落库，用户确认后再 POST /tasks）。"""
    return generate_task_draft(request.text)


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    """标题 + 描述 → 标签/优先级/分类建议。"""
    return recommend_metadata(request.title, request.description)


@router.post("/tasks/{task_id}/breakdown", response_model=BreakdownResponse)
def breakdown(task_id: int, db: Session = Depends(get_db)) -> BreakdownResponse:
    """按任务 ID 拆解为子任务列表。"""
    task = TaskService(db).get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return breakdown_task(task)


@router.post("/summarize", response_model=SummaryResponse)
def summarize(
    period: str = Query(default="day", pattern="^(day|week)$"),
    db: Session = Depends(get_db),
) -> SummaryResponse:
    """每日/每周任务摘要（?period=day|week）。"""
    now = datetime.now()
    tasks = TaskService(db).list_created_since(period_start(now, period))
    return summarize_tasks(tasks, period, now)
