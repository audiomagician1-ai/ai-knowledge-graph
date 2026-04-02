---
id: "semidefinite-programming"
concept: "半定规划"
domain: "mathematics"
subdomain: "optimization"
subdomain_name: "最优化"
difficulty: 9
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 半定规划

## 概述

半定规划（Semidefinite Programming，SDP）是一类在矩阵变量上定义的凸优化问题，其约束条件要求矩阵变量为半正定矩阵（Positive Semidefinite，PSD）。标准形式的SDP在线性目标函数下，通过矩阵不等式约束将可行域限定在半正定矩阵锥（PSD Cone）之内。相比线性规划只处理向量变量、二次规划只处理标量二次型，SDP将变量提升为矩阵，使其具有更强的表达能力。

SDP的理论框架在1990年代由Vandenberghe和Boyd系统整理并发表于1996年的《SIAM Review》综述论文，奠定了现代SDP理论的基础。在此之前，Alizadeh于1995年发展了内点法在SDP上的应用，证明了SDP可以在多项式时间内求解。这一进展将大量原本难以处理的组合优化问题和控制系统设计问题纳入了高效可求解的范畴。

SDP的重要性在于它是凸优化层次中功能最强的多项式时间可解问题类之一：线性规划 ⊂ 二阶锥规划 ⊂ 半定规划，形成严格的包含关系。许多NP难问题的最强多项式时间近似算法（如最大割问题的Goemans-Williamson算法，近似比0.878）都依赖SDP松弛。

---

## 核心原理

### 标准形式与矩阵不等式

SDP的标准形式（不等式形式）为：

$$
\min_{X \in \mathbb{S}^n} \langle C, X \rangle \quad \text{s.t.} \quad \langle A_i, X \rangle = b_i,\ i=1,\ldots,m,\quad X \succeq 0
$$

其中 $X \in \mathbb{S}^n$ 表示 $n \times n$ 实对称矩阵，$\langle C, X \rangle = \text{tr}(C^T X)$ 为矩阵内积，$X \succeq 0$ 表示 $X$ 为半正定矩阵（即所有特征值 $\geq 0$）。符号 $\succeq$ 定义了半正定锥上的偏序，称为Löwner偏序。对偶问题（等式形式）为：

$$
\max_{y \in \mathbb{R}^m} b^T y \quad \text{s.t.} \quad \sum_{i=1}^m y_i A_i \preceq C
$$

强对偶性在SDP中**不**自动成立——需要满足Slater条件（即存在严格可行点 $X \succ 0$），才能保证对偶间隙为零。这与线性规划的强对偶定理存在本质区别，是SDP理论中需特别注意的技术细节。

### 半正定锥的几何结构

半正定锥 $\mathbb{S}^n_+$ 是 $n(n+1)/2$ 维实对称矩阵空间 $\mathbb{S}^n$ 中的一个闭凸锥，其极端射线（Extreme Rays）由秩为1的矩阵 $vv^T$ 构成。当 $n=2$ 时，$\mathbb{S}^2_+$ 可几何化为三维空间中的一个"冰淇淋锥"（实际上是旋转锥面），其边界正好与二阶锥规划的可行域等价，这也直接说明了二阶锥规划是SDP的特例。半正定锥不像正定锥那样是内部开集，其边界（奇异点）是秩亏损矩阵的集合，这给内点法迭代带来数值挑战。

### 内点法求解与计算复杂度

求解SDP最常用的算法是内点法中的**原对偶路径跟踪法**（Primal-Dual Path Following）。该方法引入对数障碍函数 $-\mu \log \det(X)$，沿着中心路径迭代趋近最优解。每次迭代需要求解一个 $m \times m$ 的线性方程组（正规方程），其中 $m$ 为约束数量，单次迭代的计算量为 $O(m^2 n^2 + m n^3)$。因此当矩阵维度 $n$ 和约束数 $m$ 均较大时（如 $n > 1000$），标准内点法会面临内存和计算瓶颈，需借助一阶方法（如ADMM或谱方法）替代。常用求解器包括SeDuMi、SDPT3和MOSEK，后者在工业界应用最广泛。

---

