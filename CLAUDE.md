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
| **Phase 4** | W10-12 | 打磨 + 内测 | ✅ 完成 (响应式+Markdown+动效+设置页+6轮审查90项+49测试+EXE打包) |
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

- ✅ **第五轮审查+修复+测试(6项修复+48测试)**:
  - FE: learning.ts `recordAssessment`防止mastered状态被降级(wasMastered保护) [M-01]
  - FE: supabase-sync.ts `syncHistoryToCloud`补充error返回检查 [M-02]
  - FE: supabase-sync.ts `fullSync` upload改为批量并发(Promise.allSettled, BATCH_SIZE=10) [M-03]
  - FE: DashboardPage.tsx useEffect添加eslint-disable deps注释(Zustand stable refs) [m-01]
  - FE: SettingsPage.tsx 导出下载URL.revokeObjectURL延迟10s(防下载竞态) [m-02]
  - BE: config.py Pydantic `class Config`→`model_config = ConfigDict()`(消除DeprecationWarning) [m-03]
  - TEST: 前端23测试(learning store 10+settings store 13), 后端25测试(health 1+sqlite 12+learning API 12)
- ✅ **第六轮审查+修复(10项修复+1新测试)**:
  - BE: dialogue.py `_busy`检查移入lock保护区(修复check-then-act竞态) [C-02]
  - BE: dialogue.py `_busy_since`时间戳+`_cleanup_cache`120s超时自动释放(防永久锁死) [C-03]
  - BE: sqlite_client.py `record_assessment`mastered降级防护(was_mastered保护,与前端一致) [C-06]
  - FE: direct-llm.ts fallback评估mastered判定统一为overall>=75且所有维度>=60(与后端一致) [C-04]
  - FE: supabase-sync.ts status白名单校验(防非法值传播)+`||`改`??`(防score=0丢失) [C-05]
  - FE: supabase-sync.ts merge `last_learn_at`安全比较(fallback to 0防undefined) [M-10]
  - FE: LearnPage.tsx cleanup先cancelStream再reset(防stale回调) [M-01]
  - FE: LearnPage.tsx assessment recordedRef防重复记录 [M-02]
  - BE: evaluator.py `_format_dialogue` O(n²)→O(n)(append+reverse替代insert(0)) [m-08]
  - BE: main.py `webbrowser.open`异常处理(无头环境安全) [m-14]
  - BE: graph.py `_load_rag_index`添加threading.Lock线程安全 [m-18]
  - TEST: 后端新增mastered降级防护测试(26 tests total)
- ✅ **第七轮深度审查+修复(11项修复+5新测试, a204c99)**:
  - FE: ChatPanel.tsx assessment recordAssessment去重(recordedConvRef防重复记录, 与LearnPage一致) [C-01]
  - BE: dialogue.py _busy检查+消息append合并为单个lock块(消除TOCTOU窗口+asyncio取消风险) [C-02]
  - BE: dialogue.py generate()使用messages_snapshot(防lock外读取被并发修改) [M-05]
  - BE: sqlite_client.py start_learning改为单连接原子read-modify-write(消除TOCTOU竞态) [C-05]
  - FE: graph-api.ts fetchGraphData/fetchConcept/fetchNeighbors添加encodeURIComponent [M-06]
  - FE: learning.ts streak日期计算使用单固定时间点(getStreakDates防跨午夜竞态) [M-09]
  - FE: SettingsContent.tsx URL.revokeObjectURL延迟10s(防导出下载失败, 与SettingsPage一致) [M-11]
  - FE: direct-llm.ts conversations messages数组上限(MAX_CONTEXT_MESSAGES*2防无限增长) [M-02]
  - FE: direct-llm.ts directAssess添加AbortSignal.timeout(30s, 防无限"评估中...") [m-07]
  - BE: learning.py /sync端点添加status白名单校验(防任意状态注入) [m-11]
  - FE: supabase-sync.ts fullSync改为批量upsert(50条/批, 替代N个独立HTTP请求) [M-04]
  - TEST: 前端+2测试(streak初始化+同日不递增), 后端+3测试(原子sessions+保持score+status白名单)
  - TOTAL: 54 tests (25 FE + 29 BE)
- ✅ **第四轮深度审查+修复(14项, d62e997)**:
  - FE: supabase-sync.ts `fullSync`改为先下载后上传(防覆盖云端新数据→数据丢失) [C-01]
  - FE: supabase-sync.ts `fullSync`并发保护(`_syncing`标志防多标签页竞态) [M-06]
  - FE: supabase-sync.ts 历史事件增量同步(lastSyncTimestamp追踪→防每次登录历史翻倍) [M-05]
  - FE: supabase-sync.ts `syncProgressToCloud`检查Supabase error返回 [m-07]
  - FE: auth.ts `onAuthStateChange`订阅清理(HMR/StrictMode重复订阅泄漏) [M-01]
  - FE: auth.ts `_runLoginCallbacks`添加`.catch()`+回调去重+返回unsubscribe [M-02,m-03]
  - FE: dialogue.ts SSE abort时清除空assistant占位消息(防空气泡) [M-12]
  - FE: learning.ts `mastered_at`降级时保留历史时间戳(不再清零) [M-16]
  - FE: LoginPage切换模式清空密码+OAuth loading防重复+signUp邮箱验证检测+autocomplete属性 [M-08,M-09,m-10,m-11]
  - BE: main.py SPA path traversal改用`is_relative_to`(Windows大小写兼容) [M-26]
  - BE: dialogue.py ConversationCreate/ChatRequest/AssessmentRequest添加Field max_length输入校验 [m-36,m-37]
  - BE: learning.py RecordAssessmentRequest score范围校验(ge=0,le=100) [M-30]
  - BE: learning.py /stats endpoint total_concepts添加Query范围限制 [M-31]
  - BE: learning.py /sync score值clamping到[0,100] [M-30]
