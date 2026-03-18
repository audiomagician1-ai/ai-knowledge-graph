# AI知识图谱 — 后续扩展计划

> **文档版本**: v1.0
> **创建日期**: 2026-03-18
> **状态**: 规划中
> **关联**: `DEVELOPMENT_PLAN.md` (MVP定义) / `CLAUDE.md` (项目状态)

---

## 一、扩展愿景

### 1.1 核心理念

> **一个球 → 一片星系**
>
> 当前产品是单个"AI工程"知识连接球。扩展方向是将其演变为一个**知识星系**：
> 每个知识领域是一个独立的知识球（星球），用户可以自由切换、探索不同领域的知识宇宙。

### 1.2 产品形态

```
当前状态:
  ┌─────────────────┐
  │   🟣 AI工程球    │  ← 单球, 267节点, 15子域
  │  (唯一知识域)    │
  └─────────────────┘

扩展目标:
  ┌─────────────────────────────────────────────────────┐
  │                    知识星系                           │
  │                                                     │
  │   🟣 AI工程    🔵 数学       🟢 物理              │
  │                                                     │
  │   🟠 金融      🔴 设计       🟡 语言              │
  │                                                     │
  │   ⚪ 哲学      🟤 生物       💜 心理学            │
  │                                                     │
  │           [切换器] [进度总览] [跨球关联]             │
  └─────────────────────────────────────────────────────┘
```

---

## 二、扩展分两条主线

### 主线A：当前AI工程球内容扩增

当前267节点/334边已覆盖15个子域，但部分子域深度不足，需要补充。

### 主线B：多球知识类型系统

推出覆盖不同知识领域的知识球，用户可切换。

---

## 三、主线A — AI工程球内容扩增

### 3.1 现有子域深度扩充

| 子域 | 现有节点数(估) | 目标节点数 | 扩充重点 |
|:---|:---:|:---:|:---|
| 计算机基础 | ~12 | 18 | 编译原理基础、进程/线程、死锁、内存管理(分页/分段) |
| 编程基础 | ~20 | 28 | 正则表达式、文件IO、并发基础、函数式编程初步、包管理 |
| 数据结构 | ~18 | 24 | B树/B+树、LRU缓存、Segment Tree、Fenwick树 |
| 算法 | ~25 | 35 | A*搜索、Floyd-Warshall、最大流、字符串哈希、随机算法 |
| 面向对象 | ~18 | 22 | 命令模式、适配器模式、模板方法、CQRS |
| Web前端 | ~22 | 30 | SSG/ISR、WebAssembly、Web Workers、Canvas/WebGL、状态机 |
| Web后端 | ~16 | 24 | gRPC、OpenAPI/Swagger、连接池、任务队列(Celery)、安全(XSS/CSRF/SQL注入) |
| 数据库 | ~16 | 22 | 窗口函数、CTE、数据库锁、MVCC、时序数据库 |
| DevOps | ~14 | 20 | Helm Charts、Service Mesh、日志聚合(ELK)、GitOps、安全扫描 |
| 系统设计 | ~14 | 22 | CQRS/Event Sourcing、分布式事务、设计Feed流、设计搜索引擎 |
| AI基础 | ~20 | 28 | GAN、Diffusion Model、自监督学习、强化学习基础、NLP经典(Word2Vec) |
| LLM核心 | ~20 | 30 | Speculative Decoding、KV Cache、RoPE、FlashAttention、Agent框架比较 |
| Prompt工程 | ~12 | 20 | Prompt注入防御、结构化输出、Multi-turn策略、Prompt模板设计模式 |
| RAG与知识库 | ~10 | 18 | Graph RAG、HyDE、混合检索、Reranking、文档解析Pipeline |
| Agent系统 | ~10 | 20 | Multi-Agent协作、Tool Use设计、Memory系统、Planning策略、Eval框架 |

**扩充目标**: 267 → **~400节点**, ~334 → **~550边**

### 3.2 RAG知识文档扩充

每个新增节点需配套RAG文档(`data/rag/{subdomain}/{concept}.md`)，包含：
- 核心概念讲解 (3000字以内)
- 关键代码示例 (标注语言)
- 常见误区
- 与相邻概念的关联说明

