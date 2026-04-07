---
id: "ta-unity-shadergraph"
concept: "Unity Shader Graph"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 2
is_milestone: false
tags: ["工具"]

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


# Unity Shader Graph

## 概述

Unity Shader Graph 是 Unity 引擎自 2018.1 版本起正式引入的可视化着色器编辑工具，它允许技术美术在不直接编写 HLSL 代码的前提下，通过连接节点（Node）的方式构建着色器逻辑。Shader Graph 生成的底层代码基于 Unity 的 Scriptable Render Pipeline（SRP），因此它只能在 Universal Render Pipeline（URP）或 High Definition Render Pipeline（HDRP）中运行，无法在旧版 Built-in 渲染管线下工作。

Shader Graph 的历史起源可以追溯到早期图形工具 Shader Forge（第三方插件）和 Amplify Shader Editor，Unity 官方在收集社区需求后于 2018 年将类似功能纳入引擎本体。2021 年，Unity 进一步在 Shader Graph 11.x（对应 Unity 2021 LTS）中稳定了 Custom Function Node 功能，使 Shader Graph 同时具备可视化与代码混合编写的能力。

对于技术美术而言，Shader Graph 的核心价值在于将 GPU 渲染管线中的顶点处理阶段和片段处理阶段可视化呈现：开发者可以直接看到数据从 Vertex Stage 流向 Fragment Stage 的路径，而不必在脑中抽象映射寄存器与插值器的工作方式。

---

## 核心原理

### 节点系统与数据流

Shader Graph 的编辑界面以有向无环图（DAG）为基础。每个 Node 代表一个数学操作或 GPU 采样操作，节点的输入端口（Input Port）和输出端口（Output Port）通过连线（Edge）传递数据。数据类型包括 Float（1分量）、Vector2、Vector3、Vector4 以及 Texture2D、SamplerState 等，端口之间存在隐式类型提升规则：将一个 Float 连接到 Vector4 的输入端口时，Shader Graph 会自动将其广播到四个分量，等价于 HLSL 中的 `float4(x, x, x, x)`。

最终所有逻辑汇聚到 Master Stack（主栈），它包含 Vertex Block 和 Fragment Block 两个输出区域。以 URP Lit Shader 为例，Fragment Block 中的 Base Color、Metallic、Smoothness、Normal（Tangent Space）等端口直接对应 PBR 光照模型的物理参数输入，连接错误的数据范围（如将 HDR 颜色直接连入 Smoothness）会导致明显的渲染错误，但 Shader Graph 不会在编译时报错。

### SubGraph（子图）

SubGraph 是 Shader Graph 的模块化机制，文件扩展名为 `.shadersubgraph`。它允许将一组重复使用的节点封装为单个自定义节点，供多个 Shader Graph 文件引用。SubGraph 内部可以定义 Property（属性）作为输入端口，也可以定义多个输出端口。

SubGraph 的典型用途是封装 Triplanar Mapping 逻辑、程序化噪声（如 Gradient Noise 与 Voronoi 的混合）、或自定义的 Normal Blend 算法。需要注意的是，SubGraph 不能在其内部引用另一个 SubGraph 的循环路径，即严格禁止循环依赖，否则 Unity 编辑器会报 `Cycle detected` 错误并拒绝编译。

### Custom Function Node（自定义函数节点）

当节点系统无法直接表达某些底层 GPU 操作时，Custom Function Node 允许开发者内嵌原生 HLSL 代码。它支持两种模式：

- **String 模式**：直接在 Inspector 的文本框中输入 HLSL 函数体，函数名须与 Custom Function Node 的 Name 字段完全一致，例如将 Name 设为 `ParallaxOcclusionMapping`，则 HLSL 中需声明 `void ParallaxOcclusionMapping_float(...)`。
- **File 模式**：引用外部 `.hlsl` 文件，Shader Graph 在编译时通过 `#include` 将其注入，适合函数较复杂或需要与程序员共享代码的场景。

