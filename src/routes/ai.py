"""AI 智能功能路由。"""
from fastapi import APIRouter

from src.ai.generate import generate_task_draft
from src.models.schemas import GenerateRequest, TaskDraft

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/generate", response_model=TaskDraft)
def generate(request: GenerateRequest) -> TaskDraft:
    """自然语言 → 任务草稿（不落库，用户确认后再 POST /tasks）。"""
    return generate_task_draft(request.text)
