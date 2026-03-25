---
id: "vfx-shader-erosion"
concept: "边缘侵蚀"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 边缘侵蚀

## 概述

边缘侵蚀（Alpha Erosion）是一种基于Alpha通道逐步腐蚀物体边缘像素的Shader技术，通过将噪声纹理的采样值与一个动态阈值进行比较，来决定每个像素是否保留、半透明还是完全透明，从而产生物体边缘向内"溶解消失"的视觉效果。与普通淡出（Alpha Fade）不同，边缘侵蚀产生的消失轨迹是不规则的、有机的，而非均匀的透明度递减。

该技术最早在2000年代中期的游戏特效开发中被广泛应用，尤其在《魔兽世界》等MMORPG的单位死亡动画中得到标志性使用——角色死亡时从脚底开始向上被"侵蚀"消失，而非直接倒地或淡出。核心数学基础是将噪声纹理的灰度值（0.0~1.0）减去一个随时间推进的侵蚀阈值 `threshold`，当差值低于0时该像素被丢弃（`clip`或`discard`）。

边缘侵蚀之所以在粒子系统和角色消散效果中不可替代，是因为它能在几乎零额外计算成本的条件下，利用一张静态噪声纹理驱动出视觉上极为丰富的有机边界感，这是线性Alpha过渡无法实现的。

## 核心原理

### 噪声纹理驱动的像素裁剪

边缘侵蚀的核心公式为：

```
float noiseValue = tex2D(_NoiseTex, uv).r;
float eroded = noiseValue - _Threshold;
clip(eroded);
```

其中 `_Threshold` 是一个从 `-1.0` 增大到 `1.0` 的动态值（或从 `0.0` 到 `1.0`，取决于噪声纹理的值域映射）。当 `_Threshold = 0` 时物体完整显示；当 `_Threshold = 1` 时物体完全消失。`clip()` 函数在参数为负数时直接丢弃当前像素，不进入后续光照计算，因此性能开销极低。

### 边缘发光与颜色渐变

仅仅做裁剪会产生硬边，真正的"溶解感"需要在侵蚀边界附近添加发光或颜色变化。实现方式是在 `clip` 之前计算一个额外的边缘宽度变量：

```
float edgeWidth = 0.05; // 边缘宽度，典型值0.02~0.1
float edgeFactor = saturate(eroded / edgeWidth);
float3 edgeColor = lerp(_BurnColor, _BaseColor, edgeFactor);
```

`_BurnColor` 通常设置为橙红色（如火焰灼烧效果 `(1.0, 0.3, 0.0)`）或蓝白色（魔法消散效果）。`edgeFactor` 在0到 `edgeWidth` 范围内从0变化到1，使得刚过裁剪线的像素呈现出灼烧颜色而非突然变为原始颜色，视觉上产生燃烧边缘的效果。

### 噪声纹理的选择与UV扭曲

噪声纹理的频率和类型直接决定侵蚀边缘的形状特征。使用低频Perlin噪声（典型分辨率256×256，频率1~2个周期）产生大块有机溶解；使用高频Worley噪声（细胞噪声）产生类似晶体碎裂的效果。为了避免侵蚀路径总是相同，常对噪声UV添加滚动偏移：

```
float2 noiseUV = uv + float2(_Time.y * 0.1, 0.0);
```

此处 `_Time.y` 是Unity内置的以秒为单位的运行时间，乘以0.1控制流动速度。噪声UV与模型UV分离，允许噪声纹理独立平铺（`_NoiseTex_ST` 的 `tiling` 设为2~4）而不影响漫反射纹理坐标。

## 实际应用

**角色死亡消散**：将 `_Threshold` 绑定到角色死亡动画的曲线上，配合Y轴方向的遮罩（通过顶点的WorldPos.y做额外偏移），实现从脚底向头顶逐步侵蚀的效果。侵蚀边缘使用橙色 `_BurnColor`，总体侵蚀时长设置为1.5~2.5秒符合玩家认知节奏。

**传送门进出效果**：物体进入传送门时，以传送门法线方向为基准，用dot乘积计算每个顶点与传送平面的距离，叠加进 `_Threshold` 偏移，使得靠近传送平面的部分最先被侵蚀，模拟穿越传送门"被吸入"的感觉。

**粒子消亡**：在粒子Shader中，将粒子的归一化生命周期（`TEXCOORD0.w` 存储的粒子年龄比 `age/lifetime`）直接映射为 `_Threshold`，每个粒子从诞生到消亡的侵蚀进度完全由自身生命周期驱动，无需CPU逐粒子传参。这是软粒子技术的自然升级——软粒子解决相交处的硬边，边缘侵蚀则解决粒子消亡时的硬边。

## 常见误区

**误区一：认为侵蚀方向由Shader自动确定**
边缘侵蚀本身不具备方向性，侵蚀总是沿噪声纹理的灰度分布展开，不会自动"从下向上"或"从中心向外"。要实现方向性侵蚀，必须显式地将方向信息编码进 `_Threshold` 的偏移量，例如 `float threshold = _Threshold - worldPos.y * _DirectionStrength`，方向效果是手动叠加的，而非边缘侵蚀技术本身的特性。

**误区二：clip()与Alpha混合可以混用实现半透明侵蚀**
`clip()` 使像素完全不透明或完全丢弃，无法产生半透明的羽化边缘。若需要边缘处的半透明过渡，必须将 `edgeFactor` 写入 `o.Alpha` 并开启Alpha Blend渲染队列（`Queue = Transparent`），同时移除 `clip()` 改用 `o.Alpha = saturate(eroded / edgeWidth)` 驱动透明度。两种方案各有取舍：`clip()` 版本可以写入深度缓冲，适合不透明队列；Alpha版本边缘更柔和但有排序问题。

**误区三：噪声纹理分辨率越高效果越好**
128×128的噪声纹理在大多数侵蚀场景中与512×512的效果几乎无差别，因为侵蚀本身是低频的形态变化。过高分辨率的噪声反而会使边缘过于琐碎，丧失有机感。实践中噪声纹理通常压缩为单通道（R8格式），256×256是性价比最优的常用规格。

## 知识关联

边缘侵蚀以软粒子技术为前置基础：软粒子通过采样深度缓冲解决粒子与场景几何体相交处的硬边问题，而边缘侵蚀进一步解决粒子或物体自身轮廓消亡时的视觉问题，两者共同构成粒子渲染的完整边缘处理方案。

学习边缘侵蚀后，遮罩技术（Mask）是自然的进阶方向：边缘侵蚀本质上是用噪声纹理灰度值做动态阈值遮罩，而遮罩技术将这一思路拓展为多通道、多层叠加的精确控制，允许美术用手绘遮罩图而非程序噪声来精确指定侵蚀区域的优先顺序，实现更具艺术可控性的溶解效果，例如让角色从伤口处向外扩散侵蚀，而非随机噪声分布。