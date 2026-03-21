# RAG 知识库迭代进化方案

> **文档版本**: v2.0
> **创建日期**: 2026-03-21
> **最后更新**: 2026-03-21
> **状态**: 🔥 最高优先级 — Sprint 0+1 完成, Sprint 1.5 (research-rewrite-v2) 进行中
> **关联**: `CLAUDE.md` (项目状态) / `EXPANSION_PLAN.md` (多球体路线图) / `DEVELOPMENT_PLAN.md` (MVP定义)

---

## 一、问题诊断

当前 5,996 篇 RAG 文档存在三个层级的质量差异：

| 层级 | 域数 | 概念数 | 平均文档大小 | 核心问题 |
|:---|:---:|:---:|:---:|:---|
| **Tier-S** 手工精写 | 1 域（llm-core 部分） | ~36 | 3,786B | 基本达标，仍可提升 |
| **Tier-B** 脚本生成+占位 | 10 域（通识） | ~1,871 | 1,232-1,740B | 仅概念名+子域级模板，同子域概念共享同一段"关键要点" |
| **Tier-C** 对话批量生成 | 18 域（游戏开发） | ~4,089 | 1,108-1,221B | 每篇仅 1KB，"基本原理/设计原则/常见误区"三段完全雷同 |

**关键约束**：苏格拉底引擎每次只取 3,000 字符送入 LLM，RAG 文档的有效信息密度比总字数更关键。

**当前质量分布估算**：Tier-S ~10 篇, Tier-A ~26 篇, Tier-B ~0 篇, Tier-C ~5,960 篇。

---

## 二、设计原则

1. **渐进式改写，不做一次性重构** — 5,996 篇不可能一次全部提升，必须有优先级
2. **来源可追溯** — 每篇文档记录内容来源（AI 生成 / 教科书改写 / 论文引用 / 社区验证）
3. **质量可度量** — 引入 quality_score，可自动检测和排序
4. **管线化** — 改写过程是可重复、可自动化的流水线，不依赖人工逐篇操作
5. **知识获取多元化** — 不只靠 AI 自己"编"，要有外部知识注入通道

---

## 三、知识文档 Schema v2

当前文档只有最简的 YAML frontmatter。新结构需要为迭代进化预留元数据：

```yaml
---
# === 基本标识 ===
id: "cell-membrane"
concept: "细胞膜"
domain: biology
subdomain: cell-biology
difficulty: 2

# === 质量元数据（新增） ===
content_version: 2          # 文档内容版本号，每次改写+1
quality_tier: "B"           # S/A/B/C 四级
quality_score: 45           # 0-100 自动评分
last_reviewed: "2026-03-21"
generation_method: "template-v1"  # template-v1 | ai-rewrite-v1 | human-curated | source-based

# === 来源追踪（新增） ===
sources:
  - type: "textbook"
    ref: "Alberts et al. Molecular Biology of the Cell, 7th ed."
    sections: ["Ch.10 Membrane Structure"]
  - type: "wikipedia"
    url: "https://en.wikipedia.org/wiki/Cell_membrane"
    retrieved: "2026-03-21"
  - type: "ai-generated"
    model: "claude-sonnet-4"
    prompt_version: "rewrite-v2"

# === 教学元数据 ===
key_facts: 3               # 文档包含的关键知识点数
has_examples: true          # 是否含具体示例/案例
has_formulas: false         # 是否含公式
has_code: false             # 是否含代码
unique_content_ratio: 0.85  # 概念特异内容占比（vs 模板内容）
---
```

---

## 四、质量评分体系（Quality Score）

自动化评分，每次文档变更后重新计算：

```
quality_score = Σ(维度权重 × 维度得分), 满分100
```

| 维度 | 权重 | 评分规则 |
|:---|:---:|:---|
| 概念特异性 | 30% | 正文非模板段落占比。0分: <20%, 50分: 20-60%, 100分: >80% |
| 信息密度 | 25% | 去除标题/格式后有效字符数。0分: <500, 50分: 500-1500, 100分: >2000 |
| 来源可信度 | 20% | sources 字段质量。0分: 仅AI, 50分: AI+wiki, 100分: 教科书/论文 |
| 结构完整度 | 15% | 必备段落数(核心概念/关键要点/常见误区/衔接/应用)。0分: ≤2段, 50分: 3-4段, 100分: 5+段 |
| 教学适配度 | 10% | 难度标注准确/有引导性问题/有类比或案例。各项布尔，满足一项33分 |

