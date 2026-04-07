---
id: "differential-equations-intro"
concept: "常微分方程初步"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 7
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 常微分方程初步

## 概述

常微分方程（Ordinary Differential Equation，简称 ODE）是含有未知函数及其导数的方程，其中未知函数仅依赖**一个**自变量。最简单的形式如 $\frac{dy}{dx} = f(x, y)$，其中 $y$ 是关于 $x$ 的未知函数。与代数方程求未知数不同，ODE 的解是一个函数或一族函数，称为**通解**；加上初始条件 $y(x_0) = y_0$ 后确定的唯一解称为**特解**。

常微分方程的系统研究始于17世纪末。莱布尼茨（Leibniz）于1693年首次给出了一阶线性ODE的求解方法，伯努利（Jakob Bernoulli）随后研究了以其命名的伯努利方程。牛顿在力学问题中大量使用ODE描述运动规律，这也是ODE理论发展的最初驱动力。

一阶ODE在工程与自然科学中直接建模大量现象：RC电路的充放电过程、种群的指数增长与逻辑斯谛增长、放射性衰变等，其数学结构均归结为一阶ODE。掌握可分离变量法与一阶线性ODE的求解，是进入二阶ODE和偏微分方程领域的必要前提。

---

## 核心原理

### 可分离变量方程

若一阶ODE可以写成以下形式：

$$\frac{dy}{dx} = g(x) \cdot h(y)$$

则称其为**可分离变量方程**。求解步骤是将含 $y$ 的因子移到左边，含 $x$ 的因子保留右边，再两端积分：

$$\frac{dy}{h(y)} = g(x)\, dx \quad \Rightarrow \quad \int \frac{1}{h(y)}\, dy = \int g(x)\, dx$$

例如，方程 $\frac{dy}{dx} = ky$（$k$ 为常数）描述指数增长/衰减。分离变量后得 $\frac{dy}{y} = k\, dx$，两端积分得 $\ln|y| = kx + C_1$，即通解为 $y = Ce^{kx}$（$C$ 为任意常数）。若已知 $y(0) = y_0$，则特解为 $y = y_0 e^{kx}$。放射性衰变中 $k < 0$，半衰期公式 $T_{1/2} = \frac{\ln 2}{|k|}$ 直接由此推出。

注意：当 $h(y) = 0$ 时，$y = \text{const}$ 本身也可能是方程的解，称为**奇解**或**平衡解**，不能被通解的参数化形式覆盖，必须单独验证。

### 一阶线性常微分方程

一阶线性ODE的标准形式为：

$$\frac{dy}{dx} + P(x)\, y = Q(x)$$

其中 $P(x)$ 和 $Q(x)$ 均为 $x$ 的已知函数。当 $Q(x) \equiv 0$ 时称为**齐次**线性方程，可直接用分离变量法求解；当 $Q(x) \not\equiv 0$ 时称为**非齐次**。

求解非齐次方程的标准工具是**积分因子法**（由莱布尼茨提出）。定义积分因子：

$$\mu(x) = e^{\int P(x)\, dx}$$

将方程两端乘以 $\mu(x)$，左端恰好凑成乘积导数的形式：

$$\frac{d}{dx}\left[\mu(x) \cdot y\right] = \mu(x) \cdot Q(x)$$

两端对 $x$ 积分，即得通解：

$$y = \frac{1}{\mu(x)}\left[\int \mu(x)\, Q(x)\, dx + C\right]$$

例如，方程 $\frac{dy}{dx} + \frac{2}{x}y = x^2$，此处 $P(x) = \frac{2}{x}$，积分因子为 $\mu = e^{\int \frac{2}{x}dx} = x^2$。乘以 $x^2$ 后得 $\frac{d}{dx}(x^2 y) = x^4$，积分得 $x^2 y = \frac{x^5}{5} + C$，通解为 $y = \frac{x^3}{5} + Cx^{-2}$。

### 初值问题与解的存在唯一性

