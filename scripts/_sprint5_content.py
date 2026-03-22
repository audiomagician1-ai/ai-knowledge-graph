#!/usr/bin/env python3
"""Sprint 5 content for batch rewrite."""

DOCUMENTS = [

# ═══════════════════════════════════════════════════════════════
# 1. 同余理论
# ═══════════════════════════════════════════════════════════════
{
"path": r"mathematics\number-theory\congruences.md",
"sources_yaml": '''sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Modular arithmetic"
    url: "https://en.wikipedia.org/wiki/Modular_arithmetic"
  - type: "textbook-reference"
    ref: "Hardy & Wright. An Introduction to the Theory of Numbers, 6th ed."''',
"body": r'''# 同余理论

## 概述

同余（Congruence）是数论中描述整数除法余数关系的核心概念，由德国数学家卡尔·弗里德里希·高斯（Carl Friedrich Gauss）于1801年在其里程碑式著作《算术研究》（*Disquisitiones Arithmeticae*）中系统化提出。

**定义**：对于整数 $a$、$b$ 和正整数 $m$，若 $m$ 整除 $(a - b)$，则称 $a$ 与 $b$ 模 $m$ 同余，记作：

$$a \equiv b \pmod{m}$$

等价地，$a$ 和 $b$ 除以 $m$ 的余数相同。例如 $17 \equiv 2 \pmod{5}$，因为 $17 - 2 = 15$ 是5的倍数。

同余理论是现代密码学（RSA算法）、计算机科学（哈希函数）和代数数论的基石。

## 核心原理

### 同余的基本性质

同余关系是等价关系，满足三大性质：
- **自反性**：$a \equiv a \pmod{m}$
- **对称性**：若 $a \equiv b \pmod{m}$，则 $b \equiv a \pmod{m}$
- **传递性**：若 $a \equiv b$ 且 $b \equiv c \pmod{m}$，则 $a \equiv c \pmod{m}$

**运算兼容性**：若 $a \equiv b$ 且 $c \equiv d \pmod{m}$，则：
- $a + c \equiv b + d \pmod{m}$（加法）
- $a \cdot c \equiv b \cdot d \pmod{m}$（乘法）
- $a^n \equiv b^n \pmod{m}$（幂运算）

**注意**：除法不能直接运算。$a \cdot c \equiv b \cdot c \pmod{m}$ 仅当 $\gcd(c, m) = 1$ 时才能消去 $c$。

### 剩余类与模运算

模 $m$ 的全体整数被划分为 $m$ 个**剩余类**（residue classes）：$\{[0], [1], [2], \ldots, [m-1]\}$。这些剩余类构成**整数模 m 的环** $\mathbb{Z}/m\mathbb{Z}$（或简记 $\mathbb{Z}_m$）。

当 $m$ 为素数 $p$ 时，$\mathbb{Z}_p$ 不仅是环，还是**域**——每个非零元素都有乘法逆元。例如在 $\mathbb{Z}_7$ 中，$3 \times 5 = 15 \equiv 1 \pmod{7}$，所以 $3^{-1} \equiv 5 \pmod{7}$。

### 费马小定理与欧拉定理

**费马小定理**（Fermat's Little Theorem, 1640年）：若 $p$ 为素数且 $\gcd(a, p) = 1$，则 $a^{p-1} \equiv 1 \pmod{p}$。

例如：$2^{6} = 64 \equiv 1 \pmod{7}$。

**欧拉推广**：对任意正整数 $m$，若 $\gcd(a, m) = 1$，则 $a^{\varphi(m)} \equiv 1 \pmod{m}$，其中欧拉函数 $\varphi(m)$ 表示 $1$ 到 $m$ 中与 $m$ 互素的整数个数。当 $m = p$（素数）时 $\varphi(p) = p - 1$，退化为费马小定理。

### 中国剩余定理

**中国剩余定理**（Chinese Remainder Theorem，CRT）最早见于南宋数学家秦九韶1247年的《数书九章》中"物不知其数"问题：有物不知其数，三三数之剩二，五五数之剩三，七七数之剩二，问物几何？

形式化表述：若 $m_1, m_2, \ldots, m_k$ 两两互素，则同余方程组 $x \equiv a_i \pmod{m_i}$ 在模 $M = m_1 m_2 \cdots m_k$ 下有唯一解。

## 实际应用

1. **RSA加密算法**：公钥密码学的基础。选两个大素数 $p, q$，计算 $n = pq$。加密：$c \equiv m^e \pmod{n}$；解密利用 $m \equiv c^d \pmod{n}$，其中 $ed \equiv 1 \pmod{\varphi(n)}$。RSA的安全性依赖于大整数分解的计算困难性。

2. **哈希函数**：计算机中常用 $h(k) = k \bmod m$ 作为哈希函数，将键值映射到 $[0, m-1]$ 的桶中。

3. **ISBN校验码**：ISBN-13的校验位使用模10运算验证条码正确性。

## 常见误区

1. **"同余可以随意做除法"**：$6 \equiv 0 \pmod{6}$ 但不能两边除以2得出 $3 \equiv 0 \pmod{6}$（事实上 $3 \not\equiv 0 \pmod{6}$）。除法仅在除数与模数互素时有效。

2. **"模运算结果总是正数"**：数学定义中 $-1 \equiv 4 \pmod{5}$，但不同编程语言对负数取模的结果不同（Python返回非负值，C++可能返回负值）。

3. **"费马小定理对所有整数成立"**：条件 $\gcd(a, p) = 1$ 不可省略。$0^{p-1} = 0 \not\equiv 1 \pmod{p}$。

## 知识关联

**先修概念**：整除性、最大公约数（欧几里得算法）、素数基础。

**后续发展**：同余理论直接引向二次互反律（Gauss称之为"算术的宝石"）、椭圆曲线上的模运算（椭圆曲线密码学ECC的基础）、以及抽象代数中的群论和环论。

## 参考来源

- [Modular arithmetic - Wikipedia](https://en.wikipedia.org/wiki/Modular_arithmetic)
- Hardy, G.H. & Wright, E.M. *An Introduction to the Theory of Numbers*, 6th ed., Oxford University Press.
- Gauss, C.F. *Disquisitiones Arithmeticae* (1801).
'''
},

# ═══════════════════════════════════════════════════════════════
# 2. 三角形
# ═══════════════════════════════════════════════════════════════
{
"path": r"mathematics\geometry\triangles.md",
"sources_yaml": '''sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Triangle"
    url: "https://en.wikipedia.org/wiki/Triangle"
  - type: "textbook-reference"
    ref: "Euclid. Elements, Book I"''',
"body": r'''# 三角形

## 概述

三角形（Triangle）是由三条线段首尾相连构成的最简单多边形，也是欧几里得几何中最基本的图形。三角形的研究可追溯到古埃及和古巴比伦时期（约公元前2000年），而系统化的三角形理论由欧几里得在《几何原本》（*Elements*，约公元前300年）的第一卷中建立。

三角形有三个顶点、三条边和三个内角，内角和恒为 $180°$（即 $\pi$ 弧度）。这一定理是欧几里得几何的标志性结论，在非欧几何中不成立——球面三角形的内角和大于180°，双曲面三角形的内角和小于180°。

## 核心原理

### 分类体系

**按角分类**：
| 类型 | 定义 | 特征 |
|------|------|------|
| 锐角三角形 | 三个角均 < 90° | 外接圆圆心在三角形内部 |
| 直角三角形 | 有一个角 = 90° | 满足勾股定理 $a^2 + b^2 = c^2$ |
| 钝角三角形 | 有一个角 > 90° | 外接圆圆心在三角形外部 |

**按边分类**：
- **等边三角形**（equilateral）：三边相等，三角均为60°
- **等腰三角形**（isosceles）：至少两边相等，底角相等
- **不等边三角形**（scalene）：三边互不相等

### 核心定理

**勾股定理**（Pythagorean Theorem）：直角三角形中，$a^2 + b^2 = c^2$，其中 $c$ 为斜边。该定理至少有370种已知证明方法。最早的严格证明出现在欧几里得《原本》命题I.47。勾股数的例子：$(3,4,5)$、$(5,12,13)$、$(8,15,17)$。

**正弦定理**：$\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R$，其中 $R$ 为外接圆半径。

**余弦定理**：$c^2 = a^2 + b^2 - 2ab\cos C$，这是勾股定理的推广——当 $C = 90°$ 时，$\cos C = 0$，退化为勾股定理。

### 面积公式

三角形面积有多种计算方式：

1. **基本公式**：$S = \frac{1}{2} \times \text{底} \times \text{高}$
2. **两边夹角**：$S = \frac{1}{2}ab\sin C$
3. **海伦公式**（Heron's Formula，约公元60年）：$S = \sqrt{s(s-a)(s-b)(s-c)}$，其中 $s = \frac{a+b+c}{2}$ 为半周长
4. **坐标公式**：给定三顶点 $(x_1,y_1), (x_2,y_2), (x_3,y_3)$，$S = \frac{1}{2}|x_1(y_2-y_3) + x_2(y_3-y_1) + x_3(y_1-y_2)|$

### 特殊点与线

- **重心**（centroid）：三条中线交点，坐标为三顶点坐标的算术平均
- **外心**（circumcenter）：三条中垂线交点，到三顶点等距
- **内心**（incenter）：三条角平分线交点，到三边等距
- **垂心**（orthocenter）：三条高线交点

**欧拉线**（Euler Line, 1767年）：任意三角形的重心、外心和垂心共线，且重心将外心到垂心的线段分为 $1:2$。等边三角形中四心重合，无欧拉线。

## 实际应用

1. **三角测量法**：测量难以直接到达的距离。例如，通过在地面两点测量山顶的仰角，结合两点间距，用正弦定理计算山高。

2. **计算机图形学**：所有3D模型的表面由三角形网格（triangle mesh）组成，因为三角形是唯一保证共面的多边形。现代GPU每秒可渲染数十亿个三角形。

3. **结构工程**：三角形是唯一具有**刚性**的多边形——给定三边长度，三角形的形状唯一确定。桥梁和屋架大量使用三角形桁架结构。

## 常见误区

1. **"三角形内角和在任何情况下都是180°"**：仅在欧几里得平面几何中成立。球面上三角形内角和为 $180° + \frac{S}{R^2} \times \frac{180°}{\pi}$（$S$为球面三角形面积，$R$为球半径）。

2. **"勾股定理的逆定理不成立"**：实际上逆定理成立——若 $a^2 + b^2 = c^2$，则三角形必为直角三角形（欧几里得《原本》命题I.48）。

3. **"任意三条线段都能构成三角形"**：必须满足**三角不等式**：任意两边之和大于第三边。即 $a + b > c$，$a + c > b$，$b + c > a$。

## 知识关联

**先修概念**：角的度量、线段长度、面积概念、勾股定理（初步了解）。

**后续发展**：三角形理论通向三角函数（正弦、余弦的几何定义）、向量几何（用向量表示三角形运算）、以及计算几何（凸包算法的基础构件）。在拓扑学中，三角剖分（triangulation）是研究曲面的核心方法。

## 参考来源

- [Triangle - Wikipedia](https://en.wikipedia.org/wiki/Triangle)
- Euclid. *Elements*, Book I (c. 300 BC), Propositions I.47-I.48.
- Coxeter, H.S.M. & Greitzer, S.L. *Geometry Revisited*, MAA (1967).
'''
},

# ═══════════════════════════════════════════════════════════════
# 3. 素数
# ═══════════════════════════════════════════════════════════════
{
"path": r"mathematics\number-theory\primes.md",
"sources_yaml": '''sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Prime number"
    url: "https://en.wikipedia.org/wiki/Prime_number"
  - type: "textbook-reference"
    ref: "Hardy & Wright. An Introduction to the Theory of Numbers, 6th ed."''',
"body": r'''# 素数

## 概述

素数（Prime Number）是大于1的自然数中，除了1和自身外没有其他正因数的数。前几个素数为：2, 3, 5, 7, 11, 13, 17, 19, 23, 29, ...。特别地，**2是唯一的偶素数**。

素数的研究始于古希腊。欧几里得在《几何原本》第九卷命题20中证明了**素数有无穷多个**——这是数学史上最优美的证明之一。假设素数有限，设为 $p_1, p_2, \ldots, p_n$，考虑 $N = p_1 p_2 \cdots p_n + 1$，则 $N$ 不能被任何 $p_i$ 整除（余数为1），因此 $N$ 要么自身是素数，要么有一个不在列表中的素因子，矛盾。

素数是**算术基本定理**（Fundamental Theorem of Arithmetic）的核心：任何大于1的自然数都可以唯一分解为素数的乘积（不计顺序）。例如 $360 = 2^3 \times 3^2 \times 5$。

## 核心原理

### 素数判定

**试除法**：判定 $n$ 是否为素数，只需检查从2到 $\lfloor\sqrt{n}\rfloor$ 的所有整数是否整除 $n$。原理：若 $n = ab$ 且 $a \leq b$，则 $a \leq \sqrt{n}$。

**埃拉托斯特尼筛法**（Sieve of Eratosthenes，约公元前230年）：列出2到 $N$ 的所有整数，从2开始逐步划去每个素数的倍数，剩余的即为素数。找到 $N$ 以内的所有素数，时间复杂度为 $O(N \log \log N)$。

**Miller-Rabin检验**：现代概率性素性测试，对于大数（数百位）效率远高于试除法。2002年，Agrawal-Kayal-Saxena（AKS）算法证明素性测试可以在多项式时间内确定性完成。

### 素数分布

**素数定理**（Prime Number Theorem, 1896年Hadamard和de la Vallée-Poussin独立证明）：不超过 $x$ 的素数个数 $\pi(x)$ 近似为：

$$\pi(x) \sim \frac{x}{\ln x}$$

更精确地，$\pi(x) \sim \text{Li}(x) = \int_2^x \frac{dt}{\ln t}$。例如，$\pi(10^9) = 50,847,534$，而 $10^9 / \ln(10^9) \approx 48,254,942$（误差约5%）。

### 特殊素数

- **孪生素数**：相差2的素数对，如 $(11, 13)$、$(29, 31)$、$(71, 73)$。孪生素数猜想（是否有无穷多对）至今未解决。2013年张益唐证明存在无穷多个间距不超过7000万的素数对，陶哲轩等人将此上界缩小至246。
- **梅森素数**：形如 $2^p - 1$ 的素数（$p$ 本身也必须是素数）。截至2024年12月，已知最大素数为第52个梅森素数 $2^{136,279,841} - 1$（41,024,320位数），由GIMPS项目发现。
- **费马素数**：形如 $2^{2^n} + 1$ 的素数。已知仅5个：$3, 5, 17, 257, 65537$（$n = 0,1,2,3,4$）。

## 实际应用

1. **RSA密码系统**：选两个大素数（通常各1024位），其乘积作为公钥的一部分。破解RSA需要分解这个乘积，而当前最好的算法对2048位整数需要的计算量远超现有算力。

2. **哈希表设计**：使用素数作为哈希表大小可以减少碰撞概率。因为当模数为素数时，乘法散列的分布更均匀。

3. **数字水印与校验**：循环冗余校验（CRC）使用不可约多项式（多项式环中的"素数"）检测数据传输错误。

## 常见误区

1. **"1是素数"**：历史上确有数学家将1视为素数，但现代定义明确排除1。原因在于保证算术基本定理中分解的**唯一性**——若1是素数，则 $6 = 2 \times 3 = 1 \times 2 \times 3 = 1^2 \times 2 \times 3$ 等无穷种分解方式。

2. **"存在生成所有素数的公式"**：不存在简单的代数公式能生成所有素数。$n^2 - n + 41$ 对 $n = 1, 2, \ldots, 40$ 都给出素数（欧拉发现），但 $n = 41$ 时结果为 $41^2$（非素数）。

3. **"素数越来越稀疏，最终会消失"**：虽然素数密度趋于0（$\pi(x)/x \to 0$），但素数个数是无穷的。素数的绝对数量在任何范围内都在增长。

## 知识关联

**先修概念**：自然数、整除性、因数与倍数、最大公约数。

**后续发展**：素数直接连接同余理论与模运算、密码学基础（RSA、椭圆曲线）。在解析数论中，素数分布与黎曼ζ函数 $\zeta(s) = \sum_{n=1}^{\infty} n^{-s}$ 深度关联——黎曼猜想（1859年提出，至今未证明，千禧年奖金100万美元）正是关于ζ函数非平凡零点与素数分布的精确关系。

## 参考来源

- [Prime number - Wikipedia](https://en.wikipedia.org/wiki/Prime_number)
- Hardy, G.H. & Wright, E.M. *An Introduction to the Theory of Numbers*, 6th ed.
- GIMPS (Great Internet Mersenne Prime Search), https://www.mersenne.org
'''
},

# ═══════════════════════════════════════════════════════════════
# 4. 梯度下降
# ═══════════════════════════════════════════════════════════════
{
"path": r"mathematics\optimization\gradient-descent.md",
"sources_yaml": '''sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Gradient descent"
    url: "https://en.wikipedia.org/wiki/Gradient_descent"
  - type: "textbook-reference"
    ref: "Boyd & Vandenberghe. Convex Optimization, Cambridge University Press (2004)"''',
"body": r'''# 梯度下降

## 概述

梯度下降（Gradient Descent）是求解无约束优化问题的一阶迭代算法，由法国数学家奥古斯丁-路易·柯西（Augustin-Louis Cauchy）于1847年首次提出。其核心思想：**沿目标函数梯度的反方向移动，每步都朝函数值减小最快的方向前进。**

对于可微函数 $f: \mathbb{R}^n \to \mathbb{R}$，梯度下降的更新规则为：

$$\mathbf{x}_{t+1} = \mathbf{x}_t - \eta \nabla f(\mathbf{x}_t)$$

其中 $\eta > 0$ 为**学习率**（learning rate），$\nabla f(\mathbf{x}_t)$ 为 $f$ 在 $\mathbf{x}_t$ 处的梯度向量。

梯度下降是现代机器学习的核心引擎——几乎所有深度学习模型的训练都依赖于梯度下降的某种变体。

## 核心原理

### 数学直觉

梯度 $\nabla f(\mathbf{x})$ 指向函数 $f$ 在点 $\mathbf{x}$ 增长最快的方向。因此，$-\nabla f(\mathbf{x})$ 指向下降最快的方向。一阶泰勒展开给出：

$$f(\mathbf{x} + \Delta\mathbf{x}) \approx f(\mathbf{x}) + \nabla f(\mathbf{x})^T \Delta\mathbf{x}$$

取 $\Delta\mathbf{x} = -\eta \nabla f(\mathbf{x})$，则 $f(\mathbf{x} + \Delta\mathbf{x}) \approx f(\mathbf{x}) - \eta \|\nabla f(\mathbf{x})\|^2$，只要 $\eta$ 足够小且梯度非零，函数值必然下降。

### 学习率的影响

学习率 $\eta$ 是梯度下降最关键的超参数：

- **$\eta$ 过大**：步长过大可能跨过极小值点，导致振荡甚至发散。例如对 $f(x) = x^2$，当 $\eta > 1$ 时迭代发散：$x_{t+1} = x_t - 2\eta x_t = (1-2\eta)x_t$，若 $|1-2\eta| > 1$ 则 $|x_t| \to \infty$。
- **$\eta$ 过小**：收敛极慢，需要大量迭代才能接近极小值。
- **最优学习率**：对于 $L$-Lipschitz 连续梯度的凸函数，最优固定学习率为 $\eta = \frac{1}{L}$，此时收敛率为 $O(1/t)$。

### 主要变体

**随机梯度下降**（SGD, Robbins & Monro, 1951）：每次仅用一个或小批量（mini-batch）样本估计梯度，大幅降低每步计算成本。对 $n$ 个样本的损失函数 $f(\mathbf{x}) = \frac{1}{n}\sum_{i=1}^n f_i(\mathbf{x})$，SGD随机选取 $i$ 并按 $\nabla f_i(\mathbf{x})$ 更新。

**Momentum**（Polyak, 1964）：引入动量项 $\mathbf{v}_t = \beta \mathbf{v}_{t-1} + \nabla f(\mathbf{x}_t)$，$\mathbf{x}_{t+1} = \mathbf{x}_t - \eta \mathbf{v}_t$。动量通常取 $\beta = 0.9$，有助于加速收敛并穿越窄谷。

**Adam**（Kingma & Ba, 2014）：结合一阶矩（均值）和二阶矩（方差）的自适应学习率方法，是当前深度学习中最常用的优化器。默认参数 $\beta_1 = 0.9, \beta_2 = 0.999, \epsilon = 10^{-8}$。

### 收敛条件

对于**凸函数**：梯度下降保证收敛到全局最小值。对于 $L$-光滑凸函数，$f(\mathbf{x}_t) - f(\mathbf{x}^*) \leq O(1/t)$。
对于**强凸函数**（条件数 $\kappa = L/\mu$）：线性收敛，$f(\mathbf{x}_t) - f(\mathbf{x}^*) \leq O((1-\mu/L)^t)$。
对于**非凸函数**（如深度神经网络）：只保证收敛到局部极小值或鞍点。实践中，SGD的随机性有助于逃离鞍点。

## 实际应用

1. **深度学习训练**：GPT、ResNet等模型含数十亿参数，通过mini-batch SGD+Adam在数周内训练。GPT-3的训练使用了约3.14×10²³ FLOPs。

2. **线性回归的正规解 vs 梯度下降**：当特征数 $n$ 较小（< 10,000），正规方程 $\mathbf{x}^* = (A^T A)^{-1} A^T \mathbf{b}$ 更快；当 $n$ 很大时梯度下降更高效，因其复杂度为 $O(n)$/步而非 $O(n^3)$。

3. **推荐系统**：Netflix奖竞赛（2006-2009）中获胜方案使用SGD优化矩阵分解模型的均方误差。

## 常见误区

1. **"梯度下降总能找到全局最优解"**：仅对凸函数成立。非凸函数（几乎所有深度学习问题）中，梯度下降可能陷入局部极小值。但近年研究表明，高维非凸问题中局部极小值通常接近全局最优。

2. **"学习率越小越好"**：过小的学习率不仅收敛慢，还可能使SGD陷入尖锐极小值（sharp minima），泛化性能反而更差。Li et al. (2019) 的实验表明，适当大的学习率配合衰减策略找到的平坦极小值泛化更好。

3. **"梯度为零 = 找到了最小值"**：梯度为零的点（驻点）可能是极小值、极大值或鞍点。在高维空间中，鞍点远比极小值更常见——对于 $n$ 维函数，随机驻点是鞍点的概率接近 $1 - 2^{-n}$。

## 知识关联

**先修概念**：多元微积分（偏导数、梯度向量）、线性代数（向量运算）、凸集与凸函数基础。

**后续发展**：梯度下降通向二阶优化方法（牛顿法使用Hessian矩阵，收敛更快但计算量为 $O(n^3)$/步）、约束优化（拉格朗日乘子法）、以及自动微分（反向传播算法的数学基础）。

## 参考来源

- [Gradient descent - Wikipedia](https://en.wikipedia.org/wiki/Gradient_descent)
- Boyd, S. & Vandenberghe, L. *Convex Optimization*, Cambridge University Press (2004), Ch. 9.
- Kingma, D.P. & Ba, J. "Adam: A Method for Stochastic Optimization." *ICLR* (2015).
- Ruder, S. "An overview of gradient descent optimization algorithms." *arXiv:1609.04747* (2016).
'''
},

]  # END DOCUMENTS
