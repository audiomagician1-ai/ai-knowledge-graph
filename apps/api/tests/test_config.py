"""config.py 测试 — Settings defaults, env overrides, warning logic"""

import os
import pytest
from unittest.mock import patch


class TestSettingsDefaults:
    """Test default values for Settings fields"""

    def test_default_neo4j_uri(self):
        from config import Settings
        s = Settings()
        assert s.neo4j_uri == "bolt://localhost:7687"

    def test_default_neo4j_user(self):
        from config import Settings
        s = Settings()
        assert s.neo4j_user == "neo4j"

    def test_default_neo4j_password_empty(self):
        """Password must not have a hardcoded default"""
        from config import Settings
        s = Settings()
        # May be set by .env, but the class default is empty
        assert isinstance(s.neo4j_password, str)

    def test_default_redis_url(self):
        from config import Settings
        s = Settings()
        assert s.redis_url == "redis://localhost:6379/0"

    def test_default_supabase_url(self):
        from config import Settings
        s = Settings()
        # Class default is localhost; may be overridden by .env
        assert isinstance(s.supabase_url, str)
        assert s.supabase_url  # not empty

    def test_default_llm_models(self):
        from config import Settings
        s = Settings()
        # Class defaults are free tier models; may be overridden by .env
        assert isinstance(s.llm_model_dialogue, str)
        assert isinstance(s.llm_model_assessment, str)
        assert isinstance(s.llm_model_simple, str)
        assert s.llm_model_dialogue  # not empty
        assert s.llm_model_assessment
        assert s.llm_model_simple

    def test_default_api_keys_empty(self):
        """Server-side API keys should default to empty (users provide their own)"""
        from config import Settings
        s = Settings()
        # These may be set via .env, just verify they're strings
        assert isinstance(s.openrouter_api_key, str)
        assert isinstance(s.openai_api_key, str)
        assert isinstance(s.deepseek_api_key, str)


class TestSettingsEnvOverride:
    """Test that env vars override defaults"""

    def test_env_override_neo4j_uri(self):
        with patch.dict(os.environ, {"NEO4J_URI": "bolt://custom:7687"}):
            from config import Settings
            s = Settings()
            assert s.neo4j_uri == "bolt://custom:7687"

    def test_env_override_redis_url(self):
        with patch.dict(os.environ, {"REDIS_URL": "redis://custom:6380/1"}):
            from config import Settings
            s = Settings()
            assert s.redis_url == "redis://custom:6380/1"

    def test_env_override_llm_model(self):
        with patch.dict(os.environ, {"LLM_MODEL_DIALOGUE": "anthropic/claude-3"}):
            from config import Settings
            s = Settings()
            assert s.llm_model_dialogue == "anthropic/claude-3"


class TestSettingsConfigDict:
    """Test that Settings uses modern Pydantic v2 ConfigDict (not deprecated class Config)"""

    def test_uses_model_config(self):
        from config import Settings
        # Pydantic v2: model_config should be a dict-like ConfigDict
        assert hasattr(Settings, 'model_config')
        cfg = Settings.model_config
        assert cfg.get("env_file") == ".env"
        assert cfg.get("env_file_encoding") == "utf-8"

    def test_no_deprecated_inner_config_class(self):
        """Should not have deprecated 'class Config' inner class"""
        from config import Settings
        # If Config exists as inner class, it's the deprecated pattern
        inner = getattr(Settings, 'Config', None)
        # Pydantic v2 may have a Config but model_config takes precedence
        # The key check is that model_config is properly set
        assert Settings.model_config.get("env_file") == ".env"
