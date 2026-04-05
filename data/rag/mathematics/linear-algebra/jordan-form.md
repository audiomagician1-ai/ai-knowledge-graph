---
id: "jordan-form"
concept: "Jordan标准形"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 9
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Jordan标准形

## 概述

Jordan标准形是线性代数中对矩阵进行最精细分类的规范形式。给定一个 $n \times n$ 复矩阵 $A$，即使 $A$ 不可对角化，也必然相似于一个由若干**Jordan块**拼成的分块对角矩阵，这个矩阵就称为 $A$ 的Jordan标准形，记为 $J$。Jordan标准形定理保证：在复数域上，任意方阵都有且仅有（在不计Jordan块排列顺序的意义下唯一）一个Jordan标准形。

Jordan标准形由法国数学家Camille Jordan于1870年在其著作《代换与代数方程论》（*Traité des substitutions et des équations algébriques*）中系统建立。Jordan块对应于特征多项式有重根却无法对角化的情形——这正是对角化理论留下的"盲区"。从应用角度看，常微分方程组 $\dot{x} = Ax$ 的完整解法依赖Jordan标准形，因为 $e^{At}$ 的计算在矩阵不可对角化时必须借助Jordan结构展开。

## 核心原理

### Jordan块的定义

$k$ 阶Jordan块 $J_k(\lambda)$ 是一个 $k \times k$ 矩阵，主对角线全为特征值 $\lambda$，主对角线**正上方**的上次对角线全为 $1$，其余位置全为 $0$：

$$
J_k(\lambda) = \begin{pmatrix} \lambda & 1 & 0 & \cdots & 0 \\ 0 & \lambda & 1 & \cdots & 0 \\ \vdots & & \ddots & \ddots & \vdots \\ 0 & 0 & \cdots & \lambda & 1 \\ 0 & 0 & \cdots & 0 & \lambda \end{pmatrix}
$$

$J_k(\lambda)$ 的特征多项式为 $(\lambda_0 - \lambda)^k$（其中 $\lambda_0$ 是块对应的特征值），最小多项式也为 $(\lambda - \lambda_0)^k$，且其**特征空间维数恰好为 1**——这是与可对角化情形最根本的区别。当 $k=1$ 时，$J_1(\lambda)$ 退化为标量 $(\lambda)$，即普通的对角元。

### Jordan标准形的整体结构

矩阵 $A$ 的Jordan标准形由若干Jordan块直和组成：

$$
J = J_{k_1}(\lambda_1) \oplus J_{k_2}(\lambda_2) \oplus \cdots \oplus J_{k_r}(\lambda_r)
$$

其中 $k_1 + k_2 + \cdots + k_r = n$。关键参数的含义如下：

- **$\lambda_i$ 的代数重数**等于所有以 $\lambda_i$ 为对角元的Jordan块的阶数之和。  
- **$\lambda_i$ 的几何重数**（即特征空间 $\ker(A - \lambda_i I)$ 的维数）等于以 $\lambda_i$ 为对角元的Jordan块**个数**。  
- **最小多项式**中 $(\lambda - \lambda_i)$ 的幂次等于所有以 $\lambda_i$ 为对角元的Jordan块中**最大阶数**。

可对角化矩阵的Jordan标准形就是对角矩阵本身，即每个Jordan块均为 $1 \times 1$ 块。

### 广义特征向量与Jordan基

要实际构造Jordan标准形所对应的可逆变换矩阵 $P$（使 $P^{-1}AP = J$），需要构造**广义特征向量链**。对特征值 $\lambda_i$，定义广义特征空间 $K_{\lambda_i} = \ker(A - \lambda_i I)^{n}$。广义特征向量链（Jordan链）的形式为：

$$
(A - \lambda_i I)v_k = v_{k-1}, \quad (A - \lambda_i I)v_{k-1} = v_{k-2}, \quad \cdots, \quad (A - \lambda_i I)v_1 = 0
$$

其中 $v_1$ 是普通特征向量，$v_2, \ldots, v_k$ 是各阶广义特征向量。将 $k$ 阶Jordan块对应的链 $(v_1, v_2, \ldots, v_k)$ 按列排入 $P$，所得 $P$ 的列空间恰好是广义特征空间的一组基。

### 不变因子与初等因子

