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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 重积分

## 概述

重积分是将一元函数的定积分推广到多元函数的积分运算，包括二重积分和三重积分。二重积分 $\iint_D f(x,y)\,dA$ 表示函数 $f(x,y)$ 在平面区域 $D$ 上的积分，其几何意义是以曲面 $z=f(x,y)$ 为顶面、以区域 $D$ 为底面的"曲顶柱体"的有向体积。当 $f(x,y)\geq 0$ 时，二重积分给出该柱体的实际体积。

重积分的理论由莱布尼茨和欧拉在18世纪初步建立，黎曼在1854年将其严格化为"黎曼和的极限"：将区域 $D$ 分割为 $n$ 个小块 $\Delta\sigma_i$，在每块上取点 $(\xi_i,\eta_i)$，当最大分块直径 $\lambda\to 0$ 时，极限 $\lim_{\lambda\to 0}\sum_{i=1}^n f(\xi_i,\eta_i)\Delta\sigma_i$ 即为二重积分的定义。

重积分的计算意义超越几何体积：它是计算质心、转动惯量、引力场以及概率论中联合概率密度的核心工具。例如，均匀薄板 $D$ 的质心横坐标为 $\bar{x}=\frac{1}{A}\iint_D x\,dA$，其中 $A$ 是 $D$ 的面积。没有重积分，这类物理量的精确计算将无法实现。

---

## 核心原理

### 化为累次积分（Fubini定理）

重积分的计算核心依赖**Fubini定理（1907年）**：若 $f(x,y)$ 在矩形区域 $[a,b]\times[c,d]$ 上连续，则：

$$\iint_D f(x,y)\,dA = \int_a^b\left(\int_c^d f(x,y)\,dy\right)dx = \int_c^d\left(\int_a^b f(x,y)\,dx\right)dy$$

对于非矩形区域，需先确定积分限。X型区域（$a\leq x\leq b$，$\varphi_1(x)\leq y\leq\varphi_2(x)$）写为：

$$\iint_D f(x,y)\,dA = \int_a^b dx\int_{\varphi_1(x)}^{\varphi_2(x)} f(x,y)\,dy$$

Y型区域则先对 $x$ 积分。选择积分次序的关键在于使内层积分的上下限为**简单函数**，否则运算复杂度会急剧上升。例如对 $\iint_D e^{x^2}dA$（$D$: $0\leq x\leq 1$, $0\leq y\leq x$），若先对 $x$ 积分，$e^{x^2}$ 无初等原函数；交换次序先对 $y$ 积分，化为 $\int_0^1 xe^{x^2}dx = \frac{e-1}{2}$，立即可解。

### 极坐标变换

当被积函数含 $x^2+y^2$ 或积分区域为圆形/扇形时，令 $x=r\cos\theta$，$y=r\sin\theta$，二重积分变换为：

