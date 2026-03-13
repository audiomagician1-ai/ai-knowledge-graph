# AI知识图谱 — 开发计划

> **项目名**: AI知识图谱 (AI Knowledge Graph)
> **创建日期**: 2026-03-13
> **版本**: v1.0

---

## 一、产品定义

### 1.1 一句话描述

> 一个让用户通过"教AI"来学会知识的平台 — 结合费曼学习法、苏格拉底式对话和可视化知识图谱，
> 让学习变成点亮宇宙中每一颗星辰的过程。

### 1.2 核心用户画像

| 用户类型 | 描述 | 核心需求 |
|:---|:---|:---|
| **自学者** | 想系统学习编程/数学/科学的成年人 | 结构化路径 + 深度理解 |
| **学生** | 大学生/研究生，需要真正理解而非死记硬背 | 费曼式检验 + 考试准备 |
| **终身学习者** | 已有一定基础，想扩展知识版图 | 跨域知识网络 + 持续激励 |
| **专业人士** | 需要快速掌握新领域知识 | 最短路径推荐 + 深度对话 |

### 1.3 核心功能矩阵

```
                        MVP (P0)              V1.0 (P1)              V2.0 (P2)
                    ─────────────         ─────────────          ─────────────
费曼对话引擎         ✅ 基础对话            ✅ 理解度评分           ✅ 语音输入
                    ✅ 追问/反问            ✅ 知识漏洞检测         ✅ 多模态解释
                    ✅ 解释评估              ✅ 自适应难度           ✅ 协作学习

知识图谱系统         ✅ 单域图谱(编程)       ✅ 多域图谱            ✅ 全域图谱
                    ✅ 依赖关系              ✅ 跨域关联             ✅ 用户自建节点
                    ✅ 基础可视化            ✅ 3D宇宙视觉          ✅ 社区共建

技能树点亮           ✅ 节点状态管理         ✅ 动态路径推荐         ✅ 社交排行
                    ✅ 学习进度              ✅ FSRS复习调度         ✅ 学习数据分析
                    ✅ 战争迷雾              ✅ 成就系统             ✅ 班级/团队

用户系统             ✅ 注册/登录            ✅ 学习档案             ✅ 多端同步
                    ✅ 基本设置              ✅ 偏好学习             ✅ API/插件
```

---

## 二、技术架构

### 2.1 系统架构图

