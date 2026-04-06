# AI知识图谱 — 开发计划

> **项目名**: AI知识图谱 (AI Knowledge Graph)
> **创建日期**: 2026-03-13
> **版本**: v2.0 (2026-04-07 重写，反映实际实现状态)
> **上一版本**: v1.0 (2026-03-13, 初始规划)

---

## 一、产品定义

### 1.1 一句话描述

> 一个让用户通过交互式苏格拉底对话学习知识的平台 — AI先讲解知识、提供选项引导互动、
> 探测用户水平、自适应深度讲解、选项式理解检验、评估点亮知识图谱。

### 1.2 核心用户画像

| 用户类型 | 描述 | 核心需求 |
|:---|:---|:---|
| **自学者** | 想系统学习多领域知识的成年人 | 结构化路径 + 深度理解 |
| **学生** | 大学生/研究生，需要真正理解而非死记硬背 | 费曼式检验 + 理解检验 |
| **终身学习者** | 已有一定基础，想扩展知识版图 | 跨域知识网络 + 持续激励 |
| **专业人士** | 需要快速掌握新领域知识 | 最短路径推荐 + 深度对话 |

### 1.3 核心功能状态 (截至 2026-04-07)

```
                        已实现 (✅)                   计划中 (📋)
                    ─────────────                  ─────────────
费曼对话引擎         ✅ AI引导式苏格拉底对话         📋 语音输入
                    ✅ 选项式交互(2-4选项)          📋 多模态解释
                    ✅ 多维理解度评估(4维度)         📋 协作学习
                    ✅ RAG知识文档注入
                    ✅ SSE流式输出
                    ✅ LLM响应缓存(Redis)

知识图谱系统         ✅ 30域6,156概念图谱            📋 用户自建节点
                    ✅ 595条跨球链接                 📋 社区共建
                    ✅ 3D宇宙可视化(Three.js)
                    ✅ 100% RAG文档覆盖

技能树点亮           ✅ 节点状态管理                 📋 社交排行
                    ✅ FSRS-5间隔重复               📋 学习数据分析Dashboard
                    ✅ BKT知识追踪
                    ✅ 成就系统

用户系统             ✅ 免登录完整体验(ADR-009)      📋 OAuth社交登录
                    ✅ Supabase Auth基础设施         📋 多端数据同步
                    ✅ 学习数据云同步
```

---

## 二、技术架构 (实际实现)

### 2.1 架构决策记录 (ADR) 索引

| ID | 决策 | 理由 | 与v1计划的偏离 |
|----|------|------|----------------|
| ADR-001 | Supabase 做 Auth/用户数据/RLS | 对齐 MuseSea 验证过的架构 | 对齐 |
| ADR-002 | FastAPI 独立后端 (非纯 BaaS) | 知识图谱需要 Neo4j + 复杂 LLM 编排 | 对齐 |
| ADR-003 | Neo4j 做知识图谱 | Cypher 查询语言成熟，图遍历性能优 | 对齐 |
| ADR-004 | **Vite+React** (非 Next.js) | 对齐 MuseSea 工具链，Capacitor 兼容好 | 🔀 偏离 |
| ADR-005 | Capacitor 做移动端 (非 RN) | 对齐 MuseSea，共享同一套 Web 代码 | 新增 |
| ADR-006 | 深色主题优先 | 知识宇宙主题 | 对齐 |
| ADR-007 | FSRS-5 间隔重复 (非 SM-2) | 97.4% 优于 SM-2，Anki 已默认采用 | 升级 |
| ADR-009 | 全站免登录可用 | MVP阶段降低门槛 | 新增 |
| ADR-010 | 默认免费 LLM + 可选自带 Key | stepfun/step-3.5-flash:free 作为默认后端 | 🔀 偏离 |
| ADR-011 | 登录用户 Supabase-first 持久化 | 登录用户数据以 Supabase Cloud 为权威源 | 新增 |

### 2.2 确定技术栈 (实际)

