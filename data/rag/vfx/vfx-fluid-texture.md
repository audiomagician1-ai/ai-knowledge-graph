---
id: "vfx-fluid-texture"
concept: "流体纹理"
domain: "vfx"
subdomain: "fluid-sim"
subdomain_name: "流体模拟"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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


# 流体纹理

## 概述

流体纹理是指利用预计算或实时生成的纹理贴图来模拟流体视觉表现的技术集合，核心手段包括 Flowmap（流向图）、法线扰动贴图（Normal Distortion Map）以及速度场纹理等。与全物理流体模拟不同，流体纹理依赖 GPU 的采样与混合能力，将流体运动的视觉信息"烘焙"进贴图通道，从而以极低的运行时开销还原河流、熔岩、雨水等流体效果。

Flowmap 技术由 Valve 公司的 Alex Vlachos 于 2010 年在 GDC 演讲《Water Flow in Portal 2》中系统化公开，该技术将二维流向信息编码进 RG 两个颜色通道（R 通道对应 X 轴流速，G 通道对应 Y 轴流速），使普通美术人员也能通过绘制 Flowmap 精确控制纹理流动的走向与速度，从此成为游戏行业水面与熔岩渲染的标准方案之一。

流体纹理的价值在于它将"流体运动"与"渲染消耗"解耦。以 Portal 2 的水面为例，整张 Flowmap 仅需一次 Draw Call 内完成采样与计算，帧率影响不到传统粒子流体方案的 5%，同时视觉品质完全满足 1080p 实时渲染的需求。

---

## 核心原理

### Flowmap 的双时间相位混合

Flowmap 最关键的算法问题是纹理坐标随时间线性偏移会导致纹理"拉伸撕裂"。解决方案是使用**双相位周期混合（Dual-Phase Cyclic Blending）**：

```
offset_A = flowUV * (time mod 1.0)
offset_B = flowUV * ((time + 0.5) mod 1.0)
blend = abs((time mod 1.0) * 2.0 - 1.0)
result = lerp(tex(UV + offset_A), tex(UV + offset_B), blend)
```

其中 `flowUV` 是从 Flowmap 解码出的流向向量（原始值需从 [0,1] 重映射到 [-1,1]），`time` 为全局时间参数。两个相位的纹理采样结果每 0.5 个周期交替淡入淡出，使循环边界处的接缝在视觉上不可见。相位混合权重 `blend` 呈锯齿波形状，是消除撕裂的核心机制。

### 法线扰动与水面折射

法线扰动使用两张以不同速度、不同方向滚动的法线贴图叠加，模拟水面波纹的随机感。标准公式为：

```
N_final = normalize(N1(UV + dir1 * t * speed1) + N2(UV + dir2 * t * speed2))
```

典型参数设置中，`speed1` 和 `speed2` 之比约为 1.0 : 0.73（使用无理数比例防止规律性重复），两张贴图的 UV 缩放比例通常设为 1.0 : 2.3。最终叠加法线用于偏移折射采样坐标，偏移量乘以水深遮罩可以产生浅水区扰动弱、深水区扰动强的物理合理效果。

### 流速与泡沫遮罩的生成

Flowmap 的 B 通道（或独立的速度强度图）可以存储流速标量。流速越高的区域，泡沫/白浪产生的概率越大。泡沫遮罩通常通过以下逻辑计算：

```
foam_mask = step(1.0 - flowSpeed, noise(UV * 8.0 + time * 0.3))
```

`noise` 使用 Worley 噪声（细胞噪声）时，泡沫形状呈现聚集状气泡感；使用 Perlin 噪声时则表现为连续绒状白浪。《荒野大镖客：救赎2》的河流系统正是将这两种噪声按深度权重混合，分别用于浅滩泡沫和急流白浪。

---

## 实际应用

**河流与溪流**：在 Unity 的 Shader Graph 或 Unreal 的 Material Editor 中，将美术绘制的 Flowmap 导入后，配合双相位混合节点即可实现完整河流效果。美术师用 Houdini 的 Labs Flow Map 工具或 Flowmap Painter（免费工具）绘制 Flowmap，导出精度通常选用 16-bit PNG 以保留流向的平滑渐变。

**熔岩与魔法地面**：熔岩 Flowmap 的流速参数远低于水（约为水面速度的 0.05~0.1 倍），同时在高流速区域叠加自发光遮罩，产生熔岩被撕开时内部更亮的视觉效果。《暗黑破坏神 4》的地狱熔岩地面大量使用了此类方案。

**雨水湿润表面**：雨水打湿地面时，法线扰动贴图以向心圆形方向（通过 Flowmap 编码）向外扩散涟漪。每个水滴落点的涟漪使用 Sprite Sheet 动画纹理（通常为 4×4 = 16 帧）在 UV 坐标内播放，与法线扰动组合后无需任何粒子系统。

---

## 常见误区

**误区一：Flowmap 的 RG 通道可以直接使用而无需重映射**
Flowmap 纹理存储时 RGB 值范围是 [0, 1]，中性值（无流动）编码为 (0.5, 0.5)。若跳过重映射步骤 `flow = tex.rg * 2.0 - 1.0`，所有流向向量的分量都是正值，纹理会朝右上方单向漂移，无法表现向左或向下的流动。这是初学者最常见的实现错误。

**误区二：两张法线贴图叠加时应直接相加后归一化**
直接对法线向量进行线性相加后归一化（Linear Blending）会导致两张法线垂直方向的 Z 分量被过度压缩，在掠射角下出现明显的光照变暗。正确方式是使用 **Whiteout 混合法**：`N = normalize(N1.xy + N2.xy, N1.z * N2.z)`，该方法能更好地保留两层法线各自的 Z 分量贡献，是 UE5 材质文档推荐的标准做法。

**误区三：Flowmap 分辨率越高越好**
Flowmap 编码的是平滑的流向场，高频细节需要由基础法线贴图提供，而非 Flowmap 本身。512×512 的 Flowmap 通常足以覆盖一条数十米长的河流，过高分辨率仅浪费显存而无视觉收益。River Flowmap 的最大建议分辨率约为每 10 米地面对应 256 像素。

---

## 知识关联

流体纹理的前置概念是**实时流体策略**，后者确定了项目在粒子、网格模拟与纹理方案之间的选择依据；流体纹理是纯 GPU 纹理侧的实现路径，完全不依赖 CPU 端的流体求解器。

掌握流体纹理后，下一步学习**流体交互**时会直接用到 Flowmap 的写入机制：玩家或物体扰动水面时，需要动态修改 RenderTexture 中的 Flowmap 数据（即通过 GPU 的 Render To Texture 在运行时重绘 RG 通道），使水面流向响应实时碰撞，这是将静态 Flowmap 扩展为动态交互系统的关键桥梁。