**质量分层映射**：

| Tier | quality_score | 含义 |
|:---|:---:|:---|
| **S** | 80-100 | 教科书级，有权威来源，概念特异，有案例/公式/代码 |
| **A** | 60-79 | AI 精写+来源验证，信息密度高 |
| **B** | 40-59 | AI 改写，比模板好但缺来源验证 |
| **C** | 0-39 | 纯模板/占位符，基本无概念特异内容 |

---

## 五、知识来源金字塔

```
                    ┌─────────┐
                    │ 教科书  │  ← 最权威, 手动引入, 精确科学域优先
                    │ /论文   │
                  ┌─┴─────────┴─┐
                  │  权威Wiki   │  ← 半自动, WebSearch抓取
                  │  /百科/MDN  │
                ┌─┴─────────────┴─┐
                │   AI 精写改写    │  ← 自动, Claude逐篇改写
                │  (有来源指导)    │
              ┌─┴─────────────────┴─┐
              │  当前模板生成内容    │  ← 现有5960篇, 待提升
              └─────────────────────┘
```

| 通道 | 获取方式 | 适用域 | 可信度 | 自动化程度 |
|:---|:---|:---|:---:|:---:|
| **L1: 教科书/论文** | 手动录入关键段落+引用 | 物理/数学/生物/经济学 | ★★★★★ | 低 |
| **L2: Wikipedia/百科** | WebSearch→提取核心段落→AI改写为教学体 | 全域 | ★★★★ | 高 |
| **L3: 官方文档/MDN** | WebSearch→提取 | 技术域(游戏引擎/软工/前端) | ★★★★★ | 高 |
| **L4: AI领域知识精写** | Claude基于seed概念+先修关系逐篇生成 | 全域 | ★★★ | 最高 |
| **L5: 用户反馈驱动** | 学习对话中用户纠正→标记→审核 | 长期全域 | ★★★★ | 中 |

---

## 六、改写管线（Rewrite Pipeline）

### 6.1 管线架构

```
输入:                       处理:                          输出:
seed_graph.json  ──┐
                   ├──→ [Phase 1: 评估] ──→ quality_score + tier
current_rag.md  ──┘         │
                            ▼
                   [Phase 2: 知识获取]
                   WebSearch → 抓取权威来源
                   提取关键事实 → fact_sheet.json
                            │
                            ▼
                   [Phase 3: AI 改写]
                   system_prompt + fact_sheet + current_rag
                   → Claude 逐篇生成新版本
                            │
                            ▼
                   [Phase 4: 验证]
                   事实检查 + 质量评分 + 差异对比
                   → 通过则覆盖, 否则标记人工审核
                            │
                            ▼
                   updated_rag.md (content_version +1)
```

### 6.2 改写 Prompt 模板

```
你是一位{domain_name}领域的教学内容专家。请为以下概念撰写一篇教学参考文档。

## 概念信息
- 名称: {name}
- 描述: {description}
- 所属子域: {subdomain_name}
- 难度: {difficulty}/9
- 先修概念: {prerequisites}
- 后续概念: {next_concepts}

## 外部参考资料（你必须基于这些事实撰写，不可编造）
{fact_sheet_content}

## 撰写要求
1. 【概念特异性】内容必须专门针对"{name}"，不得使用通用模板语句
2. 【信息密度】正文 1500-2500 字，每段必须包含该概念特有的知识点
3. 【核心知识点】至少包含 3 个可验证的关键事实（公式/定义/数据/案例）
4. 【常见误区】列举 2-3 个该概念特有的常见误解（不是通用学习建议）
5. 【衔接性】明确说明与先修概念的关系，以及学完后能解锁什么

## 禁止事项
- 禁止"理解X需要把握其基本定义和关键性质"这类万金油句子
- 禁止对所有概念使用相同的"设计原则"/"学习建议"段落
- 如果不确定某个事实，用 [待验证] 标记
```

### 6.3 改写优先级

```
priority = (1 - quality_score/100) × usage_weight × domain_weight

usage_weight:  里程碑节点 ×3, 低difficulty(入门) ×2, 普通 ×1
domain_weight: 精确科学(物理/数学/生物) ×2, 技术域 ×1.5, 通识域 ×1
```

---

## 七、验证体系

### 7.1 自动验证（每次改写后）

