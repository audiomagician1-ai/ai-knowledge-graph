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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 密度矩阵

## 概述

密度矩阵（density matrix），又称密度算符（density operator），是量子力学中描述**混合态系统**的数学工具。当一个量子系统的态无法用单一态矢量 |ψ⟩ 完整表示时——无论是因为系统处于统计混合，还是因为它与环境发生了纠缠——密度矩阵提供了唯一正确的描述框架。它由约翰·冯·诺依曼（John von Neumann）于1927年引入，并在他1932年出版的《量子力学的数学基础》中系统阐述。

密度矩阵 ρ 定义为：对于一个以概率 $p_i$ 处于纯态 $|\psi_i\rangle$ 的系综，其密度算符为

$$\rho = \sum_i p_i |\psi_i\rangle\langle\psi_i|$$

其中 $p_i \geq 0$，$\sum_i p_i = 1$。纯态是混合态的特殊情形，此时只有一个 $p_i = 1$，ρ 退化为 $|\psi\rangle\langle\psi|$，满足 $\rho^2 = \rho$。

密度矩阵之所以不可或缺，在于量子信息、量子光学、凝聚态物理等领域中，绝大多数真实系统都是混合态：激光器的输出光场、热平衡态的自旋系综、与环境耦合的量子比特，均无法用纯态波函数描述。密度矩阵将可观测量的期望值、系统动力学与量子关联统一纳入同一框架。

## 核心原理

### 密度矩阵的三个判定条件

一个合法的密度算符 ρ 必须同时满足：
1. **厄米性**：$\rho^\dagger = \rho$
2. **迹归一**：$\text{Tr}(\rho) = 1$
3. **半正定性**：对任意态 |φ⟩，有 $\langle\phi|\rho|\phi\rangle \geq 0$

区分纯态与混合态的判据是**纯度**（purity）$\gamma = \text{Tr}(\rho^2)$。纯态满足 $\gamma = 1$，混合态满足 $\frac{1}{d} \leq \gamma < 1$（d 为希尔伯特空间维数）。以两能级系统（qubit）为例，最大混合态为 $\rho = \frac{1}{2}I$，此时 $\gamma = \frac{1}{2}$，其布洛赫球表示为原点。

### 可观测量期望值与冯·诺依曼方程

在密度矩阵框架下，可观测量 A 的期望值为：
$$\langle A \rangle = \text{Tr}(\rho A)$$
这一公式统一了纯态的 $\langle\psi|A|\psi\rangle$ 与混合系综的统计平均。

密度算符在时间上的演化由**冯·诺依曼方程**（Liouville–von Neumann方程）给出：
$$i\hbar \frac{d\rho}{dt} = [H, \rho]$$
这是薛定谔方程在混合态下的直接推广。对于开放系统（与环境耦合），此方程需扩展为**林德布拉德方程**（Lindblad master equation）：
$$\frac{d\rho}{dt} = -\frac{i}{\hbar}[H,\rho] + \sum_k \left(L_k\rho L_k^\dagger - \frac{1}{2}L_k^\dagger L_k\rho - \frac{1}{2}\rho L_k^\dagger L_k\right)$$
其中 $L_k$ 称为**跳跃算符**（jump operator），描述系统与环境的各类耗散通道。

### 约化密度矩阵与纠缠

当系统由子系统 A 与 B 构成时，**约化密度矩阵**（reduced density matrix）通过对 B 的自由度求**偏迹**（partial trace）得到：
$$\rho_A = \text{Tr}_B(\rho_{AB})$$

以双量子比特贝尔态 $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$ 为例，计算 $\rho_{AB} = |\Phi^+\rangle\langle\Phi^+|$ 对 B 求偏迹，得到：
$$\rho_A = \text{Tr}_B(\rho_{AB}) = \frac{1}{2}I$$
这说明即使整体系统处于纯态，子系统 A 的约化密度矩阵已是最大混合态，这正是量子纠缠的本质体现——纠缠态的子系统不能用纯态描述。