## 实际应用

**最大割SDP松弛（MAX-CUT）**：给定无向图 $G=(V,E)$，权重矩阵 $W$，最大割问题的SDP松弛将 $\pm 1$ 向量变量替换为半正定矩阵，问题变为：

$$
\max \frac{1}{4} \langle L, X \rangle \quad \text{s.t.} \quad X_{ii}=1,\ X \succeq 0
$$

其中 $L$ 为图的拉普拉斯矩阵。对最优解进行随机超平面切割后得到近似解，Goemans和Williamson（1995）证明该算法的近似比为 $\alpha_{\text{GW}} \approx 0.8786$，是迄今在标准复杂度假设下已知的最佳多项式时间近似算法。

**控制系统中的线性矩阵不等式（LMI）**：判断线性系统 $\dot{x} = Ax$ 的渐近稳定性等价于寻找Lyapunov矩阵 $P \succ 0$ 满足 $A^T P + PA \prec 0$，这正是一个SDP可行性问题。$H_\infty$ 鲁棒控制设计、多目标控制综合均可转化为SDP，是控制工程中SDP应用最成熟的领域。

**量子信息中的纠缠检测**：判断密度矩阵是否对应可分态（Separable State）是量子信息中的核心问题。SDP可用于计算最优纠缠见证（Entanglement Witness）算子，形式上等价于在密度矩阵的半正定约束下最小化某个线性泛函。

**多项式优化的SOS松弛**：判断多项式 $p(x)$ 是否为平方和（Sum-of-Squares, SOS）多项式，等价于存在半正定矩阵 $Q \succeq 0$ 使得 $p(x) = z(x)^T Q\, z(x)$，其中 $z(x)$ 是单项式向量。Lasserre层级（2001）通过逐阶SDP松弛逼近多项式优化的全局最优，在有限阶数下可以恢复精确最优解。

---

## 常见误区

**误区一：混淆强对偶的适用条件。** 线性规划在原问题或对偶问题有界时强对偶自动成立，但SDP存在原对偶均可行而对偶间隙仍为正的反例（如Dattorro 2003年给出的经典构造）。必须显式验证Slater条件（严格可行性），才能保证强对偶成立和数值求解器的可靠收敛。许多学生将LP的强对偶定理直接移植到SDP，会导致推导上的严重错误。

**误区二：认为SDP可以精确表示所有凸优化问题。** SDP虽然表达能力很强，但存在凸优化问题无法用有限维SDP精确表示的情形。例如，协正锥（Copositive Cone）上的优化比SDP严格更难，可以编码NP难问题而不损失最优性，这说明"所有凸问题均可化为SDP"是错误的。正确的认识是：SDP只覆盖可用线性矩阵不等式描述的凸集。

**误区三：忽略数值精度导致的秩判断失误。** 在用SDP求解组合优化松弛时，需要根据最优解矩阵 $X^*$ 的秩来判断松弛是否紧（tight）。但数值求解器返回的解存在浮点误差，理论上秩为1的矩阵在数值上可能表现为秩为2或更高，若不设置合理的阈值（通常取特征值比值 $\lambda_2/\lambda_1 < 10^{-6}$ 作为近似秩1判断标准），会错误地认为松弛不紧，导致后续分析失误。

---

## 知识关联

**与正定矩阵的关系**：SDP的约束 $X \succeq 0$ 直接来源于正定矩阵理论。Cholesky分解、矩阵特征值的单调性以及Schur补引理（Schur Complement Lemma）是将非线性矩阵不等式转化为标准LMI的核心工具——例如，非线性约束 $C - A^T B^{-1} A \succeq 0$（$B \succ 0$）等价于分块矩阵 $\begin{pmatrix} B & A \\ A^T & C \end{pmatrix} \succeq 0$，后者是合法的线性矩阵不等式。

**与凸优化的关系**：SDP的可行域（半正定锥上的仿射截面）是凸集，目标函数是线性的，因此SDP是凸优化的特殊情形，局部最优即为全局最优的性质成立。凸优化中的KKT条件在SDP上的表现为互补松弛条件 $XS = 0$（其中 $S = C - \sum y_i A_i$