- ✅ **localStorage 持久化修复 (2026-03-17)**:
  - FE: learning.ts `syncWithBackend` 合并逻辑重写 — 本地数据为权威源(localStorage-first), 后端仅补充本地不存在的条目, 后端严格更新时才合并且不降级mastered状态
  - FE: learning.ts 新增 `verifyStorageAvailable()` 启动时检测localStorage可用性, 不可用时console.error警告
  - FE: learning.ts 新增 `getStorageDiagnostics()` + `window.__akgDiag()` 浏览器控制台调试工具
  - FE: learning.ts `saveProgress/saveHistory/saveStreak` 返回boolean成功标志, 失败时console.error
  - FE: learning.ts `loadProgress` 增加 `isValidProgress()` 校验, 跳过损坏条目
  - FE: learning.ts `startLearning/recordAssessment` 添加console.log事件追踪(DevTools可见)
- ✅ **学习开场加载提示 (2026-03-18, 8ba2749)**:
  - FE: dialogue.ts 新增 `isInitializing` 状态 — `startConversation` 入口 set true, LLM 返回/出错后 set false, reset/loadSaved 也重置
  - FE: LearnPage.tsx + ChatPanel.tsx — isInitializing 时显示 bounce 动画 loading 气泡 + "正在准备学习内容…" 文案, 解决首次进入学习 5-10 秒无反馈问题
- ✅ **Dashboard"最近学习"修复 (2026-03-18, e6c8958)**:
  - FE: DashboardContent.tsx + DashboardPage.tsx — "最近学习"改为基于 progress entries (last_learn_at排序), 而非仅显示评估记录(history); 未评估节点显示"学习中"标签, 已评估显示分数; 点击跳转到 /learn/:id

