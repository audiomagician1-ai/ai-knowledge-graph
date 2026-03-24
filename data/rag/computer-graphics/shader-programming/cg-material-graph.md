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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 材质图编辑器

## 概述

材质图编辑器（Material Graph Editor）是一种基于节点连线（Node-Based）范式的可视化工具，允许美术师和技术美术在不直接编写GLSL/HLSL代码的前提下，通过拖拽节点、连接引脚来定义物体表面的光照响应方式。每个节点封装一段特定的着色器逻辑，节点之间的连线描述数据流向，整张图最终被编译为一段完整的片元着色器代码。

材质图的概念最早在商业引擎中普及：Unreal Engine 3于2007年随虚幻引擎3发布了其Material Editor，将基于物理的节点图引入工业管线；Unity的Shader Graph则在2018年随HDRP渲染管线正式推出，采用YAML格式序列化图数据。这两套系统共同确立了"节点图→代码生成"的标准工作流，极大地降低了技术门槛，使一个不懂HLSL的美术师也能制作出包含法线贴图、视差遮蔽（Parallax Occlusion Mapping）等复杂效果的材质。

材质图编辑器之所以重要，不仅在于可视化，更在于它实现了**着色器逻辑的模块化复用**：将重复使用的子图打包成材质函数，在多个材质中引用同一套逻辑，修改一处即全局生效——这是手写着色器文件难以做到的。

---

## 核心原理

### 节点类型与数据类型系统

材质图中的节点分为几类：**输入节点**（纹理采样、常量、顶点属性）、**运算节点**（数学运算、向量操作）、**输出节点**（最终材质属性，如BaseColor、Roughness、Normal）。每条连线携带特定数据类型：`float`、`float2`、`float3`、`float4`，引擎会在连线类型不匹配时自动插入转换节点或报错。

Unreal Engine的材质图中，输出节点对应G-Buffer的各个通道：BaseColor绑定到反照率缓冲、Metallic和Roughness绑定到PBR参数缓冲，Emissive直接加法混合到HDR输出缓冲。这意味着美术师在节点图上的每一步操作都有精确对应的GPU寄存器写入目标。

### 图的拓扑排序与代码生成

材质图本质上是一张**有向无环图（DAG）**。代码生成器在编译时首先对图执行拓扑排序（Topological Sort），从输出节点出发反向遍历依赖节点，确保每个节点的输入在其执行前已被计算完毕。以下是最简单的两节点图生成代码的示例逻辑：

```
节点A: Texture2DSample(UV)  → 输出 float3 color_A
节点B: Multiply(color_A, 0.5) → 输出 float3 color_B
输出节点: BaseColor = color_B

生成的HLSL片段:
float3 color_A = tex2D(_MainTex, i.uv).rgb;
float3 color_B = color_A * 0.5;
o.BaseColor = color_B;
```

代码生成器为每个节点生成唯一的临时变量名（通常以节点GUID的前8位命名），避免多路分支中的变量名冲突。Unity Shader Graph在生成代码时还会对未连接的分支进行**死代码消除（Dead Code Elimination）**，以减少最终着色器的指令数。

### 条件分支与动态参数暴露

材质图支持通过**静态开关节点（Static Switch）**实现编译期分支：两条路径在编译时生成不同的着色器变体（Shader Variant），运行时开销为零，但每增加一个开关会使变体数量翻倍。与之不同，**动态参数**通过Uniform变量暴露给CPU端，允许在运行时通过脚本修改，代价是额外的寄存器占用（通常1个float4消耗1个常量缓冲区槽）。

Unreal Engine的材质实例（Material Instance）系统正是基于此：父材质图定义结构，子实例只覆盖暴露的参数值，而不重新编译着色器。Unity Shader Graph中对应的机制是将节点标记为`Exposed Property`，其值会出现在Material Inspector中。

---

## 实际应用

**溶解效果（Dissolve Effect）** 是材质图教学中最具代表性的案例。实现步骤：①采样一张噪声纹理得到`float dissolveNoise`；②用`Step(dissolveNoise, _Threshold)`节点生成0/1遮罩；③通过`Clip`节点丢弃像素；④在边界处额外叠加自发光颜色。整个效果在Unreal Material Editor中只需约8个节点，若手写HLSL需约15行代码，但节点图使参数调整可实时预览。

**地形混合材质** 是另一个典型场景：基于顶点色（VertexColor）的R/G/B通道分别混合草地、泥土、石头三种子材质。材质图中使用`Lerp`节点将三种纹理做两次线性插值，权重来自顶点色通道。这种做法的关键在于材质图天然支持多路输入的可视化比对，美术师可以直接看到混合权重的来源，而无需阅读代码。

**水面折射** 需要在材质图中访问场景深度缓冲和场景颜色缓冲，Unreal通过`SceneDepth`节点和`SceneTexture:SceneColor`节点暴露这两个系统资源，生成的HLSL代码会自动绑定对应的`Texture2D`采样器，美术师无需了解Render Target的绑定细节。

---

## 常见误区

**误区一：认为节点数量越少，着色器性能越好**。实际上，性能瓶颈在于生成的HLSL指令数和纹理采样次数，而非节点数量。一个`CustomExpression`节点可以内嵌10行HLSL，其性能开销远超10个简单运算节点。因此评估材质性能应查看引擎提供的指令数统计（Unreal中的"Shader Complexity"视图，数值超过300即属于高消耗材质），而不是数节点个数。

**误区二：Static Switch与动态参数等效，可随意替换**。Static Switch在编译期确定分支，会生成多个PSO（Pipeline State Object），在移动端每新增一个变体都意味着额外的内存占用和加载时间。Unity文档明确指出，当Shader Keyword总数超过256时会产生关键字溢出错误。应根据是否需要运行时切换来选择Static Switch还是动态Lerp混合。

**误区三：材质图生成的代码与手写代码性能等同**。自动代码生成器为保证通用性会引入冗余的中间变量和类型转换，在某些复杂图中会产生额外的`mov`指令。有经验的技术美术会在材质图中嵌入`Custom Node`（自定义HLSL块），对性能敏感的路径手动优化，同时保留其余部分的节点图可读性。

---

## 知识关联

材质图编辑器直接构建于**片元着色器**的概念之上：节点图的每一条执行路径最终对应片元着色器中对单个像素的计算逻辑，理解`in/out`语义、纹理采样函数`texture2D()`的返回类型，是正确理解节点连线类型系统的前提。若不理解片元着色器中UV坐标是每像素插值得到的，就无法理解材质图中`TexCoord`节点为何能驱动纹理平铺。

向后延伸，**材质函数（Material Function）**是材质图的模块化封装机制：将一组节点打包为可复用的黑盒，定义输入输出引脚，在多张材质图中作为单一节点引用。理解材质图的DAG结构和代码生成逻辑，是进一步学习如何设计高内聚、低耦合的材质函数接口的基础——特别是如何合理划分引脚的数据类型，使函数既足够通用又不引入不必要的类型转换开销。
