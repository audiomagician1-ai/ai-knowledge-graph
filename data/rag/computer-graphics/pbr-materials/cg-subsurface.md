---
id: "cg-subsurface"
concept: "次表面散射"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 次表面散射

## 概述

次表面散射（Subsurface Scattering，SSS）描述光线穿透半透明材质表面后，在材质内部发生多次散射并从不同位置射出的物理现象。与Cook-Torrance模型仅处理表面单点反射不同，SSS承认光子进入介质后会经历复杂的随机游走路径，最终从入射点周边数毫米乃至数厘米处的位置离开材质。这一特性是蜡烛、皮肤、玉石、牛奶等材质呈现出柔和通透视觉效果的根本原因。

SSS的物理研究可追溯至1941年Kubelka和Munk提出的双流模型，该模型首次量化了散射介质的光传输方程。在实时图形学领域，Henrik Wann Jensen于2001年在SIGGRAPH发表的论文《A Practical Model for Subsurface Light Transport》引入了偶极子（Dipole）近似模型，将复杂的体积光传输问题简化为可实时计算的漫反射剖面（Diffusion Profile），从此奠定了游戏与影视渲染中SSS的理论基础。

理解SSS对渲染写实皮肤至关重要：人类皮肤对660nm红光的散射半径约为7-8mm，而对450nm蓝光散射半径仅约1mm，正是这一波长相关性导致皮肤在强光下呈现红润透亮而非灰白的视觉效果。忽略SSS的皮肤渲染会产生"塑料感"——表面高光正确但缺乏内部透光的生命感。

## 核心原理

### 双向散射表面反射分布函数（BSSRDF）

标准Cook-Torrance使用BRDF，假设出射点等于入射点。SSS材质需要更通用的BSSRDF（Bidirectional Scattering Surface Reflectance Distribution Function），其定义为：

$$S(x_i, \omega_i, x_o, \omega_o) = \frac{dL_o(x_o, \omega_o)}{d\Phi_i(x_i, \omega_i)}$$

其中 $x_i$ 为入射位置，$x_o$ 为出射位置，$\omega_i$ 和 $\omega_o$ 分别为入射和出射方向，$\Phi_i$ 为入射辐射通量。由于BSSRDF的完整求解需要对整个表面积分，Jensen将其简化为假设各向同性散射的漫反射剖面函数 $R(r)$，其中 $r = |x_i - x_o|$ 为两点间距离。

### 偶极子漫反射剖面

Jensen的偶极子模型将皮肤等散射介质内的光传输等效为两个虚拟点光源（一个真实光源位于表面以下，一个虚拟负光源位于表面以上）产生的辐照度叠加。最终的漫反射剖面公式为：