```
┌───────────────────────────────────────────────────────────────┐
│                         客户端层                               │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │  Web App     │  │  Mobile PWA  │  │  Desktop (Electron) │  │
│  │  Next.js 14  │  │  (后期)      │  │  (后期)             │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘  │
│         │                 │                    │              │
│  ┌──────▼─────────────────▼────────────────────▼───────────┐  │
│  │  UI组件层: React + TailwindCSS + shadcn/ui              │  │
│  │  图谱可视化: Cytoscape.js + WebGL (后期3D)              │  │
│  │  状态管理: Zustand                                      │  │
│  │  实时通信: WebSocket (对话streaming)                    │  │
│  └──────────────────────────┬──────────────────────────────┘  │
└─────────────────────────────┼─────────────────────────────────┘
                              │
                              │ HTTPS + WSS
                              │
┌─────────────────────────────▼─────────────────────────────────┐
│                         服务端层                               │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  API Gateway: FastAPI + WebSocket                      │   │
│  │  认证: Supabase Auth (JWT)                             │   │
│  │  限流: Redis                                           │   │
│  └────────┬──────────────┬──────────────────┬─────────────┘   │
│           │              │                  │                 │
│  ┌────────▼────────┐ ┌───▼──────────┐ ┌────▼──────────────┐  │
│  │  对话引擎       │ │  图谱引擎    │ │  学习引擎         │  │
│  │                 │ │              │ │                    │  │
│  │ • Socratic      │ │ • 知识CRUD   │ │ • FSRS调度        │  │
│  │   Prompt编排    │ │ • 路径计算   │ │ • BKT知识追踪     │  │
│  │ • 多轮上下文    │ │ • 拓扑排序   │ │ • 掌握度评估      │  │
│  │ • 理解度评估    │ │ • 动态推荐   │ │ • 游戏化逻辑      │  │
│  │ • GraphRAG      │ │ • 实体对齐   │ │ • 学习分析        │  │
│  └────────┬────────┘ └───┬──────────┘ └────┬──────────────┘  │
│           │              │                  │                 │
│  ┌────────▼────────┐ ┌───▼──────────┐ ┌────▼──────────────┐  │
│  │  LLM 调度层     │ │  Neo4j       │ │  PostgreSQL       │  │
│  │                 │ │  知识图谱    │ │  用户/学习数据    │  │
│  │  分层路由:      │ │  依赖关系    │ │                    │  │
│  │  mini → std →   │ │  路径索引    │ │  Milvus/Qdrant    │  │
│  │  premium        │ │              │ │  向量检索          │  │
│  │                 │ │              │ │                    │  │
│  │  + Response缓存 │ │              │ │  Redis             │  │
│  │  + 流式输出     │ │              │ │  缓存/会话/限流    │  │
│  └─────────────────┘ └──────────────┘ └────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### 2.2 确定技术栈

| 层级 | 技术 | 版本 | 理由 |
|:---|:---|:---|:---|
| **前端框架** | Next.js | 14+ | SSR/SSG/ISR + App Router + SEO |
| **UI库** | TailwindCSS + shadcn/ui | latest | 快速开发+高质量组件 |
| **图谱可视化** | Cytoscape.js | 3.x | 最成熟的图可视化库，支持大图 |
| **状态管理** | Zustand | 4.x | 轻量、无模板代码 |
| **后端框架** | FastAPI | 0.110+ | Python生态+异步+自动文档 |
| **图数据库** | Neo4j | 5.x | 成熟的图数据库，Cypher查询语言 |
| **关系数据库** | PostgreSQL (Supabase) | 15+ | 用户数据+学习记录+Auth |
| **向量数据库** | Qdrant | latest | 开源+高性能+易部署 |
| **缓存** | Redis | 7.x | 会话/缓存/限流/排行榜 |
| **LLM** | OpenAI + DeepSeek + Anthropic | - | 多模型分层调度 |
| **LLM编排** | LangChain / LangGraph | latest | Agent编排+GraphRAG |
| **间隔重复** | FSRS (py-fsrs) | 5.x | 最先进的SRS算法 |
| **部署** | Docker + Vercel(前端) + Railway/Fly.io(后端) | - | 快速部署 |
| **CI/CD** | GitHub Actions | - | 标准化 |

### 2.3 数据模型设计（核心）

#### Neo4j 知识图谱 Schema

```cypher
// 领域节点
(:Domain {id, name, description, icon, color})

// 概念节点（核心）
(:Concept {
  id,
  name,
  description,
  domain_id,
  difficulty: 1-10,        // 难度系数
  estimated_minutes: int,  // 预估学习时间
  content_type: "theory|practice|project",
  tags: [string],
  created_at,
  updated_at
})

// 关系
(:Concept)-[:PREREQUISITE {strength: 0.0-1.0}]->(:Concept)   // 先修依赖
(:Concept)-[:RELATED_TO {type: "analogy|application|contrast"}]->(:Concept) // 关联
(:Domain)-[:CONTAINS]->(:Concept)
(:Concept)-[:BELONGS_TO]->(:Domain)
```

#### PostgreSQL 用户数据 Schema

```sql
-- 用户学习状态
CREATE TABLE user_concept_status (
  user_id       UUID REFERENCES users(id),
  concept_id    TEXT NOT NULL,
  status        TEXT CHECK (status IN ('locked','available','learning','reviewing','mastered')),
  mastery_level FLOAT DEFAULT 0,  -- 0.0 ~ 1.0
  -- FSRS 字段
  fsrs_stability    FLOAT,
  fsrs_difficulty    FLOAT,
  fsrs_due_date     TIMESTAMPTZ,
  fsrs_last_review  TIMESTAMPTZ,
  -- 知识追踪
  total_sessions    INT DEFAULT 0,
  total_time_sec    INT DEFAULT 0,
  feynman_score     FLOAT,  -- 费曼解释评分
  last_feynman_at   TIMESTAMPTZ,
  PRIMARY KEY (user_id, concept_id)
);

