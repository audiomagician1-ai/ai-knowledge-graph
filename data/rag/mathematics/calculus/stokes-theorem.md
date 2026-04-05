---
id: "stokes-theorem"
concept: "斯托克斯定理"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 9
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 斯托克斯定理

## 概述

斯托克斯定理（Stokes' Theorem）建立了有向曲面上的曲面积分与该曲面边界曲线上的曲线积分之间的精确等式关系。其标准形式为：

$$\oint_{\partial \Sigma} P\,dx + Q\,dy + R\,dz = \iint_{\Sigma} \left(\frac{\partial R}{\partial y} - \frac{\partial Q}{\partial z}\right)dy\,dz + \left(\frac{\partial P}{\partial z} - \frac{\partial R}{\partial x}\right)dz\,dx + \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right)dx\,dy$$

其中 $\Sigma$ 是光滑有向曲面，$\partial \Sigma$ 是其正向边界曲线，$P, Q, R$ 是在包含 $\Sigma$ 的开区域上具有连续偏导数的函数。

该定理由爱尔兰数学家乔治·斯托克斯（George Gabriel Stokes）于1854年在剑桥大学数学荣誉学位考试题中正式提出，但实际上更早的版本由开尔文勋爵（Lord Kelvin）于1850年在一封私人信件中写给斯托克斯。斯托克斯定理是外微分形式理论中广义斯托克斯定理 $\int_{\partial \Omega} \omega = \int_{\Omega} d\omega$ 在三维空间中的具体体现，这一广义形式统一了格林公式、散度定理和经典斯托克斯定理三大积分定理。

斯托克斯定理在物理学中具有不可替代的地位：麦克斯韦方程组的积分形式与微分形式之间的转换直接依赖此定理，特别是法拉第电磁感应定律 $\oint_C \mathbf{E} \cdot d\mathbf{l} = -\frac{d}{dt}\iint_S \mathbf{B} \cdot d\mathbf{S}$ 正是斯托克斯定理在电磁场中的物理表达。

---

## 核心原理

### 旋度与曲线积分的内在联系

斯托克斯定理可用向量场语言写成最紧凑的形式：

$$\oint_{\partial \Sigma} \mathbf{F} \cdot d\mathbf{r} = \iint_{\Sigma} (\nabla \times \mathbf{F}) \cdot d\mathbf{S}$$

其中 $\nabla \times \mathbf{F}$ 是向量场 $\mathbf{F} = (P, Q, R)$ 的旋度，$d\mathbf{S} = \mathbf{n}\,dS$ 是带方向的面积元。右侧被积量 $(\nabla \times \mathbf{F}) \cdot \mathbf{n}$ 表示旋度在曲面法向量方向上的分量，物理意义是单位面积上的环量密度。

旋度的三个分量分别为：
$$(\nabla \times \mathbf{F})_x = \frac{\partial R}{\partial y} - \frac{\partial Q}{\partial z}, \quad (\nabla \times \mathbf{F})_y = \frac{\partial P}{\partial z} - \frac{\partial R}{\partial x}, \quad (\nabla \times \mathbf{F})_z = \frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}$$

当曲面退化为平面区域（即 $z = \text{const}$，法向量指向 $z$ 轴正方向）时，仅保留 $z$ 分量，斯托克斯定理精确退化为格林公式 $\oint_{\partial D} P\,dx + Q\,dy = \iint_D \left(\frac{\partial Q}{\partial x} - \frac{\partial P}{\partial y}\right)dx\,dy$。

### 正向边界的右手法则约定

斯托克斯定理中曲面正向与边界正向的对应关系遵循**右手定则**：将右手四指弯曲向边界曲线 $\partial\Sigma$ 的前进方向，拇指所指即为曲面的正法向方向。这一约定不是任意的——若边界方向取反，等式右侧曲面积分的值也随之变号，等式仍成立。例如，对于单位球面的上半球，法向量取向上时，边界赤道圆的正向为逆时针（从上方俯视），此时等式成立；若将法向量改为向下，则赤道圆正向变为顺时针，两侧符号同时取反。

曲面本身可以是**非平面**的任意光滑有向曲面，但必须满足：曲面片数有限、边界曲线分段光滑，且函数 $P, Q, R$ 的偏导数在包含 $\Sigma$ 的某邻域内连续。

