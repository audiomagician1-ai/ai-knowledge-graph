# 最优控制

## 概述

最优控制（Optimal Control）是现代控制理论的核心分支，其根本目标是在满足系统动态约束和边界条件的前提下，寻找一个控制策略使某一预设的性能指标（Performance Index）达到极值——通常是最小化能量消耗、跟踪误差或时间成本。与经典控制仅关注稳定性和频率响应不同，最优控制将控制问题转化为一个严格的变分学或动态规划问题，从数学上保证所求解的控制律在某种明确量化的意义上是"最好的"。

这一学科的奠基工作集中在20世纪50至60年代。苏联数学家列夫·庞特里亚金（Lev Pontryagin）于1956年至1962年间与其团队（Boltyansky、Gamkrelidze、Mishchenko）发展了极大值原理，并于1962年以专著《最优过程的数学理论》（*The Mathematical Theory of Optimal Processes*）系统阐述。与此同时，美国数学家理查德·贝尔曼（Richard Bellman）于1957年在《动态规划》（*Dynamic Programming*）中提出了以"最优性原理"为核心的动态规划框架。两条路径殊途同归，共同构建了最优控制理论的数学基础（Pontryagin et al., 1962；Bellman, 1957）。

---

## 核心原理

### 性能指标的构造

最优控制问题的首要任务是量化"好坏"。性能指标（也称代价函数，Cost Function）通常采用博尔扎（Bolza）形式：

$$J = \Phi\bigl(\mathbf{x}(t_f), t_f\bigr) + \int_{t_0}^{t_f} L\bigl(\mathbf{x}(t), \mathbf{u}(t), t\bigr)\, dt$$

其中，$\mathbf{x}(t) \in \mathbb{R}^n$ 为状态向量，$\mathbf{u}(t) \in \mathbb{R}^m$ 为控制输入向量，$t_0$ 和 $t_f$ 分别为初始时刻和终止时刻，$\Phi(\cdot)$ 为终端代价（Mayer项），$L(\cdot)$ 为运行代价（Lagrange项）。当 $\Phi = 0$ 时退化为拉格朗日（Lagrange）问题；当 $L = 0$ 时退化为Mayer问题。

对于线性二次型调节器（LQR），运行代价取二次型形式：

$$L = \mathbf{x}^T Q \mathbf{x} + \mathbf{u}^T R \mathbf{u}$$

其中 $Q \in \mathbb{R}^{n \times n}$ 为半正定状态权重矩阵（$Q \geq 0$），$R \in \mathbb{R}^{m \times m}$ 为正定控制权重矩阵（$R > 0$）。$Q$ 的对角元素越大，对应状态分量的偏差惩罚越重；$R$ 越大则控制能量受到更严格限制。矩阵 $Q$ 和 $R$ 的选取直接决定了系统响应速度与能量消耗之间的权衡关系。

### 庞特里亚金极大值原理

庞特里亚金极大值原理（Pontryagin's Maximum Principle, PMP）是处理带约束最优控制问题的最强大工具之一，其适用范围超越了贝尔曼动态规划所要求的光滑性条件，可处理控制变量 $\mathbf{u}(t)$ 受闭合有界集 $\mathcal{U}$ 约束的情形。

引入协态变量（Costate Variable，也称伴随变量）$\boldsymbol{\lambda}(t) \in \mathbb{R}^n$，定义哈密顿函数（Hamiltonian）：

$$H\bigl(\mathbf{x}, \mathbf{u}, \boldsymbol{\lambda}, t\bigr) = L(\mathbf{x}, \mathbf{u}, t) + \boldsymbol{\lambda}^T f(\mathbf{x}, \mathbf{u}, t)$$

其中 $f(\mathbf{x}, \mathbf{u}, t)$ 为系统动态方程 $\dot{\mathbf{x}} = f(\mathbf{x}, \mathbf{u}, t)$。极大值原理指出，最优控制 $\mathbf{u}^*(t)$ 必须在每一时刻使哈密顿函数关于 $\mathbf{u}$ 取得极小值（当最小化 $J$ 时）：

$$\mathbf{u}^*(t) = \arg\min_{\mathbf{u} \in \mathcal{U}} H\bigl(\mathbf{x}^*(t), \mathbf{u}, \boldsymbol{\lambda}^*(t), t\bigr)$$

与此同时，协态变量满足伴随方程（Adjoint Equation）：

$$\dot{\boldsymbol{\lambda}} = -\frac{\partial H}{\partial \mathbf{x}}\bigg|^* , \quad \boldsymbol{\lambda}(t_f) = \frac{\partial \Phi}{\partial \mathbf{x}(t_f)}$$

这一两点边值问题（Two-Point Boundary Value Problem, TPBVP）——状态方程从 $t_0$ 向前积分，协态方程从 $t_f$ 向后积分——构成了求解最优轨迹的核心计算难题。

### 线性二次型调节器（LQR）

LQR是最优控制在线性系统上的完美闭合解，由卡尔曼（Rudolph Kalman）于1960年在论文《线性二次型损失问题的新结果》中正式建立（Kalman, 1960）。对于线性时不变系统 $\dot{\mathbf{x}} = A\mathbf{x} + B\mathbf{u}$，无限时域LQR的最优状态反馈控制律具有简洁的线性结构：

$$\mathbf{u}^*(t) = -K\mathbf{x}(t), \quad K = R^{-1} B^T P$$

其中增益矩阵 $K \in \mathbb{R}^{m \times n}$，$P$ 是如下代数黎卡提方程（Algebraic Riccati Equation, ARE）的唯一正定解：

