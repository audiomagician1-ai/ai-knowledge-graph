---
id: "cg-ssr"
concept: "屏幕空间反射"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 82.5
generation_method: "ai-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v2"
  - type: "academic"
    citation: "McGuire, M., & Mara, M. (2014). Efficient GPU Screen-Space Ray Tracing. Journal of Computer Graphics Techniques, 3(4), 73–85."
  - type: "book-chapter"
    citation: "Uludag, Y. (2014). Hi-Z Screen-Space Cone-Traced Reflections. GPU Pro 5: Advanced Rendering Techniques, CRC Press, pp. 149–192."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 屏幕空间反射

## 概述

屏幕空间反射（Screen-Space Reflection，SSR）是一种利用已渲染帧的深度缓冲和颜色缓冲来计算反射效果的实时图形后处理技术。与传统的平面反射或立方体贴图反射不同，SSR 能够反映出场景中动态物体、角色和粒子效果，因为其采样来源是当前帧实际渲染的像素内容，而非预烘焙的静态数据。

SSR 最早在 2011 年由 Morgan McGuire 和 Michael Mara 在其论文 *Efficient GPU Screen-Space Ray Tracing* 中系统化地提出（后于 2014 年发表于 JCGT），随后在 Ubisoft、Epic Games 等公司的商业引擎中得到广泛应用。虚幻引擎 4 在 2014 年将 SSR 作为标准后处理选项正式引入，推动了该技术在次世代游戏开发中的普及。Unity HDRP 则于 2018 年随 Unity 2018.1 版本正式提供生产级 SSR 支持，进一步扩大了该技术的工程受众。

SSR 之所以重要，在于它以极低的额外渲染 Pass 代价补全了延迟渲染管线中金属和高光材质的视觉完整性。地板反射、水面倒影、湿润石材等效果均依赖 SSR 才能在不使用光线追踪硬件的条件下实现可信的实时结果。在 GTX 1080 级别硬件上，SSR 的典型帧时预算约为 **1.5～2.5ms**（1080p 半分辨率渲染），相比之下实时光追反射通常消耗 **8～15ms**，性价比差距显著。

> **思考问题：** 为什么 SSR 只能在延迟渲染或带有 Pre-Pass 的正向渲染管线中使用，而无法直接应用于纯正向渲染？这一约束对引擎架构设计有何影响？

---

## 核心原理

### 屏幕空间光线步进（Ray Marching in Screen Space）

SSR 的基础算法是从着色点沿反射向量在屏幕空间内逐步推进。反射向量的计算公式为：

$\mathbf{R} = \mathbf{V} - 2(\mathbf{V} \cdot \mathbf{N})\mathbf{N}$

其中 $\mathbf{V}$ 为从着色点指向摄像机的单位视线方向向量，$\mathbf{N}$ 为着色点处的世界空间单位法线向量。等价地，在 HLSL/GLSL 中可写作 `R = reflect(-V, N)`。

将反射光线从观察空间变换到裁剪空间后，沿像素坐标方向迭代步进，每步采样当前深度缓冲值与步进点深度进行比较，若步进点深度大于缓冲深度（即射线穿入几何体），则认为在该处发生相交，并读取对应颜色缓冲作为反射颜色。

线性步进的致命缺陷是步长均匀，每帧需要 **32～64 次**纹理采样才能保证精度，在 1080p 全分辨率下 GPU 带宽压力极大，通常须降至半分辨率（960×540）执行以维持性能。

### Hi-Z 加速光线步进（Hierarchical-Z Ray March）

Hi-Z Ray March 是 SSR 的核心优化手段，由 Yasin Uludag 在 *GPU Pro 5*（2014年，CRC Press）中详细描述。其核心思路是为深度缓冲构建一个多层级的深度最大值金字塔（Hierarchical Depth Buffer，Hi-Z），结构类似 MIP Map，但每一层存储的是对应区域像素的**最大深度值**（即最远深度，NDC 空间中数值最大），而非平均值。

Hi-Z 层级总数的计算公式为：

$L = \lceil \log_2(\max(W, H)) \rceil$

例如，对于分辨率为 1920×1080 的 G-Buffer，$L = \lceil \log_2(1920) \rceil = \lceil 10.9 \rceil = 11$，即需要构建 **11 层**深度金字塔；而在半分辨率（960×540）下执行 SSR 时，$L = \lceil \log_2(960) \rceil = 10$，仅需 **10 层**。

光线步进时采用"升降级"策略：
1. **从高层级（粗粒度）开始**，快速跳过大片无交叉区域；
2. 若当前层级的最大深度小于射线深度，说明该区域无任何几何遮挡，直接跳跃 $2^{\text{level}}$ 个像素；
3. 若存在潜在交叉，则降回更低层级（更细粒度）精确检测，直至第 0 层（像素级精度）。

这使采样次数从线性步进的 64 次降低到通常只需 **16～24 次**，性能提升约 **3 倍**，特别是在反射光线接近水平方向（掠射角，grazing angle）时效果最为显著。

例如，在 Epic Games 于 2014 年 GDC 演讲中披露的 UE4 SSR 数据中，Hi-Z 优化使复杂城市场景的 SSR Pass 从线性步进的 4.2ms 降低至 1.4ms（PS4 硬件，1080p 半分辨率）。

