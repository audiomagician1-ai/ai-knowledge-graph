---
id: "line-integrals"
concept: "曲线积分"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 8
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 76.3
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

# 曲线积分

## 概述

曲线积分是将普通定积分的积分域从区间推广到空间曲线上的积分理论。其核心思想是沿着一条曲线 $L$ 对某个函数进行累积求和，根据被积元素的物理含义分为两类：**第一类曲线积分**（对弧长的积分）和**第二类曲线积分**（对坐标的积分）。

第一类曲线积分由黎曼在19世纪中叶将积分概念推广时逐步形成，物理背景是求曲线形物体的质量——若曲线 $L$ 的线密度为 $\rho(x,y)$，则其质量恰好等于 $\int_L \rho(x,y)\,ds$。第二类曲线积分则源于物理学中做功的计算，若力场 $\vec{F}=(P,Q)$ 作用于质点沿曲线 $L$ 运动，则做的功为 $\int_L P\,dx + Q\,dy$。这两类积分形式上迥异，却通过弧长微元紧密相连。

曲线积分的重要性在于它是格林公式、斯托克斯定理等高维积分定理的直接基础，同时在流体力学（环流量）、电磁学（安培定律）、保守场判断等领域均有不可替代的应用。掌握它是从"平面积分"迈向"场论积分"的关键一步。

---

## 核心原理

### 第一类曲线积分（对弧长的积分）

第一类曲线积分的定义形式为：

$$\int_L f(x,y)\,ds = \lim_{\lambda \to 0} \sum_{i=1}^n f(\xi_i, \eta_i)\,\Delta s_i$$

其中 $\Delta s_i$ 是第 $i$ 段弧长，$\lambda = \max\{\Delta s_i\}$。其关键性质是**与曲线方向无关**，即将 $L$ 反向后积分值不变，这一点区别于第二类曲线积分。

计算时将曲线参数化为 $x=\varphi(t),\,y=\psi(t),\,t\in[\alpha,\beta]$，代入弧长微元公式：

$$ds = \sqrt{[\varphi'(t)]^2 + [\psi'(t)]^2}\,dt$$

