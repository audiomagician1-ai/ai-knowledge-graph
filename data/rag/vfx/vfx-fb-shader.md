---
id: "vfx-fb-shader"
concept: "序列帧Shader"
domain: "vfx"
subdomain: "flipbook"
subdomain_name: "序列帧特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 序列帧Shader

## 概述

序列帧Shader是一种专门用于在GPU上驱动精灵表（Sprite Sheet）动画播放的着色器程序，通过在单张纹理内对UV坐标进行数学偏移，实现对特定帧格子的定位与采样。与CPU端逐帧切换贴图的传统方式不同，序列帧Shader将全部帧数据存储在一张Sprite Sheet中，所有帧切换逻辑由顶点着色器或片元着色器内的数学运算完成，无需任何C#脚本参与帧索引管理。

序列帧Shader的技术形态最早随着GPU Particle System的普及而成熟，大约在2010年代初期Unity 3.x和DirectX 11时代开始广泛应用于实时粒子特效。其核心优势在于：一张4096×4096分辨率的Sprite Sheet可容纳64×64共4096帧画面，渲染时Draw Call维持为1，极大降低了爆炸、火焰、魔法圈等复杂特效的渲染开销。

理解序列帧Shader的价值在于它是粒子系统特效与过场动画特效之间的技术桥梁——粒子系统的TextureSheetAnimation模块在底层就依赖此类Shader逻辑，而手写Shader版本则允许美术对混合模式、裁剪边界、帧过渡曲线进行精细控制，这是模块化工具无法提供的灵活度。

---

## 核心原理

### UV偏移计算

序列帧Shader的基础是将原始UV坐标`(u, v)`映射到Sprite Sheet内某一帧的局部UV区间。假设Sprite Sheet横向有`colCount`列、纵向有`rowCount`行，则每帧的UV尺寸为：

```
frameWidth  = 1.0 / colCount
frameHeight = 1.0 / rowCount
```

给定当前帧索引`frameIndex`（从0开始），列编号与行编号分别为：

```
col = frameIndex % colCount
row = floor(frameIndex / colCount)
```

最终采样UV为：

```
u_final = u * frameWidth  + col * frameWidth
v_final = v * frameHeight + row * frameHeight
```

注意：大多数DCC工具（如Houdini、AE）导出Sprite Sheet时，行排列从图像顶部开始，而OpenGL/Unity的UV原点在左下角，因此`row`需要对`rowCount`取反：`row = (rowCount - 1) - floor(frameIndex / colCount)`，否则动画将出现上下颠倒的播放顺序。

### 帧索引的时间驱动与裁剪

帧索引通常由`_Time.y`（Unity内置时间变量，单位秒）驱动：

```hlsl
float frameIndex = floor(_Time.y * _FPS) % (_ColCount * _RowCount);
```

其中`_FPS`为外部传入的播放帧率参数，典型特效设置范围为12～30帧/秒。`floor`函数保证帧索引为整数，`%`取模防止超出总帧数。

**裁剪（Clip）**是序列帧Shader中的重要步骤：Sprite Sheet边缘往往存在出血区（Bleeding），相邻帧的像素会因双线性过滤渗入当前帧。解决方案是在采样前对帧内UV进行Clamp，将`u`和`v`分别限制在`[epsilon, 1 - epsilon]`（epsilon通常取0.001～0.005），等效于对每帧格子的边界收缩0.1%～0.5%：

```hlsl
float2 clampedUV = clamp(frameUV, _TexelSize * 0.5, 1.0 - _TexelSize * 0.5);
```

### 帧混合（Frame Blending）

基础序列帧Shader在帧切换时会产生跳帧感，帧混合技术通过对相邻两帧进行线性插值消除此问题。方法是同时计算`frameIndex`和`frameIndex + 1`两套UV偏移，分别采样得到`colorA`和`colorB`，再用时间分数`t = frac(_Time.y * _FPS)`作为插值权重：