-- 对话历史
CREATE TABLE conversations (
  id          UUID PRIMARY KEY,
  user_id     UUID REFERENCES users(id),
  concept_id  TEXT NOT NULL,
  messages    JSONB,  -- [{role, content, timestamp}]
  summary     TEXT,
  understanding_delta FLOAT,  -- 本次对话带来的理解度变化
  created_at  TIMESTAMPTZ,
  updated_at  TIMESTAMPTZ
);

-- 学习事件流
CREATE TABLE learning_events (
  id          UUID PRIMARY KEY,
  user_id     UUID REFERENCES users(id),
  concept_id  TEXT NOT NULL,
  event_type  TEXT,  -- 'feynman_attempt','review','quiz','unlock'
  payload     JSONB,
  created_at  TIMESTAMPTZ
);
```

---

## 三、MVP 定义 (Phase 0)

### 3.1 MVP 范围：单域 × 核心闭环

**目标**: 用最小功能集验证 "费曼对话 + 知识图谱点亮" 的核心假设

**选定领域**: **编程 (Programming)**
- 理由: 知识结构清晰、依赖关系明确、目标用户精准、内容可自动生成

### 3.2 MVP 功能清单

```
✅ P0 - MVP 必须有
─────────────────────────────────────

[图谱展示]
  ✅ 编程领域知识图谱 (~200-500 个概念节点)
  ✅ 2D 交互式图谱可视化 (缩放/平移/聚焦)
  ✅ 节点状态: locked → available → learning → mastered
  ✅ 战争迷雾效果 (未解锁区域模糊)
  ✅ 点击节点进入学习

[费曼对话]
  ✅ "教AI"模式: 用户向AI解释概念
  ✅ AI苏格拉底式追问 (不直接给答案)
  ✅ 基础理解度评估 (对话结束给出评分)
  ✅ 知识漏洞标记 (具体哪里没说清楚)
  ✅ 流式输出

[技能树点亮]
  ✅ 对话完成 + 理解度达标 → 节点点亮
  ✅ 先修依赖检查 (前置节点未掌握则锁定)
  ✅ 学习进度概览 (已点亮/总数)

[用户系统]
  ✅ 邮箱注册/登录 (Supabase Auth)
  ✅ 学习数据持久化
  ✅ 基本设置页

───────────────────────────────────
❌ P0 不做 (推迟到 V1.0)
─────────────────────────────────────
  ❌ 多领域支持
  ❌ FSRS 间隔复习调度
  ❌ 3D 宇宙视觉
  ❌ 社交/排行榜
  ❌ 成就系统
  ❌ 语音输入
  ❌ 移动端适配
  ❌ 知识图谱编辑器
  ❌ 多语言
```

### 3.3 MVP 用户旅程

```
1. 注册/登录
   ↓
2. 看到编程知识图谱宇宙 — "哇，原来编程知识是这样连接的"
   ↓
3. 从"变量"或"Hello World"等入门节点开始
   ↓
4. 点击节点 → 进入费曼对话
   ↓
5. AI: "你能用最简单的话解释一下什么是变量吗？"
   ↓
6. 用户尝试解释 → AI追问细节 → 用户完善理解
   ↓
7. AI评估理解度 → 达标 → 节点点亮! ✨
   ↓
8. 周围相关节点变为"可学习" → 继续探索
   ↓
