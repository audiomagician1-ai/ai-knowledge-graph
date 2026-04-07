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



# 边缘侵蚀

## 概述

边缘侵蚀（Alpha Erosion）是一种基于噪声纹理驱动Alpha通道逐步消减的Shader特效技术，其核心思想是将物体的可见边界通过一个动态阈值与噪声贴图的对比运算来实现"从外向内溶解"的视觉效果。这种技术最早广泛出现在2000年代初的实时游戏引擎中，用于替代简单的淡入淡出（Fade）过渡，因为它能产生更具质感的有机消失感，而非单调的透明度线性变化。

该技术的历史可以追溯到离线渲染领域的"溶解效果"实验，但真正进入实时图形管线是在Unity 4.x与Unreal Engine 3时代，随着可编程Shader的普及而成熟。边缘侵蚀能够模拟燃烧边缘发光、冰雪融化、怪物尸体腐蚀消失等场景，因此在游戏特效、影视实时预览以及UI动效领域都有广泛的落地价值。

## 核心原理

### Alpha阈值比较运算

边缘侵蚀的数学基础是一次简单的比较运算。设噪声纹理在某像素点采样所得灰度值为 `N`（范围 [0,1]），程序传入的侵蚀进度参数为 `T`（同样 [0,1]），则该像素的最终Alpha值由以下规则决定：

```
Alpha = step(N, T)
```

即：当 `N < T` 时像素被完全丢弃（Alpha=0），当 `N >= T` 时像素保留（Alpha=1）。通过在运行时将 `T` 从 0 线性增大到 1，物体的可见区域就会随着噪声纹理的灰度分布从随机散点逐渐演变为完全消失。这里 `step` 函数产生的是硬边缘；若希望获得柔和过渡，则改用：

```
Alpha = smoothstep(T, T + EdgeWidth, N)
```

其中 `EdgeWidth`（典型值约 0.02~0.1）控制溶解边缘的模糊宽度。

### 侵蚀边缘发光效果

仅使用Alpha比较只能实现基础溶解，真正吸引人的是边缘处叠加的发光或燃烧颜色。实现方式是在Alpha过渡带内额外输出一个高饱和度颜色：

```
float edgeMask = saturate((N - T) / EdgeWidth);
float3 edgeColor = lerp(BurnColorHot, BurnColorCool, edgeMask);
finalColor = lerp(edgeColor, baseColor, edgeMask);
```

`BurnColorHot` 通常设置为接近白色或亮橙色（如 RGB(1.0, 0.6, 0.1)），`BurnColorCool` 设置为深红或焦黑，这样在边缘1~2个像素范围内可以看到从亮到暗的热度渐变，模拟燃烧灼烧质感。

### 噪声纹理的选择对侵蚀形状的影响

侵蚀效果的"形状感"完全由噪声纹理决定：

- **Perlin噪声**：产生大块有机流动感，适合烟雾、云层消散。
- **Worley噪声（细胞噪声）**：产生蜂窝状碎裂感，适合石头崩裂、皮肤腐蚀。
- **白噪声（随机像素）**：产生颗粒状像素溶解，常用于数字化消失的科技感特效。

噪声贴图的分辨率通常选用 256×256 或 512×512 的单通道（R8）纹理，以节省显存带宽。UV平铺系数一般设置为 1~4 倍，过高平铺会导致侵蚀图案重复感明显。

## 实际应用

**角色死亡消失特效**：在角色死亡时，将侵蚀参数 `T` 绑定到一条0到1的动画曲线（时长约1.2秒），配合边缘橙色发光，可以实现从脚底向上燃烧消失的效果，无需任何骨骼动画配合。

**技能施放UI提示**：在HUD的技能冷却图标上应用边缘侵蚀，可以用Worley噪声实现"能量碎片化充能"的视觉反馈，相比传统扇形遮罩冷却更具特效感。

**传送门边缘过渡**：在传送门周围的扭曲区域叠加一层侵蚀Shader，令边界呈现出不规则的有机形态，而非硬直圆形。侵蚀参数由到传送门中心的距离驱动，实现从中心到外缘的扩散溶解感。

**Unity ShaderGraph实现**：在Unity ShaderGraph中，典型的实现路径是：`Sample Texture 2D（噪声）→ Subtract（减去T参数）→ Step 节点→ Alpha输出`，整个节点图不超过8个节点即可完成基础版本。

## 常见误区

**误区一：将侵蚀参数直接映射到Alpha不加噪声采样**
初学者有时直接将一个从0到1的数值赋值给材质的整体透明度，认为这就是"侵蚀"。这实际上是普通淡入淡出，不涉及噪声纹理的逐像素比较，无法产生边缘不规则的溶解形态，两者在Shader实现层面有本质区别。

**误区二：EdgeWidth设置过大导致效果失真**
`EdgeWidth` 过大（如超过 0.3）会使边缘发光带宽度几乎占满整个物体，在侵蚀中段出现大面积颜色偏移，物体外观严重失真。正确做法是将 `EdgeWidth` 控制在 0.02~0.15 范围内，并根据噪声纹理的对比度动态调整。

**误区三：Alpha Erosion与软粒子（Soft Particles）混淆使用**
软粒子通过深度差值修正粒子与几何体交接处的硬边，处理的是粒子系统的相交穿插问题；而边缘侵蚀处理的是单个网格或Sprite自身的溶解消失问题，两者所修改的Alpha来源完全不同——软粒子修改的是基于深度的整体透明度，边缘侵蚀修改的是基于纹理坐标的逐像素Alpha。

## 知识关联

边缘侵蚀建立在对软粒子中Alpha通道运算的理解之上：学完软粒子后，你已了解Alpha值可以由程序运行时动态写入，而边缘侵蚀将这一思路从"深度差值"扩展到"噪声纹理阈值比较"，是Alpha操控能力的直接延伸。

在掌握边缘侵蚀后，下一步学习的遮罩技术（Mask）本质上是将侵蚀的"单纹理比较"升级为"多通道精确控制"——遮罩技术允许不同区域以不同速率或形状独立侵蚀，相当于为每个区域分配一个独立的 `T` 参数。边缘侵蚀的 `EdgeWidth` 与 `edgeMask` 变量的运算逻辑，在遮罩技术的软边遮罩（Soft Mask）中会直接复用。