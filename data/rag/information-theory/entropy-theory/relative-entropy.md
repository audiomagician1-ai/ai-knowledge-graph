# 相对熵（KL散度）

## 概述

相对熵（Relative Entropy），又称Kullback-Leibler散度（KL Divergence），由统计学家Solomon Kullback与Richard Leibler于1951年在论文《On Information and Sufficiency》中正式引入（Kullback & Leibler, 1951）。它度量的是：当我们用概率分布 $Q$ 来近似"真实"概率分布 $P$ 时，所额外付出的平均编码代价（以比特或纳特为单位）。与香农熵衡量单一分布的不确定性不同，KL散度是一种**双分布**的不对称度量，描述两个概率分布之间的"信息距离"，但严格来说它并非距离——因为它不满足对称性和三角不等式。

KL散度是现代信息论、统计推断、机器学习与贝叶斯分析的核心工具之一。Cover与Thomas在《Elements of Information Theory》（Cover & Thomas, 2006）中将其定义为互信息、信道容量、数据压缩下界等概念的统一出发点，足见其基础地位。

---

## 核心原理

### 基本定义

设 $P$ 和 $Q$ 是定义在同一可测空间 $\mathcal{X}$ 上的两个概率分布。KL散度定义为：

$$
D_{\mathrm{KL}}(P \| Q) = \sum_{x \in \mathcal{X}} P(x) \log \frac{P(x)}{Q(x)}
$$

对于连续分布，则改写为：

$$
D_{\mathrm{KL}}(P \| Q) = \int_{-\infty}^{+\infty} p(x) \log \frac{p(x)}{q(x)} \, dx
$$

其中，约定 $0 \log \frac{0}{q} = 0$，且当 $q(x) = 0$ 而 $p(x) > 0$ 时，$D_{\mathrm{KL}} = +\infty$。后者意味着：若真实分布 $P$ 在某事件上赋予正概率，而近似分布 $Q$ 却认为该事件不可能发生，则信息损失为无穷大——这一性质在实际模型训练中具有重大警示意义。

对数底数的选择决定单位：底数为2时单位为比特（bit），底数为 $e$ 时单位为纳特（nat），底数为10时单位为哈特（hart）。机器学习领域通常使用纳特（自然对数），信息论教材多使用比特。

### 非负性：吉布斯不等式

KL散度最重要的性质是**非负性**：

$$
D_{\mathrm{KL}}(P \| Q) \geq 0
$$

等号成立当且仅当 $P = Q$（几乎处处相等）。其证明依赖于**Jensen不等式**：由于 $\log$ 是严格凹函数，对任意非负函数有：

$$
-D_{\mathrm{KL}}(P \| Q) = \sum_x P(x) \log \frac{Q(x)}{P(x)} \leq \log \sum_x P(x) \cdot \frac{Q(x)}{P(x)} = \log 1 = 0
$$

这一性质在统计学中称为**吉布斯不等式**（Gibbs Inequality），是热力学第二定律在信息论语境下的对应物：用错误的分布编码信息，平均编码长度只会更长，绝不会更短。具体地，若以分布 $P$ 生成数据，用 $Q$ 设计的最优编码方案，其平均码长为 $H(P) + D_{\mathrm{KL}}(P \| Q)$，其中 $H(P)$ 是 $P$ 的香农熵——额外的 $D_{\mathrm{KL}}$ 比特即为"模型失配代价"。

### 不对称性与信息方向

KL散度的非对称性是其最常被忽视却至关重要的特性：

$$
D_{\mathrm{KL}}(P \| Q) \neq D_{\mathrm{KL}}(Q \| P) \quad \text{（一般情况下）}
$$

**正向KL**（$D_{\mathrm{KL}}(P \| Q)$，称为"包含性"或M-projection）：当 $P(x) > 0$ 处 $Q(x)$ 必须赋予正概率，否则代价无穷；优化时 $Q$ 倾向于覆盖 $P$ 的所有支撑区域，产生"均值搜寻"（mean-seeking）行为。

**反向KL**（$D_{\mathrm{KL}}(Q \| P)$，称为"排他性"或I-projection）：仅在 $Q(x) > 0$ 处有贡献；优化时 $Q$ 倾向于聚焦于 $P$ 的某个众数，产生"模式搜寻"（mode-seeking）行为，即零强迫（zero-forcing）现象。

这一区别在变分推断（Variational Inference）中直接决定了近似后验的形状：最小化 $D_{\mathrm{KL}}(Q \| P)$ 常导致后验低估方差（under-dispersion），而最小化 $D_{\mathrm{KL}}(P \| Q)$ 则过估方差（Jordan et al., 1999）。

---

## 关键公式与模型

### KL散度与互信息的关系

互信息 $I(X; Y)$ 可表达为KL散度的特例：

$$
I(X; Y) = D_{\mathrm{KL}}\!\left(P_{XY} \,\|\, P_X \otimes P_Y\right)
$$

即联合分布 $P_{XY}$ 与两个边缘分布的乘积 $P_X P_Y$ 之间的KL散度。当 $X$ 与 $Y$ 独立时，$I(X;Y)=0$，KL散度为零，完全一致。这一关系将KL散度定位为"相关性"的信息论本质。

### 高斯分布的解析表达式

对于两个单变量高斯分布 $P = \mathcal{N}(\mu_1, \sigma_1^2)$ 与 $Q = \mathcal{N}(\mu_2, \sigma_2^2)$，KL散度有闭合解：

$$
D_{\mathrm{KL}}(P \| Q) = \log \frac{\sigma_2}{\sigma_1} + \frac{\sigma_1^2 + (\mu_1 - \mu_2)^2}{2\sigma_2^2} - \frac{1}{2}
$$