| 层级 | 计划 (v1.0) | 实际实现 | 变更原因 |
|:---|:---|:---|:---|
| **前端框架** | Next.js 14 | **Vite 6 + React 19** | ADR-004: Capacitor兼容+对齐MuseSea |
| **UI库** | TailwindCSS + shadcn/ui | **TailwindCSS 4 + Lucide React** | 更轻量 |
| **图谱可视化** | Cytoscape.js | **Three.js + 3d-force-graph** | 3D宇宙主题需要 |
| **状态管理** | Zustand 4 | **Zustand 5** | 版本升级 |
| **动画** | 未计划 | **Framer Motion** | UX需要 |
| **后端框架** | FastAPI | **FastAPI** (Python 3.11+) | ✅ 对齐 |
| **图数据库** | Neo4j 5 | **Neo4j 5** | ✅ 对齐 |
| **关系数据库** | PostgreSQL (Supabase) | **PostgreSQL 15 via Supabase** | ✅ 对齐 |
| **向量数据库** | Qdrant | **文件系统 RAG** (6,156 Markdown) | 简化架构，文件RAG够用 |
| **缓存** | Redis 7 | **Redis 7** (Docker) + LLM缓存 | ✅ 对齐+缓存已实现 |
| **LLM** | OpenAI+DeepSeek+Anthropic | **OpenRouter 统一入口** + DeepSeek/OpenAI直连 | 更灵活 |
| **LLM编排** | LangChain / LangGraph | **自研 LLM Router** (分层调度+重试) | 更轻量可控 |
| **间隔重复** | FSRS (py-fsrs) | **自研 FSRS-5 实现** | 完全控制 |
| **知识追踪** | 未计划 | **BKT (贝叶斯知识追踪)** | 超额实现 |
| **部署前端** | Vercel | **Cloudflare Pages** | 零成本+全球CDN |
| **部署后端** | Railway/Fly.io | **Docker** (本地/自托管) | 零成本 |
| **Workers** | 未计划 | **Cloudflare Workers** (LLM代理) | 边缘计算+直连模式 |
| **移动端** | 未计划 | **Capacitor 8** (骨架就绪) | ADR-005 |
| **CI/CD** | GitHub Actions | **GitHub Actions** | ✅ 对齐 |

### 2.3 系统架构图 (实际)

```
┌────────────────────────────────────────────────────────────────────┐
│                          客户端层                                   │
│                                                                    │
│  ┌─────────────────┐  ┌────────────────┐  ┌────────────────────┐  │
│  │  Web App         │  │  Mobile App    │  │  Desktop (EXE)     │  │
│  │  Vite 6 + React  │  │  Capacitor 8   │  │  PyInstaller       │  │
│  │  19              │  │  (骨架就绪)    │  │  (FastAPI+SPA)     │  │
│  └──────┬──────────┘  └──────┬─────────┘  └────────┬───────────┘  │
│         │                    │                      │              │
│  ┌──────▼────────────────────▼──────────────────────▼───────────┐  │
│  │  UI: React + TailwindCSS 4 + Framer Motion + Lucide         │  │
│  │  图谱: Three.js + 3d-force-graph (3D宇宙)                  │  │
│  │  状态: Zustand 5 (dialogue/learning/domain/graph stores)    │  │
│  │  通信: SSE (对话streaming) + REST API                       │  │
│  └──────────────────────────┬──────────────────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────┘
                              │ HTTPS
            ┌─────────────────┼────────────────────┐
            ▼                 ▼                    ▼
┌──────────────────┐ ┌────────────────┐ ┌──────────────────┐
│ Cloudflare Pages │ │ CF Workers     │ │ FastAPI Backend   │
│ (前端静态托管)   │ │ (LLM代理+API) │ │ (图谱+对话+学习) │
│ akg-web.pages.dev│ │ 边缘计算      │ │ Docker / 本地     │
└──────────────────┘ └────────────────┘ └────────┬─────────┘
                                                 │
                    ┌────────────────────────────┬┼──────────────────┐
                    ▼                            ▼│                  ▼
           ┌──────────────┐            ┌─────────▼────┐     ┌──────────────┐
           │ Neo4j 5      │            │ Supabase     │     │ Redis 7      │
           │ 知识图谱     │            │ Auth + PG 15 │     │ LLM缓存     │
           │ 30域 6,156节点│           │ 用户/学习数据│     │ 会话/限流    │
           │ 7,015边      │            │ + Storage    │     │              │
           └──────────────┘            └──────────────┘     └──────────────┘
```


### 2.4 Monorepo 项目结构 (实际)

