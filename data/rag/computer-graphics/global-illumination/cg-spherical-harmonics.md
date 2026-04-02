---
id: "cg-spherical-harmonics"
concept: "球谐函数"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 3
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 球谐函数

## 概述

球谐函数（Spherical Harmonics，简称 SH）是定义在单位球面上的一组正交基函数，最初源于数学物理领域对拉普拉斯方程的球坐标求解。在图形学中，球谐函数提供了一种将球面上的低频信号（如漫反射光照）压缩表示为少量系数的方法，从而避免了存储完整辐照度贴图的巨大开销。

球谐函数由阶数 $l$（band index）和阶内编号 $m$（$-l \leq m \leq l$）共同标识，记作 $Y_l^m(\theta, \phi)$。前 $n$ 阶共包含 $n^2$ 个基函数——例如前4阶（$l = 0,1,2,3$）共有16个基函数，对应16个SH系数。Ravi Ramamoorthi 和 Pat Hanrahan 在2001年的 SIGGRAPH 论文中证明，漫反射BRDF的余弦瓣（cosine lobe）具有极强的低通特性，仅用前3阶（9个系数）就能捕捉超过99%的漫反射光照能量，这使得SH成为实时全局光照的核心工具之一。

在实时渲染管线中，球谐函数之所以优于辐照度贴图，在于它将整个球面光照环境编码为一个固定大小的系数向量，无需采样立方体贴图的六个面，也无需在Shader中执行卷积，运行时只需计算一次SH系数与基函数的点积即可还原辐照度。

## 核心原理

### 基函数的数学定义

球谐函数的实值形式定义为：

$$Y_l^m(\theta, \phi) = \begin{cases} \sqrt{2} \, K_l^m \cos(m\phi) \, P_l^m(\cos\theta) & m > 0 \\ K_l^0 \, P_l^0(\cos\theta) & m = 0 \\ \sqrt{2} \, K_l^{|m|} \sin(|m|\phi) \, P_l^{|m|}(\cos\theta) & m < 0 \end{cases}$$

其中 $P_l^m$ 是连带勒让德多项式，$K_l^m$ 是归一化系数 $\sqrt{\frac{(2l+1)(l-|m|)!}{4\pi(l+|m|)!}}$，$\theta$ 是极角，$\phi$ 是方位角。这组基函数在球面上满足正交归一性：$\int_{S^2} Y_l^m(\omega) Y_{l'}^{m'}(\omega) \, d\omega = \delta_{ll'}\delta_{mm'}$。

### 投影与重建

将任意球面函数 $f(\omega)$（如环境光照的辐亮度分布）投影到SH基上，得到系数：

$$c_l^m = \int_{S^2} f(\omega) \, Y_l^m(\omega) \, d\omega$$

实际计算时通过蒙特卡洛采样近似该积分：对环境贴图均匀采样 $N$ 个方向（通常 $N$ 取 10000 到 100000 个样本），累加 $c_l^m \approx \frac{4\pi}{N} \sum_i f(\omega_i) Y_l^m(\omega_i)$。重建时，对任意方向 $\omega$ 的辐照度为 $\tilde{f}(\omega) = \sum_{l,m} c_l^m Y_l^m(\omega)$。

### 漫反射光照的SH卷积

漫反射辐照度是环境光照与余弦瓣的球面卷积。由于SH是球面卷积的特征函数，卷积在SH域中退化为逐系数相乘：

$$E_l^m = \hat{A}_l \cdot L_l^m$$

其中 $L_l^m$ 是光照的SH系数，$\hat{A}_l$ 是余弦瓣在各阶的缩放因子（$\hat{A}_0 = \pi$，$\hat{A}_1 = 2\pi/3$，$\hat{A}_2 = \pi/4$，$l \geq 3$ 的高阶项衰减至接近零）。这一性质使得Ramamoorthi等人能够将辐照度的计算简化为一个仅含9项的二次多项式——即著名的"辐照度环境映射"（Irradiance Environment Map）的SH近似公式，在 DirectX 和 OpenGL Shader 中可在不到10条指令内完成。

### SH的旋转不变性

球谐函数在旋转变换下保持封闭性：对同一阶 $l$ 的 $2l+1$ 个基函数施加任意三维旋转 $R$，结果仍是该阶基函数的线性组合，由旋转矩阵 $D^l(R)$（Wigner D-matrix）描述。这意味着当光照环境旋转时，只需对每阶的SH系数向量做一次矩阵乘法，无需重新投影，这在日夜交替或动态天空场景中极为高效。

## 实际应用

**游戏引擎中的全局光照**：Unity 的 Light Probe 系统和 Unreal Engine 的 Sky Light 均将每个探针的间接漫反射光照存储为3阶（9个）SH系数，每个RGB通道各9个浮点数，共27个浮点数（108字节），相比一张 $128\times128$ 的辐照度立方体贴图（约98KB）节省了约99.9%的内存。

**预计算辐射传输（PRT）**：Sloan等人在2002年将SH扩展到遮蔽传输的预计算中，将每顶点的自遮蔽和相互遮蔽投影为SH系数向量，运行时将光照SH向量与传输SH向量做点积，实现包含软阴影的全局光照实时计算。该方法在早期游戏《半条命2》的辐照度体积实现中有所体现。

**球谐光源**：在离线渲染中，将点光源、面光源或环境贴图压缩为SH系数后，可以在辐照度体积（Irradiance Volume）的每个体素中存储一套SH系数，用于场景中动态物体的间接光照查询，避免了全分辨率光照贴图的烘焙成本。

## 常见误区

**误区一：阶数越高效果越好**。实际上对于漫反射表面，3阶（$l = 0,1,2$）已足够——提升到5阶或7阶对漫反射误差的改善极其有限，反而使Shader中的系数数量从9个膨胀到25个或49个。SH的低频特性决定了它不适合表示高光反射或锐利阴影；这类需求应使用球面高斯（Spherical Gaussian）或辐射度缓存（Radiance Cache）代替。

**误区二：SH系数可以直接线性插值**。由于SH投影具有球面积分的全局性，两套分别对应不同光照环境的SH系数之间的线性插值，在物理上不等价于对两个光照环境混合后再投影。在光照条件差异极大的区域（如室内与室外交界）直接插值SH系数会产生"能量错误"的灰暗过渡区域。Unity 的 Light Probe 插值在实践中会出现这类 artifact，通常需要额外的混合权重设计来缓解。

**误区三：SH投影需要在运行时完成**。SH投影（将环境贴图转换为系数）是一个耗时的积分运算，必须在预计算阶段完成。运行时只执行系数的重建（一次点积），不涉及任何积分。混淆这两个阶段是初学者常见错误。

## 知识关联

**前置概念——辐照度贴图**：辐照度贴图将每个方向的漫反射辐照度预先卷积存储在立方体贴图中，球谐函数是对同一物理量（漫反射辐照度）的不同编码方式。理解辐照度贴图的卷积过程有助于直观感受SH在频域的等价操作：辐照度贴图中卷积核的模糊程度，对应SH中高阶系数被余弦瓣缩放因子 $\hat{A}_l$ 压制为零的频率截断行为。

**后继概念——辐照度体积**：辐照度体积将空间中每个采样点的间接漫反射光照存储为独立的辐照度探针，而每个探针最自然的紧凑表示方式正是一套3阶SH系数。掌握SH的投影、重建与旋转性质，是理解辐照度体积如何在体素网格中高效存储和查询间接光照的直接前提。