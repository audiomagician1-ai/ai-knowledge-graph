---
id: "unity-shader-graph"
concept: "Shader Graph"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 2
is_milestone: false
tags: ["渲染"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Shader Graph

## 概述

Shader Graph 是 Unity 于 2018 年随通用渲染管线（URP）一同推出的可视化着色器编辑工具，允许开发者通过连接节点的方式创建着色器，无需手写 HLSL 代码。它以节点图（Node Graph）为基本编辑范式，每个节点封装一种数学运算或采样操作，开发者通过拖拽连线将节点输出端口（Output Port）与其他节点的输入端口（Input Port）相连，最终将数据流导入主节点（Master Stack），生成可被 GPU 执行的着色器程序。

Shader Graph 的前身是 Unity 商店中的第三方插件 Shader Forge（2013年），Unity 官方在观察到社区对可视化着色器编辑的强烈需求后，将类似的功能内置为第一方工具。自 Unity 2021 LTS 起，Shader Graph 同时支持 URP 和 HDRP 两条渲染管线，但不兼容旧版的内置渲染管线（Built-in Render Pipeline）。这一限制意味着项目必须先完成渲染管线迁移，才能使用 Shader Graph 资产。

Shader Graph 的核心价值在于将着色器逻辑可视化，让美术人员在不了解 GPU 编程的情况下，也能独立迭代材质效果。生成的 `.shadergraph` 文件本质上是一个 JSON 序列化的图数据结构，Unity 在构建时会将其编译为对应渲染管线的 HLSL 代码，因此运行时性能与手写着色器相当，不存在额外的解释层开销。

---

## 核心原理

### 节点类型与数据类型系统

Shader Graph 中每个节点的端口携带明确的数据类型，包括 `Float`（标量）、`Vector2`、`Vector3`、`Vector4`、`Color`、`Texture2D`、`Boolean` 等。连线时类型必须兼容，系统会对部分不匹配类型进行自动扩展（如 `Float` 连接 `Vector3` 时会填充为 `(x, x, x)`），但 `Texture2D` 端口只能接受纹理采样节点，不允许跨类别强制连接。

节点库中包含超过 200 个内置节点，分为 Input（输入）、Math（数学）、Channel（通道）、UV、Geometry（几何）、Procedural（程序化）等类别。例如 **Voronoi** 节点可直接生成程序化细胞纹理，**Normal From Height** 节点可从灰度高度图反推法线，这些封装减少了手写复杂 HLSL 的需要。

### 主节点（Master Stack）与渲染目标

图的终点是 **Master Stack**，分为 Vertex 和 Fragment 两个模块。Fragment 模块包含 Base Color、Metallic、Smoothness、Emission、Alpha 等表面属性输入；Vertex 模块允许对顶点位置（Position）和法线（Normal）进行程序化偏移，从而实现顶点动画（如布料飘动、水面波浪）。Master Stack 在 URP 下对应 **Lit** 或 **Unlit** 两种目标着色器，选择不同目标会改变可用的输入属性集合。

### 子图（Sub Graph）与图的复用

Shader Graph 支持将一段节点网络封装为 **Sub Graph**（扩展名 `.shadersubgraph`），使其像单一节点一样被其他图引用。Sub Graph 可自定义输入/输出端口名称和类型，形成可复用的函数模块。例如将"Triplanar 映射"逻辑封装为子图后，多个材质图均可调用，修改子图时所有引用者会自动同步更新。子图内部不能包含 Master Stack，不可单独编译为完整着色器。

### 预览与实时编译

Shader Graph 编辑器中每个节点右下角都有一个实时预览球，显示该节点当前输出值的可视化结果。编辑器会在节点连接发生变化时触发增量编译，将修改的子图片段重新转译为 HLSL，整个图无需全量重编。这一实时反馈循环的延迟通常在 0.5 到 2 秒之间，具体取决于节点数量和目标平台。

---

## 实际应用

**溶解效果（Dissolve Effect）**：在 Fragment 模块中，将噪声纹理的灰度值与一个可动画化的阈值属性（Property）输入 **Step** 节点，其输出连接 Alpha 端口，并在 Master Stack 中启用 Alpha Clipping。随阈值从 0 增大到 1，网格从完整逐渐"溶解"消失。整个逻辑仅需约 6 个节点，不需要任何 HLSL 代码。

**角色描边（Rim Light）**：使用 **View Direction** 节点与 **Normal Vector** 节点做点积（**Dot Product** 节点），将结果通过 **One Minus** 节点取反，再经 **Power** 节点控制边缘宽度，最后叠加到 Emission 端口，形成菲涅尔感的视角相关发光描边。

**UV 动画（Scrolling Texture）**：将 **Time** 节点输出乘以一个 Vector2 速度属性，加到 UV 坐标上，再送入 **Sample Texture 2D** 节点，实现流动的水面或传送门漩涡效果。此方案在 Vertex 和 Fragment 阶段均可实现，Fragment 阶段精度更高但性能开销略大。

---

## 常见误区

**误区一：Shader Graph 生成的着色器性能低于手写代码**
这是错误的。Shader Graph 在编辑时生成完整 HLSL 源码，构建时由 Unity 着色器编译器统一编译为 GPU 字节码，与手写着色器走完全相同的编译流程。性能差异来自节点逻辑本身是否高效，而非 Shader Graph 工具本身引入额外开销。

**误区二：Shader Graph 可以在内置渲染管线（Built-in RP）项目中使用**
Shader Graph 资产明确绑定 URP 或 HDRP 渲染管线。将 `.shadergraph` 文件拖入使用内置渲染管线的项目，材质将显示为洋红色错误材质（Magenta）。迁移管线不仅是 Shader Graph 使用前提，还会影响光照模型、批处理策略等整体渲染行为。

**误区三：Custom Function 节点可以绕过 Shader Graph 的所有限制**
**Custom Function** 节点确实允许内嵌 HLSL 代码，但它仍受 Shader Graph 的类型系统和编译上下文约束，无法访问 Shader Graph 不支持的着色器阶段（如 Geometry Shader），也无法直接写入深度缓冲区（Depth Buffer）。复杂的多 Pass 着色器依然必须手写 `.shader` 文件才能实现。

---

## 知识关联

Shader Graph 直接依赖 **URP 渲染管线**的存在——URP 定义了光照模型（如 Simple Lit、Complex Lit）和渲染 Pass 结构，Shader Graph 的 Master Stack 中的属性（Metallic、Smoothness 等）正是对 URP PBR 光照方程中参数的图形化映射。没有 URP，Shader Graph 的 Lit 目标无法完成光照计算。

理解 Shader Graph 中 Vertex 模块的位移原理，需要具备基础的 3D 坐标空间知识（对象空间、世界空间、裁剪空间之间的变换），因为 **Position** 和 **Normal Vector** 节点均有 Space 属性选项，选错坐标空间会导致效果在摄像机移动时产生漂移。这部分知识属于渲染数学基础，与 Shader Graph 工具本身独立，但在实际使用中频繁交叉。