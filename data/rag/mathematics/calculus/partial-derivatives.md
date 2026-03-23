---
id: "partial-derivatives"
concept: "偏导数"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 7
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 偏导数

## 概述

偏导数是多元函数微分学的基本工具，用于描述函数值随某一个自变量变化时的瞬时变化率，同时将所有其他自变量视为常数固定不变。对于函数 $f(x, y)$，关于 $x$ 的偏导数记作 $\frac{\partial f}{\partial x}$ 或 $f_x$，其定义为极限 $\frac{\partial f}{\partial x} = \lim_{\Delta x \to 0} \frac{f(x + \Delta x, y) - f(x, y)}{\Delta x}$。这与一元函数导数的区别不在于运算技巧，而在于"固定其他变量"这一本质操作。

偏导数的符号 $\partial$（读作"偏"或"rounded d"）由德国数学家雅可比（Carl Gustav Jacob Jacobi）在19世纪推广使用，以区别于全导数符号 $d$。偏导数概念的形成伴随着18世纪热传导方程、流体力学等物理问题的需求，欧拉和拉格朗日在分析多变量系统时已隐含使用了这一思想。

偏导数的重要性体现在它是理解曲面切平面、全微分以及梯度的直接基础。在机器学习的反向传播算法中，损失函数对每个参数的偏导数构成了梯度的分量，决定了参数更新的方向与步长。

## 核心原理

### 偏导数的计算规则

计算偏导数时，将所有不求导的变量视为数值常数，然后应用一元函数的全部求导法则。例如对 $f(x, y) = x^2 y + \sin(xy) + y^3$，对 $x$ 求偏导时，$y$ 视为常数：

$$\frac{\partial f}{\partial x} = 2xy + y\cos(xy)$$

对 $y$ 求偏导时，$x$ 视为常数：

$$\frac{\partial f}{\partial y} = x^2 + x\cos(xy) + 3y^2$$

注意 $y^3$ 对 $x$ 的偏导数为 $0$，因为它被视为常数，这是初学者最容易出错的地方。

### 高阶偏导数与混合偏导数

对偏导数再次求偏导可得高阶偏导数。二阶纯偏导数 $\frac{\partial^2 f}{\partial x^2}$ 表示先对 $x$ 求两次偏导，混合偏导数 $\frac{\partial^2 f}{\partial y \partial x}$ 表示先对 $x$ 再对 $y$ 求偏导。

克莱罗定理（Clairaut's Theorem，1740年）指出：若函数 $f$ 的两个混合偏导数 $\frac{\partial^2 f}{\partial x \partial y}$ 和 $\frac{\partial^2 f}{\partial y \partial x}$ 在某点连续，则两者在该点相等。这一条件在绝大多数工程和物理应用场景中自动满足，但数学上确实存在违反克莱罗定理的反例，例如：

$$f(x,y) = \begin{cases} \frac{xy(x^2 - y^2)}{x^2 + y^2}, & (x,y) \neq (0,0) \\ 0, & (x,y) = (0,0) \end{cases}$$

该函数在原点处 $\frac{\partial^2 f}{\partial x \partial y}(0,0) = 1$ 而 $\frac{\partial^2 f}{\partial y \partial x}(0,0) = -1$，两者不相等，因为混合偏导数在原点不连续。

### 全微分与偏导数的关系

全微分 $df$ 描述了函数值的总变化量，由各偏导数乘以对应自变量微分之和构成：

$$df = \frac{\partial f}{\partial x}dx + \frac{\partial f}{\partial y}dy$$

这里需要特别注意：偏导数存在并不保证全微分存在（即函数可微）。函数在某点可微的充分条件是所有偏导数在该点邻域内存在且连续。反例是 $f(x,y) = \frac{xy}{\sqrt{x^2+y^2}}$（原点处补充定义为0），该函数在原点处两个偏导数均为0，但函数在原点不可微，因为沿方向 $(1,1)$ 趋近原点时增量不满足线性近似条件。

## 实际应用

