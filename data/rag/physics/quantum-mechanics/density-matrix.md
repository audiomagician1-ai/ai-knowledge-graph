---
id: "density-matrix"
concept: "密度矩阵"
domain: "physics"
subdomain: "quantum-mechanics"
subdomain_name: "量子力学"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 37.4
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.414
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 密度矩阵

## 概述

密度矩阵（density matrix），也称密度算符（density operator），是量子力学中描述量子态的最普遍形式。与态矢量 |ψ⟩ 只能描述**纯态**（pure state）不同，密度矩阵能够统一描述纯态和**混合态**（mixed state），即由于与环境相互作用或经典统计不确定性而导致的统计系综状态。密度矩阵 ρ 是一个厄米算符，满足 ρ = ρ†，迹等于1（Tr(ρ) = 1），且半正定（ρ ≥ 0）。

密度矩阵的概念由约翰·冯·诺依曼（John von Neumann）于1927年独立提出，与莱夫·朗道几乎同时。冯·诺依曼在其著作《量子力学的数学基础》中系统建立了密度矩阵的理论框架，目的是将量子不确定性与经典统计不确定性置于同一数学体系中处理。这一工具在20世纪后半叶随着量子光学、量子信息论的兴起而变得极为重要。

密度矩阵的重要性在于：真实实验中的量子系统几乎从不处于纯态。一个量子比特与环境发生哪怕极微弱的相互作用，其态矢量描述就会失效，而密度矩阵仍能精确刻画系统状态。量子计算中的**退相干**问题、量子纠缠的度量、以及开放量子系统的演化，都必须借助密度矩阵语言来表述。

---

## 核心原理

### 纯态与混合态的密度矩阵

对于纯态 |ψ⟩，密度矩阵定义为外积：

$$\rho = |\psi\rangle\langle\psi|$$

例如，若 |ψ⟩ = α|0⟩ + β|1⟩（|α|² + |β|² = 1），则：

$$\rho = \begin{pmatrix} |\alpha|^2 & \alpha\beta^* \\ \alpha^*\beta & |\beta|^2 \end{pmatrix}$$

**混合态**的密度矩阵是多个纯态的经典概率加权：

$$\rho = \sum_i p_i |\psi_i\rangle\langle\psi_i|$$

其中 $p_i \geq 0$，$\sum_i p_i = 1$。区分纯态与混合态的判据是**纯度**（purity）：

$$\text{Tr}(\rho^2) = 1 \iff \text{纯态};\quad \text{Tr}(\rho^2) < 1 \iff \text{混合态}$$

对于 $N$ 维系统，混合态的纯度下限为 $1/N$，此时称为**最大混合态**（maximally mixed state），其密度矩阵为 $\rho = I/N$。

### 可观测量的期望值与冯·诺依曼熵

给定可观测量算符 $\hat{A}$，其期望值由下式计算：

$$\langle \hat{A} \rangle = \text{Tr}(\rho \hat{A})$$

这一公式统一了纯态和混合态的情形：当 ρ = |ψ⟩⟨ψ| 时，Tr(ρÂ) = ⟨ψ|Â|ψ⟩，与态矢量方法完全一致。

**冯·诺依曼熵**是密度矩阵的核心信息量度量：

$$S(\rho) = -\text{Tr}(\rho \ln \rho) = -\sum_i \lambda_i \ln \lambda_i$$

其中 $\lambda_i$ 是 $\rho$ 的本征值。纯态的冯·诺依曼熵为0，最大混合态的熵为 $\ln N$。这一概念是量子信息论中量子信道容量、量子纠缠度量的基础。

### 约化密度矩阵与纠缠

对于由子系统 A 和 B 组成的复合系统，全系统的密度矩阵为 ρ_AB。**约化密度矩阵**（reduced density matrix）通过对子系统 B 求偏迹（partial trace）得到：

$$\rho_A = \text{Tr}_B(\rho_{AB}) = \sum_j \langle j_B | \rho_{AB} | j_B \rangle$$

其中 $\{|j_B\rangle\}$ 是子系统 B 的正交完备基。

