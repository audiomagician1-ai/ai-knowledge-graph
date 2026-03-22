---
id: "product-roadmap"
concept: "产品路线图"
domain: "product-design"
subdomain: "product-management"
subdomain_name: "产品管理"
difficulty: 2
is_milestone: false
tags: ["规划", "路线图", "管理"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Cagan, Inspired: How to Create Tech Products Customers Love, 2nd ed."
  - type: "textbook"
    name: "Lombardo et al., Product Roadmaps Relaunched"
scorer_version: "scorer-v2.0"
---
# 产品路线图

## 定义与核心概念

产品路线图（Product Roadmap）是将**产品战略**转化为可执行计划的沟通工具。Marty Cagan 在《Inspired》（2nd ed.）中区分了两种路线图哲学：

- **特性路线图**（Feature Roadmap）：列出要建的具体功能和时间表 → **Cagan 强烈反对**
- **结果路线图**（Outcome Roadmap）：定义要解决的问题和衡量指标 → **推荐**

核心区别：特性路线图假设"我们知道解决方案"，结果路线图承认"我们知道问题但需要发现解决方案"。

> "路线图的第一法则：没有人真正知道你的路线图上的东西是否能解决用户问题，直到你把它放到用户面前。" — Marty Cagan

## 路线图的三种时间范围

| 范围 | 时间跨度 | 确定性 | 粒度 | 受众 |
|------|---------|--------|------|------|
| **Now（当前）** | 本季度 | 高（已验证） | 具体 Epic/Story | 开发团队 |
| **Next（即将）** | 下季度 | 中（已发现问题，方案探索中） | 主题/目标 | 跨部门 |
| **Later（未来）** | 6-12月 | 低（方向性） | 战略主题 | 高管/投资人 |

Lombardo et al.（*Product Roadmaps Relaunched*）的关键原则：**越远的未来越模糊**——用主题而非功能，用问题而非解决方案。

## 路线图框架

### 1. Now-Next-Later 框架

最灵活的现代路线图格式，无固定日期：

```
┌─────────────────┬─────────────────┬─────────────────┐
│      NOW         │      NEXT       │     LATER       │
├─────────────────┼─────────────────┼─────────────────┤
│ 减少结账流失率   │ 个性化推荐引擎  │ 国际化支付      │
│ KR: 转化率+15%  │ KR: ARPU+20%   │ 目标: 3个新市场  │
│ [方案已验证]     │ [问题已验证]    │ [机会假设]       │
├─────────────────┼─────────────────┼─────────────────┤
│ 移动端性能优化   │ 社交分享功能    │ AI客服助手       │
│ KR: LCP<2.5s   │ KR: 病毒系数>1 │ 目标: CSAT>85%  │
│ [方案已验证]     │ [发现中]        │ [探索中]         │
└─────────────────┴─────────────────┴─────────────────┘
```

### 2. OKR 驱动的路线图

直接与组织 OKR 对齐：

```
Objective: 成为年轻用户最喜爱的购物平台
  KR1: 18-25岁 DAU 增长 40%
    → 主题: 社交购物体验
    → 发现: 短视频种草功能、好友推荐列表
  KR2: NPS 从 32 提升到 55
    → 主题: 售后体验优化
    → 发现: 即时退款、智能客服升级
  KR3: 首单转化率从 8% 提升到 15%
    → 主题: 新用户引导
    → 发现: 个性化首页、新人专属优惠
```

### 3. RICE 优先级评分

| 维度 | 含义 | 量化方法 |
|------|------|---------|
| **R**each | 影响多少用户/季度 | 绝对数（如 10,000 用户） |
| **I**mpact | 对单个用户的影响程度 | 3=巨大, 2=高, 1=中, 0.5=低, 0.25=微小 |
| **C**onfidence | 估计的可信度 | 100%=高, 80%=中, 50%=低 |
| **E**ffort | 工程人月投入 | 绝对数（如 3 人月） |

```
RICE Score = (Reach × Impact × Confidence) / Effort

示例：
功能A: (10000 × 2 × 80%) / 3 = 5,333
功能B: (5000 × 3 × 100%) / 6 = 2,500
→ 功能A优先
```

## 路线图的反模式

| 反模式 | 问题 | 替代方案 |
|--------|------|---------|
| **特性工厂** | 路线图全是功能列表，无战略对齐 | 用结果/主题替代功能 |
| **承诺型路线图** | 给所有利益相关者固定日期 | 用置信区间替代固定日期 |
| **销售驱动** | 路线图由客户请求列表决定 | 区分"请求"和"问题"，验证问题 |
| **技术债忽视** | 只有新功能，无平台投资 | 预留 20-30% 容量给技术债和基础设施 |
| **空中楼阁** | 战略宏大但无可执行步骤 | 确保 Now 栏有具体的 Sprint 计划 |

## 利益相关者管理

不同受众需要不同版本的路线图：

```
CEO/投资人路线图：
  - 3-5 个战略主题
  - 与公司 OKR 的对齐关系
  - 关键里程碑
  - 1页

工程团队路线图：
  - 具体 Epic 和依赖关系
  - 技术架构决策
  - Sprint 级别分解
  - JIRA/Linear 看板

销售/客户成功路线图：
  - "我们正在解决的客户问题"
  - 大致时间范围（Q级别，非天级别）
  - 绝不承诺特定功能或日期
```

## 路线图评审节奏

| 评审类型 | 频率 | 参与者 | 产出 |
|---------|------|--------|------|
| 战略对齐 | 季度 | PM + 高管 | Now-Next-Later更新 |
| 优先级调整 | 双周 | PM + 工程Lead | RICE重新评估 |
| Sprint计划 | 每1-2周 | 产品团队 | Sprint backlog |
| 客户反馈整合 | 持续 | PM + CS | 问题验证和优先级输入 |

## 参考文献

- Cagan, M. (2017). *Inspired: How to Create Tech Products Customers Love*, 2nd ed. Wiley. ISBN 978-1119387503
- Lombardo, C.T. et al. (2017). *Product Roadmaps Relaunched*. O'Reilly Media. ISBN 978-1491971727
- Intercom (2019). "Intercom on Product Management," Intercom Inc. [内部框架 RICE scoring 的原始提出者]

## 教学路径

**前置知识**：产品管理基础概念、用户研究方法
**学习建议**：先分析一个真实产品（如 Notion、Figma）的公开路线图，理解其结构。然后用 Now-Next-Later 框架为一个假想产品制定路线图。最后练习用 RICE 评分对 10 个候选功能排序。
**进阶方向**：产品发现（Product Discovery）方法论、双轨开发（Dual-Track Agile）、平台产品的路线图特殊考量。
