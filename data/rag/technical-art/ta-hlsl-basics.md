---
id: "ta-hlsl-basics"
concept: "HLSL基础"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# HLSL基础

## 概述

HLSL（High Level Shading Language，高级着色器语言）是微软为DirectX图形API设计的着色器编程语言，首次随DirectX 8.1于2001年发布。在此之前，开发者必须直接编写汇编级别的着色器指令，HLSL的出现将着色器开发提升到了类C语言的抽象层级，大幅降低了GPU编程门槛。

HLSL代码会被FXC（Effect Compiler）或更现代的DXC（DirectX Shader Compiler）编译器编译成DXBC（DirectX Bytecode）或DXIL（DirectX Intermediate Language）中间字节码，再由驱动程序翻译为目标GPU的原生指令集。这种两阶段编译机制使得同一份HLSL代码可以运行在不同厂商的显卡上。HLSL与OpenGL生态中的GLSL是平行对应关系，两者功能相近但语法不完全互换，Unity引擎内部实际使用的ShaderLab最终也会将代码路径编译为HLSL或GLSL。

掌握HLSL是编写顶点着色器、片元着色器和Compute Shader的前提。着色器程序直接在GPU的可编程着色器核心上运行，与C++等CPU语言相比，HLSL天然支持向量与矩阵运算，单条指令即可完成四分量并行计算，这对于图形变换和光照运算至关重要。

## 核心原理

### 数据类型系统

HLSL的基础标量类型包括`float`（32位IEEE 754浮点）、`half`（16位浮点）、`double`（64位浮点）、`int`（32位有符号整数）和`bool`。在此基础上，HLSL引入了向量类型和矩阵类型两类GPU专用聚合类型。

向量类型使用`typeN`格式命名，例如`float4`代表四分量浮点向量，等价于GLSL中的`vec4`。向量支持swizzle（分量重排）操作，可以写成`color.rgba`或`color.xyzw`两套等价的语义别名进行任意组合访问，例如`float3 rgb = color.rgb`或`float2 uv = texCoord.yx`（同时完成了分量提取和翻转）。矩阵类型使用`typeRxC`格式，`float4x4`表示4行4列的浮点矩阵，是MVP变换矩阵的标准类型，访问元素使用`_mRC`下标，如`matrix._m00`访问第0行第0列。

### 语义（Semantics）机制

HLSL中的语义（Semantics）是该语言区别于通用C/C++的核心特性之一。语义是附加在变量声明后的标识符，告知编译器该变量与渲染管线的哪个槽位绑定。顶点着色器输入的顶点位置必须标记为`POSITION`或`SV_Position`语义，颜色数据使用`COLOR0`至`COLOR7`，纹理坐标使用`TEXCOORD0`至`TEXCOORD7`，法线使用`NORMAL`语义。

系统值语义（System Value Semantics）以`SV_`前缀区分，代表管线内置的特殊数据。`SV_Position`是顶点着色器输出的裁剪空间坐标，`SV_Target`是像素着色器向渲染目标写入颜色的语义，`SV_Depth`用于自定义深度写入，`SV_VertexID`和`SV_InstanceID`分别提供当前顶点索引和实例化绘制的实例索引，无需额外传参即可在着色器内访问。

### 内置函数与运算

HLSL内置了约70个专为GPU优化的数学函数，这些函数通常在硬件层面有专用指令支持。关键函数包括：`dot(a, b)`计算向量点积，`cross(a, b)`计算三维向量叉积，`normalize(v)`返回单位向量，`lerp(a, b, t)`执行线性插值（等价于GLSL的`mix`），`saturate(x)`将值钳制到`[0, 1]`区间，`clamp(x, min, max)`钳制到任意区间，`pow(x, y)`计算幂次，`frac(x)`取小数部分，`step(edge, x)`返回阶跃值。

