---
id: "cg-shader-intro"
concept: "Shader概述"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Shader概述

## 概述

Shader（着色器）是运行在GPU上的小型程序，专门负责决定3D场景中每个像素、每个顶点的最终颜色和位置。它取代了早期图形管线中固定功能管线（Fixed-Function Pipeline）的工作方式——在2001年DirectX 8.0发布之前，GPU只能按照固定算法处理光照和纹理，开发者无法自定义渲染逻辑。DirectX 8.0引入了第一个可编程着色器规范Shader Model 1.0，从此开发者可以用汇编语言编写自定义着色程序，图形编程进入可编程时代。

着色器的重要性体现在它是现代实时渲染质量的直接决定因素。从游戏中的皮肤次表面散射、水面折射，到电影特效中的毛发模拟，所有视觉效果均通过着色器程序实现。现代GPU如NVIDIA RTX 4090拥有超过16000个着色器处理单元，这些单元可并行执行数千个着色器实例，使得实时渲染复杂场景成为可能。

## 核心原理

### 着色器在图形管线中的位置

现代图形管线按顺序包含多个可编程阶段。以Vulkan/DirectX 12的管线为例：应用程序提交顶点数据 → **顶点着色器**处理每个顶点的空间变换 → 几何着色器（可选）生成或修改图元 → 光栅化（硬件固定阶段，不可编程）将几何体转换为像素片段 → **片段着色器**（像素着色器）计算每个像素的最终颜色 → 输出合并。每种着色器只在管线的特定阶段激活，输入输出格式严格规定：顶点着色器必须输出裁剪空间坐标`gl_Position`，片段着色器必须输出颜色值。

### 着色器的主要类型

| 类型 | 英文名 | 运行时机 | 典型用途 |
|------|--------|----------|----------|
| 顶点着色器 | Vertex Shader | 每顶点一次 | MVP矩阵变换、顶点动画 |
| 片段/像素着色器 | Fragment/Pixel Shader | 每片段一次 | 光照计算、纹理采样 |
| 几何着色器 | Geometry Shader | 每图元一次 | 粒子扩展、阴影体生成 |
| 计算着色器 | Compute Shader | 自由调度 | 物理模拟、后处理 |
| 曲面细分着色器 | Tessellation Shader | 每面片一次 | 地形LOD、位移贴图 |
| 光线追踪着色器 | Ray Tracing Shader | 每光线一次 | 反射、全局光照（DXR/Vulkan RT） |

计算着色器自DirectX 11（Shader Model 5.0，2009年）起成为标准配置，它不参与光栅化管线，而是直接在GPU上执行通用并行计算。

### 着色语言生态

不同平台使用不同的着色语言，但它们的语法均源自C语言：

- **GLSL**（OpenGL Shading Language）：随OpenGL 2.0在2004年正式引入，语法形如 `vec4 color = texture(sampler, uv);`，使用`in/out`关键字传递数据，跨平台支持Linux/macOS/Windows/WebGL。
- **HLSL**（High-Level Shading Language）：微软为DirectX开发，自DirectX 9起随Shader Model 2.0提供，语法使用`float4`代替`vec4`，通过`SV_Position`等语义（Semantics）描述数据含义。
- **MSL**（Metal Shading Language）：苹果2014年随Metal API推出，基于C++14语法，使用`[[position]]`属性标注语义。
- **WGSL**（WebGPU Shading Language）：2023年随WebGPU标准正式发布，专为浏览器端GPU编程设计，语法更接近Rust风格。
- **SPIR-V**：Khronos Group设计的中间表示（IR）格式，GLSL/HLSL均可编译为SPIR-V，Vulkan和OpenCL直接消费此格式，实现跨语言兼容。

### 着色器编译流程

着色器从源代码到GPU执行经历多个编译阶段：

1. **前端编译**：GLSL由`glslangValidator`编译，HLSL由`dxc`（DirectX Shader Compiler）编译，输出SPIR-V或平台中间码。
2. **驱动层编译**：显卡驱动将中间码编译为特定GPU的机器码（如NVIDIA的SASS指令集、AMD的GCN/RDNA指令集）。这一步在运行时发生，是游戏首次运行时"着色器编译卡顿"的直接原因。
3. **着色器缓存**：为避免重复编译，驱动将编译结果缓存到磁盘（如Windows的`%APPDATA%\NVIDIA\DXCache`），后续启动直接加载缓存，消除卡顿。

编译阶段的分离意味着一个语法正确但逻辑错误的着色器可能通过前端编译，却在驱动层优化时产生意外行为。

## 实际应用

**Unity中的着色器体系**：Unity使用名为ShaderLab的包装语言，内部嵌入HLSL代码块（称为`CGPROGRAM`或`HLSLPROGRAM`），由Unity工具链将HLSL编译为目标平台所需格式（PC端DXBC/DXIL，移动端GLSL ES，主机端平台专有格式）。一个Unity着色器文件可同时包含多个`Pass`，每个Pass对应一次渲染调用，用于实现多pass技术如描边效果。

**Web端着色器**：WebGL 2.0使用GLSL ES 3.00语法，开发者通过JavaScript的`gl.createShader()`创建着色器对象，以字符串形式传入GLSL源码，调用`gl.compileShader()`在浏览器内完成编译。Three.js等库将此流程封装，提供`ShaderMaterial`接口供用户直接编写GLSL代码。

## 常见误区

**误区1：着色器代码按顺序逐像素执行**  
实际上，GPU以"线程组（Warp/Wavefront）"为单位并行执行着色器，NVIDIA GPU每个Warp包含32个线程，AMD每个Wavefront包含64个线程。所有线程执行相同指令（SIMT架构），当出现`if-else`分支时，两个分支的代码都会执行，不满足条件的线程被屏蔽，这称为"Warp Divergence"，会显著降低性能。

**误区2：GLSL和HLSL可以直接互换使用**  
两者除基本数学函数同名外存在大量差异：GLSL使用`texture()`采样纹理，HLSL使用`tex.Sample(sampler, uv)`；GLSL的`gl_FragCoord`对应HLSL的`SV_Position`；GLSL没有语义系统，HLSL的语义是编译器识别变量用途的强制机制。直接复制代码必然编译失败。

**误区3：着色器只用于视觉渲染**  
计算着色器已广泛用于非视觉计算：TensorFlow和PyTorch的早期GPU加速、游戏中的GPU粒子物理模拟、音频处理（如NVIDIA DLSS的超分辨率模型推理）均通过计算着色器实现，与画面颜色计算无关。

## 知识关联

学习Shader概述后，下一步应分方向深入：若目标是DirectX/Unity开发，则直接进入**HLSL**语法学习，重点掌握其语义系统和常量缓冲区（Constant Buffer）；若目标是OpenGL/WebGL，则进入**GLSL**，理解`uniform`变量和`layout`限定符。**顶点着色器**是管线中最先接触的可编程阶段，应在了解Shader整体类型后优先实践。**Shader Model**版本号（如SM 5.0、SM 6.0）规定了不同类型着色器可使用的功能集合，是选择目标硬件时的关键参数。当编写的着色器产生视觉异常时，需要进入**着色器调试**领域，使用RenderDoc、PIX等工具逐步检查每个着色器阶段的输入输出。