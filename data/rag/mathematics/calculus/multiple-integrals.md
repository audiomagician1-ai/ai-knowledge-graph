---
id: "multiple-integrals"
concept: "重积分"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 39.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 重积分

## 概述

重积分是将定积分从一维推广至多维空间的积分形式，分为二重积分与三重积分两大类。二重积分 $\iint_D f(x,y)\,dA$ 表示函数 $f(x,y)$ 在平面区域 $D$ 上的积累量，几何上对应曲面 $z=f(x,y)$ 与 $xy$ 平面之间的有向体积；三重积分 $\iiint_\Omega f(x,y,z)\,dV$ 则将积分域扩展至三维空间区域 $\Omega$。

重积分的严格理论由黎曼（Riemann）在19世纪60年代建立，核心思路是将积分区域分割为 $n$ 个小块，取每块面积（或体积）$\Delta A_i$（或 $\Delta V_i$）与函数值之积的极限：$\iint_D f\,dA = \lim_{n\to\infty}\sum_{i=1}^n f(\xi_i,\eta_i)\Delta A_i$，与一维黎曼积分的构造完全平行。勒贝格（Lebesgue）后来在1902年提出了更一般的积分理论，使重积分在更广泛的函数类上成立。

重积分在物理、工程中有直接意义：质量计算公式 $m = \iint_D \rho(x,y)\,dA$（其中 $\rho$ 为面密度）、转动惯量、电荷分布、引力势能等均依赖重积分。掌握重积分不仅是计算技能，更是理解场论与曲线、曲面积分体系的前提。

---

## 核心原理

### 化累次积分（Fubini 定理）

将二重积分转化为两次一元定积分是计算的基本手段，理论依据是 **Fubini 定理**：若 $f(x,y)$ 在矩形区域 $[a,b]\times[c,d]$ 上连续，则

$$\iint_D f(x,y)\,dA = \int_a^b\!\left(\int_c^d f(x,y)\,dy\right)dx = \int_c^d\!\left(\int_a^b f(x,y)\,dx\right)dy$$

对非矩形区域，需确定积分上下限的依赖关系。X型区域（先 $y$ 后 $x$）：$a\le x\le b$，$\varphi_1(x)\le y\le\varphi_2(x)$；Y型区域（先 $x$ 后 $y$）：$c\le y\le d$，$\psi_1(y)\le x\le\psi_2(y)$。错误地交换积分次序而不修正积分限是最常见的计算错误。

三重积分类似地化为三次积分：先固定 $x,y$ 对 $z$ 积分（截面法），或先固定 $z$ 做横截面面积积分再对 $z$ 积分（投影法）。

### 换元法：极坐标与柱、球坐标

当积分区域具有圆形或球形对称性时，换元可大幅简化计算。

**极坐标变换**（用于二重积分）：令 $x=r\cos\theta$，$y=r\sin\theta$，则面积微元变为 $dA = r\,dr\,d\theta$。**因子 $r$ 不可遗漏**，它来自变换的雅可比行列式 $J = \partial(x,y)/\partial(r,\theta) = r$。例如计算 $\iint_D e^{-(x^2+y^2)}\,dA$（$D$ 为圆盘 $x^2+y^2\le R^2$）时，结果为 $\pi(1-e^{-R^2})$，若令 $R\to\infty$ 即可推导出著名的高斯积分 $\int_{-\infty}^{+\infty}e^{-x^2}\,dx=\sqrt{\pi}$。

**柱坐标变换**（用于三重积分）：$x=r\cos\theta$，$y=r\sin\theta$，$z=z$，体积微元 $dV = r\,dr\,d\theta\,dz$。

**球坐标变换**：$x=\rho\sin\varphi\cos\theta$，$y=\rho\sin\varphi\sin\theta$，$z=\rho\cos\varphi$，体积微元 $dV = \rho^2\sin\varphi\,d\rho\,d\varphi\,d\theta$，其中 $\rho^2\sin\varphi$ 为对应的雅可比因子。球坐标尤其适合积分区域为球体或锥体的情形。

### 一般换元公式与雅可比行列式

