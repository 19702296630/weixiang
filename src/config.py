"""应用配置：从 `.env` 读取环境变量并做类型校验。

使用 pydantic-settings，字段名大小写不敏感，`.env` 中的 `DB_HOST` 自动映射到 `db_host`。
"""
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（src/ 的上一级），用于无论从哪个 cwd 启动都能找到 .env
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """集中管理全部配置，禁止在业务代码里硬编码密钥/连接串。"""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 忽略 .env 中未声明的键，避免启动报错
    )

    # ===================== MySQL =====================
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "task_management"
    db_charset: str = "utf8mb4"
    # 连接池（生产级）
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    db_pool_pre_ping: bool = True
    db_echo: bool = False
    db_connect_timeout: int = 10

    # ===================== DeepSeek =====================
    deepseek_api_key: str = ""
    deepseek_model: str = "DeepSeek-V4.1-Flash"
    deepseek_base_url: str = "https://api.deepseek.com"
    llm_timeout: int = 60
    llm_max_retries: int = 3
    llm_max_tokens: int = 2048
    llm_temperature: float = 0.0

    @property
    def database_url(self) -> str:
        """拼装 SQLAlchemy 连接串，用户名/密码做 URL 编码避免特殊字符破坏连接串。"""
        user = quote_plus(self.db_user)
        pwd = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{user}:{pwd}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset={self.db_charset}"
        )


# 模块级单例，全项目 `from src.config import settings` 复用
settings = Settings()