**热传导方程**：物理中描述温度分布 $T(x,t)$ 随时间演变的一维热方程为 $\frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2}$，其中 $\alpha$ 是热扩散率。方程左侧是 $T$ 对时间 $t$ 的偏导数，右侧是 $T$ 对位置 $x$ 的二阶偏导数，两者均是固定另一变量后的偏导数。

**经济学中的边际分析**：柯布-道格拉斯生产函数 $Q = A L^\alpha K^\beta$ 中，$\frac{\partial Q}{\partial L} = A\alpha L^{\alpha-1} K^\beta$ 表示劳动力的边际产出，即在资本 $K$ 固定时，追加单位劳动力带来的产量增加。当 $\alpha = 0.7, \beta = 0.3$ 时，劳动力边际产出与 $L$ 成 $-0.3$ 次幂关系，体现边际递减规律。

**神经网络反向传播**：设损失函数 $L$ 依赖于权重 $w_{ij}$，反向传播通过链式法则计算 $\frac{\partial L}{\partial w_{ij}}$，这是 $L$ 对 $w_{ij}$ 的偏导数，其他所有权重在计算此偏导数时均被视为常数。整个梯度下降算法的每一步更新 $w_{ij} \leftarrow w_{ij} - \eta \frac{\partial L}{\partial w_{ij}}$ 都以偏导数计算为基础。

## 常见误区

**误区一：偏导数存在等于函数连续**
一元函数中导数存在蕴含连续，但多元函数的偏导数存在不蕴含连续，更不蕴含可微。函数 $f(x,y) = \frac{xy}{x^2+y^2}$（原点处为0）在原点处 $f_x(0,0) = f_y(0,0) = 0$，两个偏导数都存在，但函数在原点处不连续——沿直线 $y = x$ 趋近原点时极限为 $\frac{1}{2} \neq 0$。

**误区二：混合偏导数的求导顺序总可以互换**
初学者常默认 $\frac{\partial^2 f}{\partial x \partial y} = \frac{\partial^2 f}{\partial y \partial x}$ 无条件成立。实际上这需要克莱罗定理的连续性条件作保证。注意符号约定：$\frac{\partial^2 f}{\partial x \partial y}$ 表示先对 $y$ 后对 $x$（从右往左读），而 $f_{xy}$ 表示先对 $x$ 后对 $y$（从左往右读），两种记法的顺序恰好相反，这是另一个常见的符号混淆来源。

**误区三：偏导数即为曲面的斜率**
偏导数 $\frac{\partial f}{\partial x}\big|_{(x_0,y_0)}$ 仅是曲面 $z = f(x,y)$ 沿 $x$ 轴正方向的切线斜率，不代表曲面在该点沿任意方向的变化率。曲面沿任意单位向量方向的变化率需要用方向导数来描述，而方向导数可以通过偏导数（即梯度分量）与方向向量的内积来计算，这正是从偏导数过渡到梯度概念的桥梁。

## 知识关联

偏导数直接继承了一元函数导数的极限定义和运算法则——链式法则、乘积法则、商法则在固定其他变量后完全适用，因此一元导数是计算偏导数的操作前提。

掌握偏导数后，将 $n$ 个偏导数 $\left(\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, \ldots, \frac{\partial f}{\partial x_n}\right)$ 组合成向量即得到**梯度** $\nabla f$，梯度指向函数值增长最快的方向，其模长等于该最大增长率。梯度是方向导数计算的核心工具：函数沿单位向量 $\hat{u}$ 的方向导数等于 $\nabla f \cdot \hat{u}$。

在**无约束优化**中，多元函数极值的必要条件是所有偏导数同时为零，即 $\nabla f = \mathbf{0}$，这将优化问题转化为求解偏导数方程组。进一步判断极值类型需要计算二阶偏导数构成的**黑塞矩阵**（Hessian Matrix）$H_{ij} = \frac{\partial^2 f}{\partial x_i \partial x_j}$，分析其正定性，这是偏导数概念在最优化理论中的核心应用。
