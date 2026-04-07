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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 溶解效果

## 概述

溶解效果（Dissolve Effect）是一种通过噪声纹理（Noise Texture）驱动像素逐步消失的Shader技术，视觉上表现为物体表面像被火焰灼烧或粒子分解一样逐渐碎裂消失。其核心机制是：将噪声贴图的灰度值与一个可动态调节的阈值（Threshold）进行比较，当噪声值低于阈值时，该像素被丢弃（discard）或设置透明度为0，从而形成不规则的消融边界。

溶解效果最早在游戏行业广泛流行于2010年代，《暗黑破坏神3》（2012年）中怪物死亡时的碎裂消融动画是其经典应用之一。该技术之所以重要，在于它仅需一张灰度噪声贴图和一个float参数（0到1的Threshold值）即可实现极具冲击力的视觉叙事，几乎不增加额外的几何体或粒子系统开销。

在Unity的Shader实现中，溶解效果通常在片元着色器（Fragment Shader）阶段执行`clip()`或`discard`指令，这意味着它属于逐像素裁剪操作，而非顶点层面的变形。这一特性使它与顶点偏移类特效有本质区别。

## 核心原理

### 噪声纹理采样与阈值比较

实现溶解效果的最小Shader代码逻辑如下：

```hlsl
float noiseVal = tex2D(_NoiseTex, i.uv).r;
clip(noiseVal - _Threshold);
```

其中`_NoiseTex`是一张灰度噪声贴图，`noiseVal`取其红色通道（R通道）的值，范围为[0, 1]。`_Threshold`是外部传入的控制参数，当`noiseVal - _Threshold < 0`时，`clip()`函数会丢弃该像素。当`_Threshold`从0逐渐增大到1，被丢弃的像素区域从无到有覆盖整个网格，完成完整的消融过程。

噪声贴图的选择直接决定溶解图案的外观风格：Perlin Noise产生柔和的云雾状溶解，Voronoi Noise生成细胞裂纹状消融，Value Noise形成块状像素化分解。实际项目中最常用的是Perlin噪声，其连续性保证了溶解边界的自然感。

### 边缘发光效果

裸裶的溶解效果边界过于生硬，实际项目中几乎必然配合边缘发光（Edge Glow）使用。实现方式是在阈值附近定义一个宽度参数`_EdgeWidth`（典型值为0.05到0.1之间），对处于`[_Threshold, _Threshold + _EdgeWidth]`范围内的像素叠加一个高亮颜色（如橙色`float4(1, 0.4, 0, 1)`）：

```hlsl
float edge = step(_Threshold, noiseVal) * 
             step(noiseVal, _Threshold + _EdgeWidth);
finalColor += edge * _EdgeColor * _EdgeIntensity;
```

`_EdgeIntensity`通常设为2到5的HDR值，配合Bloom后处理才能呈现真实的灼烧发光感。没有Bloom的情况下，单独的高亮颜色视觉效果会大打折扣。

### Threshold动画驱动

在Unity中，`_Threshold`参数可以通过C#脚本的`Material.SetFloat("_Threshold", value)`动态设置，也可以直接在Shader中使用内置时间变量`_Time.y`驱动自动循环溶解。典型的死亡消融动画会在1.5到3秒内将Threshold从0线性插值到1，然后配合对象销毁逻辑`Destroy(gameObject, duration)`同步执行。

在Shader Graph中，此参数通过暴露为`Exposed Property`挂载到材质球，再由Animator或Timeline的Signal机制触发C#协程控制其动画曲线，可以实现非线性的"前慢后快"溶解节奏，强化死亡的戏剧感。

## 实际应用

**角色死亡消融**：RPG游戏中敌人死亡时，Threshold在2秒内从0变化到1，配合橙红色边缘光模拟灵魂散逸效果。消融完成后调用`renderer.enabled = false`而非立即销毁对象，避免帧率抖动。

**传送门入场/出场**：玩家走入传送门时，溶解方向不再是随机的，而是将噪声UV替换为基于世界空间Y轴的渐变贴图，使角色从脚底向头顶依次消失，强化"被传送走"的方向感。

**场景道具的交互反馈**：可拾取道具被玩家获取后执行0.5秒快速溶解，比直接消失更自然，比粒子特效的实现成本更低。这是溶解效果性价比最高的应用场景之一。

**地形遮挡透视**：将Threshold固定为较低值（如0.3），使地形Shader在玩家角色被建筑遮挡时呈现半透明溶解孔洞，比Alpha透明渲染在延迟渲染管线（Deferred Rendering）中的兼容性更好，因为`clip()`仍属于不透明渲染队列（Queue=2000）。

## 常见误区

**误区一：认为溶解效果需要开启Alpha Blend透明度**
很多初学者会将溶解Shader的渲染队列设置为`Transparent`并启用`Blend SrcAlpha OneMinusSrcAlpha`。这是错误的。溶解效果使用`clip()`做硬裁剪，像素非0即1，属于不透明渲染（Opaque），可以正确写入深度缓冲（Depth Buffer）。使用Alpha Blend反而会导致边缘半透明像素无法正确遮挡后方物体，且在延迟渲染管线中无法工作。

**误区二：边缘宽度用世界空间固定值而非噪声空间比例值**
`_EdgeWidth`是相对于噪声纹理灰度[0,1]的比例值，而不是像素宽度或世界单位宽度。如果误用后处理的像素宽度逻辑来控制边缘宽度，会导致物体大小不同时边缘粗细不一致。正确做法是边缘宽度始终在[0, 0.2]的噪声值域内调节，与物体的实际尺寸无关。

**误区三：溶解速度使用线性插值就足够**
将Threshold做线性动画（`Lerp(0, 1, t)`）会让溶解的感知速度在中间段（0.3到0.7）最快，而开头和结尾变化不明显。实际项目中推荐使用EaseInQuad（`t*t`）或EaseOutQuad（`1-(1-t)*(1-t)`）曲线，使消融在最后阶段加速，强化"灰飞烟灭"的爆发感。

## 知识关联

学习溶解效果需要先掌握**Shader特效概述**中的片元着色器执行流程，特别是`clip()`函数如何在光栅化阶段进行像素裁剪，以及纹理采样`tex2D()`的基本用法。不理解渲染队列（Render Queue）的设置逻辑，会在半透明场景中遇到Z-fighting和排序错误问题。

溶解效果学完后，自然衔接的下一个技术是**UV滚动**（UV Scrolling）。UV滚动同样以动态修改纹理坐标为核心，可以为溶解效果的噪声贴图叠加流动动画，制作岩浆流淌式消融或水面蒸发式消失等进阶变体——而这需要对UV坐标的变换逻辑有更深入的掌握。