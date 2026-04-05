---
id: "cg-importance-sampling"
concept: "重要性采样"
domain: "computer-graphics"
subdomain: "ray-tracing"
subdomain_name: "光线追踪"
difficulty: 4
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 重要性采样

## 概述

重要性采样（Importance Sampling）是一种蒙特卡洛积分的方差缩减技术，专门用于加速光线追踪中的渲染方程求解。其核心思想是：选择与被积函数形状相近的概率密度函数（PDF）来生成采样点，而非均匀随机采样，从而让更多采样集中在对积分贡献最大的区域。在路径追踪中，被积函数是 BRDF × 入射辐射度 × cosθ 的乘积，均匀半球采样会将大量样本浪费在对最终像素贡献极小的方向上。

该技术的理论基础来源于统计学，在图形学中由 James Kajiya 于 1986 年提出渲染方程后不久被引入。当时 Kajiya 本人在同一篇论文中就讨论了对 BRDF 进行重要性采样的必要性。现代实时和离线渲染器几乎无一例外地依赖此技术，在 Blender Cycles、PBRT、Arnold 等主流渲染器中，重要性采样是路径追踪收敛速度的关键因素，能将收敛所需样本数降低一个数量级以上。

## 核心原理

### 蒙特卡洛估计量与方差

渲染方程的蒙特卡洛估计量为：

$$L_o \approx \frac{1}{N} \sum_{i=1}^{N} \frac{f_r(\omega_i) L_i(\omega_i) \cos\theta_i}{p(\omega_i)}$$

其中 $f_r$ 是 BRDF，$L_i$ 是入射辐射度，$\theta_i$ 是入射方向与法线的夹角，$p(\omega_i)$ 是采样方向 $\omega_i$ 的概率密度函数（PDF）。均匀半球采样时 $p(\omega) = \frac{1}{2\pi}$，而余弦加权采样时 $p(\omega) = \frac{\cos\theta}{\pi}$。方差的公式为：

$$\text{Var}[\hat{I}] = \frac{1}{N} \int \left(\frac{f_r L_i \cos\theta}{p(\omega)} - I\right)^2 p(\omega) \, d\omega$$

当 $p(\omega)$ 的形状与 $f_r \cdot L_i \cdot \cos\theta$ 完全成比例时，方差降为零，即用一个样本就能得到精确结果。实践中无法对 $L_i$ 建模，但可以至少对 BRDF 或余弦项进行重要性采样。

### 余弦加权半球采样

最基础的重要性采样形式是余弦加权采样（Cosine-Weighted Hemisphere Sampling），对应 Lambertian 漫反射 BRDF $f_r = \frac{\rho}{\pi}$。此时被积函数含有 $\cos\theta$ 项，选取 $p(\omega) = \frac{\cos\theta}{\pi}$ 后，漫反射部分的估计量简化为 $\frac{1}{N}\sum \rho \cdot L_i$，完全消除了 cosθ 带来的方差。采样方法使用 Malley's method：在单位圆盘上均匀采样 $(r, \phi)$，然后将其投影到半球面，生成的方向天然服从余弦加权分布。

### 镜面 BRDF 的重要性采样

对 GGX 微面元 BRDF（由 Walter 等人于 2007 年引入），其法线分布函数为：

$$D(h) = \frac{\alpha^2}{\pi \left(\cos^2\theta_h (\alpha^2 - 1) + 1\right)^2}$$

其中 $\alpha$ 是粗糙度参数（通常为 roughness²），$\theta_h$ 是微表面法线与宏观法线的夹角。对 GGX 进行重要性采样时，直接对 $D(h)$ 建立 PDF，通过逆变换采样得到微表面法线 $h$，再将入射方向 $\omega_i$ 反射到该法线方向：

$$\theta_h = \arctan\left(\alpha \sqrt{\frac{\xi_1}{1 - \xi_1}}\right), \quad \phi_h = 2\pi \xi_2$$

