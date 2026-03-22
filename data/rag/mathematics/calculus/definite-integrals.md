---
id: "definite-integrals"
concept: "定积分"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 6
is_milestone: false
tags: ["核心"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.94
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Stewart, James. Calculus: Early Transcendentals, 9th Ed., Ch.5"
  - type: "textbook"
    ref: "Spivak, Michael. Calculus, 4th Ed., Ch.13-14"
  - type: "academic"
    ref: "Bressoud, David. A Radical Approach to Real Analysis, 2nd Ed., MAA, 2007"
scorer_version: "scorer-v2.0"
---
# 定积分

## 概述

定积分（Definite Integral）是微积分两大核心概念之一（另一个是导数），用于计算**曲线下方的有向面积**、物理量的累积（位移、功、电荷）以及无穷多个无穷小量之和。

直觉上，从 a 到 b 对 f(x) 的定积分 = 将区间 [a,b] 分成 n 个极细的矩形条，每个矩形的面积是 f(x_i) * dx，然后将所有矩形面积求和并让宽度趋近于零。这个极限过程——**黎曼和的极限**——就是定积分的严格定义。

微积分基本定理（Newton-Leibniz）建立了定积分与不定积分（反导数）之间的桥梁：Integral from a to b of f(x)dx = F(b) - F(a)，其中 F'(x) = f(x)。这个定理被誉为"人类智慧最伟大的成就之一"（Spivak），因为它将求面积问题（几何/极限）转化为求反导数问题（代数）。

## 核心知识点

### 1. 黎曼和与定积分定义

**分割**：将 [a,b] 分成 n 个子区间 [x_{i-1}, x_i]，宽度 Delta_x_i = x_i - x_{i-1}。

**黎曼和**：S_n = Sum(i=1 to n) f(c_i) * Delta_x_i，其中 c_i 是 [x_{i-1}, x_i] 中任意一点。

**定积分**：当分割越来越细（所有 Delta_x_i -> 0）时，如果 S_n 趋向同一个极限值，则该极限就是定积分：
Integral(a to b) f(x) dx = lim(max Delta_x_i -> 0) S_n

**存在性**：如果 f 在 [a,b] 上连续，则定积分必定存在（Riemann 可积）。

### 2. 定积分的基本性质

| 性质 | 公式 | 直觉 |
|------|------|------|
| **线性** | Integral(af + bg) = a*Integral(f) + b*Integral(g) | 面积的加法和缩放 |
| **区间可加** | Integral(a to b) + Integral(b to c) = Integral(a to c) | 拼接区间 |
| **反向积分** | Integral(b to a) = -Integral(a to b) | 方向反转取负 |
| **保序性** | 若 f(x) >= g(x)，则 Integral(f) >= Integral(g) | 大函数面积更大 |
| **绝对值不等式** | |Integral(f)| <= Integral(|f|) | 有向面积可能相消 |

### 3. 微积分基本定理

**第一部分**（积分的导数）：
如果 F(x) = Integral(a to x) f(t) dt，则 F'(x) = f(x)

意义：积分作为上限的函数，其导数就是被积函数本身。积分与微分互为逆运算。

**第二部分**（Newton-Leibniz 公式）：
如果 F'(x) = f(x) 在 [a,b] 上成立，则
Integral(a to b) f(x) dx = F(b) - F(a)

**计算示例**：
Integral(0 to 1) x^2 dx = [x^3/3] from 0 to 1 = 1/3 - 0 = 1/3

不需要极限过程，只需找到反导数 F(x) = x^3/3 并代入端点。

### 4. 积分计算技巧

**换元法**（Substitution）：
令 u = g(x)，则 Integral f(g(x))*g'(x) dx = Integral f(u) du
- 更换积分上下限：x=a 时 u=g(a)，x=b 时 u=g(b)

**分部积分**（Integration by Parts）：
Integral(a to b) u dv = [uv](a to b) - Integral(a to b) v du
- 选择原则（LIATE）：对数 > 反三角 > 代数 > 三角 > 指数（选前面的做 u）

**特殊技巧**：
- 偶函数在 [-a, a] 上积分 = 2 * Integral(0 to a)
- 奇函数在 [-a, a] 上积分 = 0
- 周期函数在一个完整周期上积分与起点无关

### 5. 定积分的应用

| 应用 | 公式 | 物理含义 |
|------|------|---------|
| **面积** | Integral(a to b) |f(x)| dx | 曲线与 x 轴围成面积 |
| **位移** | Integral(t1 to t2) v(t) dt | 速度对时间的累积 |
| **做功** | Integral(x1 to x2) F(x) dx | 变力沿路径的能量传递 |
| **平均值** | (1/(b-a)) * Integral(a to b) f(x) dx | 函数在区间上的平均高度 |
| **弧长** | Integral(a to b) sqrt(1 + (f'(x))^2) dx | 曲线的总长度 |

## 关键原理分析

### 定积分的本质：无穷小量的求和

莱布尼兹用 Integral 符号（拉长的 S = Summa）和 dx（无穷小量）表达了定积分的核心思想：它是"连续求和"。离散求和 Sum 对应连续的 Integral，增量 Delta x 对应微分 dx。

### 数值积分

当被积函数没有封闭反导数时（如 e^(-x^2)），需要数值方法：
- **梯形法则**：将曲线下方近似为梯形
- **辛普森法则**：用抛物线段近似，精度更高（误差 ~ O(h^4)）
- 现代计算中，高斯求积法和自适应算法可以高效处理几乎所有一维积分

## 实践练习

**练习 1**：计算 Integral(0 to pi) sin(x) dx 的几何含义（面积），并用 Newton-Leibniz 公式验证。

**练习 2**：用分部积分计算 Integral(0 to 1) x * e^x dx。

## 常见误区

1. **"积分 = 面积"**：定积分是**有向面积**，x 轴下方的部分取负值。要求无向面积需加绝对值
2. **忘记换元时更换上下限**：换元后必须将积分上下限从 x 转换为 u
3. **忽略不连续点**：如果 f 在 [a,b] 内有不连续点，需要拆成多个区间分别积分