```hlsl
float4 colorA = tex2D(_MainTex, uvA);
float4 colorB = tex2D(_MainTex, uvB);
float4 finalColor = lerp(colorA, colorB, t);
```

帧混合会使每帧的采样次数从1次变为2次，片元着色器的纹理带宽成本翻倍。在移动端，若Sprite Sheet分辨率为2048×2048，帧混合会导致带宽从约16 MB/帧增至32 MB/帧，需权衡画质与性能。

---

## 实际应用

**爆炸特效**：爆炸序列帧通常使用8列×8行共64帧的Sprite Sheet，`_FPS`设为24，整段动画持续约2.67秒。Shader中配合`_AlphaClip`参数（通常设为0.1）剔除透明像素，避免Alpha混合造成的排序问题，同时使用Additive混合模式强化光晕感。

**UI技能冷却动画**：在2D UI场景中，序列帧Shader被挂载到Image组件的Material上，`_FPS`由外部脚本根据技能冷却时间动态计算，使动画播放速度与实际冷却进度严格对齐。此场景要求Shader支持`_CustomData`输入，以便每个UI实例维护独立的播放进度。

**粒子系统集成**：在Unity Particle System的Custom Vertex Streams中，将`TEXCOORD1.xy`设为`UV2`，在Shader中读取粒子系统传入的`frameBlend`值覆盖`_Time.y`驱动，实现每颗粒子独立播放进度的序列帧，这是手写序列帧Shader与粒子系统配合的标准范式。

---

## 常见误区

**误区一：认为Sprite Sheet必须是正方形且每帧等分**。实际上，Sprite Sheet允许非均匀布局（如Atlas打包后的变长帧），但基础UV偏移公式假设每帧尺寸一致。若使用非等分布局，则必须将每帧的`(offsetX, offsetY, scaleX, scaleY)`打包进纹理数据或Buffer中，Shader逐帧查表，计算复杂度显著提升，不适用于移动端实时特效。

**误区二：帧混合适用于所有序列帧动画**。帧混合的前提是相邻帧在视觉上具有连续性。对于包含闪光、冲击波等强烈跳变的爆炸特效，帧混合会导致"鬼影"（Ghost Artifact），原本清晰的冲击环在混合态呈现半透明叠加状态，破坏特效的冲击力。此类特效应关闭`_FrameBlend`参数，保留硬切换。

**误区三：UV裁剪和UV Clamp是同一件事**。Clamp是将UV锁定在\[0,1\]防止贴图重复，而序列帧Shader中的裁剪是在帧内局部UV空间\[0,1\]范围内进一步向内收缩，两者作用域不同。若仅做全局UV Clamp而不做帧内裁剪，相邻帧出血的问题依然存在。

---

## 知识关联

**前置概念——扭曲序列帧**：扭曲序列帧Shader在本文UV偏移公式的基础上，额外引入一张流体噪声扰动图对`frameUV`进行二次偏移，扭曲的计算发生在帧定位之后、边界裁剪之前。掌握基础序列帧Shader的UV偏移数学是理解扭曲采样插入点的必要条件。

**后续概念——序列帧优化**：序列帧Shader的性能瓶颈集中在纹理采样次数（帧混合时为2次）和Sprite Sheet的Mipmap问题（跨帧Mipmap采样导致相邻帧像素渗透）。序列帧优化专题将介绍如何通过手动计算`tex2Dbias`的LOD偏移、使用`tex2Dgrad`传入帧内梯度，以及ETC2/ASTC压缩格式对Sprite Sheet的适配策略来解决这些问题。

**后续概念——UV滚动**：UV滚动是序列帧UV偏移的退化形式——当Sprite Sheet退化为1行无限宽的贴图时，帧索引偏移等价于沿U轴的连续滚动。理解序列帧Shader中`col * frameWidth`的偏移本质，有助于将UV滚动视为特例进行统一推导，而非将其视为独立技术点重新学习。