$$\iint_D f(x,y)\,dA = \iint_{D'} f(r\cos\theta,\,r\sin\theta)\,r\,dr\,d\theta$$

注意**Jacobi行列式** $r$ 不可遗漏——这是极坐标变换与直角坐标变换的本质差异。例如计算 $\iint_D e^{-(x^2+y^2)}dA$（$D$为以原点为圆心、半径为 $R$ 的圆盘），化为 $\int_0^{2\pi}d\theta\int_0^R e^{-r^2}r\,dr = \pi(1-e^{-R^2})$；令 $R\to\infty$ 便得到著名的高斯积分 $\int_{-\infty}^{+\infty}e^{-x^2}dx=\sqrt{\pi}$。

### 三重积分与柱、球坐标

三重积分 $\iiint_\Omega f(x,y,z)\,dV$ 将平面区域 $D$ 推广为空间区域 $\Omega$。化为累次积分时常用两种变换：

**柱坐标**：$x=r\cos\theta$，$y=r\sin\theta$，$z=z$，体积微元 $dV=r\,dr\,d\theta\,dz$，适用于轴对称区域（如圆柱、圆锥）。

**球坐标**：$x=\rho\sin\varphi\cos\theta$，$y=\rho\sin\varphi\sin\theta$，$z=\rho\cos\varphi$，体积微元 $dV=\rho^2\sin\varphi\,d\rho\,d\varphi\,d\theta$，其中 $\rho^2\sin\varphi$ 为球坐标的Jacobi行列式绝对值，适用于球形或锥形区域。例如计算球 $x^2+y^2+z^2\leq a^2$ 的体积，球坐标下直接得 $\int_0^{2\pi}d\theta\int_0^\pi\sin\varphi\,d\varphi\int_0^a\rho^2 d\rho = \frac{4}{3}\pi a^3$。

---

## 实际应用

**质量与质心计算**：密度函数为 $\mu(x,y)$ 的薄板，其总质量为 $M=\iint_D\mu(x,y)\,dA$，对 $x$ 轴的转动惯量为 $I_x=\iint_D y^2\mu(x,y)\,dA$。这在机械工程中用于设计旋转零件的平衡结构。

**概率论中的联合分布**：若二维随机变量 $(X,Y)$ 的联合密度为 $f(x,y)$，则 $P(X\leq a, Y\leq b)=\int_{-\infty}^a\int_{-\infty}^b f(x,y)\,dy\,dx$，即二重积分。标准正态分布的归一化条件 $\iint_{\mathbb{R}^2}e^{-(x^2+y^2)/2}\,dA=2\pi$ 也需通过极坐标下的二重积分验证。

**流体力学中的体积流量**：流体流过三维管道截面 $\Omega$ 的总流量为 $\iiint_\Omega v(x,y,z)\,dV$，其中 $v$ 为速度场。实际工程计算中，球坐标变换可将球阀内的流量积分从不可解形式转化为标准三角函数积分。

---

## 常见误区

**误区1：忽略Jacobi行列式**。做坐标变换时，直角坐标微元 $dx\,dy$ 换为极坐标时必须乘以 $r$，即 $dA=r\,dr\,d\theta$，而非 $dr\,d\theta$。遗漏 $r$ 是极坐标计算中最高频的错误。例如计算圆盘面积时漏掉 $r$，会得到 $2\pi\cdot R = 2\pi R$，而非正确的 $\pi R^2$。

**误区2：积分区域与积分次序混淆**。交换积分次序时，不能直接调换 $dx$ 和 $dy$ 的顺序，必须重新确定新次序下的积分上下限。$\int_0^1 dx\int_x^1 f(x,y)\,dy$ 交换次序后应为 $\int_0^1 dy\int_0^y f(x,y)\,dx$，而非 $\int_0^1 dy\int_y^1 f(x,y)\,dx$。这要求先画出区域 $D$ 的草图，再重新读出新方向的界限。

**误区3：将二重积分与二次积分混同**。Fubini定理要求 $f$ 在区域上**可积**（通常连续即满足），但对不连续函数，二次积分的两种次序可能给出不同结果，而二重积分本身可能不存在。Cauchy在1821年给出反例：$f(x,y)=\frac{x^2-y^2}{(x^2+y^2)^2}$ 在 $[0,1]^2$ 上两种次序结果分别为 $\pi/4$ 和 $-\pi/4$，但二重积分不存在（函数在原点无界且不可积）。

---

## 知识关联

**与定积分的关系**：重积分的计算最终归结为反复执行一元定积分（换元法、分部积分、牛顿-莱布尼茨公式），即累次积分的每一层均为定积分。因此一元定积分中的技巧（如奇偶对称性简化、特殊换元）在重积分中仍然有效：若 $f(x,y)$ 关于 $x$ 为奇函数且 $D$ 关于 $y$ 轴对称，则 $\iint_D f(x,y)\,dA=0$。

**通向曲线积分与曲面积分**：重积分是第一类曲线积分 $\int_L f(x,y)\,ds$ 与格林公式的基础。格林公式 $\oint_L P\,dx+Q\,dy=\iint_D\left(\frac{\partial Q}{\partial x}-\frac{\partial P}{\partial y}\right)dA$ 直接将第二类曲线积分（线积分）转化为二重积分，是向量分析的核心桥梁