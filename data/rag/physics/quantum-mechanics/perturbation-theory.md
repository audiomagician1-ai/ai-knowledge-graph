---
id: "perturbation-theory"
concept: "微扰理论"
domain: "physics"
subdomain: "quantum-mechanics"
subdomain_name: "量子力学"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 36.0
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 微扰理论

## 概述

微扰理论（Perturbation Theory）是量子力学中处理无法精确求解的哈密顿量问题的系统性近似方法。其核心思想是将系统哈密顿量分解为 $\hat{H} = \hat{H}_0 + \lambda\hat{H}'$，其中 $\hat{H}_0$ 是已知精确解的"未扰哈密顿量"，$\hat{H}'$ 是"微扰项"，$\lambda$ 是控制微扰大小的无量纲小参数（$0 < \lambda \ll 1$）。这种分解成立的物理条件是微扰项的矩阵元远小于未扰能级间距。

微扰理论由瑞利（Lord Rayleigh）在1894年用于经典声学振动问题，薛定谔（Erwin Schrödinger）于1926年将其移植到波动力学框架，建立了量子力学版本，同年发表于《Annalen der Physik》。这一方法之所以至关重要，在于自然界中绝大多数真实量子体系——如氢原子在外电场中（Stark效应）、自旋-轨道耦合、多电子原子——都不具有解析精确解，而微扰理论提供了系统的逐级修正方案。

## 核心原理

### 定态非简并微扰：能量与波函数的逐级展开

对于非简并能级，将能量本征值和本征态按 $\lambda$ 的幂次展开：
$$E_n = E_n^{(0)} + \lambda E_n^{(1)} + \lambda^2 E_n^{(2)} + \cdots$$
$$|\psi_n\rangle = |\psi_n^{(0)}\rangle + \lambda|\psi_n^{(1)}\rangle + \lambda^2|\psi_n^{(2)}\rangle + \cdots$$

将展开式代入定态薛定谔方程 $\hat{H}|\psi_n\rangle = E_n|\psi_n\rangle$，按 $\lambda$ 的幂次逐阶对比，得到**一阶能量修正**：
$$E_n^{(1)} = \langle\psi_n^{(0)}|\hat{H}'|\psi_n^{(0)}\rangle$$

