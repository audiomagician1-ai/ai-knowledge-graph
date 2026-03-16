# CLAUDE.md — AI知识图谱 项目大脑

> 每次新对话或 context 压缩后，必须首先读取本文件。
> 本文件是项目级持久记忆，不受上下文压缩影响。

---

## 1. PRIME DIRECTIVE（最高优先级 — 必读）

**当前阶段**: 🟢 **Phase 5 启动** | 可选登录 + Supabase 云同步（跨端进度）
**🧭 方向性文档**: `DEVELOPMENT_PLAN.md` — MVP定义/技术架构/里程碑/成本估算
**调研报告**: `RESEARCH_REPORT.md` — 市场分析/竞品/教育理论/技术可行性

**当前最高优先任务 — Phase 5: 可选登录 + 跨端同步**:
> **目标**: 保持免登录可用(ADR-009)，增加可选邮箱登录，登录用户自动同步学习数据到 Supabase，实现跨端进度恢复
> **详见**: 下方 Phase 5 迭代计划

### 12周里程碑

| Phase | 周次 | 目标 | 状态 |
|:---|:---|:---|:---|
| **Phase 0** | W1-2 | 基础设施 + 种子图谱 | ✅ 完成 |
| **Phase 1** | W3-4 | 图谱展示 + 基础交互 | ✅ 完成 (267节点334边, 3D球面力导向图, 里程碑高亮) |
| **Phase 2** | W5-7 | 对话引擎 (核心) | ✅ 完成 (LLM调用层+苏格拉底引擎+评估器+SSE流式+前端UI+RAG知识库) |
| **Phase 3** | W8-9 | 节点点亮 + 进度系统 | ✅ 完成 (前置条件图+推荐集合+mastered绿光晕+recommended青光晕+Dashboard真实数据) |
| **Phase 4** | W10-12 | 打磨 + 内测 | ✅ 完成 (响应式+Markdown+动效+设置页+3轮审查65项+EXE打包) |
| **Phase 5** | W13+ | 可选登录 + 跨端同步 | 🟡 进行中 |

---

## 2. PROJECT IDENTITY（项目基本面）

