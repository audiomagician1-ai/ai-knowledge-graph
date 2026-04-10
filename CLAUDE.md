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
| **测试总数** | 2,299 (1,468 BE + 770 FE + 61 E2E) | 2026-04-10 |
| **tsc errors** | 0 | 2026-04-10 |
| **Open Issues** | 0 | 2026-04-10 |
| **RAG 质量** | 6,300 docs — Sprint 10 ✅ (90/80), global avg **80.0** ✅ (S:1298 A:5002 B/C:0) | 2026-04-07 |

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
> | Sprint 9 | ✅ | Legacy底部200篇targeted boost (200/200完成, 0 errors, global avg 79.6→79.9) |
> | Sprint 10 | ✅ | 底部90篇定向改写 (90/80 超额, sfx+game-design+SE+technical-art+version-control), global avg **80.0** |
>
> **目标**: 全量v2覆盖 + 均分80+ ← ✅ **达成 80.0** (Sprint 10完成, S:1298 A:5002 B/C:0)
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

### V2.1 Graph可视化增强 Sprint (2026-04-07, 进行中)
- ✅ GraphMiniStats HUD (域名+进度环+掌握/学习/未开始统计+连续天数)
- ✅ GraphLegend 图例 (可折叠，展示状态颜色+难度颜色+交互提示)
- ✅ SubdomainFilter 子域筛选 (下拉列表+掌握度统计+高亮切换)
- ✅ ConceptTooltip 悬浮提示 (概念名称+状态+难度+时间+推荐标记)
- ✅ Topology API (GET /api/graph/topology/{domain_id}: 子域统计/入口节点/终端节点/孤立节点/里程碑/连接度TOP10)
- ✅ DomainComparison Dashboard组件 (12域规模对比柱状图+进度条)
- ✅ ConceptPrerequisites面板 (前置知识+后续解锁+导航, 集成到ChatPanel idle视图)
- ✅ ConceptMinimap (子域概念导航地图, 状态颜色+进度指示器)
- ✅ GraphBreadcrumb (面包屑导航: 首页>域>子域>概念, chat模式显示)
- ✅ ShareProgress (学习进度分享: 复制+推特+下载, Dashboard集成)
- ✅ Concept Context API (GET /api/graph/concepts/{id}/context: 前置/后续/相关/子域兄弟)
- ✅ Hub栏交流按钮 → 导航到 /community (修复TODO)
- ✅ SmartNextSteps智能推荐 (分析图谱+进度推荐下一步: 继续学习/解锁新概念/里程碑接近/复习)
- ✅ useGraphKeyNav键盘导航 (ArrowKeys箭头键在连接节点间导航, Enter学习, Esc取消)
- ✅ RAG Sprint 10 完成: 90/80 超额 → 全局avg **80.0** 达成
- ✅ ConceptCompare API + 组件 (概念对比: 连接/前置/相似度 + route fix)

### V2.1 分析与智能增强 Sprint (2026-04-07, 进行中)
- ✅ AI自动审核 (POST /community/suggestions/{id}/auto-moderate: 启发式质量评分+垃圾检测+批量审核)
- ✅ 周报分析 (GET /analytics/weekly-report: WoW对比+增量百分比+总览)
- ✅ 学习习惯分析 (GET /analytics/study-patterns: 24h分布+周分布+一致性评分+峰值时段)
- ✅ WeeklyReport Dashboard组件 (WoW指标卡+增量badge+总体统计)
- ✅ StudyPatterns Dashboard组件 (24h热力图+周柱状图+峰值badge)
- ✅ 笔记导出 (GET /notes/export/markdown + /notes/export/json: 全量导出+备份)
- ✅ Graph LOD系统 (graph-lod.ts: 子域聚类+节点优先级+大域性能优化)
- ✅ 概念书签 (useBookmarks: localStorage持久化+100上限+toggle+桶导出)
- ✅ Streak里程碑奖励 (StreakRewards: 7个里程碑badge+进度条+compact/full模式)
- ✅ 笔记页Markdown导出按钮 (NotesPage: 同步后端→导出.md文件)

### V2.2 Dashboard增强 Sprint (2026-04-07, 完成)
- ✅ Global Stats API (GET /api/graph/stats/global: 跨域聚合统计)
- ✅ DomainRadar SVG雷达图 (掌握度分布: 纯SVG无依赖+8轴上限+百分比标注)
- ✅ DifficultyHeatmap 难度热力图 (8域 per-difficulty分布, color-mix渐变)
- ✅ MilestoneTracker 里程碑追踪 (25/50/75/100%域里程碑, 即将达成+已达成)

### V2.3 Adaptive Learning Intelligence Sprint (2026-04-10, 完成)
- ✅ Pathfinder.adaptive_path() — 融合 FSRS复习+知识缺口+前沿学习 三信号优先队列
- ✅ Pathfinder.knowledge_gaps() — 拓扑感知前置知识缺口检测 (按解锁数排序)
- ✅ GET /api/learning/adaptive-path/{domain} — 个性化自适应学习路径 API
- ✅ GET /api/learning/knowledge-gaps/{domain} — 知识缺口检测 API
- ✅ AdaptivePathWidget Dashboard组件 (智能学习路径: 复习/补缺/新学三类步骤)
- ✅ ReviewQueue Dashboard组件 (FSRS复习队列: 逾期分级+稳定性+次数)
- ✅ LearningPathPage知识缺口板块 (优先补齐→解锁更多内容)
- ✅ 27 new tests (17 BE + 10 FE)

### V2.4 Performance & Code Health Sprint (2026-04-10, 完成)
- ✅ Split direct-llm.ts God File: 1,244→549+554 lines (prompt data extracted to direct-llm-prompts.ts)
- ✅ Lazy-load 9 dashboard widgets: DashboardPage chunk 51→27 kB (-47%), React.lazy + Suspense
- ✅ Dashboard batch API: GET /api/analytics/dashboard-batch (3 HTTP calls → 1, 60s cache + dedup)
- ✅ useDashboardBatch hook: module-level cache, concurrent request dedup, WeeklyReport + StudyPatterns integrated
- ✅ 4 new BE tests (batch endpoint schema validation)
- ✅ Three-way sync test updated for new file structure (direct-llm-prompts.ts)
- ✅ Split ChatPanel.tsx God File: 687→324 lines (extracted ChatHistoryView 87L + ChatIdleView 172L + InlineAssessmentCard 102L)
- ✅ Split HomePage.tsx God File: 651→278 lines (extracted home-canvas-utils.ts 218L: DEMO_DOMAINS + constants + hex grid + drawBubble)
- ✅ Split LearnPage.tsx AssessmentCard: 573→459 lines (extracted LearnAssessmentCard 114L)
- ✅ 20 new FE tests (chat-components 7 + home-canvas-utils 13)
- ✅ Split GraphPage.tsx God File: 565→185 lines (extracted GraphSearchOverlay 57L + GraphHubBar 199L + GraphRecommendPanel 79L + GraphConceptHeader 52L)
- ✅ Split KnowledgeGraph.tsx: 528→247 lines (extracted graph-visual-utils.ts 136L: GNode/GLink types + baseSize + nodeColor + labelTexture + celebration particles)
- ✅ Split DashboardPage.tsx: 493→144 lines (extracted StreakCalendar 70L + VelocitySection 76L + DashboardHelpers 76L + useDashboardProgress hook 70L)
- ✅ 22 new FE tests (graph-page-components 14 + graph-visual-utils 8)

### V2.4 Code Health Phase 4 — God File Splits (2026-04-10, 完成)
- ✅ Split LearnPage.tsx: 496→198 lines (extracted LearnHeader 67L + LearnMessageBubble 81L + LearnPostAssessment 84L + LearnGuideCard 61L + LearnInputArea 130L)
- ✅ Split SettingsContent.tsx: 478→155 lines (extracted SettingsLLMConfig 214L + SettingsDataIO 140L)
- ✅ Split CommunityPage.tsx: 408→146 lines (extracted SuggestionCard 122L + SuggestionForm 61L)
- ✅ 9 new FE tests (learn-components 5 + settings-components 2 + community-components 2)

