---
id: "hypothesis-testing"
concept: "假设检验"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "统计学"
difficulty: 2
is_milestone: false
tags: ["推断", "检验", "p值"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Casella & Berger, Statistical Inference, 2nd ed."
  - type: "paper"
    name: "Wasserstein & Lazar (2016) ASA Statement on p-Values"
scorer_version: "scorer-v2.0"
---
# 假设检验

## 定义与核心框架

假设检验（Hypothesis Testing）是统计推断的核心方法，通过样本数据判断关于总体参数的某个假设是否合理。Neyman-Pearson（1933）将其形式化为一个**二元决策问题**：

```
H₀: 零假设（Null Hypothesis）— 默认假设，通常是"无效应/无差异"
H₁: 备择假设（Alternative Hypothesis）— 研究者希望支持的假设

决策规则：
  若检验统计量落入拒绝域 → 拒绝 H₀
  否则 → 不拒绝 H₀（注意：不是"接受 H₀"）
```

### 两类错误

| | 真实情况：H₀为真 | 真实情况：H₀为假 |
|---|---|---|
| **决策：不拒绝H₀** | 正确（概率=1-α） | **第二类错误β**（漏检） |
| **决策：拒绝H₀** | **第一类错误α** | 正确（功效=1-β） |

- α（显著性水平）：通常设为 0.05，Fisher 的"合理怀疑"标准
- β：取决于样本量、效应大小、α 水平
- 统计功效 = 1-β：检测真实效应的能力（推荐 ≥ 0.80）

## 检验流程

### 标准五步法

```
1. 陈述假设：H₀: μ = μ₀,  H₁: μ ≠ μ₀（双尾）或 μ > μ₀（单尾）
2. 选择显著性水平：α = 0.05
3. 计算检验统计量：
   z = (x̄ - μ₀) / (σ/√n)     [σ已知，正态总体]
   t = (x̄ - μ₀) / (s/√n)     [σ未知，df=n-1]
4. 确定p值或临界值
5. 做出决策
```

### p 值的精确含义

p 值 = **在 H₀ 为真的条件下**，观察到当前样本统计量或更极端值的概率。

```
示例：检验新药是否有效
H₀: μ_新药 = μ_安慰剂
样本数据 → t = 2.31, df = 48
p = 0.025

解读：如果新药真的无效（H₀为真），我们有 2.5% 的概率观察到这么大或更大的差异
由于 p < α = 0.05 → 拒绝 H₀
```

**ASA 声明（Wasserstein & Lazar, 2016）**的六条原则：
1. p 值可以指示数据与模型的不兼容程度
2. p 值**不是** H₀ 为真的概率
3. 科学结论不应仅基于 p 值是否超过阈值
4. 需要完整报告和透明度
5. p 值不衡量效应大小或结果重要性
6. p 值本身不提供关于模型或假设的好的证据度量

## 常用检验方法

| 检验 | 适用场景 | 检验统计量 | 假设条件 |
|------|---------|-----------|---------|
| 单样本 z 检验 | 总体 σ 已知 | z = (x̄-μ₀)/(σ/√n) | 正态分布或 n>30 |
| 单样本 t 检验 | 总体 σ 未知 | t = (x̄-μ₀)/(s/√n) | 正态分布 |
| 独立 t 检验 | 两独立组均值比较 | t = (x̄₁-x̄₂)/SE | 正态、方差齐性 |
| 配对 t 检验 | 配对/重复测量 | t = d̄/(s_d/√n) | 差值正态 |
| 卡方检验 | 分类数据频率 | χ² = Σ(O-E)²/E | 期望频率≥5 |
| F 检验 (ANOVA) | 3+组均值比较 | F = MS_between/MS_within | 正态、方差齐性 |

### 效应量（Effect Size）

p 值受样本量影响（n 足够大任何差异都显著），因此必须报告效应量：

```
Cohen's d（均值差异标准化）：
  d = (x̄₁ - x̄₂) / s_pooled
  小: 0.2, 中: 0.5, 大: 0.8 (Cohen, 1988)

Pearson's r（相关强度）：
  r = √(t² / (t² + df))
  小: 0.1, 中: 0.3, 大: 0.5

η²（ANOVA效应量）：
  η² = SS_between / SS_total
  小: 0.01, 中: 0.06, 大: 0.14
```

## 多重比较问题

同时进行 k 次检验时，至少一次犯第一类错误的概率（Familywise Error Rate）：

```
FWER = 1 - (1-α)^k

k=20次检验，α=0.05：
FWER = 1 - 0.95^20 = 0.64 → 64%概率至少一个假阳性！
```

### 校正方法

| 方法 | 公式 | 特点 |
|------|------|------|
| Bonferroni | α' = α/k | 最保守，控制 FWER |
| Holm-Bonferroni | 阶梯式（stepdown） | 比 Bonferroni 更有功效 |
| Benjamini-Hochberg | 控制 FDR（False Discovery Rate） | 适合探索性研究 |
| Tukey HSD | ANOVA 后所有配对比较 | 专用于 ANOVA |

## 贝叶斯替代方案

频率学派检验的根本局限：只能告诉你"数据在H₀下有多不寻常"，不能告诉你"H₀有多可能为真"。

**贝叶斯因子**（Bayes Factor）：

```
BF₁₀ = P(data|H₁) / P(data|H₀)

解读标尺（Jeffreys, 1961）：
BF₁₀ < 1    → 支持 H₀
1-3          → 轶事级证据支持 H₁
3-10         → 中等证据
10-30        → 强证据
30-100       → 非常强证据
> 100        → 决定性证据
```

优势：可以为 H₀ 提供正面证据（"确实无差异"），而 p 值永远无法做到。

## 再现危机的教训

Open Science Collaboration（2015）：100 项心理学研究中仅 **36%** 成功复现。
关键原因分析：
- **p-hacking**：选择性报告达到 p<0.05 的结果
- **HARKing**：结果出来后编造假设（Hypothesizing After Results are Known）
- **发表偏差**：阳性结果更易发表
- **样本量不足**：中位功效仅约 50%（应为 80%+）

**预注册**（Pre-registration）和**注册报告**（Registered Reports）是当前主要的改革措施。

## 参考文献

- Casella, G. & Berger, R.L. (2002). *Statistical Inference*, 2nd ed. Cengage. ISBN 978-0534243128
- Wasserstein, R.L. & Lazar, N.A. (2016). "The ASA Statement on Statistical Significance and p-Values," *The American Statistician*, 70(2), 129-133. [doi: 10.1080/00031305.2016.1154108]
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Erlbaum. ISBN 978-0805802832
- Neyman, J. & Pearson, E.S. (1933). "On the Problem of the Most Efficient Tests of Statistical Hypotheses," *Philosophical Transactions A*, 231, 289-337.

## 教学路径

**前置知识**：描述统计、概率分布基础（正态分布）、抽样分布
**学习建议**：先通过硬币翻转理解"在H₀下数据有多不寻常"的直觉。然后掌握 z/t 检验的手算流程。关键突破点是理解"p值不是H₀为真的概率"——建议做 Bayesian 对比练习。
**进阶方向**：贝叶斯推断、非参数检验、元分析方法、因果推断（Rubin 因果模型）。