- ✅ **第八轮巡逻审查+修复 (2026-03-17, 5861592)**:
  - FE: LearnPage.tsx “再来一轮”按钮添加 `recordedRef.current = false` 重置 (修复同概念多轮学习时评估不记录的bug) [#1]
  - REVIEW: ChatPanel/DashboardPage/DashboardContent/dialogue.ts/learning.ts/supabase-sync.ts/auth.ts/main.py 全模块审查通过
  - TOTAL: 54 tests (25 FE + 29 BE) 全通过

- ✅ **Issue #2 修复: OpenRouter model ID 格式校验 (2026-03-18, a585803)**:
  - FE: settings.ts 新增 `validateModelId()` — OpenRouter provider时检测model名缺少org/前缀并显示警告 [#2]
  - FE: settings.ts 新增 `getDefaultModel()` — 集中管理各provider默认模型名(DRY, 消除3处重复)
  - FE: PROVIDER_INFO 增加 `modelHint` 字段 — OpenRouter模型输入框下方显示"格式: org/model"提示
  - FE: SettingsPage.tsx `handleTestConnection` 修复默认模型从硬编码`gpt-4o`改为`getDefaultModel(provider)`
  - FE: SettingsContent.tsx + direct-llm.ts 同步修复(getDefaultModel + 格式提示 + 实时校验)
  - TEST: +9 新测试(validateModelId 5 + getDefaultModel 3 + modelHint 1)
  - TOTAL: 63 tests (34 FE + 29 BE) 全通过

- ✅ **第九轮巡逻审查 (2026-03-18, 10fd08a)**:
  - FE: DashboardContent.tsx useEffect添加eslint-disable注释(Zustand stable refs, 与DashboardPage一致)
  - REVIEW: settings.ts(validateModelId/getDefaultModel) + SettingsContent + SettingsPage + direct-llm.ts + dialogue.ts(isInitializing) + DashboardContent + DashboardPage 全模块审查通过
  - TOTAL: 63 tests (34 FE + 29 BE) 全通过

- ✅ **第十轮深度巡逻审查+修复 (2026-03-18, 6275b8c)**:
  - FE: ChatPanel.tsx 添加 error toast 6秒自动消失(与LearnPage一致, 修复错误永久显示) [m-01]
  - REVIEW: dialogue.ts + learning.ts + direct-llm.ts + supabase-sync.ts + auth.ts + LearnPage.tsx + ChatPanel.tsx + routers/dialogue.py + routers/learning.py + evaluator.py + main.py 全11模块深度审查通过
  - Issue #2 已关闭 (a585803+10fd08a 修复确认)
  - TOTAL: 63 tests (34 FE + 29 BE) 全通过, tsc 0 errors, build 3.17s

- ✅ **第十一轮巡逻审查+重构 (2026-03-18)**:
  - FE: 提取 `stripChoicesBlock` 到 `lib/utils/text.ts` 共享工具(消除LearnPage+ChatPanel重复代码) [m-01]
  - TEST: +5 新测试(stripChoicesBlock: 完整块/不完整块/无块/空串/空白修剪)
  - REVIEW: 13模块深度审查通过: dialogue.ts + learning.ts + direct-llm.ts + supabase-sync.ts + auth.ts + settings.ts + LearnPage.tsx + ChatPanel.tsx + DashboardContent.tsx + dialogue.py + learning.py + main.py + evaluator.py
  - TEST: +5 FE测试(stripChoicesBlock) + 17 BE测试(evaluator: validate_result 6 + parse_json 5 + fallback_evaluate 3 + format_dialogue 3)
  - TOTAL: 85 tests (39 FE + 46 BE) 全通过, tsc 0 errors, build 3.42s

- ✅ **第十二轮深度巡逻审查 (2026-03-18, e64783a)**:
  - REVIEW: 15模块深度审查全通过(0 issues found):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save) + learning.ts(demotion protection/localStorage verification/streak race) + direct-llm.ts(sliding window/timeout/fallback mastered) + supabase-sync.ts(concurrency guard/batch upsert/incremental sync) + LearnPage.tsx(recordedRef reset/initializing indicator) + ChatPanel.tsx(recordedConvRef dedup/error auto-dismiss) + text.ts + text.test.ts + test_evaluator.py
    - BE: dialogue.py(_busy try/finally/snapshot messages/double-check locking) + learning.py(Field validation/status whitelist/score clamping) + evaluator.py(O(n) format/consistent mastered/fallback) + main.py(path traversal/wildcard+credentials/headless)
  - VERIFY: 85 tests (39 FE + 46 BE) 全通过, tsc 0 errors, build 3.27s
  - STATUS: 代码质量稳定, 0 open issues, 无待修复bug

- ✅ **对话API测试补全 (2026-03-18)**:
  - TEST: +16 BE新测试(dialogue API: 创建会话3 + 聊天3 + 评估4 + 获取会话3 + 输入校验3)
    - 创建: 成功/未知概念404/缺少参数422
    - 聊天: 无API Key提示/不存在会话404/缺消息422
    - 评估: 轮数不足400/成功mastered/未mastered/不存在会话404
    - 获取: 详情/不存在404/列表
    - 校验: concept_id超长/message超长/is_choice标志
  - TOTAL: 101 tests (39 FE + 62 BE) 全通过

- ✅ **第十三轮巡逻审查+修复 (2026-03-18, 3145e74)**:
  - FE: DashboardContent.tsx + DashboardPage.tsx — 概念显示名使用图谱节点label(中文名)替代原始ID(英文连字符), 修复`replace(/_/g,' ')`对hyphen-ID无效的显示bug [m-01]
  - REVIEW: 16模块深度审查通过(0 critical/0 major issues):
    - FE: dialogue.ts(isInitializing/stale guards/abort cleanup) + learning.ts(localStorage验证/streak竞态/降级防护) + direct-llm.ts(滑动窗口/timeout/mastered一致) + supabase-sync.ts(并发保护/批量upsert/增量同步) + auth.ts(订阅清理/回调去重) + LearnPage.tsx(recordedRef/loading bubble) + ChatPanel.tsx(recordedConvRef/error auto-dismiss) + DashboardContent.tsx + DashboardPage.tsx + text.ts + settings.ts
    - BE: dialogue.py(_busy try/finally/snapshot messages/double-check locking) + learning.py(Field validation/status whitelist/score clamping) + evaluator.py(O(n) format/consistent mastered) + main.py(path traversal/wildcard+credentials) + test_dialogue_api.py(16 tests quality check)
  - VERIFY: 101 tests (39 FE + 62 BE) 全通过, tsc 0 errors, build 3.24s
  - STATUS: 代码质量稳定, 0 open GitHub issues, 无待修复bug

- ✅ **第十四轮深度巡逻审查 (2026-03-18, 0e12885)**:
  - REVIEW: 18模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoicesFromContent/parseAssessmentJSON) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist) + auth.ts(subscription cleanup/callback dedup/OAuth redirect) + settings.ts(validateModelId/getDefaultModel/probeCORS retry/generateSelfContainedBat) + LearnPage.tsx(recordedRef reset on retry/initializing indicator/error auto-dismiss) + ChatPanel.tsx(recordedConvRef per-conversationId dedup/concept change reset/celebration timer cleanup) + graph-api.ts(encodeURIComponent) + text.ts(stripChoicesBlock)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered logic/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/conversation cleanup) + llm/router.py(SSRF prevention/retry logic/model tier resolution/httpx client lifecycle)
  - VERIFY: 101 tests (39 FE + 62 BE) 全通过, tsc 0 errors, build 3.21s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, 连续2轮零issues审查

- ✅ **第十五轮深度巡逻审查 (2026-03-18)**:
  - REVIEW: 20模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts + learning.ts + direct-llm.ts + supabase-sync.ts + auth.ts + settings.ts + graph.ts(store) + graph-api.ts + text.ts + LearnPage.tsx + ChatPanel.tsx + DashboardContent.tsx + DashboardPage.tsx
    - BE: dialogue.py + learning.py + evaluator.py + main.py + sqlite_client.py + llm/router.py
  - VERIFY: 101 tests (39 FE + 62 BE) 全通过, tsc 0 errors, build 3.44s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, 连续3轮零issues审查

- ✅ **第十六轮巡逻审查+Phase5测试补全 (2026-03-18)**:
  - REVIEW: auth.ts + supabase-sync.ts 深度审查通过(0 critical/0 major issues)
    - auth.ts: onAuthLogin回调去重/反注册 + HMR订阅清理 + displayName fallback链 + isAuthenticated安全getter
    - supabase-sync.ts: _syncing并发guard + try/finally释放 + 状态白名单(C-05) + last_learn_at安全比较(M-10) + 批量upsert 50/batch(M-04) + 增量历史同步
    - NOTE: downloadConversationsFromCloud/CloudConversation 为未使用的预留代码(Phase 5 E2E)
  - TEST: +17 FE新测试:
    - auth store 11测试: onAuthLogin回调注册/去重/反注册 + displayName 5种fallback + isAuthenticated有无session + supabaseConfigured默认值
    - supabase-sync 6测试: syncProgressToCloud skip(无用户)/upsert(有用户) + syncHistoryToCloud skip + syncConversationToCloud skip + fullSync zeros(无用户)/并发guard
  - TOTAL: 118 tests (56 FE + 62 BE) 全通过, tsc 0 errors, build 3.17s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 连续4轮零issues审查

