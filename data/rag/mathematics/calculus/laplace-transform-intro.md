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
quality_tier: "pending-rescore"
quality_score: 40.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.379
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 拉普拉斯变换初步

## 概述

拉普拉斯变换（Laplace Transform）是一种将时域函数 $f(t)$（$t \geq 0$）映射为复频域函数 $F(s)$ 的积分变换，其定义公式为：

$$\mathcal{L}\{f(t)\} = F(s) = \int_0^{+\infty} f(t)e^{-st}\,dt$$

其中 $s = \sigma + j\omega$ 是复数参数。该变换的本质是用衰减指数 $e^{-st}$ 对 $f(t)$ 加权后求广义积分，将微分方程中的求导运算转化为 $s$ 的多项式代数运算。

该变换以法国数学家皮埃尔-西蒙·拉普拉斯（Pierre-Simon Laplace，1749—1827）命名，他在1782年前后将这一思想用于概率母函数研究。19世纪末至20世纪初，英国工程师奥利弗·赫维赛德（Oliver Heaviside）独立发展出"算子微积分"，将其系统化应用于电路分析，这正是拉普拉斯变换在工程领域立足的历史起点。

拉普拉斯变换之所以在求解二阶（及高阶）常微分方程时至关重要，原因在于它将初始条件自动嵌入代数方程之中：对 $f'(t)$ 取变换得 $sF(s) - f(0)$，对 $f''(t)$ 取变换得 $s^2F(s) - sf(0) - f'(0)$，初始值 $f(0)$ 和 $f'(0)$ 直接出现在代数表达式里，无需事后回代。

---

## 核心原理

### 存在条件与收敛域

并非所有函数都有拉普拉斯变换。$F(s)$ 存在要求广义积分 $\int_0^{+\infty}f(t)e^{-st}\,dt$ 收敛。若存在实数 $M > 0$ 和 $\sigma_0$，使得对所有 $t \geq 0$ 满足 $|f(t)| \leq Me^{\sigma_0 t}$（称为**指数阶**条件），则当 $\text{Re}(s) > \sigma_0$ 时 $F(s)$ 存在。例如，$f(t) = e^{t^2}$ 增长过快，不是指数阶函数，没有拉普拉斯变换；而 $f(t) = t^n$（任意正整数 $n$）是指数阶的，其变换为 $F(s) = \dfrac{n!}{s^{n+1}}$（$\text{Re}(s) > 0$）。

### 常用变换对

以下是构成计算基础的核心变换对：

| 时域 $f(t)$（$t \geq 0$） | 复频域 $F(s)$ | 收敛条件 |
|---|---|---|
| $1$（单位阶跃） | $\dfrac{1}{s}$ | $\text{Re}(s)>0$ |
| $e^{at}$ | $\dfrac{1}{s-a}$ | $\text{Re}(s)>a$ |
| $\sin(\omega t)$ | $\dfrac{\omega}{s^2+\omega^2}$ | $\text{Re}(s)>0$ |
| $\cos(\omega t)$ | $\dfrac{s}{s^2+\omega^2}$ | $\text{Re}(s)>0$ |
| $\delta(t)$（单位冲激） | $1$ | 全平面 |

其中 $\sin(\omega t)$ 的变换可由 $e^{j\omega t}$ 的变换 $\dfrac{1}{s-j\omega}$ 取虚部导出，体现了欧拉公式与拉普拉斯变换的内在联系。

### 线性与微分性质

**线性性**：$\mathcal{L}\{af(t)+bg(t)\} = aF(s)+bG(s)$，这使得叠加原理直接适用于变换域。

**微分性质**（最核心）：
$$\mathcal{L}\{f^{(n)}(t)\} = s^n F(s) - s^{n-1}f(0) - s^{n-2}f'(0) - \cdots - f^{(n-1)}(0)$$

