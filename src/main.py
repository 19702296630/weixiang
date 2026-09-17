"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db import Base, engine
from src.models.task import Task  # noqa: F401  # 注册模型到 Base.metadata，供建表
from src.routes import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 挑战项目用 create_all 建表；生产环境应替换为 Alembic 迁移
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="智能任务管理系统",
    description="AI/LLM 方向 · 带智能辅助的任务管理 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tasks.router, prefix="/api/v1")


@app.get("/", tags=["meta"])
def root() -> dict:
    """根路径，用于快速确认服务已启动。"""
    return {"status": "ok", "service": "task-management", "version": "0.1.0"}
