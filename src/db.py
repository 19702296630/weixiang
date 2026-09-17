"""数据库引擎与会话管理（SQLAlchemy 2.0 同步引擎）。

连接池参数全部来自 `.env`，避免散落在代码里。
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=settings.db_pool_pre_ping,
    echo=settings.db_echo,
    # PyMySQL 建立连接的超时时间
    connect_args={"connect_timeout": settings.db_connect_timeout},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """所有 ORM 模型的基类，模型继承它即可被 metadata 管理。"""


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：每个请求一个会话，请求结束自动关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
