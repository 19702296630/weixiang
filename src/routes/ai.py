"""AI 智能功能路由。"""
from fastapi import APIRouter

from src.ai.generate import generate_task_draft
from src.ai.recommend import recommend_metadata
from src.models.schemas import (
    GenerateRequest,
    RecommendRequest,
    RecommendResponse,
    TaskDraft,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/generate", response_model=TaskDraft)
def generate(request: GenerateRequest) -> TaskDraft:
    """自然语言 → 任务草稿（不落库，用户确认后再 POST /tasks）。"""
    return generate_task_draft(request.text)


@router.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest) -> RecommendResponse:
    """标题 + 描述 → 标签/优先级/分类建议。"""
    return recommend_metadata(request.title, request.description)