### 3.3 扩充执行计划

| Phase | 内容 | 预计新增 | 工时 |
|:---|:---|:---:|:---:|
| A-1 | LLM核心 + Agent系统 + RAG知识库深化 | ~30节点 | 3天 |
| A-2 | 算法 + 数据结构 + AI基础补充 | ~30节点 | 3天 |
| A-3 | Web前端 + Web后端 + 系统设计扩充 | ~25节点 | 2天 |
| A-4 | 其余子域补齐 + 全图边关系梳理 | ~25节点 | 2天 |
| A-5 | 全量RAG文档编写 + 质量审查 | 文档 | 3天 |

---

## 四、主线B — 多球知识类型系统

### 4.1 球类型规划（按优先级）

#### P0 — 首批上线（与AI工程球同等完成度）

| 球名称 | Domain ID | 图标 | 色调 | 预计节点 | 子域数 | 理由 |
|:---|:---|:---:|:---|:---:|:---:|:---|
| **数学基础** | `mathematics` | 🔵 | 蓝色系 | ~250 | 12 | AI/编程的基石,用户强需求 |
| **英语学习** | `english` | 🟡 | 金色系 | ~200 | 10 | 最大众化需求,验证非技术类球可行性 |

#### P1 — 第二批（验证多球后）

| 球名称 | Domain ID | 图标 | 色调 | 预计节点 | 子域数 |
|:---|:---|:---:|:---|:---:|:---:|
| **物理学** | `physics` | 🟢 | 绿色系 | ~200 | 10 |
| **产品设计** | `product-design` | 🔴 | 红色系 | ~180 | 8 |
| **金融理财** | `finance` | 🟠 | 橙色系 | ~160 | 8 |

#### P2 — 长期扩展

| 球名称 | Domain ID | 备注 |
|:---|:---|:---|
| **心理学** | `psychology` | 认知/发展/社会心理学 |
| **哲学** | `philosophy` | 西方+东方哲学体系 |
| **生物学** | `biology` | 分子/细胞/生态 |
| **经济学** | `economics` | 微观/宏观/行为经济学 |
| **写作技巧** | `writing` | 非虚构/技术写作/文案 |

### 4.2 数学基础球设计草案

```json
{
  "domain": {
    "id": "mathematics",
    "name": "数学",
    "description": "从算术到高等数学的系统知识体系",
    "icon": "🔵",
    "color": "#3b82f6"
  },
  "subdomains": [
    { "id": "arithmetic",        "name": "算术基础",     "order": 1 },
    { "id": "algebra",           "name": "代数",         "order": 2 },
    { "id": "geometry",          "name": "几何",         "order": 3 },
    { "id": "trigonometry",      "name": "三角学",       "order": 4 },
    { "id": "analytic-geometry", "name": "解析几何",     "order": 5 },
    { "id": "calculus",          "name": "微积分",       "order": 6 },
    { "id": "linear-algebra",    "name": "线性代数",     "order": 7 },
    { "id": "probability",       "name": "概率论",       "order": 8 },
    { "id": "statistics",        "name": "数理统计",     "order": 9 },
    { "id": "discrete-math",     "name": "离散数学",     "order": 10 },
    { "id": "number-theory",     "name": "数论",         "order": 11 },
    { "id": "optimization",      "name": "最优化",       "order": 12 }
  ]
}
```

### 4.3 英语学习球设计草案

```json
{
  "domain": {
    "id": "english",
    "name": "英语",
    "description": "从基础语法到高级表达的英语学习体系",
    "icon": "🟡",
    "color": "#eab308"
  },
  "subdomains": [
    { "id": "phonetics",         "name": "语音",         "order": 1 },
    { "id": "basic-grammar",     "name": "基础语法",     "order": 2 },
    { "id": "vocabulary",        "name": "核心词汇",     "order": 3 },
    { "id": "tenses",            "name": "时态系统",     "order": 4 },
    { "id": "sentence-patterns", "name": "句型结构",     "order": 5 },
    { "id": "advanced-grammar",  "name": "高级语法",     "order": 6 },
    { "id": "reading",           "name": "阅读理解",     "order": 7 },
    { "id": "writing-en",        "name": "写作",         "order": 8 },
    { "id": "speaking",          "name": "口语表达",     "order": 9 },
    { "id": "idioms-culture",    "name": "习语与文化",   "order": 10 }
  ]
}
```