```
ai-knowledge-graph/
├── packages/
│   ├── web/              # Vite + React 前端 (@akg/web)
│   │   ├── src/
│   │   │   ├── components/  # UI 组件
│   │   │   ├── lib/         # 核心逻辑
│   │   │   │   ├── store/   # Zustand (dialogue/learning/domain/graph)
│   │   │   │   ├── direct-llm.ts  # 前端直连LLM (888行)
│   │   │   │   └── supabase-sync.ts
│   │   │   └── pages/       # 路由页面
│   │   └── index.html
│   ├── shared/           # 共享类型/常量 (@akg/shared)
│   └── mobile/           # Capacitor 移动端 (@akg/mobile)
│
├── apps/
│   └── api/              # FastAPI 后端
│       ├── engines/
│       │   ├── dialogue/     # 苏格拉底对话引擎 + Feynman评估
│       │   ├── graph/        # 图谱引擎 (builder/pathfinder/rag)
│       │   └── learning/     # 学习引擎 (BKT/FSRS/gamify)
│       ├── llm/             # LLM路由器 + 缓存
│       ├── routers/         # API端点 (graph/dialogue/learning/health)
│       ├── db/              # Neo4j + Redis + SQLite 客户端
│       └── tests/           # 897+ 后端测试
│
├── workers/              # Cloudflare Workers (LLM代理+API)
│   └── src/
│
├── supabase/             # Auth + PostgreSQL + Edge Functions
│
├── data/
│   ├── seed/             # 30域种子图谱 + 跨球链接
│   └── rag/              # 6,156篇 RAG知识文档
│
├── scripts/              # 批量处理脚本
├── docs/                 # 项目文档
├── docker-compose.yml    # Neo4j + Redis 开发环境
├── pnpm-workspace.yaml
└── CLAUDE.md             # 项目大脑 (AI Agent上下文)
```

---

## 三、数据规模 (实际 vs 计划)

| 指标 | v1计划 | 实际实现 | 倍率 |
|------|--------|----------|------|
| **知识域** | 1 (编程) | 36 | 36x |
| **概念数** | ~300 | 6,300 | 21x |
| **边数** | 未指定 | 7,167 | — |
| **跨域链接** | 未计划 | 595 | — |
| **RAG文档** | 未计划 | 6,300 (100%) | — |
| **RAG质量** | 未计划 | 均分79.5 (S:1096 A:5060) + 144 stubs | — |
| **测试数** | 未指定 | 1,202 (956BE+238FE+8FSRS) | — |

### 30个知识域

详见 docs/EXPANSION_PLAN.md。覆盖: AI工程、算法、Web开发、数据库、
云计算、网络安全、操作系统、编译器、计算理论、量子计算、机器人学、
自然语言处理、计算机视觉、区块链、博弈论、认知科学、系统思维、
数据科学、移动开发、DevOps、软件工程、人机交互、嵌入式系统、
生物信息学、隐私计算、边缘计算、图形学、网络、数学基础、编程。

---

## 四、已完成里程碑

### Phase 0: 基础设施 + 种子图谱 ✅
- monorepo搭建(pnpm workspace) + CI/CD(GitHub Actions)
- Neo4j + Supabase + Redis 初始化
- 编程领域种子图谱(→ 后扩展到30域)

### Phase 1: 图谱展示 + 交互 ✅
- Three.js 3D宇宙可视化(非计划的Cytoscape 2D)
- 节点交互 + 状态着色 + 战争迷雾
- 图谱API端点

### Phase 2: 费曼对话引擎 ✅
- 苏格拉底式对话引擎V2 (AI引导式探测学习)
- 多维理解度评估(完整性/准确性/深度/举例)
- RAG知识文档注入(文件系统,非向量库)
- SSE流式输出 + LLM分层调度

### Phase 3: 技能树点亮 + 用户系统 ✅
- 免登录完整体验(ADR-009)
- 节点状态机 + 点亮逻辑 + 解锁后续
- 学习数据持久化(本地+云同步)

### Phase 4: 打磨 + 内测 ✅
- UI/UX动画(Framer Motion)
- 移动端适配(safe-area/touch)
- 错误处理 + LLM降级

### V1.0 功能完成 ✅
- FSRS-5间隔重复引擎(自研实现)
- BKT贝叶斯知识追踪(超额)
- 成就系统 + UI
- 统一日志系统(39模块)
- 30域扩展 + 6,156篇RAG文档


