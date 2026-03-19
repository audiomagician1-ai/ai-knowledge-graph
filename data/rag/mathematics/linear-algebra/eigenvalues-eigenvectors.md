---
id: "eigenvalues-eigenvectors"
name: "特征值与特征向量"
subdomain: "linear-algebra"
subdomain_name: "线性代数"
difficulty: 7
is_milestone: true
tags: ["里程碑"]
generated_at: "2026-03-19T08:00:26"
---

# 特征值与特征向量

## 概述

特征值与特征向量是线性代数领域中的里程碑概念，难度等级为 7/9。

特征方程、特征多项式

## 核心内容

若方阵 $A$ 满足 $A\mathbf{v} = \lambda\mathbf{v}$（$\mathbf{v} \neq \mathbf{0}$），则 $\lambda$ 为**特征值**，$\mathbf{v}$ 为**特征向量**。

**求解方法**：
1. 特征方程：$\det(A - \lambda I) = 0$
2. 对每个 $\lambda_i$，解 $(A - \lambda_i I)\mathbf{v} = \mathbf{0}$

**性质**：
- $\sum \lambda_i = \text{tr}(A)$（迹）
- $\prod \lambda_i = \det(A)$
- 对称矩阵的特征值全为实数

## 例题与练习

**例**: $A = \begin{pmatrix} 2 & 1 \\ 1 & 2 \end{pmatrix}$

$\det(A - \lambda I) = (2-\lambda)^2 - 1 = 0 \Rightarrow \lambda_1 = 3, \lambda_2 = 1$

## 关联知识

- **先修概念**: 行列式、线性变换
  - 学习本概念前，建议先掌握以上概念
- **后续概念**: 对角化、奇异值分解、二次型、正定矩阵
  - 掌握本概念后，可以继续学习以上进阶内容

## 学习建议

- **推荐学习路径**: 先回顾先修概念(行列式、线性变换)，然后系统学习特征值与特征向量的定义、公式和证明
- **实践方法**: 多做练习题，从基础计算到综合应用逐步提高
- **常见误区**: 注意公式的适用条件和推导细节，避免机械套用
- **预计学习时间**: 根据难度(7/9)，预计需要 21-35 小时
