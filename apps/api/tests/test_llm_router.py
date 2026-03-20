"""LLM Router 单元测试 — SSRF防护/端点解析/重试逻辑/模型名解析/token参数"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from llm.router import _validate_base_url, _BLOCKED_HOSTS, LLMRouter, _token_limit_param


# ========== _validate_base_url (SSRF Prevention) ==========


class TestValidateBaseUrl:
    """SSRF 防护: _validate_base_url"""

    def test_valid_https_url(self):
        result = _validate_base_url("https://api.openai.com/v1")
        assert result == "https://api.openai.com/v1"

    def test_valid_http_url(self):
        result = _validate_base_url("http://my-proxy.example.com/v1/")
        assert result == "http://my-proxy.example.com/v1"

    def test_strips_trailing_slash(self):
        result = _validate_base_url("https://api.openrouter.ai/api/v1/")
        assert not result.endswith("/")

    def test_rejects_ftp_scheme(self):
        with pytest.raises(ValueError, match="Invalid URL scheme"):
            _validate_base_url("ftp://evil.com/data")

    def test_rejects_file_scheme(self):
        with pytest.raises(ValueError, match="Invalid URL scheme"):
            _validate_base_url("file:///etc/passwd")

    def test_rejects_no_scheme(self):
        with pytest.raises(ValueError, match="Invalid URL scheme"):
            _validate_base_url("just-a-string")

    def test_blocks_localhost(self):
        with pytest.raises(ValueError, match="Blocked host"):
            _validate_base_url("http://localhost:8080")

    def test_blocks_127_0_0_1(self):
        with pytest.raises(ValueError, match="Blocked host"):
            _validate_base_url("http://127.0.0.1:8000/v1")

    def test_blocks_metadata_google(self):
        with pytest.raises(ValueError, match="Blocked host"):
            _validate_base_url("http://metadata.google.internal")

    def test_blocks_private_ip_10(self):
        with pytest.raises(ValueError, match="Private/reserved IP"):
            _validate_base_url("http://10.0.0.1:8080/v1")

    def test_blocks_private_ip_192_168(self):
        with pytest.raises(ValueError, match="Private/reserved IP"):
            _validate_base_url("http://192.168.1.1/v1")

    def test_blocks_private_ip_172_16(self):
        with pytest.raises(ValueError, match="Private/reserved IP"):
            _validate_base_url("http://172.16.0.1:3000")

    def test_blocks_ipv6_loopback(self):
        with pytest.raises(ValueError, match="Blocked host"):
            _validate_base_url("http://[::1]:8000/v1")

    def test_allows_public_ip(self):
        result = _validate_base_url("https://8.8.8.8/v1")
        assert result == "https://8.8.8.8/v1"

    def test_allows_public_hostname(self):
        result = _validate_base_url("https://api.deepseek.com/v1/")
        assert result == "https://api.deepseek.com/v1"


# ========== _is_retryable ==========


class TestIsRetryable:
    """重试策略: 仅429和5xx可重试"""

    def test_429_is_retryable(self):
        assert LLMRouter._is_retryable(429) is True

    def test_500_is_retryable(self):
        assert LLMRouter._is_retryable(500) is True

    def test_502_is_retryable(self):
        assert LLMRouter._is_retryable(502) is True

    def test_503_is_retryable(self):
        assert LLMRouter._is_retryable(503) is True

    def test_400_not_retryable(self):
        assert LLMRouter._is_retryable(400) is False

    def test_401_not_retryable(self):
        assert LLMRouter._is_retryable(401) is False

    def test_403_not_retryable(self):
        assert LLMRouter._is_retryable(403) is False

    def test_404_not_retryable(self):
        assert LLMRouter._is_retryable(404) is False

    def test_200_not_retryable(self):
        assert LLMRouter._is_retryable(200) is False


# ========== _resolve_endpoint ==========


class TestResolveEndpoint:
    """端点解析: 用户配置优先, 各provider正确路由"""

    def setup_method(self):
        self.router = LLMRouter()

    def test_user_openrouter_key(self):
        config = {"api_key": "sk-user-123", "provider": "openrouter"}
        base, key = self.router._resolve_endpoint("openai/gpt-4o", config)
        assert base == LLMRouter.OPENROUTER_BASE
        assert key == "sk-user-123"

    def test_user_openai_key(self):
        config = {"api_key": "sk-openai-xyz", "provider": "openai"}
        base, key = self.router._resolve_endpoint("gpt-4o", config)
        assert base == LLMRouter.OPENAI_BASE
        assert key == "sk-openai-xyz"

    def test_user_deepseek_key(self):
        config = {"api_key": "sk-ds-abc", "provider": "deepseek"}
        base, key = self.router._resolve_endpoint("deepseek-chat", config)
        assert base == LLMRouter.DEEPSEEK_BASE
        assert key == "sk-ds-abc"

    def test_user_custom_base_url(self):
        config = {"api_key": "sk-custom", "base_url": "https://my-proxy.com/v1/", "provider": "custom"}
        base, key = self.router._resolve_endpoint("model-x", config)
        assert base == "https://my-proxy.com/v1"
        assert key == "sk-custom"

    def test_user_custom_base_url_ssrf_blocked(self):
        config = {"api_key": "sk-evil", "base_url": "http://localhost:8080/v1"}
        with pytest.raises(ValueError, match="Blocked host"):
            self.router._resolve_endpoint("model-x", config)

    def test_user_custom_provider_no_base_url_falls_to_openai(self):
        config = {"api_key": "sk-custom-no-base", "provider": "custom"}
        base, key = self.router._resolve_endpoint("my-model", config)
        assert base == LLMRouter.OPENAI_BASE

    def test_default_provider_is_openrouter(self):
        config = {"api_key": "sk-default"}
        base, key = self.router._resolve_endpoint("model", config)
        assert base == LLMRouter.OPENROUTER_BASE

    @patch("llm.router.settings")
    def test_server_openrouter_fallback(self, mock_settings):
        mock_settings.openrouter_api_key = "sk-server-or"
        mock_settings.deepseek_api_key = ""
        mock_settings.openai_api_key = ""
        base, key = self.router._resolve_endpoint("openai/gpt-4o")
        assert base == LLMRouter.OPENROUTER_BASE
        assert key == "sk-server-or"

    @patch("llm.router.settings")
    def test_server_deepseek_fallback(self, mock_settings):
        mock_settings.openrouter_api_key = ""
        mock_settings.deepseek_api_key = "sk-server-ds"
        mock_settings.openai_api_key = ""
        base, key = self.router._resolve_endpoint("deepseek/deepseek-chat")
        assert base == LLMRouter.DEEPSEEK_BASE
        assert key == "sk-server-ds"

    @patch("llm.router.settings")
    def test_server_openai_fallback(self, mock_settings):
        mock_settings.openrouter_api_key = ""
        mock_settings.deepseek_api_key = ""
        mock_settings.openai_api_key = "sk-server-oai"
        base, key = self.router._resolve_endpoint("gpt-4o")
        assert base == LLMRouter.OPENAI_BASE
        assert key == "sk-server-oai"

    @patch("llm.router.settings")
    def test_no_key_raises(self, mock_settings):
        mock_settings.openrouter_api_key = ""
        mock_settings.deepseek_api_key = ""
        mock_settings.openai_api_key = ""
        with pytest.raises(ValueError, match="No LLM API key configured"):
            self.router._resolve_endpoint("some-model")


# ========== Model Name Resolution ==========


class TestModelNameResolution:
    """模型名解析: OpenRouter保留org/前缀, 直连去掉前缀"""

    def setup_method(self):
        self.router = LLMRouter()

    def test_openrouter_keeps_full_model_name(self):
        config = {"api_key": "sk-test", "provider": "openrouter"}
        base, _ = self.router._resolve_endpoint("openai/gpt-4o", config)
        model_name = "openai/gpt-4o" if "openrouter" in base else "openai/gpt-4o".split("/")[-1]
        assert model_name == "openai/gpt-4o"

    def test_direct_openai_strips_prefix(self):
        config = {"api_key": "sk-test", "provider": "openai"}
        base, _ = self.router._resolve_endpoint("openai/gpt-4o", config)
        model_name = "openai/gpt-4o" if "openrouter" in base else "openai/gpt-4o".split("/")[-1]
        assert model_name == "gpt-4o"

    def test_direct_deepseek_strips_prefix(self):
        config = {"api_key": "sk-test", "provider": "deepseek"}
        base, _ = self.router._resolve_endpoint("deepseek/deepseek-chat", config)
        model_name = "deepseek/deepseek-chat" if "openrouter" in base else "deepseek/deepseek-chat".split("/")[-1]
        assert model_name == "deepseek-chat"

    def test_model_without_prefix_unchanged(self):
        config = {"api_key": "sk-test", "provider": "openai"}
        base, _ = self.router._resolve_endpoint("gpt-4o", config)
        model_name = "gpt-4o" if "openrouter" in base else "gpt-4o".split("/")[-1]
        assert model_name == "gpt-4o"


# ========== Model Tiers ==========


class TestModelTiers:
    """模型分层: 确保正确映射"""

    def test_tiers_has_three_levels(self):
        router = LLMRouter()
        tiers = router.model_tiers
        assert "simple" in tiers
        assert "dialogue" in tiers
        assert "assessment" in tiers

    def test_unknown_tier_falls_to_dialogue(self):
        router = LLMRouter()
        tiers = router.model_tiers
        model = tiers.get("nonexistent", tiers["dialogue"])
        assert model == tiers["dialogue"]


# ========== _token_limit_param ==========


class TestTokenLimitParam:
    """Token limit parameter: max_tokens vs max_completion_tokens"""

    def test_standard_models_use_max_tokens(self):
        assert _token_limit_param("gpt-4o", 800) == {"max_tokens": 800}
        assert _token_limit_param("deepseek-chat", 512) == {"max_tokens": 512}
        assert _token_limit_param("claude-3.5-sonnet", 1024) == {"max_tokens": 1024}

    def test_o1_o3_use_max_completion_tokens(self):
        assert _token_limit_param("o1", 800) == {"max_completion_tokens": 800}
        assert _token_limit_param("o1-mini", 512) == {"max_completion_tokens": 512}
        assert _token_limit_param("o3", 1024) == {"max_completion_tokens": 1024}
        assert _token_limit_param("o3-pro", 600) == {"max_completion_tokens": 600}

    def test_chatgpt_series_use_max_completion_tokens(self):
        assert _token_limit_param("chatgpt-4o-latest", 800) == {"max_completion_tokens": 800}

    def test_vendor_prefixed_models_stripped(self):
        assert _token_limit_param("openai/o1", 800) == {"max_completion_tokens": 800}
        assert _token_limit_param("openai/o3-pro", 1024) == {"max_completion_tokens": 1024}
        assert _token_limit_param("openai/gpt-4o", 800) == {"max_tokens": 800}

    def test_case_insensitive(self):
        assert _token_limit_param("O1-Mini", 512) == {"max_completion_tokens": 512}
        assert _token_limit_param("CHATGPT-4o-latest", 800) == {"max_completion_tokens": 800}


# ========== LLM Response Null-Safety ==========


class TestLLMChatNullSafety:
    """Round 80: LLM chat() must handle malformed responses gracefully."""

    @pytest.mark.asyncio
    async def test_empty_choices_raises_descriptive_error(self):
        """If LLM returns empty choices array, should raise with clear message."""
        router = LLMRouter()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"choices": []}

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=mock_response)
        router._client = mock_client

        with patch.object(router, '_resolve_endpoint', return_value=("https://api.example.com/v1", "test-key")):
            with pytest.raises(RuntimeError, match="LLM call failed"):
                await router.chat(messages=[{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_null_content_raises_descriptive_error(self):
        """If LLM returns null content, should raise with clear message."""
        router = LLMRouter()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": None}}]}

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=mock_response)
        router._client = mock_client

        with patch.object(router, '_resolve_endpoint', return_value=("https://api.example.com/v1", "test-key")):
            with pytest.raises(RuntimeError, match="LLM call failed"):
                await router.chat(messages=[{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_valid_response_returns_content(self):
        """Normal response with valid content should succeed."""
        router = LLMRouter()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "Hello world"}}]}

        mock_client = AsyncMock()
        mock_client.is_closed = False
        mock_client.post = AsyncMock(return_value=mock_response)
        router._client = mock_client

        with patch.object(router, '_resolve_endpoint', return_value=("https://api.example.com/v1", "test-key")):
            result = await router.chat(messages=[{"role": "user", "content": "test"}])
            assert result == "Hello world"