对二阶微分方程 $y'' + py' + qy = g(t)$，两边取拉普拉斯变换后立即得到：
$$[s^2Y(s) - sy(0) - y'(0)] + p[sY(s) - y(0)] + qY(s) = G(s)$$
整理出 $Y(s)$ 的代数表达式，无需求齐次解与特解再叠加。

**积分性质**：$\mathcal{L}\left\{\int_0^t f(\tau)\,d\tau\right\} = \dfrac{F(s)}{s}$，即积分对应在 $s$ 域除以 $s$，与微分对应乘以 $s$ 形成对偶。

**位移性质（$s$域平移）**：$\mathcal{L}\{e^{at}f(t)\} = F(s-a)$，利用此性质可直接得出 $\mathcal{L}\{e^{at}\sin(\omega t)\} = \dfrac{\omega}{(s-a)^2+\omega^2}$。

### 拉普拉斯逆变换

逆变换的精确公式为**Bromwich积分**：
$$f(t) = \mathcal{L}^{-1}\{F(s)\} = \frac{1}{2\pi j}\int_{\sigma-j\infty}^{\sigma+j\infty} F(s)e^{st}\,ds$$

此积分在数学上需用留数定理计算，属高等内容。在初步学习阶段，逆变换主要通过**部分分式分解**配合变换表来实现。例如，若 $F(s) = \dfrac{2s+3}{s^2+3s+2} = \dfrac{2s+3}{(s+1)(s+2)}$，分解为 $\dfrac{1}{s+1} + \dfrac{1}{s+2}$，则 $f(t) = e^{-t} + e^{-2t}$（$t \geq 0$）。分母多项式（称为**特征多项式**）的根直接决定响应的衰减模式。

---

## 实际应用

**求解带初始条件的二阶ODE**：考虑弹簧振动方程 $y'' + 4y = \sin(2t)$，初始条件 $y(0)=0,\, y'(0)=0$。取变换：
$$s^2Y(s) + 4Y(s) = \frac{2}{s^2+4}$$
$$Y(s) = \frac{2}{(s^2+4)^2}$$

利用公式 $\mathcal{L}^{-1}\left\{\dfrac{2\omega^3}{(s^2+\omega^2)^2}\right\} = \sin(\omega t) - \omega t\cos(\omega t)$（$\omega=2$ 时），可直接得出 $y(t)$，包含因 $t\cos(2t)$ 项体现的共振现象——这是方程右侧频率恰好等于固有频率 $\omega_0=2$ 的标志。

**RC电路分析**：对串联RC电路，基尔霍夫电压定律给出 $RC\,\dfrac{dV_C}{dt} + V_C = V_{in}(t)$。取拉普拉斯变换后，电容电压响应为 $V_C(s) = \dfrac{V_{in}(s)}{1+sRC}$，分母 $1+sRC$ 中的极点 $s = -\dfrac{1}{RC}$ 直接决定电路的时间常数 $\tau = RC$，无需求解微分方程全程。

---

## 常见误区

**误区一：认为 $t<0$ 的行为不影响变换**

拉普拉斯变换积分下限是 $0$，因此它只处理 $t \geq 0$ 的信息。但这意味着：若 $f(t)$ 在 $t=0$ 处不连续（例如单位阶跃函数在 $t=0$ 突变），微分性质中的初始值 $f(0)$ 应理解为单侧极限 $f(0^+)$，而非 $t=0^-$ 处的值。若混淆 $0^-$ 和 $0^+$，初始条件代入会产生错误。

**误区二：对非指数阶函数强行套用公式**

$f(t) = e^{t^2}$ 没有拉普拉斯变换，强行计算 $\int_0^\infty e^{t^2}e^{-st}dt$ 会发散。学生有时以为"只要 $s$ 足够大就收敛"，但对超指数增长函数，无论取多大的实数 $\sigma$，$e^{t^2-\sigma t}$ 在 $t\to\infty$ 时仍趋向无穷。

**误区三：将部分分式分解中的重根处理混淆**

当 $F(s) = \dfrac{1}{(s+1)^2}$ 时，逆变换是 $te^{-t}$，而非 $e^{-t}$。重极点 $(s+a)^k$ 对应的时域函数是 $\dfrac{t^{k-1}}{(k-1)!}e^{-at}$，其中多了一个 $t$ 的幂次因子。漏掉这一幂次是部分分式逆变换中最常见的计算错误。

---

## 知识关联

**与广义积分的联系**：拉普拉斯变换的定义式 $\int_0^{+\infty}f(t)e^{-st}dt$ 本身就是含参广义积分。判