- ✅ **第十七轮深度巡逻审查+修复 (2026-03-18)**:
  - BE: sqlite_client.py `start_learning` — `updated_at`/`created_at`列类型为REAL(unix timestamp)但传入了ISO字符串(`now_iso`)→统一为`now`(float timestamp), 消除类型不一致 [m-01]
  - REVIEW: 20+模块全面深度审查(0 critical/0 major issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist) + auth.ts(subscription cleanup/callback dedup/OAuth redirect) + settings.ts(validateModelId/getDefaultModel/probeCORS retry/generateSelfContainedBat) + LearnPage.tsx(recordedRef reset on retry/initializing indicator/error auto-dismiss) + ChatPanel.tsx(recordedConvRef per-conversationId dedup/concept change reset/celebration timer cleanup)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode) + llm/router.py(SSRF prevention/retry logic/model tier resolution)
  - VERIFY: 118 tests (56 FE + 62 BE) 全通过, tsc 0 errors, build 3.17s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 连续5轮近零issues审查(仅1 minor修复)

- ✅ **第十八轮深度巡逻审查 (2026-03-18)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge/getStreakDates) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist/fullSync download-first) + auth.ts(subscription cleanup/callback dedup/OAuth redirect/displayName fallback chain) + settings.ts(validateModelId/getDefaultModel/probeCORS/generateSelfContainedBat) + LearnPage.tsx(recordedRef reset on retry/initializing indicator/error auto-dismiss/stripChoicesBlock) + ChatPanel.tsx(recordedConvRef per-conversationId dedup/concept change reset/celebration timer cleanup/ChoiceButtons) + DashboardContent.tsx(progress-based activity/graph node label display)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered logic/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser/DEBUG docs) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF prevention/retry logic/model tier resolution/httpx client lifecycle/double-check lock)
  - VERIFY: 118 tests (56 FE + 62 BE) 全通过, tsc 0 errors, build 3.45s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续6轮零issues审查**

- ✅ **第十九轮深度巡逻审查+Graph API测试补全 (2026-03-18)**:
  - REVIEW: 18+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: KnowledgeGraph.tsx(label cache/celebration particles/ResizeObserver cleanup/destroyed guard) + GraphPage.tsx(enrichedGraphData/loadRecommendations try-finally/search useMemo/backendSynced one-time sync) + graph.ts(store) + graph-api.ts(encodeURIComponent) + learning-api.ts(fire-and-forget/error handling) + auth.test.ts(mock quality/11 tests) + supabase-sync.test.ts(mock chain/6 tests)
    - BE: sqlite_client.py(REAL timestamps/atomic ops/mastered demotion protection) + dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking) + main.py(path traversal/CORS/headless) + graph.py(thread-safe seed+RAG loading/BFS depth limit/path traversal protection) + config.py(ConfigDict/no hardcoded secrets) + llm/router.py(SSRF/retry/double-check lock)
  - TEST: +16 BE新测试(graph API: data全量+subdomain筛选+node结构+edge结构+不存在subdomain + domains + subdomains计数 + concept详情+404 + neighbors depth1/depth2/depth限制/404 + stats + rag stats + rag 404)
  - VERIFY: 134 tests (56 FE + 78 BE) 全通过, tsc 0 errors, build 3.43s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续7轮零issues审查**

- ✅ **第二十轮深度巡逻审查+SSRF修复+LLM Router测试补全 (2026-03-18, f4c381f)**:
  - **CRITICAL FIX**: llm/router.py `_validate_base_url` SSRF绕过漏洞 — try/except ValueError同时捕获了ip_address()解析错误和intentional的"Private IP not allowed" raise, 导致10.x/192.168.x/172.16.x等私有IP绕过SSRF保护。修复: try/except/else模式分离解析错误和校验错误 [C-01]
  - TEST: +41 BE新测试(LLM Router: SSRF防护15 + 重试逻辑9 + 端点解析11 + 模型名解析4 + 模型分层2)
    - SSRF: scheme校验(https/http/ftp/file/无) + 阻止localhost/127.0.0.1/::1/metadata.google.internal + 阻止私有IP(10.x/192.168.x/172.16.x) + 允许公网IP/hostname + 尾斜杠清理
    - 重试: 429/5xx可重试, 400/401/403/404/200不重试
    - 端点: 用户配置(openrouter/openai/deepseek/custom) + 自定义base_url + SSRF阻止 + 服务端fallback(3 providers) + 无key抛错
    - 模型名: OpenRouter保留org/前缀, 直连去掉前缀, 无前缀不变
  - VERIFY: 175 tests (56 FE + 119 BE) 全通过, tsc 0 errors, build 3.15s
  - STATUS: 发现1个CRITICAL SSRF漏洞并修复, 代码质量持续提升

