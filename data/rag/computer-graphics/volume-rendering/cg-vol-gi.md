---
id: "cg-vol-gi"
concept: "体积全局光照"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
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
---
# 体积全局光照

## 概述

体积全局光照（Volumetric Global Illumination）是指在参与介质（participating media）内部，光线经过多次散射后形成的间接光照效果的计算方法。与表面渲染中的全局光照不同，体积全局光照必须同时处理三维空间中连续介质的散射累积，而非离散表面之间的光线传递。这使得精确求解体积渲染方程（VRE）中的多重散射项在计算上极其昂贵，因此工程实践中大量依赖近似方法。

该领域的里程碑出现在2014年左右，当Frostbite引擎和Epic Games的Unreal Engine相继将体积雾纳入实时渲染管线时，体积全局光照的近似方案才真正进入工业级应用。其核心挑战在于：单次散射（single scattering）可通过光线步进直接求解，而多重散射（multiple scattering）需要在每个体素位置积分来自四面八方的间接辐射，计算量随散射次数呈指数级增长。

理解体积全局光照对雾、云、烟、次表面散射介质等效果至关重要。在电影级渲染中，云层内部光线经历数百次散射，若没有精确的多重散射近似，会产生明显偏暗的错误结果——这个现象被称为"energy loss"问题，是评价体积全局光照算法质量的重要指标。

## 核心原理

### 体积渲染方程与多重散射项

完整的体积渲染方程（VRE）为：

$$L(\mathbf{x}, \omega) = \int_0^d T(\mathbf{x}, \mathbf{x}_t) \left[ \sigma_s(\mathbf{x}_t) \int_{4\pi} p(\omega_i, \omega) L_i(\mathbf{x}_t, \omega_i) d\omega_i + \sigma_a(\mathbf{x}_t) L_e(\mathbf{x}_t) \right] dt$$

其中 $T(\mathbf{x}, \mathbf{x}_t) = e^{-\int_0^t \sigma_t ds}$ 是透射率，$\sigma_s$ 是散射系数，$\sigma_a$ 是吸收系数，$p(\omega_i, \omega)$ 是相位函数，$L_i$ 项包含了全部间接散射辐射。正是这个 $L_i$ 的递归性质使多重散射计算困难——每个点的间接辐射本身又依赖其他点的辐射。

### 扩散近似（Diffusion Approximation）

