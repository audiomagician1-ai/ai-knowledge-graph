---
id: "quantum-computing-intro"
concept: "量子计算简介"
domain: "physics"
subdomain: "quantum-mechanics"
subdomain_name: "量子力学"
difficulty: 7
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 量子计算简介

## 概述

量子计算是一种利用量子力学原理——叠加态、纠缠和干涉——执行计算的范式。与经典计算机使用只能处于0或1状态的比特不同，量子计算机使用量子比特（qubit），能够同时处于|0⟩和|1⟩的叠加态。这意味着一个 $n$ 量子比特系统可以同时表示 $2^n$ 个状态，使某些特定问题的求解速度相对经典算法实现指数级提升。

量子计算的理论基础由 Richard Feynman 于1982年提出，他在论文《Simulating Physics with Computers》（Feynman, 1982）中指出，经典计算机无法高效模拟量子系统，需要以指数级的资源存储量子态，并设想建造一台"通用量子模拟机"。1985年，David Deutsch 正式定义了通用量子图灵机模型，奠定了量子计算复杂性理论的基础。1994年，Peter Shor 提出了震惊学界的整数分解量子算法，证明量子计算机能在 $O((\log N)^3)$ 多项式时间内完成经典计算机需要亚指数时间才能完成的大数分解，直接威胁 RSA-2048 等公钥密码体系的安全性。1996年，Lov Grover 提出数据库搜索算法，将无序搜索从经典的 $O(N)$ 加速至 $O(\sqrt{N})$。

2019年10月，Google 宣称其53量子比特超导处理器 Sycamore 在200秒内完成了经典超级计算机需要约10000年才能完成的特定随机量子电路采样任务，这标志着"量子优越性"（quantum supremacy）的初步实验验证（Arute et al., *Nature*, 2019）。2023年IBM发布了1121量子比特的 Condor 处理器，但量子纠错所需的物理比特与逻辑比特比例问题仍是实用化的核心瓶颈。

---

## 核心原理

### 量子比特与叠加态

量子比特的状态用 Dirac 符号（狄拉克符号）表示为：

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$$

其中 $\alpha$ 和 $\beta$ 是复数振幅，满足归一化条件 $|\alpha|^2 + |\beta|^2 = 1$。$|\alpha|^2$ 表示测量后得到 $|0\rangle$ 的概率，$|\beta|^2$ 表示得到 $|1\rangle$ 的概率。测量操作本身具有破坏性——一旦测量，叠加态以 Born 规则坍缩为经典的0或1，无法重复读取叠加信息。这是量子算法设计的根本约束：必须在测量前通过干涉将正确答案的振幅放大，将错误答案的振幅抵消，最终以高概率读出正确结果。

$n$ 个量子比特的复合系统状态存在于 $2^n$ 维复数希尔伯特空间中。例如，3量子比特系统的一般状态为：

$$|\psi\rangle = \alpha_{000}|000\rangle + \alpha_{001}|001\rangle + \alpha_{010}|010\rangle + \cdots + \alpha_{111}|111\rangle$$

共8个基态，所有振幅的模平方之和为1。这8个振幅在计算过程中可以并行演化，形成量子并行性的物理来源。

物理上实现量子比特的方式多样，各有不同的退相干时间（coherence time）：超导约瑟夫森结（IBM、Google采用）的退相干时间约为 $10^{-4}$ 秒量级，被激光囚禁的离子阱（IonQ、Honeywell采用）约为秒量级，拓扑量子比特（微软研究）理论上具有更强的噪声免疫性但尚未大规模实现。退相干时间直接限制了在测量前可执行的量子门操作数量。

### 量子门操作

量子计算通过对量子比特施加量子门（幺正矩阵变换）执行运算。所有量子门对应 $2^n \times 2^n$ 的幺正矩阵 $U$，满足 $U^\dagger U = I$，保证量子演化的可逆性。

**Hadamard 门（H 门）** 是构造叠加态的基本工具：

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}, \quad H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \quad H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$$

**Pauli-X 门** 等价于经典非门，矩阵为 $\begin{pmatrix}0&1\\1&0\end{pmatrix}$，将 $|0\rangle \leftrightarrow |1\rangle$。

**T 门（$\pi/8$ 门）** 引入 $\pi/4$ 相对相位：

$$T = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$$

T 门与 H 门的组合是实现通用量子计算的最小门集之一，由 Solovay-Kitaev 定理保证：任意单量子比特幺正变换可用 $O(\log^c(1/\epsilon))$（$c \approx 2$）个 H 门和 T 门近似到精度 $\epsilon$。

**CNOT 门（受控非门）** 是最重要的双量子比特门，当控制位（control qubit）为 $|1\rangle$ 时对目标位（target qubit）执行 X 门，否则不操作：

$$\text{CNOT} = \begin{pmatrix} 1&0&0&0 \\ 0&1&0&0 \\ 0&0&0&1 \\ 0&0&1&0 \end{pmatrix}$$

对计算基 $\{|00\rangle, |01\rangle, |10\rangle, |11\rangle\}$ 作用效果为 $|00\rangle \to |00\rangle$，$|01\rangle \to |01\rangle$，$|10\rangle \to |11\rangle$，$|11\rangle \to |10\rangle$。

