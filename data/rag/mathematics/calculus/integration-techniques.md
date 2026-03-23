---
id: "integration-techniques"
concept: "积分技巧"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 6
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 35.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 积分技巧

## 概述

积分技巧是一组将复杂被积函数转化为可直接套用基本公式的系统性方法，核心包括**换元积分法**和**分部积分法**两大体系。不定积分本身只提供了基本函数的积分表，而绝大多数实际遇到的函数——如 $\sin(x^2)$、$xe^x$、$\ln x$ 等——并不直接出现在积分表中，必须借助技巧加以变形后才能求解。

换元法由莱布尼茨在17世纪微积分建立初期便已使用，其实质是将微分形式的链式法则"反向运用"。分部积分法则源于乘积求导法则的逆运算，公式 $\int u\,dv = uv - \int v\,du$ 由欧拉在18世纪系统整理并推广应用于特殊函数的积分计算。这两种方法至今仍是手工求解不定积分与定积分的最主要工具，Wolfram Alpha、Mathematica 等计算机代数系统在符号积分时也依赖类似算法实现。

## 核心原理

### 第一类换元法（凑微分法）

第一类换元法的基本思路：若被积式可以写成 $f(g(x))\cdot g'(x)\,dx$ 的形式，则令 $u = g(x)$，有 $du = g'(x)\,dx$，从而

$$\int f(g(x))\cdot g'(x)\,dx = \int f(u)\,du$$

成功与否取决于能否在被积函数中"凑出"某个内层函数的导数。例如求 $\int \cos(3x)\,dx$：注意到 $(3x)'= 3$，故凑出 $\frac{1}{3}\cdot 3\,dx = \frac{1}{3}d(3x)$，令 $u=3x$ 得 $\frac{1}{3}\sin(3x)+C$。常见的凑微分模板包括：$x^{n-1}dx = \frac{1}{n}d(x^n)$、$e^x dx = d(e^x)$、$\frac{1}{x}dx = d(\ln|x|)$ 等。

### 第二类换元法（变量替换法）

第二类换元法适用于被积函数含有根式或三角函数难以直接处理的情形，主动引入新变量 $x = \varphi(t)$，要求 $\varphi(t)$ 单调可导且 $\varphi'(t)\neq 0$。三类典型替换：

- **三角换元**：含 $\sqrt{a^2-x^2}$ 时令 $x=a\sin t$，$t\in[-\frac{\pi}{2},\frac{\pi}{2}]$；含 $\sqrt{a^2+x^2}$ 时令 $x=a\tan t$；含 $\sqrt{x^2-a^2}$ 时令 $x=a\sec t$。
- **根式换元**：含 $\sqrt[n]{ax+b}$ 时令 $t=\sqrt[n]{ax+b}$，直接消去根号。
- **倒代换**：当分母次数远高于分子时令 $x=\frac{1}{t}$，降低分母的幂次。

例如 $\int\sqrt{1-x^2}\,dx$：令 $x=\sin t$，则 $dx=\cos t\,dt$，$\sqrt{1-x^2}=\cos t$，积分变为 $\int\cos^2 t\,dt = \frac{t}{2}+\frac{\sin 2t}{4}+C$，回代得 $\frac{1}{2}\arcsin x + \frac{x\sqrt{1-x^2}}{2}+C$。

### 分部积分法

分部积分公式来源于乘积求导法则 $(uv)'= u'v + uv'$，两边积分整理得：

$$\int u\,dv = uv - \int v\,du$$

关键在于选取 $u$ 和 $dv$ 的分工：$\int v\,du$ 必须比原积分更容易计算。选取 $u$ 的优先级口诀通常记为"**反对幂指三**"（反三角函数 > 对数函数 > 幂函数 > 指数函数 > 三角函数），优先级高者作 $u$，其余部分作 $dv$。