**产品**: AI知识图谱 — 交互式教学+苏格拉底式对话+知识图谱技能树点亮学习平台
**核心理念**: AI先讲解知识 → 提供选项引导互动 → 探测用户水平 → 自适应深度讲解 → 选项式理解检验 → 评估点亮
**技术栈**:
- **前端**: React 19 + TypeScript 5.7 + Vite 6 + TailwindCSS 4 + Zustand 5 + Three.js/3d-force-graph + Framer Motion + Lucide React
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
- ✅ **3D 球面图谱可视化**: Three.js + 3d-force-graph, 球面力导向+指数雾渐隐+里程碑金色辉光+粒子流连线+自动旋转
- ✅ **后端图谱查询**: 5 endpoints (data/domains/subdomains/concept/neighbors/stats), JSON fallback
- ✅ **前端图谱页**: 3D球面图谱+浮动glass面板+子域筛选+右侧详情面板
- ✅ **LLM调用层**: httpx异步+OpenAI兼容API(OpenRouter/DeepSeek/OpenAI)+SSE流式+重试
- ✅ **对话引擎 V2**: AI引导式探测学习(4阶段: probe→teach→check→wrapup) + parse_ai_response选项解析 + LLM动态开场白
- ✅ **选项式交互**: 每次AI回复附2-4个可点选选项(explore/answer/action/level) + ChoiceButtons组件 + 用户可自由输入
- ✅ **理解度评估器 V2**: 4维度打分+选项交互信号评估(自由输入>选项点选)+JSON结构化输出+fallback
- ✅ **对话API V2**: SSE流式 + choices事件 + opening_choices + is_choice标记
- ✅ **前端对话页 V2**: 消息气泡+流式渲染+选项按钮区+评估卡片+stripChoicesBlock
- ✅ **Dialogue Store V2**: Zustand 5 (currentChoices/selectChoice/isChoice标记)
- ✅ **免登录体验**: 全站开放无需登录，匿名即可使用图谱+对话
- ✅ **用户自带 LLM Key**: 设置页面配置 (OpenRouter/OpenAI/DeepSeek) + localStorage + 请求头透传
- ✅ **代码分割**: Three.js + 3d-force-graph lazy import, three 551KB + graph 767KB 按需加载, 主包 238KB
- ✅ **学习进度持久化**: localStorage 存储匿名用户节点状态 (learning/mastered) + 学习历史 + 连续天数
- ✅ **节点点亮逻辑**: 评估通过→mastered, 图谱节点实时反映学习状态 (enrichedGraphData)
- ✅ **Dashboard 页面**: 真实统计(4 stat cards + 进度条 + 连续天数 + 最近学习记录 + 已掌握列表)
- ✅ **图谱搜索**: 即时搜索 overlay, 快速定位概念节点
- ✅ **Error Boundary + Toast**: 全局错误捕获 + 4类型通知系统 (success/error/info/warning)
- ✅ **响应式布局**: 桌面Sidebar + 移动BottomNav自动切换, GraphPage右侧面板移动端全屏, DashboardPage自适应grid
- ✅ **LearnPage Markdown渲染**: AI消息使用react-markdown渲染(代码高亮/表格/列表/引用)
- ✅ **评估动效增强**: 分数计数动画(useCountUp hook) + 4维度进度条延迟填充 + 庆祝动画
- ✅ **设置页增强**: 关于信息(版本/节点数/学习统计) + 学习数据JSON导出
- ✅ **BottomNav主题统一**: 使用设计系统CSS变量, 与Sidebar风格一致
- ✅ **微交互打磨**: textarea自动增高 + 按钮press反馈 + tabular-nums分数显示
- ✅ **useMediaQuery hook**: 响应式断点检测(768px), 桌面/移动端条件渲染
- ✅ **shared包修复**: 添加typescript devDependency, pnpm type-check全通过
- ✅ **UI改版「Observatory Study」**: 暖调深色(#111110)+衬线标题(Noto Serif SC)+去glass/glow/gradient+铜/苔/梅自然色系+圆角6-8px+实色按钮+图谱去辉光粒子
- ✅ **Prompt工程方案文档**: `docs/PROMPT_ENGINEERING_ITERATION_V2.md` — 完整迭代设计
- ✅ **本地CORS代理模式**: useProxy替代directMode + resolveBaseUrl/probeCORS/probeProxy + 代理脚本下载引导UI
- ✅ **CORS代理增强(照搬NewCRPG)**: probeCORS返回详细错误({ok,status,detail}) + generateSelfContainedBat()自包含BAT(base64嵌入,一键启动无需额外文件) + 错误诊断信息优化
- ✅ **持久化机制修复+导入导出**: SettingsPage directMode→useProxy迁移 + 导出含对话记录/设置 + JSON导入(合并策略) + localStorage数据校验防腐败
- ✅ **系统性代码审查+修复(30项)**: 前后端深度审查发现9critical+25major+23minor
  - FE: direct-llm.ts `||50`→`??50` score bug + directConversations内存泄漏清理 + res.body null检查
  - FE: KnowledgeGraph.tsx cleanup竞态修复(graphRef外部销毁) + _labelCache dispose + O(N²)→O(N) nodeMap
  - FE: GraphPage loading状态finally + LearnPage"再来一轮"补startLearning + assessment deps修复
  - FE: dialogue.ts requestAssessment stale guard + reset清理directConversation
  - FE: SettingsContent testStatus error自动清除(6s) + DashboardContent 2col grid响应式
  - FE: learning.ts streak合并逻辑(lastDate优先而非max) + notStarted防负数
  - BE: dialogue.py _get_lock竞态(setdefault) + messages滑动窗口(40条上限) + assess返回400
  - BE: config.py移除硬编码密码+启动警告 + evaluator.py int()→float()防崩溃+错误日志
  - BE: socratic.py subdomain_name替代subdomain_id + 异常日志
  - BE: graph.py edge过滤or→and + 移除未用domain_id参数 + RAG路径遍历防护
  - BE: redis_client.py close后置None
- ✅ tsc 0 errors, vite build 3.11s, CSS 28KB + graph 7.2KB (lazy)
- ✅ **Direct模式V2 Prompt同步+消息窗口修复**: direct-llm.ts老版Feynman双角色prompt→V2四阶段引导式学习, 添加20条消息滑动窗口(修复AI几轮后不输出), max_tokens 512→800, directCreateConversation改异步+LLM生成opening+choices, 流式响应解析choices block
- ✅ **测试+7项问题修复(bf51060)**:
  - FE: `isDirectMode()`不再要求显式baseUrl — 使用provider默认值(OpenRouter等标准provider直接可用)
  - FE: ChatPanel补充ChoiceButtons渲染(之前仅LearnPage有) + 消息stripChoicesBlock
  - FE: App.tsx路由顺序修正(/learn/:conceptId在通配符*之前, 防止被吞)
  - FE: LearnPage error toast 6秒自动消失
  - FE: directAssess评估角色标签修正(之前反了: user标为老师)
  - FE: loadSavedConversation清理stale currentChoices
- ✅ **第二轮深度审查+修复(15项重点修复)**:
  - FE: dialogue.ts AbortError分支补充`isStreaming:false`重置(防UI卡死) [C-01]
  - FE: ChatPanel.tsx setTimeout清理(组件卸载clearTimeout)+eslint注释 [M-02]
  - FE: GraphPage.tsx loadRecommendations try-finally(防loading卡死) [M-10]
  - FE: direct-llm.ts openingText初始化=''(防未赋值) [m-05]
  - FE: settings.ts downloadBlob延迟revoke 10s(防下载失败)+obfuscate注释 [m-10,m-02]
  - FE: settings.ts probeCORS优先GET /models检测(省token) [m-01]
  - FE: GraphPage+ChatPanel eslint-disable注释(Zustand stable refs) [m-04,M-01]
  - BE: evaluator.py角色标签修正"用户（学习者）"/"AI（学习伙伴/老师）"(影响评估准确性) [M-09]
  - BE: evaluator.py fallback_evaluate mastered统一为overall>=75且all dims>=60 [m-08]
  - BE: neo4j_client.py execute_read/write添加driver None检查 [C-04]
  - BE: dialogue.py添加_busy标志拒绝同会话并发请求(防消息乱序) [C-02]
  - BE: dialogue.py chat/assess调用_cleanup_cache(防锁/缓存无限增长) [C-05]
  - BE: redis_client.py惰性重连机制(60s冷却)+操作异常自动降级 [m-11]
  - BE: main.py CORS通配符+credentials互斥检查 [m-09]

- ✅ **第三轮深度审查+修复(20项, c11ac37)**:
  - BE: dialogue.py `_busy`标志改用try/finally释放(防客户端断开时会话永久死锁/GeneratorExit) [C-01]
  - BE: dialogue.py `_cleanup_cache`清理孤儿锁(防`_session_locks`内存无限增长) [C-02]
  - BE: llm/router.py `chat_stream`增加单次重试(429/5xx)+SSRF防护(`_validate_base_url`) [C-03,M-03]
  - BE: dialogue.py `_ensure_session`双重检查锁(防并发重建丢消息) [M-07]
  - BE: dialogue.py `no_key_response`将DB写入移到锁外via asyncio.to_thread [M-06]
  - BE: dialogue.py 消息截断插入`[对话历史已截断]`系统提示(LLM上下文连贯性) [m-05]
  - BE: dialogue.py 所有`save_message`包装为`asyncio.to_thread`(非阻塞事件循环) [m-06]
  - BE: learning.py `/sync`校验progress(≤500)/history(≤1000)/streak日期格式 [M-02]
  - BE: learning.py `/history` limit上限1000, `/recommend` top_k上限50 [M-08]
  - BE: learning.py history sync用`.get()`防KeyError [M-09]
  - BE: sqlite_client.py `upsert_progress`改原子INSERT...ON CONFLICT(修复TOCTOU竞态) [M-01]
  - BE: neo4j_client.py `execute_read/write`改用显式读/写事务函数 [M-04]
  - BE: evaluator.py `_format_dialogue`截断到8000字符(防超LLM上下文窗口) [m-03]
  - BE: graph.py `_load_seed`加threading.Lock线程安全 [M-05]
  - BE: graph.py RAG路径遍历使用`os.path.normcase`(Windows大小写不敏感) [m-04]
  - BE: redis_client.py `_try_reconnect`加asyncio.Lock(防并发重连泄漏连接) [m-02]
  - BE: main.py 生产环境禁用/docs和/redoc(DEBUG环境变量控制) [m-01]
  - BE: main.py SPA路由检查index.html是否存在 [m-07]

### EXE 打包规范
```
输出目录: release/                              ← 不是 dist/
EXE命名: akg-v{version}-{commit7}-{YYYYMMDD}-{HHmm}.exe
Note命名: akg-v{version}-{commit7}-{YYYYMMDD}-{HHmm}.md  ← 同名 markdown
示例:
  release/akg-v0.1.0-dd10479-20260313-1900.exe
  release/akg-v0.1.0-dd10479-20260313-1900.md

构建命令: python scripts/build_exe.py  (自动化全流程)
验证方式: 双击 exe → 浏览器访问 http://127.0.0.1:8000
          检查: /api/health + SPA index.html + /assets/*

Release Note 包含:
  - 文件名、版本、大小
  - Commit short hash + full hash + 提交信息 + 提交时间
  - 打包时间 (构建机器本地时间)
  - 运行方式说明
  - 包含内容清单

.gitignore 规则:
  - release/*.exe → 忽略 (二进制不入库)
  - release/*.md  → 跟踪 (release note 入库)
```

### Phase 4 已完成 ✅
1. ✅ **LLM 端到端测试** — mihoyo Claude 4.6 Sonnet: 4轮对话+评估 81/100 mastered ✅
2. ✅ **V2对话流程代码审查** — dialogue.ts+direct-llm.ts+LearnPage+ChoiceButtons 全链路完整
3. ✅ **EXE 重新打包** — akg-v0.1.0-e9802e4 (46.5MB), 含代理模式UI+tsc修复
4. ✅ **代理模式重构** — directMode→useProxy, CORS代理引导UI, probeCORS/probeProxy工具
5. ✅ **系统性审查+修复** — 30项问题(9C+25M+23m)，内存泄漏/竞态/安全/性能全面修复
6. ✅ **EXE 重新打包(含审查修复)** — akg-v0.1.0-bf51060 (46.6MB), 含7项测试修复
7. ✅ **第二轮深度审查+修复** — 15项修复(3C+5M+7m): isStreaming卡死/并发竞态/评估标签/Neo4j null/Redis重连
8. ✅ **第三轮深度审查+修复** — 20项修复(3C+10M+7m): SSRF防护/busy死锁/TOCTOU竞态/sync校验/stream重试/并发安全
9. ✅ **EXE 重新打包(含第三轮审查)** — akg-v0.1.0-c11ac37 (46.6MB)
10. 🟡 **最终内测版分发** — 确认EXE可正常运行后分发

### Phase 5 迭代计划: 可选登录 + Supabase 跨端同步 🟡

**设计原则**:
- **ADR-009 不变**: 全站免登录可用，匿名用户体验完全不受影响
- **登录 = 可选增值**: 登录后自动云同步，跨端恢复学习进度
- **双写**: 登录状态下每次学习行为同时写 localStorage + Supabase
- **Supabase 直连**: 前端通过 `@supabase/supabase-js` 直连 Supabase，不经后端 SQLite

**现状盘点**:
- ✅ `auth.ts` store 已有完整的 signIn/signUp/signOut + onAuthStateChange
- ✅ `LoginPage.tsx` 已有登录/注册表单 UI
- ✅ `supabase/migrations/00001_initial_schema.sql` 已有 profiles + user_concept_status + conversations + learning_events 表 + RLS + auto-profile trigger
- ✅ `supabase.ts` 已有 createClient
- ❌ App.tsx 未注册 /login 路由，未调用 auth.initialize()
- ❌ Sidebar/BottomNav 无用户入口
- ❌ 前端从未向 Supabase 写过学习数据
- ❌ 无 Supabase 同步通道 (supabase-sync.ts)

**架构**:
```
用户操作
  ├── localStorage (始终写入，离线可用)
  ├── 后端 SQLite (始终 fire-and-forget, EXE模式)
  └── Supabase (仅登录用户，前端直连)
        ├── user_concept_status (学习进度，按 last_learn_at 合并)
        ├── conversations (对话历史，JSONB messages)
        └── learning_events (学习事件流水)
```

**待实施步骤**:
1. ✅ **App.tsx 路由 + auth 初始化** — /login 路由 + useAuthStore.initialize() + supabase-sync side-effect import
2. ✅ **auth.ts 增强** — isAuthenticated/displayName, signInWithOAuth(Google/GitHub), onAuthLogin回调注册, supabaseConfigured检测
3. ✅ **新建 supabase-sync.ts** — 276行, syncProgressToCloud/downloadProgressFromCloud/syncHistoryToCloud/downloadHistoryFromCloud/syncConversationToCloud/downloadConversationsFromCloud/fullSync(双向合并), onAuthLogin自动触发
4. ✅ **learning.ts 双写** — startLearning/recordAssessment 增加 syncProgressToCloud + syncHistoryToCloud fire-and-forget
5. ✅ **dialogue.ts 双写** — autoSaveConversation 增加 syncConversationToCloud fire-and-forget
6. ✅ **Sidebar 用户区域** — 底部: 未登录→"登录·跨端同步"按钮, 已登录→头像+名字+退出, supabaseConfigured控制显隐
7. ✅ **LoginPage 改版** — Google/GitHub OAuth按钮 + 邮箱登录/注册 + "Skip, continue without account" + Observatory Study风格
8. ✅ **SettingsPage 账号区域** — Cloud图标+已登录显示头像/邮箱/退出, 未登录显示登录按钮
9. ✅ **首次登录数据迁移 + 跨端恢复** — fullSync(): localStorage→Supabase上传 + Supabase→本地下载 + last_learn_at合并
10. ✅ **tsc + build 验证** — tsc 0 errors, vite build 3.39s, 0 warnings
11. 🟡 **Supabase Cloud 配置** — 需创建线上项目 + 配置 Google/GitHub OAuth providers + 设置 .env
12. 🟡 **端到端测试** — 注册→学习→退出→新设备登录→进度恢复

**决策已确认**:
- [x] Supabase 实例: **线上 Supabase Cloud** (跨端必须云端)
- [x] 登录方式: **邮箱 + Google + GitHub** OAuth
- [x] 数据冲突: 以 **last_learn_at 较新为准** (与现有 importData 一致)
- [x] 登录入口: **Sidebar 底部 + 移动端设置页顶部**

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
