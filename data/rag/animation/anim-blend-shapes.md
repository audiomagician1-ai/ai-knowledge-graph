---
id: "anim-blend-shapes"
concept: "Blend Shape/Morph Target"
domain: "animation"
subdomain: "facial-animation"
subdomain_name: "面部动画"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Blend Shape / Morph Target（混合形状/变形目标）

## 概述

Blend Shape（混合形状）又称 Morph Target（变形目标），是一种通过储存网格顶点偏移量来记录预制形状、再以权重值（0.0 到 1.0 之间的浮点数）进行线性混合，从而驱动面部网格变形的技术。其核心数学原理为：最终顶点位置 = 基础网格顶点位置 + Σ(权重ᵢ × 偏移量ᵢ)，其中每个偏移量仅存储与基础网格不同的增量坐标，而非完整复制一套顶点数据。

这项技术最早于1980年代在高端视觉特效管线中出现，软件工具如 Alias PowerAnimator（Maya 的前身）在1990年代将其标准化。Pixar 在《玩具总动员》（1995年）制作期间广泛运用 Morph Target 来实现 Woody 和 Buzz 的面部表情，这被认为是 Blend Shape 在生产管线中成熟应用的里程碑。

Blend Shape 之所以在面部动画领域普及，根本原因在于它把复杂的面部肌肉运动预先"烘焙"成离散形状，让动画师只需调节一个0-1的滑块就能重现经过专门雕刻、审美把关的表情。与骨骼驱动相比，Blend Shape 能精确保留雕刻师在角色脸颊、嘴唇、眼睑等软组织区域的细节形变，而无需依赖骨骼权重绘制的近似计算。

---

## 核心原理

### 顶点偏移量存储机制

每一个 Blend Shape 目标实质上是一张稀疏的偏移表：只记录**与基础网格位置不同**的顶点及其 (ΔX, ΔY, ΔZ) 偏移。例如，一个"左眼眯眼"形状可能只影响眼睑周围约200个顶点，而整张脸可能有15,000个顶点，因此仅存储这200条偏移记录即可节约大量内存。Maya 在导出 Blend Shape 时默认使用这种稀疏存储格式，而 Unreal Engine 的 Morph Target 资产同样采用相同策略，仅在运行时将偏移叠加到基础 Skeletal Mesh 上。

### 权重线性混合与超出0-1范围的应用

标准权重范围为 0.0（无效果）到 1.0（完整形状），但许多软件允许**超范围权重**（如 -0.5 或 1.5），以实现夸张变形或相反方向的微调。需要注意的是，多个形状同时激活时发生的是**线性叠加**而非非线性融合，这意味着当"嘴角上扬"和"嘴角下拉"两个形状同时权重为1时，结果是两套偏移量的向量相加，往往产生不合理的中间形态，这正是后续引入**修正 Blend Shape（Corrective Blend Shape）**的直接动机。

### FACS标准与Blend Shape的对应关系

工业界常以**面部动作编码系统（FACS，Facial Action Coding System）**作为 Blend Shape 命名和数量的规范依据。FACS 将人类面部运动分解为 44 个基础动作单元（Action Unit，AU），例如 AU1 对应内眉上扬、AU6 对应颧肌收缩（微笑时眼轮匝肌参与）。MetaHuman 角色标准配备了 **130+ 个 Blend Shape**，涵盖了 FACS 全部 AU 及其左右分侧版本，远超通常游戏角色的 40-60 个形状数量，这一差距直接影响面部动画的细腻程度。

### 法线与切线的同步变形

顶点位置变形后，若法线（Normal）和切线（Tangent）不同步更新，光照计算将产生严重瑕疵——例如脸颊鼓起时出现错误的高光方向。因此正确的 Blend Shape 实现不仅存储顶点位置偏移（ΔPosition），还应存储 **ΔNormal** 和 **ΔTangent**。Unreal Engine 在 Morph Target 资产中默认同时存储这三类偏移，而部分轻量级引擎仅存储位置偏移并在运行时重新计算法线，以降低内存占用但增加 GPU 计算负担。

---

## 实际应用

**游戏实时面部动画**：在 Unreal Engine 5 中，角色的 Morph Target 由动画蓝图中的 **Pose Asset** 或曲线（Curve）节点驱动，动画师可在 Sequencer 里为每条曲线K帧，实现口型（Viseme）和情绪表情的时间控制。一套完整的口型系统通常包含 14-16 个 Viseme 形状，覆盖英语所有音素组合。

**影视级面部捕捉重定向**：Motion Capture 设备（如 iPhone 的 ARKit Face Tracking）输出52个 Blend Shape 系数，这些系数可直接映射到角色的对应形状上，驱动实时面部动画。Unreal Engine 的 Live Link Face 插件正是基于这52个 ARKit Blend Shape 命名规范建立映射表，实现演员面捕到数字角色的实时驱动。

**2D/3D 口型同步**：在 Adobe Character Animator 和 Live2D 中，Blend Shape 等价概念同样被用于口型同步，软件分析音频后自动计算各 Viseme 的权重值，驱动对应形状的插值过渡。

---

## 常见误区

**误区一：Blend Shape 权重越多激活越好**
同时激活大量 Blend Shape 并不能自动产生自然的表情组合。由于多形状线性叠加的数学特性，"抬眉"（AU1+AU2）加"闭眼"（AU46）加"张嘴"（AU27）三个形状同时为1时，眉眼嘴交界区域的顶点会接受来自三个形状的偏移叠加，极易导致皮肤穿模或过度拉伸。真实肌肉运动中这些区域存在非线性的相互制约，需要修正 Blend Shape 来补偿。

**误区二：Blend Shape 与骨骼驱动是互斥选择**
实际生产管线中，两者几乎必然配合使用。下颌骨骨骼（Jaw Joint）负责大幅度旋转驱动嘴部开合，而嘴唇细节的撅起、压扁、拉伸则由 Blend Shape 补充。MetaHuman 系统正是以骨骼系统处理主要运动、以 Blend Shape 精修软组织细节的混合架构，而非单独依赖任一技术。

**误区三：Blend Shape 数据可以无限叠加而不影响性能**
每个激活的 Morph Target 都需要在 GPU 或 CPU 上执行顶点偏移计算。Unreal Engine 文档建议单个 Skeletal Mesh 激活的 Morph Target 数量控制在合理范围，过多激活会导致顶点着色器压力上升。一个拥有15,000顶点、同时激活30个 Morph Target 的角色，每帧需处理的偏移运算量远超仅激活5个的情况，在移动平台上尤为明显。

---

## 知识关联

学习 Blend Shape 之前，需要掌握**面部动画概述**中关于面部网格拓扑的基础知识，尤其是眼轮匝肌、口轮匝肌等区域的环形布线规律——这些区域布线质量直接决定 Blend Shape 形状雕刻时能否获得干净的变形效果。

掌握 Blend Shape 原理后，自然引出**修正 Blend Shape（Corrective Blend Shape）**的学习需求：当两个或多个基础形状同时激活产生错误叠加时，修正形状以乘法权重（权重A × 权重B）为触发条件，补偿线性叠加的不足。此外，**面部绑定**课题将介绍如何用骨骼驱动器（Driver）自动触发 Blend Shape，构建完整的面部控制器体系；**皱纹贴图**技术则在 Blend Shape 形变基础上，通过法线贴图混合实现皮肤褶皱的动态纹理细节，是 Blend Shape 几何变形的重要视觉补充。