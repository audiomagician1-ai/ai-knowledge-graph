---
id: "cg-material-graph"
concept: "材质图编辑器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 材质图编辑器

## 概述

材质图编辑器（Material Graph Editor）是一种以节点图（Node Graph）为核心交互范式的可视化着色器创作工具，允许美术师和技术美术师通过连接功能节点而非手写GLSL/HLSL代码来定义物体表面的光照响应行为。每个节点封装一段具体的着色器逻辑——例如纹理采样、向量混合或数学运算——节点之间的连线则表示数据流向，最终系统将整个节点网络编译为可在GPU上执行的着色器程序。

该工具的概念最早可追溯至Alias/Wavefront于1998年在Maya中推出的Hypershade编辑器，此后Unreal Engine 3（2006年）将其引入实时渲染领域，使材质图编辑器成为现代游戏引擎的标配功能。Unity的Shader Graph于2018年随Unity 2018.1正式发布，进一步普及了这一工作流。

材质图编辑器的核心价值在于将着色器开发的迭代周期从"修改代码→编译→查看结果"缩短为"拖拽连线→实时预览"，同时为非程序员提供了可访问的创作入口，且不牺牲底层着色器的表达能力。

## 核心原理

### 节点类型与数据类型系统

材质图中每个节点拥有若干输入端口（Input Pins）和输出端口（Output Pins），端口上附有强类型标注，常见数据类型包括：`Float`（标量）、`Vector2/3/4`（向量）、`Texture2D`（纹理对象）和`Sampler State`（采样器状态）。连线只允许在兼容类型的端口之间建立——例如，`Float`可以自动提升（Promotion）为`Vector4`（分量复制），但`Texture2D`对象本身不能直接连接到颜色输入端口，必须先经过**Texture Sample**节点转换为颜色向量。

Unreal Engine的材质编辑器定义了约200种内置节点，其中包含`Lerp`（线性插值）、`Fresnel`（菲涅耳效应）、`WorldAlignedTexture`（世界空间对齐采样）等专用节点，分别对应具体的HLSL函数或代码片段。

### 图到代码的编译机制

节点图本质上是一张有向无环图（DAG，Directed Acyclic Graph），其编译过程分为三个阶段：

1. **拓扑排序**：从最终输出节点（通常是PBR材质的主节点，如Unreal的`M_Result`或Unity的`PBR Master Stack`）出发，沿输入边反向遍历，通过深度优先搜索得到节点执行顺序。
2. **代码片段展开**：按拓扑顺序为每个节点生成对应的HLSL/GLSL代码片段，中间变量以`Local_NodeID_OutputSlot`格式命名，例如`Local_42_RGB`。
3. **死代码消除**：未被任何下游节点引用的节点分支在编译阶段被裁剪，不会进入最终着色器，类似于编译器的Dead Code Elimination优化。

以`Lerp`节点为例，其代码展开结果为：
```hlsl
float3 Local_7_Result = lerp(Local_3_RGB, Local_5_RGB, Local_6_Alpha);
```
其中`lerp(A, B, T) = A + T*(B - A)`，T被限定在[0, 1]区间内。

### 主节点与PBR参数绑定

材质图的最终节点通常是一个**主材质节点**（Master Material Node），其输入插槽直接对应PBR光照模型中的物理量：`Base Color`（基础反射率，sRGB空间的漫反射颜色）、`Metallic`（金属度，0=非金属/1=金属）、`Roughness`（粗糙度，控制GGX高光波瓣宽度）、`Normal`（切线空间法线）、`Emissive Color`（自发光，不参与光照计算）等。每个插槽在内部对应片元着色器中传递给光照方程的具体变量，例如`Roughness`在Unreal的光照模型中最终影响GGX分布函数`D(h) = α²/(π((n·h)²(α²-1)+1)²)`中的粗糙度参数α。

## 实际应用

**流体表面材质**：在Unity Shader Graph中制作水面效果时，典型节点链路为：两张以不同速度在UV空间平移的法线贴图（通过`Tiling And Offset`节点控制）输入`Normal Blend`节点进行混合，输出结果连接至主节点`Normal`插槽；再通过`Fresnel Effect`节点（参数：Normal、View Dir、Power，默认Power=5.0）驱动`Lerp`在深水颜色与浅水颜色之间插值，连接至`Base Color`插槽。整个效果无需手写一行GLSL代码。

**材质实例化工作流**：在Unreal Engine中，可将材质图中的常量节点替换为`Parameter`节点（如`ScalarParameter`、`VectorParameter`），这些参数在运行时可通过材质实例（Material Instance）覆写，而无需重新编译着色器。一个典型配置是将`Roughness`定义为名为`"Surface_Roughness"`的`ScalarParameter`，默认值0.5，美术师可在场景中对不同物体的实例设置0.1（光滑金属）到0.9（粗糙石材）的不同值，底层共享同一份着色器字节码。

**自定义HLSL嵌入**：当内置节点无法满足需求时，Unreal的`Custom`节点允许直接嵌入HLSL代码字符串，输入端口对应代码中的形参名称。这是材质图编辑器与手写着色器的混合使用模式，适用于实现如Ray Marching或SDF（有向距离场）求交等复杂算法。

## 常见误区

**误区一：认为节点数量越少，运行时性能越好**
节点数量与最终着色器的指令数（Instruction Count）之间并非线性关系。多个简单节点可能被编译器合并为单条GPU指令，而某些单一节点（如`Texture Sample`）本身就会产生大量内存访问开销。Unreal提供了**Shader Complexity**视口模式（以绿→红热图显示像素着色器成本），正确的性能分析应依赖该工具而非目测节点数量。

**误区二：材质图生成的代码与手写代码性能等价**
自动生成的代码会引入冗余的中间变量和潜在的寄存器压力，部分情况下手写着色器确实可以通过人工优化指令顺序来减少ALU周期。但更重要的性能差异来自于**分支节点**（`If`/`Switch`）的使用：GPU的SIMD架构使材质图中的条件分支产生Warp Divergence，导致所有分支路径均被执行，而手写代码有时可以通过`lerp`替换`if`来规避此问题。

**误区三：法线节点输出的是世界空间法线**
材质图中的`Normal Map`节点默认输出**切线空间**（Tangent Space）法线，数值范围为[-1, 1]，需由引擎在顶点着色阶段利用TBN矩阵（Tangent-Bitangent-Normal矩阵）变换至世界空间后，才能参与光照计算。若将两张法线贴图直接用`Add`节点相加（而非使用`Normal Blend`/`Reoriented Normal Mapping`算法），会因为忽略切线空间的几何含义而产生错误的混合结果。

## 知识关联

材质图编辑器是片元着色器概念的可视化封装层——学习者必须先理解片元着色器中的`uniform`变量、纹理采样函数`texture2D(sampler, uv)`及输出变量`gl_FragColor`的含义，才能正确理解材质图中各节点插槽对应的数据含义，以及为何`Texture2D`节点需要配合`Sampler State`才能产生颜色输出。

在掌握材质图编辑器之后，下一个学习目标是**材质函数**（Material Function）：这是将一组节点封装为可复用模块的机制，类似于着色器代码中的函数抽象。材质函数可以接受输入参数并返回计算结果，在多个材质图之间共享，是大型项目中管理着色器复杂度的核心工程化手段——例如将通用的"雨水湿润效果"逻辑封装为`MF_WetSurface`函数节点，供场景中所有受雨水影响的材质调用。