纹理采样函数在HLSL中分为两代API：旧式的`tex2D(sampler, uv)`适用于Shader Model 3.0及以下；现代HLSL使用`Texture2D`对象配合`SamplerState`，调用方式为`tex.Sample(samplerState, uv)`，支持`SampleLevel`（指定mip级别）和`SampleGrad`（传入偏导数）等扩展版本，提供更细粒度的采样控制。

### 着色器入口函数与Shader Model

每个HLSL着色器程序必须声明一个入口函数，其命名可自定义（通常写作`VSMain`、`PSMain`）。`#pragma target`或编译时`/T`参数指定Shader Model版本，如`vs_5_0`代表顶点着色器Shader Model 5.0。Shader Model 5.0（对应DirectX 11）引入了曲面细分着色器和Compute Shader支持；Shader Model 6.0（对应DirectX 12）则引入了波操作（Wave Intrinsics），允许在一个Wave内的线程间共享数据而无需显式同步。

## 实际应用

一个最简单的漫反射着色器展示了HLSL的完整结构。顶点着色器接收`float4 pos : POSITION`和`float3 normal : NORMAL`，通过矩阵乘法`mul(pos, WorldViewProj)`输出`SV_Position`，同时将世界空间法线传递给像素着色器。像素着色器接收插值后的法线，与光照方向做`dot`运算并`saturate`，乘以光照颜色后输出到`SV_Target`，不足20行代码即实现了Lambert漫反射模型。

在Unity的URP管线中，Surface Shader已被淘汰，取而代之的是直接编写HLSL的ShaderLab Pass，通过`#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"`引入URP内置的坐标变换宏和光照函数，这些宏内部封装了`UNITY_MATRIX_MVP`等标准变换矩阵，避免手动声明cbuffer。

## 常见误区

**误区一：混淆行主序与列主序**。HLSL默认矩阵以行主序（row-major）存储，但DirectX数学约定的向量是行向量，变换写法为`mul(vector, matrix)`；而GLSL和OpenGL使用列主序和列向量，写法为`matrix * vector`。在从GLSL移植代码到HLSL时若不注意此区别，矩阵乘法的结果会完全错误。当使用`float4x4`通过cbuffer传递矩阵时，还需注意CPU端是否需要转置。

**误区二：将`half`类型当作性能银弹**。在PC端的桌面GPU上，`half`（float16）的运算速度与`float`（float32）几乎相同，因为大多数桌面GPU的ALU并不支持原生16位运算，编译器会自动提升为32位。`half`的真正优势在于移动端GPU（如Adreno、Mali系列），这类GPU支持FP16硬件加速，理论吞吐量翻倍；在移动端着色器中用`half`替换非必要的`float`精度计算，是实际有效的优化手段。

**误区三：混淆`POSITION`与`SV_Position`的使用位置**。`SV_Position`在顶点着色器的输出结构体和像素着色器的输入结构体中含义不同：顶点着色器输出时代表裁剪空间的齐次坐标（四维），像素着色器接收时已变为屏幕空间坐标（xy为像素坐标，z为深度值，w为1/w_clip）。在像素着色器中直接将`SV_Position.xy`当作纹理UV使用是错误的，需要除以渲染目标分辨率才能得到`[0,1]`范围的UV坐标。

## 知识关联

学习HLSL基础之前需要理解GPU渲染管线的各个阶段划分，明确顶点着色器和像素着色器在管线中分别处于几何变换阶段和光栅化之后的阶段，这样才能理解为何顶点着色器输出需要`SV_Position`语义、像素着色器输出需要`SV_Target`语义。

掌握HLSL语法、数据类型和内置函数后，可以直接进入顶点着色器编写和片元着色器编写的专项学习，前者重点在空间变换矩阵运算和顶点属性传递，后者重点在纹理采样和光照模型实现。Compute Shader是HLSL的进阶方向，使用`numthreads(x, y, z)`属性声明线程组维度，利用`RWTexture2D`和`RWStructuredBuffer`进行读写操作，其语法建立在熟练掌握HLSL基础类型和编译模型之上。
