"""应用配置 — 从环境变量加载"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict

from utils.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""  # Must be set via .env or env var

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Supabase (用于验证 JWT)
    supabase_url: str = "http://localhost:54321"
    supabase_jwt_secret: str = ""
    supabase_service_role_key: str = ""

    # LLM
    openrouter_api_key: str = ""
    openai_api_key: str = ""
    deepseek_api_key: str = ""

    # 默认 LLM 模型 (free tier via OpenRouter)
    llm_model_dialogue: str = "google/gemma-4-31b-it:free"
    llm_model_assessment: str = "google/gemma-4-31b-it:free"
    llm_model_simple: str = "google/gemma-4-31b-it:free"


settings = Settings()

# Warn about unconfigured sensitive fields
if not settings.neo4j_password:
    logger.warning("⚠️ neo4j_password is empty — set it via .env or NEO4J_PASSWORD env var")
if not any([settings.openrouter_api_key, settings.openai_api_key, settings.deepseek_api_key]):
    logger.warning("⚠️ No server-side LLM API keys configured — users without their own key will see a setup prompt")
else:
    logger.info("✅ Server-side LLM key configured — default model: %s", settings.llm_model_dialogue)