### V2.4 Code Health Phase 5 — LoginPage + ReviewPage splits (2026-04-10, 完成)
- ✅ Split LoginPage.tsx: 362→289 lines (extracted LoginOAuthButtons 70L — OAuth buttons + Google/GitHub SVG icons)
- ✅ Split ReviewPage.tsx: 346→238 lines (extracted ReviewFlashcard 109L — progress bar + flashcard + FSRS rating buttons)
- ✅ 3 new FE tests (auth + review component exports + RATINGS validation)

### V2.4 Code Health Phase 7 — LearningPath + Dashboard + Chat splits (2026-04-10, 完成)
- ✅ Split LearningPathPage.tsx: 341→184 lines (extracted PathGroupSection 140L + KnowledgeGapsSection 52L)
- ✅ Split DashboardContent.tsx: 325→200 lines (extracted OtherDomainCard + ActivityRow + formatTimeAgo → DashboardContentParts 100L)
- ✅ Split ChatPanel.tsx: 323→114 lines (extracted ChatView 172L — full chat message list + input area + celebration overlay)
- ✅ 9 new FE tests (learning-path-components 4 + dashboard-content-parts 4 + chat-view 1)

### V2.4 Code Health Phase 8 — Achievement + StudyGoal + DomainOverview splits (2026-04-10, 完成)
- ✅ Split AchievementPanel.tsx: 259→139 lines (extracted AchievementCard + TIER_COLORS/LABELS + CATEGORY_META → AchievementParts 72L)
- ✅ Split StudyGoalWidget.tsx: 254→78 lines (extracted ProgressRing + GoalSettings → StudyGoalParts 91L)
- ✅ Split DomainOverview.tsx: 222→101 lines (extracted DomainCard 69L)
- ✅ 7 new FE tests (achievement-parts 4 + study-goal-parts 2 + domain-card 1)
- 📊 Remaining files >200L: 9 (all <290L, already split once or near boundary)

### V2.5 Learning Experience & Cross-Domain Intelligence Sprint (2026-04-10, 完成)
- ✅ GET /api/analytics/session-history: 分页学习事件时间线 (action/concept/days过滤, 分页)
- ✅ GET /api/analytics/mastery-timeline/{concept_id}: 概念掌握度时间线 (分数进展+改进量)
- ✅ GET /api/analytics/study-time-report: 每日/每周学习时间报告 (会话估算+生产力指标)
- ✅ GET /api/analytics/streak-insights: 学习习惯分析 (90天一致性+习惯分数+周分布)
- ✅ GET /api/graph/cross-domain-bridge/{concept_id}: 跨域关联概念桥接 (跨知识球探索)
- ✅ SessionHistoryPage (/history): 分页学习时间线+操作过滤+概念搜索+导航
- ✅ MasteryTimeline SVG折线图: 概念掌握度进展可视化 (集成到ChatIdleView)
- ✅ CrossDomainBridge面板: 跨域关联概念展示+域分组 (集成到ChatIdleView)
- ✅ StudyTimeChart Dashboard组件: 14天学习时间柱状图+总计/日均/活跃天
- ✅ StreakInsights Dashboard组件: 习惯分数badge+4指标网格+周分布迷你柱状图
- ✅ HomePage历史快捷导航按钮, App.tsx /history懒加载路由
- ✅ 18 BE tests + 9 FE tests = 27 new tests

### V2.6 Multi-Domain Intelligence Sprint (2026-04-10, 完成)
- ✅ GET /api/analytics/domain-recommendation: 跨域推荐 (学习历史+跨球链接+难度匹配+多样性加分)
- ✅ GET /api/analytics/study-plan: 个性化学习计划 (FSRS复习+继续学习+新概念, 每日时间预算分配)
- ✅ GET /api/analytics/learning-journey: 跨域学习旅程时间线 (成就事件+域里程碑+进度总览)
- ✅ DomainRecommendWidget Dashboard组件: 推荐探索领域 (跨域关联+原因+概念数+难度)
- ✅ StudyPlanWidget Dashboard组件: 学习计划 (日程切换+复习/继续/新学三类+时间估算)
- ✅ LearningJourneyPage (/journey): 跨域成就时间线 (域掌握度+事件过滤+里程碑徽章)
- ✅ HomePage旅程快捷导航按钮 (Map图标 → /journey)
- ✅ 16 BE tests + 10 FE tests = 26 new tests

### V2.7 Smart Analytics & Engagement Sprint (2026-04-10, 完成)
- ✅ GET /api/analytics/weak-concepts: 薄弱概念检测 (多因子弱点评分: 多次未过/分数下降/停滞/低分+可行建议)
- ✅ GET /api/analytics/learning-efficiency: 学习效率分析 (概念级效率=分数/次数+域级汇总+全局统计+掌握时间)
- ✅ GET /api/analytics/difficulty-calibration: 难度校准 (种子难度vs实际表现差异+误标概念检测+难度分布摘要)
- ✅ WeakConceptsWidget Dashboard组件: 薄弱概念警报 (分数趋势+原因标签+改进建议)
- ✅ LearningEfficiencyChart Dashboard组件: 域级效率对比 (水平条形图+全局统计卡片)
- ✅ 16 BE tests + 5 FE tests = 21 new tests

### V2.8 Social & Collaborative Learning Sprint (2026-04-10, 完成)
- ✅ GET /api/analytics/leaderboard: 真实排行榜 (4种排序: mastered/efficiency/streak/score, 上下文感知mock peers, 复合评分)
- ✅ GET /api/analytics/peer-comparison: 同伴对比 (百分位排名: 学习速度/连续天数/评分/掌握数, 4维度可视化)
- ✅ POST /api/community/discussions: 概念讨论帖 (提问/洞见/资源/解释 4类型, 投票+回复+解决标记)
- ✅ GET /api/community/discussions: 讨论列表 (concept_id/domain_id过滤, recent/popular/active排序, 分页)
- ✅ POST /api/community/discussions/{id}/reply: 讨论回复 (回复计数自动更新)
- ✅ POST /api/community/discussions/{id}/vote: 讨论投票 (+1)
- ✅ PATCH /api/community/discussions/{id}/resolve: 标记已解决
- ✅ GET /api/community/discussions/concept-activity/{id}: 概念讨论活动摘要 (类型统计+回复数+未解决问题)
- ✅ GlobalLeaderboard Dashboard组件: 社交排行榜 (排序切换+排名图标+连续天数火焰+导航, lazy-load)
- ✅ PeerComparisonCard Dashboard组件: 同伴对比卡片 (4维度百分位条形图+前X%标签, lazy-load)
- ✅ ConceptDiscussionPanel组件: 概念讨论面板 (发帖表单+类型选择+回复+投票+展开详情, 集成到ChatIdleView)
- ✅ 15 BE tests + 9 FE tests = 24 new tests

### V2.9 Advanced Search & Content Intelligence Sprint (2026-04-10, 完成)
- ✅ Split analytics.py (1,777L → 1,205L) — extracted analytics_insights.py (1,004L) for V2.7+V2.8+V2.9 endpoints
- ✅ GET /api/analytics/concept-similarity/{id}: 跨域概念相似度引擎 (共享前置/后续Jaccard + 标签重叠 + 子域加成 + 跨域桥接 + 难度相近)
- ✅ GET /api/analytics/content-search: RAG全文内容搜索 (跨36域文档内容搜索 + 名称匹配加权 + 精确短语加成 + 上下文片段提取)
- ✅ GET /api/analytics/learning-report: 综合学习报告 (全量指标聚合: 进度/领域/优势/弱点/连续/效率 + 个性化建议)
- ✅ LearningReportPage (/report): 可打印学习报告 (概览网格 + 领域进度条 + 优势/弱点分析 + 建议 + JSON导出)
- ✅ ContentSearchWidget Dashboard组件: 知识文档内容搜索 (去抖输入 + 结果预览 + 片段展示 + 导航)
- ✅ ConceptSimilarityPanel组件: 相似概念面板 (跨域标记 + 原因标签 + 难度展示, ChatIdleView集成)
- ✅ HomePage浮动导航新增"报告"按钮 (FileText图标 → /report)
- ✅ 14 BE tests + 9 FE tests = 23 new tests