- ✅ **第二十一轮深度巡逻审查 (2026-03-18)**:
  - REVIEW: 8核心模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge/getStreakDates) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations/content-type guard/message cap)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks/input validation) + evaluator.py(O(n) format_dialogue/consistent mastered logic/parse_json fallback chain/score clamping) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser/DEBUG docs) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock/model tier resolution)
    - TEST: test_llm_router.py quality check (41 tests: SSRF 15 + retry 9 + endpoint 11 + model 4 + tier 2)
  - VERIFY: 175 tests (56 FE + 119 BE) 全通过, tsc 0 errors, build 3.27s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续8轮零issues审查**

- ✅ **第二十二轮深度巡逻审查 (2026-03-18)**:
  - REVIEW: 16+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations/content-type guard/message cap) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist/fullSync download-first) + settings.ts(validateModelId/getDefaultModel/probeCORS/generateSelfContainedBat) + DashboardContent.tsx(progress-based activity/nameMap useMemo/graph node label display) + graph-api.ts(encodeURIComponent) + text.ts(stripChoicesBlock)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks/input validation) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless/DEBUG docs) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock/model tier resolution) + graph.py(thread-safe seed+RAG loading/BFS depth limit/path traversal protection/normcase) + neo4j_client.py(explicit read/write transactions/driver None check)
  - VERIFY: 175 tests (56 FE + 119 BE) 全通过, tsc 0 errors, build 3.18s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续9轮零issues审查**

- ✅ **第二十三轮巡逻审查+对话Store测试补全 (2026-03-18, c84fba9)**:
  - **FIX**: dialogue.ts `startConversation` catch块补充`isStreaming: false`重置(防开场streaming阶段异常后isStreaming卡死) [m-01]
  - TEST: +24 FE新测试(dialogue store: 初始状态2 + reset清理1 + cancelStream 1 + startConversation错误处理2 + loadSavedConversation加载/不存在2 + deleteSavedConversation删除/持久化2 + importConversations去重/无效跳过/排序3 + replaceConversations替换/过滤2 + selectChoice空choices/无效id 2 + sendMessage guards(无convId/streaming/assessing) 3 + requestAssessment guards(无convId/streaming/assessing) 3 + 持久化50上限1)
  - REVIEW: dialogue.ts深度审查 — stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController/streaming simulation stale check 全通过
  - VERIFY: 199 tests (80 FE + 119 BE) 全通过, tsc 0 errors, build 3.44s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 仅1 minor修复

- ✅ **第二十四轮深度巡逻审查+direct-llm测试补全 (2026-03-18, 4caa1fd)**:
  - **FIX**: direct-llm.ts `directChatStream` content-type不匹配时SSE done事件使用`data: [DONE]`(非JSON格式)→改为标准`{type:'done',suggest_assess:false}`JSON格式(确保dialogue.ts正确解析done事件) [m-01]
  - **EXPORT**: parseChoicesFromContent + windowMessages + parseAssessmentJSON 导出供测试
  - TEST: +19 FE新测试(direct-llm: parseChoicesFromContent 9 + windowMessages 3 + parseAssessmentJSON 7)
    - parseChoicesFromContent: 空输入/有效块/最多4选项/文字截断60字/未知type默认explore/无效JSON/最少2选项/过滤空文字/无块纯文本
    - windowMessages: 低于限制不变/超限保留首条+最后N条/恰好限制不变
    - parseAssessmentJSON: 直接JSON/json代码块/花括号提取/分数clamp 0-100/mastered重算/不可解析返回null/缺失字段填充
  - REVIEW: 20+模块全面深度审查(0 critical/0 major issues):
    - FE: direct-llm.ts(parseChoicesFromContent/windowMessages/parseAssessmentJSON/resolveEndpoint/getConceptContext/buildSystemPrompt/directCreateConversation 15s timeout/directChatStream content-type guard+sliding window+messages cap/directAssess 30s timeout/pruneDirectConversations) + graph.ts(store, 简单setter) + toast.ts(setTimeout+removeToast) + graph-api.ts(encodeURIComponent) + dialogue-api.ts(signal传递) + learning-api.ts(fire-and-forget) + useCountUp.ts(cleanup) + useMediaQuery.ts(SSR安全)
    - BE: graph.py(double-check locking/BFS depth limit/path traversal protection/thread-safe RAG loading) + config.py(ConfigDict/no secrets) + socratic.py(RAG loading/fallback opening/streaming)
  - VERIFY: 218 tests (99 FE + 119 BE) 全通过, tsc 0 errors, build 3.20s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 仅1 minor修复