从而将曲线积分化为关于参数 $t$ 的普通定积分。若曲线由 $y=y(x)$，$x\in[a,b]$ 给出，则 $ds=\sqrt{1+[y'(x)]^2}\,dx$，积分下限总为 $a$，上限总为 $b$（不因方向改变）。

### 第二类曲线积分（对坐标的积分）

第二类曲线积分定义为：

$$\int_L P\,dx + Q\,dy = \lim_{\lambda \to 0} \sum_{i=1}^n \left[P(\xi_i,\eta_i)\Delta x_i + Q(\xi_i,\eta_i)\Delta y_i\right]$$

其中 $\Delta x_i = x_i - x_{i-1}$，$\Delta y_i = y_i - y_{i-1}$ 带有方向符号。**第二类曲线积分对曲线方向敏感**：将 $L$ 反向得到 $L^-$，则 $\int_{L^-} P\,dx+Q\,dy = -\int_L P\,dx+Q\,dy$。

同样参数化后代入：

$$\int_L P\,dx+Q\,dy = \int_\alpha^\beta \left[P(\varphi(t),\psi(t))\varphi'(t) + Q(\varphi(t),\psi(t))\psi'(t)\right]dt$$

注意积分下限 $\alpha$ 对应曲线起点，上限 $\beta$ 对应终点，**必须严格按方向确定上下限**，否则结果符号出错。

### 两类曲线积分的联系

设曲线 $L$ 的切向量方向余弦为 $(\cos\alpha, \cos\beta)$，则两类积分通过以下公式相互转化：

$$\int_L P\,dx + Q\,dy = \int_L (P\cos\alpha + Q\cos\beta)\,ds$$

这一关系揭示：第二类曲线积分实质是将向量场 $\vec{F}=(P,Q)$ 在切线方向上的投影沿弧长积分，即 $\int_L \vec{F}\cdot\vec{\tau}\,ds$，其中 $\vec{\tau}$ 是单位切向量。两类积分统一于此向量内积的几何框架之下。

---

## 实际应用

**计算曲线形物体质量：** 半径为 $R$ 的上半圆弧，密度 $\rho=y$，则质量为

$$M = \int_L y\,ds$$

参数化 $x=R\cos t,\,y=R\sin t,\,t\in[0,\pi]$，得 $ds=R\,dt$，从而

$$M = \int_0^\pi R\sin t \cdot R\,dt = R^2[-\cos t]_0^\pi = 2R^2$$

**变力做功：** 力 $\vec{F}=(x^2, xy)$ 沿抛物线 $y=x^2$ 从 $(0,0)$ 到 $(1,1)$ 做的功为

$$W = \int_L x^2\,dx + xy\,dy$$

令 $x=t,\,y=t^2$，$t\in[0,1]$，代入得 $W = \int_0^1(t^2 + t\cdot t^2 \cdot 2t)\,dt = \int_0^1(t^2+2t^4)\,dt = \frac{1}{3}+\frac{2}{5}=\frac{11}{15}$。

**流体环流量：** 向量场 $\vec{v}=(P,Q)$ 沿封闭曲线 $L$ 的环流量定义为 $\oint_L P\,dx+Q\,dy$，可用于判断流体旋转特性，是流体力学中涡量概念的积分表达。

---

## 常见误区

**误区一：混淆两类积分的方向依赖性。** 许多学生对第一类曲线积分也进行方向调整，将积分上下限随方向互换，导致结果出现无意义的负号。实际上 $\int_L f\,ds$ 的弧长微元 $ds>0$ 恒成立，计算时参数必须从小到大（即 $\alpha<\beta$），与曲线走向无关。

**误区二：参数化时忘记检查范围对应的曲线方向。** 在第二类曲线积分中，若题目指定从 $A$ 到 $B$，参数化后必须确认 $\alpha$ 对应 $A$，$\beta$ 对应 $B$。若参数化自然给出 $\alpha>\beta$（如沿圆弧顺时针），则定积分仍应保持 $\int_\beta^\alpha$（即下限大于上限），切勿将积分限强制调换。

**误区三：认为路径无关是普遍规律。** 第二类曲线积分 $\int_L P\,dx+Q\,dy$ 与路径无关的充要条件（在单连通域内）是 $\frac{\partial P}{\partial y}=\frac{\partial Q}{\partial x}$ 处处成立，即 $P\,dx+Q\,dy$ 是某函数 $u$ 的全微分。对于不满足此条件的向量场（如 $\vec{F}=\left(\frac{-y}{x^2+y^2},\frac{x}{x^2+y^2}\right)$ 在含原点的区域内），沿不同路径积分值可以不同，不可随意替换路径。

---

## 知识关联

**前置知识——重积分：** 曲线积分与重积分在化为参数积分的思路上类似，都需要将高维积分域降维处理。第一类曲线积分的弧长公式 $ds=\sqrt{(\varphi')^2+(\psi')^2}\,dt$ 与重积分换元时雅可比行列式的角色类似，均起到"面积（长度）缩放"的作用。

**后续概念——格林公式：** 格林公式 $\oint_L P\,dx+Q\,dy = \iint_D\left(\frac{\partial Q}{\partial x}-\frac{\partial P}{\partial y}\right)d\sigma$ 将第二类曲线积分与二重积分联系起来，其中 $L$ 必须是 $D$ 的正向（逆时针）边界。格林公式本质上是牛顿-莱布尼茨公式在二维的推广，是曲线积分理论的核心定理，可用于简化封闭曲线上的积分计算以及判断保守场。

**后续概念——曲面积分：** 曲面积分是曲线积分在三维空间中的自然推广，同样分为第一类（对面积）和第二类（对坐标）。三维情形下第二类曲线积分 $\int_L P\,dx+Q\,dy+R\,dz$ 的方向余弦关系与斯托克斯定理直接衔接，是学习三维场论不可跳过的环节。