---
id: "vfx-vfxgraph-shader-graph"
concept: "Shader Graph集成"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Shader Graph集成

## 概述

Shader Graph集成是指在Unity VFX Graph中，将粒子的视觉渲染交由Shader Graph自定义着色器来控制的工作流程。通过这一机制，VFX Graph负责粒子的物理行为、生命周期和空间变换，而Shader Graph则接管每个粒子表面的像素级着色逻辑，两者通过Output节点上的"Shader Graph"资产槽位进行绑定，形成完整的渲染管线。

这一集成功能在Unity 2019.3版本中正式进入稳定可用状态，配合HDRP和URP渲染管线使用。在此之前，VFX Graph的粒子外观只能依赖内置的Lit/Unlit输出节点，无法实现折射、次表面散射等复杂光照效果。Shader Graph集成打破了这一限制，开发者可以为粒子火焰编写视差遮蔽贴图效果，或为魔法粒子实现依赖视角的菲涅尔发光。

从特效制作角度看，这一集成的价值在于将"粒子行为"与"粒子外观"彻底解耦。一套Shader Graph资产可以被多个不同行为的VFX Graph共享，反之，同一套粒子行为也可以快速切换多种着色风格，大幅提升特效迭代效率。

## 核心原理

### VFX Graph输出节点的着色器绑定机制

VFX Graph通过**Output Particle Shader Graph**节点实现集成。该节点在Inspector面板中暴露一个Shader Graph字段，接受类型为`VFX Shader Graph`的着色器资产。要创建可被VFX Graph识别的Shader Graph，必须在Shader Graph的Graph Settings中将**Target**设置为`VFX`，而非默认的`Universal`或`HDRP`。这一Target选项会在Shader Graph内自动生成一组VFX专用的输入端口，包括`VFXPositionWS`（世界空间位置）、`VFXNormalWS`（世界空间法线）和`VFXTexCoord`（UV坐标）。

### 属性映射与Exposed属性通道

Shader Graph中被标记为**Exposed**的属性，会自动出现在VFX Graph的Output节点属性列表中，允许VFX Graph在每个粒子层面对该属性赋值。例如，若Shader Graph中暴露一个名为`_AlphaScale`的Float属性，则VFX Graph可以用粒子的年龄（Age/Lifetime比值）驱动该属性，实现粒子在生命末期自然淡出的效果。这与普通材质的属性绑定有本质区别——普通材质的Exposed属性只能提供全局统一值，而VFX Graph的绑定是**逐粒子（Per-Particle）**的，每个粒子可以拥有独立的着色参数值。

属性映射使用GPU缓冲区传递，VFX Graph在模拟步骤计算出每个粒子的属性值后，将其写入一个Structured Buffer，Shader Graph在片元着色阶段通过该Buffer读取对应粒子的数据，整个过程不涉及CPU回读，保持了全程GPU驱动的性能优势。

### 顶点变形与自定义插值器

VFX Graph的Shader Graph集成支持**自定义顶点插值器（Custom Interpolator）**，这是2022 LTS版本新增的关键特性。开发者可以在VFX Graph的顶点阶段（Vertex Output Context）计算每个顶点的自定义数据，例如顶点在粒子本地空间中的极坐标角度，然后通过Custom Interpolator将该值传递给Shader Graph的片元阶段使用。典型公式为：

```
θ = atan2(localPos.z, localPos.x)
扭曲偏移 = sin(θ × frequency + time) × amplitude
```

其中`frequency`和`amplitude`均可作为Exposed属性由粒子属性驱动，实现每个粒子表面扭曲频率各异的动态效果。

## 实际应用

**火焰特效的折射扭曲**：在HDRP管线下，为火焰粒子创建带有折射（Refraction）节点的Shader Graph，通过VFX Graph的粒子年龄驱动折射强度（IntensityScale属性）——粒子生命初期折射强度为0.15，在生命50%时峰值达到0.4，随后衰减至0，模拟火焰中心热空气扰动先增强后消散的视觉逻辑。

**护盾命中波纹**：将一个带有球形粒子的VFX Graph与含有`ScanLine`Shader Graph绑定，Shader Graph根据粒子的生命比值（0到1）计算一个向外扩散的环形UV遮罩：`ring = step(abs(uv.r - age), 0.05)`，VFX Graph负责控制命中点位置和粒子的物理扩散，Shader Graph控制环形波纹的像素形态，二者职责清晰。

**蒙皮网格表面能量流**：结合前置知识蒙皮网格采样，将从角色皮肤表面采样得到的粒子，绑定一个包含各向异性高光（Anisotropic BSDF）的Shader Graph，通过VFX Graph将每个粒子的切线方向（来自蒙皮网格的切线属性）传入Shader Graph，使粒子高光方向与角色皮肤纹理走向对齐，实现贴合角色体表的能量流动效果。

## 常见误区

**误区一：将普通URP Shader Graph直接拖入VFX Graph输出节点**。这是最高频的错误。普通URP Target的Shader Graph缺少VFX顶点数据输入端口，拖入后Output节点显示"Shader Graph is not compatible"错误。正确做法是在创建Shader Graph时选择空白模板，然后在Graph Settings的Active Targets中添加`VFX`而非`Universal`，两者Graph Settings面板入口相同但选项不同，极易混淆。

**误区二：认为逐粒子属性与MaterialPropertyBlock等价**。部分开发者认为VFX Graph的逐粒子Shader属性等同于在CPU上使用MaterialPropertyBlock批量设置，因此担心性能问题而回避使用。实际上VFX Graph的逐粒子属性完全在GPU上的Compute Shader阶段写入Buffer，与CPU的MaterialPropertyBlock机制完全独立，不会产生CPU端的DrawCall开销，100万粒子的逐粒子属性传递与1000粒子的开销在GPU侧几乎相同（受带宽限制而非调用次数）。

**误区三：在Shader Graph的VFX Target下使用Screen Space功能**。`Distortion`（屏幕空间扭曲）等依赖OpaqueTexture的节点在VFX Target中的行为与标准URP Material不完全一致，HDRP下需要单独开启`Distortion Sort Priority`并设置正确的渲染队列偏移（默认偏移值为0，命中粒子需要设置为-1以保证在不透明物体之后渲染），否则扭曲区域会采样到自身粒子造成穿帮。

## 知识关联

从**蒙皮网格采样**到Shader Graph集成，是VFX Graph从"粒子从哪里来"到"粒子看起来像什么"的延伸。蒙皮网格采样解决了粒子的位置来源和属性继承问题（切线、法线、UV），而这些从蒙皮网格继承的顶点属性恰好是Shader Graph集成中自定义插值器的数据源——没有蒙皮网格采样提供的精确顶点数据，Shader Graph中依赖切线方向的各向异性效果便无从实现。

向后延伸至**Timeline集成**，Shader Graph集成提供了一个关键基础：Timeline可以通过Exposed属性对VFX Graph进行时间轴控制，而VFX Graph又可以将部分属性转发给绑定的Shader Graph。这意味着Timeline上的一个`float`轨道可以最终控制Shader Graph中溶解效果的消融阈值，形成"剧情事件→Timeline→VFX Graph→Shader Graph→像素颜色"的完整驱动链路。理解Shader Graph集成中属性映射的方向性（单向从VFX Graph流向Shader Graph），是正确设计Timeline控制链路时避免属性回路错误的关键。