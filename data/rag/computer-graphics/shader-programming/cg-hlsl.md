---
id: "cg-hlsl"
concept: "HLSL"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 2
is_milestone: false
tags: ["语言"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# HLSL（高级着色语言）

## 概述

HLSL（High-Level Shading Language）是微软开发的着色器编程语言，专为DirectX图形API配套设计。它于2002年随DirectX 9发布，首次让图形开发者能够用类C语法编写顶点着色器（Vertex Shader）和像素着色器（Pixel Shader），取代了此前晦涩难懂的汇编级着色器指令。HLSL至今仍是Windows平台游戏和实时渲染领域最主流的着色器语言之一。

HLSL的设计目标是让着色器代码兼顾可读性与GPU执行效率。编译器（fxc.exe 或现代的 dxc.exe）将HLSL源代码编译成DXBC（DirectX Bytecode）或 DXIL（DirectX Intermediate Language）中间表示，再由驱动程序转译为具体GPU的机器码。这种两阶段编译架构让同一份HLSL代码能运行在不同品牌的GPU上。

HLSL的重要性在于它直接塑造了现代实时渲染的工作流：UE5的材质系统最终输出HLSL代码，Unity的ShaderLab也将Surface Shader转译为HLSL（在DirectX后端）。学习HLSL等于直接操作GPU渲染管线的可编程阶段。

## 核心原理

### 语义（Semantics）系统

HLSL最显著区别于普通C语言的特性是**语义（Semantic）**标注。语义是绑定在输入/输出变量上的标识符，告诉渲染管线该变量对应GPU管线的哪个寄存器或系统数据。例如：

```hlsl
struct VSOutput {
    float4 position : SV_POSITION;  // 系统值语义，输出裁剪空间坐标
    float2 uv       : TEXCOORD0;    // 用户定义语义，传递UV坐标
    float3 normal   : NORMAL;       // 传递法线向量
};
```

`SV_`前缀的语义（System Value Semantics）具有特殊含义：`SV_POSITION`标记顶点着色器最终输出的裁剪空间位置，`SV_TARGET`标记像素着色器写入的渲染目标，`SV_DISPATCHTHREADID`在计算着色器中表示线程全局编号。若省略语义标注，编译器会直接报错，这与C/C++的变量声明规则完全不同。

### 内置向量与矩阵类型

HLSL内置了GPU原生支持的向量和矩阵类型，无需引入任何库。基础类型包括：`float`（32位浮点）、`half`（16位浮点）、`int`、`uint`、`bool`。在此基础上，`float2`、`float3`、`float4`分别表示2/3/4维向量，`float4x4`表示4×4矩阵。

HLSL支持**向量混合操作（Swizzling）**，这是HLSL代码简洁性的关键来源：

```hlsl
float4 color = float4(1.0, 0.5, 0.2, 1.0);
float3 rgb = color.rgb;     // 取前三个分量
float2 yx  = color.yx;      // 交换顺序
float  r   = color.xxxx.x;  // 重复分量
```

矩阵乘法使用内置函数`mul(matrix, vector)`，注意HLSL默认使用**行主序（row-major）**存储，但`mul`函数将矩阵视为列主序进行乘法，这是初学者频繁踩坑的根源（见常见误区）。

### Shader Model 与编译目标

HLSL代码必须指定编译目标（Shader Model），格式为 `[类型]_[主版本]_[次版本]`，例如`vs_5_0`（Vertex Shader Model 5.0）、`cs_6_6`（Compute Shader Model 6.6）。Shader Model版本决定了可用的指令集和特性：

| Shader Model | DirectX版本 | 新增关键特性 |
|---|---|---|
| SM 4.0 | DX10 | 几何着色器、整数运算 |
| SM 5.0 | DX11 | 曲面细分、UAV、计算着色器 |
| SM 6.0 | DX12 | 波内操作（Wave Intrinsics） |
| SM 6.6 | DX12 Ultimate | 网格着色器（Mesh Shader） |

### cbuffer 与资源绑定

HLSL通过`cbuffer`（Constant Buffer）向着色器传递CPU端数据：

```hlsl
cbuffer PerFrameData : register(b0) {
    float4x4 viewProj;
    float3   cameraPos;
    float    time;
};

Texture2D    albedoMap : register(t0);
SamplerState linearSampler : register(s0);
```

`register`关键字指定绑定槽位，`b`代表cbuffer槽，`t`代表纹理槽，`s`代表采样器槽，`u`代表UAV（可读写资源）槽。DX12/SM6.0引入了**Space**概念（如`register(t0, space1)`）来支持无绑定渲染（Bindless Rendering），允许在着色器中访问任意数量的纹理。

## 实际应用

**Blinn-Phong 光照像素着色器**是HLSL入门的经典示例。完整片段如下：

```hlsl
float4 PS_BlinnPhong(VSOutput input) : SV_TARGET {
    float3 N = normalize(input.normal);
    float3 L = normalize(lightPos - input.worldPos);
    float3 V = normalize(cameraPos - input.worldPos);
    float3 H = normalize(L + V);  // 半角向量
    
    float diff = max(dot(N, L), 0.0);
    float spec = pow(max(dot(N, H), 0.0), shininess);  // shininess通常为32~256
    
    float3 result = (kd * diff + ks * spec) * lightColor;
    return float4(result, 1.0);
}
```

**计算着色器（Compute Shader）**用于GPU通用计算，例如屏幕空间环境光遮蔽（SSAO）的模糊pass。`[numthreads(8, 8, 1)]`属性声明线程组大小（8×8=64线程/组），`SV_DISPATCHTHREADID`获取每个线程处理的像素坐标，配合`RWTexture2D`读写结果图像，整个pass完全在GPU上完成，无需CPU介入。

## 常见误区

**误区1：混淆行主序声明与mul()的列主序约定**

HLSL的`float4x4`按行主序在内存中排列（matrix[0]是第一行），但`mul(M, v)`函数将向量`v`视为列向量进行矩阵-向量乘法。当从DirectXMath（行向量惯例）传入矩阵时，必须使用`mul(v, M)`（行向量左乘），否则变换结果完全错误。这一点因DirectX文档历史上表述不一致而长期困扰开发者。

**误区2：将HLSL的half类型当作性能万能药**

`half`（16位浮点）在移动GPU和某些桌面GPU上确实能提升性能，但在传统NVIDIA桌面GPU（如GTX 10系列）上，驱动会将`half`悄悄提升为`float`执行，性能提升为零。只有在明确支持FP16原生运算的硬件（如RDNA2及以上、移动Adreno GPU）上，`half`才能带来实质收益。盲目用`half`替换`float`可能引入精度问题而无任何性能回报。

**误区3：认为HLSL只能用于DirectX**

自Vulkan生态成熟后，HLSL可通过DXC（DirectX Shader Compiler）编译为SPIR-V字节码，直接在Vulkan中使用。Unreal Engine 5默认就是将HLSL编译成SPIR-V供Vulkan后端使用。因此"HLSL=DX专属"的认知已经过时，现代HLSL是跨API的着色器语言。

## 知识关联

从**Shader概述**中了解的渲染管线阶段（顶点→光栅化→片元）在HLSL中通过不同的入口函数和语义对号入座：顶点着色器入口使用`SV_POSITION`输出，像素着色器使用`SV_TARGET`输出，几何着色器则介于两者之间。Shader概述中"着色器是GPU上运行的程序"的概念，在HLSL中具体化为`[shader("vertex")]`等入口属性和严格的类型系统。

学习HLSL之后，**SPIR-V**是自然的下一站。SPIR-V是Khronos定义的着色器中间表示，DXC可将HLSL编译成SPIR-V供Vulkan/OpenCL使用。理解HLSL的`cbuffer`、`register`绑定模型，能帮助理解SPIR-V中`Binding`和`DescriptorSet`装饰符的设计动机——两者解决的是同一个问题：如何在着色器中引用CPU传入的资源。