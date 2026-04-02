---
id: "conditional-expectation"
concept: "条件期望"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 7
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.393
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 条件期望

## 概述

条件期望（Conditional Expectation）是在已知某一事件发生或某一随机变量取特定值的前提下，另一随机变量的平均取值。与普通期望 $E[X]$ 给出 $X$ 的无条件均值不同，条件期望 $E[X \mid Y=y]$ 利用了 $Y$ 的信息来"更新"对 $X$ 均值的估计，体现了概率论中信息与不确定性之间的核心张力。

条件期望的严格数学框架由柯尔莫哥洛夫（Kolmogorov）于1933年在其测度论概率公理体系中建立。在此之前，条件期望的概念已被统计学家和物理学家直觉性地使用，但缺乏处理连续随机变量时的严格基础——因为当 $P(Y=y)=0$ 时，直接用条件概率公式 $P(A \mid B) = P(A \cap B)/P(B)$ 已无意义，需要借助 Radon-Nikodym 导数来定义。

条件期望在现代概率论和统计学中不可或缺：贝叶斯推断的后验均值即为条件期望；马尔可夫链的转移特性通过条件期望描述；随机过程中的鞅（martingale）定义正是 $E[X_{n+1} \mid \mathcal{F}_n] = X_n$。掌握条件期望是理解这些高阶主题的前提。

---

## 核心原理

### 离散情形的定义

设 $X, Y$ 均为离散随机变量，$Y$ 的可能取值为 $y_1, y_2, \ldots$，且 $P(Y=y_j) > 0$，则 $X$ 关于事件 $\{Y=y_j\}$ 的条件期望定义为：

$$E[X \mid Y = y_j] = \sum_i x_i \cdot P(X = x_i \mid Y = y_j)$$

其中条件概率 $P(X=x_i \mid Y=y_j) = \dfrac{P(X=x_i,\, Y=y_j)}{P(Y=y_j)}$。

注意此时 $E[X \mid Y=y_j]$ 是一个**数**，而 $E[X \mid Y]$ 是将 $y_j$ 替换为随机变量 $Y$ 后得到的**随机变量**——这一区分是条件期望最常被忽视的细节。

### 连续情形的定义

设 $(X, Y)$ 有联合密度 $f_{X,Y}(x,y)$，$Y$ 的边缘密度为 $f_Y(y)$，则在 $f_Y(y)>0$ 处：

$$E[X \mid Y = y] = \int_{-\infty}^{+\infty} x \cdot \frac{f_{X,Y}(x,y)}{f_Y(y)}\, dx = \int_{-\infty}^{+\infty} x \cdot f_{X\mid Y}(x \mid y)\, dx$$

此式的本质是用条件密度 $f_{X\mid Y}(x \mid y)$ 代替普通密度来计算期望，与离散情形在结构上完全一致。

### 全期望公式（Law of Total Expectation）

全期望公式（又称迭代期望公式）是条件期望最重要的计算工具：

$$E[X] = E\bigl[E[X \mid Y]\bigr]$$

离散版本展开为：

$$E[X] = \sum_j E[X \mid Y = y_j] \cdot P(Y = y_j)$$

连续版本为：

$$E[X] = \int_{-\infty}^{+\infty} E[X \mid Y=y] \cdot f_Y(y)\, dy$$

**证明思路（离散）**：将右侧展开，$\sum_j \left(\sum_i x_i P(X=x_i \mid Y=y_j)\right) P(Y=y_j) = \sum_j \sum_i x_i P(X=x_i, Y=y_j)$，交换求和顺序后等于 $\sum_i x_i P(X=x_i) = E[X]$，严格成立。

全期望公式的使用策略是：选择一个能将复杂问题**分层**的条件变量 $Y$，在每个 $Y=y_j$ 的层内计算 $E[X \mid Y=y_j]$，最后按 $Y$ 的分布加权平均。

### 条件期望的基本性质

以下性质对理解和计算至关重要：

