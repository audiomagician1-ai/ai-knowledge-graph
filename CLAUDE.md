# CLAUDE.md — AI知识图谱 项目大脑

> 每次新对话或 context 压缩后，必须首先读取本文件。
> 本文件是项目级持久记忆，不受上下文压缩影响。

---

## 1. PRIME DIRECTIVE（最高优先级 — 必读）

**当前阶段**: 🟢 **Phase 2 完成 + Phase 3 边缘功能完成 + Code Review 修复完成** | 图谱可视化 + 费曼对话引擎 + EXE打包
**🧭 方向性文档**: `DEVELOPMENT_PLAN.md` — MVP定义/技术架构/里程碑/成本估算
**调研报告**: `RESEARCH_REPORT.md` — 市场分析/竞品/教育理论/技术可行性

**当前最高优先任务 — Phase 2 集成测试** (进行中):
> **目标**: LLM API 实际对接测试 + 端到端对话验证 + 里程碑点亮
> **详见**: `DEVELOPMENT_PLAN.md` Phase 2-3

### 12周里程碑

| Phase | 周次 | 目标 | 状态 |
|:---|:---|:---|:---|
| **Phase 0** | W1-2 | 基础设施 + 种子图谱 | ✅ 完成 |
| **Phase 1** | W3-4 | 图谱展示 + 基础交互 | ✅ 完成 (267节点334边, Cytoscape.js, 里程碑高亮) |
| **Phase 2** | W5-7 | 费曼对话引擎 (核心) | ✅ 核心完成 (LLM调用层+苏格拉底引擎+评估器+SSE流式+前端UI) |
| **Phase 3** | W8-9 | 技能树点亮 + 用户系统 | 🟡 下一步 |
| **Phase 4** | W10-12 | 打磨 + 内测 | ⬜ |

---

## 2. PROJECT IDENTITY（项目基本面）

**产品**: AI知识图谱 — 费曼对话+苏格拉底式教学+知识图谱技能树点亮学习平台
**核心理念**: 通过"教AI"来学会知识 — 结合费曼学习法、苏格拉底式对话和可视化知识图谱
**技术栈**:
- **前端**: React 19 + TypeScript 5.7 + Vite 6 + TailwindCSS 4 + Zustand 5 + Cytoscape.js + Framer Motion
- **后端**: FastAPI (Python 3.11+) — 图谱引擎/对话引擎/学习引擎
- **数据库**: Neo4j 5 (知识图谱) + PostgreSQL 15 via Supabase (用户/学习数据) + Redis 7 (缓存)
- **移动端**: Capacitor 8 (Android/iOS)
- **BaaS**: Supabase (Auth + PostgreSQL + Edge Functions + Storage)
- **LLM**: 分层调度 (DeepSeek/GPT-4o-mini/GPT-4o) via OpenRouter
- **部署**: Cloudflare Pages (前端) + Docker (后端) + Supabase Cloud

**架构**: pnpm monorepo
```
packages/web/      — Vite + React 前端 (@akg/web)
packages/shared/   — 共享类型/常量 (@akg/shared)
packages/mobile/   — Capacitor 移动端 (@akg/mobile)
apps/api/          — FastAPI 后端 (图谱+对话+学习引擎)
supabase/          — Auth + PostgreSQL + Edge Functions
data/seed/         — 种子图谱数据
```

---

## 3. ACTIVE DECISIONS（生效中的架构决策）

| ID | 决策 | 理由 |
|----|------|------|
| ADR-001 | Supabase 做 Auth/用户数据/RLS | 对齐 MuseSea 验证过的架构，快速出活 |
| ADR-002 | FastAPI 独立后端 (非纯 BaaS) | 知识图谱需要 Neo4j + 复杂 LLM 编排，Edge Function 不够 |
| ADR-003 | Neo4j 做知识图谱 | Cypher 查询语言成熟，图遍历性能优 |
| ADR-004 | 前端 Vite+React (非 Next.js) | 对齐 MuseSea 工具链，Capacitor 兼容好 |
| ADR-005 | Capacitor 做移动端 (非 RN) | 对齐 MuseSea，共享同一套 Web 代码 |
| ADR-006 | 深色主题优先 | 知识宇宙主题，对齐 MuseSea 风格 |
| ADR-007 | FSRS 间隔重复 (非 SM-2) | 97.4% 优于 SM-2，Anki 已默认采用 |
| ADR-009 | 全站免登录可用 | MVP 阶段降低门槛，匿名即可体验全部功能 |
| ADR-010 | 用户自带 LLM Key | 前端 localStorage 存储，请求头透传后端，服务端不保存 |

---

## 4. CURRENT STATE（项目当前状态）

