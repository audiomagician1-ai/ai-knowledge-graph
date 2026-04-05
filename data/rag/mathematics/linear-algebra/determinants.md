---
id: "determinants"
concept: "行列式"
domain: "mathematics"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 6
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 6
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

# 行列式

## 概述

行列式（Determinant）是一个将方阵映射为标量的函数，记作 $\det(A)$ 或 $|A|$。对于 $n \times n$ 矩阵 $A$，其行列式是一个单一数值，编码了该矩阵所代表的线性变换对空间体积的缩放比例。若 $\det(A) = 0$，则矩阵 $A$ 奇异（不可逆）；若 $\det(A) \neq 0$，则 $A$ 可逆。

行列式的历史可追溯至17世纪。日本数学家关孝和（Seki Takakazu）约在1683年首次系统地使用类似行列式的方法求解联立方程，莱布尼茨（Leibniz）也在1693年独立提出了相关概念。"Determinant"这一术语由柯西（Cauchy）于1812年正式确立，他同时给出了行列式的乘法定理。

行列式的重要性在于它是判断线性方程组是否有唯一解的判据，同时出现在特征多项式 $\det(A - \lambda I) = 0$ 中，这是求解特征值的基本方程。几何上，$|\det(A)|$ 等于矩阵各列向量构成的平行多面体的体积，正负号则反映了方向是否保持（定向）。

---

## 核心原理

### 低阶行列式的直接计算

**2阶行列式**定义为：
$$\det\begin{pmatrix} a & b \\ c & d \end{pmatrix} = ad - bc$$
这是主对角线乘积减去副对角线乘积。

**3阶行列式**可用萨鲁斯法则（Sarrus' Rule）计算：将矩阵前两列附写在右侧，沿3条正对角线之积求和，再减去3条负对角线之积。注意：萨鲁斯法则**仅适用于3阶**，不可推广至4阶及以上。

### Leibniz公式与置换展开

$n$ 阶行列式的精确定义由Leibniz公式给出：
$$\det(A) = \sum_{\sigma \in S_n} \text{sgn}(\sigma) \prod_{i=1}^{n} a_{i,\sigma(i)}$$
其中求和遍历所有 $n!$ 种排列 $\sigma$，$\text{sgn}(\sigma)$ 为排列的符号（偶排列为 $+1$，奇排列为 $-1$）。对于 $3 \times 3$ 矩阵，共有 $3! = 6$ 项；对于 $4 \times 4$ 矩阵，共有 $4! = 24$ 项，计算量随阶数阶乘增长，因此实用中多采用展开法。

### 余子式展开（拉普拉斯展开）

按第 $i$ 行展开的公式为：
$$\det(A) = \sum_{j=1}^{n} a_{ij} \cdot C_{ij}$$
其中代数余子式 $C_{ij} = (-1)^{i+j} M_{ij}$，$M_{ij}$ 是删去第 $i$ 行第 $j$ 列后形成的 $(n-1)$ 阶子矩阵的行列式（余子式）。实际计算中，应选择含零元素最多的行或列展开，以减少计算量。

### 行列式的关键性质

以下性质是行列式计算的实用工具，每条均与矩阵乘法结果密切相关：

- **多线性**：对某一行进行数乘 $k$，行列式乘以 $k$。因此 $\det(kA) = k^n \det(A)$（$n$ 为阶数）。
- **交替性**：交换任意两行（列），行列式变号。
- **乘法定理**：$\det(AB) = \det(A) \cdot \det(B)$，这是行列式最重要的运算性质之一。
- **转置不变**：$\det(A^T) = \det(A)$，因此行的所有性质对列同样成立。
- **三角矩阵**：上三角或下三角矩阵的行列式等于主对角线元素之积，即 $\det(A) = \prod_{i=1}^{n} a_{ii}$。

---

## 实际应用

**判断线性方程组的解的情况**：对于 $n$ 元线性方程组 $A\mathbf{x} = \mathbf{b}$，当 $\det(A) \neq 0$ 时，方程组恰有唯一解，可通过克莱姆法则（Cramer's Rule）明确写出每个 $x_i = \det(A_i) / \det(A)$，其中 $A_i$ 是将 $A$ 第 $i$ 列替换为 $\mathbf{b}$ 后的矩阵。

**计算平面/空间面积与体积**：在二维中，以向量 $\mathbf{u} = (a, b)$ 和 $\mathbf{v} = (c, d)$ 为边的平行四边形面积等于 $|ad - bc|$。在三维中，三个向量构成的平行六面体体积等于 $3 \times 3$ 行列式的绝对值，这在计算机图形学中的多边形面积计算中被频繁使用。

**求逆矩阵的伴随矩阵公式**：当 $\det(A) \neq 0$ 时，$A^{-1} = \frac{1}{\det(A)} \text{adj}(A)$，其中伴随矩阵 $\text{adj}(A)$ 的 $(i,j)$ 元素为代数余子式 $C_{ji}$（注意转置关系）。

---

## 常见误区

**误区一：$\det(A + B) = \det(A) + \det(B)$**
这是错误的。行列式对矩阵加法**不具备线性**。正确的乘法定理是 $\det(AB) = \det(A)\det(B)$，但加法没有类似的分拆公式。例如取 $A = I$，$B = -I$，则 $\det(A+B) = \det(0) = 0$，但 $\det(A) + \det(B) = 1 + (-1)^n$，两者在 $n$ 为奇数时才相等，偶数时不等。

**误区二：混淆 $\det(kA)$ 与 $k \cdot \det(A)$**
由于多线性，数乘 $k$ 作用于整个 $n \times n$ 矩阵时，每一行都被乘以 $k$，共 $n$ 行，因此 $\det(kA) = k^n \det(A)$，而非 $k \cdot \det(A)$。例如 $3 \times 3$ 矩阵 $A$ 满足 $\det(2A) = 8\det(A)$，而非 $2\det(A)$。

**误区三：萨鲁斯法则推广至高阶矩阵**
萨鲁斯法则是3阶行列式的快速记忆技巧，但对于 $4 \times 4$ 及以上矩阵，沿对角线累加的"斜线法"将给出错误结果。高阶行列式必须使用拉普拉斯展开或高斯消元后利用三角矩阵公式计算。

---

## 知识关联

**前置知识**：矩阵乘法是理解乘法定理 $\det(AB) = \det(A)\det(B)$ 的基础，同时余子式展开涉及对子矩阵反复计算行列式，需要熟悉矩阵的分块与索引操作。

**后续概念**：行列式直接支撑三个关键主题。**逆矩阵**的存在性完全由 $\det(A) \neq 0$ 判定，且伴随矩阵公式将逆矩阵的计算化为行列式运算；**克莱姆法则**将线性方程组的每个未知量表达为两个行列式之比；**特征值**由特征多项式 $p(\lambda) = \det(A - \lambda I)$ 的根给出，这是一个关于 $\lambda$ 的 $n$ 次多项式，其系数全部由 $A$ 的行列式及其子矩阵行列式构成。