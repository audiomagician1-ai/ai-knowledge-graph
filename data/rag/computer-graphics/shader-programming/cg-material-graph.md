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

材质图编辑器（Material Graph Editor）是一种基于节点连接（Node-based）的可视化工具，允许美术师和技术美术在不直接编写GLSL/HLSL代码的情况下构建片元着色器逻辑。用户通过将代表不同运算的节点（如纹理采样、向量运算、数学函数）拖放到画布上，并用"连线"描述数据流向，系统后台自动将节点图翻译为可在GPU执行的着色器代码。

材质图编辑器的思想最早在2004年左右随Unreal Engine 3的材质编辑器商业化普及，随后Unity的ShaderGraph（2018年正式发布）、Blender的Shader Nodes以及Godot的VisualShader系统相继推出。在此之前，编写一个支持法线贴图、镜面反射和环境光遮蔽的PBR材质需要数百行GLSL代码；有了材质图编辑器，同等逻辑可以在数十分钟内通过拖拉节点完成。

材质图编辑器的价值不仅在于降低门槛，还在于它将着色器逻辑**具象化为有向无环图（DAG）**，使代码重用、参数曝光和跨平台编译成为系统级特性，而非手工维护的工程任务。

---

## 核心原理

### 节点类型与引脚系统

材质图中的每个节点对应着色器中的一段操作。节点分为三大类：
- **输入节点**：提供原始数据，例如`Texture2D Sample`节点读取一张贴图并输出`float4`颜色，`Time`节点输出`float`类型的全局时间值。
- **运算节点**：对数据进行变换，例如`Multiply`节点执行逐分量乘法，`Lerp`节点执行线性插值 `A*(1-t) + B*t`，其中A、B、t均为可连接的引脚。
- **输出节点**：代表最终材质属性，Unreal Engine的主材质节点（Master Material Node）拥有`Base Color`、`Metallic`、`Roughness`、`Normal`等固定输入引脚，每个引脚对应PBR光照模型中的一个参数。

引脚有严格的数据类型：`float`、`float2`、`float3`、`float4`，不同类型直接连接会触发编辑器的隐式类型提升或报错。例如将`float`连接到`float3`引脚时，Unity ShaderGraph会自动将标量扩展为`(v, v, v)`形式。

### 从节点图到HLSL的代码生成流程

编辑器在保存或编译时执行**图遍历（Graph Traversal）**，从输出节点出发，以深度优先的顺序递归访问所有上游节点，并为每个节点生成一段HLSL代码片段。以下是一个简化示意：

```
// Texture Sample 节点生成：
float4 node_texSample = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, i.uv);

// Multiply 节点生成：
float4 node_multiply = node_texSample * _Color;

// 输出节点写入：
o.Albedo = node_multiply.rgb;
```

最终所有节点代码片段被按拓扑排序拼接进片元着色器的`void frag()`函数体内。每个节点在代码生成时负责声明自己的局部变量（变量名通常含有节点唯一ID以防冲突），并将输出引脚的值存入该变量供下游节点引用。

### 参数曝光与材质实例

节点图中标记为"属性（Property）"的节点会被提升为着色器的`uniform`变量，从而允许在运行时通过材质实例（Material Instance）修改数值而无需重新编译着色器。例如将一个`Float Parameter`节点命名为`_Roughness`，编辑器会在生成的HLSL头部插入`uniform float _Roughness;`，并在Unity的Inspector或Unreal的参数面板中自动创建对应的UI控件。这一机制的本质是将节点图中的常量节点（Constant Node）与Uniform变量节点（Parameter Node）在代码生成阶段区别对待。

---

## 实际应用

**溶解效果（Dissolve Effect）**是材质图编辑器最典型的教学案例。具体做法：用一张噪声纹理的R通道输出与一个`Float Parameter`（命名`_Threshold`，范围0到1）进行`Step`节点比较，`Step(threshold, noiseValue)`返回0或1，再将结果连接至输出节点的`Opacity Mask`引脚（材质混合模式须设置为Masked）。整个逻辑在节点图中仅需5个节点，若手写对应HLSL约需15行代码，且调试可见性极低。

**UV动画水面**是另一个典型场景：将`Time`节点乘以速度参数后加到UV坐标上，再输入`Texture2D Sample`节点，即可实现纹理流动效果。在Unity ShaderGraph中，这条路径为：`UV节点 → Add → Texture2D Sample`，Time值通过`Multiply`节点缩放后连接至Add的第二个输入。

在Unreal Engine中，材质图编辑器还支持**材质层（Material Layers）**工作流，允许将多个子节点图叠加组合，底层系统会将多张节点图合并编译为一个着色器，避免多Pass渲染的性能损耗。

---

## 常见误区

**误区一：节点数量越多越消耗性能。**
实际上，材质图的性能取决于生成的HLSL指令数，而非节点数本身。一个包含30个节点但全部是简单加减法的材质，其GPU开销可能远低于仅有5个节点但其中包含`tex2D`循环采样的材质。编辑器工具栏中的"着色器统计（Shader Stats）"面板显示的是编译后的ALU指令数和纹理采样次数，这才是性能评估的正确指标。Unreal Engine中可通过`stat shadercomplexity`命令可视化屏幕上各材质的实际指令消耗。

**误区二：节点图可以表达任意着色器逻辑。**
材质图编辑器本质上只能生成片元着色器中的**无状态、无循环**逻辑。标准节点图不支持`for`循环、条件分支（虽然有`If`节点，但底层是`lerp`近似而非真正的GPU分支）、顶点着色器深度定制，以及跨帧状态读写（如渲染目标反馈）。这些需求仍须通过自定义代码节点（Unreal的`Custom`节点或Unity ShaderGraph的`Custom Function`节点）手动插入HLSL片段来实现。

**误区三：材质图与代码之间是单向转换。**
部分引擎（如Godot）支持将VisualShader导出为等价的GDShader文本代码，并允许继续在代码层面修改。但Unreal Engine的材质图不支持反向导出为HLSL进行外部编辑——其内部AST格式是私有的，这意味着一旦选择节点图工作流，就必须在编辑器内完成所有修改。

---

## 知识关联

**前置概念——片元着色器**：理解材质图编辑器的代码生成结果，需要知道最终产物是插入`void frag()`函数体内的HLSL语句序列。若不清楚`SV_Target`输出语义、`SAMPLE_TEXTURE2D`宏的参数含义，就无法判断节点连接是否正确，也无法使用Custom节点扩展节点图。

**后续概念——材质函数（Material Functions）**：材质图编辑器支持将一组节点封装为可复用的材质函数（Unreal）或子图（Unity ShaderGraph中的Sub Graph）。材质函数本质上是带有命名输入输出引脚的节点子图，在代码生成时被内联（inline）展开为等价的HLSL代码段。掌握材质图编辑器的节点数据流模型后，材质函数的封装与参数设计会顺理成章地成为下一步的工程化工具。
