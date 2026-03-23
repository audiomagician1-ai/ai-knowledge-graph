---
id: "path-integrals-intro"
concept: "路径积分简介"
domain: "physics"
subdomain: "quantum-mechanics"
subdomain_name: "量子力学"
difficulty: 8
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 路径积分简介

## 概述

路径积分（Path Integral）是由理查德·费曼（Richard Feynman）于1948年在其博士论文及后续论文中系统提出的量子力学表述方式。这一形式体系与薛定谔的波函数方程方法等价，但提供了截然不同的物理图像：量子粒子从点A运动到点B时，不是沿某一条确定轨迹传播，而是**同时沿所有可能的路径传播**，每条路径对总振幅均有贡献。费曼的灵感来源于狄拉克（Dirac）1933年的一篇短文，后者提示了作用量（Action）与量子力学传播振幅之间的关联。

路径积分的数学核心是对所有可能路径的"求和"。在非相对论性量子力学中，从点 $(x_a, t_a)$ 传播到点 $(x_b, t_b)$ 的量子振幅——即**传播子（Propagator）** $K(x_b, t_b; x_a, t_a)$——写作：

$$K(x_b, t_b; x_a, t_a) = \int \mathcal{D}[x(t)]\, \exp\!\left(\frac{i}{\hbar} S[x(t)]\right)$$

其中 $S[x(t)] = \int_{t_a}^{t_b} L(x, \dot{x}, t)\, dt$ 是沿路径 $x(t)$ 计算的经典作用量，$L$ 为拉格朗日量，$\mathcal{D}[x(t)]$ 表示对所有满足边界条件的路径进行"泛函积分"。这一表述将量子力学与经典分析力学的拉格朗日框架直接联系在一起，而薛定谔方程使用的是哈密顿量 $H$。

## 核心原理

### 作用量相位与路径叠加

每条路径贡献一个复数振幅 $e^{iS/\hbar}$，其相位等于该路径作用量除以约化普朗克常数 $\hbar \approx 1.055 \times 10^{-34}$ J·s。当 $S \gg \hbar$ 时（宏观物体），相邻路径的相位差极大，彼此发生激烈的相消干涉，只有**经典路径邻域**（即作用量取驻值 $\delta S = 0$ 的路径）的贡献幸存——这正是最小作用量原理的量子起源。而在量子尺度，$S \sim \hbar$ 时，大量路径的相位相近，非经典路径的贡献不可忽略，干涉效应显著，产生纯量子行为如隧穿效应。

### 传播子与格林函数

传播子 $K(x_b, t_b; x_a, t_a)$ 同时也是薛定谔方程的格林函数，满足：

$$i\hbar \frac{\partial K}{\partial t_b} = \hat{H} K, \quad K(x_b, t_a; x_a, t_a) = \delta(x_b - x_a)$$

波函数的时间演化可以通过传播子完整描述：$\psi(x_b, t_b) = \int K(x_b, t_b; x_a, t_a)\, \psi(x_a, t_a)\, dx_a$。对于自由粒子（$V=0$），传播子可以精确计算：

$$K_{\text{free}}(x_b, t_b; x_a, t_a) = \sqrt{\frac{m}{2\pi i\hbar (t_b - t_a)}} \exp\!\left(\frac{im(x_b - x_a)^2}{2\hbar(t_b - t_a)}\right)$$

这一结果与高斯波包的自由扩散完全一致，验证了路径积分与薛定谔方程的等价性。

### 离散化构造与泛函积分的严格含义

$\mathcal{D}[x(t)]$ 的精确定义通过时间切片极限实现：将时间区间 $[t_a, t_b]$ 分成 $N$ 段，每段时长 $\varepsilon = (t_b - t_a)/N$，在每个中间时刻 $t_k$ 对空间坐标 $x_k$ 进行积分，然后取 $N \to \infty$：

