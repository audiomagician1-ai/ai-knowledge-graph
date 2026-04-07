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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# HLSL基础

## 概述

HLSL（High Level Shading Language）是微软为DirectX图形API开发的着色器编程语言，首次随DirectX 8.1于2001年发布。与汇编级别的着色器代码相比，HLSL引入了类C语言语法，让程序员能以更高抽象层级描述GPU上的并行计算逻辑，最终由DirectX编译器（FXC或DXC）将其编译为GPU可执行的字节码（DXBC或DXIL）。

HLSL在技术美术领域的重要性体现在：Unity的ShaderLab底层使用HLSL或CG（两者语法几乎等同），Unreal Engine的材质节点最终也会编译为HLSL代码。理解HLSL语法意味着可以绕过节点编辑器的限制，直接描述像素级别的光照模型、噪声算法或自定义后处理效果。HLSL还支持Shader Model 分级（从SM 2.0到SM 6.6），每个版本对应不同的GPU指令集能力，例如SM 6.0引入了Wave Intrinsics，SM 6.5引入了DXR光追着色器。

---

## 核心原理

### 基本数据类型与向量/矩阵扩展

HLSL最基础的标量类型包括 `float`（32位浮点）、`half`（16位浮点）、`int`（32位整数）、`uint`（32位无符号整数）和 `bool`。与C语言不同，HLSL内置向量和矩阵类型作为一等公民：`float4` 表示四维浮点向量，`float4x4` 表示4×4浮点矩阵，可直接对向量进行逐分量算术运算，例如：

```hlsl
float4 a = float4(1.0, 0.5, 0.2, 1.0);
float4 b = a * 2.0;  // 每个分量乘以2，结果(2.0, 1.0, 0.4, 2.0)
```

HLSL独有的**Swizzle（混排）**语法允许任意重组向量分量：`a.zyx` 将返回 `float3(0.2, 0.5, 1.0)`；`a.xxxx` 将x分量广播为 `float4`。Swizzle也可用于赋值左值，如 `col.rgb = tex.bgr;` 可在单行内完成RGB通道顺序翻转。

### 语义（Semantic）系统

语义是HLSL独特的概念，用于告知渲染管线某个变量的用途，写法为变量名后加冒号和语义标识符。顶点着色器的输入语义包括：

- `POSITION`：顶点位置（通常是模型空间的 `float4`）
- `TEXCOORD0` ~ `TEXCOORD7`：UV坐标或自定义插值数据
- `NORMAL`：法线向量
- `COLOR0`：顶点色

输出到片元着色器时使用 `SV_Position`（其中SV代表System Value，表示经裁剪空间变换后的最终位置）。片元着色器必须输出 `SV_Target` 以写入渲染目标颜色缓冲，若存在多个MRT（Multiple Render Target），则使用 `SV_Target0` ~ `SV_Target7`。语义机制本质上是编译器在链接顶点着色器输出与片元着色器输入时匹配槽位的手段，名称不匹配会导致链接错误而非运行时异常。

### 常用内置函数

HLSL提供大量GPU原生加速的内置函数，以下是技术美术最常用的子集：

| 函数 | 作用 | 典型应用 |
|------|------|----------|
| `lerp(a, b, t)` | 线性插值，等同于 `a + t*(b-a)` | 颜色混合、动画过渡 |
| `saturate(x)` | 将x钳制到 [0, 1]，单指令执行 | 防止颜色溢出 |
| `pow(x, n)` | 幂运算，注意x为负时结果未定义 | Phong高光指数 |
| `frac(x)` | 返回x的小数部分 | 周期性纹理、噪声 |
| `ddx(x)` / `ddy(x)` | 屏幕空间偏导数 | MIP级别计算、法线重建 |
| `clip(x)` | x<0时丢弃当前片元 | 透明镂空效果 |
| `mul(M, v)` | 矩阵-向量乘法 | MVP变换 |