### 反射颜色采样与消隐

确定交叉点后，SSR 需要处理两个关键问题：

**边界消隐（Edge Fade）**：当反射光线超出屏幕边界或指向摄像机背面时，无法获得有效颜色，需要根据光线终点与屏幕边缘的距离进行淡出衰减处理，公式为：

$\text{fade} = 1 - \text{saturate}\!\left(\frac{|uv - 0.5| \times 2 - t}{1 - t}\right)$

其中阈值 $t$ 通常取 **0.8**，即在屏幕边缘 20% 的区域线性淡出至 0，避免屏幕外反射突然消失产生的视觉跳变。

**粗糙度混合**：SSR 反射结果需与材质粗糙度（Roughness）结合，常见做法是根据 roughness 值在 SSR 颜色与环境球谐/IBL 之间进行混合。当 $\text{roughness} > 0.5$ 时通常完全回退到 IBL，因为 Hi-Z 步进无法高效模拟散焦模糊反射，此时计算量不成比例地上升而视觉增益极低。

---

## 时序降噪与 TAA 集成

现代引擎中的 SSR 并非孤立的单帧算法，而是深度依赖**时序累积抗锯齿（Temporal Anti-Aliasing，TAA）** 的重建机制。Unity HDRP 技术文档（2021）与 Unreal Engine 源码注释均记载了该设计：将每像素射线数降至 **1 次**，依靠 TAA 的历史帧混合（历史权重通常为 0.9）在时域上重建高质量反射结果。

其混合公式为：

$C_{\text{out}} = \alpha \cdot C_{\text{history}} + (1 - \alpha) \cdot C_{\text{current}}$

其中 $\alpha$ 为历史帧权重，典型取值 $\alpha = 0.9$；$C_{\text{current}}$ 为当前帧 SSR 单次采样颜色，$C_{\text{history}}$ 为经运动矢量重投影后的历史帧结果。当场景静止时，经过约 **10 帧**累积后，信噪比接近每像素 10 次采样的效果。

这一设计使 Hi-Z SSR 在 1080p 分辨率下的总开销降至约 **0.8ms**（RTX 3060 级别硬件），成为当前引擎工程实践中最常见的 SSR 配置。

> **例如**，在 Unity HDRP 的 `HDRenderPipeline.RenderSSR()` 流程中，SSR Trace Pass（Hi-Z 步进）与 SSR Accumulation Pass（TAA 混合）分别作为独立的 Compute Shader 调度，前者耗时约 0.4ms，后者约 0.3ms，合计约 0.7ms（测试平台：RTX 3070，1440p，半分辨率追踪）。

---

## 实际应用

**游戏中的地板反射**：《赛博朋克 2077》（CD Projekt Red，2020）和《地平线：禁忌之西》（Guerrilla Games，2022）均使用 SSR 渲染城市湿润地面的动态反射。与光线追踪反射相比，SSR 在中等配置显卡上（如 GTX 1080）可将帧时保持在 **2ms 以内**，而光追反射通常消耗 **8～15ms**，在不支持 DXR 的硬件上更是完全无法使用。

**延迟渲染的集成方式**：SSR 作为后处理 Pass 在延迟渲染的 Lighting Pass 之后执行。它直接读取 G-Buffer 中的世界法线（通常为 RG16F 格式存储，共 4 字节/像素）和线性深度缓冲，以及 HDR 颜色缓冲（通常为 R11G11B10F 格式，共 4 字节/像素）。这种设计使 SSR 对几何复杂度完全不敏感——1000 个三角形的场景与 1000 万个三角形的场景，SSR 的 GPU 开销完全相同，体现了后处理架构的核心优势。

**水面实时倒影**：虚幻引擎的水体插件（Water Plugin，UE 4.26 引入）默认在水面材质中启用 SSR，水面法线由两层流动 Normal Map 驱动，Hi-Z 步进可以正确捕获水面上方动态角色和植被的倒影。

> **例如**，在《最终幻想 XVI》（Square Enix，2023）的河流场景中，SSR 为水面提供了角色倒影，而平面反射贴图（Planar Reflection Capture）仅作为远景低频反射的补充，两者混合的总开销比纯光追方案低约 **60%**。

**正向渲染管线的适配**：正向渲染若要使用 SSR，需要额外渲染一个仅包含深度和法线的 Pre-Pass（Depth Pre-Pass + Normal Pre-Pass），成本比延迟渲染高约 **20%**（额外约 0.3ms，1080p，RX 6700 XT）。这也是移动端游戏较少采用 SSR 的原因之一——移动 GPU 的 TBDR 架构对额外 Pass 的带宽代价尤为敏感。

---

## 常见误区

**误区一：SSR 能反射屏幕外的物体**

SSR 只能反射出现在当前帧颜色缓冲中的内容。若一个高反射率金属球旁边有一个离屏光源，SSR 无法重建该光源的反射，只会在反射区域出现黑色或回退到 IBL，这是 SSR 的本质局限而非实现缺陷。实践中通常用环境反射捕获（Reflection Capture）或 IBL 覆盖离屏区域，与 SSR 按置信度混合。

**误区二：Hi-Z 层级越多越好**

Hi-Z 金字塔超过 $\lceil \log_2(\max(W, H)) \rceil$ 层后，额外层级对步进加速毫