当介质光学厚度（optical depth $\tau = \sigma_t \cdot d$）较大时（通常 $\tau > 5$），多重散射的角度分布趋向各向同性，此时可以用扩散方程来近似辐射传输。扩散系数定义为 $D = \frac{1}{3(\sigma_a + \sigma_s')}$，其中约化散射系数 $\sigma_s' = \sigma_s(1 - g)$，$g$ 是Henyey-Greenstein相位函数的各向异性参数。扩散近似将三维体积内的辐射求解简化为一个椭圆型偏微分方程，运算量从 $O(N^3)$ 降低至可预处理的线性系统求解，是离线渲染中云层和皮肤次表面散射的重要基础。

### 体素化全局光照与光照传播体（Light Propagation Volumes）

实时渲染中最常用的体积全局光照近似是**光照传播体（LPV，Light Propagation Volumes）**，由Crytek在2009年的GDC上提出（Anton Kaplanyan）。LPV将场景划分为规则的三维体素网格，每个体素存储用球谐函数（通常为2阶SH，共9个系数）表示的辐射分布。算法分三步：

1. **注入（Inject）**：将虚拟点光源（VPL）注入对应体素；
2. **传播（Propagate）**：迭代地将每个体素的辐射扩散到6个相邻体素，通常迭代8次可收敛；
3. **采样（Sample）**：体积雾或表面渲染时从LPV中查询间接光照。

LPV的精度受制于体素分辨率，在32×32×32网格下，间接光照会出现明显漏光（light leaking）现象。

### 体积辐照度缓存与预积分

另一种方法是在三维体积中存储**辐照度缓存（Irradiance Volume）**。在稀疏探针网格（probe grid）的各节点预计算球谐系数，运行时对体积中任意位置通过三线性插值获取间接光照，再乘以相位函数积分即可得到多重散射贡献。Lumen（UE5中的全局光照系统）在其体积雾模块中采用了类似思路，将体积探针网格与屏幕空间光线追踪结合，实现动态场景下的近似体积全局光照。

### 多重散射近似的指数衰减模型

对于均匀介质，Hillaire在2020年的EGSR论文中提出了一种解析多重散射近似：将多重散射贡献视为无穷散射次数的几何级数之和，其系数可通过对单次散射结果乘以一个依赖反照率 $\rho = \sigma_s / \sigma_t$ 的修正因子 $\frac{1}{1-\rho F_{ms}}$ 来近似，其中 $F_{ms}$ 是预计算的各向同性多重散射查找表。该方法的优势在于仅需一张二维LUT（以 $\sigma_t$ 和 $\rho$ 为参数），在实时大气渲染中每帧增加的额外开销小于0.5ms。

## 实际应用

**大气层渲染**：Sebh Hillaire在《Cyberpunk 2077》和Unreal Engine的天空大气系统中均使用了上述多重散射LUT方法，将云层内部的间接光照误差控制在5%以内，同时保持实时帧率。相比不考虑多重散射的单次散射模型，云层向光面亮度提升约40%，整体视觉结果更接近物理正确。

**体积雾中的间接光照**：在Frostbite引擎中，体积雾通过160×90×64分辨率的三维Froxel（视锥体体素）存储散射光，通过将场景中反射探针（Reflection Probes）的SH系数注入Froxel，近似实现雾中的间接漫反射。这使得洞穴或室内场景的体积雾能够正确地接收来自有色光源反弹的颜色溢出。

**电影级离线渲染**：在RenderMan或Arnold渲染器中，体积路径追踪（Volume Path Tracing）可以精确追踪数十次散射事件，结合重要性采样的相位函数（Henyey-Greenstein），用于处理云层和海水中的光传播。平均需要4096+样本/像素才能使多重散射噪声收敛，是离线渲染最耗时的部分之一。

## 常见误区

**误区一：单次散射已经足够**
许多初学者认为实时渲染中只计算单次散射已足够接近真实。然而在高散射反照率（$\rho > 0.8$）的介质中，如云或浓雾，忽略多重散射会导致介质整体亮度被严重低估——能量损失有时超过60%。这不仅影响视觉亮度，还会错误地改变介质的颜色饱和度，因为不同波长的多重散射路径长度不同。

**误区二：LPV能准确处理高频体积光照变化**
LPV以低阶球谐函数（L2 SH）存储辐射分布，只能表示低频（各向同性为主）的光照变化，无法处理强方向性的间接光照（如阳光透过窗户的折射）。在这种场景下强行使用LPV会产生明显的高频光照丢失和能量错误，应当转用基于光线追踪的方法或辐照度探针代替。

**误区三：扩散近似适用于所有体积介质**
扩散近似要求介质在光学上足够"厚"（$\tau \gg 1$）且散射主导吸收。对于光学薄介质（如晴天大气的蓝天散射，$\tau \approx 0.1$），扩散近似的误差可超过200%，必须退回到单次散射或完整的辐射传输方程求解。

## 知识关联

**前置概念**：参与介质（Participating Media）定义了 $\sigma_s$、$\sigma_a$、$\sigma_t$ 等基础参数以及相位函数的物理意义，是理解体积全局光照中各系数物理含义的前提。只有理解单次散射的路径积分形式，才能明白多重散射是在单次散射基础上添加的递归辐射项。

**横向概念**：体积全局光照与表面全局光照（如屏幕空间AO、光线追踪GI）在算法层面高度类似——LPV和辐照度探针方法都有表面渲染的对应版本，差异在于体积版本需要在三维空间（而非二维表面）中传播辐射，使存储和计算开销提升约32倍（多一个空间维度）。掌握球谐函数的频域特性对同时理解体积和表面间接光照至关重要。