---

## 五、架构改造方案

### 5.1 数据层改造

**当前**: 单domain `ai-engineering`, 种子数据在 `data/seed/programming/seed_graph.json`

**改造为**:
```
data/
  seed/
    ai-engineering/     ← 现有,重命名
      seed_graph.json
    mathematics/         ← 新增
      seed_graph.json
    english/             ← 新增
      seed_graph.json
  rag/
    ai-engineering/      ← 现有,按domain隔离
      cs-fundamentals/
      programming-basics/
      ...
    mathematics/          ← 新增
      arithmetic/
      algebra/
      ...
    english/              ← 新增
      phonetics/
      basic-grammar/
      ...
```

### 5.2 后端改造

```python
# 新增: GET /api/domains — 列出所有可用知识球
# 返回: [{ id, name, description, icon, color, stats: { nodes, edges, subdomains } }]

# 改造: 所有现有API添加 domain_id 参数
# GET /api/graph/data?domain=ai-engineering
# GET /api/graph/domains?domain=ai-engineering  → 改名 /api/graph/subdomains
# POST /api/dialogue/conversations  → body增加 domain_id
# GET /api/learning/progress?domain=ai-engineering
```

### 5.3 前端改造

#### 球切换器 (Domain Switcher)
```
位置: Sidebar顶部 / 移动端顶部导航栏
形态: 下拉选择器 + 球图标列表
行为: 切换后重新加载对应domain的图谱数据,学习进度独立
```

#### 每个球独立的:
- 3D球面图谱渲染 (保持现有知识连接球形态)
- 学习进度追踪 (per-domain progress)
- 对话历史 (per-domain conversations)
- Dashboard统计 (per-domain + 总览)

#### 新增星系总览页:
- 所有球的缩略3D预览
- 每个球的学习进度概览
- 跨球学习统计 (总掌握概念数、总学习时间、连续天数)

### 5.4 数据模型变更

```sql
-- 现有表增加 domain_id 列
ALTER TABLE user_concept_status ADD COLUMN domain_id TEXT DEFAULT 'ai-engineering';
ALTER TABLE learning_events ADD COLUMN domain_id TEXT DEFAULT 'ai-engineering';
ALTER TABLE conversations ADD COLUMN domain_id TEXT DEFAULT 'ai-engineering';

-- 新增: 领域配置表
CREATE TABLE domains (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT,
  color TEXT,
  node_count INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

---

## 六、球间关联系统（远期）

### 6.1 跨球先修关系

某些概念跨越多个知识球:
- 数学球 "线性代数" → AI工程球 "神经网络基础"
- 数学球 "概率论" → AI工程球 "机器学习基础"
- 数学球 "微积分" → 物理球 "牛顿力学"
- 英语球 "技术写作" → AI工程球 "Prompt工程"

```json
{
  "cross_domain_edges": [
    {
      "source": { "domain": "mathematics", "concept": "linear-algebra-fundamentals" },
      "target": { "domain": "ai-engineering", "concept": "neural-network-basics" },
      "type": "cross_prerequisite",
      "strength": "recommended"
    }
  ]
}
```

### 6.2 学习路径推荐

> "想学AI? 建议先完成数学球中线性代数和概率论的里程碑节点"

系统可根据目标球推荐其他球的前置学习路径。

---

## 七、执行时间线

```
Phase 5.5 (当前)           Phase 6                Phase 7               Phase 8
──────────────────    ──────────────────    ──────────────────    ──────────────────
Supabase Cloud上线     AI工程球内容扩增       多球架构改造           第二个球上线
Auth配置完成           267→400节点           domain切换器           数学基础球
默认免费LLM           RAG文档补全            后端多domain API       250节点种子图谱
持久化迭代            边关系梳理             前端球切换UI           RAG文档编写
                     质量审查               数据模型迁移           质量审查+测试
                                           星系总览页

