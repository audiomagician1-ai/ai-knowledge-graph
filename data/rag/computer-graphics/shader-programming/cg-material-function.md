---
id: "cg-material-function"
concept: "材质函数"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
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

# 材质函数

## 概述

材质函数（Material Function）是Unreal Engine材质系统中的一种可封装、可复用的材质节点子图，本质上是将一组材质节点打包为单个可调用单元，存储为独立的 `.uasset` 资源文件。它最早随Unreal Engine 3引入，目的是解决大型项目中大量材质之间重复性逻辑（如菲涅尔计算、UV平铺变换、法线混合）不断被复制粘贴的问题。与普通材质不同，材质函数本身无法直接赋给网格体，它只能作为子模块被其他材质或材质函数调用。

材质函数的重要性在于它从根本上改变了材质的维护模式。在一个包含数百个材质的项目中，如果某一种金属磨损算法需要调整，使用材质函数意味着只需修改一个 `.uasset` 文件，所有引用它的材质在保存后会自动同步更新，而非逐一打开每个材质图手动修改。Unity的ShaderGraph同样提供了名为Sub Graph（子图）的等价机制，其核心思想与材质函数一致。

## 核心原理

### 函数接口：输入与输出节点

材质函数通过两种专用节点定义其对外接口：**FunctionInput**（函数输入）和**FunctionOutput**（函数输出）。FunctionInput节点可以指定类型，包括 `Float1`、`Float2`、`Float3`、`Float4`、`Texture2D`、`StaticBool` 等共9种类型，并可设置默认值，使调用者在不连接该输入时仍能正常编译。FunctionOutput节点定义函数的返回值，一个材质函数可以有多个输出引脚，例如同时输出BaseColor和Roughness。在材质图中调用时，该函数以单个节点呈现，其左侧为输入引脚，右侧为输出引脚，实现了内部逻辑对外的完全隐藏。

### 调用机制与内联展开

材质函数在编译阶段并非以函数调用（call instruction）的形式存在于最终着色器中，而是会被**内联展开**（inline expansion）。这意味着如果同一材质调用了同一个材质函数三次，编译后的HLSL代码中该函数内部的所有节点逻辑会出现三份副本。这与CPU编程中的函数复用不同，它不会带来函数调用开销，但会增加指令数（instruction count）。因此，对于指令数紧张的移动平台材质，应避免在同一材质中过度重复调用复杂材质函数。

### 静态开关与参数传递

材质函数支持 `StaticBool` 类型的输入，配合内部的 `StaticSwitch` 节点，可以实现编译期分支。例如，一个通用的表面湿润效果函数可以接受一个 `StaticBool` 输入 `bEnableRipple`，当外部传入 `true` 时编译进水波纹扰动逻辑，传入 `false` 时该分支的指令完全不存在于最终着色器中。这与运行时的 `If` 节点根本不同——`StaticSwitch` 产生两个独立的着色器排列（shader permutation），而 `If` 节点在两条分支上均产生指令消耗。

## 实际应用

**菲涅尔边缘光函数**是引擎自带材质函数库（Engine Content）中最典型的案例，路径为 `Engine/Functions/Engine_MaterialFunctions02/Shading/MF_Fresnel`。其内部封装了 `dot(Normal, CameraVector)` 运算及幂次控制，对外暴露 `ExponentIn`（Float1，控制边缘锐利程度）和 `BaseReflectFractionIn`（Float1，控制正视角最低反射率）两个输入，输出单个 `Float1` 遮罩值。美术人员无需了解菲涅尔公式 `F = F0 + (1 - F0)(1 - cosθ)^n` 的具体推导，直接调用即可。

**UV变换函数**是另一个高频应用场景。可以将 `TexCoord * Tiling + Offset` 的逻辑、以及时间驱动的UV流动动画封装为单一材质函数，对外暴露 `Tiling`（Float2）、`Offset`（Float2）、`Speed`（Float2）三个参数。项目中所有需要流动效果的水面、熔岩、传送门材质共享同一个函数，保证视觉行为的一致性。

**图层混合系统**中，材质函数可以表示单一材质图层（如泥土层、石块层），通过标准化的 `BaseColor/Normal/Roughness/Metallic` 输出接口，搭配混合权重输入，在父材质中用统一方式叠加多个图层，这正是Unreal Engine材质图层（Material Layer）功能的底层实现方式。

## 常见误区

**误区一：认为材质函数会降低运行时性能**。许多初学者担心"调用函数"会产生额外开销。实际上，如前文所述，材质函数在编译时被内联，最终生成的HLSL与手动复制粘贴节点完全等价，运行时不存在任何函数调用开销。性能问题只来自函数内部的指令数本身，而非函数的封装这一行为。

**误区二：修改材质函数后调用它的材质会自动重新编译着色器**。这一点具有欺骗性：保存材质函数后，引用它的材质会被标记为"脏"（dirty），但着色器的重新编译只在下次打开或保存这些材质时触发，并非实时发生。在大型项目中，批量更新材质函数后，需要主动使用 **Fix Up Redirectors** 或执行 **Resave All** 操作来确保全部材质的着色器缓存是最新的。

**误区三：材质函数等同于材质实例中的参数集合**。材质函数封装的是节点逻辑（计算图），而材质实例（Material Instance）公开的是标量/向量/纹理参数供运行时调整。两者解决的是不同层次的复用问题：函数复用计算逻辑，实例复用材质结构并允许参数变化。一个材质函数内部可以包含 `Parameter` 节点，但这些参数只有在包含该函数的父材质中才会作为实例参数暴露出来。

## 知识关联

学习材质函数之前，需要熟悉**材质图编辑器**的基本操作，包括节点连接方式、引脚类型系统（Float1到Float4的隐式转换规则）以及材质属性（BaseColor、Normal、Roughness等输出槽的含义）。不理解材质图的数据流方向，就无法正确设计FunctionInput的类型和默认值。

材质函数是实现**材质图层系统**（Material Layer System，Unreal Engine 4.19正式推出）的直接技术基础，材质图层本质上是具有固定接口约定的特殊材质函数。此外，掌握材质函数的设计模式后，可自然过渡到理解**着色器库文件**（`.ush`/`.usf` 中的HLSL函数）的组织方式，两者在逻辑封装和复用思想上高度一致，只是一个工作在可视化节点层，另一个工作在文本代码层。