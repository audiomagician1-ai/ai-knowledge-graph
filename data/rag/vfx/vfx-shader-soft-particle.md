---
id: "vfx-shader-soft-particle"
concept: "软粒子"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 软粒子（Soft Particles）

## 概述

软粒子是一种通过读取深度缓冲（Depth Buffer）并将粒子的透明度与场景几何体的深度差进行比较，从而消除粒子边缘硬切割（Hard Clipping）的渲染技术。当普通粒子四边形（Billboard Quad）与不透明几何体相交时，会产生清晰可见的矩形截断线；软粒子通过在交叉区域衰减Alpha值，让烟雾、火焰、爆炸等体积感效果与场景无缝融合。

该技术最早由Nvidia在2007年的"Soft Particles"白皮书中系统化提出，随后被整合进DirectX 10的示例代码库。其核心突破在于利用了延迟渲染管线中已经存在的深度缓冲，无需额外的几何信息，只需一次纹理采样即可完成柔和过渡。

在游戏和实时特效制作中，软粒子解决的是视觉瑕疵中最常被玩家无意识察觉的一类——粒子"插入"地面或墙壁时的塑料感切边。烟雾贴着地面滚动、蒸汽从地缝升起、爆炸冲击波扫过建筑，这些场景在没有软粒子的情况下都会露出拼贴感。

---

## 核心原理

### 深度差计算公式

软粒子的核心运算是比较两个深度值：**场景深度**（从深度缓冲中采样）与**粒子自身深度**（当前片元的线性深度）。衰减系数由以下公式决定：

```
softFactor = saturate((sceneDepth - particleDepth) / fadeDistance)
```

- `sceneDepth`：深度缓冲中重建的线性深度，单位为世界空间距离（米）
- `particleDepth`：当前粒子片元到摄像机的线性深度
- `fadeDistance`：控制过渡区域宽度的参数，典型值为 **0.5 到 2.0 米**
- `saturate`：将结果钳制在 [0, 1] 范围

最终粒子的Alpha值为 `originalAlpha × softFactor`，使得粒子在靠近几何体表面时透明度自然降为零。

### 深度缓冲的采样与重建

深度缓冲存储的是非线性的NDC空间深度值（范围0到1），直接相减没有物理意义。必须将其还原为线性相机空间深度，使用以下公式（以OpenGL约定为例）：

```
linearDepth = (2.0 * near * far) / (far + near - ndcDepth * (far - near))
```

其中 `near` 和 `far` 分别是摄像机近远裁切面距离。Unity引擎中通过 `LinearEyeDepth()` 函数封装此转换；Unreal Engine则通过 `SceneDepth` 材质节点直接输出线性深度，无需手动换算。

### 前向渲染与延迟渲染的差异

在**延迟渲染**管线中，深度缓冲在G-Buffer阶段已经写入了全场景几何深度，粒子渲染阶段可以直接读取，软粒子实现相对简单。在**前向渲染**管线中，透明物体不写入深度缓冲，因此软粒子需要借助一张额外的**预先渲染好的不透明场景深度副本**（Pre-pass Depth Texture）。Unity的URP管线中，需要在渲染器资产里启用"Depth Texture"选项才能为粒子Shader提供 `_CameraDepthTexture`。

### fadeDistance参数的物理含义

`fadeDistance` 不是随意调整的艺术参数，它应该对应粒子效果的"物理厚度感"。一团地面烟雾的 `fadeDistance` 设为1.5米表示：当粒子四边形距离地面1.5米以内时开始渐隐，模拟烟雾密度从地表向上逐渐稀薄的真实现象。若该值设置过小（如0.05米），效果退化为近似硬切；设置过大（如5米），粒子在远离交叉面时也会变淡，丢失体积感。

---

## 实际应用

**地面烟雾与扬尘**：士兵奔跑扬起的尘土贴着地面扩散，软粒子使尘土颗粒在接触地表时自然消融，而非在地面上方0.1米处突然截断。`fadeDistance` 通常设为0.3至0.8米以匹配尘埃颗粒大小。

**水面蒸汽**：热泉或岩浆表面的蒸汽效果，粒子发射点就在水面几何体上。没有软粒子时，蒸汽底部会出现整齐的矩形切线与水面齐平，暴露出Billboard的本质。启用软粒子后，蒸汽看起来从液体内部升起。

**爆炸与冲击波**：爆炸粒子系统与建筑物墙壁相交时，软粒子保证火焰/烟雾不会"嵌入"墙体而产生奇怪的几何裁剪，`fadeDistance` 可设为1.0至2.5米以体现爆炸的冲击厚度。

**Unity ShaderGraph实现路径**：使用`Scene Depth`节点（Eye空间）减去`Screen Position`节点的W分量（即粒子的Eye深度），除以一个`fadeDistance`属性，再通过`Saturate`节点输出，连接至粒子材质的Alpha乘法链。

---

## 常见误区

**误区一：认为软粒子会解决所有粒子与场景的穿插问题**
软粒子只处理粒子边缘与不透明几何体的交叉衰减，它无法解决两个透明粒子四边形之间相互穿插的排序问题。两片烟雾粒子互相交叉仍然需要依赖粒子排序或Order-Independent Transparency（OIT）技术，与软粒子是完全不同的问题域。

**误区二：混淆NDC深度与线性深度直接计算**
初学者常犯的错误是直接用深度缓冲的原始值（0到1的NDC非线性值）减去粒子深度值，得到的差值在靠近摄像机的区域非常敏感，在远处几乎无变化。这会导致近处的粒子几乎完全透明，远处粒子与硬粒子无异。必须使用线性深度转换后再做差值运算。

**误区三：在移动平台上不加限制地使用软粒子**
读取`_CameraDepthTexture`在移动GPU上会打断Tile-Based Rendering的合并优化，造成额外的带宽消耗。PowerVR和Mali架构的GPU在深度纹理采样时可能有15%-30%的额外性能开销。移动项目中应通过Shader变体（Shader Keyword）提供不含深度采样的Fallback版本，并在低端设备上禁用软粒子。

---

## 知识关联

**前置概念——纹理流动**：纹理流动技术控制粒子贴图的UV动画，决定了烟雾/火焰的运动形态；软粒子在此基础上解决这些运动贴图与场景几何体的边缘融合问题。两者在同一粒子Shader中共存，流动贴图决定"粒子长什么样"，软粒子决定"粒子如何与世界融合"。

**后续概念——边缘侵蚀（Edge Erosion）**：软粒子通过深度差控制整体透明度衰减，边缘侵蚀则通过噪声纹理采样配合阈值截断控制粒子消散的形态细节。两者可叠加使用：软粒子负责靠近几何体时的整体淡出，边缘侵蚀负责粒子生命周期结束时的碎裂式消散，合力产生自然的烟雾消散效果。

**后续概念——Overdraw控制**：软粒子使粒子边缘区域大量像素的Alpha趋近于零，这些接近透明的像素仍然参与了片元着色器运算，加剧了Overdraw问题。在Overdraw控制的学习中，需要理解软粒子的Alpha衰减区域是Overdraw热点之一，并通过粒子网格裁剪或Early-Out优化来缓解。