### 已完成 ✅
- ✅ 深度调研报告 (`RESEARCH_REPORT.md`)
- ✅ 完整开发计划 (`DEVELOPMENT_PLAN.md`)
- ✅ Monorepo 骨架 (pnpm workspace, 3 packages + 1 app)
- ✅ 前端骨架 (Vite+React19+TS5.7+TailwindCSS4+Zustand5, 4页面+3 stores+3 API client)
- ✅ 共享类型库 (graph/learning/chat/user 4大类型模块 + 常量)
- ✅ 后端骨架 (FastAPI, 4 routers + 3 engines + LLM router + Neo4j/Redis client)
- ✅ Supabase Schema (6表 + RLS + 索引 + auto-profile trigger)
- ✅ Edge Functions 骨架 (health + llm-proxy)
- ✅ Docker Compose (Neo4j 5 + Redis 7)
- ✅ Capacitor 移动端配置
- ✅ CI/CD (GitHub Actions: frontend + backend)
- ✅ GitHub 仓库: https://github.com/audiomagician1-ai/ai-knowledge-graph
- ✅ **种子图谱 v2**: 267概念节点 + 304先修依赖 + 30关联关系 = 334边 (15子域, 含LLM/Agent/Prompt/RAG/Agent系统)
- ✅ **里程碑高亮**: 27个milestone节点 (替代战争迷雾, 金色发光引导)
- ✅ **Cytoscape.js 图谱可视化**: 力导向布局+子域着色+里程碑高亮+邻居highlight+缩放平移
- ✅ **后端图谱查询**: 5 endpoints (data/domains/subdomains/concept/neighbors/stats), JSON fallback
- ✅ **前端图谱页**: Cytoscape.js交互式图谱+子域Tab+详情面板+图例
- ✅ **LLM调用层**: httpx异步+OpenAI兼容API(OpenRouter/DeepSeek/OpenAI)+SSE流式+重试
- ✅ **费曼对话引擎**: System Prompt(苏格拉底式4种策略)+图谱上下文注入+开场白生成
- ✅ **理解度评估器**: 4维度打分(完整性/准确性/深度/举例)+JSON结构化输出+fallback
- ✅ **对话API**: SSE流式/conversations CRUD/评估端点(5 endpoints)
- ✅ **前端对话页**: 消息气泡+流式渲染+评估卡片+4维度进度条
- ✅ **Dialogue Store**: Zustand 5 状态管理(会话/消息/流式/评估)
- ✅ **免登录体验**: 全站开放无需登录，匿名即可使用图谱+对话
- ✅ **用户自带 LLM Key**: 设置页面配置 (OpenRouter/OpenAI/DeepSeek) + localStorage + 请求头透传
- ✅ **代码分割**: Cytoscape.js lazy import, 主包 656KB→219KB (-66%), graph chunk 442KB 按需加载
- ✅ **学习进度持久化**: localStorage 存储匿名用户节点状态 (learning/mastered) + 学习历史 + 连续天数
- ✅ **节点点亮逻辑**: 评估通过→mastered, 图谱节点实时反映学习状态 (enrichedGraphData)
- ✅ **Dashboard 页面**: 真实统计(4 stat cards + 进度条 + 连续天数 + 最近学习记录 + 已掌握列表)
- ✅ **图谱搜索**: 即时搜索 overlay, 快速定位概念节点
- ✅ **Error Boundary + Toast**: 全局错误捕获 + 4类型通知系统 (success/error/info/warning)
- ✅ tsc 0 errors, vite build 2.67s, 主包 219KB + graph 442KB (lazy), 所有Python模块导入通过
- ✅ **Code Review 修复**: 24项问题全部修复 (9 critical + 9 medium + 6 minor)
- ✅ **PyInstaller EXE 打包**: 55MB 单文件, FastAPI+前端SPA+种子数据内嵌, 双击运行自动开浏览器

### EXE 打包规范
```
命名: {缩写}-v{version}-{commit7}-{YYYYMMDD}-{HHmm}.exe
示例: akg-v0.1.0-e9318f2-20260313-1607.exe
构建: python scripts/build_exe.py  (自动化全流程)
验证: /api/health + SPA index.html + /assets/*
```

### 待完成 🟡
1. 🟡 **LLM 端到端测试** — 配置 Key 后实际对话验证
2. 🟡 本地 Docker 安装 (Neo4j + Redis)
3. 🟡 UI/UX 打磨 (移动端适配、动画过渡、loading states)
4. 🟡 API 缓存 + 离线支持

---

## 5. AGENT GUIDELINES（Agent 操作指南）

### 移动端布局规范（MUST — Web+移动端双平台）
- 📱 所有布局以移动端屏幕为第一优先级
- 📱 使用 `min-h-dvh` 而非 `min-h-screen`
- 📱 viewport meta 含 `maximum-scale=1.0, user-scalable=no`
- 📱 触控目标 ≥ 44px
- 📱 safe-area 使用 CSS 变量
- 📱 底部导航高度用 `var(--bottom-nav-height)`
- 📱 所有颜色使用 CSS 变量，禁止混用 Tailwind 默认色值
- 📱 必须为 ≤375px 和 ≤390px 提供 @media 断点适配

### 测试命令
```bash
cd packages/web && npx vitest run        # 前端测试 ✅
cd apps/api && python -m pytest          # 后端测试 ✅
```

### 提交规范
- 格式: `feat(scope): description` 或 `fix(scope): description`
- scope: graph / dialogue / learning / ui / auth / infra
- 提交前必须: `pnpm type-check` + 对应测试通过

### 开发命令
```bash
pnpm dev                    # 前端 dev server (port 3000)
pnpm api:dev                # FastAPI dev server (port 8000)
pnpm docker:up              # 启动 Neo4j + Redis
pnpm docker:down            # 停止
pnpm build                  # 前端构建
pnpm mobile:sync:android    # 构建+同步到 Android
```

### MUST NOT（绝对禁止）
- ❌ 不得在前端代码中暴露 LLM API Key
- ❌ 不得跳过 RLS 策略直接操作数据库
- ❌ 不得使用 >1MB 非代码文件提交
- ❌ 不得在图谱查询中使用无限深度遍历（最大 depth=3）