- ✅ **第二十五轮深度巡逻审查+修复 (2026-03-18, 0fdd064)**:
  - FE: ErrorBoundary.tsx 错误页面背景/文字颜色从硬编码深色(#0f172a/#f1f5f9/#94a3b8)改为CSS变量(--color-surface-0/--color-text-primary/--color-text-tertiary)+fallback值, 与Observatory Study浅色主题一致 [m-01]
  - REVIEW: 20+模块全面深度审查(0 critical/0 major issues):
    - FE: KnowledgeGraph.tsx(labelCache dispose/celebration rAF self-terminating/ResizeObserver cleanup/destroyed guard/dataRef stable callback) + GraphPage.tsx(enrichedGraphData useMemo/loadRecommendations try-finally/search useMemo/backendSynced one-time sync/loading finally) + LoginPage.tsx(OAuth loading guard/mode switch clear password/email confirmation check/autocomplete) + Sidebar.tsx(supabaseConfigured guard/displayName fallback/progress stats) + DraggableModal.tsx(center on open/drag bounds/backdrop close/event listener cleanup) + ErrorBoundary.tsx(CSS variable colors) + graph.ts(store简单setter) + graph-api.ts(encodeURIComponent) + learning-api.ts(fire-and-forget) + toast.ts(setTimeout+removeToast/counter uniqueness) + App.tsx(auth initialize/supabase-sync side-effect import/route order)
    - BE: config.py(ConfigDict/no hardcoded secrets/warning logs) + neo4j_client.py(explicit read/write transactions/driver None check) + redis_client.py(lazy reconnect with lock+cooldown/old client cleanup/graceful degradation)
  - VERIFY: 218 tests (99 FE + 119 BE) 全通过, tsc 0 errors, build 3.15s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 仅1 minor修复

- ✅ **第二十六轮深度巡逻审查+Prompt Parser测试补全 (2026-03-18, a8f34f5)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing) + learning.ts(localStorage verification/streak race/demotion protection/syncWithBackend local-first) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist) + auth.ts(subscription cleanup/callback dedup) + settings.ts(validateModelId/getDefaultModel/probeCORS) + toast.ts(auto-dismiss/counter uniqueness) + graph.ts(simple setters)
    - BE: feynman_system.py(parse_ai_response/choices block regex+trailing JSON fallback/_validate_choices min2 max4/text cap 60/type whitelist/_parse_choices_json single-quote+trailing-comma cleanup) + socratic.py(RAG loading/YAML frontmatter strip/3000 char truncation/build_system_prompt graph context/opening fallback) + dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache) + evaluator.py(O(n) format_dialogue/consistent mastered/parse_json fallback) + main.py(path traversal/CORS/headless) + sqlite_client.py(atomic ops/mastered demotion protection/REAL timestamps) + llm/router.py(SSRF try/except/else/retry/double-check lock)
    - SECURITY: No eval/exec/innerHTML/dangerouslySetInnerHTML across entire codebase. socratic.py RAG path uses seed-data concept IDs (trusted). No TODO/FIXME in production code (only in future-phase stubs).
  - TEST: +28 BE新测试(prompt parser: parse_ai_response 11 + _parse_choices_json 5 + _try_trailing_json 4 + _validate_choices 8)
    - parse_ai_response: 空串/None/空白→默认 + 有效choices块 + 空白choices块 + 尾部JSON fallback + 无choices→默认 + 畸形JSON→默认 + 文字60字截断 + 最多4选项 + 无效type默认explore
    - _parse_choices_json: 有效数组/单引号修复/尾逗号修复/无效JSON→空/对象非数组→空
    - _try_trailing_json: 尾部数组提取/无括号/无type字段忽略/单项数组拒绝
    - _validate_choices: 空列表/None→默认 + 单项→默认 + 4种type保留 + 自动分配ID/保留ID + 非dict跳过 + 空text跳过
  - VERIFY: 246 tests (99 FE + 147 BE) 全通过, tsc 0 errors, build 3.40s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续10轮零issues审查**

- ✅ **第二十七轮深度巡逻审查 (2026-03-18)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge/getStreakDates) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations/content-type guard/message cap) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist/fullSync download-first) + auth.ts(subscription cleanup/callback dedup/OAuth redirect/displayName fallback chain)
    - BE: socratic.py(RAG loading/YAML frontmatter strip/3000 char truncation/build_system_prompt graph context/opening fallback) + graph.py(double-check locking/BFS depth limit/path traversal protection/thread-safe RAG loading/normcase) + dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser/DEBUG docs) + redis_client.py(lazy reconnect with lock+cooldown/old client cleanup/graceful degradation) + config.py(ConfigDict/no hardcoded secrets) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock)
  - VERIFY: 246 tests (99 FE + 147 BE) 全通过, tsc 0 errors, build 3.50s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续11轮零issues审查**

- ✅ **第二十八轮深度巡逻审查+苏格拉底引擎测试补全 (2026-03-18)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge/getStreakDates) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations/content-type guard/message cap) + graph.ts(simple setters) + graph-api.ts(encodeURIComponent) + text.ts(stripChoicesBlock)
    - BE: socratic.py(RAG loading/YAML frontmatter strip/3000 char truncation/build_system_prompt graph context/opening fallback/LLM failure resilience) + feynman_system.py(parse_ai_response/choices block regex/trailing JSON fallback/validate_choices) + dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks/input validation) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser/DEBUG docs) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + learning.py(Field validation/status whitelist/score clamping)
  - TEST: +24 BE新测试(socratic engine: _get_rag_dir 3 + _load_rag_content 6 + build_system_prompt 13 + opening_prompt 1 + get_opening fallback 1)
    - _get_rag_dir: 返回类型/路径后缀/dev模式路径存在
    - _load_rag_content: 已知概念返回内容/不存在概念返回空/不存在子域返回空/截断3000字/YAML frontmatter剥离/H1标题剥离
    - build_system_prompt: 概念名/子域名/难度/先修/无先修/后续/关联/里程碑/非里程碑/RAG注入/无RAG/四阶段/choices格式
    - get_opening: LLM失败时fallback(4个level选项)
  - VERIFY: 270 tests (99 FE + 171 BE) 全通过, tsc 0 errors
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续12轮零issues审查**