其中 $\xi_1, \xi_2$ 是 $[0,1]$ 均匀分布随机变量。粗糙度 $\alpha$ 越小（越光滑），GGX 波瓣越窄，重要性采样的收益越显著；对于 $\alpha < 0.1$ 的近镜面材质，均匀半球采样几乎无法在合理样本数内收敛。

### PDF 转换与 Jacobian

由于 BRDF 重要性采样对微表面法线 $h$ 采样，而渲染方程是对入射方向 $\omega_i$ 积分，需要进行 PDF 的 Jacobian 变换：

$$p(\omega_i) = \frac{p(h)}{4(\omega_i \cdot h)}$$

分母 $4(\omega_i \cdot h)$ 是从 $h$ 空间到 $\omega_i$ 空间的变换行列式。忽略此 Jacobian 是初学者最常见的错误之一，会导致高光区域出现系统性的亮度偏差。

## 实际应用

**材质系统中的采样策略选择**：在 PBRT v4 中，每种 BRDF 模型都实现了 `Sample_f()` 方法，返回采样方向、PDF 值以及 BRDF 值。Unreal Engine 的路径追踪模式对漫反射使用余弦加权、对金属使用 GGX 重要性采样，并根据材质的 metallic/roughness 参数在运行时动态选择策略。

**环境光贴图采样**：对 HDR 环境贴图进行重要性采样时，预先对亮度值构建 2D 累积分布函数（CDF），采样时通过二分查找以 O(log n) 复杂度找到对应像素。这使得对包含强光源（如太阳）的 HDRI 的采样效率提升可达 50 倍以上。

**混合采样权重**：当场景同时有直接光照和 BRDF 高光时，单独对其中一个进行重要性采样均不理想。这是引入多重重要性采样（MIS）的直接动机——在实践中，Arnold 渲染器默认对 BRDF 和光源各采一个样本，然后用 balance heuristic 权重合并。

## 常见误区

**误区一：PDF 应等于被积函数本身**。实际上 PDF 必须是归一化的概率密度，满足 $\int p(\omega) d\omega = 1$。若将 BRDF 直接当作 PDF 而不归一化，估计量的期望值会偏离真实积分值。对 GGX 而言，正确的 PDF 是 $p(\omega_i) = D(h) \cos\theta_h / (4(\omega_i \cdot h))$，而不是简单的 $D(h)$。

**误区二：重要性采样总能减少噪声**。只有当 PDF 的形状与被积函数匹配时方差才减小。若 $p(\omega)$ 与被积函数形状相差甚远（例如用 GGX 采样对 Lambertian 材质），分子分母之比的方差反而可能增大。极端情况下，若采样方向集中在 $L_i$ 接近零的区域，会产生过暗的有偏估计。

**误区三：对所有材质使用相同 roughness 的 GGX 采样**。对于粗糙度极低（$\alpha < 0.01$）的材质，GGX PDF 会在极窄的立体角内极度集中，导致数值精度问题和浮点溢出。PBRT 对此做法是在 $\alpha$ 极小时退化为完美镜面反射处理，避免 PDF 值超过浮点表示范围。

## 知识关联

重要性采样直接建立在**路径追踪**的蒙特卡洛框架之上：路径追踪确定了需要估计的渲染方程积分，而重要性采样提供了减少该估计方差的具体采样策略。理解路径追踪中每个弹射点独立估计反射方程是应用重要性采样的前提。

**多重重要性采样（MIS）**是重要性采样的直接延伸，由 Veach 和 Guibas 于 1995 年提出，解决了单一 PDF 无法同时匹配 BRDF 和光源分布的问题。MIS 的 balance heuristic 权重 $w_k = \frac{n_k p_k}{\sum_j n_j p_j}$ 在本质上是将多个重要性采样策略以最优方式组合。

**ReSTIR**（Reservoir-based Spatiotemporal Importance Resampling，2020 年 SIGGRAPH）则将重要性采样推广到时空复用场景，通过水库采样（reservoir sampling）算法对来自前帧和相邻像素的大量候选样本进行加权重采样，相当于在屏幕空间中执行高效的重要性采样，使直接光照质量在实时约束下接近离线渲染水平。