**例如**，将 H 门施加于第一个量子比特（初态 $|00\rangle$），再施加 CNOT 门，可生成 Bell 态（最大纠缠态）：

$$|00\rangle \xrightarrow{H \otimes I} \frac{|0\rangle+|1\rangle}{\sqrt{2}} \otimes |0\rangle \xrightarrow{\text{CNOT}} \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

这个 Bell 态正是量子纠缠的直接体现：两个量子比特处于完全关联的叠加态，对其中一个测量后，另一个状态立即确定，无论二者相距多远。

### Shor 算法的结构与复杂度

Shor 算法（Shor, 1994）用于分解整数 $N$，其核心是将因子分解问题规约为**阶求解问题**：找到最小正整数 $r$，使得

$$a^r \equiv 1 \pmod{N}$$

其中 $a$ 是随机选取的与 $N$ 互质的整数（$\gcd(a, N) = 1$）。找到 $r$ 后，若 $r$ 为偶数且 $a^{r/2} \not\equiv -1 \pmod{N}$，则 $\gcd(a^{r/2} \pm 1, N)$ 以至少 $1/2$ 的概率给出 $N$ 的非平凡因子。

算法流程分为三段：

1. **经典预处理**：随机选 $a \in \{2, \ldots, N-1\}$，若 $\gcd(a, N) > 1$ 则直接得到因子，否则进入量子步骤。
2. **量子阶求解**：初始化两个寄存器，第一个含 $2\lceil \log_2 N \rceil$ 个量子比特（约 $2n$ 位），第二个含 $n$ 位。对第一寄存器施加 H 门生成均匀叠加，然后通过受控模幂运算计算 $|x\rangle|a^x \bmod N\rangle$，对第一寄存器施加**量子傅里叶变换（QFT）**提取周期 $r$。
3. **经典后处理**：由连分数算法从测量结果中恢复 $r$，计算 $\gcd(a^{r/2} \pm 1, N)$，最多重复 $O(\log \log N)$ 次即可以恒定概率成功。

Shor 算法的总时间复杂度为 $O((\log N)^2 (\log \log N)(\log \log \log N))$，空间复杂度为 $O(\log N)$ 个量子比特，与经典最优算法（数域筛法，亚指数时间 $e^{O((\log N)^{1/3}(\log \log N)^{2/3})}$）相比是指数级加速。对于分解2048位RSA密钥，经典数域筛法估计需要约 $10^{13}$ MIPS-年的计算量，而理论上仅需约4000个逻辑量子比特的量子计算机即可在数小时内完成。

---

## 关键公式与算法实现

量子傅里叶变换（QFT）是 Shor 算法的核心子程序，其作用定义为：

$$\text{QFT}_N |j\rangle = \frac{1}{\sqrt{N}} \sum_{k=0}^{N-1} e^{2\pi i jk/N} |k\rangle$$

对于 $n$ 量子比特系统（$N = 2^n$），QFT 可用 $O(n^2)$ 个量子门实现（相比经典 FFT 的 $O(n \cdot 2^n)$），这是量子计算相对经典计算取得指数加速的关键来源。

以下是用 IBM Qiskit 构建3量子比特 QFT 线路的示例代码：

```python
from qiskit import QuantumCircuit
import numpy as np

def qft_3qubit():
    qc = QuantumCircuit(3)
    # 第0位：H门 + 受控相位门
    qc.h(0)
    qc.cp(np.pi / 2, 1, 0)   # 受控R2门，相位 π/2
    qc.cp(np.pi / 4, 2, 0)   # 受控R3门，相位 π/4
    # 第1位：H门 + 受控相位门
    qc.h(1)
    qc.cp(np.pi / 2, 2, 1)   # 受控R2门
    # 第2位：H门
    qc.h(2)
    # 交换比特顺序（QFT约定）
    qc.swap(0, 2)
    return qc

circuit = qft_3qubit()
print(circuit.draw())
# 总门数：3个H门 + 3个CP门 + 1个SWAP门 = 7个基本门
# 经典3点DFT需要 3×2³ = 24 次乘法运算
```

此代码中，`cp(θ, control, target)` 表示受控相位门 $R_k$，其矩阵为 $\begin{pmatrix}1&0\\0&e^{i\theta}\end{pmatrix}$，其中 $\theta = 2\pi/2^k$。3量子比特 QFT 仅需7个基本门，而对应的经典8点 DFT 需要约24次复数乘法，量子优势随比特数 $n$ 呈指数增长。

---

## 实际应用

### 密码学与后量子密码

Shor 算法对 RSA、椭圆曲线密码（ECC）等基于数论困难问题的公钥系统构成根本威胁。美国 NIST 自2016年启动"后量子密码标准化"竞赛，并于2024年正式发布三项标准：基于格的 ML-KEM（原 CRYSTALS-Kyber）和 ML-DSA（原 CRYSTALS-Dilithium），以及基于哈希的 SLH-DSA（原 SPHINCS+）。这些算法的安全性基于最短向量问题（SVP）等量子计算机同样无法高效求解的困难问题（NIST, 2024）。

### 量子化学模拟

Feynman 最初设想的应用领域。模拟含 $N$ 个电子的分子体系，经典方法（完全组态相互作用，FCI）需要 $O(2^N)$ 的存储和计算量。量子计算通过变分量子本征求解器（VQE, Peruzzo