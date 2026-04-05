---
id: "laplace-transform-intro"
concept: "拉普拉斯变换初步"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 8
is_milestone: false
tags: ["拓展"]

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

# 拉普拉斯变换初步

## 概述

拉普拉斯变换是一种将时域函数 $f(t)$（$t \geq 0$）转化为复频域函数 $F(s)$ 的积分变换，其定义式为：

$$\mathcal{L}\{f(t)\} = F(s) = \int_0^{+\infty} f(t)e^{-st}\,dt$$

其中 $s = \sigma + j\omega$ 是复数参数，该积分在 $\text{Re}(s)$ 充分大时收敛。这一变换的核心价值在于：原本难以直接求解的常微分方程，经拉普拉斯变换后变为关于 $s$ 的代数方程，求解后再做逆变换即可还原答案。

该变换由法国数学家皮埃尔-西蒙·拉普拉斯（Pierre-Simon Laplace）在18世纪末的概率论研究中提出雏形，后由英国工程师奥利弗·亥维赛（Oliver Heaviside）于19世纪90年代发展为实用的"运算微积分"方法，广泛应用于电路分析与控制系统设计。拉普拉斯变换存在的充分条件是 $f(t)$ 在 $[0,+\infty)$ 上分段连续，且存在常数 $M > 0$、$c \geq 0$ 使得 $|f(t)| \leq Me^{ct}$（称为指数级增长条件），此时收敛域为 $\text{Re}(s) > c$。

## 核心原理

### 基本变换对

掌握几个关键的变换对是使用拉普拉斯变换的基础。

- **常数函数**：$\mathcal{L}\{1\} = \dfrac{1}{s}$，$\text{Re}(s) > 0$
- **指数函数**：$\mathcal{L}\{e^{at}\} = \dfrac{1}{s-a}$，$\text{Re}(s) > a$
- **幂函数**：$\mathcal{L}\{t^n\} = \dfrac{n!}{s^{n+1}}$，$n$ 为非负整数，$\text{Re}(s) > 0$
- **正弦函数**：$\mathcal{L}\{\sin(\omega t)\} = \dfrac{\omega}{s^2 + \omega^2}$
- **余弦函数**：$\mathcal{L}\{\cos(\omega t)\} = \dfrac{s}{s^2 + \omega^2}$

以 $\mathcal{L}\{e^{at}\}$ 为例，直接代入定义式：$\int_0^{+\infty} e^{at}e^{-st}\,dt = \int_0^{+\infty} e^{-(s-a)t}\,dt = \dfrac{1}{s-a}$，要求 $\text{Re}(s-a) > 0$，即 $\text{Re}(s) > a$。这里的广义积分收敛性判断直接依赖于前置知识中的含参数广义积分理论。

### 线性性质与微分性质

拉普拉斯变换具有**线性性**：$\mathcal{L}\{\alpha f(t) + \beta g(t)\} = \alpha F(s) + \beta G(s)$，使得变换对叠加信号同样有效。

最具实用价值的是**微分性质**：

