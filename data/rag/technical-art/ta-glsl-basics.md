---
id: "ta-glsl-basics"
concept: "GLSL基础"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# GLSL基础

## 概述

GLSL（OpenGL Shading Language，OpenGL着色器语言）是由Khronos Group随OpenGL 2.0标准于2004年正式引入的着色器编程语言，取代了早期基于汇编指令的ARB着色器扩展。它以C语言为语法基础，专为在GPU着色器阶段编写程序而设计，能够直接运行于顶点着色器（Vertex Shader）和片元着色器（Fragment Shader）两个可编程阶段，OpenGL 3.2之后还支持几何着色器，OpenGL 4.0起引入曲面细分着色器，OpenGL 4.3起支持计算着色器。

GLSL最重要的应用场景是跨平台图形开发，尤其在OpenGL ES 2.0确立之后，它成为移动端GPU编程的统一标准——iOS早期的Metal推出之前、Android平台至今仍大量使用GLSL的ES变体。Unity引擎在编写Surface Shader和OpenGL/OpenGL ES后端时，底层也会将ShaderLab代码编译为GLSL。理解GLSL的语法与限制，是技术美术在跨平台着色器开发与调试中不可绕开的基本能力。

## 核心原理

### 与HLSL的主要差异

GLSL和HLSL（High-Level Shading Language，微软DirectX专用）在功能上高度对等，但存在若干具体的语法和语义差异。

**语义（Semantic）系统**：HLSL使用显式语义标注（如`POSITION`、`TEXCOORD0`、`SV_Target`）来绑定输入输出变量；GLSL不存在这套语义关键字，改用`layout(location = n)` 限定符（OpenGL 3.3+）或内置变量来指定数据槽位。例如，片元着色器最终输出颜色在HLSL中写`float4 col : SV_Target`，在GLSL中则声明 `layout(location = 0) out vec4 fragColor;`，或在旧版中直接写入内置变量 `gl_FragColor`。

**坐标系约定**：GLSL裁剪空间的NDC（Normalized Device Coordinates）深度范围是 **[-1, 1]**，而HLSL/DirectX的NDC深度范围是 **[0, 1]**。这一差异在自己实现投影矩阵或读取深度缓冲时极易引发错误。

**入口函数与着色器分离**：HLSL允许在一个文件里定义多个着色器阶段的函数，通过编译时指定入口名选择；GLSL每个编译单元只对应一个着色器阶段，且入口函数固定命名为 `main()`，没有返回值和参数列表，返回值通过 `out` 变量或内置变量传出。

**矩阵乘法顺序**：HLSL中矩阵默认行主序（row-major），向量通常左乘矩阵写作 `mul(vec, mat)`；GLSL中矩阵默认列主序（column-major），向量右乘矩阵写作 `mat * vec`，两者等价但写法相反，混淆会导致变换结果完全错误。

### 精度修饰符

GLSL ES（用于OpenGL ES 2.0/3.0，即移动端）引入了三种精度修饰符，桌面版GLSL接受这些关键字但通常忽略其语义，编译器仍按最高精度处理。

| 修饰符 | 说明 | 典型精度 |
|---|---|---|
| `highp` | 高精度浮点，对应IEEE 754 32位浮点 | 24位尾数 |
| `mediump` | 中等精度，至少16位浮点 | 10位尾数 |
| `lowp` | 低精度，至少9位浮点，范围 [-2, 2] | 8位 |

在片元着色器中，`mediump` 精度通常足够处理颜色值（0~1范围），但用于世界空间坐标或大范围UV偏移时会出现明显抖动伪影。最佳实践是在文件头部写 `precision mediump float;` 设置默认精度，对需要高精度的变量单独追加 `highp` 修饰，平衡移动端GPU的计算带宽与精度需求。顶点着色器中 `highp` 是默认精度，片元着色器无默认精度，若不声明会引发编译错误（部分驱动会隐式补全，但属于未定义行为）。

### uniform变量

`uniform` 是GLSL中从CPU向GPU传递常量数据的专用存储限定符。uniform变量在同一次Draw Call内对所有顶点和片元保持相同的值，修改只能在CPU端通过 `glUniform*` 系列函数完成，着色器内部不能写入。

