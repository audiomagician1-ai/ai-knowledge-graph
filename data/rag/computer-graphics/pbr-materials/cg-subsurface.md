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
quality_tier: "B"
quality_score: 46.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
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

次表面散射（Subsurface Scattering，SSS）描述光线进入半透明材质表面后，在材质内部经历多次散射与吸收，最终从不同于入射点的位置重新射出的物理现象。与Cook-Torrance模型只处理表面反射不同，SSS捕捉的是光在介质体积内部传播的行为。皮肤、牛奶、蜡烛、大理石、玉石等材质在视觉上的柔和透亮感，正是由SSS主导的。

这一现象的物理描述源于辐射传输方程（Radiative Transfer Equation，RTE），1960年代被引入大气光学领域，1990年代随James Kajiya的路径追踪研究逐步进入图形学视野。2001年Jensen等人在SIGGRAPH发表的论文《A Practical Model for Subsurface Light Transport》首次提出双极子扩散近似（Dipole Approximation），将RTE简化为可实时查表的漫射剖面（Diffusion Profile），标志着SSS在实时渲染中走向实用。

在PBR管线中，忽略SSS会导致皮肤在强光下呈现出"橡皮感"——表面仅有高光而缺少向皮下渗透的暖色散射光。正是这种体积内部的红光优先穿透（血红素对红光吸收率低于蓝绿光）赋予了皮肤独特的半透明质感。

## 核心原理

### 双极子扩散模型与漫射剖面

Jensen的双极子模型将皮肤等多层介质简化为均匀的散射介质，利用两个虚拟光源（一个位于表面上方、一个位于表面下方，模拟边界条件）推导出漫射剖面 R(r)：

$$R(r) = \frac{\alpha'}{4\pi} \left[ z_r \left(\sigma_{tr} + \frac{1}{d_r}\right)\frac{e^{-\sigma_{tr} d_r}}{d_r^2} + z_v \left(\sigma_{tr} + \frac{1}{d_v}\right)\frac{e^{-\sigma_{tr} d_v}}{d_v^2} \right]$$

其中 r 是入射点与出射点的水平距离，σ_tr 是有效传输系数，z_r、z_v 分别是真实光源与虚拟光源的深度，d_r、d_v 是对应距离，α' 是减少散射反照率。此函数描述了单位入射通量在距离 r 处重新射出的比例，形状上是一条以入射点为中心、随距离快速衰减的径向曲线。

### 屏幕空间次表面散射（SSSSS）

Jorge Jimenez在2009年提出屏幕空间次表面散射（Screen-Space Subsurface Scattering，SSSSS），将漫射剖面近似为一组高斯函数之和，在后处理阶段对屏幕空间的漫反射缓冲区进行分离卷积。皮肤的漫射剖面可以用6个高斯核叠加拟合，其中宽高斯核（σ ≈ 6mm）捕捉深层红光散射，窄高斯核（σ ≈ 0.08mm）捕捉细节层。分离式高斯卷积将二维卷积分解为水平与垂直两次一维卷积，把复杂度从 O(N²) 降为 O(2N)，使实时运行成为可能。该方法的关键局限是卷积操作在屏幕空间进行，无法感知几何形状，在角色边缘可能产生漏光。

### 预积分皮肤渲染

Penner与Simon在2011年提出预积分方法（Pre-Integrated Skin Rendering），将散射效果预计算进一张以 **dot(N,L)** 和曲率（1/r）为索引的二维查找纹理（LUT）。曲率可以由顶点法线在屏幕空间的变化率估算，或直接由美术人员在顶点色或纹理中手动指定。运行时只需采样这张512×512的LUT并与Albedo相乘，渲染开销极低，适合移动端和主机游戏。该LUT的RGB三通道分别存储红、绿、蓝光的散射积分值，直观地呈现出皮肤在正面受光区域偏暖、在终结子（terminator）区域出现红色渗透带的效果。

### 透射项的处理

当光从背面穿透薄层几何体（如耳廓、手指）时，需要单独计算透射分量。常用方法是用"厚度贴图"（Thickness Map）近似光在几何体内的路径长度 d，透射强度按 e^(-σ_t·d) 衰减，σ_t 是消光系数。Frostbite引擎中，皮肤的散射颜色设定为 RGB(0.48, 0.18, 0.13)，反映了血液对蓝绿光的强吸收特性。

## 实际应用

**UE5皮肤材质**：虚幻引擎5的Shading Model设为`Subsurface Profile`时，引擎在延迟渲染的后处理阶段注入屏幕空间高斯卷积，散射半径和颜色权重存储在Subsurface Profile资产中，美术可直接调节六层高斯核的权重与宽度而无需修改着色器代码。

**蜡烛与玉石**：这两种材质的散射距离远大于皮肤（蜡的平均自由程约1–5mm），在预积分LUT的参数上需要使用更高的散射系数，曲率感知范围也需要扩大。玉石因其各向同性散射，可以在离线渲染中直接用路径追踪的体积散射处理，在实时场景中用厚度贴图乘以绿色主导的散射颜色近似。

**数字人MetaHuman**：Epic的MetaHuman角色在表情捕捉后的最终渲染中，皮肤的散射剖面基于真实人体组织的光学测量值（Krishnaswamy & Baranoski 2004的多层皮肤数据），划分了表皮（Epidermis）和真皮（Dermis）两层，分别赋予不同的散射颜色和深度系数。

## 常见误区

**误区一：SSS等同于半透明（Translucency）**。半透明指光线直接穿透而不改变方向，例如玻璃；SSS指光线在内部多次散射后从邻近位置射出。皮肤几乎不透明，但呈现强烈的SSS效果；而玻璃高度透明但基本不发生SSS。将两者混淆会导致使用Alpha混合代替SSS，完全丢失皮下散射的暖色模糊感。

**误区二：提高漫反射模糊就等同于SSS**。直接对漫反射贴图做模糊处理只是模拟了颜色的空间扩散，但无法重现散射的光照依赖性——SSS的散射程度随曲率和入射角变化，在阴影边界（terminator）处产生的红色渗透带是纯粹的空间模糊无法复现的。预积分方法的核心价值正在于将散射积分与法线-光源夹角耦合，而非简单模糊。

**误区三：SSS只影响漫反射分量**。这在大多数实时方案中是简化假设，实际上高频镜面反射下方的多次散射也会贡献一个宽泛的"次镜面叶瓣"（subsurface lobe）。离线渲染中的皮肤模型（如BSSRDF）对镜面与次表面分量同时积分，只是实时方案出于性能原因将镜面部分单独用Cook-Torrance处理而不计入SSS计算。

## 知识关联

Cook-Torrance模型是理解SSS必要的对比基础：Cook-Torrance的BRDF假设光在入射点处立即反射，输出点与输入点相同，而SSS使用的BSSRDF（双向次表面散射反射分布函数）允许入射点 x_i 与出射点 x_o 不重合，是前者的体积推广形式。若材质的散射平均自由程远小于一个像素对应的物理尺寸，则BSSRDF退化为BRDF，SSS效果可忽略——这正是为何细小颗粒材质如磨砂金属不需要SSS处理。

掌握SSS后，**皮肤渲染**将在此基础上引入多层皮肤结构（表皮黑色素层、真皮血红素层）的分层散射，以及法线贴图在不同频率下分别影响镜面与漫射的解耦处理；**眼球渲染**则将SSS原理延伸至巩膜的血丝散射与角膜的单次散射，同时引入虹膜深度视差等眼球特有效果。