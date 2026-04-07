---
id: "cg-lightmap-baking"
concept: "光照图烘焙"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 光照图烘焙

## 概述

光照图烘焙（Lightmap Baking）是一种将全局光照计算结果预先存储到纹理贴图中的离线渲染技术。与实时光照不同，烘焙过程在场景编辑阶段完成，将直接光、漫反射间接光（通常经过2至4次光线弹射）、环境光遮蔽等信息编码为RGB或HDR格式的二维纹理，运行时GPU只需采样贴图而无需重新计算光传输方程。这使得静态场景在极低的运行时开销下呈现高质量光照效果。

光照图烘焙技术的工程化普及始于1990年代末的游戏引擎实践。Quake（1996年）使用了简单的预计算亮度图，而Unreal Engine在1998年引入了完整的光照贴图管线，支持多光源叠加烘焙。现代引擎（Unity的Enlighten与Progressive Lightmapper、UE5的GPU Lightmass）已将烘焙精度提升至路径追踪级别，单张光照图分辨率可达4096×4096像素。核心学术依据来自渲染方程（Kajiya, 1986）以及后续的辐射度量学框架《Real-Time Rendering》（Akenine-Möller et al., 2018, CRC Press）。

光照图烘焙的核心价值在于一次计算、无限次采样的经济性。对于建筑可视化、关卡场景等以静态几何体为主的应用，烘焙方案能将光照渲染成本压缩至接近零帧时间，同时保留软阴影、色溢（Color Bleeding）等全局光照特有的视觉质量。

---

## 核心原理

### UV展开与光照图UV通道

每个参与烘焙的网格需要一套专用的光照图UV（通常称为UV2或Lightmap UV），其核心约束是**无重叠、无镜像、充分利用 $[0,1]^2$ 空间**。普通渲染UV允许镜像和平铺以节省纹素，但光照图UV中每个表面在贴图空间必须唯一映射，否则镜像的两侧会共享同一光照信息，导致阴影方向错误或重影。

展开质量的关键指标是**纹素密度均匀性**：1平方米地面和1平方厘米螺栓若分配相同纹素密度会造成严重浪费。自动展开工具（如开源的 xAtlas 库，2018年由 Jonathan Young 发布）通过最小化角度失真和拉伸失真来切割UV孤岛（Island），相邻孤岛之间必须保留至少2像素的填充边距（Padding/Gutter），防止双线性插值采样时跨孤岛漏色，产生光照图接缝。

UV填充率（Packing Efficiency）直接影响光照图分辨率需求：对于复杂建筑模型，人工展开的填充率可达 70%～85%，而自动展开通常仅有 50%～65%。低填充率意味着在相同分辨率下每纹素覆盖更大的世界空间面积，导致光照细节模糊。例如，在一张 1024×1024 的光照图中，若填充率为 50%，则有效纹素仅相当于 724×724 分辨率下的覆盖密度。

### 烘焙参数配置

烘焙器的核心参数分为采样参数与传输参数两类。**样本数（Samples Per Texel）**决定每个光照图纹素投射多少条光线来估算辐照度。Unity Progressive Lightmapper 中默认值为 512，高质量建筑可视化场景建议设置为 2048 以上，将蒙特卡洛噪声降至可接受水平。噪声标准差与样本数的关系为：

$$\sigma_{\text{noise}} \propto \frac{1}{\sqrt{N}}$$

即样本数从 512 提升至 2048（翻4倍），噪声标准差降低为原来的 $\frac{1}{2}$，烘焙时间也相应增加约4倍，需在质量与时间之间权衡。

**间接反弹次数（Indirect Bounces）**控制漫反射光子弹射深度。1次弹射即可捕获主要的色溢效果，3次弹射后能量衰减通常已低于 1%。假设场景平均漫反射率为 $\rho = 0.5$，第 $n$ 次弹射剩余能量比例为 $\rho^n = 0.5^n$；当 $n=3$ 时仅剩 12.5%，$n=4$ 时仅剩 6.25%，继续增加弹射次数收益微乎其微，但计算开销线性增长。

**光照图密度（Texels Per Unit/Meter）**是场景级参数，Unity 中默认值 40 texels/unit（1 unit = 1 米），大面积地板可降至 10～20 texels/unit，门框、踢脚线等细节模型可提升至 80～100 texels/unit。**环境光遮蔽最大距离（AO Max Distance）**通常设置为场景最大尺度的 1%～5%，例如一个 50 米长的室内场景中，AO 射线长度建议设为 0.5～2.5 米。

### 编码格式与压缩方案

光照图存储格式的选择直接影响画面质量与内存占用。常见方案对比如下：

- **RGBM 编码**：将 HDR 辐照度值压缩进标准 RGBA8 纹理，R/G/B 通道存储颜色，M（Alpha）通道存储缩放因子，最大表示亮度约为 6～8 倍标准白（依乘数而定）。解码公式为 $L = \text{RGB} \times M \times k$，其中 $k$ 通常取 6.0。该方案内存开销为 4 字节/纹素，兼容性好。
- **BC6H 压缩**（DirectX 11+）：专为 HDR 数据设计的块压缩格式，以 16 字节编码 4×4 纹素块，即每纹素仅 1 字节，相比 RGBA16F 节省 75% 内存，且硬件解压无额外 GPU 开销。移动平台可使用 ASTC HDR（6×6 block）作为替代。
- **球谐系数（Spherical Harmonics, SH）**：对于动态物体的环境光探针，通常存储 3 阶 SH 系数（9 个系数 × 3 通道 = 27 个浮点数），可表示低频漫反射光照，但无法捕获硬阴影细节。

