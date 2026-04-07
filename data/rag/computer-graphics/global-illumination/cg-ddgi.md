---
id: "cg-ddgi"
concept: "DDGI"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 4
is_milestone: false
tags: ["前沿"]

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


# DDGI（动态漫反射全局光照）

## 概述

DDGI（Dynamic Diffuse Global Illumination）是由 NVIDIA 研究院在 2019 年发表的论文《Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields》中提出的实时全局光照技术。其核心创新在于将场景空间划分为三维网格，在每个网格点上放置辐照度探针（Irradiance Probe），并以每帧持续追踪少量光线的方式动态更新这些探针，从而实现可随光源、几何体、材质变化而实时响应的漫反射间接光照。

DDGI 解决了预烘焙光照贴图无法应对动态场景的根本缺陷。传统 Light Map 需要离线计算数小时，且几何体或光源一旦移动就会产生错误的阴影漏光。DDGI 每帧对每个探针仅发射 **64～512 条**随机方向的光线（论文原型使用 128 条/探针/帧），通过时间累积平滑后达到与离线方案接近的视觉效果，在 RTX 显卡上可维持实时帧率。

DDGI 之所以重要，在于它为 UE5 的 Lumen 和多款 AAA 游戏的动态 GI 奠定了工程原型。理解 DDGI 的探针更新机制，是掌握现代实时全局光照管线的必经之路。

---

## 核心原理

### 探针网格布局与辐照度存储格式

DDGI 在世界空间中均匀排布三维探针网格，相邻探针间距通常为 **1～3 米**（可按场景尺度调整）。每个探针存储两张小尺寸纹理：

- **辐照度图（Irradiance Map）**：分辨率 **6×6**（加 1 像素边框 = 8×8），采用 Oct-encoding（八面体展开投影）将球面辐照度压缩到正方形 UV 空间，存储格式为 RGB16F。
- **可见度图（Visibility/Depth Map）**：分辨率 **14×14**（加边框 = 16×16），每个像素存储沿该方向追踪光线命中的平均距离及距离平方（用于 Chebyshev 不等式遮挡测试），格式为 RG16F。

所有探针的纹理被打包进同一张 **Probe Atlas** 大纹理，GPU 批量读取无需切换绑定。

### 每帧光线追踪与探针更新流程

DDGI 的更新分为以下几个 GPU Pass：

1. **光线生成 Pass**：对每个探针生成 N 条（默认 128）随机方向光线，方向使用**球面 Fibonacci 点集**加帧间旋转偏移（Spherical Fibonacci Sampling with per-frame rotation），保证时域分布均匀。
2. **光线追踪 Pass**：使用 DXR/VK_KHR_ray_tracing 追踪每条光线的最近命中点，在命中表面采样直接光与前一帧的探针辐照度（递归一次间接弹射）。
3. **探针混合 Pass（Probe Blending）**：将新的光线结果与历史辐照度做**指数移动平均（EMA）**：

$$I_{new} = \alpha \cdot I_{ray} + (1 - \alpha) \cdot I_{old}$$

其中 $\alpha$ 为混合率，论文推荐值为 **0.03**（对应约 33 帧的时间常数）。辐照度在混合前先做 **Gamma 5.0** 非线性变换（存储时压缩、读取时展开），以增强明暗对比、减少漏光。
4. **边框更新 Pass**：更新 Atlas 中每块探针纹理的 1 像素边框，保证 Oct-encoding 的边界采样连续，避免接缝伪影。

### 着色阶段的探针插值

在 GBuffer 着色时，像素对周围 **8 个最近探针**（形成三线性插值立方体）进行加权采样。权重由三部分乘积决定：

1. **三线性权重**：探针在立方体内的位置权重。
2. **Visibility 权重**：利用可见度图中存储的均值距离和均值距离平方，套用 **Chebyshev 不等式**估算探针对当前像素的遮挡概率，被墙体遮挡的探针权重趋向 0，从根本上抑制漏光。
3. **背面权重**：若探针位于着色点几何法线的背面，权重乘以接近 0 的小值，防止采样到从背面透射过来的错误能量。

最终加权平均后乘以表面反照率（Albedo），得到漫反射间接光照贡献。

---

## 实际应用

**《赛博朋克 2077》的动态 GI**：CD Projekt RED 在 Ray Tracing Overdrive 模式中采用了类 DDGI 方案，探针网格覆盖整个开放城市区块，夜晚霓虹灯颜色变化时，数秒内探针即可收敛到新的辐照度状态，彩色间接光溢出效果完全动态响应。

**UE5 Lumen 的软件回退路径**：Lumen 在不支持硬件光追的平台上，使用 Screen-Space Radiance Cache 与 DDGI 类似的探针混合机制，每帧少量更新探针并时间积累，维持低延迟的 GI 响应。

**室内建筑可视化**：在房间尺度（10m×10m×3m）的场景中，以 1m 间距布置探针后，开关灯光的辐照度变化在约 **30～50 帧**内完成收敛（取决于 α 值），满足交互式预览需求。

---

## 常见误区

**误区一：探针数量越多越好**
DDGI 的探针总数直接乘以每探针光线数，决定总光线追踪开销。128 条/探针 × 10,000 个探针 = 128 万条/帧，已接近中端 RTX 显卡实时极限。实际工程中需要根据场景尺度和帧预算手动裁剪探针区域，在玩家不可见或几何变化稀少的区域降低密度，而非无限堆叠。

**误区二：EMA 混合率 α 越大收敛越快因此越好**
α 增大虽然使探针在光照变化后更快收敛，但会减弱时间平滑效果，导致每帧 128 条低采样光线产生的噪声直接出现在画面中，闪烁明显。**α = 0.03** 是论文经过主观质量评估后的平衡值；若需更快响应，应配合增加每帧光线数而非单纯提高 α。

**误区三：DDGI 可以独立提供镜面反射 GI**
DDGI 仅输出低频漫反射辐照度（存储在 6×6 极低分辨率的 Oct-map 中），无法捕捉高频镜面反射。场景中的光泽/镜面间接光照必须由独立的 SSR（屏幕空间反射）或 RTXGI 镜面分量负责，两者结合才构成完整的间接光照解决方案。

---

## 知识关联

**前置概念——光探针**：DDGI 的辐照度探针直接继承了传统 Light Probe 的球谐函数（SH）思想，但以 Oct-encoded 纹理替代 L2 球谐（9个系数），获得更高的低频精度同时支持 GPU 快速更新；理解静态光探针的烘焙流程有助于对比 DDGI 动态更新机制带来的改变。

**并列技术——RTXGI SDK**：NVIDIA 将 DDGI 工业化为 RTXGI（RTX Global Illumination）SDK，在 DDGI 基础上增加了探针重定位（Probe Relocation，探针自动移离几何体内部）和探针分类（Probe Classification，对遮挡或空旷区域停用光线追踪），是 DDGI 论文算法的直接工程实现参考。

**扩展方向——Radiance Caching**：DDGI 每帧的递归单次弹射限制了多次间接弹射的精度。更进一步的 World-Space Radiance Cache 技术允许多次弹射的能量逐帧积累，ReSTIR GI 等算法则在此基础上引入重要性重采样，进一步提升每条光线的信息利用率。