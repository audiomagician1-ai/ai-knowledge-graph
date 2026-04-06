# Cross-Module Invariants Registry — AKG Three-Platform Sync Manual

> **Owner**: AI Knowledge Graph team
> **Last Updated**: 2026-04-07
> **Rule**: Any PR touching files listed below MUST check all sync points.

---

## Architecture Overview

```
packages/web/       <- React SPA (TypeScript)         "FE"
workers/            <- Cloudflare Workers (TypeScript)  "Workers"
apps/api/           <- FastAPI (Python)                 "BE"
```

Three independent runtimes, two languages (TS x2 + Python), no shared type generation.
All invariants maintained by **manual discipline + this document**.

---

## Invariant Registry

### INV-01: Mastered Judgment Threshold (7 sync points)

**Rule**: `overall >= 75 AND all dimensions >= 60`

| # | Location | File | Function |
|---|----------|------|----------|
| 1 | FE | `packages/web/src/lib/direct-llm.ts` | `validateAssessment()` |
| 2 | FE | `packages/web/src/lib/direct-llm.ts` | fallback evaluate |
| 3 | FE | `packages/web/src/lib/store/learning.ts` | `recordAssessment()` |
| 4 | BE | `apps/api/engines/dialogue/evaluator.py` | `validate_result()` |
| 5 | BE | `apps/api/engines/dialogue/evaluator.py` | `fallback_evaluate()` |
| 6 | BE | `apps/api/db/sqlite_client.py` | `record_assessment()` |
| 7 | Workers | `workers/src/dialogue.ts` | `validateAssessment()` |

### INV-02: Mastered Demotion Guard (8 sync points)

**Rule**: Once mastered, a concept MUST NOT be demoted to learning/not_started.

| # | Location | File | Guard |
|---|----------|------|-------|
| 1 | FE | `learning.ts` | `startLearning()` wasMastered |
| 2 | FE | `learning.ts` | `recordAssessment()` wasMastered |
| 3 | FE | `supabase-sync.ts` | `toDbStatus()` mapping |
| 4 | BE | `sqlite_client.py` | `start_learning()` |
| 5 | BE | `sqlite_client.py` | `record_assessment()` C-06 |
| 6 | BE | `learning.py` | `/sync` mastered guard |
| 7 | Workers | `learning.ts` | `/start` + `/assess` |
| 8 | Workers | `learning.ts` | `/sync` mastered CASE |

### INV-03: tokenLimitParam (4 sync points)

**Rule**: OpenAI o1/o3/chatgpt-* use `max_completion_tokens` not `max_tokens`.

| # | Location | File |
|---|----------|------|
| 1 | FE | `direct-llm.ts` |
| 2 | FE | `settings.ts` |
| 3 | BE | `llm/router.py` |
| 4 | Workers | `llm.ts` |

### INV-04: validateAssessment Score Clamping (3 sync points)

**Rule**: Scores clamped [0,100], mastered recalc, null/NaN -> fallback 50.

| # | Location | File |
|---|----------|------|
| 1 | FE | `direct-llm.ts` |
| 2 | BE | `evaluator.py` |
| 3 | Workers | `dialogue.ts` |

### INV-05: DOMAIN_SUPPLEMENTS (3 sync points)

**Rule**: New domain -> register supplements in all three.

| # | Location | File |
|---|----------|------|
| 1 | BE | `prompts/feynman_system.py` |
| 2 | FE | `direct-llm.ts` |
| 3 | Workers | `prompts.ts` |

### INV-06: Dialogue Truncation (3 sync points)

**Rule**: 8000 char limit, push+reverse O(n).

| # | Location | File |
|---|----------|------|
| 1 | FE | `direct-llm.ts` |
| 2 | BE | `evaluator.py` `_format_dialogue()` |
| 3 | Workers | `dialogue.ts` |

### INV-07: Status Mapping (4-endpoint consistency)

**Rule**: local status -> toDbStatus() -> DB CHECK -> downloadProgressFromCloud() reverse.

| # | Endpoint | Direction |
|---|----------|-----------|
| 1 | FE `learning.ts` | Local enum |
| 2 | FE `supabase-sync.ts` | local -> DB |
| 3 | DB | CHECK constraint |
| 4 | FE `supabase-sync.ts` | DB -> local |

---

## Change Checklist Template

Copy into any PR that touches cross-module logic:

```markdown
### Pre-Commit Invariant Check
- [ ] Identified which INV-xx is affected
- [ ] Updated ALL sync points (see registry)
- [ ] Ran verification grep commands
- [ ] Updated this registry if sync points changed
- [ ] Tests: pnpm test + python -m pytest
```

---

## ADR-013: Workers Layer Long-term Positioning

**Status**: ACCEPTED (2026-04-07)

### Context
Three runtimes cause 7+ invariant groups requiring manual triple-sync.

### Decision
**Workers = Edge Cache + CORS Proxy + Auth Gateway.**
Workers should NOT duplicate business logic from BE (FastAPI).

### Rationale
1. Workers duplicate dialogue/learning/assessment logic from BE
2. Duplication is root cause of all 7 invariant groups
3. Workers value = edge latency + CORS bypass, not business logic
4. FastAPI is authoritative; Workers should proxy

### Migration Path
- **Phase A**: Workers proxy `/api/*` to FastAPI (zero business logic)
- **Phase B**: Add edge caching (Cloudflare KV) for read-heavy endpoints
- **Phase C**: Auth token validation only (JWT verify at edge)

### Exception
Direct-LLM mode (FE -> OpenRouter) bypasses both layers by design (ADR-010).