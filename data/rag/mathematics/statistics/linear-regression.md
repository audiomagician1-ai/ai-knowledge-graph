---
id: "linear-regression"
concept: "线性回归"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "数理统计"
difficulty: 6
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "An Introduction to Statistical Learning"
    authors: ["Gareth James", "Daniela Witten", "Trevor Hastie", "Robert Tibshirani"]
    year: 2021
    isbn: "978-1071614174"
  - type: "textbook"
    title: "The Elements of Statistical Learning"
    authors: ["Trevor Hastie", "Robert Tibshirani", "Jerome Friedman"]
    year: 2009
    isbn: "978-0387848570"
  - type: "textbook"
    title: "Pattern Recognition and Machine Learning"
    author: "Christopher M. Bishop"
    year: 2006
    isbn: "978-0387310732"
scorer_version: "scorer-v2.0"
---
# 线性回归

## 概述

线性回归（Linear Regression）是用线性函数建模因变量 y 与自变量 x 之间关系的统计方法——也是所有监督学习的起点。James et al. 在《An Introduction to Statistical Learning》（ISLR, 2021）中称其为"统计学习中最重要的工具，不是因为它最强大，而是因为理解了线性回归就理解了几乎所有更复杂方法的基础"。

线性回归的数学框架：给定 n 个观测 {(x₁,y₁), ..., (xₙ,yₙ)}，找到参数 β 使得 y ≈ β₀ + β₁x₁ + ... + βₚxₚ 最优。"最优"的标准是 **最小化残差平方和**（Ordinary Least Squares, OLS）。

## 简单线性回归

一个自变量 x 预测 y：

```
模型：y = β₀ + β₁x + ε
      β₀ = 截距（intercept）
      β₁ = 斜率（slope）
      ε  = 随机误差项，假设 ε ~ N(0, σ²)

OLS 解（闭式）：
      β₁ = Σ(xᵢ - x̄)(yᵢ - ȳ) / Σ(xᵢ - x̄)²
      β₀ = ȳ - β₁x̄

等价矩阵形式：
      β = (X^T X)^{-1} X^T y
```

**几何解释**：OLS 是将 y 投影到 X 的列空间上——β 使得残差向量 e = y - Xβ 与列空间正交。

## 多元线性回归

p 个自变量：

```
y = β₀ + β₁x₁ + β₂x₂ + ... + βₚxₚ + ε

矩阵形式：y = Xβ + ε
  X: n×(p+1) 设计矩阵（含截距列）
  β: (p+1)×1 参数向量
  
OLS 解：β̂ = (X^T X)^{-1} X^T y
```

**计算复杂度**：直接求逆 O(p³)。当 p > 10,000 时应使用梯度下降或 QR 分解。

## 模型评估指标

| 指标 | 公式 | 含义 | 范围 |
|------|------|------|------|
| R² | 1 - SS_res/SS_tot | 模型解释的方差比例 | [0,1]，越大越好 |
| Adjusted R² | 1 - (1-R²)(n-1)/(n-p-1) | 惩罚多余特征的 R² | 可为负 |
| MSE | Σ(yᵢ-ŷᵢ)²/n | 平均预测误差 | ≥0，越小越好 |
| RMSE | √MSE | 与 y 同单位 | ≥0 |
| MAE | Σ|yᵢ-ŷᵢ|/n | 对异常值鲁棒 | ≥0 |

**R² 的陷阱**：添加任何自变量都会使 R² 增大（即使该变量无关）。始终使用 Adjusted R² 比较不同特征数的模型。

## OLS 的五大假设（Gauss-Markov 条件）

| 假设 | 含义 | 违反后果 | 检验方法 |
|------|------|---------|---------|
| 线性关系 | E[y|x] = Xβ | 系统性偏差 | 残差图 vs 拟合值 |
| 独立性 | 观测之间独立 | 标准误低估 | Durbin-Watson 检验 |
| 同方差性 | Var(ε) = σ² (常数) | 不高效估计 | Breusch-Pagan 检验 |
| 正态性 | ε ~ N(0, σ²) | 假设检验不可靠 | Q-Q 图, Shapiro-Wilk |
| 无多重共线性 | X 列之间线性无关 | β 估计不稳定 | VIF > 10 则严重 |

