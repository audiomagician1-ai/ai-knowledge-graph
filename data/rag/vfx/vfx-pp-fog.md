---
id: "vfx-pp-fog"
concept: "体积雾"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 体积雾

## 概述

体积雾（Volumetric Fog）是一种模拟光线在参与介质（participating media）中散射与衰减的后处理渲染技术。不同于简单的距离雾（depth fog）仅根据像素深度值叠加颜色，体积雾将空间中的雾气视为具有密度、散射系数和吸收系数的三维体积，计算光子在该介质内经历的多次散射路径，从而产生丁达尔效应（Tyndall effect）所呈现的光柱、光晕等视觉现象，即俗称的"God Ray"。

该技术的理论基础来自辐射传输方程（Radiative Transfer Equation，RTE），最早在离线渲染领域（如电影视觉特效）中广泛应用，2010年代随着GPU可编程管线的成熟逐步进入实时渲染范畴。Frostbite引擎在2015年GDC上发表的《Physically Based and Unified Volumetric Rendering》是实时体积雾的里程碑论文，将体积雾的实时计算误差控制在视觉可接受范围内。

体积雾在游戏和影视特效中承担着极强的场景氛围塑造职能：丛林中穿透树冠的上帝之光、地下城内流动的薄雾、爆炸后的烟尘散射，均依赖体积雾实现。若缺乏该效果，场景会显得干燥且缺乏空气感，光源也失去真实的体积感。

---

## 核心原理

### 辐射传输方程与相位函数

体积雾的物理核心是辐射传输方程，其简化形式为：

$$\frac{dL}{ds} = -(\sigma_a + \sigma_s) \cdot L + \sigma_s \cdot \int_{4\pi} p(\omega, \omega') \cdot L_i(\omega') \, d\omega'$$

其中：
- $\sigma_a$ 为介质的**吸收系数**，描述光被介质吸收的比率
- $\sigma_s$ 为介质的**散射系数**，描述光被介质改变方向的比率
- $p(\omega, \omega')$ 为**相位函数**，描述光从方向 $\omega'$ 散射到方向 $\omega$ 的概率分布

实时渲染中常用 **Henyey-Greenstein 相位函数**近似散射行为：

$$p_{HG}(g, \theta) = \frac{1 - g^2}{4\pi (1 + g^2 - 2g\cos\theta)^{3/2}}$$

参数 $g \in [-1, 1]$：$g=0$ 表示各向同性散射，$g>0$ 表示前向散射（如薄雾），$g<0$ 表示后向散射（如浓烟）。God Ray效果通常使用 $g \approx 0.7\text{–}0.9$ 的强前向散射。

### 视锥体体素化（Froxel）技术

实时体积雾的主流实现方案是将摄像机视锥体（frustum）离散化为三维纹理网格，每个单元称为 **Froxel**（frustum voxel 的合称）。典型的分辨率为屏幕分辨率的 1/8，深度方向分为 64~128 个切片，切片分布通常采用对数分布，使近处细节更密集。

渲染流程分三步：
1. **密度注入（Density Injection）**：向三维纹理写入每个Froxel的散射系数、吸收系数和发光量，支持噪声函数调制以模拟湍流雾气。
2. **光照散射计算（Light Scattering）**：对每个Froxel累加来自方向光、点光源的in-scattering贡献，方向光需结合级联阴影贴图（CSM）判断遮挡。
3. **沿视线积分（Ray Marching Integration）**：沿视线方向从近到远累积透射率和散射光，得到体积雾的最终颜色和不透明度，写入屏幕空间的雾效缓冲区与主图像合成。

### 高度雾（Height Fog）的解析近似

高度雾是体积雾的一种特殊简化形式，假设雾的密度 $\rho$ 随高度 $h$ 呈指数衰减：

$$\rho(h) = \rho_0 \cdot e^{-k \cdot h}$$

其中 $\rho_0$ 为海平面密度，$k$ 为衰减系数。该形式允许对沿视线的光学深度进行解析积分而无需ray marching，计算量仅为一次全屏pass，适合移动端等性能受限场景。Unreal Engine 4的Exponential Height Fog组件即基于此原理实现，并提供两层叠加支持以模拟低云层与地表薄雾共存的效果。

---

## 实际应用

**场景氛围：丛林/圣光效果**
在光源方向与摄像机之间放置遮挡物（树冠、窗框），体积雾的in-scattering计算会在光线透过间隙处产生明显的光柱，即God Ray。Frostbite的实现中，方向光的光柱效果通过在Froxel阶段对CSM采样并累积散射贡献实现，无需额外的屏幕空间后处理。

**粒子系统与体积雾联动**
爆炸、烟雾、水面蒸汽等粒子效果可将自身的密度写入Froxel三维纹理，使粒子烟雾同样参与光照散射计算，从而产生自然的烟雾内光晕，而不是像传统Billboard粒子那样显得平板。Unity HDRP的Local Volumetric Fog组件支持通过3D纹理蒙版控制局部密度，分辨率上限为64³体素。

**水下散射效果**
水下场景中将介质散射系数 $\sigma_s$ 调高、吸收系数 $\sigma_a$ 设置为强烈的红色衰减（水对红光吸收率高），即可模拟水下特有的蓝绿色丁达尔散射，该效果在《Subnautica》等深海题材游戏中被大量使用。

---

## 常见误区

**误区一：体积雾等同于屏幕空间的God Ray后处理**
屏幕空间God Ray（如径向模糊法）是将光源周围的亮度进行屏幕空间模糊，属于近似欺骗技巧，在光源被遮挡时会产生错误结果（光柱穿透不透明物体）。真正的体积雾God Ray在Froxel阶段就已考虑阴影遮挡，两者原理和质量存在本质差异，不可混用概念。

**误区二：雾的密度越高视觉效果越真实**
过高的散射系数 $\sigma_s$ 会导致多次散射能量丢失（单次散射近似误差放大），表现为雾气颜色偏暗甚至发黑，而非现实中高密度雾的白色乳浊效果。实际工程中需配合增加**环境散射项（ambient scattering）**或多次散射近似（如Frostbite的多散射LUT方案）来补偿高密度情况。

**误区三：高度雾可以完全替代体积雾**
指数高度雾的解析积分假设密度场是均匀分层的，无法模拟局部浓雾团、流动烟雾或带有阴影遮挡的体积光。凡是需要光源投射可见光柱、雾气具有非均匀密度分布、或雾气内部存在自发光（如魔法粒子）的场景，均需切换到完整的Froxel体积雾方案。

---

## 知识关联

**前置概念：屏幕空间反射（SSR）**
体积雾与SSR同属后处理特效管线，共同使用深度缓冲区重建像素的世界空间位置。SSR通过深度缓冲追踪反射光线，体积雾的Froxel深度切片也依赖精确的深度信息来正确定位雾气在视锥体中的位置，二者在深度缓冲的读取和视锥体重建（frustum reconstruction）上共享基础技术。

**后续概念：描边效果（Outline Effect）**
描边效果同样属于屏幕空间后处理阶段，通常在体积雾合成之后执行，以避免描边线条被雾气效果淡化。在距离摄像机较远的物体上，体积雾的透射率会显著降低物体边缘的对比度，这要求描边算法在检测边缘时需要考虑雾效深度衰减权重，或直接在雾效合成前完成描边写入，两者的执行顺序对最终画质有直接影响。