$$\int \mathcal{D}[x(t)] \equiv \lim_{N \to \infty} \left(\frac{m}{2\pi i\hbar \varepsilon}\right)^{N/2} \int_{-\infty}^{\infty} dx_1 \cdots dx_{N-1}$$

前置归一化因子 $(m/2\pi i\hbar\varepsilon)^{N/2}$ 是为了使乘积在 $N\to\infty$ 时保持有限，其形式直接来自自由粒子高斯积分的归一化要求。

## 实际应用

**谐振子的精确解**：对于势 $V = m\omega^2 x^2 / 2$，路径积分可以通过将路径分解为经典路径加量子涨落来精确计算，结果与薛定谔方程完全一致，传播子为 $K_{\text{osc}} = \sqrt{m\omega / (2\pi i\hbar \sin\omega T)}\exp\bigl(\frac{im\omega}{2\hbar\sin\omega T}[(x_a^2 + x_b^2)\cos\omega T - 2x_a x_b]\bigr)$，其中 $T = t_b - t_a$。

**量子隧穿的半经典估算**：当粒子穿越势垒时，路径积分可在虚时间（将 $t \to -i\tau$）下计算，此时指数因子变为 $e^{-S_E/\hbar}$，$S_E$ 是欧氏作用量（Euclidean action）。对于高为 $V_0$、宽为 $a$ 的方形势垒，WKB近似下隧穿振幅正比于 $\exp(-2a\sqrt{2mV_0}/\hbar)$，路径积分框架给出了该结果的系统推导。

**量子场论基础**：路径积分方法是现代量子场论（QFT）的标准语言。标准模型中费曼图的生成泛函 $Z[J] = \int \mathcal{D}[\phi] \exp\bigl(iS[\phi] + i\int J\phi\bigr)$ 直接推广自非相对论性粒子路径积分，格点QCD的数值模拟也依赖欧氏路径积分的蒙特卡洛采样。

## 常见误区

**误区一：路径积分等同于对经典轨迹求和**。实际上，积分中包含的路径是所有可微或甚至不可微的连续函数，大量路径在经典力学中根本不被允许（如在势垒内的路径、超光速路径）。经典轨迹只是相位驻值点，其贡献在 $\hbar \to 0$ 的极限下主导，但在有限 $\hbar$ 下量子涨落的全部路径同等重要。

**误区二：路径积分是比薛定谔方程"更深"的理论**。两者在数学上完全等价——给定相同的哈密顿量，两种方法预言完全相同的物理结果。路径积分的优势在于物理直觉更清晰、处理规范场论时更自然，而非蕴含额外物理内容。

**误区三：对路径的积分是普通黎曼积分**。$\int \mathcal{D}[x(t)]$ 是泛函积分，其测度在数学上尚未完全严格化（Wiener测度在欧氏情形有严格定义，但闵可夫斯基情形存在振荡收敛问题）。在实际计算中，通常依赖威克转动（Wick rotation）$t \to -i\tau$ 转换为欧氏情形后再解析延拓。

## 知识关联

路径积分以薛定谔方程为等价基准：薛定谔方程中的时间演化算符 $\hat{U}(t) = e^{-i\hat{H}t/\hbar}$ 对应的位置空间矩阵元正是传播子 $K = \langle x_b | \hat{U}(t_b - t_a) | x_a \rangle$，两种方法从该等式出发可以相互推导。经典分析力学中的拉格朗日量 $L$ 和作用量 $S$ 是路径积分的直接输入，最小作用量原理在路径积分中获得了量子力学的解释：它是相位驻定（stationary phase）条件 $\delta S = 0$ 在 $\hbar \to 0$ 极限下的涌现结果。路径积分思想也为统计力学与量子力学架起了桥梁——将时间替换为虚时间 $\tau = it$，传播子 $K$ 变为配分函数的密度矩阵 $e^{-\beta H}$，有限温度量子场论正是建立在这一对应之上。