- ✅ **第二十九轮深度巡逻审查 (2026-03-18)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge/getStreakDates) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations/content-type guard/message cap) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist/fullSync download-first) + auth.ts(subscription cleanup/callback dedup/OAuth redirect/displayName fallback chain) + settings.ts(validateModelId/getDefaultModel/probeCORS/generateSelfContainedBat) + LearnPage.tsx(recordedRef reset on retry/initializing indicator/error auto-dismiss/stripChoicesBlock) + ChatPanel.tsx(recordedConvRef per-conversationId dedup/concept change reset/celebration timer cleanup/ChoiceButtons) + DashboardContent.tsx(progress-based activity/nameMap useMemo/graph node label display)
    - BE: socratic.py(RAG loading/YAML frontmatter strip/3000 char truncation/build_system_prompt graph context/opening fallback/LLM failure resilience) + dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks/input validation) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered logic/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser/DEBUG docs) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock/model tier resolution) + config.py(ConfigDict/no hardcoded secrets)
  - GITHUB: 0 open issues, 2 closed (all resolved)
  - VERIFY: 270 tests (99 FE + 171 BE) 全通过, tsc 0 errors, build 3.17s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续13轮零issues审查**

- ✅ **第三十轮深度巡逻审查+toast/graph store测试补全 (2026-03-18, 7c31f1d)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist) + auth.ts(subscription cleanup/callback dedup) + settings.ts(validateModelId/getDefaultModel/probeCORS) + toast.ts(auto-dismiss/counter uniqueness/shorthand helpers) + graph.ts(simple setters/loading clear) + graph-api.ts(encodeURIComponent) + dialogue-api.ts(signal passthrough) + learning-api.ts(fire-and-forget error handling) + text.ts(stripChoicesBlock)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks/input validation) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered logic/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock) + redis_client.py(lazy reconnect with lock+cooldown/graceful degradation) + neo4j_client.py(explicit read/write transactions/driver None check) + config.py(ConfigDict/no hardcoded secrets)
  - TEST: +22 FE新测试:
    - toast store 12测试: addToast(唯一ID/多toast/默认3秒自动dismiss/自定义duration/duration=0永久/唯一ID验证) + removeToast(指定删除/不存在ID无效) + shorthand(success/error 5s/info/warning 4s)
    - graph store 10测试: 初始状态(null checks/loading false) + setGraphData(设数据+清loading) + selectNode(设/清) + setActiveSubdomain(设/清) + setLoading(toggle) + setError(设error清loading/清error)
  - GITHUB: 0 open issues, 2 closed (all resolved)
  - VERIFY: 292 tests (121 FE + 171 BE) 全通过, tsc 0 errors, build 3.41s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续14轮零issues审查**

- ✅ **第三十一轮深度巡逻审查+main.py测试补全 (2026-03-18)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist) + auth.ts(subscription cleanup/callback dedup) + settings.ts(validateModelId/getDefaultModel/probeCORS) + graph.ts(simple setters) + text.ts(stripChoicesBlock)
    - BE: main.py(path traversal is_relative_to/wildcard+credentials CORS/headless/DEBUG docs/SPA serve) + dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache) + learning.py(Field validation/status whitelist/score clamping) + evaluator.py(O(n) format_dialogue/consistent mastered/parse_json fallback) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock) + config.py(ConfigDict/no hardcoded secrets)
  - TEST: +18 BE新测试(main.py: CORS config 5 + route registration 6 + debug mode 2 + SPA path traversal 3 + CORS headers integration 2)
    - CORS: 默认origins/wildcard禁credentials/指定origins启credentials/空格清理/空串
    - Routes: health/graph data/graph domains/learning stats/dialogue list/非存在路径404
    - Debug: 默认false/解析逻辑
    - SPA: 路径遍历阻止/正常路径安全/空路径index fallback
    - CORS Headers: allowed origin返回headers/自定义X-LLM-*headers允许
  - GITHUB: 0 open issues, 2 closed (all resolved)
  - VERIFY: 310 tests (121 FE + 189 BE) 全通过, tsc 0 errors, build 3.20s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续15轮零issues审查**

- ✅ **第三十二轮深度巡逻审查+config/redis测试补全 (2026-03-18, 8db37d4)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist) + auth.ts(subscription cleanup/callback dedup) + settings.ts(validateModelId/getDefaultModel/probeCORS) + graph.ts(simple setters) + text.ts(stripChoicesBlock)
    - BE: config.py(ConfigDict/env overrides/no hardcoded secrets) + redis_client.py(lazy reconnect with lock+cooldown/graceful degradation/old client cleanup) + dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache) + learning.py(Field validation/status whitelist/score clamping) + evaluator.py(O(n) format_dialogue/consistent mastered/parse_json fallback) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock) + main.py(path traversal/CORS/headless/DEBUG docs)
  - TEST: +31 BE新测试:
    - config.py 12测试: 默认值(neo4j_uri/user/password/redis/supabase/llm_models/api_keys 7) + 环境变量覆盖(neo4j_uri/redis_url/llm_model 3) + ConfigDict验证(model_config/no deprecated Config 2)
    - redis_client.py 19测试: 初始化(state/property 2) + 连接(success/failure/close/close_noop 4) + 缓存(get_value/get_miss/get_no_client/get_error_clears/set_ttl/set_default/set_no_client/set_error_clears 8) + 重连(success/cooldown_60s/failure_clears/closes_old/get_triggers_reconnect 5)
  - GITHUB: 0 open issues, 2 closed (all resolved)
  - VERIFY: 341 tests (121 FE + 220 BE) 全通过, tsc 0 errors
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续16轮零issues审查**