设变换 $x=x(u,v)$，$y=y(u,v)$ 将 $uv$ 平面上的区域 $D'$ 映射到 $xy$ 平面上的区域 $D$，则

$$\iint_D f(x,y)\,dA = \iint_{D'} f(x(u,v),y(u,v))\left|\frac{\partial(x,y)}{\partial(u,v)}\right|du\,dv$$

其中雅可比行列式 $\displaystyle\frac{\partial(x,y)}{\partial(u,v)} = \begin{vmatrix} x_u & x_v \\ y_u & y_v \end{vmatrix}$。极坐标、柱坐标、球坐标都是这一公式的特殊情形，其雅可比因子分别为 $r$、$r$、$\rho^2\sin\varphi$。

### 对称性简化

若积分区域 $D$ 关于 $y$ 轴对称，被积函数 $f(x,y)$ 关于 $x$ 是奇函数，则 $\iint_D f\,dA = 0$；若为偶函数则可化为半区域积分的两倍。三重积分具有类似的三个方向对称性原则。利用对称性往往能将计算量减少一半甚至直接得零。

---

## 实际应用

**质心计算**：均匀薄板在区域 $D$ 上的质心坐标为 $\bar{x} = \frac{1}{A}\iint_D x\,dA$，$\bar{y} = \frac{1}{A}\iint_D y\,dA$，其中 $A=\iint_D dA$ 为面积。对非均匀密度 $\rho(x,y)$，分母换成总质量 $m=\iint_D\rho\,dA$。

**转动惯量**：绕 $z$ 轴的转动惯量 $I_z = \iint_D (x^2+y^2)\rho(x,y)\,dA$，这一积分在机械工程中用于计算飞轮、齿轮的惯性参数。

**概率论中的联合分布**：二元连续随机变量 $(X,Y)$ 的联合概率密度 $f(x,y)$ 满足 $P\{(X,Y)\in D\} = \iint_D f(x,y)\,dA$，标准二元正态分布的归一化正是通过极坐标下的二重积分验证的。

**体积计算**：两曲面 $z=x^2+y^2$ 与 $z=2-x^2-y^2$ 围成的立体体积，通过令两式相等得交线为圆 $x^2+y^2=1$，再用极坐标计算得体积 $V = \iint_{x^2+y^2\le 1}(2-2(x^2+y^2))\,dA = \pi$。

---

## 常见误区

**误区一：遗忘换元后的雅可比因子**。在极坐标换元时，很多学生将 $dA$ 直接写成 $dr\,d\theta$ 而漏掉因子 $r$，导致结果相差一个 $r$ 的积分。例如计算圆盘上 $\iint e^{r^2}dA$，错误结果为 $2\pi\int_0^R e^{r^2}dr$，正确结果应为 $2\pi\int_0^R r e^{r^2}dr = \pi(e^{R^2}-1)$，两者相差巨大。

**误区二：非矩形区域交换积分次序时不修正上下限**。Fubini 定理保证积分次序可交换，但上下限的函数关系必须重新推导。例如 $\int_0^1\int_y^1 f(x,y)\,dx\,dy$ 交换次序后应为 $\int_0^1\int_0^x f(x,y)\,dy\,dx$，积分域 $D$ 是三角形，若直接写 $\int_0^1\int_0^1$ 则是错误的，积分区域扩大了。

**误区三：混淆柱坐标与球坐标的适用场景**。柱坐标适合"轴对称"且保留 $z$ 方向线性结构的区域（如圆柱、抛物面），球坐标适合与原点距离有关的球体或锥体。对球体 $x^2+y^2+z^2\le R^2$ 强行使用柱坐标，$z$ 的上下限变为 $\pm\sqrt{R^2-r^2}$，计算复杂度远高于球坐标下直接得到 $\frac{4}{3}\pi R^3$。

---

## 知识关联

**前置概念**：重积分的每一次内层积分本质上是一个关于单变量的定积分，因此**定积分**的换元法（对应重积分的内层积分换元）、分部积分与牛顿-莱布尼茨公式是必不可少的基础工具。此外，偏导数与雅可比行列式来自**多元函数微分学