9. 看到自己的图谱慢慢亮起来 — 成就感
```

---

## 四、开发里程碑

### Phase 0: 基础设施 + 种子图谱 (第 1-2 周)

| 任务 | 具体内容 | 产出 |
|:---|:---|:---|
| 项目初始化 | monorepo 搭建 (pnpm workspace), CI/CD | 可运行的空壳项目 |
| 数据库搭建 | Neo4j + Supabase 初始化, Schema 创建 | 数据层就绪 |
| 种子图谱构建 | 用 LLM 生成编程领域知识图谱 (~300节点) | Neo4j 中有完整图谱 |
| 图谱数据校验 | 人工审核核心节点和依赖关系 | 高质量种子数据 |

### Phase 1: 图谱展示 + 基础交互 (第 3-4 周)

| 任务 | 具体内容 | 产出 |
|:---|:---|:---|
| 图谱渲染 | Cytoscape.js 集成, 节点/边渲染 | 可缩放浏览的知识图谱 |
| 节点交互 | 点击/hover/聚焦, 状态着色 | 交互式图谱 |
| 战争迷雾 | 未解锁区域模糊/半透明效果 | 探索感 |
| 图谱API | FastAPI 端点: 获取图谱/节点详情/邻居 | 后端API就绪 |

### Phase 2: 费曼对话引擎 (第 5-7 周)

| 任务 | 具体内容 | 产出 |
|:---|:---|:---|
| 对话核心 | LLM 编排, System Prompt 设计, 流式输出 | 基础对话能力 |
| 苏格拉底模式 | 追问/反问策略, 不直接给答案 | 引导式对话 |
| 理解度评估 | 多维度打分 (完整性/准确性/深度/举例) | 自动评分系统 |
| 知识漏洞检测 | 标记用户解释中的模糊/错误/遗漏点 | 精准反馈 |
| GraphRAG | 基于图谱上下文的检索增强 | 相关知识注入 |

### Phase 3: 技能树点亮 + 用户系统 (第 8-9 周)

| 任务 | 具体内容 | 产出 |
|:---|:---|:---|
| 用户认证 | Supabase Auth 集成 | 注册/登录 |
| 状态管理 | 节点状态机 (locked→available→learning→mastered) | 学习进度 |
| 点亮逻辑 | 理解度达标 → 节点点亮 → 解锁后续 | 核心游戏循环 |
| 进度展示 | 学习统计面板, 已点亮/总数 | 数据可视化 |

### Phase 4: 打磨 + 内测 (第 10-12 周)

| 任务 | 具体内容 | 产出 |
|:---|:---|:---|
| UI/UX打磨 | 动画/过渡/加载状态/响应式 | 流畅体验 |
| 性能优化 | 图谱大图渲染优化, API缓存 | 秒开 |
| 错误处理 | 边界情况/LLM降级/离线提示 | 鲁棒性 |
| 内测 | 邀请10-20名用户测试 | 反馈收集 |
| 迭代修复 | 根据反馈调整 | 稳定版本 |

### 📅 总时间线

```
Week 1-2:   ████████ Phase 0 — 基础设施+种子图谱
Week 3-4:   ████████ Phase 1 — 图谱展示+交互
Week 5-7:   ████████████ Phase 2 — 费曼对话引擎 (核心)
Week 8-9:   ████████ Phase 3 — 技能树点亮+用户
Week 10-12: ████████████ Phase 4 — 打磨+内测
            ─────────────────────────────────────
            总计: 约 12 周 (3个月) 到 MVP
```

---

## 五、V1.0 路线图 (MVP 之后)

| 阶段 | 时间 | 核心功能 |
|:---|:---|:---|
| **V1.0** | MVP+4周 | FSRS间隔复习 + 成就系统 + 多域图谱(+数学) |
| **V1.1** | V1.0+3周 | 3D宇宙视觉 + 学习数据分析Dashboard |
| **V1.2** | V1.1+3周 | 移动端PWA + 语音费曼模式 |
| **V2.0** | V1.2+6周 | 社区共建图谱 + 社交排行 + 团队学习 |
| **V2.1** | V2.0+4周 | 用户自建节点 + 私有知识图谱(Obsidian导入) |
| **V3.0** | 待定 | 全域知识图谱 + 企业版 + API市场 |

---

## 六、成本估算

### 6.1 开发成本 (MVP阶段)

| 项目 | 月成本 | 备注 |
|:---|:---|:---|
| Supabase (Pro) | $25/月 | 数据库+Auth+Storage |
| Neo4j AuraDB (Free/Pro) | $0-65/月 | Free tier 20万节点够MVP |
| Qdrant Cloud (Free) | $0/月 | 1GB免费 |
| Vercel (Pro) | $20/月 | 前端部署 |
| Railway/Fly.io | $5-20/月 | 后端部署 |
| Redis Cloud (Free) | $0/月 | 30MB免费 |
| **LLM API** | **$50-200/月** | **最大支出**，取决于用户量 |
| 域名 | $12/年 | - |
| **合计** | **~$100-330/月** | MVP阶段可控 |

### 6.2 LLM 成本控制策略

```
策略1: 分层调度
  简单问答 → DeepSeek ($0.14/1M tokens)     节省 95%
  复杂推理 → GPT-4o-mini ($0.15/1M input)   节省 90%
  核心评估 → GPT-4o ($2.50/1M input)         仅在需要时