Jordan标准形与**Smith标准形**紧密相关。矩阵 $\lambda I - A$ 作为多项式矩阵有一组不变因子 $d_1(\lambda) \mid d_2(\lambda) \mid \cdots \mid d_n(\lambda)$；将每个 $d_i(\lambda)$ 分解为不可约因子幂次之积，得到的各幂次因子称为**初等因子**。每一个初等因子 $(\lambda - \lambda_i)^{k}$ 精确对应Jordan标准形中的一个 $k$ 阶Jordan块 $J_k(\lambda_i)$。两矩阵相似的充要条件是它们具有相同的全部初等因子（等价地，相同的特征矩阵的Smith标准形）。

## 实际应用

**矩阵函数的计算**：计算 $e^{At}$ 时，若 $A$ 不可对角化，则通过 $A = PJP^{-1}$ 将问题转化为 $e^{Jt}$。对于 $k$ 阶Jordan块 $J_k(\lambda)$，有

$$
e^{J_k(\lambda)t} = e^{\lambda t} \begin{pmatrix} 1 & t & \frac{t^2}{2!} & \cdots & \frac{t^{k-1}}{(k-1)!} \\ 0 & 1 & t & \cdots & \frac{t^{k-2}}{(k-2)!} \\ \vdots & & \ddots & \ddots & \vdots \\ 0 & \cdots & 0 & 1 & t \\ 0 & \cdots & 0 & 0 & 1 \end{pmatrix}
$$

上三角中出现 $t^j/j!$ 的项正是Jordan块中那条"1"所带来的非对角贡献。

**线性ODE系统**：若 $A$ 有二重特征值 $\lambda_0$ 且几何重数为1（即有一个 $2 \times 2$ Jordan块），则方程组 $\dot{x}=Ax$ 的解包含形如 $te^{\lambda_0 t}$ 的项；若 $A$ 可对角化则只有 $e^{\lambda_0 t}$ 项。Jordan结构直接决定了解的增长模式。

**幂零矩阵的分类**：幂零矩阵（满足 $N^k = 0$）的Jordan标准形由以 $0$ 为对角元的Jordan块构成。例如，$5 \times 5$ 幂零矩阵的Jordan类型与整数 $5$ 的**整数分拆**一一对应：$(5), (4,1), (3,2), (3,1,1), (2,2,1), (2,1,1,1), (1,1,1,1,1)$ 共7种，每种对应不同的Jordan块大小组合。

## 常见误区

**误区一：实矩阵的Jordan标准形在实数域上总存在**。Jordan标准形定理在**复数域**成立。对于实矩阵，若存在虚特征值（如特征多项式含不可约实二次因子），则其复Jordan标准形含复数对角元，在实数域内无法实现。实数域上类似角色由**实Jordan标准形**（或称实标准形）承担，以 $2\times2$ 旋转-伸缩块取代复数对角元。

**误区二：特征多项式相同则矩阵相似**。特征多项式相同只保证代数重数相同，不能确定Jordan块的大小分布。例如，$3\times3$ 矩阵特征多项式均为 $(\lambda-2)^3$ 时，有三种情形：$J_3(2)$（一个 $3$ 阶块）、$J_2(2)\oplus J_1(2)$（一个 $2$ 阶加一个 $1$ 阶块）、$J_1(2)\oplus J_1(2)\oplus J_1(2)$（三个 $1$ 阶块，即 $2I$）——三者互不相似，必须通过**最小多项式**或各阶零化空间维数 $\dim\ker(A-\lambda I)^k$ 才能区分。

**误区三：最小多项式决定唯一Jordan标准形**。最小多项式给出了每个特征值对应的最大Jordan块阶数，但不能确定有几个最大阶块，也不能确定其余块的大小。需要逐步计算 $\dim\ker(A-\lambda_i I)^j$（对 $j=1,2,\ldots$）的递增量，才能唯一确定Jordan块的全部大小。

## 知识关联

Jordan标准形是对角化理论的直接推广：对角化要求每个特征值的几何重数等于代数重数（即所有Jordan块均为 $1\times1$），而Jordan标准形去掉了这一限制，以广义特征向量链填补了缺失的基向量。学习Jordan标准形时，**最小多项式**和**Cayley-Hamilton定理**（矩阵满足自身特征多项式 $p(A)=0$）是不可缺少的工具：最小多项式揭示Jordan块的最大阶数，Cayley-Hamilton定理则保证广义特征空间可以覆盖整个向量空间。Jordan标准形还与**有理标准形**（Frobenius标准形）形成互补——后者在有理数域上可行，前者在代数闭域（如复