以 $\int x e^x\,dx$ 为例：令 $u=x$，$dv=e^x\,dx$，则 $du=dx$，$v=e^x$，代入得 $xe^x - \int e^x\,dx = xe^x - e^x + C$。对于 $\int e^x\sin x\,dx$ 这类循环型，连续分部积分两次后原积分重新出现在右侧，设其为 $I$，解方程 $I = -e^x\cos x + e^x\sin x - I$ 得 $I = \frac{e^x(\sin x - \cos x)}{2}+C$。

## 实际应用

**物理中的功与位移**：弹簧弹力 $F=kx$，拉伸距离 $a$ 到 $b$ 所做的功 $W=\int_a^b kx\,dx$，用第一类换元或直接积分得 $W=\frac{k}{2}(b^2-a^2)$。若力为 $F=xe^{-x}$ 形式，则需用分部积分法求定积分。

**概率论中的期望值**：正态分布、指数分布的期望值计算都依赖积分技巧。例如指数分布期望 $E(X)=\int_0^{+\infty} x\lambda e^{-\lambda x}\,dx$，令 $u=x$，$dv=\lambda e^{-\lambda x}dx$，分部积分后得 $E(X)=\frac{1}{\lambda}$，此结果是排队论和可靠性工程的基础参数。

**工程信号处理**：傅里叶变换中 $\int_{-\infty}^{+\infty} f(t)e^{-i\omega t}\,dt$ 的计算，对于 $f(t)$ 为多项式与指数函数之积时，反复使用分部积分法——每次分部后多项式次数降低1次，经过有限步骤可得到解析结果。

## 常见误区

**误区一：换元后忘记替换积分限（定积分）**  
做定积分换元时，必须将原变量的积分限同步替换为新变量的积分限。例如 $\int_0^1 2x e^{x^2}\,dx$，令 $u=x^2$，上下限需改为 $u(0)=0$、$u(1)=1$，不需要回代——若计算完后回代到原变量再代入原积分限，结果相同但会多一步操作且容易出错。许多学生习惯只改被积函数，保留原积分限，导致错误。

**误区二：分部积分的 $u$ 与 $dv$ 选反导致死循环或更复杂**  
对 $\int \ln x\,dx$，若错误地令 $u=1$（即将 $\ln x$ 归入 $dv$），则 $v=\int\ln x\,dx$ 仍然未知，陷入循环。正确做法是令 $u=\ln x$，$dv=dx$，则 $v=x$，$du=\frac{1}{x}dx$，得 $x\ln x - \int x\cdot\frac{1}{x}\,dx = x\ln x - x + C$。"反对幂指三"的优先级规则正是为了避免这类无效选择。

**误区三：三角换元回代时符号处理错误**  
令 $x=a\sin t$ 时，$\sqrt{a^2-x^2}=a|\cos t|$，由于 $t\in[-\frac{\pi}{2},\frac{\pi}{2}]$，$\cos t \geq 0$，故 $|\cos t|=\cos t$ 可去绝对值。但若对 $x=a\sec t$（$\sqrt{x^2-a^2}$ 情形）不注意 $t$ 的范围，$\tan t$ 的符号处理错误会导致结果差一个负号。

## 知识关联

学习积分技巧需要熟练掌握不定积分的基本公式表（约20条），以及复合函数求导（链式法则）和乘积求导法则——换元法是链式法则的积分版本，分部积分法是乘积法则的积分版本，两者在本质上都是微分法则的"逆向工程"。

掌握这两种积分技巧后，将直接支撑**常微分方程初步**的学习：分离变量法求解 $\frac{dy}{dx}=f(x)g(y)$ 时，分离后的两侧都需要独立积分，往往涉及换元或分部积分；一阶线性方程的通解公式 $y=e^{-\int P(x)dx}\left[\int Q(x)e^{\int P(x)dx}dx + C\right]$ 中，两层积分的计算直接依赖本章技巧。此外，这两种方法也是后续学习含参变量积分和多重积分化简的前提。
