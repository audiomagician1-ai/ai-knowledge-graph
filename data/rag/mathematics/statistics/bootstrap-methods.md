---
id: "bootstrap-methods"
concept: "Bootstrap方法"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "数理统计"
difficulty: 7
is_milestone: false
tags: ["现代"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Bootstrap方法

## 概述

Bootstrap方法（自助法）是由统计学家Bradley Efron于1979年在论文《Bootstrap Methods: Another Look at the Jackknife》中正式提出的重抽样技术。其核心思想是：当总体分布未知时，用样本的经验分布函数（EDF）来近似总体分布，然后通过从原始样本中**有放回地**重复抽样，生成大量"Bootstrap样本"，从而估计统计量的抽样分布。

Bootstrap方法彻底改变了统计推断的实践方式。在此之前，构造置信区间通常需要依赖正态性假设或推导出统计量的精确抽样分布，对于相关系数、中位数、方差比等复杂统计量，理论推导往往极其困难甚至无解。Bootstrap方法通过计算力替代了数学解析能力，使任意统计量的置信区间构造都变得可行。以样本中位数为例，其抽样分布没有简洁的封闭形式，但Bootstrap可以轻松给出置信区间。

该方法的名称来源于短语"to pull oneself up by one's bootstraps"（靠自身努力），隐喻用样本数据本身来生成推断所需信息，无需依赖外部的分布假设。

## 核心原理

### 经验分布函数与Bootstrap世界

设原始样本为 $\mathbf{x} = (x_1, x_2, \ldots, x_n)$，其经验分布函数将概率质量 $\frac{1}{n}$ 均匀赋予每个观测值。Bootstrap的逻辑分为两层类比：

- **真实世界**：总体 $F$ → 样本 $\mathbf{x}$ → 统计量 $\hat{\theta} = s(\mathbf{x})$
- **Bootstrap世界**：经验分布 $\hat{F}$ → Bootstrap样本 $\mathbf{x}^*$ → Bootstrap统计量 $\hat{\theta}^* = s(\mathbf{x}^*)$

用Bootstrap世界中 $\hat{\theta}^*$ 相对于 $\hat{\theta}$ 的波动，来近似真实世界中 $\hat{\theta}$ 相对于 $\theta$ 的波动。这一替换的合理性依赖于 $\hat{F}$ 依概率收敛到真实 $F$（Glivenko-Cantelli定理保证）。

### Bootstrap标准误差的计算

设执行 $B$ 次有放回重抽样（每次抽取 $n$ 个观测值），得到Bootstrap统计量 $\hat{\theta}^{*1}, \hat{\theta}^{*2}, \ldots, \hat{\theta}^{*B}$，Bootstrap标准误差估计为：

$$\widehat{se}_{B} = \sqrt{\frac{1}{B-1}\sum_{b=1}^{B}\left(\hat{\theta}^{*b} - \bar{\theta}^*\right)^2}$$

其中 $\bar{\theta}^* = \frac{1}{B}\sum_{b=1}^{B}\hat{\theta}^{*b}$。

实践中 $B = 1000$ 通常足以估计标准误差，而构造置信区间则建议 $B \geq 2000$，高精度场合（如双侧 $\alpha = 0.01$）需要 $B \geq 10000$。

### 四种Bootstrap置信区间的构造方法

**方法一：正态近似区间**
假设 $\hat{\theta}$ 近似正态分布：
$$\left[\hat{\theta} - z_{\alpha/2}\cdot\widehat{se}_B,\quad \hat{\theta} + z_{\alpha/2}\cdot\widehat{se}_B\right]$$
该方法计算简单，但依赖正态假设，对偏态统计量效果差。

**方法二：百分位区间（Percentile Interval）**
直接取Bootstrap分布的 $\alpha/2$ 和 $1-\alpha/2$ 分位数：
$$\left[\hat{\theta}^*_{(\alpha/2)},\quad \hat{\theta}^*_{(1-\alpha/2)}\right]$$
例如95%置信区间取Bootstrap分布的第2.5和第97.5百分位数。该方法直觉简单，但在偏态情形下覆盖率不准确。

**方法三：基本Bootstrap区间（Basic/Pivotal）**
利用 $\hat{\theta} - \theta$ 的Bootstrap分布来反推：
$$\left[2\hat{\theta} - \hat{\theta}^*_{(1-\alpha/2)},\quad 2\hat{\theta} - \hat{\theta}^*_{(\alpha/2)}\right]$$
注意与百分位区间相比，端点顺序相反，体现了"翻转"（reflection）的思想。

**方法四：BCa区间（Bias-Corrected and Accelerated）**
BCa方法由Efron（1987）提出，对偏差和加速度同时校正，是理论性质最好的Bootstrap置信区间，具有二阶精确性（second-order accuracy）。其分位点为：

$$\alpha_1 = \Phi\left(\hat{z}_0 + \frac{\hat{z}_0 + z_{\alpha/2}}{1 - \hat{a}(\hat{z}_0 + z_{\alpha/2})}\right)$$

其中 $\hat{z}_0$ 是偏差校正常数，$\hat{a}$ 是加速度常数（通过刀切法估计）。BCa区间在统计软件（如R的`boot`包）中已内置实现。

## 实际应用

**应用一：相关系数的置信区间**
对于Pearson相关系数 $r$，Fisher Z变换 $\frac{1}{2}\ln\frac{1+r}{1-r}$ 近似正态，但对于Spearman等秩相关系数，Bootstrap是更稳健的选择。取 $n=50$ 的双变量数据，Bootstrap $B=2000$ 次即可获得可靠的95% BCa置信区间。

**应用二：回归系数的Bootstrap推断**
在线性回归中，当误差项非正态时，OLS估计的t检验不可靠。Bootstrap可分为两种策略：对残差重抽样（Residual Bootstrap）或对观测对 $(x_i, y_i)$ 整行重抽样（Pairs Bootstrap）。前者假设误差同分布，后者对设计矩阵也作了随机化，更适用于异方差场景。

**应用三：机器学习中的Bagging**
随机森林中的Bagging（Bootstrap Aggregating）直接使用Bootstrap思想：每棵决策树在一个Bootstrap样本（约含原始数据63.2%的不重复观测）上训练，剩余36.8%作为袋外样本（Out-of-Bag, OOB）用于误差估计。这一63.2%来自极限 $1-(1-\frac{1}{n})^n \to 1-e^{-1} \approx 0.632$。

## 常见误区

**误区一：Bootstrap样本量不等于原始样本量**
有些初学者认为Bootstrap重抽样时可以抽取比 $n$ 更多的样本来"增加信息"。这是错误的。Bootstrap样本必须与原始样本大小相同（均为 $n$），否则估计的方差结构将发生改变，近似不再有效。抽取更多样本不会增加原始数据所含的信息量。

**误区二：Bootstrap可以修正小样本偏差**
Bootstrap的理论保证建立在 $\hat{F}$ 是 $F$ 的良好近似基础上，而这需要足够大的 $n$。当 $n < 10$ 时，经验分布函数对真实分布的近似很粗糙，Bootstrap置信区间覆盖率可能严重偏离名义水平。Bootstrap并不是解决小样本问题的万能工具。

**误区三：百分位区间与基本Bootstrap区间的混淆**
两者在计算上仅差一个"翻转"操作，但含义不同。百分位区间直接使用 $\hat{\theta}^*$ 的分位数，隐含了一个变换等变性假设；基本区间使用 $\hat{\theta}^* - \hat{\theta}$ 的枢轴量思想。当统计量接近参数空间边界（如方差接近0）时，两者结果可能相差悬殊，此时应优先选用BCa区间。

## 知识关联

Bootstrap方法以**抽样分布**为直接前驱概念：理解抽样分布（即统计量在重复抽样下的概率行为）是理解Bootstrap模拟目标的基础。Bootstrap的精髓是用计算机模拟的方式估计那些无法解析求得的抽样分布。

Bootstrap与刀切法（Jackknife，由Quenouille于1949年提出）同属重抽样方法家族，后者通过依次删除一个观测值（Leave-one-out）来估计偏差和标准误差，可看作Bootstrap在计算资源匮乏时代的先驱。在参数假设检验中，Bootstrap也可用于置换检验（Permutation Test），但两者的抽样机制不同：Bootstrap有放回，置换无放回。

在贝叶斯框架下，Bootstrap近似于使用Dirichlet(1,…,1)先验的贝叶斯后验预测分布，这一联系由Rubin（1981）的贝叶斯Bootstrap揭示，是理解Bootstrap统计基础的更深层视角。