### V2.10 Backend Scalability Sprint (2026-04-10, 完成)
- ✅ Split analytics.py (1,205L → 402L) — extracted analytics_experience.py (364L, V2.5) + analytics_planning.py (444L, V2.6)
- ✅ Split analytics_insights.py (1,007L → 335L) — extracted analytics_social.py (192L, V2.8) + analytics_search.py (460L, V2.9)
- ✅ Created analytics_utils.py (54L) — shared load_seed_metadata() helper, DRY across 4 routers
- ✅ Split graph.py (1,102L → 696L) — extracted graph_advanced.py (487L, V2.1+: topology/context/compare/cross-domain/global-stats)
- ✅ Split learning.py (1,062L → 752L) — extracted learning_extended.py (345L: export/import/adaptive-path/knowledge-gaps)
- ✅ All 16 BE routers now under 800-line Python limit (max: 752L learning.py)
- ✅ Fixed test_analytics_v28.py peer-comparison assertion (comparison_labels → summary, mastery_speed → learn_speed_per_week)
- ✅ 1,192 BE tests pass, 641 FE tests pass, tsc 0 errors, pnpm build success

### V2.11 Notification Center & Content Quality Feedback Sprint (2026-04-10, 完成)
- ✅ GET /api/notifications: 通知列表 (未读过滤+类型过滤+分页+时间倒序)
- ✅ POST /api/notifications/{id}/read: 标记单条已读
- ✅ POST /api/notifications/read-all: 全部标记已读
- ✅ DELETE /api/notifications/{id}: 删除通知
- ✅ GET /api/notifications/summary: 通知摘要 (按类型统计+未读数)
- ✅ POST /api/notifications/generate: 生成示例通知 (6种类型: mastery/streak/review_due/milestone/weekly_report/recommendation)
- ✅ POST /api/community/content-feedback: 内容质量反馈 (5类: 不准确/已过时/不清楚/不完整/很棒)
- ✅ GET /api/community/content-feedback: 反馈列表 (concept/domain/category/unresolved过滤)
- ✅ PATCH /api/community/content-feedback/{id}/resolve: 管理员解决反馈
- ✅ GET /api/community/content-health: 内容健康总览 (概念级反馈聚合+健康分+紧迫度排序)
- ✅ NotificationsPage (/notifications): 全页通知中心 (类型过滤+已读/删除+深链接导航)
- ✅ NotificationCenter组件: Bell图标+未读徽章+下拉通知面板 (60s轮询+点击外关闭)
- ✅ ContentFeedbackButton组件: 内联内容反馈按钮 (展开表单+5类别选择+可选评论, ChatIdleView集成)
- ✅ ContentHealthWidget Dashboard组件: 内容健康总览 (反馈统计+待处理+健康分+概念列表, lazy-load)
- ✅ HomePage浮动导航新增"通知"快捷按钮 (Bell图标 → /notifications)
- ✅ App.tsx注册 /notifications 懒加载路由
- ✅ create_notification() 编程式帮助函数 (可从其他路由器调用)
- ✅ 内容反馈自动触发通知 (提交反馈后自动创建通知)
- ✅ 13 BE tests (notifications) + 10 BE tests (content-feedback) + 11 FE tests = 34 new tests

### V4.4 Learning Calendar + Knowledge Map Exploration Sprint (2026-04-10, 完成)
- ✅ GET /api/analytics/learning-calendar: 月度学习日历 (每日活动+掌握+FSRS复习投影+GitHub-style强度0-4+未来30天复习预测)
- ✅ GET /api/analytics/knowledge-map-stats: 知识图谱探索统计 (覆盖率+掌握率+领域探索度+难度分布+深度/广度得分+探索风格检测)
- ✅ LearningCalendarWidget Dashboard组件: 学习日历 (月度色阶网格+hover工具提示+事件/掌握/复习统计+图例, lazy-load, 133L)
- ✅ KnowledgeMapWidget Dashboard组件: 知识图谱探索 (渐变覆盖率进度条+统计网格+Top域列表+难度分布迷你柱图+探索风格标签, lazy-load, 120L)
- ✅ DashboardWidgetGrid集成: 43 lazy-loaded widgets (新增LearningCalendarWidget到analytics区, KnowledgeMapWidget到domains区, 184L)
- ✅ Fixed stale V3.9 size-check test (analytics_experience 500→800L universal limit)
- ✅ 13 BE tests + 18 FE tests = 31 new tests

### V4.3 Difficulty Tuner Widget + Portfolio Export Widget Sprint (2026-04-10, 完成)
- ✅ DifficultyTunerWidget Dashboard组件: 难度校准建议可视化 (偏简单/偏困难方向箭头+难度变化值+置信度百分比+高置信警告+概念导航, lazy-load, 89L)
- ✅ PortfolioExportWidget Dashboard组件: 学习档案预览+导出 (概览网格+Top域技能雷达进度条+强项/成长空间+Markdown导出+JSON导出, lazy-load, 155L)
- ✅ DashboardWidgetGrid集成: 41→43 lazy-loaded widgets (新增DifficultyTunerWidget到domains区, PortfolioExportWidget到learning区, 180L)
- ✅ 15 BE tests + 17 FE tests = 32 new tests

### V4.2 Quick Actions + Learning Portfolio + Difficulty Tuner Sprint (2026-04-10, 完成)
- ✅ QuickActionsBar组件: Dashboard顶部智能快捷操作 (复习/继续学习/探索新域, 基于study-plan+due+recommendation API上下文感知, 100L)
- ✅ GET /api/learning/portfolio: 综合学习档案导出 (技能雷达+成就里程碑+强弱项+学习时间线+总览统计, 可用于简历/分享)
- ✅ GET /api/analytics/difficulty-tuner: 难度自动校准建议 (seed难度vs实际表现偏差检测+方向/置信度+建议新难度值)
- ✅ DashboardPage集成QuickActionsBar (Global Stats下方, 136L)
- ✅ Fixed V3.8 stale size-check tests (learning_extended/analytics_insights limits → 800L universal)
- ✅ 14 BE tests + 3 FE tests = 17 new tests

### V4.1 Error Resilience + Latency Monitoring + API Health Sprint (2026-04-10, 完成)
- ✅ WidgetErrorBoundary: 每个Dashboard widget独立错误隔离 (crash→compact错误卡+重试按钮, 不影响其他widget)
- ✅ DashboardWidgetGrid重构: Suspense→W helper (ErrorBoundary+Suspense双层包裹, 41个widget全覆盖, 174→176L)
- ✅ GET /api/health/latency-report: API延迟报告 (慢端点TOP10+高错误率端点+全局统计, 基于metrics collector)
- ✅ ApiHealthWidget Dashboard组件: API系统健康 (端点数/请求数/延迟/错误率+慢端点列表+错误警报, lazy-load, 107L)
- ✅ DashboardWidgetGrid: 41→42 lazy-loaded widgets (added ApiHealthWidget to analytics section)
- ✅ 7 BE tests + 6 FE tests = 13 new tests

### V4.0 Dashboard Customization + API Catalog + Code Health Sprint (2026-04-10, 完成)
- ✅ Split analytics_planning.py (800L→625L) — extracted analytics_advanced.py (187L: V3.9 cross-domain-insights + learning-style)
- ✅ GET /api/health/api-catalog: API目录端点 (枚举所有注册路由+方法/路径/名称/标签, 按tag分组)
- ✅ useDashboardPrefs hook: Dashboard布局偏好持久化 (显示/隐藏/排序section, localStorage, useSyncExternalStore)
- ✅ DashboardCustomizer组件: Dashboard自定义面板 (眼睛toggle+上下移动+重置默认, 82L)
- ✅ DashboardWidgetGrid重构: 静态section → SECTION_MAP + prefs驱动渲染 (136→165L)
- ✅ All 26 BE routers under 800-line limit (max: 696L graph.py)
- ✅ 16 BE tests + 6 FE tests = 22 new tests

