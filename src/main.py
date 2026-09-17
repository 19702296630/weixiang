"""FastAPI 应用入口。"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from src.config import settings
from src.db import Base, SessionLocal, engine
from src.models.task import Task  # noqa: F401  # 注册模型到 Base.metadata，供建表
from src.routes import ai, tasks

logger = logging.getLogger(__name__)


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
app.include_router(ai.router, prefix="/api/v1")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """统一兜底：未处理异常记录日志，返回干净的 500，不泄露内部细节。"""
    logger.exception("未处理异常：%s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误"})


@app.get("/", tags=["meta"])
def root() -> dict:
    """根路径，用于快速确认服务已启动。"""
    return {"status": "ok", "service": "task-management", "version": "0.1.0"}


@app.get("/healthz", tags=["meta"])
def healthz() -> JSONResponse:
    """健康检查：探测数据库连通性 + LLM 密钥配置状态。"""
    db_status = "ok"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 — 健康检查只记录，不抛出
        logger.warning("健康检查数据库失败：%s", exc)
        db_status = "error"

    llm_status = "configured" if settings.deepseek_api_key else "missing"
    healthy = db_status == "ok"
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={
            "status": "ok" if healthy else "degraded",
            "database": db_status,
            "llm": llm_status,
        },
    )