这是微扰项 $\hat{H}'$ 在零阶态上的期望值。**一阶波函数修正**为：
$$|\psi_n^{(1)}\rangle = \sum_{m \neq n} \frac{\langle\psi_m^{(0)}|\hat{H}'|\psi_n^{(0)}\rangle}{E_n^{(0)} - E_m^{(0)}}|\psi_m^{(0)}\rangle$$

分母 $E_n^{(0)} - E_m^{(0)}$ 揭示了微扰理论的适用边界：若某两个未扰能级间距极小或为零，波函数修正项将发散，非简并微扰理论失效。

### 二阶能量修正

二阶能量修正为：
$$E_n^{(2)} = \sum_{m \neq n} \frac{|\langle\psi_m^{(0)}|\hat{H}'|\psi_n^{(0)}\rangle|^2}{E_n^{(0)} - E_m^{(0)}}$$

注意对于**基态**（$n=0$），所有分母 $E_0^{(0)} - E_m^{(0)} < 0$，因此 $E_0^{(2)} \leq 0$，即二阶修正必然使基态能量降低。这一结论对分析极化率（polarizability）和van der Waals相互作用具有重要意义。

### 简并微扰理论：好量子态的构造

当 $\hat{H}_0$ 的某一能级 $E_n^{(0)}$ 具有 $f$ 重简并时（即有 $f$ 个线性独立本征态对应同一能量），非简并公式中分母为零导致理论崩溃。简并微扰理论要求在这 $f$ 维简并子空间内，将 $\hat{H}'$ 限制在该子空间上构造 $f \times f$ **微扰矩阵**：
$$W_{ij} = \langle\psi_i^{(0)}|\hat{H}'|\psi_j^{(0)}\rangle, \quad i,j = 1,2,\ldots,f$$

对角化此矩阵，所得 $f$ 个本征值即为一阶能量修正 $E^{(1)}$，对应本征向量给出"好基"（good basis）——这些态是 $\hat{H}'$ 在简并子空间中的本征态，保证微扰展开的自洽性。若对角化后仍存在简并，则需引入更高阶微扰处理。

## 实际应用

**氢原子Stark效应（一阶）**：对于氢原子基态 $|1s\rangle$ 施加外电场 $\mathcal{E}$，微扰项为 $\hat{H}' = e\mathcal{E}z$。由于氢原子波函数具有确定宇称，$\langle 1s|z|1s\rangle = 0$，故基态一阶能量修正为零。须计算二阶修正，结果为 $E^{(2)} = -\frac{9}{2}a_0^3\mathcal{E}^2$（$a_0$ 为玻尔半径），由此得出氢原子基态极化率 $\alpha = 9a_0^3 \approx 4.5 \times 10^{-30}\ \mathrm{m}^3$。

**氢原子 $n=2$ 级Stark效应（简并微扰）**：$n=2$ 有四重简并（$|2s\rangle, |2p,0\rangle, |2p,+1\rangle, |2p,-1\rangle$）。构造 $4\times 4$ 微扰矩阵，仅 $\langle 2s|e\mathcal{E}z|2p,0\rangle = -3e\mathcal{E}a_0$ 非零，对角化后能级分裂为 $E^{(1)} = \pm 3e\mathcal{E}a_0, 0, 0$，这正是线性Stark效应——能级移动与电场强度成正比，与基态的二次Stark效应形成鲜明对比。

**精细结构（自旋-轨道耦合）**：氢原子精细结构中，微扰项为 $\hat{H}' = \frac{1}{2m_e^2c^2r^3}\hat{\mathbf{L}}\cdot\hat{\mathbf{S}}$。利用恒等式 $\hat{\mathbf{L}}\cdot\hat{\mathbf{S}} = \frac{1}{2}(\hat{J}^2 - \hat{L}^2 - \hat{S}^2)$，在好量子态 $|n,l,j,m_j\rangle$ 基下对角化，一阶修正使 $2p$ 能级分裂为 $2p_{1/2}$ 和 $2p_{3/2}$，实验观测分裂约为 $0.365\ \mathrm{cm}^{-1}$。

## 常见误区

**误区一：将 $\lambda$ 视为必须明确赋值的物理参数。** 实际计算中 $\lambda$ 仅是一个"标记参数"，用于追踪修正的阶次，最终令 $\lambda = 1$ 将所有修正直接代入原始哈密顿量。许多教材直接写 $\hat{H} = \hat{H}_0 + \hat{H}'$，不显式出现 $\lambda$，但逻辑上各阶修正仍按 $\hat{H}'$ 矩阵元的幂次组织。

**误区二：非简并条件仅要求能级不等。** 正确条件是微扰矩阵元 $|\langle\psi_m^{(0)}|\hat{H}'|\psi_n^{(0)}\rangle|$ 必须远小于对应的能级间距 $|E_n^{(0)} - E_m^{(0)}|$。若两个能级间距虽不为零但极小（"近简并"），而矩阵元不可忽略，仍需用简并微扰框架处理这两个态，否则波函数修正会异常放大。

**误区三：简并被完全消除则简并微扰计算结束。** 若对角化 $f\times f$ 矩阵后仍有本征值相等（剩余简并），此时对应的"好基"并不唯一，一阶修正无法区分这些态，必须上升到二阶微扰矩阵进行进一步处理，即在剩余简并子空间内再次构造并对角化更高阶的有效矩阵。

## 知识关联

微扰理论的推导全程依赖**算符与可观测量**的语言：$\hat{H}_0$ 的本征态完备性保证了波函数修正的展开合法性，$\hat{H}'$ 作为厄米算符确保所有能量修正均为实数，简并微扰中矩阵 $W_{ij}$ 的厄米性保证了本征值（能量修正）的实性。若 $\hat{H}'$ 与 $\hat{H}_0$ 的某个守恒量算符 $\hat{A}$ 对易，则 $\hat{H}'$ 在不同量子数对应态之间的矩阵元为零（即 $\langle n',a'|\hat{H}'|n,a\rangle = 0$ 当 $a' \neq a$），这一选择定则大幅简化了微扰矩阵的计算——这在自旋-轨道耦合使用 $|j,m_j\rangle$ 好量子态时体现得最为直接。

微扰理论的有效性在场论中被进一步扩展为费曼图展开：量子电动力学（Q
