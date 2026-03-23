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
---
# 半定规划

## 概述

半定规划（Semidefinite Programming，SDP）是一类在对称矩阵锥上求解线性目标函数的凸优化问题。其标准形式要求决策变量 $X$ 为对称半正定矩阵（$X \succeq 0$），约束条件为线性矩阵不等式（LMI），目标函数为矩阵内积 $\langle C, X \rangle = \text{tr}(C^T X)$。与线性规划将变量约束在非负象限不同，SDP 将变量约束在半正定矩阵锥（PSD cone）上，这是一个真正的无穷维推广。

SDP 的理论框架在 20 世纪 90 年代初由 Vandenberghe 和 Boyd 等人系统化整理，1994 年 Nesterov 和 Nemirovskii 提出了针对 SDP 的内点法多项式时间算法，使得 SDP 从理论走向大规模实际计算成为可能。在此之前，处理线性矩阵不等式约束几乎没有可靠的数值方法。

SDP 的重要性在于它是目前已知计算上可处理（polynomial-time solvable）的最富表达力的凸优化类之一。大量组合优化问题（如 MAX-CUT）的最优松弛、控制理论中的稳定性分析、量子信息中的密度矩阵优化，都统一在 SDP 框架下求解。

## 核心原理

### 标准形式与对偶

SDP 的**原始标准形式**为：
$$\min_{X \in \mathbb{S}^n} \; \text{tr}(CX) \quad \text{s.t.} \; \text{tr}(A_i X) = b_i,\; i=1,\ldots,m,\; X \succeq 0$$
其中 $\mathbb{S}^n$ 表示 $n \times n$ 对称矩阵空间，$C, A_1, \ldots, A_m \in \mathbb{S}^n$，$b \in \mathbb{R}^m$。

对应的**对偶问题**为：
$$\max_{y \in \mathbb{R}^m} \; b^T y \quad \text{s.t.} \; \sum_{i=1}^m y_i A_i \preceq C$$
即对偶约束要求 $C - \sum_i y_i A_i \succeq 0$。SDP 满足弱对偶性（strong duality 在 Slater 条件下成立），对偶间隙为零需要原始和对偶均严格可行。注意 SDP 不像线性规划那样总是强对偶，存在原始/对偶可行但间隙非零的病态情形。

### 线性矩阵不等式（LMI）

LMI 的一般形式为 $F(x) = F_0 + \sum_{i=1}^m x_i F_i \succeq 0$，其中 $F_i \in \mathbb{S}^n$ 为给定矩阵，$x \in \mathbb{R}^m$ 为决策变量。LMI 约束集合是凸集，因为半正定矩阵锥在加法和正数标量乘法下封闭。多个 LMI 约束可通过块对角组合 $\text{diag}(F_1(x), F_2(x), \ldots) \succeq 0$ 统一处理。实际上，线性规划的非负约束 $x \geq 0$ 是 LMI 的特殊情形（取 $F_i$ 为对角矩阵）。

### 内点法求解

求解 SDP 的主要算法为**原始-对偶内点法**，核心思路是对障碍函数 $-\ln \det(X)$ 进行中心路径跟踪。每次迭代需要求解一个 $O(n^2) \times O(n^2)$ 的线性方程组（Schur 补方程），单次迭代复杂度为 $O(m^2 n^2 + m n^3)$。对于问题规模 $n = 1000, m = 10^4$ 的 SDP，现代求解器（如 SDPT3、SeDuMi、MOSEK）通常需要数分钟至数小时。精度保证上，内点法可在 $O(\sqrt{n} \ln(1/\varepsilon))$ 步内达到 $\varepsilon$ 精度。

## 实际应用

**MAX-CUT 的 Goemans-Williamson 松弛**是 SDP 最著名的应用之一。对于图 $G=(V,E)$ 的最大割问题，Goemans 和 Williamson（1995）构造如下 SDP：$\max \frac{1}{2}\sum_{(i,j)\in E}(1 - \langle v_i, v_j \rangle)$，约束 $\|v_i\|^2 = 1$，将每个节点对应单位向量。通过随机超平面舍入（random hyperplane rounding），该算法保证近似比 $0.878$，即结果不低于最优整数解的 87.8%，这一比值由 Irrational number $\alpha_{GW} = \min_{0 \leq \theta \leq \pi} \frac{2\theta}{\pi(1-\cos\theta)} \approx 0.8785$ 精确确定。

