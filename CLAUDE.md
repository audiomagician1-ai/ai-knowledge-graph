# CLAUDE.md — AI知识图谱 项目大脑

> 每次新对话或 context 压缩后，必须首先读取本文件。
> 本文件是项目级持久记忆，不受上下文压缩影响。
> 详细 历史记录见 docs/history/CHANGELOG-2026.md

---

## 1. PRIME DIRECTIVE（最高优先级 — 必读）

### ⚠️⚠️⚠️ UI间距纪律 — 最高优先级 ⚠️⚠️⚠️

> **这是反复犯过的错误，必须在每次UI开发前重新阅读！**
>
> **规则**：所有UI组件必须有合理的 `padding`、`margin`、`gap` 间距。禁止出现以下情况：
> 1. 元素之间**零间距**或间距不一致
> 2. 文字紧贴容器边缘无呼吸空间
> 3. 按钮/卡片之间间距不均匀
> 4. 新增组件不考虑与周围元素的间距关系
>
> **检查清单**（每次UI改动后必须自查）：
> - [ ] 组件内部 padding ≥ 8px
> - [ ] 同级元素间 gap/margin 统一（使用 Tailwind gap-* 或一致的 px 值）
> - [ ] 按钮组中所有按钮尺寸/间距对称
> - [ ] 浮层/弹窗/面板四周有至少 12px padding
> - [ ] 文字与图标之间有 4-8px gap

### 🚨🚨🚨 Bug修复全流程纪律（强制执行）🚨🚨🚨

