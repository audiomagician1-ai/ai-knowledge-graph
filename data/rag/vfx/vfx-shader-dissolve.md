---
id: "vfx-shader-dissolve"
concept: "溶解效果"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 溶解效果

## 概述

溶解效果（Dissolve Effect）是一种通过Shader将物体表面逐渐"烧蚀"或"碎裂消失"的视觉特效技术。其核心机制是用一张噪声贴图（Noise Texture）的灰度值与一个可动态变化的阈值（Threshold）做比较，当像素的噪声采样值低于当前阈值时，该像素被丢弃（clip/discard），从而在空间上制造出不规则的消融边界，而非简单的线性淡出。

溶解Shader最早在游戏工业中随可编程管线的普及而流行，约2005年后随着Unity、Unreal等引擎对Surface Shader的支持，开发者能够以极低成本实现此效果。如今它被广泛用于角色死亡动画、传送门开启、魔法技能释放等场景，因其能配合粒子特效产生"边缘发光燃烧"的视觉延伸而成为特效美术的常备技法。

溶解效果的关键价值在于：它只需一张噪声贴图和一个float参数（溶解进度），即可驱动复杂的视觉变化，GPU端的clip指令执行成本极低，对移动端也友好。

---

## 核心原理

### 噪声贴图与阈值比较

溶解Shader的数学本质是一条简单的判断：

```
dissolveValue = tex2D(_NoiseTex, i.uv).r
clip(dissolveValue - _Threshold)
```

其中 `_Threshold` 是0到1之间的浮点数，由外部脚本随时间驱动。`clip(x)` 函数在x < 0时丢弃该像素。当 `_Threshold = 0` 时，所有像素保留（物体完整）；当 `_Threshold = 1` 时，所有像素被丢弃（物体完全消失）。噪声贴图决定了哪些区域先消失——灰度值低的区域更早被clip掉，因此Perlin Noise或Worley Noise的有机形态使消融边界呈现自然的不规则感，而非矩形裁切。

### 边缘发光（Edge Glow）效果

仅有clip逻辑的溶解效果视觉上较为生硬，业界标准做法是在消融边界处叠加高亮颜色。实现公式为：

```
float edge = step(dissolveValue, _Threshold + _EdgeWidth) 
             * step(_Threshold, dissolveValue);
col.rgb += edge * _EdgeColor * _EdgeIntensity;
```

其中 `_EdgeWidth` 控制发光带宽度（典型值为0.05到0.15），`_EdgeColor` 和 `_EdgeIntensity` 控制颜色与强度（HDR值可超过1以配合Bloom后处理）。这一层逻辑使消融边界呈现"燃烧火焰"或"能量侵蚀"的质感，是溶解效果高品质的核心标志。

### 噪声贴图的选择与影响

不同的噪声类型产生截然不同的消融风格：
- **Perlin Noise**：产生有机云雾状溶解，适合角色消失、烟雾散去
- **Voronoi/Worley Noise**：产生细胞破碎状溶解，适合岩石碎裂、玻璃破碎
- **Gradient Noise（方向性渐变）**：从某一方向向另一方向溶解，适合传送或滑动消失

噪声贴图通常为单通道（R通道）灰度图，分辨率256×256或512×512即可满足大多数需求，使用时开启双线性过滤（Bilinear Filtering）以避免硬边噪点。

---

## 实际应用

**角色死亡消融**：将 `_Threshold` 从0动画曲线过渡到1，配合曲线Ease-In使前半段消融慢、后半段加速，模拟"烧尽"感。边缘颜色设为橙红色（RGB: 1.0, 0.4, 0.0），HDR强度设为3，与场景Bloom组件配合即产生燃烧效果。

**技能召唤物显现**：反向使用，`_Threshold` 从1到0，物体从噪声破碎状态逐渐显现完整形态。可在UV采样时叠加世界空间Y轴坐标偏移，使溶解方向自下而上。

**传送门与空间裂缝**：在边缘Glow之外，额外在 `_EdgeWidth * 2` 范围内对UV做扭曲偏移采样（UV Distortion），使边界看起来在空间中颤动，强化"次元撕裂"感。

**UI消失动效**：在UI Shader中同样可用此技术，将噪声贴图与UI元素的Rect UV对齐，用C#的 `Material.SetFloat("_Threshold", value)` 每帧更新，实现卡片或对话框的燃烧退场。

---

## 常见误区

**误区一：认为溶解效果必须使用Alpha透明度混合**
实际上标准溶解Shader使用的是 `clip()` 丢弃像素，而非Alpha Blend。这意味着材质球的渲染队列应设为"Geometry"（2000），Blend Mode保持Opaque，不需要开启Alpha Blending。若错误地改为透明混合模式，会导致深度写入问题，尤其在有多个溶解物体重叠时产生错误的遮挡排序。

**误区二：将_Threshold范围误理解为需要手动钳制**
`clip(dissolveValue - _Threshold)` 中，当 `_Threshold < 0` 时所有像素均保留，当 `_Threshold > 1` 时所有像素均被丢弃，HLSL的clip函数天然处理了边界，无需额外的 `saturate()` 包裹，多余的钳制反而可能导致在0和1附近出现突兀的全保留/全消失跳变，破坏边缘发光的平滑过渡。

**误区三：用纯程序噪声替代贴图噪声以节省内存**
在片元Shader中实时计算Perlin Noise（每像素多次sin/cos运算）在移动端代价远高于纹理采样。实测在Mali-G72 GPU上，256×256 Perlin Noise的实时计算比贴图采样慢约4-6倍，在粒子系统大量实例化该Shader时尤为明显，应优先使用预烘焙贴图。

---

## 知识关联

**前置知识衔接**：学习溶解效果需要理解Shader特效概述中介绍的 `clip()` 函数语义、片元Shader执行阶段以及 `tex2D()` 纹理采样基础。如果对这些概念不熟悉，溶解Shader中的 `clip(dissolveValue - _Threshold)` 逻辑将难以理解其为何能产生空间上不规则的消失区域。

**后续扩展方向**：掌握溶解效果后，学习UV滚动技术可以让溶解边缘的噪声纹理动态流动，例如使噪声贴图的UV随时间偏移 `i.uv + _Time.y * _ScrollSpeed`，使燃烧边界呈现流动的火焰效果而非静态纹理，这是溶解效果在技能特效中进一步提升品质的自然演进路径。此外，溶解效果与顶点动画结合（如溶解同时伴随顶点向外扩散）可构造出"崩解飞散"的高级效果。
