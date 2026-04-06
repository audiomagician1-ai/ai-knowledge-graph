---
id: "cg-gi-hybrid"
concept: "混合GI方案"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 4
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 82.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "academic"
    author: "Majercik, A., Müller, T., Nowrouzezahrai, D., & McGuire, M."
    year: 2019
    title: "Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields"
    venue: "Journal of Computer Graphics Techniques (JCGT), Vol. 8, No. 2"
  - type: "academic"
    author: "Lumen Technical Team (Wihlidal, G. et al.)"
    year: 2022
    title: "Lumen: Real-time Global Illumination in Unreal Engine 5"
    venue: "SIGGRAPH 2022 Advances in Real-Time Rendering Course"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---

# 混合GI方案

## 概述

混合GI方案（Hybrid Global Illumination，简称Hybrid GI）是将离线烘焙光照贴图（Baked Lightmap）、实时光照探针（Light Probe）以及屏幕空间全局光照（SSGI，Screen Space Global Illumination）三种技术叠加组合，以覆盖不同空间频率和动态程度光照需求的多层次渲染策略。该方案的核心诉求来自于单一GI技术无法同时满足静态低频环境光、动态物体间接光响应以及近距离高频接触光等三类截然不同的光照现象。

混合GI的系统化实践在2017年前后随Unreal Engine 4.18的"距离场AO + 光照贴图 + 反射捕获"管线组合而广泛普及；Unity的Enlighten Realtime GI（最初集成于Unity 5.0，2015年发布）与烘焙GI共存的双模式架构也在同期形成行业标准。这种分层思想的理论依据是球谐函数（Spherical Harmonics，SH）的频率分离特性：低频项（$L_0$、$L_1$，即直流与偶极项，共4个系数/通道）适合探针存储，中频（$L_2$ 项，9个系数/通道的二阶SH）适合光照贴图，而高频细节则依赖屏幕空间重建。

混合GI方案的意义在于它是目前大型开放世界游戏能够实现兼顾画质与性能的核心工程路径。《赛博朋克2077》（CD Projekt Red，2020年）、《荒野大镖客：救赎2》（Rockstar Games，2018年）以及《地平线：零之曙光》（Guerrilla Games，2017年）等AAA作品的GI实现均属于此类混合方案，而非依赖任何单一技术。

## 核心原理

### 分层覆盖模型

混合方案将空间划分为三个作用域，每层负责不同频率的光照贡献，形成互补而非竞争的关系：

- **烘焙层（Baked Layer）**：处理静态几何体之间的低频间接光，典型分辨率为每Texel覆盖10–50 cm的世界空间，存储于Lightmap Atlas中。该层对动态物体完全透明，仅贡献静态表面的漫反射辐照度（Irradiance）。烘焙工具（如UE4的Lightmass，于2008年随UE3引入）通常采用路径追踪或光子映射计算，离线时间从数分钟到数小时不等。
- **探针层（Probe Layer）**：使用三阶球谐（SH9，即每颜色通道9个系数，RGB共27个浮点值）或Irradiance Cubemap捕获动态物体所在位置的环境辐照度。更新频率通常为每帧局部刷新全部探针的1/4体积，或基于物体位移超过阈值（通常为0.5米）时触发局部重烘。
- **屏幕空间层（Screen Space Layer，SSGI）**：以当前帧的GBuffer（深度缓冲、法线缓冲、颜色/反照率缓冲）为输入，利用光线步进（Ray Marching）或随机半球采样（Stochastic Hemisphere Sampling）重建近场间接漫反射。典型参数为：采样半径0.5–3米，每像素8–16条射线，以1/2分辨率渲染后经双边上采样（Bilateral Upsample）恢复全分辨率。

三层按优先级叠加：SSGI结果叠加在探针层之上，探针层填补SSGI的屏幕外信息缺失，烘焙层作为全局基底兜底。混合权重公式写为：

$$L_{\text{final}} = L_{\text{baked}} \cdot w_b + L_{\text{probe}} \cdot (1 - w_{ss}) + L_{\text{ssgi}} \cdot w_{ss}$$

其中 $w_{ss}$ 由SSGI射线命中置信度（Hit Confidence，取值范围0–1）驱动——命中率低于阈值（通常为0.3）时，$w_{ss}$ 自动衰减至0，GI贡献完全退化至探针层，从而保证画面稳定性。能量守恒要求各层有效贡献在像素级归一化，避免叠加后总辐照度超出物理上限。

### 球谐函数的频率分析

球谐函数是定义在单位球面上的一组正交基函数，第 $l$ 阶共有 $2l+1$ 个基函数，前三阶（$l=0,1,2$）合计9个基函数，称为SH9。其辐照度重建公式为：

$$E(\mathbf{n}) = \sum_{l=0}^{2} \sum_{m=-l}^{l} L_{lm} \cdot Y_{lm}(\mathbf{n})$$

其中 $\mathbf{n}$ 为表面法线方向，$L_{lm}$ 为第 $l$ 阶第 $m$ 次谐波系数，$Y_{lm}$ 为对应基函数。SH9可准确重建低频漫反射辐照度，对于Lambertian BRDF而言，$l \geq 3$ 阶的高频项贡献可忽略不计（能量占比不足1%），这正是探针选用SH9而非更高阶的理论依据（Ramamoorthi & Hanrahan，2001年证明）。

