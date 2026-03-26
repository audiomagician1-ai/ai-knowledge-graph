---
id: "unity-vfx-graph"
concept: "VFX Graph"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 3
is_milestone: false
tags: ["特效"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# VFX Graph

## 概述

VFX Graph（Visual Effect Graph）是Unity引擎中专为GPU加速粒子特效设计的节点化可视编程系统，于Unity 2018.3版本作为预览功能首次引入，并在Unity 2019.3版本正式进入生产可用状态。与传统Particle System（Shuriken）不同，VFX Graph将粒子模拟计算完全卸载到GPU上执行，单一特效在现代GPU上可轻松处理**数百万个粒子**，而传统CPU粒子系统通常在数万个粒子时就出现明显性能瓶颈。

VFX Graph的运行依赖于Unity的**Scriptable Render Pipeline（SRP）**，因此它只能在URP（Universal Render Pipeline）或HDRP（High Definition Render Pipeline）项目中使用，不支持内置渲染管线（Built-in Render Pipeline）。这一架构选择意味着VFX Graph能直接利用Compute Shader技术，在GPU上并行计算每个粒子的位置、速度、颜色和生命周期等属性，极大提升了大规模特效的实时渲染能力。

在游戏特效制作中，VFX Graph适用于需要海量粒子的场景，例如密集的雨雪天气、爆炸碎片群、星云宇宙场景以及流体模拟近似效果。其节点化界面使美术师无需编写HLSL着色器代码，即可通过连线方式定义粒子的完整生命周期逻辑。

## 核心原理

### GPU粒子计算架构

VFX Graph使用**Compute Shader**在GPU上存储和更新粒子数据。所有粒子的属性（位置、速度、年龄、颜色等）都存储在GPU显存的**GraphicsBuffer**中，CPU每帧只需发送少量参数更新命令，粒子的实际计算完全在GPU端完成。这与传统Shuriken系统每帧在CPU内存中遍历所有粒子对象有本质区别。粒子数据在CPU与GPU之间的回读（Readback）操作默认被禁用，因为这类同步操作会打破GPU流水线并造成性能停顿。

### 系统层级结构：Context与Block

VFX Graph的节点系统由三层结构组成：**Context（上下文）**、**Block（块）**和**Operator（运算符）**。

- **Context**是粒子生命周期的阶段节点，包括`Spawn`（生成）、`Initialize`（初始化）、`Update`（更新）、`Output`（输出）四个核心阶段。粒子从Spawn产生，经Initialize设置初始属性，在Update中每帧更新状态，最终在Output阶段决定渲染方式（如Quad、Mesh、Strip等）。
- **Block**是挂载在Context内部的操作单元，例如在Update Context中添加`Turbulence`块可为粒子施加湍流扰动，添加`Conform to Sphere`块可让粒子向球体表面聚拢。
- **Operator**是独立的数学/逻辑运算节点，如`Noise`、`Sample Texture 2D`、`Cross Product`等，通过连线向Block提供动态数值输入。

### 属性暴露与外部控制

VFX Graph通过**Exposed Property（暴露属性）**机制与外部C#代码或Timeline交互。在Graph中将属性标记为Exposed后，可通过`VisualEffect`组件的API在运行时修改，例如：

```csharp
GetComponent<VisualEffect>().SetFloat("SpawnRate", 500f);
GetComponent<VisualEffect>().SetVector3("AttractorPosition", target.position);
```

VFX Graph还支持**Event**系统，通过`SendEvent("OnPlayerHit")`触发特定粒子效果，实现游戏逻辑与视觉特效的解耦控制，而无需直接操作粒子系统的Play/Stop状态。

### 粒子容量与内存管理

每个VFX Graph资产在创建时需要预先设定**Capacity（容量）**值，这是GPU为该特效分配的最大粒子数上限，在运行时无法动态扩展。该值决定了显存占用量：一个属性配置典型的粒子（位置、速度、颜色、生命期）每粒子约占用**64至128字节**显存，设置100万容量的特效将固定占用约64MB至128MB显存，无论当前实际存活粒子数量多少。因此需要根据目标平台的显存限制谨慎设置容量值。

## 实际应用

**大规模环境特效**：在HDRP项目中制作沙尘暴效果时，利用VFX Graph的`Point Cache`功能从地形网格采样粒子生成位置，配合`Sample Signed Distance Field`节点让粒子与场景几何体产生碰撞近似，可在不依赖物理引擎的情况下实现数十万粒子的流动感。

**技能特效与游戏反馈**：RPG游戏中的法术技能特效常使用VFX Graph的`GPU Event`功能：当一个粒子（如火球主体）在Update阶段触发`Trigger Event on Die`时，可在该位置自动生成子粒子系统（爆炸火花），整个链式特效逻辑全部在GPU端完成，无需CPU介入。

**与Shader Graph联动**：VFX Graph的Output Context中可指定自定义Shader Graph材质，通过将粒子属性（如年龄比率`ageOverLifetime`）传递给Shader Graph的`VFX Input`节点，实现每个粒子独立的UV动画或溶解效果，制作出粒子随生命周期变化外观的高级特效。

## 常见误区

**误区一：认为VFX Graph可以替代所有粒子系统场景**。VFX Graph不支持内置渲染管线，且在移动平台上对GPU Compute Shader的兼容性要求较高（需要OpenGL ES 3.1或Vulkan支持）。对于需要运行在低端移动设备的项目，或粒子数量较少（低于数千个）的简单特效，传统Particle System的CPU开销反而更低，因为GPU Dispatch本身存在固定调用开销。

**误区二：认为容量（Capacity）越大越好**。由于显存在资产加载时即完成分配，将未经评估的特效容量设为100万会立即消耗约64MB以上显存，即便该特效每次只生成100个粒子。在有多个VFX Graph特效同时存在的场景中，盲目设置大容量值极易导致显存超限，引发GPU内存不足错误或渲染卡顿。

**误区三：混淆VFX Graph中的粒子碰撞与物理引擎碰撞**。VFX Graph中的`Collide with Depth Buffer`碰撞是基于屏幕空间深度图的近似碰撞，粒子并不真正参与Unity物理世界的刚体模拟，无法触发OnCollisionEnter等物理回调，也无法与Rigidbody对象产生力的交互。需要真实物理响应时仍需使用传统Particle System的碰撞模块。

## 知识关联

学习VFX Graph需要先掌握Unity引擎的基础架构，特别是Scriptable Render Pipeline的工作方式——因为VFX Graph必须在SRP环境下运行，理解URP或HDRP的渲染流程有助于正确配置Output Context的渲染选项和混合模式。

在图形编程方向，VFX Graph与**Shader Graph**形成互补关系：VFX Graph负责控制粒子的运动与生命周期逻辑，而Shader Graph负责定义粒子的表面着色外观，两者在Output阶段通过材质资产连接。如果希望深入定制粒子行为，可进一步学习HLSL和Compute Shader，以理解VFX Graph内部节点所对应的底层GPU代码逻辑。

在工作流层面，VFX Graph与**Unity Timeline**深度集成，可在过场动画中通过Timeline的VFX Track精确控制特效的触发时机和参数动画，这对于需要精确同步特效与剧情镜头的影视级游戏内容制作至关重要。