当假设被违反时的修复方案：
- 非线性 → 添加多项式特征 / 使用非线性模型
- 异方差 → 加权最小二乘（WLS）/ 稳健标准误
- 多重共线性 → Ridge/Lasso 正则化 / 删除冗余特征

## 正则化：Ridge 与 Lasso

| 方法 | 目标函数 | 惩罚项 | 效果 |
|------|---------|--------|------|
| OLS | min ‖y-Xβ‖² | 无 | 基准 |
| Ridge (L2) | min ‖y-Xβ‖² + λ‖β‖² | L2 范数 | 缩小系数，不置零 |
| Lasso (L1) | min ‖y-Xβ‖² + λ‖β‖₁ | L1 范数 | 缩小+稀疏化（特征选择） |
| Elastic Net | min ‖y-Xβ‖² + λ₁‖β‖₁ + λ₂‖β‖² | L1+L2 | 兼得两者优点 |

**λ 选择**：通过交叉验证（Cross-Validation）选择使测试误差最小的 λ。ISLR（2021）推荐 10-fold CV。

## Python 实现

```python
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score, mean_squared_error

# 简单线性回归
model = LinearRegression()
model.fit(X_train, y_train)
print(f"Intercept: {model.intercept_:.3f}")
print(f"Coefficients: {model.coef_}")
print(f"R²: {r2_score(y_test, model.predict(X_test)):.4f}")

# Ridge 回归 + 交叉验证
from sklearn.linear_model import RidgeCV
ridge = RidgeCV(alphas=[0.01, 0.1, 1, 10, 100], cv=10)
ridge.fit(X_train, y_train)
print(f"Best alpha: {ridge.alpha_}")

# Lasso 回归（自动特征选择）
lasso = Lasso(alpha=0.1)
lasso.fit(X_train, y_train)
selected = np.sum(lasso.coef_ != 0)
print(f"Selected features: {selected}/{X_train.shape[1]}")
```

## 线性回归的位置：从统计到机器学习

```
线性回归
  ├─ 加正则化 → Ridge / Lasso / Elastic Net
  ├─ 加多项式特征 → 多项式回归
  ├─ 改变损失函数 → 分位数回归 / Huber 回归
  ├─ y 为二值 → Logistic 回归（分类）
  ├─ 加核技巧 → 核回归 / SVM 回归
  └─ 多层+非线性 → 神经网络（y = f(Wx+b) 的堆叠）
```

所有这些方法的起点都是线性回归——理解 OLS 的闭式解、正则化的几何含义、假设检验，就能理解整个监督学习体系。

## 常见误区

1. **相关 ≠ 因果**：线性回归发现 x 和 y 有线性关系 ≠ x 导致 y。经典反例：冰淇淋销量与溺水死亡正相关——真正原因是夏天
2. **R² 高 = 好模型**：R²=0.95 但所有残差都呈U形 = 模型结构错误（非线性关系用线性拟合）。**永远要看残差图**
3. **外推**：在训练数据范围外预测。如果训练数据 x ∈ [0,100]，用模型预测 x=500 是极其危险的——线性关系不保证在范围外成立

## 知识衔接

### 先修知识
- **概率论基础** — 正态分布、期望、方差
- **线性代数** — 矩阵运算、向量空间、投影

### 后续学习
- **逻辑回归** — 线性回归 + sigmoid → 分类
- **多项式回归** — 非线性拟合的最简扩展
- **正则化方法** — Ridge/Lasso 的理论和实践
- **假设检验** — t-test, F-test 在回归中的应用
- **贝叶斯线性回归** — 概率视角的线性回归

## 参考文献

1. James, G. et al. (2021). *An Introduction to Statistical Learning* (2nd ed.). Springer. ISBN 978-1071614174
2. Hastie, T., Tibshirani, R. & Friedman, J. (2009). *The Elements of Statistical Learning* (2nd ed.). Springer. ISBN 978-0387848570
3. Bishop, C.M. (2006). *Pattern Recognition and Machine Learning*. Springer. ISBN 978-0387310732
4. Freedman, D.A. (2009). *Statistical Models: Theory and Practice* (2nd ed.). Cambridge University Press. ISBN 978-0521743853
