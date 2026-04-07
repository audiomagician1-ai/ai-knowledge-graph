---
id: "ta-material-function"
concept: "材质函数"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 材质函数

## 概述

材质函数（Material Function）是虚幻引擎材质系统中用于封装可复用计算逻辑的独立资产，以 `.uasset` 格式存储于内容浏览器中，可被任意数量的材质或其他材质函数调用。与普通材质节点不同，材质函数拥有自己独立的节点图（Node Graph），内部的计算在编译时会被内联（inline）展开到调用它的宿主材质中，因此不产生额外的运行时函数调用开销。

材质函数的概念随虚幻引擎 3（UE3）的后期版本引入，在 UE4 中得到全面完善。其设计动机是解决大型项目中大量材质之间重复编写相同雪花噪声、法线混合、湿润效果等逻辑的问题。引擎内置了超过 80 个官方材质函数，例如专门处理 PBR 层叠混合的 `LayerBlend`，以及用于世界坐标对齐贴图的 `WorldAlignedTexture`，开发者可以直接调用或以它们为参考学习封装规范。

材质函数真正的价值在于"一处修改，全局生效"。假设一个项目中 200 个材质共用同一套角色湿润逻辑，若将该逻辑封装为材质函数，修复其中一个公式错误只需编辑这一个函数文件，保存后所有引用它的材质会自动重新编译更新，而无需逐一打开每个材质资产进行修改。

## 核心原理

### FunctionInput 与 FunctionOutput 节点

材质函数通过两类特殊节点与外部材质通信。`FunctionInput` 节点定义函数的入参，支持 Float1～Float4、Texture2D、TextureCube、StaticBool 等 10 余种类型，每个入参可设置默认值（Preview Value），使得函数在预览时无需宿主材质提供数据即可独立显示结果。`FunctionOutput` 节点定义出参，一个材质函数可以拥有多个输出引脚，例如同时输出 BaseColor 和 Roughness 值，供调用方分别连接到不同通道。

在宿主材质中，材质函数以 `CallMaterialFunction` 节点的形式出现，该节点的左侧引脚对应函数内部的 `FunctionInput`，右侧引脚对应 `FunctionOutput`。编译器在处理宿主材质的 HLSL 代码时，会将材质函数的整个节点图展开，等效于手动复制粘贴了所有节点，因此函数调用次数不影响 Shader 指令层次深度。

### 参数暴露机制（Expose to Library）

材质函数内部可以包含 `ScalarParameter`、`VectorParameter` 和 `TextureObjectParameter` 节点。若在材质函数编辑器的函数属性中勾选 **Expose to Library**，该函数会出现在材质编辑器的节点搜索面板中，可直接拖拽调用，无需手动在内容浏览器中定位资产。更重要的是，材质函数内的参数默认情况下**不会**穿透到材质实例的参数列表中；若需要暴露，必须在宿主材质内通过 `SetMaterialAttributes` 或直接将参数节点提升到宿主层级的方式处理，这与材质实例的参数覆盖机制形成明确的层次分工。

### 静态开关与编译分支

材质函数支持 `StaticBool` 类型的 `FunctionInput`，配合函数内部的 `StaticSwitch` 节点，可以在调用方按需选择不同的计算分支。例如一个通用的法线贴图混合函数可以通过静态开关在"Reoriented Normal Mapping（RNM）混合"和"简单叠加混合"之间切换。由于 `StaticSwitch` 在编译时确定分支，被丢弃的分支不会产生任何 Shader 指令，相比动态 `if` 分支零性能损耗。RNM 混合的核心公式为：

```
n = normalize(float3(n1.xy + n2.xy, n1.z * n2.z))
```

其中 n1、n2 分别为两张法线贴图解码后的切线空间向量，此公式常被封装在名为 `BlendAngleCorrectedNormals` 的材质函数中，是引擎内置函数库的典型案例。

## 实际应用

**角色皮肤次表面散射封装**：将 Subsurface Profile 设置、曲率贴图采样、次表面颜色混合逻辑封装为 `MF_SkinSSS` 函数，暴露 `SkinToneColor`（VectorParameter）和 `ScatterRadius`（ScalarParameter）两个输入引脚，项目中所有角色材质直接调用此函数，确保全项目皮肤渲染效果一致，且美术人员只需调整暴露参数无需接触底层公式。

**地形层叠混合**：虚幻引擎的地形材质可使用 `LandscapeLayerBlend` 节点，但实际项目中往往需要基于坡度、高度的程序化混合。将坡度计算（利用 `VertexNormalWS` 的 Z 分量）和高度渐变混合封装为 `MF_TerrainBlend`，函数内接收两个 `Texture2D` 输入和一个控制混合锐度的 `Float1` 输入，可被草地、岩石、泥土等不同地形层材质复用，避免每种地形材质各自维护一套混合逻辑。

**程序化 UV 动画**：将基于 `Time` 节点驱动的 UV 滚动、旋转、缩放逻辑封装为 `MF_UVAnimation`，暴露速度（Speed）和旋转中心（Pivot）参数，水面、传送门、能量护盾等材质统一调用，修改动画曲线只需编辑一次函数。

## 常见误区

**误区一：认为材质函数内的参数会自动出现在材质实例面板中**。实际上，材质函数内部的 `ScalarParameter` 和 `VectorParameter` 节点的参数名，不会自动向上传递到宿主材质实例的参数覆盖列表。只有宿主材质图层中直接存在的参数节点才能被材质实例覆盖。若需要在材质实例层面控制材质函数内的某个数值，正确做法是在宿主材质中创建同名参数节点，将其连接到材质函数的 `FunctionInput` 引脚，由此实现参数的"透传"。

**误区二：频繁调用同一材质函数会产生性能叠加**。由于材质函数在编译时内联展开，每次调用都等于完整复制一份节点图的 HLSL 代码，而非跳转到一个共享函数体。因此在同一材质中重复调用 `MF_ComplexNoise` 5 次，其 Shader 指令数等于手写 5 份相同噪声代码的总和。优化策略是在材质内部用局部变量（通过 `Custom` 节点或先计算一次再分支引用）缓存结果，而非依赖"函数调用开销小"的错误假设。

**误区三：将材质函数与材质实例的用途混淆**。材质函数解决的是"逻辑复用"问题——多个材质需要执行相同的计算过程；材质实例解决的是"参数变体"问题——同一套逻辑下不同的数值组合。两者在项目中通常配合使用：先用材质函数封装计算逻辑，再以材质实例暴露参数供美术人员在不打开材质编辑器的情况下调整效果。

## 知识关联

在学习材质函数之前，掌握**材质实例**的参数系统是必要前提。理解材质实例中 `ScalarParameter` 和 `VectorParameter` 如何在父材质与实例之间传递数据，能够帮助准确判断哪些参数应留在宿主材质层、哪些可以封装进材质函数内部作为固定计算的一部分。

掌握材质函数之后，下一个关键主题是**材质库管理**。当项目中材质函数的数量增长到数十甚至数百个后，如何通过命名规范（如 `MF_` 前缀）、目录分类（按功能划分 `/Functions/Blend`、`/Functions/UV`、`/Functions/Noise` 等子目录）以及函数版本管理来保证大型团队的协作效率，成为技术美术工作流的核心议题。材质函数的资产组织方式直接影响材质库是否可被团队成员高效检索和安全复用。