$$\mathcal{L}\{f'(t)\} = sF(s) - f(0^+)$$

$$\mathcal{L}\{f''(t)\} = s^2F(s) - sf(0^+) - f'(0^+)$$

这两个公式将导数运算转化为关于 $s$ 的乘法运算，并自动将初始条件 $f(0^+)$ 和 $f'(0^+)$ 纳入方程，这正是它求解初值问题时远比特征根法简洁的原因。对应地，**积分性质**为：

$$\mathcal{L}\left\{\int_0^t f(\tau)\,d\tau\right\} = \frac{F(s)}{s}$$

### 平移性质与卷积定理

**s 域平移**（频移）：$\mathcal{L}\{e^{at}f(t)\} = F(s-a)$，例如由 $\mathcal{L}\{\sin\omega t\} = \dfrac{\omega}{s^2+\omega^2}$ 可直接得到 $\mathcal{L}\{e^{at}\sin\omega t\} = \dfrac{\omega}{(s-a)^2+\omega^2}$。

**时域卷积定理**：若 $\mathcal{L}\{f(t)\} = F(s)$，$\mathcal{L}\{g(t)\} = G(s)$，则

$$\mathcal{L}\{(f * g)(t)\} = F(s) \cdot G(s)$$

其中 $(f*g)(t) = \int_0^t f(\tau)g(t-\tau)\,d\tau$。卷积定理将时域的卷积积分转化为 $s$ 域的乘积，在求解含积分项的积分微分方程时极为高效。

### 拉普拉斯逆变换

逆变换的严格定义为**Bromwich 积分**（复反演积分）：

$$f(t) = \mathcal{L}^{-1}\{F(s)\} = \frac{1}{2\pi j}\int_{c-j\infty}^{c+j\infty} F(s)e^{st}\,ds$$

但在初等应用中，通常不直接计算此围道积分，而是采用**部分分数分解法**：将有理函数 $F(s)$ 拆分为若干形如 $\dfrac{A}{s-a}$、$\dfrac{Bs+C}{s^2+\omega^2}$ 的项，再对照标准变换对逐项取逆变换。

例如，$F(s) = \dfrac{2s+3}{s^2+3s+2} = \dfrac{1}{s+1} + \dfrac{1}{s+2}$，故 $f(t) = e^{-t} + e^{-2t}$（$t \geq 0$）。

## 实际应用

**求解二阶常系数线性初值问题**：考虑 $y'' + 3y' + 2y = e^{-t}$，初始条件 $y(0) = 0$，$y'(0) = 1$。

两边取拉普拉斯变换，利用微分性质：

$$[s^2Y - 0 - 1] + 3[sY - 0] + 2Y = \frac{1}{s+1}$$

整理得：$(s^2+3s+2)Y = 1 + \dfrac{1}{s+1} = \dfrac{s+2}{s+1}$

因此 $Y(s) = \dfrac{s+2}{(s+1)(s+1)(s+2)} = \dfrac{1}{(s+1)^2}$

对照幂函数变换对：$\mathcal{L}\{te^{-t}\} = \dfrac{1}{(s+1)^2}$，故 $y(t) = te^{-t}$。整个过程绕过了待定系数法中对特解形式的猜测，初始条件在变换阶段便已处理完毕。

在电路分析中，电感电路方程 $L\dfrac{di}{dt} + Ri = u(t)$ 经拉普拉斯变换后变为 $(Ls + R)I(s) = U(s) + Li(0^+)$，其中 $\dfrac{1}{Ls+R}$ 即为电路的**传递函数**，这是控制工程的基础概念。

## 常见误区

**误区一：忽略收敛域的存在**。$\mathcal{L}\{e^{2t}\} = \dfrac{1}{s-2}$ 仅在 $\text{Re}(s) > 2$ 时成立；若将此式用于 $\text{Re}(s) < 2$ 的区域则无意义。初学者往往只记住变换式而忘记收敛域，在叠加不同收敛域的变换时尤易出错。

**误区二：混淆微分性质中初始值的取法**。公式 $\mathcal{L}\{f'(t)\} = sF(s) - f(0^+)$ 中使用的是 $t = 0^+$ 处的右极限，而非 $f(0)$。对于在 $t = 0$ 处有跳跃间断点的函数（如阶跃函数），$f(0^-)$、$f(0)$、$f(0^+)$ 可能各不相同，必须取 $f(0^+)$。

**误区三：将逆变换的部分分数法当作万能工具**。部分分数分解仅对有理函数 $F(s)$ 有效。对于含 $e^{-as}$ 因子的函数（对应时域的延迟），需要结合**时移定理** $\mathcal{L}\{f(t-a)u(t-a)\} = e^{-as}F(s)$ 处理，单纯套用部分分数会得到错误结果。

## 知识关联

拉普拉斯变换的定义本身就是一个含参数 $s$ 的**广义积分** $\int_0^{+\infty} f(t)e^{-st}\,dt$，因此广义积分的收敛性判别（如比较判别法、绝对收敛）是理解变换存在条件的直接工具。

与**二阶常微分方程**的联系最为直接：特征根方程 $r^2 + pr + q = 0$ 对应拉普拉斯变换后分母多项式 $s^2 + ps + q$ 的零点，两种方法处理的是同一类方程，但拉普拉斯变换法通过代数化操作将求齐次解、特解和初始条件的三步骤合并为一步，对非零初始条件和不连续