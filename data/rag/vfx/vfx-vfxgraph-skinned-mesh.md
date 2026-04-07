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
quality_tier: "S"
quality_score: 82.9
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

# 蒙皮网格采样

## 概述

蒙皮网格采样（Skinned Mesh Sampling）是VFX Graph中一种从骨骼动画角色表面直接生成粒子的技术。与静态网格采样不同，蒙皮网格采样能够实时追踪骨骼权重变形后的顶点世界坐标，使粒子始终贴合角色皮肤表面运动。这项功能在Unity VFX Graph中通过`Sample Skinned Mesh`节点实现，该节点在2019.3版本随VFX Graph正式发布时首次加入。

蒙皮网格采样的核心价值在于解决动态角色与粒子系统之间的数据同步问题。传统粒子系统无法感知骨骼动画的形变，只能将角色视为静态边界框，导致粒子与角色动作产生明显错位。蒙皮网格采样通过每帧读取`SkinnedMeshRenderer`的变形后网格数据，将顶点位置、法线方向和UV坐标实时传递给GPU上的粒子系统。

这项技术在制作燃烧角色、能量溢出、受伤流血等贴合角色躯体的特效时不可替代。它要求目标对象必须挂载`SkinnedMeshRenderer`组件，并且在VFX Graph的上下文中以`Skinned Mesh`类型的属性公开绑定。

## 核心原理

### GPU蒙皮数据读取机制

蒙皮网格采样依赖Unity将CPU端骨骼矩阵运算结果写入一块临时GPU缓冲区的机制。在启用该功能后，VFX Graph要求`SkinnedMeshRenderer`开启`Update When Offscreen`选项，否则当角色离开摄像机视锥时骨骼计算会被Unity剔除，导致粒子发射位置冻结在最后一帧的网格状态。`Sample Skinned Mesh`节点直接从这块GPU缓冲区采样，避免了CPU-GPU数据回传的性能瓶颈。

### 采样模式与数据输出

`Sample Skinned Mesh`节点提供两种采样模式：**按顶点索引（Vertex Index）**和**随机表面（Random Surface）**。

- **Vertex Index模式**：输入一个整数索引`[0, VertexCount-1]`，精确返回该顶点在当前帧骨骼变形后的世界坐标（Position）、法线（Normal）和切线（Tangent）。适合需要在固定解剖位置生成粒子的场景，例如在角色肩膀顶点位置产生火焰特效。

- **Random Surface模式**：节点内部通过重心坐标插值（Barycentric Coordinate Interpolation）在三角面上随机采样，公式为：
  $$P = u \cdot V_0 + v \cdot V_1 + (1-u-v) \cdot V_2$$
  其中 $u, v \geq 0$ 且 $u + v \leq 1$，$V_0, V_1, V_2$ 为三角形三个顶点的变形后坐标。这保证了粒子在网格表面的均匀分布而非聚集在顶点密集区域。

### 与Point Cache的关键区别

Point Cache存储的是烘焙于文件中的静态顶点快照，无法反映运行时骨骼动画的实时形变。蒙皮网格采样每帧从`SkinnedMeshRenderer`的动态缓冲区读取数据，这意味着当角色执行奔跑动画时，粒子生成坐标会随手臂摆动、腿部抬起而实时更新。代价是蒙皮网格采样必须在运行时（Play Mode）才能看到正确结果，在编辑器静止预览时只会采样T-Pose网格数据。

### 采样率与性能控制

在`Initialize Particle`上下文中使用蒙皮网格采样时，建议将单帧发射粒子数控制在目标网格顶点数的1/10以内，以避免大量重复采样同一顶点造成视觉聚集。对于顶点数约8000的标准人形角色网格，单帧发射上限通常设置为800个粒子，可通过`Spawn Rate`节点结合角色动作速度动态调整。

## 实际应用

### 角色溶解与重组效果

制作角色传送特效时，将`Sample Skinned Mesh`的Position输出接入`Set Position`模块，同时将Normal输出乘以一个随时间增大的速度标量作为粒子初速度。粒子从角色全身表面均匀飞散，视觉上模拟身体分解为能量粒子的效果。关键在于在粒子生命周期的前20%帧内采用Random Surface模式密集发射，之后停止发射让已存在粒子自由飞散。

### 血液与液体飞溅

在角色受击时，通过C#脚本调用`VFXEventAttribute.SetInt("hitVertexIndex", closestVertex)`将最近受击顶点索引传递给VFX Graph，再由`Sample Skinned Mesh`的Vertex Index模式精确从该位置生成血液粒子。结合Normal方向作为粒子初速度方向，可实现从正确的受击点朝外喷射的物理真实感。

### 能量护盾充能

为法师角色制作全身覆盖的能量充能特效时，使用蒙皮网格采样获取全身表面的法线方向，将粒子初速度设为沿法线向内偏移（Normal乘以-0.05），使粒子悬浮在皮肤表面约5厘米处，再叠加沿Y轴向上的0.2 m/s漂移速度，形成粒子贴身上升的充能视觉效果。

## 常见误区

### 误区一：认为蒙皮网格采样能在Scene视图静态预览中正常工作

许多初学者在编辑器中预览VFX Graph时发现粒子全部聚集在角色T-Pose的初始位置，误以为节点连接有误。实际原因是`SkinnedMeshRenderer`只有在运行时才执行骨骼混合，编辑器静止状态下采样到的是静止蒙皮网格。解决方案是进入Play Mode预览，或使用`BakeMesh()`方法手动烘焙特定动画帧的网格用于编辑器调试。

### 误区二：混淆`Update When Offscreen`与蒙皮采样精度的关系

部分开发者认为不开启`Update When Offscreen`只会在角色离屏时造成问题，实际上Unity的动态遮挡剔除（Dynamic Occlusion Culling）可能在角色被场景物体遮挡时提前停止骨骼计算，即角色仍在视锥内也会导致蒙皮数据冻结。蒙皮网格采样的任何项目中，绑定的`SkinnedMeshRenderer`必须强制勾选`Update When Offscreen`。

### 误区三：将蒙皮网格采样的输出Position直接用于Velocity计算

`Sample Skinned Mesh`输出的是当前帧的绝对世界坐标，若用相邻两帧Position之差计算粒子速度，会在动画关键帧切换时因插值跳变产生瞬间极大速度，导致粒子爆炸性飞散。正确做法是使用节点内置的`Velocity`输出引脚，该引脚由VFX Graph内部用有限差分法计算蒙皮顶点的帧间速度，并已做平滑处理。

## 知识关联

蒙皮网格采样建立在Point Cache的概念基础之上：Point Cache教会了用户如何将网格表面坐标作为粒子生成源，而蒙皮网格采样将这个数据源从静态文件换成了运行时动态骨骼系统，新增了对骨骼权重和帧间变形的处理能力。学习过Point Cache中重心坐标采样和法线偏移的操作习惯，可以直接迁移到蒙皮网格采样的Random Surface模式配置中。

掌握蒙皮网格采样后，下一步学习Shader Graph集成将使粒子的视觉表现与角色材质产生联动。具体路径是将蒙皮网格采样获取的UV坐标输出传递给VFX Graph的粒子颜色模块，再通过Shader Graph中的`VFX Graph Output`节点让粒子颜色采样角色皮肤纹理贴图，实现粒子颜色与角色皮肤颜色精确匹配的高级效果。