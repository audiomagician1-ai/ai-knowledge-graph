"""analytics_utils tests — seed metadata loading + caching."""

import time
from unittest.mock import patch


class TestLoadSeedMetadata:
    """Test load_seed_metadata returns correct structure."""

    def setup_method(self):
        from routers.analytics_utils import invalidate_seed_cache
        invalidate_seed_cache()

    def test_returns_three_dicts(self):
        from routers.analytics_utils import load_seed_metadata
        result = load_seed_metadata()
        assert isinstance(result, tuple)
        assert len(result) == 3
        cdm, ci, dm = result
        assert isinstance(cdm, dict)
        assert isinstance(ci, dict)
        assert isinstance(dm, dict)

    def test_domain_map_has_entries(self):
        from routers.analytics_utils import load_seed_metadata
        _, _, dm = load_seed_metadata()
        assert len(dm) > 0, "domain_map should have at least one domain"

    def test_concept_domain_map_non_empty(self):
        from routers.analytics_utils import load_seed_metadata
        cdm, _, _ = load_seed_metadata()
        assert len(cdm) > 0, "concept_domain_map should have concepts"

    def test_concept_info_has_required_keys(self):
        from routers.analytics_utils import load_seed_metadata
        _, ci, _ = load_seed_metadata()
        if ci:
            first = next(iter(ci.values()))
            assert "name" in first
            assert "difficulty" in first
            assert "subdomain" in first
            assert "tags" in first


class TestSeedMetadataCache:
    """Test caching behavior of load_seed_metadata."""

    def setup_method(self):
        from routers.analytics_utils import invalidate_seed_cache
        invalidate_seed_cache()

    def test_second_call_returns_same_object(self):
        from routers.analytics_utils import load_seed_metadata
        r1 = load_seed_metadata()
        r2 = load_seed_metadata()
        assert r1 is r2, "Cached call should return the same tuple object"

    def test_invalidate_forces_reload(self):
        from routers.analytics_utils import load_seed_metadata, invalidate_seed_cache
        r1 = load_seed_metadata()
        invalidate_seed_cache()
        r2 = load_seed_metadata()
        assert r1 is not r2, "After invalidation, should return a new tuple"

    def test_cache_expires_after_ttl(self):
        from routers import analytics_utils
        from routers.analytics_utils import load_seed_metadata
        original_ttl = analytics_utils._CACHE_TTL
        try:
            analytics_utils._CACHE_TTL = 0.05  # 50ms
            r1 = load_seed_metadata()
            time.sleep(0.06)
            r2 = load_seed_metadata()
            assert r1 is not r2, "Cache should expire after TTL"
        finally:
            analytics_utils._CACHE_TTL = original_ttl

    def test_cache_hit_is_fast(self):
        from routers.analytics_utils import load_seed_metadata
        load_seed_metadata()  # warm up
        t0 = time.perf_counter()
        for _ in range(100):
            load_seed_metadata()
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.1, f"100 cached calls should be <100ms, got {elapsed*1000:.1f}ms"