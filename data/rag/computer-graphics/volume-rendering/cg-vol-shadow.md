---
id: "cg-vol-shadow"
concept: "体积阴影"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 3
is_milestone: false
tags: ["光照"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 体积阴影

## 概述

体积阴影（Volumetric Shadow）是体积渲染中用于计算光线在参与介质（如云、烟雾、大气）内部传播时被遮挡和衰减的技术。与表面渲染的硬阴影不同，体积阴影不是简单的二值（照亮/遮挡），而是一个连续衰减过程——光线从光源到达介质内某一采样点的过程中，介质本身会吸收和散射光子，导致该点接收到的光强度小于光源原始强度。

体积阴影的计算方法源自大气光学中的Beer-Lambert定律，该定律由Johann Heinrich Lambert于1760年发表，后由August Beer于1852年扩展。在计算机图形学中，Perlin和Hoffert在1989年的论文《Hypertexture》中首次将类似思想应用于体积烟雾渲染。现代实时图形引擎（如Unreal Engine和Unity的HDRP管线）均内置了不同精度等级的体积阴影实现。

在物理正确的体积渲染方程中，若忽略体积阴影，介质内部各点的光照贡献将被严重高估，导致烟雾、云层等效果完全缺乏内部结构和深度感。正是体积阴影使烟柱底部比顶部更暗、云层内核比边缘更阴沉——这些视觉特征对于真实感渲染至关重要。

---

## 核心原理

### Beer-Lambert衰减与透射率

体积阴影的数学基础是透射率（Transmittance）函数。给定一条从点 **x** 沿方向 **ω** 到点 **y** 的光线路径，透射率定义为：

$$T(\mathbf{x}, \mathbf{y}) = \exp\!\left(-\int_{\mathbf{x}}^{\mathbf{y}} \sigma_t(\mathbf{p})\, \mathrm{d}s\right)$$

其中：
- $\sigma_t(\mathbf{p}) = \sigma_a(\mathbf{p}) + \sigma_s(\mathbf{p})$ 是消光系数（extinction coefficient），单位为 m⁻¹ 或 cm⁻¹
- $\sigma_a$ 是吸收系数，$\sigma_s$ 是散射系数
- 积分路径为从采样点到光源的线段

当 $\sigma_t$ 均匀时，透射率退化为 $T = e^{-\sigma_t \cdot d}$，其中 $d$ 是路径长度。当介质密度不均匀（如噪声生成的云）时，必须通过数值积分估算这个指数函数内的光学深度（optical depth）。

### Shadow Ray Marching

计算体积阴影的主要方法称为**Shadow Ray Marching（阴影光线步进）**。在主摄像机光线的每个采样点处，向光源方向额外发射一条"阴影光线"，沿该光线进行步进采样以估算透射率：

$$T \approx \exp\!\left(-\sum_{i=1}^{N_s} \sigma_t(\mathbf{p}_i) \cdot \Delta s_i\right)$$

其中 $N_s$ 是阴影光线的步进步数，$\Delta s_i$ 是每步的间隔长度。阴影光线步进是体积渲染中计算开销最大的部分之一：若主光线有64个采样点，每个采样点的阴影光线又需要8步，总共需要 $64 \times 8 = 512$ 次密度采样，仅针对单个光源。

步进策略的选择对精度和性能影响显著。**等步长步进**实现简单但效率低；**自适应步进**在密度梯度大的区域缩短步长，空旷区域加大步长；**随机偏移**（jittering）可以通过低频随机数扰动采样位置，将规则步进的条纹伪影转化为噪声，再通过时间抗锯齿（TAA）消除。

### 深度阴影贴图与Voxel方法

为避免每帧对每个采样点重新执行Shadow Ray Marching，实时渲染引入了预计算方案。**深度阴影贴图（Deep Shadow Maps，Lokovic & Veach, 2000）**从光源视角预存储沿光线方向累积的透射率函数，以分段线性曲线表示每个像素上透射率随深度的变化，可在渲染时快速查表。

另一种方案是**Voxel阴影（Voxel Shadow）**：将体积介质体素化到3D纹理中，沿光源方向逐切片累积光学深度，生成一张"光传播3D纹理"。Unreal Engine 5的**Volumetric Fog**功能即使用此类Froxel（视锥体素，frustum-aligned voxel）方法，将场景划分为160×90×64的视锥体素格，每帧以Compute Shader计算光照累积。

---

## 实际应用

**云与大气渲染**：游戏《地平线：零之曙光》使用体积云系统，其中每朵云的自阴影通过6方向的预计算透射率近似实现，避免了实时Shadow Ray Marching的高开销。光照从云顶向下穿透时，越深处透射率越低，形成明显的丁达尔效应（Tyndall Effect）。

**烟雾与爆炸粒子**：影视级渲染（如Houdini + Karma渲染器）中，烟雾模拟每个体素的 $\sigma_t$ 值从流体模拟中获取（密度场），Shadow Ray Marching步数通常设置为32至128步，以还原烟柱内部的光轴（god ray）效果。

**实时引擎的权衡**：Unity HDRP的Volumetric Fog默认使用64个Froxel深度切片，阴影投射通过级联阴影贴图（CSM）与体积密度场相乘近似，而非精确的光线步进，换取移动/主机平台的实时帧率。

---

## 常见误区

**误区一：体积阴影等同于光线是否能"照到"该点**
体积阴影不是二值判断，而是连续的透射率 $T \in [0,1]$。即使光线路径上有密集介质，透射率也不会精确到零（除非光学深度趋向无穷）。直接用表面阴影的"是否在阴影内"逻辑处理体积介质，会产生硬边伪影，丢失介质的半透明体积感。

**误区二：阴影光线步进步数越多越好**
Shadow Ray Marching的精度瓶颈通常在密度采样的空间频率而非步数。当介质密度由Perlin噪声等低频函数生成时，8至16步的阴影步进与64步的结果视觉差异极小，但性能开销相差8倍。过多的步数只在介质有高频细节（如Worley噪声生成的卷积云）时才能体现差异。

**误区三：体积阴影只影响介质内部**
体积介质同样可以在其表面之外投射阴影到场景几何体上。烟雾遮挡光源时，地面上会出现柔和的体积阴影投影，这需要在计算几何体表面光照时也纳入介质的透射率，而非仅在体积渲染通道内处理。

---

## 知识关联

体积阴影建立在**参与介质**（Participating Media）的物理模型之上：消光系数 $\sigma_t$ 的定义、吸收与散射的区别，以及Beer-Lambert定律的适用前提（无多次散射路径干涉）都来自参与介质的基础理论。只有理解为何介质会消减光强，才能正确设置 $\sigma_t$ 的数值范围（空气约 $10^{-4}$ m⁻¹，密集云约 $10$ m⁻¹）。

体积阴影与**体积散射**（单次散射/多次散射）紧密配合：透射率 $T(\mathbf{x},\mathbf{y})$ 作为权重系数，乘以散射相位函数的积分结果，共同构成完整的体积光照方程 $L_s = \int \sigma_s \cdot p(\omega, \omega') \cdot T \cdot L_i \, \mathrm{d}\omega'$。此外，**时间重投影与降噪**技术（如TAA和DLSS）是解决体积阴影步进噪声的工程实践方向，在理解体积阴影的计算开销后自然引出对这些优化技术的需求。