当 $\mu_1 = \mu_2$，$\sigma_1 \neq \sigma_2$ 时，此式退化为纯方差失配代价；当两分布完全相同时结果为零，与非负性定理吻合。这一公式在变分自编码器（VAE）的训练损失中直接出现，是深度生成模型的核心组件（Kingma & Welling, 2013）。

### 链式法则

KL散度满足类似熵的链式法则：

$$
D_{\mathrm{KL}}(P(X, Y) \| Q(X, Y)) = D_{\mathrm{KL}}(P(X) \| Q(X)) + D_{\mathrm{KL}}(P(Y|X) \| Q(Y|X))
$$

其中右侧第二项是对 $P(X)$ 加权平均的条件KL散度。这说明联合分布的KL散度等于边缘分布KL散度加上条件分布KL散度之和，体现了信息的可分解性。

### 信息投影（I-Projection）

在指数族分布的凸集 $\mathcal{E}$ 中，给定目标分布 $P$，求最优近似分布：

$$
Q^* = \arg\min_{Q \in \mathcal{E}} D_{\mathrm{KL}}(P \| Q)
$$

称为 **M-投影**（矩投影），其充要条件是 $Q^*$ 与 $P$ 在充分统计量上具有相同的期望值（Amari, 2016，《Information Geometry and Its Applications》）。这是最大熵原理的信息几何表述，将概率模型的参数估计等价于信息流形上的正交投影。

---

## 实际应用

### 机器学习中的交叉熵损失

在多分类任务中，神经网络的**交叉熵损失**实质上是KL散度的变体。设真实标签的one-hot分布为 $P$，模型输出的softmax概率为 $Q$，则：

$$
\mathcal{L} = D_{\mathrm{KL}}(P \| Q) + H(P) = -\sum_c P(c) \log Q(c)
$$

由于 $H(P)$ 对one-hot分布为零（熵为0），最小化交叉熵等价于最小化KL散度。**例如**，在ImageNet千类分类中，每次前向传播计算的交叉熵损失，本质上都是在量化softmax输出分布与真实标签分布之间的信息失配程度。

### 变分推断与VAE

变分贝叶斯推断（Variational Bayes）将难以计算的后验 $P(\mathbf{z}|\mathbf{x})$ 用参数化分布 $Q_\phi(\mathbf{z}|\mathbf{x})$ 近似，目标是最小化 $D_{\mathrm{KL}}(Q_\phi \| P)$。变分自编码器（VAE）的ELBO（证据下界）为：

$$
\mathcal{L}_{\mathrm{ELBO}} = \mathbb{E}_{Q_\phi}[\log P(\mathbf{x}|\mathbf{z})] - D_{\mathrm{KL}}(Q_\phi(\mathbf{z}|\mathbf{x}) \| P(\mathbf{z}))
$$

其中第二项惩罚近似后验偏离标准正态先验的程度。

### 假设检验与大偏差理论

Sanov定理（Sanov, 1957）指出：独立同分布样本的经验分布落入某集合 $\Gamma$（不含真实分布）的概率，以指数速率 $\exp(-n \cdot D_{\mathrm{KL}}(Q^* \| P))$ 衰减，其中 $Q^*$ 是 $\Gamma$ 中最接近 $P$ 的分布。这直接连接了KL散度与统计假设检验的错误指数（Error Exponent）。

---

## 常见误区

**误区1："KL散度是距离"**——KL散度不满足对称性（$D_{\mathrm{KL}}(P\|Q) \neq D_{\mathrm{KL}}(Q\|P)$），也不满足三角不等式，因此严格来说不是度量（metric）。若需要对称度量，可使用**Jensen-Shannon散度**（JSD）：$\mathrm{JSD}(P\|Q) = \frac{1}{2}D_{\mathrm{KL}}(P\|M) + \frac{1}{2}D_{\mathrm{KL}}(Q\|M)$，其中 $M = \frac{P+Q}{2}$，JSD的平方根满足度量公理。

**误区2："KL散度越小模型越好"**——使用反向KL（$D_{\mathrm{KL}}(Q\|P)$）做变分推断时，优化会导致 $Q$ 忽略 $P$ 的多峰结构，选择性地拟合单个众数（mode collapse），这在生成模型中是严重问题，而非优化成功的标志。

**误区3："P和Q可以随意互换"**——在监督学习中，将真实分布置于第一位（$D_{\mathrm{KL}}(P\|Q)$）与将模型置于第一位（$D_{\mathrm{KL}}(Q\|P)$）具有本质区别。前者要求模型对真实数据的每个支撑点都赋予正概率（零避免），后者允许模型忽略部分支撑点（零强迫）。混淆两者会导致算法行为的根本性误判。

**误区4："KL散度只适用于离散分布"**——连续情形的KL散度同样定义良好，只需用概率密度函数替换概率质量函数，前提是 $P$ 关于 $Q$ 绝对连续（即 $P \ll Q$）。

---

## 知识关联

**前置概念**：互信息（$I(X;Y) = D_{\mathrm{KL}}(P_{XY}\|P_X P_Y)$）是KL散度的特殊情形；香农熵 $H(P) = -D_{\mathrm{KL}}(P\|\mathcal{U})$ 可视为 $P$ 与均匀分布之间KL散度的相反数（相差常数 $\log|\mathcal{X}|$）。

**后继概念**：KL散度通向**信息几何**（Amari, 1985），其中 $\alpha$-散度族统一了KL散度（$\alpha=\pm 1$）与欧几里得距离（$\alpha=0$）；通向**最大熵原理**（Jaynes, 1957），后者可重