---
id: "cg-shader-permutation"
concept: "着色器变体"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.429
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 着色器变体

## 概述

着色器变体（Shader Variant）是指同一个着色器源文件通过不同的宏定义组合编译出来的多个独立的二进制程序。当你在HLSL或GLSL中使用 `#pragma multi_compile` 或 `#pragma shader_feature` 声明多组宏时，编译器会将每种宏的开关组合分别编译一次，每个结果就是一个变体。假设一个着色器声明了8组独立的 `multi_compile` 宏，每组有2个关键字，理论上最多产生 2⁸ = 256 个变体。

着色器变体的概念随着"Uber Shader"设计模式的普及而出现。Uber Shader将大量条件逻辑集中在一个文件中，用宏控制不同的光照模型、特性开关，避免维护数十个相似的独立着色器。然而这种方式的代价是，编译时需要覆盖所有宏组合，从而催生了"变体爆炸"（Variant Explosion）问题——变体数量呈指数级增长，构建时间、内存占用和运行时PSO缓存开销全面膨胀。

对于现代图形API（Vulkan、DirectX 12、Metal），着色器变体直接关联到**管线状态对象（Pipeline State Object，PSO）**的构建。错误的变体管理策略会导致运行时PSO缓存未命中，触发实时编译，造成游戏中的帧率卡顿（Pipeline Stall）。理解变体的生成机制是优化构建时间与避免运行时卡顿的前提。

---

## 核心原理

### 宏驱动的变体生成机制

Unity的 `#pragma multi_compile A B` 和 `#pragma shader_feature A B` 是最典型的变体声明方式，两者有本质区别：`multi_compile` 的所有变体无论是否被材质使用都会被打包进构建，而 `shader_feature` 只打包被场景内至少一个材质实际引用的变体。这一区别使得 `shader_feature` 适合用于材质级别的特性开关（如 `_NORMALMAP`），而 `multi_compile` 适合运行时动态切换的全局特性（如 `FOG_LINEAR`、`FOG_EXP2`）。

变体的数量公式为：

$$N_{total} = \prod_{i=1}^{k} |S_i|$$

其中 $k$ 是宏组的数量，$|S_i|$ 是第 $i$ 组宏集合的关键字数量（含"全部关闭"状态）。例如，3组宏分别有 {A, B}、{C, D, E}、{F, _} 共3个集合，变体总数为 2 × 3 × 2 = 12。

### 变体剥离（Variant Stripping）

变体剥离是在构建阶段主动删除不会被使用的变体的技术。在Unity中可以通过实现 `IPreprocessShaders` 接口，在 `OnProcessShader` 回调中检查每个 `ShaderSnippetData` 和 `ShaderCompilerData`，根据项目实际使用的关键字集合过滤掉冗余变体。一个实际项目中未经剥离的角色着色器可能产生超过4096个变体，经过针对性剥离后可压缩至64个以内，构建时间缩短70%以上。

Unreal Engine通过 `FShaderPermutationParameters` 和 `ShouldCompilePermutation()` 静态函数实现类似功能——在每个着色器类中重写该函数，返回 `false` 即可在编译时排除不符合条件的排列组合。

### PSO缓存与变体预热

在Vulkan和DX12中，每个着色器变体与一组固定的渲染状态（混合模式、深度测试、顶点布局）结合构成一个PSO。PSO的编译在GPU驱动层发生，耗时可达数百毫秒。如果在游戏运行时首次遇到某个变体与状态组合，会触发实时PSO编译，产生明显卡顿。

解决方案是**PSO预缓存**：在加载界面期间根据已知的变体和渲染状态组合提前创建所有PSO并写入磁盘缓存。Unity的 `ShaderWarmup.WarmupAllShaders()` 和 Unreal的 `FPipelineFileCache` 都是实现这一策略的具体API。PSO缓存文件通常以 `.upipelinecache`（Unreal）或平台特定格式存储，首次运行后二次启动可直接加载，将PSO构建时间从数秒压缩至毫秒级。

---

## 实际应用

**移动端变体优化案例**：某手游的角色着色器原始声明了12组 `multi_compile`，总变体数达到 2¹² = 4096。通过分析发现，其中4组宏（动态阴影、屏幕空间反射、次表面散射、头发高光）在移动端永不启用，直接用 `shader_feature` 替代并在 `IPreprocessShaders` 中强制剥离，最终变体数降至256，包体内着色器内存从180MB降至12MB。

**PSO预热的实现时机**：正确的做法是在关卡加载时通过 `ShaderVariantCollection`（Unity）收集目标场景所有材质引用的变体，调用 `ShaderVariantCollection.WarmUp()` 触发预编译，而非在 `Start()` 或首帧渲染时随机触发。Unreal中在 `GameInstance::Init()` 阶段调用 `FShaderPipelineCache::SetBatchMode(FShaderPipelineCache::BatchMode::Fast)` 可以在后台线程异步构建PSO。

**关键字全局污染问题**：`Shader.EnableKeyword()` 设置的是全局关键字，会影响场景内所有使用该着色器的材质，导致意外激活非预期变体。正确做法是通过 `Material.EnableKeyword()` 设置局部关键字，将变体切换的作用域限制在单个材质实例上。

---

## 常见误区

**误区一：multi_compile 和 shader_feature 可以互换使用**
很多开发者将所有宏都声明为 `multi_compile`，导致构建包含大量从未被材质使用的变体。事实上，任何与材质属性绑定的特性开关（法线贴图、金属度贴图、自发光等）都应使用 `shader_feature`，只有运行时通过 `Shader.EnableKeyword` 全局切换的功能才需要 `multi_compile`。将法线贴图开关从 `multi_compile` 改为 `shader_feature` 这一步骤单独就能使一个典型PBR着色器的变体数减半。

**误区二：变体数量越少越好，无需考虑分支**
与变体方案相对的是在着色器内部使用 `if` 动态分支（Dynamic Branching）。对于GPU上的 uniform 条件（整个 draw call 内条件值不变），现代GPU可以有效地执行动态分支而无需两条执行路径。但对于逐像素变化的条件，动态分支会导致 warp divergence，性能反而差于静态编译的变体。因此，是否使用变体取决于条件是否为 uniform，而非一律追求减少变体数量。

**误区三：PSO缓存只需要在PC端管理**
实际上，iOS的Metal后端和Android的Vulkan后端同样存在PSO实时编译问题，且移动端GPU驱动的PSO编译耗时比桌面端更不稳定，波动范围可达50ms至800ms。忽略移动端PSO预热是导致移动游戏首次进入关卡时出现明显卡顿帧的常见原因之一。

---

## 知识关联

着色器变体的设计前提是**Uber Shader**模式——正是因为将多种功能集中在一个着色器源文件中，才需要宏开关来裁剪功能集，从而产生变体。学习变体之前需要掌握 `#ifdef`/`#pragma multi_compile` 的语法以及HLSL/GLSL的预处理器机制。

从变体管理延伸出去，需要进一步学习**着色器缓存（Shader Cache）系统**的完整架构，包括离线编译工具链（如 `glslangValidator`、`dxc`）如何将变体组织为二进制缓存文件，以及**渲染管线状态管理**中PSO的生命周期、缓存键的构成（着色器哈希 + 渲染状态哈希）。掌握变体管理也是理解**着色器包（Shader Bundle）**热更新方案的基础，因为热更新时需要精确控制哪些变体需要重新下载，哪些可以复用本地缓存。