声明格式为：
```glsl
uniform mat4 u_ModelViewProjection; // 4x4变换矩阵
uniform sampler2D u_MainTex;        // 纹理采样器
uniform float u_Time;               // 时间变量
```

纹理采样器（`sampler2D`、`samplerCube`等）也通过uniform传递，但其本质是纹理单元索引，绑定方式与普通数值uniform不同——需调用 `glUniform1i(location, textureUnit)` 传入纹理单元编号，而非纹理对象ID。

OpenGL ES 2.0规范要求实现至少支持顶点着色器8个uniform向量（`GL_MAX_VERTEX_UNIFORM_VECTORS >= 128`）和片元着色器16个（`GL_MAX_FRAGMENT_UNIFORM_VECTORS >= 16`），超出限制将导致链接失败。OpenGL 3.1之后引入的**Uniform Buffer Object（UBO）**将uniform打包进GPU缓冲区，可以跨着色器程序共享，并突破单着色器uniform数量限制。

## 实际应用

**移动端半透明Unlit Shader**：在Unity中为Android平台手写一个简单的贴图乘色着色器，片元着色器开头必须写 `precision mediump float;`，颜色输出写入 `gl_FragColor`（OpenGL ES 2.0后端）或通过 `layout(location=0) out vec4 fragColor;` 输出（OpenGL ES 3.0），否则编译器报精度未声明错误或输出变量未定义错误。

**时间驱动的UV动画**：通过 `uniform float u_Time;` 接收CPU每帧传入的时间值，在片元着色器中对采样坐标做偏移 `texture2D(u_MainTex, v_uv + vec2(u_Time * 0.1, 0.0))`，实现流动水面效果。注意 `v_uv` 是从顶点着色器通过 `varying`（ES 2.0）或 `out/in`（ES 3.0）传入的插值变量，与uniform的传递路径不同。

**跨平台深度重建**：从深度缓冲重建世界坐标时，必须考虑GLSL的NDC深度范围 [-1,1] 与HLSL的 [0,1] 差异，线性化公式也需相应调整：GLSL中深度值为 `depth = gl_FragCoord.z * 2.0 - 1.0` 才能还原为线性深度。

## 常见误区

**误区一：认为精度修饰符在PC端有实际效果**
桌面OpenGL驱动几乎都将三种精度统一处理为32位浮点，`lowp` 和 `mediump` 不会带来任何性能提升。精度优化只在实际运行于移动GPU（如Mali、Adreno、PowerVR系列）时才生效，在PC上通过精度修饰符"优化性能"是徒劳的。

**误区二：混淆varying与uniform的生命周期**
`uniform` 是CPU设置、全体着色器调用共享的常量；`varying`（ES 2.0）/ `in/out`（ES 3.0及以上）是在顶点着色器中写入、经过光栅化插值后传入片元着色器的逐片元数据。两者都是"只读"的（对片元着色器而言），但数据来源和插值行为完全不同——将逐顶点计算结果误放入uniform，结果只会取第一个顶点或发生未定义行为。

**误区三：GLSL版本声明可以省略**
不同GLSL版本语法差异显著：1.00 ES使用 `attribute`/`varying`，3.00 ES改用 `in`/`out` 并废弃 `gl_FragColor`，桌面GLSL 1.20 vs 3.30的差异同样巨大。省略 `#version` 指令时，驱动默认按版本 `110`（桌面）或 `100 es`（移动）编译，极易因语法不匹配产生大量编译警告甚至错误，且行为因驱动厂商而异。

## 知识关联

GLSL的执行模型直接建立在GPU渲染管线的可编程阶段之上：顶点着色器读取顶点缓冲中的属性数据（通过 `attribute`/`in` 变量），沿管线写入 `gl_Position` 交给光栅化器，光栅化器对 `varying`/`out` 变量进行双线性插值后将结果送入片元着色器——理解这一数据流是正确使用GLSL各类变量限定符的前提。

从GLSL出发可以进一步延伸到SPIR-V（Vulkan使用的中间字节码）：Khronos于Vulkan 1.0（2016年发布）中引入SPIR-V作为着色器传递格式，GLSL源码通过 `glslangValidator` 或 `shaderc` 工具编译为SPIR-V二进制，运行时不再需要驱动内置的GLSL编译器，解决了长期以来不同厂商GLSL编译器行为不一致