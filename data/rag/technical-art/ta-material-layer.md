---
id: "ta-material-layer"
concept: "材质分层"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 材质分层

## 概述

材质分层（Material Layering）是指在同一个表面上将多个独立材质通过特定权重或遮罩堆叠混合的技术手段。与单一材质只描述一种物理外观不同，材质分层允许一个网格体同时呈现"铁锈覆盖在金属上"或"泥土附着于岩石表面"这类多层次的真实感效果，每一层都保持各自完整的PBR参数集（BaseColor、Roughness、Metallic、Normal）。

该技术在2012年前后随虚幻引擎4和寒霜引擎的材质图层系统（Material Layer System）广泛应用于AAA游戏制作流程。《杀戮地带：暗影坠落》等次世代游戏首次大规模使用高度混合驱动的材质分层，使武器和环境表面在不增加额外Draw Call的前提下呈现多层磨损细节。

材质分层对技术美术的意义在于它将"艺术表达"与"性能预算"解耦——美术人员可以独立制作单层材质资产，技术人员只需调整混合逻辑，无需重写整个Shader。这与传统的单一超级着色器相比，大幅降低了材质维护成本，也是Unreal Engine 5中材质层（Material Layer）资产格式成为标准工作流的根本原因。

---

## 核心原理

### 高度混合（Height-based Blending）

高度混合是材质分层中最物理直觉的混合方式。其核心公式为：

```
BlendWeight = saturate((HeightA - HeightB + BlendSharpness) / BlendSharpness)
```

其中 `HeightA` 为上层材质的高度图采样值，`HeightB` 为下层材质的高度图采样值，`BlendSharpness` 控制过渡锐度（典型值范围0.1～0.5）。当 BlendSharpness 趋近于0时，过渡边界几乎硬切；接近0.5时则产生柔和渐变。这一公式的物理含义是：凸起部分（高度值大）的材质会"压住"凹陷部分的材质，模拟灰尘落在砖缝高处、积雪堆积于石块顶部的自然现象。

### 遮罩分层（Mask-based Layering）

遮罩分层使用一张专门绘制或程序生成的灰度遮罩贴图来决定每层材质的覆盖区域。每个灰度通道可以独立存储一层的覆盖信息，因此一张RGBA遮罩贴图理论上可承载4个独立材质层的分布数据，这一做法在Houdini程序化管线中被称为"Layer Mask Packing"。遮罩分层的关键在于过渡区域的处理——直接用Lerp节点混合两套Normal贴图时，法线方向会产生错误的中间值，必须使用Blend_Overlay或专用的BlendAngleCorrectedNormals节点才能保证法线混合结果物理正确。

### 材质函数叠加（Material Function Stacking）

Unreal Engine的材质函数（Material Function）允许将单层完整PBR材质封装为可复用模块，再通过"Make Material Attributes"和"Blend Material Attributes"节点将多个材质函数的输出按权重合并为最终属性集。典型结构是：

- **Layer_Base**：基础金属材质函数，输出完整MaterialAttributes
- **Layer_Rust**：锈迹材质函数，输出完整MaterialAttributes  
- **BlendNode**：以高度混合权重作为Alpha，对两组属性逐参数插值

这种结构要求着色器中必须开启"Use Material Attributes"选项，否则单独的BaseColor/Roughness输出引脚无法接受MaterialAttributes类型的连接。每新增一个材质层，Shader的Instruction Count通常增加80～150条，因此移动平台项目普遍将分层数量限制在2层以内。

---

## 实际应用

**角色装备磨损系统**：在第一人称射击游戏中，武器模型通常配置3层材质：底层为干净金属、中层为使用磨损层（利用法线贴图曲率驱动遮罩自动生成棱边磨损）、顶层为污迹/油渍层。《地平线：西部禁域》的武器材质中可以看到高度混合权重被绑定到材质参数集（MPC），随游戏内耐久度数值实时更新，使武器外观随耐久衰减动态变化。

**地形混合**：UE5的Landscape材质使用Landscape Layer Blend节点实现泥土、草地、岩石三种地面材质的空间分层，配合高度混合后，岩石层会自然从凸起处"冒出"草地覆盖，无需美术手动绘制过渡区域。这与传统顶点色混合的区别在于，高度混合的过渡边界受高度图形态控制，视觉上更接近自然侵蚀效果。

**建筑材质老化**：程序化材质工具Substance Designer提供"Multi Material Blend"节点，可以将干净混凝土、霉斑、剥落涂料三层材质按Ambient Occlusion、曲率和随机噪点的组合权重分层输出，生成一张包含全部分层逻辑的Tileable贴图，最终在引擎侧只需一个材质实例即可控制整栋建筑的老化程度。

---

## 常见误区

**误区一：法线贴图可以直接Lerp混合**  
许多初学者直接用`Lerp(NormalA, NormalB, Alpha)`混合两层法线，这会导致混合区域的法线向量长度小于1，出现不正确的光照反应（高光"塌陷"）。正确做法是使用引擎内置的BlendAngleCorrectedNormals函数，该函数将两层法线转换到切线空间的偏导数形式后叠加，再归一化，确保输出向量始终是单位向量。

**误区二：层数越多效果越好**  
实际上，每增加一个材质层，GPU需要多采样至少4张贴图（BaseColor、Roughness、Metallic、Normal），在512×512的贴图分辨率下，3层材质已需要12次贴图采样，极易触碰移动端16次采样上限（OpenGL ES 3.0规范）。正确的工作流是先通过Substance Designer将多层混合结果烘焙为单张贴图集，只在需要运行时动态变化（如耐久系统）时才保留引擎侧的实时分层。

**误区三：高度混合等价于简单的遮罩混合**  
高度混合的权重是由两层材质各自的高度图相互竞争计算得出的，这意味着同一个位置的混合权重会随两张高度图的局部细节同时变化，产生犬牙交错的自然边界。而遮罩混合的边界完全由一张外部遮罩贴图决定，无法自动适应高度图的微观凹凸。两者在边界形态上有本质区别，选择错误会导致材质过渡看起来"手工痕迹明显"。

---

## 知识关联

材质分层以PBR材质基础为前提，要求学习者已经理解BaseColor、Roughness、Metallic和Normal四个核心通道的物理含义——只有明确这些参数的独立语义，才能理解为何"逐参数插值"是合法的混合操作，而不是简单的图像叠加。

在掌握材质分层后，可以自然过渡到**材质混合技术**，后者聚焦于运行时动态驱动层权重的技术方案，包括顶点色、距离场和物理交互触发的混合权重更新机制，是材质分层从静态效果走向动态表现的延伸。同时，**贴花系统**与材质分层互为补充：贴花适合在已完成分层的基础材质上叠加局部细节（弹孔、血迹），其本质是在材质分层体系之外单独插入一个Screen-Space或Deferred层，两者结合可覆盖从宏观磨损到微观细节的完整表现需求。
