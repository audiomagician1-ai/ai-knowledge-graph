---
id: "vfx-vfxgraph-skinned-mesh"
concept: "蒙皮网格采样"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 蒙皮网格采样

## 概述

蒙皮网格采样（Skinned Mesh Sampling）是VFX Graph中一种从骨骼动画角色表面实时生成粒子的技术。与静态网格采样不同，蒙皮网格在每帧都会根据骨骼权重（Bone Weights）发生形变，因此粒子的生成位置和法线方向需要跟随网格顶点的实时变换一起更新。Unity在VFX Graph 10.x（对应Universal Render Pipeline 10.0）版本中正式引入了对`SkinnedMeshRenderer`组件的原生采样支持。

蒙皮网格采样的价值在于它能够将角色动画与粒子特效紧密绑定。例如，制作人物奔跑时脚底扬起的尘土、战士铠甲上迸发的火花，或者法师施咒时沿手臂皮肤流淌的魔法粒子流，这些效果都依赖蒙皮网格采样提供的逐帧蒙皮位置数据。若使用传统的静态网格采样，动画形变后粒子会浮空脱离角色表面，无法实现贴合效果。

## 核心原理

### 顶点变换与骨骼权重

蒙皮网格采样的数学基础是线性混合蒙皮（Linear Blend Skinning，LBS）公式：

$$p' = \sum_{i=1}^{n} w_i \cdot M_i \cdot p$$

其中 $p$ 是顶点在绑定姿势（Bind Pose）下的原始位置，$M_i$ 是第 $i$ 根骨骼的变换矩阵，$w_i$ 是该骨骼对此顶点的权重，$n$ 通常为每顶点最多影响4根骨骼（Unity默认限制）。VFX Graph在GPU端通过Compute Shader读取经过CPU或GPU蒙皮计算后的顶点缓冲区，从而获取每帧最终的蒙皮位置。

### 采样模式：顶点采样与三角形表面采样

VFX Graph提供两种主要采样模式。**顶点采样（Vertex Sampling）**直接从`SkinnedMeshRenderer`的顶点列表中选取坐标，适合粒子数量与顶点数量一一对应的场景，如角色身体每个顶点冒出一颗粒子。**三角形表面采样（Triangle Surface Sampling）**则在三角形面片内部用重心坐标插值计算随机点，公式为 $p = (1-\sqrt{u}) \cdot v_0 + \sqrt{u}(1-v) \cdot v_1 + \sqrt{u} \cdot v \cdot v_2$，其中 $u, v$ 为均匀随机数。三角形采样生成的粒子分布更均匀，适合覆盖面积不均的复杂角色模型。

### 采样上下文：Spawn Context中的位置绑定

在VFX Graph的Spawn Context或Initialize Context中，使用`Sample Skinned Mesh`节点时必须将`SkinnedMeshRenderer`通过**Exposed Property**（暴露属性）从场景中传入图表。节点输出包括：`Position`（蒙皮后世界空间位置）、`Normal`（法线方向）、`Color`（顶点颜色，若存在）以及`TexCoord`（UV坐标）。法线输出在制作粒子朝角色表面外侧喷发的效果时尤为关键，粒子初速度可直接设置为 `Normal * SpawnSpeed`。

### 实时更新与`Update Position`标志

当角色持续播放骨骼动画时，可在Update Context中再次调用`Sample Skinned Mesh`节点，并将每帧新采样的位置赋给粒子的`Position`属性，使粒子始终贴附在网格表面移动。这与Point Cache的静态采样形成对比——Point Cache烘焙的是某一帧的顶点数据，无法响应运行时骨骼变化；而蒙皮网格采样每帧从GPU顶点缓冲中读取最新数据，因此有每帧约0.1~0.3ms的额外GPU读取开销（取决于顶点数量）。

## 实际应用

**角色受击特效**：当敌人角色受到攻击时，在受击骨骼所在的网格区域采样生成血液或火花粒子。通过Bone Mask或顶点颜色通道将采样范围限制在受击部位，可避免全身所有表面都产生粒子。

**溶解消亡效果**：角色死亡时结合粒子生命周期，从蒙皮网格全表面采样生成灰烬粒子，并随时间增大粒子的`Noise Offset`使其向上飘散，形成角色逐渐化为灰烬的视觉效果。此类效果在《Destiny 2》风格的科幻题材游戏中被广泛使用。

**魔法附着流动效果**：沿蒙皮网格法线方向偏移一个固定距离（如0.05米），使粒子悬浮于皮肤表面，配合Update Context中的`Conform to Skinned Mesh`逻辑，令粒子随动画流动，制造液态魔法包裹角色身体的效果。

## 常见误区

**误区一：认为蒙皮网格采样可以直接与静态`MeshRenderer`通用**。`Sample Skinned Mesh`节点专门读取`SkinnedMeshRenderer`提交至GPU的蒙皮后顶点缓冲（通常是`AsyncGPUReadback`或Compute Buffer共享），普通`MeshRenderer`没有此缓冲区，必须改用`Sample Mesh`节点。混用会导致编译错误或粒子全部生成在原点位置。

**误区二：认为顶点采样的粒子分布密度均匀**。蒙皮网格的顶点并不均匀分布在表面——面部、手部等细节区域顶点密度远高于后背、大腿等平坦区域。若直接做顶点采样，角色面部的粒子密度会远大于躯干部分。需要使用三角形表面采样并启用`Surface-Weighted`选项，按三角形面积加权随机选取，才能得到均匀覆盖整个表面的粒子分布。

**误区三：在Spawn Context中每帧重新采样等同于粒子跟随角色运动**。Spawn Context只在粒子出生时执行一次采样，粒子出生后便脱离网格独立运动。若要粒子持续贴附蒙皮表面，必须在Update Context中每帧重新采样并将位置写回，同时将粒子`Lifetime`设置为与特效持续时间匹配的较短数值（如0.016秒，即每帧刷新一次），否则粒子会在出生位置漂离。

## 知识关联

蒙皮网格采样以Point Cache的采样概念为基础：Point Cache教会了你如何从网格表面的采样点读取位置、法线和颜色属性，蒙皮网格采样将这一流程从离线烘焙扩展到了运行时实时计算，增加了对骨骼动画变换的响应能力。在掌握蒙皮网格采样后，下一步学习Shader Graph集成时，可以将蒙皮网格采样输出的UV坐标和顶点颜色传递给自定义Shader，通过粒子的`TexCoord`属性驱动贴图采样，实现粒子颜色随角色贴图变化的高级效果，例如让每颗粒子的颜色精确匹配其出生位置对应的皮肤纹理颜色。