---

## 关键公式与算法

光照图烘焙本质上是对渲染方程的数值积分。对于光照图中位置 $\mathbf{p}$、法线 $\mathbf{n}$ 的纹素，其存储的辐照度 $E(\mathbf{p}, \mathbf{n})$ 定义为：

$$E(\mathbf{p}, \mathbf{n}) = \int_{\Omega} L_i(\mathbf{p}, \boldsymbol{\omega}) \, (\boldsymbol{\omega} \cdot \mathbf{n}) \, d\boldsymbol{\omega}$$

其中 $\Omega$ 为以 $\mathbf{n}$ 为轴的半球，$L_i$ 为来自方向 $\boldsymbol{\omega}$ 的入射辐亮度，$(\boldsymbol{\omega} \cdot \mathbf{n})$ 为余弦加权项（Lambert 余弦定律）。蒙特卡洛估算以 $N$ 条随机光线近似积分：

$$\hat{E} = \frac{2\pi}{N} \sum_{i=1}^{N} L_i(\mathbf{p}, \boldsymbol{\omega}_i) \, (\boldsymbol{\omega}_i \cdot \mathbf{n})$$

其中 $2\pi$ 为均匀半球采样的概率密度 $p(\boldsymbol{\omega}) = \frac{1}{2\pi}$ 的倒数。

以下是 Unity Progressive Lightmapper 的典型烘焙脚本配置（Editor 脚本）：

```csharp
using UnityEditor;
using UnityEngine;

public class LightmapBakeSettings
{
    [MenuItem("Tools/Configure and Bake Lightmap")]
    static void BakeWithCustomSettings()
    {
        // 设置光照图密度：40 texels/unit（默认），细节场景可调至 80
        LightmapEditorSettings.bakeResolution = 40f;

        // 每纹素样本数：2048 用于高质量最终烘焙
        LightmapEditorSettings.directSampleCount = 32;
        LightmapEditorSettings.indirectSampleCount = 2048;

        // 间接反弹次数：2 次弹射覆盖 >93.75% 的漫反射能量（ρ=0.5）
        LightmapEditorSettings.bounces = 2;

        // 光照图最大分辨率：2048×2048
        LightmapEditorSettings.maxAtlasSize = 2048;

        // 孤岛间填充边距：2 像素，防止插值漏色
        LightmapEditorSettings.padding = 2;

        // 启用环境光遮蔽，最大距离 1 米
        LightmapEditorSettings.enableAmbientOcclusion = true;
        LightmapEditorSettings.aoMaxDistance = 1.0f;

        // 开始异步烘焙
        Lightmapping.BakeAsync();
        Debug.Log("Lightmap baking started with high-quality settings.");
    }
}
```

---

## 实际应用

### 建筑可视化与关卡场景

建筑可视化是光照图烘焙最主流的应用场景。例如，在一个面积约 200 平方米的室内场景中，典型配置为：光照图分辨率 80 texels/unit，样本数 4096，2 次间接反弹，最终生成 4 张 2048×2048 的 BC6H 压缩光照图，总内存占用约 16 MB（每张 4 MB），运行时帧率可维持在 120 fps 以上（在 NVIDIA GTX 1060 级别 GPU 上），而等效的实时路径追踪方案在同等硬件上仅能实现约 10 fps。

### 移动端优化策略

移动端 GPU 显存带宽受限，光照图压缩尤为关键。iOS 平台建议使用 ASTC 4×4（8 bpp）格式，Android 平台优先使用 ETC2（但 ETC2 不支持 HDR，需将光照图预先转为 LDR + RGBM 编码再压缩）。对于分辨率为 1920×1080 的移动端游戏，单张光照图建议不超过 1024×1024，全场景光照图集合总内存控制在 32 MB 以内，以避免在 2 GB RAM 设备上触发系统内存警告。

### 动静混合场景

纯静态光照图无法处理动态角色和可移动道具。常见方案是将静态环境烘焙光照图与动态物体的**光照探针（Light Probe）**结合：Unity 的 Light Probe Group 在场景空间中放置离散探针点，每个探针存储 3 阶球谐系数（L2 SH，27 个浮点数 × 4 字节 = 108 字节/探针），动态物体通过四面体插值获取近似的环境光照，与光照图保持视觉一致性。

---

## 常见误区

### 误区一：光照图UV与渲染UV混用

许多初学者直接使用模型的 UV0 通道烘焙光照图。若 UV0 存在平铺（Tiling，如地砖纹理的 UV 重复 10×10 次），则同一张光照图纹素将被所有砖块共享，导致烘焙器无法区分每块砖的独立光照，最终所有砖块呈现完全相同的阴影。正确做法是在 DCC 工具（Blender、Maya）或引擎内自动生成 UV1/UV2 专用光照图通道，保证 $[0,1]^2$ 内无重叠。

### 误区二：孤岛间距不足导致漏光

当孤岛 Padding 设置为 0 或 1 像素时，在生成 Mipmap 后（Mip Level 1 将像素合并为 2×2 块），相邻孤岛的边缘像素会被混合，产生穿透式漏光（Light Bleeding）。具体表现为墙角处出现亮线或暗角错误。解决方案是将 Padding 设置为 2～4 像素，并在烘焙完成后对孤岛边缘执行**边缘填充（Dilation/Edge Padding）**，将孤岛颜色向外扩展填充空白区域，使插值采样落在有效颜色范围内。

### 误区三：