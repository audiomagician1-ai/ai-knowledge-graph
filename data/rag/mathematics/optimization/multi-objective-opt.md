---
id: "multi-objective-opt"
concept: "多目标优化"
domain: "mathematics"
subdomain: "optimization"
subdomain_name: "最优化"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 多目标优化

## 概述

多目标优化（Multi-Objective Optimization）是指在满足约束条件的前提下，同时优化两个或两个以上相互冲突的目标函数的数学问题。其标准形式为：

$$\min \mathbf{f}(\mathbf{x}) = [f_1(\mathbf{x}), f_2(\mathbf{x}), \ldots, f_k(\mathbf{x})]^T, \quad \text{s.t. } \mathbf{x} \in \Omega$$

其中 $k \geq 2$ 为目标函数个数，$\mathbf{x}$ 为决策变量向量，$\Omega$ 为可行域。与单目标优化不同，多目标优化不存在唯一"最优解"，而是产生一组**折中解集**。

多目标优化的理论框架由意大利经济学家维尔弗雷多·帕累托（Vilfredo Pareto）于1896年在研究经济资源分配时奠定。帕累托首次指出，当优化多个相互竞争的目标时，改进某一目标必然导致至少另一个目标的恶化，这种不可避免的权衡关系是多目标问题的本质特征。20世纪60年代，Charnes与Cooper将此思想系统化为运筹学方法。

多目标优化在工程设计领域具有不可替代的作用：飞机结构设计需要同时最小化重量和最大化强度，这两个目标本质冲突；投资组合管理需要同时最大化收益与最小化风险。理解如何处理这种冲突性，是多目标优化区别于带多个约束的单目标优化的根本所在。

## 核心原理

### Pareto支配关系与Pareto前沿

**Pareto支配**是多目标优化中最基础的偏序关系。对于最小化问题，称解 $\mathbf{x}^{(1)}$ **支配** $\mathbf{x}^{(2)}$（记作 $\mathbf{x}^{(1)} \prec \mathbf{x}^{(2)}$），当且仅当：

$$\forall i \in \{1,\ldots,k\}: f_i(\mathbf{x}^{(1)}) \leq f_i(\mathbf{x}^{(2)}), \quad \exists j: f_j(\mathbf{x}^{(1)}) < f_j(\mathbf{x}^{(2)})$$

即 $\mathbf{x}^{(1)}$ 在所有目标上不劣于 $\mathbf{x}^{(2)}$，且至少在一个目标上严格优于它。不被任何可行解支配的解称为**Pareto最优解**，全体Pareto最优解构成的集合称为**Pareto最优集**，其在目标函数空间中的映像称为**Pareto前沿**（Pareto Front）。对于两目标凸优化问题，Pareto前沿通常是一条连续曲线；当目标数 $k \geq 3$ 时，Pareto前沿是一个超曲面。

### 权重法（加权和法）

权重法将多目标问题转化为单目标问题：

$$\min_{\mathbf{x} \in \Omega} \sum_{i=1}^{k} w_i f_i(\mathbf{x}), \quad w_i \geq 0, \quad \sum_{i=1}^{k} w_i = 1$$

通过系统地改变权重向量 $\mathbf{w} = (w_1, w_2, \ldots, w_k)$，可以扫描出不同的Pareto最优解。权重法的一个关键定理保证：若权重 $w_i > 0$（$\forall i$）且优化问题为凸优化，则加权和法得到的最优解必然是Pareto最优解。

然而，权重法存在一个严重局限：**对于非凸Pareto前沿，某些Pareto最优解无论如何设置正权重都无法被发现**（即凹陷区域的点）。实践中各目标量纲差异悬殊时，需先对 $f_i$ 进行归一化处理，否则权重的实际经济意义会扭曲。

### ε-约束法

ε-约束法（ε-Constraint Method）保留一个主目标 $f_p(\mathbf{x})$ 进行最小化，将其余 $k-1$ 个目标转化为约束：

$$\min_{\mathbf{x} \in \Omega} f_p(\mathbf{x}), \quad \text{s.t. } f_i(\mathbf{x}) \leq \varepsilon_i, \quad i \in \{1,\ldots,k\} \setminus \{p\}$$

