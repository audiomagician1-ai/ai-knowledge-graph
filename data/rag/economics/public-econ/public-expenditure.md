---
id: "public-expenditure"
concept: "公共支出"
domain: "economics"
subdomain: "public-econ"
subdomain_name: "公共经济学"
difficulty: 2
is_milestone: false
tags: ["支出", "财政", "公共品"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Stiglitz & Rosengard, Economics of the Public Sector, 4th ed."
  - type: "data"
    name: "OECD Government at a Glance 2023"
scorer_version: "scorer-v2.0"
---
# 公共支出

## 定义与核心概念

公共支出（Public Expenditure）指政府为提供公共服务、基础设施和转移支付而进行的资源配置活动。Stiglitz 在《公共部门经济学》中将其本质概括为：**政府代替市场做出的"谁得到什么"的分配决策**。

2023 年 OECD 国家平均政府支出占 GDP 的 **40.5%**，其中法国最高（58.1%），韩国最低（24.7%）。这一巨大差异反映了各国对"市场失灵的边界在哪里"这个根本问题的不同回答（OECD Government at a Glance, 2023）。

## 公共支出的功能分类（COFOG体系）

联合国政府职能分类（COFOG）将公共支出分为 10 大类：

| 功能类别 | OECD均值(GDP%) | 代表性项目 |
|---------|--------------|-----------|
| 社会保障 | 14.2% | 养老金、失业保险、社会救助 |
| 医疗卫生 | 7.8% | 公立医院、医保补贴 |
| 教育 | 4.9% | 公立学校、大学拨款、助学金 |
| 一般公共服务 | 4.7% | 行政机构运行、债务利息 |
| 经济事务 | 4.5% | 交通基础设施、产业补贴 |
| 国防 | 1.5% | 军事开支（NATO目标为GDP 2%） |
| 公共秩序与安全 | 1.6% | 警察、司法、消防 |
| 住房与社区 | 0.6% | 保障房、城市规划 |
| 环境保护 | 0.5% | 污染治理、自然保护 |
| 文娱宗教 | 0.6% | 公共图书馆、文化遗产 |

## 公共支出的经济学原理

### 公共品理论（Samuelson条件）

纯公共品满足**非竞争性**（一人消费不减少他人消费）和**非排他性**（无法排除未付费者），市场无法有效供给。

最优供给条件（Samuelson, 1954）：

```
Σ MRS_i = MRT

其中：
MRS_i = 个体i对公共品的边际替代率（愿意放弃多少私人品来获得一单位公共品）
MRT = 生产转换的边际技术率（生产一单位公共品的机会成本）
```

与私人品不同（MRS = MRT 对每个人成立），公共品的最优条件要求对所有消费者的边际价值**求和**。

### Wagner定律（政府支出增长趋势）

Adolph Wagner（1890）观察到：随着人均收入增长，政府支出占 GDP 比重倾向于上升。三个驱动机制：

1. **行政与保护功能扩展**：工业化带来的合同执行、产权保护需求
2. **文化与福利功能**：收入弹性 > 1 的服务（教育、医疗）需求增长更快
3. **自然垄断管理**：基础设施规模经济要求政府参与

实证检验（Lamartina & Zaghini, 2011）：对 23 个 OECD 国家 1970-2006 数据分析，支出收入弹性为 **1.07-1.18**，基本支持 Wagner 定律，但弹性在高收入阶段趋于下降。

### Baumol 成本病

公共部门劳动密集型服务（教育、医疗）的生产率增长慢于制造业，但工资必须与制造业保持竞争力，导致**公共服务的相对成本持续上升**。

```
数值示例：
制造业：生产率年增 3%，工资年增 3% → 单位成本不变
教育部门：生产率年增 0.5%，工资年增 3%（竞争压力）→ 单位成本年增 2.5%
30年后：教育服务的相对价格变为 (1.025)^30 ≈ 2.1 倍
```

## 支出效率评估

### 成本效益分析（CBA）框架

公共项目决策的标准工具：

| 步骤 | 核心问题 | 技术难点 |
|------|---------|---------|
| 1. 识别效益与成本 | 包括外部性 | 间接效益的边界界定 |
| 2. 货币化估值 | 非市场品的WTP | 统计生命价值（VSL）争议 |
| 3. 贴现 | 社会贴现率选择 | Stern（1.4%） vs Nordhaus（4.3%） |
| 4. 敏感性分析 | 关键假设变化的影响 | 分布假设选择 |

**关键争议——社会贴现率**：Stern Review（2006）使用 1.4% 贴现率得出"立即大力减排"的结论；Nordhaus 使用 4.3% 得出"渐进减排"的结论。仅这一个参数就能翻转价值 **数万亿美元** 的政策建议。

### 公共支出效率的 DEA 方法

数据包络分析（Data Envelopment Analysis）用于比较同类公共服务提供者的相对效率。例如：对比各国教育支出效率时，投入为人均教育支出，产出为 PISA 成绩。

Herrera & Pang（2005）对 140 国的 DEA 分析发现：发展中国家的教育支出效率平均仅为前沿面的 **60%**，意味着在不增加支出的情况下，产出仍有 40% 的提升空间。

## 支出控制机制

### 财政规则的国际实践

| 规则类型 | 代表国家 | 具体内容 |
|---------|---------|---------|
| 债务上限 | 欧盟（马斯特里赫特） | 公债 < GDP 60% |
| 赤字上限 | 欧盟 | 年度赤字 < GDP 3% |
| 支出上限 | 瑞典、荷兰 | 设定3年滚动支出天花板 |
| 平衡预算 | 瑞士（债务刹车） | 结构性预算平衡 |

瑞典的支出上限制度（1997年引入）被认为是最成功的案例：政府支出占 GDP 比重从 1993 年的 **67%** 降至 2019 年的 **49%**，同时维持了高水平的公共服务质量（IMF Fiscal Monitor, 2020）。

## 参考文献

- Stiglitz, J. & Rosengard, J. (2015). *Economics of the Public Sector*, 4th ed. W.W. Norton. ISBN 978-0393925227
- Samuelson, P. (1954). "The Pure Theory of Public Expenditure," *Review of Economics and Statistics*, 36(4), 387-389.
- Herrera, S. & Pang, G. (2005). "Efficiency of Public Spending in Developing Countries," World Bank Policy Research Working Paper 3645.
- Lamartina, S. & Zaghini, A. (2011). "Increasing Public Expenditure: Wagner's Law in OECD Countries," *German Economic Review*, 12(2).

## 教学路径

**前置知识**：微观经济学基础（供需、外部性）、基础统计学
**学习建议**：先理解"为什么需要公共支出"（公共品理论），再学"花多少"（Wagner定律、Baumol成本病），最后学"如何花得更好"（CBA、DEA）。建议用 OECD 数据库做跨国对比分析练习。
**进阶方向**：公共选择理论（政治决策如何扭曲最优支出）、代际核算（Generational Accounting）。