### 定理的证明思路

斯托克斯定理的标准证明分两步：先对**可投影曲面**（即能向某坐标面作单值投影的曲面）证明单个分量的等式，再叠加三个分量。以 $R$ 分量为例，设曲面 $\Sigma: z = z(x,y)$，$(x,y) \in D_{xy}$，利用复合函数求导：

$$\iint_{\Sigma} \frac{\partial R}{\partial x}\,dy\,dz - \frac{\partial R}{\partial y}\,dz\,dx$$

通过参数化后转化为 $D_{xy}$ 上的二重积分，再用格林公式将其转化为 $D_{xy}$ 边界上的积分，最后投影回空间曲线 $\partial\Sigma$，即得该分量等式。一般曲面通过分割为若干可投影片段后拼合完成证明，内部切割线上的曲线积分方向相反而抵消。

---

## 实际应用

**计算空间曲线积分**：当直接参数化空间曲线 $\partial\Sigma$ 较繁琐时，可任意选取以该曲线为边界的简单曲面来计算。例如，计算 $\oint_C y\,dx + z\,dy + x\,dz$，其中 $C$ 是平面 $x+y+z=1$ 与三坐标面围成三角形的边界（正向按右手定则），取该三角形平面片 $\Sigma$ 作为积分曲面，法向量指向 $(1,1,1)/\sqrt{3}$ 方向，计算旋度 $\nabla\times\mathbf{F} = (-1,-1,-1)$，则曲面积分为 $(-1,-1,-1)\cdot(1,1,1)/\sqrt{3} \cdot \text{面积} = -3/\sqrt{3}\cdot\sqrt{3}/2 = -3/2$。

**验证向量场是否为保守场**：若 $\nabla\times\mathbf{F}=\mathbf{0}$ 在单连通区域内处处成立，则由斯托克斯定理可知该区域内任意闭合曲线上 $\oint \mathbf{F}\cdot d\mathbf{r}=0$，即 $\mathbf{F}$ 为保守场，存在势函数 $\phi$ 使得 $\mathbf{F}=\nabla\phi$。注意单连通性是关键条件：向量场 $\mathbf{F}=\left(-\frac{y}{x^2+y^2},\frac{x}{x^2+y^2},0\right)$ 旋度为零但在包含 $z$ 轴的环形区域内不保守，正因为该区域非单连通。

**电磁学中的应用**：安培-麦克斯韦定律的积分形式 $\oint_C \mathbf{B}\cdot d\mathbf{l} = \mu_0 \iint_S \mathbf{J}\cdot d\mathbf{S}$ 正是斯托克斯定理与微分形式 $\nabla\times\mathbf{B}=\mu_0\mathbf{J}$ 之间的等价转化。

---

## 常见误区

**误区一：曲面的选取影响结果**。在满足条件的前提下，同一边界曲线可以任意选取不同曲面，斯托克斯定理保证结果相同。这一结论本身是判断旋度是否为零的重要工具——若同一边界曲线对不同曲面给出不同的旋度通量值，则说明两曲面所围区域内旋度不恒为零，即 $\nabla\times\mathbf{F}\neq\mathbf{0}$。

**误区二：混淆法向量方向与边界方向的关联**。斯托克斯定理要求曲面法向量方向与边界正向严格遵循右手定则，而非可以独立选取。许多学生在计算中将曲面法向量取为"向上"，却将边界方向随意选取，导致等式两边符号不一致。具体操作时应先固定曲面法向量（决定 $dx\,dy$ 等面积元的符号），再由右手定则确定边界积分方向，不能颠倒次序。

**误区三：将斯托克斯定理与高斯散度定理混淆**。斯托克斯定理连接的是**曲面**积分与其**边界曲线**积分（降一维），被积量是旋度；散度定理连接的是**空间体**积分与其**边界曲面**积分（同样降一维），被积量是散度。前者方程右侧涉及 $\iint(\nabla\times\mathbf{F})\cdot d\mathbf{S}$，后者涉及 $\iiint\nabla\cdot\mathbf{F}\,dV$，二者处理的几何对象和微分算子完全不同。

---

## 知识关联

**