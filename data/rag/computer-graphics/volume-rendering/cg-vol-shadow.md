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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

体积阴影（Volumetric Shadow）是体积渲染中描述光线穿过参与介质（如雾、烟、云）时因介质吸收和散射而产生能量衰减的光照效果。与表面阴影（Surface Shadow）不同，体积阴影并非简单的二元"遮挡/不遮挡"判断，而是一个连续的透射率（Transmittance）值，反映光线从光源到介质中某采样点的累积衰减程度。

体积阴影的理论基础来源于Beer-Lambert定律（1852年由August Beer系统化），该定律最初用于描述光线穿过化学溶液的衰减行为，后被引入计算机图形学用于模拟参与介质中的光传输。在实时渲染与离线渲染的Pipeline中，体积阴影的求解方式直接影响烟雾、云层、次表面散射等效果的真实感。

在实际渲染场景中，体积阴影带来的视觉特征非常明显：阳光穿过云层边缘时形成的"丁达尔效应"光柱、烟雾中蜡烛被自身遮挡产生的深色阴影区域，都依赖于正确计算介质内部各点对光源的透射率。

---

## 核心原理

### Beer-Lambert定律与透射率公式

体积阴影的数学核心是Beer-Lambert定律。对于均匀介质，透射率 $T$ 由以下公式给出：

$$T = e^{-\sigma_t \cdot d}$$

其中：
- $\sigma_t = \sigma_a + \sigma_s$ 为消光系数（Extinction Coefficient），单位为 $m^{-1}$
- $\sigma_a$ 为吸收系数，$\sigma_s$ 为散射系数
- $d$ 为光线在介质中穿过的距离

对于非均匀介质，该公式推广为积分形式：

$$T(x_0, x_1) = \exp\left(-\int_{x_0}^{x_1} \sigma_t(x)\, dx\right)$$

当 $T=1$ 时介质完全透明，当 $T=0$ 时介质完全不透光。这一连续值正是体积阴影区别于表面阴影的根本所在。

### Shadow Ray Marching

Shadow Ray Marching 是在体积介质中求解上述积分的标准数值方法。其基本流程如下：

1. 对于体积中每个采样点 $P$，向光源方向发射一条**阴影射线（Shadow Ray）**
2. 沿该阴影射线以步长 $\Delta s$（通常为 $0.1\sim1.0$ 单位，取决于介质密度变化频率）均匀或自适应地采样
3. 在每个阴影采样点读取局部消光系数 $\sigma_t$，累加光学深度 $\tau = \sum_i \sigma_t(x_i) \cdot \Delta s$
4. 最终透射率估算为 $T \approx e^{-\tau}$

Shadow Ray Marching 的计算代价很高：若主射线（Primary Ray）有 $N$ 个采样点，每个采样点又进行 $M$ 步阴影采样，则总体积采样次数为 $O(N \times M)$。对于电影级渲染，$N$ 与 $M$ 可分别达到 128 至 512，导致体积阴影成为体积渲染中最耗时的环节之一。

### 透射率估算的优化策略

**Early Exit（提前终止）**：当累积光学深度 $\tau$ 超过阈值（通常取 $\tau > 8$，即 $T < e^{-8} \approx 0.000335$）时，认为透射率已趋近于零，提前终止该条阴影射线的步进，减少无效采样。

**Deep Shadow Map（深度阴影贴图）**：由Lokovic和Veach于2000年在SIGGRAPH提出，将阴影射线从光源视角预计算，沿每条光线方向存储透射率关于深度的函数（以分段折线压缩），渲染时查表代替逐点步进。这将实时查询的复杂度从 $O(M)$ 降至 $O(\log M)$。

**Voxel-Based Transmittance Cache**：将场景离散为体素网格（如 $128^3$ 或 $256^3$ 分辨率），预计算每个体素相对于主光源的透射率并缓存，主渲染Pass直接三线性插值查询，适合密度场在帧间变化缓慢的场景。

---

## 实际应用

### 云层渲染中的自阴影

云朵的体积阴影效果几乎完全依赖Shadow Ray Marching。Horizon Zero Dawn（2017年）的云系统中，游戏团队在光照方向对每个云采样点发射16至32步的阴影射线，并使用粉末效果（Powder Effect）修正项 $1 - e^{-2\sigma_t d}$ 来增强云朵边缘的暗化，使自阴影看起来更厚重真实。如果跳过体积阴影计算，云朵会呈现均匀明亮的"纸片感"。

### 烟雾与爆炸特效

VFX领域（如使用Houdini + Mantra渲染烟雾）中，烟雾自阴影直接来自对光源射线的透射率积分。消光系数 $\sigma_t$ 由烟雾密度场驱动，浓密区域（如爆炸核心部分 $\sigma_t$ 可达 $50\sim200\, m^{-1}$）会产生明显的内部阴影，使爆炸具有层次感，而稀薄外缘则保持较高透射率。

### 实时渲染中的体积阴影近似

在游戏引擎（如Unreal Engine 5）中，完整的Shadow Ray Marching因性能限制常被近似替代。常见方案是在Cascaded Shadow Map（CSM）的基础上叠加低分辨率的Volumetric Fog Shadow Pass，以 $4\sim8$ 步的极少采样获得近似透射率，再通过时间抗锯齿（TAA）在帧间积累补偿质量不足的问题。

---

## 常见误区

**误区一：将体积阴影等同于表面阴影的遮挡判断**

初学者容易将阴影射线视为普通Shadow Ray，认为"打到介质就算遮挡"。实际上介质的遮挡是连续的透射率值，同一光线穿过密度不均的雾气时，可能前半段几乎透明（$T\approx0.9$）而后半段极度衰减（$T\approx0.02$）。忽略这一连续性会导致体积阴影呈现生硬的硬阴影边界，完全丧失体积感。

**误区二：步长越小结果越准确且代价线性增长**

Shadow Ray Marching的步长选择存在下限价值递减问题。将步长从 $\Delta s = 0.1$ 缩小到 $\Delta s = 0.01$ 时，在低频密度场中精度提升微乎其微，但采样数增加10倍。正确做法是结合介质密度的空间频率选择步长：密度变化频率高（如精细烟雾）时用小步长，稳定均匀介质（如薄雾）用大步长，或使用自适应步进策略。

**误区三：Deep Shadow Map可以完全替代实时Shadow Ray Marching**

Deep Shadow Map预计算的是静态或慢变密度场的透射率。对于实时动态烟雾（如粒子系统驱动的爆炸），密度场每帧都在变化，预计算缓存会立即失效。此时仍需在每帧执行Shadow Ray Marching，Deep Shadow Map仅适用于密度场静态或变化极缓的离线渲染场景。

---

## 知识关联

体积阴影建立在**参与介质**的消光系数 $\sigma_t$、吸收系数 $\sigma_a$ 与散射系数 $\sigma_s$ 的定义之上——若不理解这三个参数的物理含义，Beer-Lambert定律中的指数衰减就无法正确配置，导致透射率估算出现数量级偏差。

从Shadow Ray Marching的实现出发，还需要理解**Ray Marching**基础框架（主射线步进与阴影射线步进共享相似的数值积分结构）以及体积渲染方程（VRE）中的自发光项 $L_e$ 与散射项 $L_s$ 如何依赖透射率 $T$ 进行权重调制——体积阴影本质上是渲染方程内光源可见性函数的连续化推广。

在工程实现层面，理解**3D纹理采样**与三线性插值对Voxel-Based方案的性能影响，以及GPU上如何组织阴影射线步进的着色器并行结构，是将体积阴影从原理转化为可运行渲染器的必要工程知识。