以贝尔态 $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ 为例，对子系统 B 求偏迹：

$$\rho_A = \text{Tr}_B(|\Phi^+\rangle\langle\Phi^+|) = \frac{1}{2}\begin{pmatrix}1 & 0 \\ 0 & 1\end{pmatrix} = \frac{I}{2}$$

结果是最大混合态（$\text{Tr}(\rho_A^2) = 1/2$），表明子系统 A 单独而言处于完全不确定的混合态，而整体却是纯态。这一矛盾直接揭示了**量子纠缠**的本质：纠缠越强，子系统的约化密度矩阵越接近最大混合态，冯·诺依曼熵越大。

### 退相干与密度矩阵的演化

**退相干**（decoherence）在密度矩阵语言中表现为非对角元素（相干项 coherences）的衰减。以量子比特为例，初始叠加态 ρ(0) 的非对角元 ρ₀₁(0) = αβ* 在与环境耦合后按指数衰减：

$$\rho_{01}(t) = \rho_{01}(0)\, e^{-\Gamma t}$$

其中 Γ 是退相干率，由系统-环境耦合强度决定。对角元（布居数 populations）保持不变，而非对角元（相干性 coherences）趋向零。这使得密度矩阵趋近于对角矩阵，量子干涉效应消失，系统表现出经典行为。

开放量子系统密度矩阵的时间演化由**林德布拉德方程**（Lindblad master equation）描述：

$$\frac{d\rho}{dt} = -\frac{i}{\hbar}[H, \rho] + \sum_k \left(L_k \rho L_k^\dagger - \frac{1}{2}L_k^\dagger L_k \rho - \frac{1}{2}\rho L_k^\dagger L_k\right)$$

其中 $L_k$ 是**跳跃算符**（jump operators），描述系统与环境的各种耗散通道。

---

## 实际应用

**量子层析（Quantum State Tomography）**：实验中通过对大量相同制备的量子系统进行不同基矢的测量，重构系统的密度矩阵。对于 $n$ 个量子比特，密度矩阵有 $4^n - 1$ 个独立实参数需要确定（例如2量子比特系统需要确定15个参数）。

**量子纠缠度量**：对于双量子比特纯态，纠缠程度由子系统 A 的约化密度矩阵的冯·诺依曼熵定量描述，称为**纠缠熵**。最大纠缠态（贝尔态）的纠缠熵为 ln 2 ≈ 0.693。

**核磁共振（NMR）量子计算**：室温下核自旋系综处于极高温混合态，密度矩阵为 ρ ≈ I/N + ε·δρ，其中 ε ~ 10⁻⁵ 量级。实验中操作的是所谓**赝纯态**（pseudopure state），通过密度矩阵框架才能正确分析NMR量子计算协议。

---

## 常见误区

**误区一：混合态等同于叠加态**。纯态 $\frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$ 的密度矩阵含有非零非对角元，具有量子相干性；而经典等概率混合态 $\rho = \frac{1}{2}|0\rangle\langle0| + \frac{1}{2}|1\rangle\langle1| = \frac{I}{2}$ 的非对角元为零，无相干性。两者在 Z 基测量结果相同（各50%），但在 X 基（Hadamard基）测量中，纯叠加态 |+⟩ 总给出确定结果，混合态则给出随机结果，可通过干涉实验区分。

**误区二：约化密度矩阵的混合性来自于无知**。初学者常认为ρ_A是混合态只是因为"我们不知道B的状态"。实际上，即使对整个AB系统有完全量子力学描述（纯态），A的约化密度矩阵仍可能是混合态。这种混合性源于量子纠缠本身，是量子力学的内在非定域性质，与经典统计无知有本质区别。

**误区三：密度矩阵分解的唯一性**。同一密度矩阵 ρ 可以对应无穷多种纯态系综分解，例如最大混合态 I/2 既可以写成 $\frac{1}{2}|0\rangle\langle0| + \frac{1}{2}|1\rangle\langle1|$，也可以写成 $\frac{1}{2}|+\rangle\langle+| + \frac{1}{2}|-\rangle\langle-|$。这意
