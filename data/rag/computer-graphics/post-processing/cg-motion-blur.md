---
id: "cg-motion-blur"
concept: "运动模糊"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 3
is_milestone: false
tags: ["效果"]

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
updated_at: 2026-04-01
---


# 运动模糊

## 概述

运动模糊（Motion Blur）是一种模拟摄影曝光期间物体移动所产生视觉拖影效果的后处理技术。在现实摄影中，当快门速度慢于物体运动速度时，物体会在底片上留下连续的轨迹，形成自然的模糊带。图形渲染引擎通过在单帧图像的基础上对像素进行方向性模糊采样，来模拟这种曝光积累效果，从而使动态画面更自然流畅，消除高帧率下画面抖动感。

运动模糊技术在游戏图形领域的大规模应用始于2000年代中期，Crytek的CryEngine 2（2007年）将其作为标配后处理效果引入。早期实现直接对全屏进行基于摄像机运动的模糊，而现代方案已演进为能够区分单个物体运动与摄像机运动的精细化系统。Epic Games在Unreal Engine 4中将Per-Object Motion Blur正式作为生产特性开放，使得角色奔跑、车辆行驶等局部运动可以独立产生模糊效果。

运动模糊在视觉体验上的意义不只是美观：人类视觉系统在跟踪运动物体时本身会产生生理性模糊，缺乏运动模糊的高速动画反而会让人感觉不自然，甚至引发视觉疲劳。在电影标准24fps的渲染中，运动模糊几乎是还原真实感的必要条件，180度快门角（等效快门速度为帧率的二倍分之一）是业界约定的参考标准。

---

## 核心原理

### Velocity Buffer（速度缓冲区）方案

现代运动模糊的主流实现基于**Velocity Buffer**，也称为Motion Vector Buffer。在几何渲染阶段，着色器额外输出每个像素在屏幕空间的二维速度向量，单位为NDC坐标差值（当前帧位置减去上一帧位置）。

速度向量的计算公式如下：

$$\vec{v} = \text{pos}_{\text{current}} - \text{pos}_{\text{prev}}$$

其中 $\text{pos}_{\text{current}}$ 为顶点经当前帧MVP矩阵变换后的NDC坐标，$\text{pos}_{\text{prev}}$ 为同一顶点经**上一帧**MVP矩阵变换后的NDC坐标。Velocity Buffer通常使用RG16F格式存储，两个通道分别存储X和Y方向的速度分量，精度足够覆盖全屏快速运动。

后处理阶段读取Velocity Buffer，沿速度方向对颜色缓冲区进行多点采样（典型采样数为8到16次），取加权平均值输出为最终像素颜色。采样步长由速度向量长度和用户设置的模糊强度系数共同决定。

### Camera Motion Blur（摄像机运动模糊）

摄像机运动模糊作用于整个屏幕，速度向量来源是当前帧与上一帧的**View-Projection矩阵差**，无需依赖物体本身的位移数据。具体做法是将每个像素的深度值重建为世界空间坐标，分别用当前帧和上一帧的VP矩阵投影到屏幕空间，取差值作为速度向量。

这种方法的核心优势在于计算成本极低——只需一次全屏后处理Pass，不需要修改场景中任意物体的渲染逻辑。但其限制是仅能反映摄像机本身的平移与旋转，无法表现场景内独立运动物体（如跑动的角色）所产生的局部模糊。

### Per-Object Motion Blur（逐物体运动模糊）

Per-Object Motion Blur需要在场景的Geometry Pass中，为每个可运动物体的Mesh单独记录上一帧的变换矩阵。蒙皮动画角色还需将骨骼的上一帧蒙皮权重也传入着色器，才能正确计算蒙皮网格的逐顶点速度向量。

实现时，引擎通常维护一个"上一帧Transform缓存"，在每帧渲染开始前将需要产生运动模糊的对象的Transform写入缓存，下一帧渲染时读取。静止物体（速度向量为零向量）不参与模糊采样，直接输出原色，这是Per-Object方案能在性能和质量间取得平衡的关键设计。

Per-Object和Camera Motion Blur的速度向量可以写入同一张Velocity Buffer，最终的后处理模糊Pass统一消费这张缓冲区，Camera Blur对应的像素速度覆盖来自静态背景，而运动物体像素的速度来自Per-Object计算结果。

---

## 实际应用

**赛车游戏**：车辆以高速穿越屏幕时，Per-Object Motion Blur使车身产生横向拖影，而Camera Motion Blur同步处理摄像机跟随产生的背景模糊，两种效果叠加还原赛车游戏的速度感。《极品飞车》系列正是利用夸张的运动模糊强度（将模糊强度系数调高至正常值的1.5到2倍）来营造极速氛围。

**第一人称射击游戏**：FPS游戏通常对Camera Motion Blur持谨慎态度，因为快速转视角时的全屏模糊会严重干扰玩家的目标瞄准。许多FPS游戏（如《使命召唤》系列）默认关闭Camera Motion Blur，仅保留武器和手臂的Per-Object Motion Blur，或提供独立的开关选项。

**电影级渲染**：在离线渲染或电影CG制作中，运动模糊通常使用时间采样（Temporal Sampling）方案，在一帧的模拟时间范围内均匀采集8到64个子帧后合成，计算量是实时方案的数十倍，但物理精度远高于Velocity Buffer近似方法。

---

## 常见误区

**误区一：速度向量越长，模糊效果越好**

Velocity Buffer中的速度向量长度需要被合理裁剪（Clamp）。当速度超过屏幕分辨率的某个阈值（通常为屏幕短边的10%到20%）后，继续增大模糊长度会导致采样范围超出屏幕边界，出现边缘色彩渗漏（Bleeding）瑕疵，以及因采样点稀疏而产生明显条纹（Ghosting）。正确做法是为速度向量设置最大长度上限并配合足够的采样数。

**误区二：Per-Object Motion Blur可以完全替代Camera Motion Blur**

两者的速度来源不同，不可互相替代。Camera Motion Blur计算的是背景静态物体因摄像机移动产生的速度，这些物体本身没有运动，在Per-Object方案中速度向量为零，因此Camera Motion Blur是静态背景在摄像机运动时产生正确拖影的唯一途径。

**误区三：运动模糊只影响快速移动的物体**

低速运动物体在Velocity Buffer中的速度向量接近零，后处理采样范围极小，肉眼可见的模糊效果几乎为零。但这些速度向量仍会被写入Buffer，参与后续的TAA（时间性抗锯齿）重投影计算——Velocity Buffer在现代渲染管线中同时服务于运动模糊和TAA两种后处理，这使得即便视觉上不需要模糊的物体也必须正确输出速度向量。

---

## 知识关联

运动模糊建立在**后处理概述**所介绍的渲染管线概念之上：它需要在Geometry Pass之后存在独立的后处理Pass，并依赖MRT（Multiple Render Targets）技术将速度向量与颜色同时输出到不同的缓冲区。理解G-Buffer的存储结构有助于明白为何Velocity Buffer可以与深度缓冲共用渲染目标。

从技术延伸角度看，Velocity Buffer是**TAA（时间性抗锯齿）**的必要输入——TAA利用速度向量将上一帧的像素正确重投影到当前帧，实现跨帧采样累积。在集成了TAA的现代渲染管线中，运动模糊的Velocity Buffer生成Pass往往与TAA的Motion Vector Pass合并，避免重复计算变换矩阵，这是性能优化中频繁出现的工程决策。