### V3.9 Code Health + Cross-Domain Insights + Learning Style Sprint (2026-04-10, 完成)
- ✅ Split analytics_experience.py (792L→474L) — extracted analytics_profile.py (284L: V3.7 learning-profile + V3.8 concept-journey + learning-heatmap)
- ✅ analytics_planning.py docstring compacted + V3.9 endpoints added (633→799L)
- ✅ GET /api/analytics/cross-domain-insights: 跨域知识迁移分析 (域对共享链接+迁移分数+协同推荐+下一步建议)
- ✅ GET /api/analytics/learning-style: 学习风格检测 (速度/深度+时间偏好+域广度+一致性+风格标签+特质分析)
- ✅ CrossDomainInsightsWidget Dashboard组件: 跨域关联 (域对链接条+协同推荐+链接计数, lazy-load, 93L)
- ✅ LearningStyleWidget Dashboard组件: 学习风格 (风格标签+特质chips+时间分布柱图+指标网格, lazy-load, 112L)
- ✅ DashboardWidgetGrid updated: 39→41 lazy-loaded widgets (added CrossDomainInsightsWidget + LearningStyleWidget)
- ✅ All 25 BE routers under 800-line limit (max: 799L analytics_planning.py)
- ✅ 25 new tests (18 BE: 6 split-verify + 3 profile-regression + 4 cross-domain + 5 learning-style + 7 FE)

- ✅ Split learning_extended.py (708L→480L) — extracted learning_intelligence.py (253L: V3.2 review-priority + V3.5 session-replay)
- ✅ Split analytics_insights.py (703L→337L) — extracted analytics_forecast.py (389L: V3.2 mastery-forecast + V3.6 fsrs-insights + goal-recommendations)
- ✅ analytics_experience.py docstring compacted (801→792L) after adding new V3.8 endpoints
- ✅ GET /api/analytics/concept-journey/{concept_id}: 概念完整学习旅程 (评估时间线+分数趋势+里程碑+域上下文+统计)
- ✅ GET /api/analytics/learning-heatmap/{domain_id}: 域学习热力图 (子域×概念2D活动强度+覆盖率+掌握率)
- ✅ ConceptJourneyWidget Dashboard组件: 概念旅程查询 (搜索+分数柱状图+统计网格+状态, lazy-load, 125L)
- ✅ LearningHeatmapWidget Dashboard组件: 学习热力图 (子域行+概念格+强度色阶+域选择器, lazy-load, 123L)
- ✅ DashboardWidgetGrid updated: 37→39 lazy-loaded widgets (added ConceptJourneyWidget + LearningHeatmapWidget)
- ✅ All 24 BE routers under 800-line limit (max: 792L analytics_experience.py)
- ✅ 30 new tests (23 BE: 9 split-verify + 4 concept-journey + 5 heatmap + 5 regression + 7 FE)

- ✅ GET /api/analytics/learning-profile: 统一学习档案 (进度总览+连续天数+7日活动+域进度+BKT强弱项+FSRS复习状态, 单API替代5+调用)
- ✅ GET /api/graph/domain-overview-batch: 全域批量概览 (36域一次返回: 概念数/边数/子域/难度/进度/里程碑+聚合统计)
- ✅ LearningProfileWidget Dashboard组件: 统一档案卡 (进度条+活动摘要+域网格+强弱项, lazy-load, 128L)
- ✅ DomainOverviewBatchWidget Dashboard组件: 全域网格 (进度条+难度+展开收起, lazy-load, 90L)
- ✅ DashboardWidgetGrid updated: 35→37 lazy-loaded widgets (added LearningProfileWidget + DomainOverviewBatchWidget)
- ✅ 18 new tests (13 BE: 7 learning-profile + 6 domain-batch + 5 FE)

### V3.6 FSRS Retention Analytics + Goal Intelligence Sprint (2026-04-10, 完成)
- ✅ GET /api/analytics/fsrs-insights: FSRS记忆保持分析 (保持率摘要+遗忘风险分布高/中/低+复习效率+高风险概念TOP10)
- ✅ GET /api/analytics/goal-recommendations: 智能目标建议 (日学习量/周掌握量/学习时间+连续天数目标+专注领域推荐, 基于7日平均+15%挑战)
- ✅ FSRSInsightsWidget Dashboard组件: 间隔复习分析 (风险分布条+效率统计+高风险概念列表, lazy-load, 118L)
- ✅ GoalRecommendWidget Dashboard组件: 智能目标 (上下文统计+推荐列表+专注领域, lazy-load, 107L)
- ✅ DashboardWidgetGrid updated: 33→35 lazy-loaded widgets (added FSRSInsightsWidget + GoalRecommendWidget)
- ✅ 16 new tests (11 BE: 6 fsrs-insights + 5 goal-recommendations + 5 FE)