策略2: 智能缓存
  相同概念的基础解释 → Redis缓存
  相似问题的回答 → 语义缓存(Embedding相似度)

策略3: 批处理
  知识图谱扩展 → 离线批量生成
  理解度评估模型 → 定期训练微调

预估: 1000 DAU 时月LLM成本约 $150-300
```

---

## 七、关键决策点

| # | 决策 | 选项 | 建议 | 原因 |
|:---|:---|:---|:---|:---|
| 1 | 第一个领域 | 编程 vs 数学 vs 英语 | **编程** | 结构清晰+用户精准+变现明确 |
| 2 | 图谱初始规模 | 100 vs 300 vs 1000节点 | **~300** | 足够展示效果，不至于质量失控 |
| 3 | 开源 vs 闭源 | 完全开源 vs 核心闭源 | **核心开源+数据私有** | 建立社区信任+获取贡献 |
| 4 | 变现模式 | 订阅 vs 免费增值 vs 一次性 | **Freemium** | 免费体验核心→付费解锁高级 |
| 5 | Monorepo 结构 | pnpm workspace | **是** | 前后端+共享类型统一管理 |
| 6 | 部署策略 | 全Serverless vs 容器 | **混合** | 前端Vercel+后端容器 |

---

## 八、Monorepo 项目结构

```
ai-knowledge-graph/
├── apps/
│   ├── web/                    # Next.js 前端
│   │   ├── app/                # App Router
│   │   │   ├── (auth)/         # 登录/注册
│   │   │   ├── graph/          # 图谱页面
│   │   │   ├── learn/[id]/     # 费曼对话页
│   │   │   └── dashboard/      # 学习统计
│   │   ├── components/
│   │   │   ├── graph/          # 图谱可视化组件
│   │   │   ├── chat/           # 对话组件
│   │   │   └── ui/             # shadcn/ui
│   │   └── lib/
│   │       ├── store/          # Zustand stores
│   │       └── api/            # API客户端
│   │
│   └── api/                    # FastAPI 后端
│       ├── routers/
│       │   ├── graph.py        # 图谱API
│       │   ├── chat.py         # 对话API
│       │   ├── learning.py     # 学习进度API
│       │   └── auth.py         # 认证API
│       ├── engines/
│       │   ├── dialogue/       # 对话引擎
│       │   │   ├── socratic.py # 苏格拉底提问
│       │   │   ├── evaluator.py# 理解度评估
│       │   │   └── prompts/    # System Prompts
│       │   ├── graph/          # 图谱引擎
│       │   │   ├── builder.py  # 图谱构建
│       │   │   ├── pathfinder.py # 路径计算
│       │   │   └── rag.py      # GraphRAG
│       │   └── learning/       # 学习引擎
│       │       ├── fsrs.py     # 间隔重复
│       │       ├── tracker.py  # 知识追踪
│       │       └── gamify.py   # 游戏化
│       ├── models/             # 数据模型
│       ├── db/                 # 数据库连接
│       └── llm/                # LLM调度层
│
├── packages/
│   └── shared/                 # 共享类型和工具
│       ├── types/              # TypeScript/Python 共享类型
│       └── constants/          # 共享常量
│
├── data/
│   ├── seed/                   # 种子图谱数据
│   │   └── programming/        # 编程领域
│   └── scripts/                # 图谱生成脚本
│
├── docker-compose.yml          # 本地开发环境
├── pnpm-workspace.yaml
├── pyproject.toml
└── README.md
```

---

## 九、成功指标 (MVP)

| 指标 | 目标 | 衡量方式 |
|:---|:---|:---|
| **核心假设验证** | 用户愿意"教AI"而非"被教" | 费曼对话完成率 > 60% |
| **理解提升** | 对话后理解度显著提升 | 前后测评分差 > 30% |
| **图谱吸引力** | 用户被图谱视觉吸引 | 首页停留时间 > 30秒 |
| **留存** | 7日留存 > 20% | 事件追踪 |
| **节点点亮** | 平均每用户点亮 5+ 节点 | 数据库统计 |
| **NPS** | > 40 | 内测问卷 |

---

*本开发计划将随调研深入和实际开发进展持续更新。*