特别注意：`tex2D(sampler, uv)` 是SM 3.0及以下的旧式采样函数，SM 4.0以上应使用 `Texture2D.Sample(SamplerState, uv)` 的对象方法形式，两者在Compute Shader中不可互换。

### cbuffer 与常量缓冲区

从CPU传入GPU的数据通过 `cbuffer`（Constant Buffer）声明，语法如下：

```hlsl
cbuffer PerObjectData : register(b0)
{
    float4x4 _MatrixMVP;
    float4   _Color;
    float    _Glossiness;
};
```

`register(b0)` 指定绑定到常量缓冲区槽位0。HLSL要求cbuffer内部遵循**16字节对齐规则**：每个变量不能跨越16字节边界，因此 `float3` 后直接跟 `float` 共16字节可打包，但 `float3` 后跟 `float4` 则会插入4字节填充，这一规则在手写cbuffer时是最常见的数据错位来源。

---

## 实际应用

**Lambert漫反射着色器片段**是理解HLSL语法组合使用的经典案例。设光线方向为 `float3 L`，法线为 `float3 N`，漫反射强度公式为：

```hlsl
float diff = saturate(dot(normalize(N), normalize(L)));
float4 finalColor = _BaseColor * diff;
```

`dot()` 计算点积，结合 `saturate()` 将背面（负值点积）钳制为0，整行代码在GPU上编译为3~4条向量指令。

在Unity URP的自定义HLSL中，常见的文件结构是将cbuffer声明放在 `.hlsl` 头文件中，通过 `#include` 引入，主Pass的 `HLSLPROGRAM` / `ENDHLSL` 块内只保留顶点和片元函数体。这种组织方式使得多个Pass共享同一套常量定义，避免重复声明导致的编译错误。

---

## 常见误区

**误区1：float与half精度无差异**  
在移动端GPU（如Mali、Adreno）上，`half`（mediump）运算的吞吐量是 `float` 的两倍，且寄存器占用减半。将不需要高精度的颜色值、UV坐标声明为 `half` 可显著降低移动端带宽消耗。但在PC端桌面GPU上，硬件通常将 `half` 提升到32位执行，精度优化在此平台无效，需根据目标平台选择。

**误区2：向量运算中Swizzle的赋值副作用**  
初学者常写出 `v.xy = v.yx;`，期望交换x和y分量，但这在HLSL中会产生未定义行为，因为左侧和右侧引用同一向量的重叠分量。正确写法是引入临时变量：`float2 tmp = v.yx; v.xy = tmp;`，或使用内置的 `float2(v.y, v.x)` 构造器。

**误区3：`pow(x, n)` 对负数输入的处理**  
HLSL规范规定当 `x < 0` 时 `pow(x, n)` 的返回值未定义，不同驱动和GPU可能返回NaN、0或错误值。在使用菲涅耳公式 `pow(1 - NdotV, 5)` 时，由于 `1 - NdotV` 在掠射角可能因浮点误差产生极小负数，必须写成 `pow(saturate(1 - NdotV), 5)` 以保证正确性。

---

## 知识关联

学习HLSL基础前需理解**GPU渲染管线**中各阶段的执行顺序：顶点着色器→光栅化→片元着色器，这决定了语义系统中 `POSITION` 与 `SV_Position` 分别作用于哪个阶段，以及为何顶点着色器输出的 `float4 worldPos : TEXCOORD1` 到达片元着色器时已经过重心坐标插值。

掌握HLSL语法和语义系统后，**顶点着色器编写**和**片元着色器编写**会围绕MVP变换矩阵乘法（`mul(_MatrixMVP, v.vertex)`）和纹理采样（`_MainTex.Sample(_MainTex_Sampler, i.uv)`）展开具体实现。而**Compute Shader**将引入 `numthreads` 线程组声明、`RWTexture2D` 可读写资源和 `SV_DispatchThreadID` 内置语义，这些都建立在本文介绍的cbuffer布局规则和内置函数体系之上。