### 退相干

退相干（decoherence）描述的是量子叠加态的非对角元素（coherence）在与环境相互作用后逐渐衰减为零的过程。以计算基 {|0⟩, |1⟩} 为例，一个叠加态的密度矩阵：
$$\rho = \begin{pmatrix} \frac{1}{2} & \frac{1}{2} \\ \frac{1}{2} & \frac{1}{2} \end{pmatrix}$$
在退相干后趋近于：
$$\rho \rightarrow \begin{pmatrix} \frac{1}{2} & 0 \\ 0 & \frac{1}{2} \end{pmatrix}$$
非对角元（量子相干性）消失，系统表现得如同经典概率混合。退相干时间 $T_2$（横向弛豫时间）是刻画这一过程速率的核心参数，超导量子比特的 $T_2$ 通常在微秒量级，而离子阱系统的 $T_2$ 可达秒量级，两者相差约六个数量级。

## 实际应用

**量子计算中的错误分析**：量子算法的噪声模型使用密度矩阵表示真实量子比特状态，用林德布拉德方程模拟退相干、振幅阻尼等噪声通道。IBM等公司的量子设备标定报告中，密度矩阵的纯度是评估量子比特质量的直接指标。

**量子态层析（Quantum State Tomography）**：通过对密度矩阵各矩阵元进行实验测量，可以完整重构一个未知量子态。对 n 量子比特系统，密度矩阵有 $4^n - 1$ 个独立实参数，例如2量子比特系统需要15个独立测量量。

**热平衡态描述**：温度为 T 的热平衡系统，其密度矩阵由**吉布斯态**（Gibbs state）给出：$\rho = \frac{e^{-H/k_BT}}{Z}$，其中 $Z = \text{Tr}(e^{-H/k_BT})$ 为配分函数。这将统计力学的正则系综直接编码进密度算符，是量子统计力学的基础。

**量子纠缠度量**：给定双体系统的密度矩阵 $\rho_{AB}$，**纠缠熵**定义为 $S(\rho_A) = -\text{Tr}(\rho_A \log \rho_A)$（冯·诺依曼熵），其中 $\rho_A$ 是约化密度矩阵。对于贝尔态，$S = \log 2 \approx 0.693$，达到1 qubit的最大纠缠熵。

## 常见误区

**误区1：混合态是"不知道系统在哪个态"的纯粹主观无知**

这是最常见的错误。经典概率混合（如不知道硬币正反面）与量子混合态在数学形式上看似相同，但物理含义截然不同。量子混合态（特别是由纠缠产生的约化密度矩阵）是客观的、不可还原的——即使掌握了全局纯态 $|\Phi^+\rangle$ 的全部信息，子系统 A 的状态依然必须用混合态 $\rho_A = \frac{1}{2}I$ 描述，不存在任何隐变量能将其还原为纯态。

**误区2：$\rho$ 的对角元代表量子概率，非对角元可以忽略**

非对角元（coherences）是量子干涉效应的载体。在双缝干涉实验中，条纹可见度与密度矩阵非对角元的模直接相关。当非对角元被退相干消除后，干涉条纹消失——这不是数学上的简化，而是真实物理效应的丧失。完全忽略非对角元等价于假设系统已经完全退相干，是一种物理上的额外假设。

**误区3：纯度 $\text{Tr}(\rho^2) < 1$ 意味着信息丢失**

对于一个开放量子系统的约化密度矩阵，纯度小于1并不意味着信息真正丢失——信息转移到了环境自由度中。整个系统（量子比特+环境）仍由纯态描述，冯·诺依曼方程仍然成立。只有在林德布拉德方程的Markov近似框架下，才将环境自由度"积分掉"，从而在约化描述层面呈现不可逆性。

## 知识关联

密度矩阵是算符与可观测量框架的直接延伸：可观测量 A 在混合态下的期望值 $\text{Tr}(\rho A)$ 将投影算符的谱分解与系综统计权重合并，成为比 $\langle\psi|