通过系统地变化参数向量 $(\varepsilon_1, \ldots, \varepsilon_{k-1})$，可以得到Pareto前沿上的一系列点。与权重法相比，ε-约束法的核心优势在于：**即使对非凸问题，只要 $\varepsilon_i$ 取值合适，也能找到Pareto前沿凹陷区域中的解**。选择主目标时，通常选择最容易求解或最重要的目标函数。实操中，$\varepsilon_i$ 的范围应从第 $i$ 个目标的理想值（单独最小化时的值）到最差值均匀取样。

### 理想点与Nadir点

多目标优化中有两个特殊参考点：**理想点**（Ideal Point）$\mathbf{z}^* = (z_1^*, \ldots, z_k^*)$，其中 $z_i^* = \min_{\mathbf{x} \in \Omega} f_i(\mathbf{x})$ 是各目标独立最优值；**Nadir点** $\mathbf{z}^{nad}$ 是Pareto前沿上各目标的最大值组成的向量。理想点通常不可达（因为各目标相互冲突），Nadir点则代表Pareto意义下的"最差情形"。这两点共同定义了Pareto前沿在目标空间中的边界框，是ε-约束法设置参数范围和比较不同方法性能的标准参照。

## 实际应用

**工程结构优化**：在桁架设计中，目标1为最小化结构总质量，目标2为最小化最大节点位移。设计变量为各杆件截面积，约束为应力不超过材料屈服强度。使用ε-约束法，固定最大位移上限 $\varepsilon$，对质量最小化，逐步收紧 $\varepsilon$ 从而描绘出质量-刚度的Pareto前沿，供工程师在轻量化与刚性之间做出决策。

**机器学习超参数调优**：在神经网络训练中，同时优化验证集准确率（最大化）与模型参数量（最小化）。这是一个两目标问题，Pareto前沿描述了精度与模型复杂度之间的折中曲线。Google的NAS（神经架构搜索）工具中即使用了多目标优化框架NSGA-II（非支配排序遗传算法），该算法于1994年由Deb等人提出，是目前最广泛使用的多目标进化算法之一。

**供应链管理**：同时最小化运输成本 $f_1$ 与最大化服务水平 $f_2 = -\min_j(\text{满足率}_j)$，约束为仓库容量与车辆数量上限。权重法此时可为决策者提供直观的费用-服务权衡曲线。

## 常见误区

**误区一：将多约束单目标问题等同于多目标优化**。一个含20个约束的单目标问题仍然是单目标优化，因为只有一个需要优化的目标函数；多目标优化的特征是存在多个**需要同时最优化**的目标函数，它们之间存在不可消除的冲突关系，不能通过数学等价变换合并为一个目标。

**误区二：认为权重法可以遍历所有Pareto最优解**。对于凸问题，权重法确实可以通过 $w_1$ 从0到1均匀采样来覆盖整个Pareto前沿；但对于非凸Pareto前沿（如两个凸子集之间有间隙），凹陷区间内的Pareto最优解无论如何选取正权重都不会被权重法找到，此时必须使用ε-约束法或进化算法。

**误区三：Pareto最优解就是"最好的解"**。Pareto最优集通常包含无穷多个解（连续情形），其中没有哪一个在数学意义上优于其他Pareto最优解。从Pareto集中选出最终方案，需要决策者额外引入偏好信息（如权重、满意度函数或交互式决策），这一步称为**后验决策**（Post-optimality Decision），是多目标优化流程中不可缺少但属于决策科学范畴的环节。

## 知识关联

多目标优化直接建立在约束优化的KKT（Karush-Kuhn-Tucker）条件之上：Pareto最优的必要条件可以用广义KKT条件表达，即在Pareto最优点处，目标函数梯度的任意正线性组合不能指向可行下降方向。具体而言，$\mathbf{x}^*$ 为Pareto最优的必要条件是存在 $\mathbf{w} \geq \mathbf{0}$（$\mathbf{w} \neq \mathbf{0}$）使得 $\sum_i w_i \nabla f_i(\mathbf{x}^*) + \text{约束梯度项} = \mathbf{0}$，这正是将约束优化KKT条件推广到向量