对初值问题 $\frac{dy}{dx} = f(x, y)$，$y(x_0) = y_0$，**皮卡–林德洛夫定理**（Picard-Lindelöf，1890年代建立）保证：若 $f$ 在点 $(x_0, y_0)$ 附近连续，且对 $y$ 满足利普希茨条件（即存在常数 $L > 0$ 使 $|f(x,y_1) - f(x,y_2)| \le L|y_1 - y_2|$），则该初值问题在 $x_0$ 某邻域内存在**唯一**解。利普希茨条件可用 $\left|\frac{\partial f}{\partial y}\right| \le L$ 来验证，这要求 $\frac{\partial f}{\partial y}$ 有界。

---

## 实际应用

**RC电路充电模型**：电阻 $R$ 与电容 $C$ 串联，接恒压源 $V_0$，电容电压 $u(t)$ 满足一阶线性ODE：$RC\frac{du}{dt} + u = V_0$，即 $\frac{du}{dt} + \frac{1}{RC}u = \frac{V_0}{RC}$。用积分因子法（$P = \frac{1}{RC}$，$Q = \frac{V_0}{RC}$）求解，初始条件 $u(0) = 0$，得特解 $u(t) = V_0\left(1 - e^{-t/(RC)}\right)$。时间常数 $\tau = RC$ 决定充电速度：经过 $\tau$ 时间，电容电压达到 $V_0$ 的约 $63.2\%$。

**逻辑斯谛增长**：种群数量 $N(t)$ 满足可分离变量方程 $\frac{dN}{dt} = rN\left(1 - \frac{N}{K}\right)$，其中 $r$ 为增长率，$K$ 为环境容量。分离变量并用部分分数分解积分后，通解为 $N(t) = \frac{K}{1 + \left(\frac{K - N_0}{N_0}\right)e^{-rt}}$，这是一条 S 形曲线，$N = K$ 是稳定平衡解。

---

## 常见误区

**误区1：积分因子计算中忽略常数项。** 计算 $\mu(x) = e^{\int P(x)dx}$ 时，积分结果不需要加积分常数，因为任意一个原函数都可使方程凑成全导数形式。若错误地写成 $e^{\int P\,dx + C} = Ce^{\int P\,dx}$，则会引入多余的参数，最终通解的形式虽然等价，但过程逻辑混乱，且初学者容易双重计数常数。

**误区2：通解包含所有解。** 对于某些非线性ODE（如可分离变量方程中 $h(y_*)=0$ 的情况），通解 $y = F(x, C)$ 并不能通过选取任何有限的 $C$ 值得到奇解 $y = y_*$。例如 $\frac{dy}{dx} = y^2$ 的通解为 $y = -\frac{1}{x+C}$，而 $y \equiv 0$ 也是方程的解，但无法由通解取任何 $C$ 表示。忽略奇解在物理建模中会导致遗漏某些平衡状态。

**误区3：混淆方程的阶与次。** ODE 的**阶**（order）指方程中出现的最高阶导数的阶数：$\frac{dy}{dx} = y^3$ 是**一阶**方程，尽管 $y$ 出现了三次（这是方程的**次**/次数）。线性ODE的定义要求 $y$ 及其各阶导数均以一次幂出现，$\frac{dy}{dx} = y^2$ 因含 $y^2$ 而是非线性方程，不能直接用积分因子法，必须先判断是否属于伯努利方程等特殊类型。

---

## 知识关联

**与积分技巧的关系**：求解可分离变量方程和线性ODE的核心步骤均是对给定函数求积分，因此部分分数分解、换元积分、分部积分等技巧直接决定能否得到显式解析解。例如逻辑斯谛方程的求解中必须用到 $\frac{1}{N(K-N)}$ 的部分分数分解。

**通向二阶常微分方程**：一阶线性ODE的解结构（通解 = 齐次通解 + 特解）在二阶线性ODE中被推广为叠加原理。一阶方程的积分因子思路，在二阶方程中演变为**常数变易法**（variation of parameters），其中的代入形式直接对应本章一阶线性ODE的通解结构。

**通向变分法**：某类变分问题（如欧拉-拉格朗日方程）在简单情形下退化为一阶或二阶ODE，ODE中建立的解的存在性与唯一性思想也是变分问题极值条件分析的理论基础。掌握 ODE 解的结构，使学习者在遇到变分法中