---

## 五、当前剩余任务 + 路线图

### 5.1 审计发现 (2026-04-06) — 全部关闭

详见 GitHub Issue #42-#51。所有审计发现已在 2026-04-07 修复并关闭。

| 优先级 | Issue | 状态 | 说明 |
|--------|-------|------|------|
| P0 | #42 图谱引擎空壳化 | ✅ Closed | pathfinder + builder + 7 API + 40 tests |
| P0 | #43 GraphRAG退化为文件硬匹配 | ✅ Closed | 独立 rag.py 模块 + ADR-014 |
| P0 | #44 三端同步复杂度 | ✅ Closed | CROSS_MODULE_INVARIANTS.md + ADR-013 |
| P1 | #45 LLM响应缓存 | ✅ Closed | Redis缓存已实现 |
| P1 | #46 学习分析Dashboard | ✅ Closed | DashboardPage 全局统计/掌握度/活动趋势 |
| P1 | #47 E2E测试缺失 | ✅ Closed | Playwright 10 核心流测试 |
| P1 | #49 OAuth配置 | ✅ Closed | 代码就绪，待 Supabase 控制台配置 |
| P2 | #48 SSR/SEO缺失 | ✅ Closed | OG/meta/robots/sitemap + ADR-012 |
| P2 | #50 DEVELOPMENT_PLAN.md | ✅ Closed | v2.0 全量重写 |
| P2 | #51 审计总结 | ✅ Closed | 整合进开发计划 |

### 5.2 下阶段路线图

| 阶段 | 时间估计 | 核心功能 |
|:---|:---|:---|
| **V1.1** | 2-3周 | E2E测试 + OAuth + 学习分析Dashboard |
| **V1.2** | 3-4周 | 图谱引擎实现(builder/pathfinder) + 三端同步治理 |
| **V1.3** | 2-3周 | SSR/SEO方案 + 移动端Capacitor完善 |
| **V2.0** | 6周 | 社区共建图谱 + 社交排行 + 语音输入 |

---

## 六、成本对比

| 项目 | v1计划 (月) | 实际 (月) | 说明 |
|:---|:---|:---|:---|
| Supabase | $25 | $0 (Free tier) | 用户量尚小 |
| Neo4j | $0-65 | $0 (Docker本地) | 自托管 |
| 向量数据库 | $0 (Qdrant) | $0 (不需要) | 文件RAG替代 |
| 前端部署 | $20 (Vercel) | $0 (Cloudflare Pages) | 免费CDN |
| 后端部署 | $5-20 (Railway) | $0 (Docker本地) | 自托管 |
| Redis | $0 | $0 (Docker本地) | 自托管 |
| **LLM API** | $50-200 | **$0** | stepfun/step-3.5-flash:free |
| **合计** | **~$100-330** | **~$0** | 零成本运行 |

### LLM 成本控制 (已实现)

1. **默认免费模型**: stepfun/step-3.5-flash:free via OpenRouter (ADR-010)
2. **分层调度**: simple/dialogue/assessment 三档
3. **Redis精确缓存**: 相同概念开场白24h缓存 (Issue #45)
4. **用户自带Key**: 可选配置自己的API Key获得更好模型

---

## 七、关键偏离总结

### 战略性偏离 (有意为之)
- Next.js → Vite+React (ADR-004)
- Vercel → Cloudflare Pages (零成本)
- LangChain → 自研LLM Router (更轻量)
- Qdrant → 文件系统RAG (简化架构)
- 全站免登录 (ADR-009)
- 免费LLM默认 (ADR-010)

### 超额实现
- 30域6,156概念 (计划1域300概念，20x)
- 6,156篇RAG知识文档 (计划外)
- 1,143个测试 (计划未指定)
- FSRS-5自研实现 + BKT知识追踪 (计划外)
- 成就系统 + Capacitor移动端骨架 (提前于计划)

### 遗漏性偏离 (已全部补齐 2026-04-07)
- ✅ builder.py/pathfinder.py 图谱引擎核心算法 (#42)
- ✅ 学习分析Dashboard (#46)
- ✅ E2E测试 (#47)
- ✅ OAuth社交登录代码就绪 (#49, 待控制台配置)

---

*本文档于 2026-04-07 全面重写，反映实际实现状态。后续更新请保持与 CLAUDE.md 同步。*