### V3.5 Learning Engine Health + Session Intelligence Sprint (2026-04-10, 完成)
- ✅ Split learning.py (793L→535L) — extracted learning_review.py (277L: FSRS /due + /review + Achievement /achievements/*)
- ✅ check_and_unlock_achievements() shared between learning.py /assess and learning_review.py /review
- ✅ GET /api/learning/session-replay: 学习回放 (概念级步骤时间线+分数变化+掌握事件+概念/域过滤)
- ✅ GET /api/analytics/comparative-progress: 周度对比 (WoW域级事件/掌握/均分对比+趋势+全局汇总)
- ✅ SessionReplayWidget Dashboard组件: 学习回放 (概念步骤条形图+分数delta+掌握统计, lazy-load, 113L)
- ✅ ComparativeProgressWidget Dashboard组件: 周度对比 (域级趋势+delta badges+全局汇总, lazy-load, 114L)
- ✅ DashboardWidgetGrid updated: 31→33 lazy-loaded widgets (added SessionReplayWidget + ComparativeProgressWidget)
- ✅ All 22 BE routers under 800-line limit (max: 708L learning_extended.py)
- ✅ 24 new tests (19 BE: 7 split-verify + 6 session-replay + 3 comparative-progress + 3 code-health + 5 FE)

### V3.4 Search Enhancement + Progress Snapshot + Code Health Sprint (2026-04-10, 完成)
- ✅ Split graph_advanced.py (815L→489L) — extracted graph_topology.py (352L: V3.0 relationship-strength + V3.1 concept-clusters + V3.3 dependency-tree)
- ✅ Trigram fuzzy matching engine: _trigrams() + _trigram_similarity() helpers in analytics_search.py
- ✅ Content search fuzzy enhancement: trigram fallback scoring for typo-tolerant results (fuzzy_match field)
- ✅ GET /api/analytics/search-suggestions: autocomplete with prefix + substring + trigram fuzzy matching
- ✅ GET /api/analytics/progress-snapshot: compact exportable progress summary (overview/streak/efficiency/top domains/recent mastery)
- ✅ ProgressSnapshotWidget Dashboard组件: 进度快照+JSON导出+Top域进度条 (114L, lazy-load)
- ✅ SearchSuggestionsWidget Dashboard组件: 智能模糊搜索+难度标签+点击导航 (87L, lazy-load)
- ✅ DashboardWidgetGrid updated: 29→31 lazy-loaded widgets (added ProgressSnapshotWidget + SearchSuggestionsWidget)
- ✅ All 20 BE routers under 800-line limit (max: 630L analytics_search.py)
- ✅ 22 new tests (17 BE: 5 trigram + 4 suggestions + 1 fuzzy-search + 7 snapshot + 5 FE)

### V3.3 Dashboard Organization + Dependency Tree + Next Milestones Sprint (2026-04-10, 完成)
- ✅ DashboardWidgetGrid组件抽取: 27个懒加载小组件分为5个可折叠分类 (学习复习/数据分析/领域图谱/社交互动/内容发现)
- ✅ DashboardPage瘦身: 180L→1115L (小组件全部移入DashboardWidgetGrid)
- ✅ GET /api/graph/dependency-tree/{concept_id}: 概念依赖树 (BFS上下游遍历+深度可控+节点信息)
- ✅ GET /api/analytics/next-milestones: 即将达成里程碑 (域%进度+总数里程碑+连续天数+按距离排序)
- ✅ NextMilestonesWidget Dashboard组件: 即将达成卡片 (进度条+badge+剩余距离, lazy-load)
- ✅ 16 new tests (13 BE: 7 dependency-tree + 6 next-milestones + 3 FE)

### V3.2 Learning Velocity & Domain Mastery Intelligence Sprint (2026-04-10, 完成)
- ✅ GET /api/analytics/mastery-forecast/{domain_id}: 域掌握度预测 (学习速度历史+难度加权+子域分布+置信度)
- ✅ GET /api/learning/review-priority: 智能复习优先级 (逾期紧迫度+稳定性风险+下游价值+遗忘历史 4因子加权)
- ✅ MasteryForecastWidget Dashboard组件: 掌握度预测 (进度条+天数/小时预估+子域分布+置信度, lazy-load)
- ✅ ReviewPriorityWidget Dashboard组件: 复习优先级队列 (优先分数+理由标签+可点击导航, lazy-load)
- ✅ DifficultyAccuracyWidget Dashboard组件: 难度校准可视化 (难度分布柱状图+偏差概念列表, lazy-load)
- ✅ 18 new tests (14 BE: 7 mastery-forecast + 7 review-priority + 4 FE)

### V3.1 Prerequisite Intelligence & Learning Flow Sprint (2026-04-10, 完成)
- ✅ GET /api/learning/prerequisite-check/{concept_id}: 前置知识就绪检查 (就绪分数+推荐等级ready/partial/not_ready+未掌握前置列表+建议优先学习)
- ✅ GET /api/graph/concept-clusters/{domain_id}: 概念模块聚类分析 (BFS连通分量+密度+难度范围+入口概念+子域组成)
- ✅ GET /api/analytics/session-summary: 学习小结 (时间窗口内活动聚合+领域分布+最佳/最弱分数+活跃时长估算)
- ✅ PrerequisiteCheckWidget Dashboard组件: 前置知识就绪检查 (就绪进度条+前置状态列表+建议, lazy-load)
- ✅ ConceptClusterWidget Dashboard组件: 概念模块分组展示 (可折叠集群+密度+入口概念, lazy-load)
- ✅ SessionSummaryWidget Dashboard组件: 学习小结卡片 (统计网格+领域标签+最佳分数, lazy-load)
- ✅ 27 new tests (22 BE: 8 prerequisite-check + 8 concept-clusters + 6 session-summary + 5 FE)

### V3.0 Onboarding Intelligence & Graph Topology Sprint (2026-04-10, 完成)
- ✅ Seed metadata memory cache (TTL 300s): analytics_utils.py — 4 call sites no longer re-read 36 JSON files per request
- ✅ GET /api/onboarding/recommended-start: 新用户推荐起始领域 (入门友好度评分+入口概念+时间预估, 按beginner_score排序)
- ✅ GET /api/onboarding/domain-preview/{domain_id}: 领域预览 (入口概念+难度分布+子域概览+总学习时间)
- ✅ OnboardingRecommendWidget Dashboard组件: 推荐起点卡片列表+域预览弹窗 (lazy-load)
- ✅ GET /api/graph/relationship-strength/{domain_id}: 图谱拓扑分析 (枢纽节点/跨域桥接/孤立概念/子域密度/平均度)
- ✅ GraphTopologyWidget Dashboard组件: 拓扑分析卡片 (核心枢纽+跨域桥接+孤立概念警告, lazy-load)
- ✅ onboarding-api.ts: FE API客户端 (fetchRecommendedStart + fetchDomainPreview)
- ✅ 38 new tests (8 analytics_utils + 14 onboarding + 10 relationship-strength + 6 FE)

- ✅ Split LoginPage.tsx: 289→89 lines (extracted BackgroundDecoration + FeaturePills + LoginEmailForm → LoginPageParts 110L)
- ✅ Split HomePage.tsx: 281→109 lines (extracted canvas logic → useHomeCanvas hook 176L)
- ✅ Split KnowledgeGraph.tsx: 247→136 lines (extracted 3 reactive effects → useGraphEffects hook 80L)
- ✅ Split ReviewPage.tsx: 238→112 lines (extracted ReviewError + ReviewEmpty + ReviewComplete → ReviewStates 56L)
- ✅ Split SessionHistoryPage.tsx: 216→182 lines (extracted HistoryItemRow + type defs + constants 50L)
- ✅ Split LearningReportPage.tsx: 214→200 lines (extracted ReportData type + StatCard → ReportParts 42L)
- ✅ Split SettingsLLMConfig.tsx: 214→192 lines (extracted SettingsProxyActions → SettingsProxyGuide 37L)
- ✅ Split DomainRadar.tsx: 213→82 lines (extracted SVG rendering → RadarSVG 45L)
- ✅ Split ConceptSearch.tsx: 210→197 lines (extracted SearchResult type → ConceptSearchTypes 7L)
- ✅ Split NotesPage.tsx: 210→192 lines (extracted NoteCard 33L)
- ✅ Condensed SmartNextSteps.tsx: 207→178 lines (render JSX compaction)
- 🎯 **ALL React components now under 200 lines** — 0 files exceed the 200L limit
- ✅ 10 new FE tests (v213-components.test.ts)
- 📊 FE files >200L: **11 → 0** (100% compliance)

- ✅ Split community.py (788L → 437L) — extracted community_discussions.py (193L, V2.8) + community_content.py (209L, V2.11)
- ✅ Split ConceptDiscussionPanel.tsx (295L → 130L) — extracted DiscussionForm (82L) + DiscussionListItem (118L)
- ✅ Event-driven mastery notifications — _emit_learning_notifications() in learning.py /assess endpoint
- ✅ Event-driven streak milestone notifications — auto-detect 7/14/30/60/90/180/365 day streaks
- ✅ All 19 BE routers under 800-line limit (max: 792L learning.py)
- ✅ FE >200L files reduced from 12 to 11
- ✅ .gitignore updated for apps/api/data/*.db
- ✅ 6 BE tests (event notifications + community split) + 6 FE tests = 12 new tests

---（生效中的架构决策）

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
| pps/api/routers/graph_advanced.py | V2.1+图谱高级API (V2.10拆分: 拓扑分析/概念上下文/对比/跨域桥接/全局统计, V3.4: 489L) |
| pps/api/routers/graph_topology.py | V3.0+图谱拓扑API (V3.4拆分: relationship-strength/concept-clusters/dependency-tree, 352L) |
| pps/api/routers/learning_extended.py | 学习引擎扩展API (V2.10拆分: 数据导入导出/自适应路径/知识缺口) |
| pps/api/llm/router.py | LLM路由器 (SSRF/retry/tier) |
| pps/api/rate_limiter.py | 请求频率限制器 |
| packages/web/src/lib/store/ | Zustand stores (dialogue/learning/domain/graph) |
| packages/web/src/lib/direct-llm.ts | 前端直连LLM (549行, 含validateAssessment) |
| packages/web/src/lib/direct-llm-prompts.ts | LLM提示词模板+域评估补充 (554行, V2.4 从direct-llm.ts拆出) |
| packages/web/src/components/graph/GraphSearchOverlay.tsx | 图谱搜索浮层 (57行, V2.4 从GraphPage.tsx拆出) |
| packages/web/src/components/graph/GraphHubBar.tsx | 底部Hub导航栏: 域切换+导航+推荐 (199行, V2.4 从GraphPage.tsx拆出) |
| packages/web/src/components/graph/GraphRecommendPanel.tsx | 推荐学习路径面板 (79行, V2.4 从GraphPage.tsx拆出) |
| packages/web/src/components/graph/GraphConceptHeader.tsx | 概念详情头部: 难度+状态+关闭 (52行, V2.4 从GraphPage.tsx拆出) |
| packages/web/src/components/graph/graph-visual-utils.ts | 3D图谱视觉工具: 节点颜色/大小/标签纹理/庆祝粒子 (136行, V2.4 从KnowledgeGraph.tsx拆出) |
| packages/web/src/components/dashboard/StreakCalendar.tsx | 30天学习热力图日历 (70行, V2.4 从DashboardPage.tsx拆出) |
| packages/web/src/components/dashboard/VelocitySection.tsx | 学习节奏图表 (76行, V2.4 从DashboardPage.tsx拆出) |
| packages/web/src/components/dashboard/DashboardHelpers.tsx | StatCard+DomainCard+WidgetSkeleton (76行, V2.4 从DashboardPage.tsx拆出) |
| packages/web/src/lib/hooks/useDashboardProgress.ts | Dashboard进度聚合hook (70行, V2.4 从DashboardPage.tsx拆出) |
| packages/web/src/lib/utils/home-canvas-utils.ts | HomePage蜂窝Canvas: DEMO_DOMAINS+常量+hex grid+drawBubble (218行, V2.4 从HomePage.tsx拆出) |
| packages/web/src/components/chat/ChatHistoryView.tsx | 对话历史视图 (87行, V2.4 从ChatPanel.tsx拆出) |
| packages/web/src/components/chat/ChatIdleView.tsx | 概念空闲视图: 掌握度卡片+前置知识+小地图 (172行, V2.4 从ChatPanel.tsx拆出) |
| packages/web/src/components/chat/InlineAssessmentCard.tsx | 评估结果卡片: 动画分数+维度条 (102行, V2.4 从ChatPanel.tsx拆出) |
| packages/web/src/components/chat/LearnAssessmentCard.tsx | LearnPage评估结果卡片: 梯度边框+维度图标 (114行, V2.4 从LearnPage.tsx拆出) |
| packages/web/src/components/learn/LearnHeader.tsx | 学习页头部: 概念名+轮次+评估按钮 (67行, V2.4 从LearnPage.tsx拆出) |
| packages/web/src/components/learn/LearnMessageBubble.tsx | 对话气泡: 用户/AI消息渲染+反馈 (81行, V2.4 从LearnPage.tsx拆出) |
| packages/web/src/components/learn/LearnPostAssessment.tsx | 评估后操作: 返回/重来/推荐+笔记 (84行, V2.4 从LearnPage.tsx拆出) |
| packages/web/src/components/learn/LearnGuideCard.tsx | 学习引导卡+加载指示器 (61行, V2.4 从LearnPage.tsx拆出) |
| packages/web/src/components/learn/LearnInputArea.tsx | 聊天输入区: 语音+选项+文本框 (130行, V2.4 从LearnPage.tsx拆出) |
| packages/web/src/components/settings/SettingsLLMConfig.tsx | LLM配置面板: 服务商/Key/URL/模型/代理 (214行, V2.4 从SettingsContent.tsx拆出) |
| packages/web/src/components/settings/SettingsDataIO.tsx | 数据导入导出+关于+安全信息 (140行, V2.4 从SettingsContent.tsx拆出) |
| packages/web/src/components/community/SuggestionCard.tsx | 社区建议卡片: 投票/审核/删除 (122行, V2.4 从CommunityPage.tsx拆出) |
| packages/web/src/components/community/SuggestionForm.tsx | 新建议提交表单 (61行, V2.4 从CommunityPage.tsx拆出) |
| packages/web/src/components/auth/LoginOAuthButtons.tsx | OAuth登录按钮: Google/GitHub SVG图标+按钮 (70行, V2.4 从LoginPage.tsx拆出) |
| packages/web/src/components/learning-path/PathGroupSection.tsx | 学习路径分组: 可折叠概念组+状态图标+推荐标记 (140行, V2.4 从LearningPathPage.tsx拆出) |
| packages/web/src/components/learning-path/KnowledgeGapsSection.tsx | 知识缺口面板: 阻塞下游概念排序 (52行, V2.4 从LearningPathPage.tsx拆出) |
| packages/web/src/components/panels/DashboardContentParts.tsx | OtherDomainCard+ActivityRow+formatTimeAgo (100行, V2.4 从DashboardContent.tsx拆出) |
| packages/web/src/components/chat/ChatView.tsx | 聊天视图: 消息列表+输入区+评估覆盖+庆祝动效 (172行, V2.4 从ChatPanel.tsx拆出) |
| packages/web/src/components/review/ReviewFlashcard.tsx | FSRS复习闪卡: 进度条+概念卡+评分按钮 (109行, V2.4 从ReviewPage.tsx拆出) |
| packages/web/src/components/common/WelcomeGuide.tsx | 首访引导层 (价值主张+推荐域) |
| packages/web/src/components/common/ReviewBanner.tsx | FSRS复习提示+学习进度 |
| packages/web/src/components/common/DailyRecommendation.tsx | 每日推荐概念 (30概念日轮) |
| packages/web/src/pages/DashboardPage.tsx | 学习分析面板 (含StreakCalendar) |
| packages/web/src/pages/SettingsPage.tsx | 独立设置页面 (/settings) |
| packages/web/src/pages/NotFoundPage.tsx | 404 页面 (渐变标题+导航) |
| packages/web/src/lib/utils/capacitor.ts | Capacitor平台抽象层 (storage/keyboard/lifecycle) |
| packages/web/src/lib/utils/perf-monitor.ts | Core Web Vitals 监控 (FCP/LCP/TTFB) |
| packages/web/src/lib/hooks/ | useAppLifecycle + useBackButton + useKeyboardHeight + useOnlineStatus + useKeyboardShortcuts + useLocalStorage + useLearningTimer + useSpeechRecognition + useStudyGoal + useGraphKeyNav + useDashboardBatch (barrel: hooks/index.ts) |
| packages/web/src/lib/utils/fetch-retry.ts | fetchWithRetry: 指数退避 + 抖动 + Retry-After + abort signal |
| packages/web/src/components/common/OfflineIndicator.tsx | 离线状态提示横幅 (useSyncExternalStore) |
| packages/web/src/components/common/KeyboardShortcutsHelp.tsx | 全局键盘快捷键帮助弹窗 (Shift+?) |
| packages/web/src/components/common/ConceptSearch.tsx | 全局概念搜索 (Ctrl+K, 支持↑↓Enter导航) |
| packages/web/src/components/common/StudyGoalWidget.tsx | 学习目标组件 (SVG进度环 + 目标设置 + 周趋势) |
| packages/web/src/pages/LearningPathPage.tsx | 学习路径页面 (/path/:domainId, 拓扑排序导学) |
| packages/web/src/pages/LeaderboardPage.tsx | 排行榜页面 (/leaderboard, 模拟排名 + Supabase-ready) |
| packages/web/src/components/common/InlineFeedback.tsx | 内联反馈组件 (拇指快捷评价 + 详细反馈表单 + 自动提交到社区) |
| packages/web/src/pages/CommunityPage.tsx | 社区共建页面 (/community, 建议提交/投票/管理员审核工作流) |
| packages/web/src/components/graph/GraphMiniStats.tsx | 图谱HUD: 域进度环+掌握度统计+连续天数 |
| packages/web/src/components/graph/GraphLegend.tsx | 图谱图例: 可折叠状态/难度颜色说明 |
| packages/web/src/components/graph/SubdomainFilter.tsx | 子域筛选下拉: 掌握度统计+高亮切换 |
| packages/web/src/components/graph/ConceptTooltip.tsx | 节点悬浮提示: 名称/状态/难度/时间 |
| packages/web/src/components/dashboard/DomainComparison.tsx | 域掌握度对比: 12域规模柱状图+进度条 |
| packages/web/src/components/graph/ConceptPrerequisites.tsx | 概念前置知识+后续解锁面板 (graph edges导航) |
| packages/web/src/components/graph/ConceptMinimap.tsx | 子域概念导航地图 (状态颜色dot grid) |
| packages/web/src/components/graph/GraphBreadcrumb.tsx | 面包屑导航 (首页>域>子域>概念) |
| packages/web/src/components/common/ShareProgress.tsx | 学习进度分享 (复制/推特/下载) |
| packages/web/src/components/common/SmartNextSteps.tsx | 智能下一步推荐 (graph分析+优先级建议) |
| packages/web/src/components/dashboard/WeeklyReport.tsx | 周报组件 (WoW对比卡+增量badge+总览) |
| packages/web/src/components/dashboard/StudyPatterns.tsx | 学习习惯 (24h/周分布+峰值+一致性) |
| packages/web/src/components/common/StreakRewards.tsx | Streak里程碑奖励 (7级badge+进度条) |
| packages/web/src/components/dashboard/DomainRadar.tsx | 掌握度雷达图 (SVG radar chart, 8轴上限) |
| packages/web/src/components/dashboard/DifficultyHeatmap.tsx | 难度分布热力图 (SVG, 8域×10难度级) |
| packages/web/src/components/dashboard/MilestoneTracker.tsx | 学习里程碑追踪 (25/50/75/100%域进度) |
| packages/web/src/components/dashboard/AdaptivePathWidget.tsx | 智能学习路径 (V2.3: FSRS复习+知识缺口+前沿学习三合一) |
| packages/web/src/components/dashboard/ReviewQueue.tsx | FSRS复习队列 (V2.3: 逾期分级+稳定性+刷新) |
| packages/web/src/components/dashboard/StudyTimeChart.tsx | 学习时间柱状图 (V2.5: 14天+总计/日均/活跃天+生产力指标) |
| packages/web/src/components/dashboard/StreakInsights.tsx | 学习习惯分析 (V2.5: 习惯分数0-100+周分布+一致性) |
| packages/web/src/components/dashboard/MasteryTimeline.tsx | 概念掌握度时间线 (V2.5: SVG折线图+改进量+首次/最近日期) |
| packages/web/src/components/graph/CrossDomainBridge.tsx | 跨域关联概念桥接 (V2.5: 跨知识球探索+域分组+理由) |
| packages/web/src/pages/SessionHistoryPage.tsx | 学习历史时间线 (V2.5: /history, 分页+过滤+搜索) |
| packages/web/src/pages/LearningJourneyPage.tsx | 跨域学习旅程 (V2.6: /journey, 成就时间线+域进度+里程碑) |
| packages/web/src/components/dashboard/DomainRecommendWidget.tsx | 领域推荐 (V2.6: 跨域关联+难度匹配+原因展示) |
| packages/web/src/components/dashboard/StudyPlanWidget.tsx | 学习计划 (V2.6: 日程切换+复习/继续/新学三类+时间预算) |
| packages/web/src/components/dashboard/WeakConceptsWidget.tsx | 薄弱概念警报 (V2.7: 多因子弱点评分+分数趋势+改进建议) |
| packages/web/src/components/dashboard/LearningEfficiencyChart.tsx | 学习效率 (V2.7: 域级效率对比+全局统计+水平条形图) |
| packages/web/src/components/dashboard/GlobalLeaderboard.tsx | 社交排行榜 (V2.8: 4种排序+排名图标+连续火焰+lazy-load) |
| packages/web/src/components/dashboard/PeerComparisonCard.tsx | 同伴对比 (V2.8: 4维度百分位条形图+前X%标签) |
| packages/web/src/components/community/ConceptDiscussionPanel.tsx | 概念讨论面板 (V2.8: 发帖+回复+投票+展开+类型过滤, ChatIdleView集成) |
| apps/api/routers/analytics_insights.py | V2.7分析API (V2.10拆分: 弱点检测/效率/难度校准) |
| apps/api/routers/analytics_experience.py | V2.5分析API (V2.10拆分: 会话历史/掌握度时间线/学习时间/习惯分析) |
| apps/api/routers/analytics_planning.py | V2.6分析API (V2.10拆分: 域推荐/学习计划/学习旅程) |
| apps/api/routers/analytics_social.py | V2.8社交API (V2.10拆分: 排行榜/同伴对比) |
| apps/api/routers/analytics_search.py | V2.9搜索API (V2.10拆分: 概念相似度/学习报告/内容搜索) |
| apps/api/routers/analytics_utils.py | 分析API共享工具 (V2.10: load_seed_metadata DRY helper) |
| packages/web/src/pages/LearningReportPage.tsx | 综合学习报告 (V2.9: /report, 可打印+JSON导出+概览/领域/优劣势/建议) |
| packages/web/src/components/dashboard/ContentSearchWidget.tsx | 知识内容搜索 (V2.9: RAG全文搜索+片段预览+去抖+导航) |
| packages/web/src/components/graph/ConceptSimilarityPanel.tsx | 相似概念面板 (V2.9: 拓扑+标签+跨域相似度+原因标签, ChatIdleView集成) |
| packages/web/src/lib/utils/graph-lod.ts | Graph LOD (子域聚类+节点优先级+大域性能优化) |
| packages/web/src/lib/hooks/useBookmarks.ts | 概念书签hook (localStorage+toggle+上限100) |
| packages/web/src/lib/api/notes-api.ts | 笔记API客户端 (CRUD + bulk sync + stats) |
| packages/web/src/lib/hooks/useNotifications.ts | 通知提醒hook (Notification API + daily reminder) |
| apps/api/utils/metrics.py | API指标收集器 (请求数/错误率/响应时间/per-endpoint) |
| apps/api/routers/notes.py | 概念笔记CRUD + bulk sync + stats API |
| apps/api/routers/analytics.py | 学习分析API (difficulty-map/domain-heatmap/learning-velocity/content-quality-signals) |
| apps/api/routers/community.py | 社区建议API (V2.12拆分: suggestions/voting/moderation/auto-moderate/batch-moderate) |
| apps/api/routers/community_discussions.py | 概念讨论API (V2.12拆分: 发帖/回复/投票/解决/活动摘要) |
| apps/api/routers/community_content.py | 内容质量反馈API (V2.12拆分: 提交/列表/解决/健康总览) |
| apps/api/routers/notifications.py | 通知中心API (V2.11: CRUD+批量已读+摘要+示例生成, create_notification()可编程接口) |
| packages/web/src/pages/NotificationsPage.tsx | 通知中心页面 (V2.11: /notifications, 类型过滤+已读/删除+深链接导航) |
| packages/web/src/components/notifications/NotificationCenter.tsx | 通知Bell组件 (V2.11: 未读徽章+下拉面板+60s轮询+点击外关闭) |
| packages/web/src/components/community/ContentFeedbackButton.tsx | 内容反馈按钮 (V2.11: 展开表单+5类别+评论, ChatIdleView集成) |
| packages/web/src/components/dashboard/ContentHealthWidget.tsx | 内容健康度 (V2.11: 反馈统计+待处理+概念健康分+lazy-load) |
| apps/api/routers/onboarding.py | 新用户入门推荐API (V3.0: recommended-start + domain-preview) |
| packages/web/src/lib/api/onboarding-api.ts | 入门推荐FE API客户端 (V3.0: fetchRecommendedStart + fetchDomainPreview) |
| packages/web/src/components/dashboard/DashboardWidgetGrid.tsx | 仪表板分类小组件网格 (V3.3: 5分类可折叠+27懒加载小组件) |
| packages/web/src/components/dashboard/NextMilestonesWidget.tsx | 即将达成里程碑 (V3.3: 进度条+badge+剩余距离, lazy-load) |
| packages/web/src/components/dashboard/MasteryForecastWidget.tsx | 掌握度预测 (V3.2: 完成天数+小时预估+子域分布, lazy-load) |
| packages/web/src/components/dashboard/ReviewPriorityWidget.tsx | 复习优先级 (V3.2: 4因子加权优先分+理由+导航, lazy-load) |
| packages/web/src/components/dashboard/DifficultyAccuracyWidget.tsx | 难度校准 (V3.2: 难度分布+偏差概念列表, lazy-load) |
| packages/web/src/components/dashboard/PrerequisiteCheckWidget.tsx | 前置知识就绪检查 (V3.1: 就绪分数+前置状态+建议, lazy-load) |
| packages/web/src/components/dashboard/ConceptClusterWidget.tsx | 概念模块分组 (V3.1: 连通分量+密度+入口概念, lazy-load) |
| packages/web/src/components/dashboard/SessionSummaryWidget.tsx | 学习小结 (V3.1: 活动聚合+领域分布+最佳分数, lazy-load) |
| packages/web/src/components/dashboard/OnboardingRecommendWidget.tsx | 推荐起点组件 (V3.0: 推荐卡片+域预览弹窗, lazy-load) |
| packages/web/src/components/dashboard/GraphTopologyWidget.tsx | 图谱拓扑分析 (V3.0: 枢纽/桥接/孤立概念+子域密度, lazy-load) |
| packages/web/src/components/dashboard/ProgressSnapshotWidget.tsx | 进度快照导出 (V3.4: 核心指标+Top域+效率+JSON导出, lazy-load) |
| packages/web/src/components/dashboard/SearchSuggestionsWidget.tsx | 智能模糊搜索 (V3.4: trigram+prefix+导航, lazy-load) |
| apps/api/routers/learning_review.py | FSRS复习+成就系统API (V3.5拆分: /due+/review+/achievements/*, 277L) |
| packages/web/src/components/dashboard/SessionReplayWidget.tsx | 学习回放 (V3.5: 概念步骤时间线+分数变化+掌握统计, lazy-load) |
| packages/web/src/components/dashboard/ComparativeProgressWidget.tsx | 周度对比 (V3.5: WoW域级事件/掌握/均分对比+趋势, lazy-load) |
| packages/web/src/components/dashboard/FSRSInsightsWidget.tsx | FSRS记忆分析 (V3.6: 风险分布+效率统计+高风险概念列表, lazy-load) |
| packages/web/src/components/dashboard/GoalRecommendWidget.tsx | 智能目标建议 (V3.6: 日/周目标+学习时间+专注领域, lazy-load) |
| packages/web/src/components/dashboard/LearningProfileWidget.tsx | 统一学习档案 (V3.7: 进度+连续+7日活动+域进度+强弱项+复习, lazy-load) |
| packages/web/src/components/dashboard/DomainOverviewBatchWidget.tsx | 全域概览网格 (V3.7: 36域批量+进度条+难度+展开, lazy-load) |
| apps/api/routers/learning_intelligence.py | 学习智能API (V3.8拆分: review-priority/session-replay, 253L) |
| apps/api/routers/analytics_forecast.py | 预测分析API (V3.8拆分: mastery-forecast/fsrs-insights/goal-recommendations, 389L) |
| packages/web/src/components/dashboard/ConceptJourneyWidget.tsx | 概念学习旅程 (V3.8: 搜索+分数柱状图+统计网格+状态, lazy-load, 125L) |
| packages/web/src/components/dashboard/LearningHeatmapWidget.tsx | 学习热力图 (V3.8: 子域行×概念格+强度色阶+域选择, lazy-load, 123L) |
| apps/api/routers/analytics_profile.py | 学习档案API (V3.9拆分: learning-profile/concept-journey/learning-heatmap, 284L) |
| packages/web/src/components/dashboard/CrossDomainInsightsWidget.tsx | 跨域知识关联 (V3.9: 域对链接+协同推荐+迁移分数, lazy-load, 93L) |
| packages/web/src/components/dashboard/LearningStyleWidget.tsx | 学习风格 (V3.9: 风格标签+特质chips+时间分布+指标, lazy-load, 112L) |
| apps/api/routers/analytics_advanced.py | 高级分析API (V4.0拆分: cross-domain-insights/learning-style, 187L) |
| packages/web/src/hooks/useDashboardPrefs.ts | Dashboard布局偏好hook (V4.0: 显示/隐藏/排序section, localStorage+useSyncExternalStore) |
| packages/web/src/components/dashboard/DashboardCustomizer.tsx | Dashboard自定义面板 (V4.0: toggle+reorder+reset, 82L) |
| packages/web/src/components/dashboard/WidgetErrorBoundary.tsx | Widget错误隔离 (V4.1: crash→错误卡+重试, class component) |
| packages/web/src/components/dashboard/ApiHealthWidget.tsx | API系统健康 (V4.1: 端点数/延迟/错误率+慢端点TOP3, lazy-load, 107L) |
| packages/web/src/components/dashboard/QuickActionsBar.tsx | 快捷操作栏 (V4.2: 复习/继续/探索, 上下文感知, 100L) |
| packages/web/src/components/dashboard/DifficultyTunerWidget.tsx | 难度校准建议 (V4.3: 偏简单/偏困难箭头+置信度+导航, lazy-load, 89L) |
| packages/web/src/components/dashboard/PortfolioExportWidget.tsx | 学习档案导出 (V4.3: 技能雷达+Markdown/JSON导出+强项/成长, lazy-load, 155L) |
| packages/web/src/components/dashboard/LearningCalendarWidget.tsx | 学习日历 (V4.4: 月度活动色阶+FSRS复习投影+hover工具提示+图例, lazy-load, 133L) |
| packages/web/src/components/dashboard/KnowledgeMapWidget.tsx | 知识图谱探索 (V4.4: 覆盖率进度条+难度分布+深度/广度风格, lazy-load, 120L) |
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

### V2.0 社区与交互增强 Sprint (2026-04-07, 进行中)
- ✅ 语音输入 (Web Speech API): useSpeechRecognition hook + LearnPage麦克风按钮 (zh-CN)
- ✅ 语音多语言切换 (7种语言: zh-CN/en-US/ja-JP/ko-KR/de-DE/fr-FR/es-ES + 连续模式)
- ✅ 学习目标系统: useStudyGoal hook + StudyGoalWidget (SVG进度环 + 7天趋势 + 达标连续)
- ✅ 学习目标通知: useNotifications hook + 设置页通知开关 + 提醒时间选择 + 每日学习提醒
- ✅ 学习路径页面 (/path/:domainId): 拓扑排序导学 + 分组展开 + 推荐标记 + 掌握度进度条
- ✅ 排行榜页面 (/leaderboard): 模拟全站排名 + 个人成绩卡 + Supabase-ready
- ✅ 概念笔记系统: useConceptNotes (localStorage+后端双写) + notes-api.ts + 15 BE测试
- ✅ 笔记后端同步: debounced双向同步 (localStorage↔/api/notes) + bulk sync + pull-on-mount
- ✅ 社区共建图谱: community.py API (suggestions/voting/moderation/feedback) + CommunityPage + 22 BE测试
- ✅ 学习分析API: analytics.py (4个分析端点: difficulty-map/domain-heatmap/velocity/quality-signals) + 8 BE测试
- ✅ 内联反馈: InlineFeedback组件 (学习页👍👎快捷评价 + 详细反馈表单 → 自动提交到社区)
- ✅ 首页浮动导航栏: 分析/排行/笔记/社区/设置快捷入口
- ✅ 图谱页Hub栏: 新增"路径"按钮
- ✅ 社区审核工作流 (管理员审批/拒绝建议 + 审核队列 + 删除 + Bearer token鉴权 + 状态筛选)
- ✅ 语音自动语言检测 (Unicode script分析 + 拉丁语系词频检测 + 对话上下文自适应切换)

## Last Review

**Date**: 2026-04-10 | **Scope**: V4.4 Learning Calendar + Knowledge Map Exploration — learning-calendar API (monthly activity + FSRS projection), knowledge-map-stats API (coverage + depth/breadth + exploration style), 2 Dashboard widgets, 31 tests | **Result**: 1,468 BE + 770 FE + 61 E2E = 2,299 all pass, tsc: 0 errors, 0 open issues, build OK