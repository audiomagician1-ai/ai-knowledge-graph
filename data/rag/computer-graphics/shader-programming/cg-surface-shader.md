---
id: "cg-surface-shader"
concept: "表面着色器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 2
is_milestone: false
tags: ["引擎"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 表面着色器

## 概述

表面着色器（Surface Shader）是Unity引擎于2010年前后引入的一种着色器抽象层，其核心思想是让开发者只需描述"物体表面的材质属性"，而无需手动编写完整的光照计算代码。Unity的ShaderLab编译器会在后台自动将Surface Shader代码展开（expand）为若干个完整的顶点/片元着色器Pass，每个Pass对应不同的渲染路径（如Forward Rendering和Deferred Rendering）。

历史上，在Unity引入Surface Shader之前，开发者必须为每种光照模型（Lambert、Blinn-Phong等）单独编写多个Pass，并手动处理不同平台的光照差异。Surface Shader通过`#pragma surface`指令和内置宏，将这一重复劳动压缩到了一个函数中。时至今日，Surface Shader仍是Unity中处理标准PBR（基于物理的渲染）材质的快捷方式，尤其适合初级到中级难度的材质开发场景。

Surface Shader的重要性在于它降低了着色器编程的入门门槛。由于Unity内置了`Standard`、`Lambert`、`BlinnPhong`等光照模型，开发者只需填充一个名为`SurfaceOutput`或`SurfaceOutputStandard`的结构体，即可获得与内置着色器一致的光照效果，减少了数百行重复的光照遍历代码。

## 核心原理

### `#pragma surface` 指令与代码展开机制

Surface Shader的入口是`#pragma surface surf Standard fullforwardshadows`这行指令，其中`surf`是开发者定义的表面函数名，`Standard`指定使用Unity内置的PBS光照模型，`fullforwardshadows`启用完整阴影支持。Unity编译时会读取这行指令，自动生成顶点着色器、多个前向渲染Pass（Base Pass和Additional Pass）以及阴影投射Pass，开发者在Inspector中可点击"Show generated code"查看展开后的完整HLSL代码，通常展开后代码量可达原始代码的5～10倍。

### SurfaceOutputStandard 结构体

开发者在`surf`函数中填写的核心数据结构是`SurfaceOutputStandard`，其主要字段如下：

| 字段 | 类型 | 说明 |
|------|------|------|
| `Albedo` | `fixed3` | 基础颜色（漫反射率） |
| `Normal` | `fixed3` | 切线空间法线 |
| `Metallic` | `fixed` | 金属度，范围0～1 |
| `Smoothness` | `fixed` | 光滑度，范围0～1 |
| `Emission` | `half3` | 自发光颜色 |
| `Alpha` | `fixed` | 透明度 |

只要填满这个结构体，Unity即可在Standard PBS光照模型下计算出基于Cook-Torrance BRDF的完整光照结果，开发者无需自行实现BRDF方程。

### 自动生成多Pass的渲染路径适配

Surface Shader最关键的自动化能力是同时生成前向渲染和延迟渲染的Pass。当项目切换到Deferred Rendering时，Unity会使用同一份`surf`函数，但生成的Pass改为将`Albedo`、`Normal`、`Metallic`等数据写入G-Buffer（通常为4张RT），而不是直接输出光照颜色。这一自动适配节省了开发者为两种渲染路径分别维护代码的工作量，同时也意味着开发者对底层Pass细节的控制权有所减少。

### 输入结构体 Input 的作用

Surface Shader要求开发者定义一个名字固定为`Input`的结构体，用于向`surf`函数传递插值数据。常用字段如`float2 uv_MainTex`（自动关联名为`_MainTex`的贴图的UV），以及`float3 worldPos`（世界坐标）、`float3 worldNormal`（世界法线）等。字段名必须与Unity规定的语义名称完全一致，否则编译器无法正确注入数据。例如，写成`float2 texcoord`不会自动绑定UV，而`float2 uv_MainTex`才会触发自动UV注入。

## 实际应用

**雪地覆盖效果**：利用`worldNormal.y`判断朝上的面，在`surf`函数中混合雪白色到`Albedo`，并降低`Metallic`、提升`Smoothness`，整个逻辑只需约15行代码，无需手写光照循环。

**视差贴图（Parallax Mapping）**：在`Input`中加入`float3 viewDir`后，可在`surf`函数中调用Unity内置的`ParallaxOffset`函数偏移UV，从而模拟凹凸深度效果。`ParallaxOffset`的签名为`float2 ParallaxOffset(half h, half height, half3 viewDir)`，其中`h`为高度图采样值，`height`为效果强度系数。

**溶解效果**：采样一张噪声贴图，将采样值与Dissolve阈值比较，在`surf`函数中通过`clip(noiseValue - _Threshold)`丢弃片元，并在边缘处叠加`Emission`发光颜色，整个效果在Surface Shader框架内约20行即可实现，而底层的多Pass阴影剔除由Unity自动处理。

## 常见误区

**误区一：认为Surface Shader比Vertex/Fragment Shader性能更高**
这是错误的。Surface Shader展开后实际上就是Vertex/Fragment Shader，且由于自动生成代码通常包含大量条件分支和通用计算，性能往往低于手写的精简Vertex/Fragment Shader。在移动端对Draw Call和填充率敏感的场景中，Surface Shader生成的冗余指令可能导致不必要的性能开销。

**误区二：修改`SurfaceOutput`结构体字段名**
部分初学者会尝试重命名`Albedo`为`Color`等自定义名称，但Unity的光照模型函数（如`LightingStandard`）通过固定字段名访问结构体数据，修改字段名会导致光照计算读取到默认零值，产生全黑或错误的渲染结果，而编译器并不会报错提示。

**误区三：期望在Surface Shader中完全控制渲染顺序**
Surface Shader的Pass由Unity自动决定，开发者无法直接插入自定义Pass或改变Pass的执行顺序。若需要轮廓线、多层混合等需要精细Pass控制的效果，必须退出Surface Shader框架，改用完整的Vertex/Fragment Shader结合`SubShader`的多Pass手动编写。

## 知识关联

**前置概念：片元着色器**
理解片元着色器的输入输出模型（如`SV_Target`输出最终颜色、插值器传递顶点数据）是读懂Surface Shader展开代码的基础。Surface Shader的`surf`函数本质上是片元着色器中材质属性计算阶段的封装，展开后的代码正是标准的片元着色器结构，只是光照循环部分被Unity的宏替换。

**与Unity Shader Graph的关系**
Unity 2018年引入的Shader Graph是Surface Shader的可视化替代方案，两者都基于"填充材质属性节点"的抽象思路，但Shader Graph支持HDRP（高清渲染管线）且提供实时预览。Surface Shader仅适用于内置渲染管线（Built-in Render Pipeline），在URP和HDRP项目中已被官方标记为不推荐使用，开发者应根据渲染管线版本选择合适的着色器工作流。