| 检查项 | 方法 | 阈值 |
|:---|:---|:---|
| 格式完整 | YAML frontmatter 必填字段检查 | 必须通过 |
| 唯一性 | 与同子域其他文档做余弦相似度 | < 0.7 |
| 长度 | 去除标题/格式后纯文本字数 | ≥ 800 字 |
| 事实标记 | 检查是否含 `[待验证]` 标记 | 有则降级为 Tier-B |
| 来源标注 | sources 字段非空 | 否则 quality_score 上限 59 |

### 7.2 交叉验证（定期批量）

对高优先级概念的关键事实声明做 WebSearch 验证，矛盾则标记人工审核。

### 7.3 用户反馈驱动

学习对话中的纠正/质疑 → 自动收集到 review_queue → 每 N 个质疑触发 AI 复核。

---

## 八、过时检测

```yaml
freshness:
  created: "2026-03-21"
  max_age_days: 365        # 通识域=永不过期, 技术域=365天
  last_verified: "2026-03-21"
  needs_refresh: false
```

---

## 九、执行路线图

### Sprint 0：基础设施（1-2 天） ✅ 完成
- [x] 实现 RAG Doc Schema v2（新增元数据字段）→ `scripts/upgrade_schema.py`
- [x] 实现 `quality_scorer.py` — 自动评分脚本（5维度100分制）
- [x] 对现有 5,996 篇文档执行首次全量评分 → `data/quality_report.json`
- [x] 编写 `rewrite_pipeline.py` 框架（Phase 1-4 骨架）

### Sprint 1：物理里程碑改写 ✅ 完成
- [x] 26 个物理里程碑概念精写（纯 AI 记忆改写 v1）
- [x] 物理域: avg 34.7→45.5, Tier-S 0→7, Tier-A 0→19, Tier-C 194→14
- [x] 批量脚本: `batch_rewrite_physics.py` (6), `batch_rewrite_physics2.py` (4), `batch_rewrite_physics3.py` (12)

### Sprint 1.5：研究增强改写 v2 🔥 进行中

**核心升级：每个概念精写前必须通过 WebResearch 获取外部来源**

新增工具: `scripts/research_rewrite.py`

工作流:
```
seed_graph元数据 → 生成4条搜索查询(中英各2) → WebSearch
→ 阅读3-5个优先来源(Wikipedia > 教科书在线版 > Khan Academy)
→ 编译 external_knowledge + sources.json
→ AI基于来源精写(v2 prompt: 禁止无来源编造)
→ 验证 + 回写(generation_method: research-rewrite-v2)
```

已验证效果:
- `cell-membrane` (biology): 13.8 → **93.3** (Tier-C → Tier-S)
- `accessibility-audit` (game-design): 17.9 → **82.6** (Tier-C → Tier-S)

批量执行计划:
- [ ] biology 域 milestone 概念 (~15 篇)
- [ ] game-design 域 milestone 概念 (~25 篇)
- [ ] mathematics 域 milestone 概念 (~20 篇)
- [ ] economics 域 milestone 概念 (~15 篇)
- [ ] 剩余域 milestone 概念

### Sprint 2：精确科学入门层改写（3-5 天）
- [ ] 物理/数学/生物/经济学 difficulty 1-3（约 300 篇）
- [ ] 全部使用 research-rewrite-v2 流程
- [ ] 目标：300 篇 Tier-C → Tier-A+

### Sprint 3：全域质量提升管线化（持续）
- [ ] 批量改写调度器（按 priority 排序，每次 50 篇）
- [ ] 集成到项目 CI
- [ ] quality dashboard 可视化

### 长期：用户反馈驱动进化
- [ ] 学习对话纠正自动收集
- [ ] 季度全量质量复扫
- [ ] 技术域年度刷新

---

## 十、预期效果

| 指标 | 初始状态 | Sprint 0+1 后(实际) | Sprint 1.5 预期 | Sprint 2 预期 | 6 个月预期 |
|:---|:---:|:---:|:---:|:---:|:---:|
| Tier-S 文档数 | ~10 | 9 (+v1精写) | ~100 | ~300 | ~1,000 |
| Tier-A 文档数 | ~26 | 19 (physics) | ~200 | ~500 | ~2,000 |
| Tier-C 文档数 | ~5,960 | ~5,820 | ~5,500 | ~4,500 | ~2,000 |
| 平均 quality_score | ~15 | 31.0 | ~35 | ~42 | ~60 |
| 有外部来源 | 0% | <1% (physics) | ~5% | ~15% | ~50% |
| generation_method: research-rewrite-v2 | 0 | 2 | ~100 | ~400 | ~2,000 |
