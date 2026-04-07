---
id: "cg-slang"
concept: "Slang语言"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 4
is_milestone: false
tags: ["前沿"]

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
updated_at: 2026-03-26
---



# Slang语言

## 概述

Slang是由NVIDIA研究院与卡内基梅隆大学合作开发的现代着色器编程语言，首个公开版本于2022年发布，其源代码托管在GitHub的shader-slang组织下。Slang的设计目标是解决HLSL在大型渲染管线工程中模块化困难、代码复用率低的问题，同时引入了GPU端自动微分（Automatic Differentiation）能力，使可微渲染（Differentiable Rendering）研究得以直接在着色器层面进行，无需借助外部框架。

Slang在语法上高度兼容HLSL，开发者可以渐进式地将现有HLSL代码库迁移到Slang，而无需全量重写。其编译器后端可以将Slang代码输出为SPIR-V、HLSL、GLSL、Metal Shading Language（MSL）以及CUDA等多种目标格式，这使得一份着色器代码能跨越Vulkan、DirectX 12、Metal和CUDA计算管线。这种跨后端能力对于需要同时支持多平台图形API的引擎开发具有极高的工程价值。

Slang之所以在可微渲染领域受到关注，是因为它是第一个将前向模式（Forward-mode）和反向模式（Reverse-mode）自动微分作为语言一等特性内建到着色器语言规范中的实用工具，而不是依赖运行时解释或Python侧的符号微分。

## 核心原理

### 泛型与接口系统（Generics & Interfaces）

Slang引入了类似Rust trait的`interface`关键字，配合泛型类型参数（Generic Type Parameters）实现可组合的着色器代码。例如，可以定义一个`IMaterial`接口，声明`evalBSDF(float3 wi, float3 wo) -> float3`方法，然后编写一个泛型路径追踪函数`trace<T: IMaterial>(T mat, Ray ray)`，该函数对任意满足`IMaterial`约束的材质类型均可工作。这与HLSL中只能依赖宏（Macro）或代码复制来实现类似效果形成鲜明对比。Slang编译器会在特化（Specialization）阶段将泛型实例化为具体类型，最终生成的GPU字节码不存在虚函数调用开销。

### 自动微分机制

Slang的自动微分通过两个关键修饰符实现：`[Differentiable]`标记一个函数为可微分函数，`DifferentialPair<T>`类型同时携带原始值（primal value）和导数值（differential value）。对于前向模式微分，编译器调用`fwd_diff(f)(DifferentialPair<T> x)`语法生成雅可比向量积（Jacobian-Vector Product, JVP）；对于反向模式微分，使用`bwd_diff(f)(inout DifferentialPair<T> x, T.Differential dResult)`生成向量雅可比积（Vector-Jacobian Product, VJP）。编译器通过对标注为`[Differentiable]`的函数进行源码变换（Source Transformation），在编译期静态生成导数代码，而非在运行期记录计算图（Tape），因此反向传播的内存开销可控。

### 模块系统与编译单元

Slang采用`.slang`文件作为模块单元，通过`import`关键字导入依赖，类似现代C++的模块（Modules）机制。每个模块可以独立编译为Slang IR（一种类SSA形式的中间表示），随后在链接阶段（Link Stage）合并。这使得大型着色器工程可以实现增量编译，避免HLSL中`#include`头文件导致的全量重新编译问题。Slang的编译器API（SlangCompileRequest）也支持在宿主程序中直接驱动，无需调用外部进程，便于集成进实时渲染引擎的资产热重载（Hot Reload）流程。

## 实际应用

在神经辐照缓存（Neural Radiance Cache）的GPU训练场景中，Slang的反向模式自动微分被用于直接在着色器内计算小型MLP网络的权重梯度。研究人员编写一个`[Differentiable]`标注的前向推理函数，Slang编译器自动生成反向传播代码，整个训练循环在单个Dispatch Call内完成，比在CPU侧构建计算图再下发GPU的方案减少约40%的往返延迟。

在跨平台渲染引擎（如基于Falcor框架的实验性渲染器）中，Slang的接口系统被用于构建可插拔的光线追踪管线：定义`ILight`、`IMaterial`、`ISampler`三个接口，不同的材质实现（如Disney BRDF、GGX VNDF）作为独立`.slang`模块，引擎在运行时根据场景需求动态链接对应模块，生成针对目标API（Vulkan或DX12）的专用SPIR-V或DXIL字节码。

## 常见误区

**误区一：认为Slang的自动微分等同于PyTorch的autograd**。PyTorch autograd基于动态计算图，在运行期录制操作序列；Slang的自动微分是编译期源码变换，生成的导数代码是静态的GPU着色器代码，不存在Python GIL开销和运行期图构建，但也无法处理动态控制流中的隐式依赖（需要开发者显式标注可微路径）。

**误区二：以为Slang可以完全替代SPIRV-Cross的跨平台转译工作**。Slang自身可以输出SPIR-V和HLSL等多种后端，但它在输出SPIR-V时仍然依赖其内置的SPIR-V生成器而非SPIRV-Cross。SPIRV-Cross的主要用途是将已有的SPIR-V二进制转换为其他语言，而Slang面向的是源码层的跨平台编写，两者处于管线的不同位置，不能混淆其职责。

**误区三：认为Slang的泛型特化会造成代码膨胀**。与C++模板可能导致的代码膨胀（Code Bloat）不同，Slang编译器在特化时会对共享子表达式进行主动合并，且由于着色器程序通常特化次数有限（材质类型数量受场景约束），最终SPIR-V体积的增长通常在可接受范围内，Slang团队的基准测试显示平均增幅低于15%。

## 知识关联

理解Slang语言需要先掌握SPIR-V的基本结构：SPIR-V以模块（Module）、函数（Function）、基本块（Basic Block）和指令流（Instruction Stream）为组织单元，Slang的Slang IR到SPIR-V的降低（Lowering）过程会将泛型特化结果映射为SPIR-V的`OpFunction`条目，将`DifferentialPair<T>`映射为SPIR-V的结构体类型（`OpTypeStruct`）。如果不理解SPIR-V的类型系统和装饰符（Decoration）机制，将难以调试Slang输出的反射信息（Reflection API）中资源绑定不匹配的错误。

Slang是当前着色器语言演进路线中最接近"着色器领域的Rust"的实践：接口与泛型提供零开销抽象，模块系统提供大规模工程的可维护性，而内建自动微分则将着色器语言的适用范围从实时渲染扩展到科学计算与机器学习领域，代表了GPU编程语言设计的一个重要前沿方向。