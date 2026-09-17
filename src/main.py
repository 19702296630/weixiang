"""FastAPI 应用入口。

路由（/tasks、/ai/*）将在后续阶段注册进来，此处先提供一个可启动的空应用骨架。
"""
from fastapi import FastAPI

app = FastAPI(
    title="智能任务管理系统",
    description="AI/LLM 方向 · 带智能辅助的任务管理 API",
    version="0.1.0",
)


@app.get("/", tags=["meta"])
def root() -> dict:
    """根路径，用于快速确认服务已启动。"""
    return {"status": "ok", "service": "task-management", "version": "0.1.0"}
