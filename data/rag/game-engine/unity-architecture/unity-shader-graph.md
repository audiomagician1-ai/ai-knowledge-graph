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
quality_tier: "B"
quality_score: 49.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
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

Shader Graph 是 Unity 于 2018 年随 Scriptable Render Pipeline（SRP）一同推出的可视化着色器编辑工具，允许开发者通过连接节点（Node）来构建 GPU 着色逻辑，而无需手写 HLSL 或 Cg 代码。它以 `.shadergraph` 格式保存文件，底层会自动将节点网络编译为符合 URP 或 HDRP 规范的 Shader 代码。

Shader Graph 的设计目标是降低着色器开发门槛——在此之前，Unity 开发者要么使用 Surface Shader（只支持 Built-in 管线），要么从零编写顶点/片元着色器。Shader Graph 的节点编辑器继承了 Unreal Engine 的 Material Editor 理念，但深度集成于 Unity 的 SRP 架构，支持 URP 和 HDRP 两套管线，无法在 Built-in Render Pipeline 中使用。

对于使用 URP 的项目，Shader Graph 是构建自定义材质效果的主要途径。它支持实时预览（Main Preview 窗口），节点更改后可在编辑器中即时看到渲染结果，配合 Blackboard 面板管理 Shader 属性（Properties），大幅提升了迭代效率。

## 核心原理

### 节点系统与数据流

Shader Graph 的工作逻辑是有向无环图（DAG）：数据从输入节点（Input Nodes）流向输出节点（Master Stack）。每条连线（Edge）传递特定数据类型，包括 `Float`、`Vector2`、`Vector3`、`Vector4`、`Color`、`Texture2D`、`Boolean` 等。节点的输出端口（Output Port）连接到另一个节点的输入端口（Input Port），不允许形成循环。

每个节点代表一个 GPU 运算操作，例如 `Sample Texture 2D` 节点对纹理进行采样，`Multiply` 节点执行逐分量乘法，`Lerp` 节点执行线性插值：`result = A × (1 - T) + B × T`。开发者通过组合这些节点描述像素颜色、透明度、法线等最终属性。

### Master Stack（主堆栈）

Shader Graph 2020.2 版本引入了 Master Stack 取代旧版的 Master Node。Master Stack 分为两个 Stage：
- **Vertex Stage**：控制顶点位置（Position）、法线（Normal）、切线（Tangent）
- **Fragment Stage**：控制基础颜色（Base Color）、金属度（Metallic）、平滑度（Smoothness）、自发光（Emission）等

在 URP 中，Shader Graph 默认提供 **Lit** 和 **Unlit** 两种 Graph 类型。Lit Graph 的 Fragment Stage 使用 PBR 光照模型，Unlit Graph 则只输出最终颜色，不参与光照计算，适合 UI 特效或风格化渲染。

### Blackboard 与 Graph Inspector

Blackboard 面板用于定义 Shader 的对外属性（Property），这些属性会暴露到 Material Inspector 面板，供美术在材质实例中调节数值。属性类型包括 `Float`、`Color`、`Texture2D`、`Vector` 等。每个属性都有一个 **Reference Name**（如 `_BaseColor`），材质球通过这个名称在 CPU 侧传递数据给 GPU。

Graph Inspector 则控制整个 Shader 的全局设置，包括精度（Precision，可选 `Half` 或 `Single`）、渲染面（Render Face，Front/Back/Both）以及 Alpha Clipping 的阈值。将 Precision 设为 Half 可以在移动端节省 GPU 寄存器，但对高动态范围颜色计算可能引入精度误差。

### 子图（Sub Graph）

Sub Graph 以 `.shadersubgraph` 格式保存，封装可复用的节点逻辑，类似于编程中的函数。Sub Graph 可以定义自己的输入输出端口，并在多个 Shader Graph 中引用。例如可以把"雪覆盖效果"封装为一个 Sub Graph，在角色、地形、道具的 Shader Graph 中统一调用，修改 Sub Graph 后所有引用它的着色器自动更新。

## 实际应用

**溶解效果（Dissolve Effect）**：使用 `Sample Texture 2D` 采样噪声贴图，将其输出值与一个 `Float` 属性（控制溶解进度）相减，结果传入 `Alpha Clip Threshold`。当进度属性从 0 动画到 1，物体表面像素依次被裁剪，形成溶解动画。整个效果只需约 6 个节点即可实现。

**UV 流动水面**：将 `Time` 节点的输出乘以速度系数，加到 `UV` 节点的输出上，再传入 `Sample Texture 2D` 的 UV 输入端口。水面法线贴图随时间偏移，结合两层不同速度的法线叠加（使用 `Normal Blend` 节点），可实现真实的水流扰动效果。

**角色描边（Outline）**：在 Vertex Stage 中，将顶点位置沿法线方向偏移一个固定距离（如 0.02 单位），结合反面渲染（Render Face 设为 Back）实现描边层，配合主 Pass 共同构成卡通渲染风格描边，无需额外 C# 脚本控制。

## 常见误区

**误区一：Shader Graph 可以用于 Built-in 渲染管线**
Shader Graph 依赖 SRP 的 Shader 后端，生成的 Shader 代码包含 URP 或 HDRP 的专用宏（如 `SHADERGRAPH_PREVIEW`、`UNITY_MATRIX_VP` 的 SRP 版本）。将 `.shadergraph` 文件拖入 Built-in 项目会显示品红色错误材质，无法正常工作。如需在 Built-in 管线中使用可视化工具，需借助第三方插件如 Amplify Shader Editor。

**误区二：节点越少性能越好，与代码量无关**
Shader Graph 的每个节点都会编译为若干条 GPU 指令。一个 `Sample Texture 2D` 节点展开后在 Fragment Stage 会产生多条纹理采样指令，而纹理采样是 GPU 的高开销操作。节点数量本身不直接等于性能代价，采样类节点、循环结构（通过 Custom Function 引入）和高精度数学运算才是主要性能瓶颈。应使用 Frame Debugger 或 RenderDoc 分析实际 Overdraw 和 Shader 指令数。

**误区三：Shader Graph 生成的代码无法优化**
通过右键 `.shadergraph` 文件选择 "Copy Shader"，可以获取完整的编译后 HLSL 代码。开发者可以将其复制为独立 `.shader` 文件后手动修改，删除冗余分支或合并 Pass，适用于性能敏感的平台（如主机或移动端）的最终优化阶段。

## 知识关联

学习 Shader Graph 需要先理解 **URP 渲染管线**的核心架构，特别是 URP 的 Renderer Feature 机制和 Pass 执行顺序——只有明白 URP 中 Lit Shader 如何参与前向渲染（Forward Rendering）的多 Pass 流程，才能正确设置 Shader Graph 的混合模式（Blend Mode）和深度写入（Depth Write）选项，避免透明物体排序错误等问题。

Shader Graph 输出的材质直接作用于 Renderer 组件，与 **Material Property Block**（C# API）结合可实现 GPU 实例化（GPU Instancing）下的每实例属性差异化。进一步学习着色器编程可以从 Shader Graph 的 Custom Function 节点入手，该节点允许内嵌 HLSL 代码片段，是从可视化工具过渡到手写着色器的桥梁。