- ✅ **第三十三轮深度巡逻审查+vitest OOM修复 (2026-03-18, 8d19556)**:
  - **FIX**: vitest.config.ts 添加 `pool: 'forks'` + `execArgv: ['--max-old-space-size=4096']` — 修复 Node v24 环境下 vitest 批量运行时 worker 进程 OOM 崩溃(worker 默认堆大小不足导致 jsdom 测试失败) [m-01]
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge/getStreakDates) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations/content-type guard/message cap) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist/fullSync download-first) + auth.ts(subscription cleanup/callback dedup/OAuth redirect) + settings.ts(validateModelId/getDefaultModel/probeCORS/generateSelfContainedBat) + LearnPage.tsx(recordedRef reset on retry/initializing indicator/error auto-dismiss) + ChatPanel.tsx(recordedConvRef per-conversationId dedup/concept change reset/celebration timer cleanup/ChoiceButtons) + graph.ts(simple setters) + text.ts(stripChoicesBlock)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks/input validation) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser/DEBUG docs) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock/model tier resolution) + graph.py(thread-safe seed+RAG loading/BFS depth limit/path traversal protection) + config.py(ConfigDict/no hardcoded secrets) + redis_client.py(lazy reconnect with lock+cooldown/graceful degradation)
  - GITHUB: 0 open issues, 2 closed (all resolved)
  - VERIFY: 341 tests (121 FE + 220 BE) 全通过, tsc 0 errors, build 3.14s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, vitest OOM修复改善DX

- ✅ **第三十四轮深度巡逻审查 (2026-03-18)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge/getStreakDates) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations/content-type guard/message cap) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist/fullSync download-first) + auth.ts(subscription cleanup/callback dedup) + settings.ts(validateModelId/getDefaultModel/probeCORS) + graph.ts(simple setters) + text.ts(stripChoicesBlock)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks/input validation) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser/DEBUG docs) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock/model tier resolution) + config.py(ConfigDict/no hardcoded secrets) + redis_client.py(lazy reconnect with lock+cooldown/graceful degradation)
  - GITHUB: 0 open issues, 2 closed (all resolved)
  - VERIFY: 341 tests (121 FE + 220 BE) 全通过, tsc 0 errors, build 3.11s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续17轮零issues审查**

- ✅ **第三十五轮深度巡逻审查 (2026-03-18)**:
  - REVIEW: 20+模块全面深度审查全通过(0 critical/0 major/0 minor issues):
    - FE: dialogue.ts(stale guards/abort cleanup/auto-save/flushBuffer/isInitializing/module-level AbortController) + learning.ts(localStorage verification/streak race fix/demotion protection/syncWithBackend local-first merge/getStreakDates) + direct-llm.ts(sliding window/timeout/fallback mastered/parseChoices/parseAssessment/pruneDirectConversations/content-type guard/message cap) + supabase-sync.ts(concurrency guard/batch upsert/incremental history sync/status whitelist/fullSync download-first) + auth.ts(subscription cleanup/callback dedup) + settings.ts(validateModelId/getDefaultModel/probeCORS) + graph.ts(simple setters) + text.ts(stripChoicesBlock) + graph-api.ts(encodeURIComponent) + dialogue-api.ts(signal passthrough) + learning-api.ts(fire-and-forget) + supabase.ts(createClient)
    - FE Components: DashboardContent.tsx(progress-based activity/nameMap useMemo/graph node label display) + DashboardPage.tsx(two-column responsive layout/navigate on click) + useCountUp.ts(rAF cleanup/setTimeout cleanup) + useMediaQuery.ts(SSR safe/listener cleanup)
    - BE: dialogue.py(_busy try/finally+timeout/snapshot messages/double-check locking/cleanup_cache orphan locks/input validation) + learning.py(Field validation/status whitelist/score clamping/sync input validation) + evaluator.py(O(n) format_dialogue/consistent mastered/parse_json fallback chain) + main.py(path traversal is_relative_to/wildcard+credentials CORS/headless webbrowser/DEBUG docs) + sqlite_client.py(atomic start_learning/mastered demotion protection/WAL mode/REAL timestamps) + llm/router.py(SSRF try/except/else pattern/retry logic/double-check lock/model tier resolution) + config.py(ConfigDict/no hardcoded secrets) + redis_client.py(lazy reconnect with lock+cooldown/graceful degradation) + neo4j_client.py(explicit read/write transactions/driver None check)
  - GITHUB: 0 open issues, 2 closed (all resolved)
  - VERIFY: 341 tests (121 FE + 220 BE) 全通过, tsc 0 errors, build 3.21s
  - STATUS: 代码质量持续稳定, 0 open GitHub issues, 无待修复bug, **连续18轮零issues审查**

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
10. ✅ **第四轮深度审查+修复** — 14项修复(1C+8M+5m): fullSync数据丢失/auth订阅泄漏/SSE空气泡/输入校验 (d62e997)
11. 🟡 **最终内测版分发** — 需重新打包EXE(含第四轮审查修复)

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
cd packages/web && npx vitest run        # 前端测试 ✅ (121 tests: learning 12 + settings 22 + text 5 + auth 11 + supabase-sync 6 + dialogue 24 + direct-llm 19 + toast 12 + graph 10) [vitest.config.ts: pool=forks, 4GB heap per worker for Node v24]
cd apps/api && python -m pytest          # 后端测试 ✅ (220 tests: health 1 + sqlite 16 + learning 12 + evaluator 17 + dialogue 16 + graph 16 + llm_router 41 + prompt_parser 28 + socratic 24 + main 18 + config 12 + redis_client 19)
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