例如，在一个有红色砖墙和白色天花板的室内场景中，探针捕获的SH9系数的 $L_0$（直流项）编码了场景平均亮度约0.4 nit，$L_1$（偶极项）编码了来自右侧红墙方向的彩色溢色（Color Bleeding），而高频的砖缝阴影细节则完全依赖Lightmap中预计算的遮蔽图来呈现。

### 探针与烘焙的接缝处理

烘焙Lightmap与探针采样之间的颜色不一致（Seam/Leaking）是混合方案最典型的技术挑战。标准做法是在烘焙阶段将探针的SH系数作为约束条件写入，使Lightmap的平均辐照度与探针读数在数值上对齐，误差容忍度通常要求在0.02 nit以内。Unity于2022年（Unity 2022 LTS）引入的Adaptive Probe Volumes（APV）通过体素化探针网格替代传统手动放置，探针密度可根据几何复杂度自适应调整（稀疏区域每3米一个，复杂区域每0.5米一个），使接缝问题从美术手工调整流程转为引擎自动处理，节省了大型场景下约60%的美术调整工时（据Unity 2022技术报告）。

### 时域稳定性控制

SSGI层对摄像机移动极为敏感，快速移动时会产生"鬼影"（Ghosting）或"萤火虫"噪点（Firefly）。混合方案通常在SSGI之上叠加时域累积滤波（TAA风格的Temporal Reprojection），利用Motion Vector将历史帧混合比例（History Blend Factor）限制在0.85–0.92之间（即当前帧权重为0.08–0.15），并以深度差（$\Delta d > 0.1$ 米）和法线差（$\Delta \theta > 15°$）作为历史拒绝条件，防止遮挡不连续处的历史帧信息污染当前帧。时域滤波有效地将8射线/像素的噪声质量提升至等效64射线的视觉效果，是SSGI得以在实时渲染中实用化的关键技术。

## 实际应用案例

**Unreal Engine 5 的 Lumen 降级方案**：Lumen（Epic Games，2021年随UE5发布）在PC和次世代主机端作为全实时GI方案运行，但在移动端或低端硬件上会自动降级为烘焙Lightmap + SSGI混合模式。降级触发阈值为GI步骤帧时间超过4ms，降级后整体GI性能开销可从约8ms降至约1.5ms，体现了混合方案在跨平台部署中不可替代的实用价值（Wihlidal et al.，SIGGRAPH 2022）。

**开放世界动态昼夜循环**：《地平线：零之曙光》采用烘焙4套时间段Lightmap（黎明06:00、正午12:00、黄昏18:00、夜晚00:00）并在运行时按太阳仰角进行双线性插值，同时以实时天空球探针（每帧完整更新，分辨率64×64 HDR Cubemap）覆盖动态天光变化，SSGI处理草地与岩石间的近场漫反射（半径约1.5米）。这使得整个24小时昼夜周期的GI过渡平滑，无明显烘焙感，同时将动态天光的实时计算量控制在每帧约0.8ms之内。

例如，在正午至黄昏过渡阶段（太阳仰角从90°降至20°），系统按插值因子 $t = 0.6$ 混合正午与黄昏两套Lightmap，同时天空探针实时更新为橙红色调，SSGI则实时响应岩石背光面出现的暖色调间接光——三层协作完成了单层技术无法独立实现的光照效果。

**室内角色照明**：在密闭室内场景中，光照探针密度可提升至每1米3个探针。例如，一个约20米×10米的室内空间布置约600个探针，配合烘焙的墙面二次反弹光（Secondary Bounce），角色在靠近彩色墙壁时会从探针中采样到正确的彩色溢色，而SSGI则补充角色脚部与地面之间0–0.3米范围内的接触遮蔽与短程间接光，使角色与场景的融合感显著提升。

## 常见误区与注意事项

**误区一：认为SSGI可以完全替代探针层**

SSGI仅能重建屏幕内可见表面的间接光，当光源、反射面或遮挡物处于视野之外时，SSGI贡献为零，且无法平滑退化，会产生突兀的暗部。探针层覆盖的正是这部分"屏幕外辐照度（Off-Screen Irradiance）"，两者作用域不重叠而非竞争关系。去掉探针层后，角色走到门口时会因屏幕外室外光照丢失而出现明显的亮度跳变，通常表现为亮度在0.3秒内骤降约40%，破坏光照连贯性。

**误区二：烘焙层仅适用于全静态场景**

即使在全动态场景中，烘焙层仍可存储预计算环境遮蔽因子（Pre-baked AO Factor），使动态对象的探针采样结果乘以遮蔽权重，避免探针在狭窄空间（如走廊宽度小于2米）中产生过曝。完全抛弃烘焙层的方案在遮蔽密集区域会呈现不自然的高辐照度，亮度误差可达真实值的2–3倍。

**误区三：三层权重可凭美术经验随意调整**

三层混合权重若不以能量守恒为约束，叠加后总辐照度会超过物理