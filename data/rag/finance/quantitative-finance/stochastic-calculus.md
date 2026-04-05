---
id: "stochastic-calculus"
concept: "随机微积分"
domain: "finance"
subdomain: "quantitative-finance"
subdomain_name: "量化金融"
difficulty: 4
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Stochastic calculus"
    url: "https://en.wikipedia.org/wiki/Stochastic_calculus"
  - type: "encyclopedia"
    ref: "Wikipedia - Ito calculus"
    url: "https://en.wikipedia.org/wiki/It%C3%B4_calculus"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 随机微积分

## 概述

随机微积分（Stochastic Calculus）是处理含有随机噪声项的微分方程的数学框架，其核心对象是布朗运动（Brownian Motion，又称维纳过程）和以此为基础构建的随机积分。与经典牛顿-莱布尼茨微积分不同，随机微积分必须应对一个根本性的障碍：布朗运动路径处处连续但处处不可微，导致经典链式法则完全失效。

该领域由日本数学家伊藤清（Itô Kiyosi）在1944年奠定基础。他在论文《On a Stochastic Integral Equation》中定义了随机积分，并于1951年推导出以他名字命名的伊藤引理（Itô's Lemma）。这一工作在金融领域沉寂了约30年，直到1973年布莱克、肖尔斯和默顿将其用于推导期权定价公式，随机微积分才成为量化金融不可或缺的工具语言。

在量化金融中，随机微积分的意义在于它提供了对资产价格不确定性进行严格数学描述的手段。股票价格的连续时间运动、利率的随机波动、波动率的均值回归行为，均需要用随机微分方程（SDE）而非普通ODE来建模。没有随机微积分，Black-Scholes公式的推导在数学上是不严格的。

---

## 核心原理

### 布朗运动与二次变差

标准布朗运动 $W_t$ 满足四个条件：$W_0 = 0$，增量 $W_t - W_s$（$t > s$）服从 $\mathcal{N}(0, t-s)$，不重叠时间段的增量相互独立，以及路径关于时间连续。

布朗运动最反直觉的性质是其**二次变差**（Quadratic Variation）非零且等于时间本身：

$$[W, W]_t = t$$

这用符号写作 $(dW_t)^2 = dt$。相比之下，普通可微函数的二次变差恒为零。正是这条规则（以及 $dt \cdot dW_t = 0$，$(dt)^2 = 0$）构成了伊藤微积分区别于经典微积分的运算基础。

### 伊藤引理

设 $X_t$ 满足随机微分方程 $dX_t = \mu_t \, dt + \sigma_t \, dW_t$，$f(t, x)$ 是关于 $t$ 和 $x$ 的二阶连续可微函数，则：

$$df(t, X_t) = \frac{\partial f}{\partial t} dt + \frac{\partial f}{\partial x} dX_t + \frac{1}{2} \frac{\partial^2 f}{\partial x^2} (dX_t)^2$$

代入 $(dX_t)^2 = \sigma_t^2 \, dt$ 后展开为：

$$df = \left(\frac{\partial f}{\partial t} + \mu_t \frac{\partial f}{\partial x} + \frac{1}{2}\sigma_t^2 \frac{\partial^2 f}{\partial x^2}\right) dt + \sigma_t \frac{\partial f}{\partial x} dW_t$$

与经典链式法则相比，多出了 $\frac{1}{2}\sigma_t^2 \frac{\partial^2 f}{\partial x^2}$ 这一**伊藤修正项**。该项来源于布朗运动非零的二次变差，在 $\sigma_t = 0$ 时自动退化为经典结果。

### 几何布朗运动（GBM）与对数正态分布

Black-Scholes模型假设股价 $S_t$ 服从**几何布朗运动**，其SDE为：

$$dS_t = \mu S_t \, dt + \sigma S_t \, dW_t$$

对 $f(t, S_t) = \ln S_t$ 应用伊藤引理，得到：

$$d(\ln S_t) = \left(\mu - \frac{\sigma^2}{2}\right) dt + \sigma \, dW_t$$

积分后得到精确解：

$$S_t = S_0 \exp\left[\left(\mu - \frac{\sigma^2}{2}\right)t + \sigma W_t\right]$$

这说明 $\ln S_t$ 服从正态分布，漂移项为 $\mu - \frac{\sigma^2}{2}$ 而非 $\mu$。两者之差 $\frac{\sigma^2}{2}$ 正是伊藤修正项的直接后果，对于 $\sigma = 0.2$（年化20%波动率），该修正量为每年 $0.02$，在长期定价中不可忽略。