$$A^T P + P A - P B R^{-1} B^T P + Q = 0$$

ARE的存在唯一正定解依赖于系统的可控性（$(A, B)$ 可控）与可观测性（$(A, \sqrt{Q})$ 可观测）条件。LQR的闭环极点总是位于复平面左半部分，且对增益和相位裕度有严格保证：单输入情形下，增益裕度为 $[1/2, +\infty)$，相位裕度至少为 60°——这是LQR在鲁棒性方面的重要先天优势（Doyle & Stein, 1981）。

---

## 关键公式与模型

### 有限时域LQR与黎卡提微分方程

当终止时刻 $t_f$ 有限时，最优代价函数可以写为 $J^* = \mathbf{x}^T(t_0) P(t_0) \mathbf{x}(t_0)$，其中时变矩阵 $P(t)$ 满足黎卡提微分方程（Riccati Differential Equation）：

$$-\dot{P}(t) = A^T P(t) + P(t) A - P(t) B R^{-1} B^T P(t) + Q$$

边界条件为 $P(t_f) = Q_f$（终端状态权重矩阵）。该方程需从 $t_f$ 向 $t_0$ 反向积分求解，相应最优控制为时变增益：$K(t) = R^{-1} B^T P(t)$。

### 最优时间控制与Bang-Bang控制

当性能指标为最短时间 $J = \int_{t_0}^{t_f} 1\, dt = t_f - t_0$，且控制量满足 $|u_i(t)| \leq u_{max}$，由极大值原理可知最优控制呈Bang-Bang形式——控制量在每一时刻取其上下界之一：

$$u^*(t) = -u_{max} \cdot \text{sgn}\bigl(\lambda^T(t) b\bigr)$$

其中 $b$ 为控制输入矩阵 $B$ 对应列向量。控制量切换次数对于 $n$ 阶系统不超过 $n-1$ 次（对于双积分器模型为1次切换）。双积分器时间最优问题的解即为著名的"抛物线切换曲线"，是时间最优控制的经典案例。

---

## 实际应用

**案例一：航天器姿态机动**  
航天器在有限燃料约束下的快速姿态调整是最优控制的典型应用场景。以最小燃料消耗（$J = \int_0^{t_f} \|\mathbf{u}\|_1 dt$）为目标，利用PMP可以导出推力器的开关时序（即Bang-Off-Bang控制律）。美国阿波罗登月舱姿控系统设计中即采用了类似的最优开关逻辑（Breakwell, 1959年相关工作为先驱）。

**案例二：自动驾驶车辆轨迹规划**  
在结构化道路上，将车辆纵向运动建模为双积分器 $\ddot{s} = a$，以舒适性指标（最小化加速度变化率，即Jerk）$J = \int_0^T \dddot{s}^2\, dt$ 为性能函数，可得到5次多项式轨迹。这是当前量产自动驾驶系统（如Waymo、Tesla Autopilot纵向规划模块）中轨迹平滑算法的数学基础。

**案例三：经济增长的最优投资**  
拉姆齐（Ramsey）-卡斯（Cass）-库普曼斯（Koopmans）增长模型将跨期效用最大化表达为：$\max \int_0^\infty e^{-\rho t} U(c(t))\, dt$，其中 $\rho$ 为时间偏好率，$c(t)$ 为人均消费。这是最优控制在宏观经济学中的奠基性应用，被誉为将Ramsey（1928年）直觉与Pontryagin工具相结合的范式。

---

## 常见误区

**误区一：混淆协态变量与拉格朗日乘子**  
协态变量 $\boldsymbol{\lambda}(t)$ 虽在形式上类似静态优化的拉格朗日乘子，但它是时间的函数，在经济学解释上代表状态变量 $\mathbf{x}$ 的"影子价格"随时间的演化，满足动态方程而非代数关系。忽视其时变性是初学者常见错误。

**误区二：LQR的鲁棒性保证仅对单输入系统严格成立**  
上文提到的 60° 相位裕度和 $[1/2, +\infty)$ 增益裕度，仅在单输入（SISO）情形下由Kalman不等式直接保证。对于多输入系统，若加入执行器权重或传感器噪声后设计为LQG（LQR+卡尔曼滤波），则这些鲁棒性保证可能完全消失——这正是Doyle于1978年"Guaranteed Margins for LQG Regulators"论文所揭示的著名反例（Doyle, 1978）。

**误区三：极大值原理给出的是必要条件而非充分条件**  
满足PMP条件的解称为极值（Extremal），它是最优解的必要条件。在系统为线性、代价为凸函数的情形下，必要条件同时是充分条件；但对于一般非线性非凸问题，PMP给出的候选解可能是局部极值甚至鞍点，需结合充分条件（如Hamilton-Jacobi-Bellman方程的验证函数）进一步确认。

**误区四：忽视两点边值问题的数值求解难度**  
许多教材在推导PMP后轻描淡写地说"求解TPBVP即可"。实际上，TPBVP对初值极度敏感（协态变量初值 $\boldsymbol{\lambda}(t_0)$ 未知），传统打靶法在系统维度较高时收敛困难。实际工程中大量转而使用直接法（Direct Method）——将轨迹离散后转化为非线性规划（NLP）问题求解，代表软件包括GPOPS-II（伪谱法）和CasADi（自动微分+内点法）。

---

## 知识关联

**向上关联——状态空间控制（state-space-control）**：最优控制以状态方程 $\dot{\mathbf{x}} = f(\mathbf{x}, \mathbf{u