> **事故教训**：Hub bar UI修复 commit 后未 push，导致线上未部署，用户投诉。
>
> **所有 Bug 必须走完以下全流程**：
> 1. **创建 GitHub Issue** — 标题含 `[Bug]` 前缀，body 含复现步骤/预期/实际行为
> 2. **本地修复** — commit message 引用 Issue 编号: `fix(scope): description #N`
> 3. **验证** — `pnpm build` + `pnpm test` 通过
> 4. **⚠️ 立即 `git push`** — commit ≠ 部署！不 push = CI/CD 不触发 = 用户看不到修复
> 5. **确认部署** — 检查 [GitHub Actions](https://github.com/audiomagician1-ai/ai-knowledge-graph/actions) 运行状态
> 6. **线上验证** — 访问 https://akg-web.pages.dev 确认修复生效
> 7. **关闭 Issue**

---
## 2. PROJECT IDENTITY（项目基本面）

**产品**: AI知识图谱 — 交互式教学+苏格拉底式对话+知识图谱技能树点亮学习平台
**核心理念**: AI先讲解知识 → 提供选项引导互动 → 探测用户水平 → 自适应深度讲解 → 选项式理解检验 → 评估点亮
**GitHub**: https://github.com/audiomagician1-ai/ai-knowledge-graph
**线上**: https://akg-web.pages.dev

**技术栈**:
- **前端**: React 19 + TypeScript 5.7 + Vite 6 + TailwindCSS 4 + Zustand 5 + Three.js/3d-force-graph + Framer Motion + Lucide React
- **后端**: FastAPI (Python 3.11+) — 图谱引擎/对话引擎/学习引擎
- **数据库**: Neo4j 5 (知识图谱) + PostgreSQL 15 via Supabase (用户/学习数据) + Redis 7 (缓存)
- **移动端**: Capacitor 8 (Android/iOS)
- **BaaS**: Supabase (Auth + PostgreSQL + Edge Functions + Storage)
- **LLM**: 分层调度 (DeepSeek/GPT-4o-mini/GPT-4o) via OpenRouter; 默认免费: stepfun/step-3.5-flash:free
- **部署**: Cloudflare Pages (前端) + Docker (后端) + Supabase Cloud

**架构**: pnpm monorepo
```
packages/web/      — Vite + React 前端 (@akg/web)
packages/shared/   — 共享类型/常量 (@akg/shared)
packages/mobile/   — Capacitor 移动端 (@akg/mobile)
apps/api/          — FastAPI 后端 (图谱+对话+学习引擎)
workers/           — Cloudflare Workers (代理API)
supabase/          — Auth + PostgreSQL + Edge Functions
data/seed/         — 种子图谱数据 (36球)
data/rag/          — RAG知识文档 (6,300篇)
```

---

## 3. CURRENT METRICS（当前指标）

| 指标 | 值 | 更新日期 |
|------|------|----------|
| **知识球** | 36 个知识球 | 2026-04-07 |
| **知识概念** | 6,300 | 2026-04-07 |
| **边** | 7,167 | 2026-04-07 |
| **跨球链接** | 633 (0 断引用) | 2026-04-07 |
| **RAG 覆盖** | 6,300 (100% 覆盖) | 2026-04-07 |
| **测试总数** | 1,382 (1,006 BE + 329 FE + 47 E2E) | 2026-04-07 |
| **tsc errors** | 0 | 2026-04-07 |
| **Open Issues** | 0 | 2026-04-07 |
| **RAG 质量** | 6,300 docs — legacy 6,156 avg 79.5 + new 144 avg 84.0 → global avg 79.6 | 2026-04-07 |

---

## 4. CURRENT P0 TASKS（当前优先任务）

### RAG 知识库质量 迭代

> 详情 见 docs/RAG_EVOLUTION_PLAN.md
>
> **Scorer v2.0** 重评: ai-rewrite-v1 原始均分44.9 → 迭代改写后均分77.8
>
> | Sprint | 状态 | 内容 |
> |--------|------|------|
> | Sprint 0-4 | ✅ | Schema v2 + Scorer + 手动精写 + research-rewrite + ai-rewrite + Tier-C消除 |
> | Sprint 5 | ✅ | intranet-llm-rewrite-v2 Tier-B批量提升 (Batch 1-3 + P2) |
> | Sprint 6 | ✅ | 全量Tier-B升级 — 3353/3353完成 (100%), 0 errors |
> | Sprint 6.5 | ✅ | 全量rescore完成 — 6156/6156 (100%), avg 78.4, 0 pending |
> | Sprint 7 | ✅ | Tier-S Booster — 416/425 完成 (98%), 9 skipped (name mismatch), S:706→1096, avg 78.5→79.5 |
> | Sprint 8 | ✅ | 6新域144篇全量升级 (ST 86.0, CB 84.1, IT 84.8, DS 83.9, SY 83.8, CT 81.5), 新域avg 84.0 |
> | Sprint 9 | 进行中 | Legacy底部200篇targeted boost (目标: global avg 79.6→80+) |
>
> **目标**: 全量v2覆盖 + 均分80+ ← 当前 79.6 (Sprint 9进行中)
> **脚本**: scripts/_batch_sprint6.py, scripts/_batch_sprint6_5.py, scripts/_batch_tier_b_parallel.py, scripts/_batch_tier_s_booster.py

### V1.0 剩余任务
- ✅ FSRS 间隔重复引擎 (#34/#35)
- ✅ BKT 知识追踪引擎 (#36)
- ✅ 成就系统 + UI (#37/#38)
- ✅ 统一日志系统 (FE 23模块 + BE 16模块)
- ✅ FSRS 复习UI集成 (ReviewPage + Hub按钮 + API客户端 + 8测试)

### 审计 Issues 修复 Sprint
- ✅ #45 LLM响应缓存 (Redis, 19 tests)
- ✅ #50 DEVELOPMENT_PLAN.md v2.0 全量重写
- ✅ #48 SSR/SEO (OG/meta/robots/sitemap + ADR-012)
- ✅ #51 审计报告总结 (整合进开发计划)
- ✅ #44 三端同步治理 (CROSS_MODULE_INVARIANTS.md + ADR-013)
- ✅ #42 图谱引擎实现 (pathfinder + builder + 7 API + 40 tests)
- ✅ #43 GraphRAG独立模块 (rag.py: 精确+模糊+搜索, ADR-014)
- ✅ #46 学习分析Dashboard (DashboardPage + 全局统计/掌握度分布/活动趋势/域进度卡片)
- ✅ #49 OAuth代码已完成 (待Supabase Dashboard配置)
- ✅ #47 E2E测试框架 (Playwright + 10个核心用户流测试)

### 行为设计优化 Sprint (基于 BEHAVIOR_DESIGN_AUDIT.md)
- ✅ 6新域完整集成 (systems-theory家族: seed+RAG+Workers+cross-links+supplements 三端同步)
- ✅ P0 首页引导层 (WelcomeGuide: 价值主张+推荐域快速开始, 首访弹窗)
- ✅ P0 回访提示体系 (ReviewBanner: FSRS复习提醒+学习进度+连续天数)
- ✅ P1 评估后终点重设计 (庆祝动效+推荐下一个概念+三按钮布局)
- ✅ 38条跨球链接 (595→633, 6新域互联+与现有域关联)
- ✅ 12个领域教学/评估Prompt补充 (三端同步: BE+FE+Workers)
- ✅ P2 社交证明层 ("X人在学" 气泡标注 + DomainOverview + Dashboard)
- ✅ P2 学习日历热力图 (30天StreakCalendar + 连续学习徽章)
- ✅ P2 每日推荐概念 (DailyRecommendation: 30精选概念日轮推荐)

---

## 5. ACTIVE DECISIONS（生效中的架构决策）

| ID | 决策 | 理由 |
|----|------|------|
| ADR-001 | Supabase 做 Auth/用户数据/RLS | 对齐 MuseSea 验证过的架构 |
| ADR-002 | FastAPI 独立后端 (非纯 BaaS) | 知识图谱需要 Neo4j + 复杂 LLM 编排 |
| ADR-003 | Neo4j 做知识图谱 | Cypher 查询语言成熟，图遍历性能优 |
| ADR-004 | 前端 Vite+React (非 Next.js) | 对齐 MuseSea 工具链，Capacitor 兼容好 |
| ADR-005 | Capacitor 做移动端 (非 RN) | 对齐 MuseSea，共享同一套 Web 代码 |
| ADR-006 | 深色主题优先 | 知识宇宙主题，对齐Observatory Study 风格 |
| ADR-007 | FSRS 间隔重复 (非 SM-2) | 97.4% 优于 SM-2，Anki 已默认采用 |
| ADR-009 | 全站免登录可用 | MVP阶段降低门槛，匿名即可体验全部功能 |
| ADR-010 | 默认免费 LLM + 可选自带 Key | stepfun/step-3.5-flash:free 作为默认后端 |
| ADR-011 | 登录用户 Supabase-first 持久化 | 登录用户数据以 Supabase Cloud 为权威源 |
| ADR-012 | SPA保留 + OG/meta SEO + 未来预渲染 | 迁移成本高,当前用户获取非SEO依赖,OG tags先行 |
| ADR-013 | Workers = Edge Cache + CORS Proxy | Workers不复制业务逻辑,长期转为纯代理层 |
| ADR-014 | RAG: 精确匹配优先 + 模糊fallback | 97.7%概念有精确匹配,向量检索ROI不足暂缓 |
| ADR-015 | 路由级代码分割 + PWA | React.lazy减60%初始bundle,PWA manifest可安装性,Capacitor平台抽象层统一web/native |

---
## 6. CROSS-MODULE INVARIANTS（跨模块不变量清单）

> 以下 规则同时存在于多个文件中，修改时必须同步所有出处。

### Mastered 判定阈值 (7处同步)
```
overall >= 75 AND all dimensions >= 60
```
- FE: direct-llm.ts (validateAssessment + fallback)
- FE: learning.ts (recordAssessment)
- BE: evaluator.py (validate_result + fallback_evaluate)
- BE: sqlite_client.py (record_assessment)
- Workers: dialogue.ts (validateAssessment + fallback)

### Mastered 降级防护 (8处同步)
已mastered的概念不允许被降级回learning/not_started:
- FE: learning.ts (startLearning + recordAssessment wasMastered guard)
- FE: supabase-sync.ts (toDbStatus mapping)
- BE: sqlite_client.py (start_learning + record_assessment C-06)
- BE: learning.py /sync (mastered guard)
- Workers: learning.ts (/start + /assess + /sync mastered CASE)

### tokenLimitParam (4处同步)
OpenAI o1/o3/chatgpt-* 专用: max_completion_tokens 替代 max_tokens
- FE: direct-llm.ts + settings.ts (regex o[1-9]|chatgpt-)
- BE: llm/router.py (re.match o[1-9]|chatgpt-)
- Workers: llm.ts (regex o[1-9]|chatgpt-)

### validateAssessment (3处同步)
Score clamping [0,100] + mastered recalc + null/异常值 → fallback 50:
- FE: direct-llm.ts (Number.isFinite)
- BE: evaluator.py (int(float()) try/except)
- Workers: dialogue.ts (Number.isFinite)

### DOMAIN_SUPPLEMENTS / ASSESSMENT_SUPPLEMENTS (三端同步)
新增域时必须同步补充注册到以下三处:
- BE: pps/api/engines/dialogue/prompts/feynman_system.py
- FE: packages/web/src/lib/direct-llm.ts
- Workers: workers/src/prompts.ts

### 对话截断 (3处同步)
8000字符上限, push+reverse O(n):
- FE: direct-llm.ts
- BE: evaluator.py (_format_dialogue)
- Workers: dialogue.ts

### Status Mapping (四端一致)
learning.ts local → toDbStatus() → DB CHECK → downloadProgressFromCloud() reverse

---

## 7. CODING STANDARDS（编码规范）

### 代码规范
- JS/TS ≤ 800行, React组件 ≤ 200行, 超限必须拆分
- 颜色使用 CSS 变量 (--color-*), 禁止硬编码 hex
- 编译器 0 个 s any (除 supabase-sync.ts enum转换 + learning.ts diagnostics 豁免)
- 禁止使用 eval/exec/innerHTML/dangerouslySetInnerHTML

### 安全规范
- 禁 前端硬编码 LLM API Key
- 禁 绕过或关闭 RLS 策略（除管理员迁移）
- 禁 图遍历深度超过 depth=3
- ✅ SSRF 防护: BE _validate_base_url + Workers validateBaseUrl (private IP blocked)
- ✅ CORS: URL-parsed hostname白名单校验 (非substring)

### 移动端适配规范
- 全局 使用 min-h-dvh 替代 min-h-screen
- 触摸 目标区域 ≥ 44px
- 使用 safe-area 环境 CSS 变量
- 测试 ≥375px 及 ≥390px 的 @media 断点布局

---

## 8. COMMANDS（常用命令）

```bash
# 开发
pnpm dev                    # 启动 dev server (port 3000)
pnpm api:dev                # FastAPI dev server (port 8000)
pnpm docker:up              # 启动 Neo4j + Redis
pnpm build                  # 生产构建

# 测试
cd packages/web && npx vitest run        # 前端测试
cd apps/api && python -m pytest          # 后端测试
npx playwright test                      # E2E测试 (需先 pnpm dev)

# 类型检查
pnpm type-check             # 全量 tsc

# 部署
git add -A ; git commit -m "feat(scope): desc" ; git push
# → GitHub Actions 自动构建 → Cloudflare Pages

# EXE 打包
python scripts/build_exe.py  # 输出到 release/
```

### 提交规范
- 格式: `feat(scope): description` 或 `fix(scope): description #N`
- scope: graph / dialogue / learning / ui / auth / infra
- 提交前必须: pnpm type-check + 相关测试通过
- **修复类 commit 必须立即 git push**

---
## 9. KEY FILES INDEX（关键文件索引）

### 文档
| 文件 | 用途 |
|------|------|
| DEVELOPMENT_PLAN.md | MVP定义/技术架构/里程碑/成本估算 |
| RESEARCH_REPORT.md | 市场分析/竞品/教育理论/技术可行性 |
| docs/EXPANSION_PLAN.md | 多球体扩展路线 + 30球体详情 |
| docs/RAG_EVOLUTION_PLAN.md | RAG知识库质量迭代进化方案 |
| docs/history/CHANGELOG-2026.md | 所有Phase/Sprint/CR详细记录 |
| docs/BEHAVIOR_DESIGN_AUDIT.md | 行为设计审计报告(B=MAP+SDT+双系统+行为经济学+JTBD多透镜诊断) — P0:首页引导+回访提示+推荐锚点, P1:Aha Moment缩短+进度可见+评估终点重设计 |
| docs/CROSS_MODULE_INVARIANTS.md | 三端同步不变量手册(7组INV) + 变更检查清单 + ADR-013 |

### 数据
| 文件 | 用途 |
|------|------|
| data/seed/domains.json | 36球体定义 (id/name/icon/color/sort_order) |
| data/seed/{domain}/seed_graph.json | 各域种子图谱 |
| data/seed/cross_sphere_links.json | 633条跨球链接 |
| data/rag/{domain}/{subdomain}/{concept}.md | RAG知识文档 |

### 核心代码
| 文件 | 用途 |
|------|------|
| pps/api/engines/dialogue/ | 对话引擎主逻辑 + Feynman提示 |
| pps/api/engines/learning/ | 学习引擎 + BKT + FSRS |
| pps/api/engines/graph/pathfinder.py | 路径计算器: 拓扑排序+最短路径+推荐+前置验证 |
| pps/api/engines/graph/builder.py | 图谱构建器: ZPD子图+实体对齐+学习区域摘要 |
| pps/api/engines/graph/rag.py | RAG检索模块: 精确匹配+模糊fallback+搜索 |
| pps/api/routers/ | graph/dialogue/learning API |
| pps/api/llm/router.py | LLM路由器 (SSRF/retry/tier) |
| pps/api/rate_limiter.py | 请求频率限制器 |
| packages/web/src/lib/store/ | Zustand stores (dialogue/learning/domain/graph) |
| packages/web/src/lib/direct-llm.ts | 前端直连LLM (888行, 含validateAssessment) |
| packages/web/src/components/common/WelcomeGuide.tsx | 首访引导层 (价值主张+推荐域) |
| packages/web/src/components/common/ReviewBanner.tsx | FSRS复习提示+学习进度 |
| packages/web/src/components/common/DailyRecommendation.tsx | 每日推荐概念 (30概念日轮) |
| packages/web/src/pages/DashboardPage.tsx | 学习分析面板 (含StreakCalendar) |
| packages/web/src/pages/SettingsPage.tsx | 独立设置页面 (/settings) |
| packages/web/src/pages/NotFoundPage.tsx | 404 页面 (渐变标题+导航) |
| packages/web/src/lib/utils/capacitor.ts | Capacitor平台抽象层 (storage/keyboard/lifecycle) |
| packages/web/src/lib/utils/perf-monitor.ts | Core Web Vitals 监控 (FCP/LCP/TTFB) |
| packages/web/src/lib/hooks/ | useAppLifecycle + useBackButton + useKeyboardHeight + useOnlineStatus + useKeyboardShortcuts + useLocalStorage + useLearningTimer (barrel: hooks/index.ts) |
| packages/web/src/lib/utils/fetch-retry.ts | fetchWithRetry: 指数退避 + 抖动 + Retry-After + abort signal |
| packages/web/src/components/common/OfflineIndicator.tsx | 离线状态提示横幅 (useSyncExternalStore) |
| packages/web/src/components/common/KeyboardShortcutsHelp.tsx | 全局键盘快捷键帮助弹窗 (Shift+?) |
| packages/web/src/components/common/ConceptSearch.tsx | 全局概念搜索 (Ctrl+K, 支持↑↓Enter导航) |
| apps/api/utils/metrics.py | API指标收集器 (请求数/错误率/响应时间/per-endpoint) |
| workers/src/ | Cloudflare Workers代理后端 |

---

## 10. KNOWN ISSUES / NOTES

- OAuth: Supabase Cloud控制台配置待完成 (代码层面已就绪)
- RAG: 向量语义检索保留为Phase 2 (ADR-014), 当前精确+模糊覆盖97.7%
- RAG: 6个systems-theory家族新域RAG升级 ✅ 144/144 完成 (ST 86.0, CB 84.1, IT 84.8, DS 83.9, SY 83.8, CT 81.5), 新域均分 84.0
- dialogue-api.ts 导出但无import (dialogue.ts直接fetch), future-ready
- useMediaQuery.ts 暂时unused (Round 74保留), future-ready
- NPM audit: 6漏洞(4moderate+2high)均属workers>wrangler dev依赖, 不影响生产
- data/scripts/ 目录含已完成脚本 data/seed/programming/, 保留供参考
- Vite warning: learning.ts 循环依赖+未用import (不影响运行), cosmetic

### V1.3 Performance & Mobile Sprint ✅ (2026-04-07)
- ✅ 路由级代码分割 (React.lazy 7个lazy页面, 初始bundle减60%)
- ✅ GZip压缩中间件 + Cache-Control (1h cache + SWR 24h on static endpoints)
- ✅ Core Web Vitals监控 (FCP/LCP/TTFB via PerformanceObserver)
- ✅ PWA Web App Manifest (standalone display, iOS meta tags)
- ✅ Service Worker (离线缓存: cache-first for assets, network-first for API)
- ✅ Capacitor平台抽象层 (storage/keyboard/statusbar/lifecycle)
- ✅ useAppLifecycle hook (foreground auto-refresh streak)
- ✅ useBackButton + useKeyboardHeight + useOnlineStatus hooks
- ✅ useKeyboardShortcuts hook (Ctrl/Cmd/Shift modifier, input-aware)
- ✅ useLocalStorage hook (type-safe persisted state)
- ✅ useLearningTimer hook (5s粒度学习时间追踪, 90天留存)
- ✅ fetchWithRetry utility (exponential backoff + jitter + Retry-After)
- ✅ OfflineIndicator全局组件 (useSyncExternalStore)
- ✅ KeyboardShortcutsHelp全局帮助弹窗 (Shift+?, D/G/S/H/Esc快捷键)
- ✅ SettingsPage独立路由 (/settings)
- ✅ 404 NotFoundPage
- ✅ /health/system全组件健康检查端点
- ✅ /health/metrics API指标端点 (请求数/错误率/响应时间)
- ✅ /health/project 项目统计端点 (域/概念/边/RAG覆盖率)
- ✅ /learning/export + /learning/import数据导出导入 (GDPR + roundtrip)
- ✅ RequestIdMiddleware (X-Request-ID + X-Response-Time + 慢请求日志)
- ✅ 无障碍: skip-to-content链接 + aria labels + main landmark role
- ✅ 移动端: safe-area-inset-bottom for LearnPage聊天输入
- ✅ Hooks桶导出 (hooks/index.ts: 9个自定义hook统一导出)
- ✅ Dashboard学习时间展示 (今日/累计分钟/小时)
- ✅ 144/144新域RAG全量升级 (ST 86.0, CB 84.1, IT 84.8, DS 83.9, SY 83.8, CT 81.5)

## Last Review

**Date**: 2026-04-07 | **Scope**: V1.3 COMPLETE + V2.0 prep — ConceptSearch (Ctrl+K) + ErrorBoundary retry + KeyboardShortcutsHelp + useLearningTimer + 10 navigation E2E specs + legacy RAG booster launched (target: global avg 80+) | **Result**: 1,006 BE + 329 FE + 47 E2E all pass, tsc: 0 errors, 0 open issues, build OK