Custom Function Node 的输入输出端口须手动在 Inspector 中声明，类型对应关系为：Shader Graph 的 `Vector1` 对应 HLSL 的 `float`，`Vector4` 对应 `float4`，`Texture2D` 配合 `SamplerState` 分别对应 `UnityTexture2D` 与 `UnitySamplerState`（URP 的封装结构体）。

---

## 实际应用

**溶解效果（Dissolve Effect）**：这是 Shader Graph 最常见的入门案例。将一张噪声贴图的 R 通道采样值减去一个可动画化的 `_DissolveAmount`（范围 0~1 的 Float Property），结果输入 Step 节点（边缘值设为 0），输出连接到 Fragment Block 的 Alpha 端口，同时开启材质的 Alpha Clipping。再用 Smoothstep 节点在阈值边缘附近叠加一个 Emission Color，即可实现带发光边缘的溶解。整个效果不需要写一行 HLSL，完全通过节点连接实现。

**顶点动画（Vertex Animation）**：在 Vertex Block 的 Position 端口上叠加基于 `_Time.y`（Shader Graph 中对应 Time 节点的 Time 输出）驱动的 Sine 函数，可以实现旗帜飘动或水面起伏。顶点世界坐标通过 Position 节点（Space 设为 World）获取，计算完成后需要将结果从 World Space 转换回 Object Space 再输入 Master Stack，否则顶点偏移会忽略物体的 Transform。

**与 VFX Graph 集成**：在 Unity 2022 及以上版本，Shader Graph 创建的 Shader 可以直接指定为 VFX Graph 的 Output 使用，实现粒子系统的高度自定义外观，这是 Built-in 管线下无法原生实现的工作流。

---

## 常见误区

**误区一：认为 Shader Graph 与 Built-in 渲染管线兼容**  
许多初学者在新建 Unity 项目后直接创建 Shader Graph，却发现材质显示为品红色（Missing Shader），原因是项目默认的 Built-in 渲染管线不支持 Shader Graph。必须在 Project Settings → Graphics 中将 Scriptable Render Pipeline Asset 指向一个 URP 或 HDRP 资产后，Shader Graph 才能正常编译。

**误区二：把 SubGraph 的 Property 与 Shader Graph 本体的 Property 混淆**  
SubGraph 内部定义的 Property 属于 SubGraph 的输入端口，不会暴露在材质的 Inspector 面板上。只有 Shader Graph 本体（`.shadergraph` 文件）的 Blackboard 中定义的 Property，才会出现在材质 Inspector 并允许在运行时通过 `Material.SetFloat()` 等接口进行动态修改。

**误区三：认为 Shader Graph 生成的 HLSL 性能一定低于手写 Shader**  
Shader Graph 编译后生成的 HLSL 代码质量在简单逻辑下与手写基本一致，但在节点层级较多或存在大量分支（Branch 节点内部使用 `lerp` 而非真正的 GPU `if` 语句）时，会产生多余的指令。通过菜单 View → Shader Inspector 可以查看 Shader Graph 当前生成的 HLSL 原始代码，用以判断是否需要改用 Custom Function Node 进行优化。

---

## 知识关联

学习 Shader Graph 需要对 **GPU 渲染管线**中的顶点着色器阶段与片段着色器阶段有基本认知，因为 Shader Graph 的 Master Stack 直接镜像了这两个阶段的输入输出关系——不理解光栅化插值的工作方式，就难以判断应该在 Vertex Block 还是 Fragment Block 中执行某个计算（在 Vertex Block 计算可以减少 Fragment 调用次数，但精度受顶点密度限制）。

Shader Graph 生成的着色器可以作为 **VFX Graph** 粒子系统的外观基础，也可以配合 **Shader Variant** 与 Keywords 系统实现运行时的功能分支切换（通过 Blackboard 中的 Boolean Keyword 节点定义 `shader_feature` 或 `multi_compile`）。掌握 Shader Graph 的节点逻辑后，若需要进一步提升性能或实现更复杂的算法（如屏幕空间反射或自定义光照模型），则需要过渡到直接编写 HLSL 代码，此时 Shader Graph 的"查看生成代码"功能可以作为学习手写 Shader 的重要参考桥梁。