$$R(r) = \frac{\alpha'}{4\pi} \left[ z_r \left(\sigma_{tr} + \frac{1}{d_r}\right)\frac{e^{-\sigma_{tr} d_r}}{d_r^2} + z_v \left(\sigma_{tr} + \frac{1}{d_v}\right)\frac{e^{-\sigma_{tr} d_v}}{d_v^2} \right]$$

其中 $\sigma_{tr} = \sqrt{3\sigma_a \sigma_s'}$ 为有效散射系数，$\sigma_a$ 为吸收系数，$\sigma_s'$ 为约化散射系数，$d_r$ 和 $d_v$ 分别为真实光源和虚拟光源到出射点的距离。对于皮肤材质，红色通道的 $\sigma_s'$ 约为1.09 mm⁻¹，绿色通道约为1.59 mm⁻¹，蓝色通道约为1.79 mm⁻¹。

### 屏幕空间次表面散射（SSSSS）

Jorge Jimenez在2009年提出屏幕空间SSS（Screen-Space Subsurface Scattering），其核心思想是：SSS可近似为对屏幕空间漫反射光照图进行加权高斯模糊。具体实现将漫反射剖面 $R(r)$ 分解为6个高斯核的加权和（针对皮肤的红绿蓝三通道分别使用不同宽度），在屏幕空间对辐照度贴图执行可分离的高斯滤波。这种方法的代价是一次额外的渲染Pass和约2-4个模糊Pass，整体开销约为0.3-1.0ms（1080p分辨率，现代GPU）。

### 预积分皮肤渲染

Penner于2010年提出预积分（Pre-Integrated Skin Rendering）方法，将漫反射剖面与球面漫反射的曲率信息预先烘焙到一张2D查找表（LUT）中。该LUT的两个轴分别为 $N \cdot L$（范围-1到1）和 $r/\rho$（曲率半径的倒数，范围0到1）。在着色时，只需采样这张512×512的LUT即可获得考虑了散射效果的漫反射值，开销几乎可以忽略不计，因此被广泛用于实时游戏引擎中。

## 实际应用

**UE4/UE5中的SSS实现**：虚幻引擎提供两种SSS材质着色模型——"Subsurface"使用屏幕空间模糊近似，适合背光透射场景；"Subsurface Profile"使用基于Jimenez改进的分离可扫描（Separable SSS）方法，通过材质的Subsurface Color参数控制散射颜色，Opacity参数控制散射半径，默认皮肤散射半径约为1.2cm。

**蜡烛与玉石渲染**：蜡烛材质的散射系数远大于皮肤，$\sigma_s'$ 约为10-20 mm⁻¹，散射距离达数厘米。实现时通常配合透射（Translucency）贴图，利用"包裹光照"技巧将 $N \cdot L$ 的计算范围从[0,1]扩展到[-0.5, 1]，模拟背面透光效果。

**离线渲染中的路径追踪SSS**：Arnold、RenderMan等离线渲染器使用随机游走（Random Walk）方法直接在体积中追踪光子，每条散射路径需要模拟数十次碰撞，但结果与物理完全一致，无偶极子近似的误差，适用于耳朵等薄层区域的透射渲染。

## 常见误区

**误区一：SSS等同于简单的漫反射模糊**。部分实现将SSS简化为对最终颜色图像进行均匀高斯模糊，但这错误地模糊了镜面高光和阴影边界，应仅对漫反射辐照度分量进行模糊，镜面高光需保持清晰。正确的屏幕空间SSS实现需要将漫反射和镜面反射写入独立的渲染目标，分别处理后合并。

**误区二：所有颜色通道使用相同的散射半径**。皮肤中的血红蛋白对红光（650nm）的散射长度约是蓝光（450nm）的3倍，忽略这一波长依赖性会导致散射后颜色偏灰而不是应有的暖红色调。正确实现必须为RGB三通道分别指定散射距离，通常红：绿：蓝≈1.0：0.5：0.3的比例关系。

**误区三：预积分LUT可以完全替代屏幕空间SSS**。预积分方法假设表面曲率均匀且光照来自单一方向，对于复杂光照环境（如多光源、环境光遮蔽边界处）会产生错误结果。在阴影边缘，预积分会失去SSS独有的"红晕"过渡效果，而屏幕空间方法能正确处理这类情况。

## 知识关联

**与Cook-Torrance模型的扩展关系**：Cook-Torrance解决了单点表面反射的微表面建模问题，而SSS在此基础上引入了空间耦合——出射点的着色结果依赖周围区域的入射光照。两者在最终着色方程中并列存在：最终颜色 = 镜面项（Cook-Torrance）+ 漫反射SSS项，镜面项无需修改，仅漫反射项被SSS剖面替换。

**通向皮肤渲染**：皮肤渲染是SSS最重要的应用场景，需要进一步结合皮肤的多层结构（表皮层厚约0.1mm，真皮层厚1-4mm）建立多极子（Multi-pole）散射模型，并考虑皮肤特有的次级镜面高光（来自角质层的菲涅尔反射）和皮肤微观细节法线贴图的正确处理方式。

**通向眼球渲染**：眼球的角膜、虹膜和巩膜具有完全不同的散射参数，巩膜（眼白）的散射特性与皮肤相近但散射系数更高，虹膜需要特殊的透射模型模拟瞳孔深度。SSS的偶极子模型在眼球渲染中需要适应球形几何体的曲率修正，这与平面假设下的皮肤SSS推导存在本质差异。