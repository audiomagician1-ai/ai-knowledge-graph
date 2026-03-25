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
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 材质函数

## 概述

材质函数（Material Function）是虚幻引擎（Unreal Engine）材质系统中的一种封装机制，允许将一组材质节点打包为可复用的子图单元，以 `.uasset` 文件单独保存在内容浏览器中。与普通材质图不同，材质函数本身不会被编译为独立着色器，而是在被调用时将其内部节点"展开"（inline）到调用材质的节点图中，最终参与该材质的着色器编译。这种设计意味着材质函数是一种编译期复用机制，而非运行期函数调用。

材质函数的概念于 UE3 时代引入，在 UE4/UE5 中得到完整支持。引擎自带的 `Engine Content/Functions` 目录下预置了大量官方材质函数，例如 `MF_Fresnel`、`Blend_Overlay`（混合模式函数）、`WorldAlignedTexture` 等，开发者可直接调用这些函数，也可以仿照其结构创建自定义函数。

材质函数解决了大型项目中材质节点图重复冗余的问题。当同一套法线扰动逻辑需要在数十个材质中使用时，若不使用函数封装，任何修改都需要手动同步到每个材质图，而使用材质函数后，修改函数本身即可自动传播到所有调用者，显著降低维护成本。

---

## 核心原理

### 输入与输出引脚的声明

材质函数通过两种专用节点暴露接口：`FunctionInput`（函数输入）和 `FunctionOutput`（函数输出）。每个 `FunctionInput` 节点需要指定数据类型，可选类型包括 `Scalar`、`Vector2/3/4`、`Texture2D`、`TextureCube`、`StaticBool` 等共计 10 种类型。`FunctionInput` 还支持设置默认值（Preview Value），当调用方未连接该引脚时，函数将使用此默认值进行预览计算。一个材质函数必须至少包含一个 `FunctionOutput` 节点，否则无法被调用方使用输出结果。

### 内联展开机制

在材质编辑器中放置 `CallMaterialFunction` 节点并引用某个材质函数后，编译器会将函数内部的全部节点完整复制并替换掉 `CallMaterialFunction` 节点的位置，其输入输出引脚与函数声明的 `FunctionInput`/`FunctionOutput` 一一对应。这意味着：若同一个材质中有 3 处调用同一材质函数，编译后的 HLSL 代码中该函数的指令会出现 3 份，而不会合并为一次函数调用。因此，在性能敏感场合应避免在同一材质内大量重复调用同一高复杂度函数。

### 静态参数与动态参数的区别

材质函数中的 `FunctionInput` 若类型为 `StaticBool`，其值在材质实例层面通过 `Static Switch Parameter` 控制，属于编译期常量，不同的静态开关组合会产生不同的着色器变体（Shader Permutation）。而 `Scalar` 或 `Vector` 类型的输入则是动态参数，在运行期由 CPU 传入着色器的常量缓冲区（Constant Buffer）。这一区分直接影响着色器变体数量与运行时性能，设计函数接口时需谨慎选择参数类型。

### 函数库组织与命名规范

虚幻引擎官方推荐以 `MF_` 前缀命名自定义材质函数（如 `MF_TriplanarMapping`），并将其集中存放于专用文件夹（如 `/Game/Materials/Functions/`）。函数支持在 `FunctionInput` 节点上填写 `Description` 字段，调用方悬停引脚时可见该说明，是维护团队协作项目的重要文档化手段。

---

## 实际应用

**三平面映射（Triplanar Mapping）封装**：将沿 X/Y/Z 三个轴分别采样贴图并按法线方向混合的逻辑封装为 `MF_TriplanarMapping`，输入为 `Texture2D`（贴图）、`Scalar`（TilingScale，默认值 1.0）、`Scalar`（BlendSharpness，默认值 4.0），输出为 `Vector3`（混合后颜色）。此函数可被地形材质、岩石材质等多种材质共同调用，修改混合锐度参数只需在函数内部调整即可全局生效。

**Fresnel 边缘光封装**：引擎预置的 `MF_Fresnel` 函数接收 `ExponentIn`（指数，控制边缘范围）和 `BaseReflectFractionIn`（基础反射率）两个输入，内部使用 `Dot(Camera Vector, Vertex Normal)` 后取反并进行幂运算，输出 0~1 的边缘光遮罩。调用该函数时无需重建 Fresnel 公式 `F = F0 + (1 - F0)(1 - cosθ)^n` 的节点连接，只需调整两个引脚参数。

**混合层封装**：角色皮肤材质中，将"皮肤毛孔法线叠加到基础法线"的逻辑（通过 `BlendAngleCorrectedNormals` 节点）封装为独立函数，输入基础法线贴图与细节法线贴图，输出合并法线。项目中所有角色材质引用同一函数，艺术家只需在函数层面调整细节法线强度，所有角色的细节法线表现即同步更新，避免了对十几个角色材质逐一修改。

---

## 常见误区

**误区一：认为材质函数等同于运行时函数调用**。初学者常以为材质函数像 C++ 函数一样在 GPU 上被"调用"并共享指令，实际上材质函数在编译时被展开为内联代码，多次调用等于多份指令拷贝。评估性能开销时应计算展开后的总指令数，而非假设"只执行一次"。

**误区二：混淆材质函数与材质实例的复用方式**。材质实例（Material Instance）是针对整个材质的参数化复用，通过父材质+参数覆盖实现；材质函数是针对材质内部节点子图的封装复用。两者不可互相替代：材质函数无法控制混合模式、着色模型等材质属性，而材质实例无法封装可被多种不同着色模型的材质共用的节点逻辑。

**误区三：在材质函数内部使用全局贴图坐标默认值替代传入参数**。部分开发者在函数内部直接使用 `TexCoord[0]` 节点获取 UV，而不通过 `FunctionInput` 暴露 UV 输入。这导致调用方无法覆盖 UV 偏移或缩放，函数的复用灵活性大幅降低。正确做法是将 UV 作为 `Vector2` 类型的 `FunctionInput` 暴露，并在 `Preview Value` 中填入 `TexCoord[0]` 节点作为默认值，保证函数在预览时正确显示，同时允许调用方传入自定义 UV。

---

## 知识关联

材质函数建立在**材质图编辑器**的节点操作基础之上——需要熟悉材质图中的节点连接方式、数据类型（Scalar/Vector/Texture）以及常用运算节点（Multiply、Lerp、Normalize 等），才能有效设计函数内部的节点拓扑。不了解材质图编辑器的基本操作，将无法正确配置 `FunctionInput` 的数据类型或构建有意义的函数内部逻辑。

在掌握材质函数之后，可以进一步探索**材质参数集合（Material Parameter Collection）**——这是另一种跨材质共享数据的机制，与材质函数的区别在于参数集合传递的是全局标量/向量值，可在蓝图中运行时修改，而材质函数传递的是节点计算逻辑。两者组合使用时，可在材质函数的输入引脚连接参数集合节点，实现"全局统一参数驱动可复用节点逻辑"的设计模式。此外，熟悉材质函数的内联展开机制后，理解**着色器指令计数（Instruction Count）**与**着色器变体（Shader Permutation）**的优化方法也会更加直观。