- **线性**：$E[aX+bZ \mid Y] = aE[X \mid Y] + bE[Z \mid Y]$
- **已知量提取**：若 $g(Y)$ 是 $Y$ 的函数，则 $E[g(Y) \cdot X \mid Y] = g(Y) \cdot E[X \mid Y]$
- **独立性退化**：若 $X \perp Y$，则 $E[X \mid Y] = E[X]$（条件不提供额外信息）
- **塔性质**（Tower Property）：$E\bigl[E[X \mid Y, Z] \mid Y\bigr] = E[X \mid Y]$，即在粗信息下的期望等于在精细信息下期望的粗化

---

## 实际应用

**例1：复合分布的期望计算**  
设某保险公司一天的理赔次数 $N \sim \text{Poisson}(\lambda)$，每次理赔金额 $X_i$ 独立同分布，均值为 $\mu$。一天总赔付 $S = X_1 + X_2 + \cdots + X_N$（$N=0$ 时 $S=0$）。直接计算 $E[S]$ 较繁，但条件期望给出：

$$E[S \mid N=n] = E[X_1 + \cdots + X_n] = n\mu$$

故 $E[S \mid N] = N\mu$，由全期望公式：

$$E[S] = E[N\mu] = \mu \cdot E[N] = \mu\lambda$$

这一结论对任意 $N$ 分布均成立，只要 $E[N] = \lambda$。

**例2：几何分布均值的递推推导**  
设 $X$ 为首次成功所需试验次数，每次成功概率为 $p$。令 $m = E[X]$，对第一次试验结果取条件：

$$E[X] = E[X \mid \text{第1次成功}] \cdot p + E[X \mid \text{第1次失败}] \cdot (1-p)$$
$$= 1 \cdot p + (1 + m)(1-p)$$

解得 $m = 1/p$，与直接求和公式结果一致，但推导更为简洁。

---

## 常见误区

**误区1：混淆 $E[X \mid Y=y]$（数）与 $E[X \mid Y]$（随机变量）**  
$E[X \mid Y=y]$ 在 $y$ 固定时是一个实数，例如 $E[X \mid Y=3] = 7$；而 $E[X \mid Y]$ 是将 $y$ 替换为随机变量 $Y$ 后的函数 $g(Y)$，本身具有随机性，可以求其期望和方差。学生常在推导中不加区分地交替使用这两种记号，导致逻辑混乱。

**误区2：认为条件期望总是"更精确"**  
给定 $Y$ 后，$E[X \mid Y]$ 作为 $X$ 的估计量其均方误差 $E[(X - E[X \mid Y])^2]$ 确实不大于 $E[(X - E[X])^2]$（即无条件方差），这是投影的正交性保证的。但这并非"精确"，而是方差意义下最优。当 $X$ 与 $Y$ 独立时，$E[X \mid Y] = E[X]$，条件信息完全无益——条件期望的改进幅度取决于 $X$ 与 $Y$ 的相关程度。

**误区3：全期望公式中忘记对 $Y$ 的分布加权**  
学生有时将 $E[X]$ 误写为各层条件期望的简单平均 $\frac{1}{k}\sum_{j=1}^k E[X \mid Y=y_j]$，而非加权平均 $\sum_j E[X \mid Y=y_j] P(Y=y_j)$。当 $Y$ 的各取值概率不相等时（绝大多数实际情况），这一错误会导致显著偏差。

---

## 知识关联

**依赖的前置概念**：条件期望直接建立在**条件概率**的基础上——离散情形的条件期望公式中每一项的权重正是条件概率 $P(X=x_i \mid Y=y_j)$；连续情形则使用条件密度，后者由联合密度除以边缘密度得到，这与条件概率的 $P(A \mid B) = P(A \cap B)/P(B)$ 结构完全类比。对**期望与方差**的计算熟练度也必不可少，因为条件期望本质上是在条件分布下求期望，计算步骤与普通期望相同。

**向后延伸的方向**：条件期望是定义**鞅**（martingale）的直接工具——若随机序列满足 $E[X_{n+1} \mid X_1, \ldots, X_n] = X_n$，则称之为鞅，这在金融数学（期权定价的风险中性定价）和赌博理论中有根本性应用。全期望公式也是贝叶斯网络中变量消除算法的数学基础，条件期望的塔性质则对应图模型中的边际化操作。