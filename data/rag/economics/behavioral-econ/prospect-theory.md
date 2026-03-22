---
id: "prospect-theory"
concept: "前景理论"
domain: "economics"
subdomain: "behavioral-econ"
subdomain_name: "行为经济学"
difficulty: 2
is_milestone: false
tags: ["核心", "决策", "心理偏差"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "paper"
    name: "Kahneman & Tversky (1979) Prospect Theory: An Analysis of Decision under Risk"
  - type: "paper"
    name: "Tversky & Kahneman (1992) Advances in Prospect Theory: Cumulative Representation"
scorer_version: "scorer-v2.0"
---
# 前景理论

## 定义与历史背景

前景理论（Prospect Theory）是 Daniel Kahneman 和 Amos Tversky 于 1979 年提出的描述性决策模型，解释人们在**不确定性条件下如何做出选择**。它直接挑战了预期效用理论（Expected Utility Theory, EUT）的理性人假设，揭示了人类决策中系统性偏离理性的模式。

Kahneman 因此获得 2002 年诺贝尔经济学奖（Tversky 于 1996 年去世，未能共享此奖）。原始论文（Kahneman & Tversky, 1979）至今被引用超过 **80,000 次**，是社会科学领域被引最高的论文之一。

## 预期效用理论的失败

前景理论的出发点是 EUT 无法解释的实验现象：

### Allais 悖论（1953）

| 问题 | 选项A | 选项B | 多数人选择 |
|------|------|------|-----------|
| 问题1 | 确定得 $3000 | 80%概率得 $4000 | A（确定性偏好） |
| 问题2 | 25%概率得 $3000 | 20%概率得 $4000 | B（偏好反转！） |

在 EUT 下，选A意味着 u(3000) > 0.8·u(4000)，推导出 0.25·u(3000) > 0.20·u(4000)，应选A。但实验中多数人在问题2选B——这违反了 EUT 的独立性公理。

## 前景理论的四大支柱

### 1. 参考点依赖（Reference Dependence）

人们评估结果的方式是相对于**参考点**的偏离（gains/losses），而非绝对财富水平。

```
EUT:  U = u(W + x)        # 最终财富的效用
PT:   v = v(x - r)         # 相对于参考点r的偏离的价值
```

**实验证据**：同一个人拥有 $1,100 时的满意度，取决于他原来有 $1,000（获得 $100→开心）还是 $1,200（损失 $100→痛苦），尽管最终财富完全相同。

### 2. 损失厌恶（Loss Aversion）

损失带来的心理痛苦约为同等收益带来的快乐的 **2-2.5 倍**。

价值函数的数学形式（Tversky & Kahneman, 1992）：

```
v(x) = x^α          当 x ≥ 0 (收益域)
v(x) = -λ(-x)^β     当 x < 0 (损失域)

参数估计值：
α = 0.88 (收益域递减敏感度)
β = 0.88 (损失域递减敏感度)  
λ = 2.25 (损失厌恶系数)
```

这意味着：失去 $100 的痛苦 ≈ 获得 $225 的快乐。

### 3. 递减敏感性（Diminishing Sensitivity）

价值函数在收益域为凹函数（risk averse），在损失域为凸函数（risk seeking）：
- 从 $0 到 $100 的心理增量 > 从 $900 到 $1000 的增量
- 从 -$0 到 -$100 的心理痛苦 > 从 -$900 到 -$1000 的痛苦

**推论（四重模式）**：

| | 高概率 | 低概率 |
|---|--------|--------|
| **收益** | 风险厌恶（确定性效应） | 风险寻求（买彩票） |
| **损失** | 风险寻求（赌一把） | 风险厌恶（买保险） |

### 4. 概率加权（Probability Weighting）

人们不按客观概率评估——对小概率**过度加权**，对大概率**不足加权**：

```
π(p) = p^γ / [p^γ + (1-p)^γ]^(1/γ)

γ = 0.61 (收益域)
γ = 0.69 (损失域)

关键转换点：
π(0.01) ≈ 0.06  (小概率被放大6倍)
π(0.50) ≈ 0.42  (中概率被低估)
π(0.99) ≈ 0.91  (高概率的确定性缺口)
```

## 累积前景理论（CPT, 1992）

原始 PT 存在两个技术问题：违反随机占优（stochastic dominance）、无法处理多结果赌博。Tversky & Kahneman（1992）提出累积前景理论解决：

关键改进：
- 概率加权函数应用于**累积分布**而非单个概率
- 收益域和损失域分别独立处理后合并

CPT 下的价值计算：

```
V = Σ π+(p_i) · v(x_i)  [对所有 x_i ≥ 0]
  + Σ π-(p_j) · v(x_j)  [对所有 x_j < 0]
```

## 应用领域

### 金融市场

- **处置效应**（Disposition Effect）：投资者过早卖出赢利股票（锁定收益）、过久持有亏损股票（损失域风险寻求）。Odean（1998）分析 10,000 个交易账户，发现投资者卖出盈利股的概率比卖出亏损股高 **50%**。

### 保险市场

- **过度保险**：人们为小概率灾难事件支付远高于精算公平保费的价格（π(0.001) >> 0.001）

### 产品定价

- **价格框架**："省 $50" vs "获得 $50 折扣" → 框架为避免损失时转化率更高
- **捆绑销售**：将多项费用合并（一次损失 < 多次分离损失的总痛苦）

### 游戏设计

- **gacha 机制**：低概率高价值物品的吸引力（小概率过度加权）
- **损失框架**：限时活动"错过将失去"比"参与可获得"更有效

## 批评与局限

| 批评 | 提出者 | 核心论点 |
|------|-------|---------|
| 参考点不确定 | Kőszegi & Rabin (2006) | 参考点应为"理性预期"而非现状 |
| 参数不稳定 | 多项 meta-analysis | λ 的估计值在 1.5-5.0 之间波动 |
| 进化解释缺乏 | 进化心理学者 | 损失厌恶可能是食物匮乏时代的适应性特征 |
| 领域特异性 | 实验经济学 | 金融决策 vs 健康决策的参数显著不同 |

## 参考文献

- Kahneman, D. & Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk," *Econometrica*, 47(2), 263-291. [doi: 10.2307/1914185]
- Tversky, A. & Kahneman, D. (1992). "Advances in Prospect Theory: Cumulative Representation of Uncertainty," *Journal of Risk and Uncertainty*, 5(4), 297-323.
- Odean, T. (1998). "Are Investors Reluctant to Realize Their Losses?" *The Journal of Finance*, 53(5), 1775-1798.
- Kőszegi, B. & Rabin, M. (2006). "A Model of Reference-Dependent Preferences," *Quarterly Journal of Economics*, 121(4).

## 教学路径

**前置知识**：基础概率论、预期效用理论基础
**学习建议**：先通过 Allais 悖论理解 EUT 的失败，再逐一学习 PT 四大支柱。手算几个 CPT 价值函数的数值例子（如比较 v(100) 与 v(-100)·λ）。最后用 PT 解释日常决策现象（为什么买保险又买彩票）。
**进阶方向**：Kőszegi-Rabin 参考点模型、神经经济学中损失厌恶的脑区定位（杏仁核）。