~1周                  ~2周                   ~2周                   ~3周
```

### 7.1 详细Phase规划

#### Phase 6: AI工程球内容扩增 (2周)
- [ ] 6.1 LLM核心+Agent系统+RAG知识库 深度扩充 (~30节点)
- [ ] 6.2 算法+数据结构+AI基础 补充 (~30节点)
- [ ] 6.3 Web+系统设计+其余子域 扩充 (~50节点)
- [ ] 6.4 全图边关系梳理 (新增~200条边)
- [ ] 6.5 RAG文档全量补齐 + 质量审查
- [ ] 6.6 种子数据目录迁移 (`programming/` → `ai-engineering/`)

#### Phase 7: 多球架构改造 (2周)
- [ ] 7.1 数据层: seed/rag 多domain目录结构
- [ ] 7.2 后端API: 全部添加domain_id参数 + /api/domains端点
- [ ] 7.3 前端: domain store + 球切换器UI
- [ ] 7.4 前端: 图谱渲染按domain加载 + 每球独立配色
- [ ] 7.5 数据模型: Supabase migration + localStorage per-domain
- [ ] 7.6 Dashboard: 星系总览 + per-domain进度
- [ ] 7.7 测试: 多domain E2E测试

#### Phase 8: 数学基础球上线 (3周)
- [ ] 8.1 种子图谱设计 (12子域, ~250节点, ~350边)
- [ ] 8.2 里程碑节点选定 (~25个)
- [ ] 8.3 RAG知识文档编写 (~250篇)
- [ ] 8.4 苏格拉底引擎适配 (数学领域prompt调优)
- [ ] 8.5 评估器适配 (数学理解度评估逻辑)
- [ ] 8.6 质量审查 + 用户测试

#### Phase 9: 英语学习球 + 跨球关联 (3周)
- [ ] 9.1 英语球种子图谱 (10子域, ~200节点)
- [ ] 9.2 英语球RAG文档
- [ ] 9.3 对话引擎适配 (语言学习模式, 不同于知识讲解)
- [ ] 9.4 跨球先修关系数据建模
- [ ] 9.5 跨球学习路径推荐
- [ ] 9.6 星系视图增强 (球间连线可视化)

---

## 八、技术风险与对策

| 风险 | 影响 | 对策 |
|:---|:---|:---|
| 单球数据量增大后图谱渲染卡顿 | 400+节点Three.js性能 | LOD分层渲染, 远处节点简化, 按子域懒加载 |
| 非技术类球的苏格拉底引擎效果差 | 英语/哲学等领域对话质量 | 每个domain独立prompt模板, 评估维度可定制 |
| 多球数据量爆炸导致存储成本 | Supabase/存储增长 | RAG文档CDN缓存, 种子数据前端bundle, SQLite per-domain |
| 用户被过多选择淹没 | 新用户不知选哪个球 | 入口推荐问卷, 热门球优先展示, 引导式首次体验 |
| 跨球关联增加复杂度 | 数据模型/UI/推荐算法 | Phase 9再上线, 先验证单球切换可行性 |

---

## 九、成功指标

| 指标 | Phase 6 目标 | Phase 8 目标 | Phase 9 目标 |
|:---|:---|:---|:---|
| AI工程球节点数 | ≥380 | 维持 | 维持 |
| 知识球总数 | 1 | 2 | 3 |
| 总概念节点数 | ~400 | ~650 | ~850 |
| 测试覆盖率 | ≥360 tests | ≥420 tests | ≥480 tests |
| 球切换延迟 | N/A | <1s | <1s |
| 图谱渲染FPS | ≥30 (400节点) | ≥30 (250节点) | ≥30 |

---

## 十、总结

扩展的核心原则:
1. **保持知识连接球的视觉形态** — 这是产品的核心辨识度
2. **每个球独立完整** — 独立图谱、独立进度、独立对话
3. **渐进式上线** — 先扩充现有球,再造新球,最后连通
4. **质量优先** — 每个球的内容深度和对话质量必须达标才上线
5. **数据驱动** — 根据用户使用数据决定下一个球的优先级