**控制系统稳定性分析**中，线性时不变系统 $\dot{x} = Ax$ 的 Lyapunov 稳定性条件 $A^T P + PA \prec 0, P \succ 0$ 可直接写为关于矩阵变量 $P$ 的 LMI，从而用 SDP 验证或设计满足 $H_\infty$ 性能指标的控制器。

**量子信息**中，量子态的密度矩阵 $\rho$ 满足 $\rho \succeq 0, \text{tr}(\rho) = 1$，判断两量子态是否纠缠（separability problem）的 PPT 准则等价于一组 SDP 约束。量子信道容量的计算也通过 SDP 给出可计算上界。

**多项式优化**中，SOS（Sum-of-Squares）方法将多项式非负性验证转化为 SDP：多项式 $p(x)$ 可表示为平方和当且仅当存在半正定矩阵 $Q$ 使得 $p(x) = z(x)^T Q z(x)$，其中 $z(x)$ 为单项式向量。

## 常见误区

**误区一：将 SDP 与普通矩阵变量优化混淆**。许多初学者认为"目标函数含矩阵变量的优化"就是 SDP，实际上 SDP 的关键约束是矩阵变量的**半正定性** $X \succeq 0$，而非仅仅矩阵参数化。若没有 PSD 约束，即使目标含矩阵内积，问题可能退化为普通线性规划甚至非凸问题。正定矩阵约束 $X \succ 0$（严格正定）与 $X \succeq 0$（半正定）在可行集几何上有本质区别：前者是开集，后者是闭凸锥。

**误区二：认为 SDP 强对偶总是成立**。线性规划在可行时强对偶恒成立，但 SDP 存在原始和对偶均可行却对偶间隙严格大于零的反例。例如，Ramana（1997）构造了如下情形：$\min x_1$ s.t. $\begin{pmatrix} x_1 & 1 \\ 1 & x_2 \end{pmatrix} \succeq 0$ 原始最优值为 0 但对偶不可达。强对偶成立的充分条件是 Slater 条件（内点可行性），即存在严格正定的可行解 $X \succ 0$。

**误区三：将 SDP 规模与线性规划规模等量齐观**。SDP 变量个数为 $n(n+1)/2$（对称矩阵独立元素数），但每步迭代要处理 $n \times n$ 矩阵的正定性（涉及 Cholesky 分解，复杂度 $O(n^3)$），因此 $n=100$ 的 SDP 比 $m=5050$ 的线性规划求解代价高出若干数量级。实践中，矩阵规模 $n > 2000$ 的 SDP 已属大规模问题，需要一阶方法（如 ADMM、谱方法）近似求解。

## 知识关联

**前置知识衔接**：理解 SDP 需要掌握**凸优化**中的对偶理论——Lagrange 对偶、KKT 条件直接对应 SDP 的原始-对偶关系，SDP 的对偶可行性条件 $C - \sum_i y_i A_i \succeq 0$ 即是 KKT 互补条件的矩阵版本。**正定矩阵**的知识则支撑了 SDP 可行集的几何理解：半正定矩阵锥的极点结构（秩-1 矩阵 $vv^T$）解释了 SDP 最优解通常具有低秩的现象（Barvinok-Pataki 界：若约束数为 $m$，最优解秩 $r$ 满足 $r(r+1)/2 \leq m$）。

**横向连接**：SDP 与**二阶锥规划**（SOCP）形成优化问题层次——LP $\subset$ SOCP $\subset$ SDP，三者均可在多项式时间内求解，表达能力依次增强。组合优化中的 Lovász theta 函数 $\vartheta(G)$（图的独立数与色多项式的界）是 SDP 松弛的经典成果，将离散问题与连续凸优化深度连接。