### 随机微分方程的数值解法与蒙特卡洛

当SDE无解析解（如Heston随机波动率模型）时，需要数值离散化方法。**欧拉-丸山格式**（Euler-Maruyama）是最基础的离散化：

$$X_{t+\Delta t} \approx X_t + \mu(t, X_t)\Delta t + \sigma(t, X_t)\sqrt{\Delta t}\, Z_t, \quad Z_t \sim \mathcal{N}(0,1)$$

该格式对GBM的强收敛阶为 $\frac{1}{2}$，即误差与 $\sqrt{\Delta t}$ 成比例。更高精度的**米尔斯坦格式**（Milstein）通过加入二阶伊藤修正项将强收敛阶提升至 $1$，代价是需要计算扩散系数对状态变量的偏导数。在蒙特卡洛模拟中，每一条路径本质上是对SDE的一次数值求解，因此数值格式的选取直接影响模拟结果的偏差与收敛速度。

---

## 实际应用

**期权定价中的测度变换**：Black-Scholes定价公式的推导利用了吉尔萨诺夫定理（Girsanov's Theorem），将真实概率测度 $\mathbb{P}$ 下含风险溢价的漂移项，变换为风险中性测度 $\mathbb{Q}$ 下以无风险利率 $r$ 为漂移的过程。操作方式是将布朗运动重新定义为 $\tilde{W}_t = W_t + \frac{\mu - r}{\sigma} t$，新漂移项 $\frac{\mu - r}{\sigma}$ 称为夏普比率或市场风险价格。

**利率模型**：Vasicek模型用SDE描述短期利率的均值回归行为：$dr_t = \kappa(\theta - r_t)dt + \sigma dW_t$，其中 $\kappa$ 为回归速度，$\theta$ 为长期均值水平。利用伊藤引理可以求得该SDE的解析解，并进一步推导出债券价格的封闭形式。

**随机波动率模型**：Heston模型在GBM基础上引入波动率的独立SDE，波动率 $v_t$ 满足：$dv_t = \kappa(\bar{v} - v_t)dt + \xi\sqrt{v_t}\, dW_t^v$，其中 $W_t^v$ 与股价布朗运动相关系数为 $\rho$（通常为负值，体现杠杆效应）。该二维SDE系统需要用特征函数法或数值PDE方法求解，无法直接用一维伊藤引理处理。

---

## 常见误区

**误区一：将 $dW_t$ 当作普通微分处理**。部分初学者直接套用经典链式法则计算 $d(W_t^2)$，得到 $2W_t \, dW_t$，漏掉了伊藤修正项 $dt$。正确结果是 $d(W_t^2) = 2W_t \, dW_t + dt$，对应于 $W_t^2 - t$ 是鞅（martingale）这一重要性质。

**误区二：混淆伊藤积分与斯特拉托诺维奇积分**。斯特拉托诺维奇积分（Stratonovich Integral，记作 $\int f \circ dW$）与伊藤积分的差别在于前者满足经典链式法则，但代价是不再具有鞅性质。在物理随机过程中斯特拉托诺维奇更常用，但金融衍生品定价依赖鞅理论，因此必须使用伊藤约定，否则无风险中性定价框架将失效。

**误区三：认为漂移项 $\mu$ 决定期权价格**。由于测度变换，在风险中性测度下期权价格与真实世界漂移 $\mu$ 完全无关，仅依赖无风险利率 $r$ 和波动率 $\sigma$。许多初学者在应用Black-Scholes公式时仍然代入历史收益率 $\mu$，这是对伊藤公式与测度变换关系的根本性误解。

---

## 知识关联

随机微积分与**Black-Scholes模型**的关系是推导与结果的关系：Black-Scholes偏微分方程 $\frac{\partial V}{\partial t} + \frac{1}{2}\sigma^2 S^2 \frac{\partial^2 V}{\partial S^2} + rS\frac{\partial V}{\partial S} - rV = 0$ 正是对含GBM的期权价值应用伊藤引理、再通过Delta对冲消去随机项后所得。方程中的 $\frac{1}{2}\sigma^2 S^2$ 项直接对应伊藤修正项，缺少随机微积分基础时该方程的来源无从理解。

与**蒙特卡洛模拟**的关联在于：蒙特卡洛路径模拟的