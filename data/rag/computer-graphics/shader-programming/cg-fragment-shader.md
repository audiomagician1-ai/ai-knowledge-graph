---
id: "cg-fragment-shader"
concept: "片元着色器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.375
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 片元着色器

## 概述

片元着色器（Fragment Shader），在Direct3D中称为像素着色器（Pixel Shader），是GPU渲染管线中对每个片元（Fragment）独立执行的可编程阶段。所谓"片元"，是指光栅化阶段将三角形分解后产生的候选像素，它携带了由顶点着色器输出值插值得到的数据，包括屏幕坐标、深度值、纹理坐标和颜色等属性。片元着色器的最终职责是输出一个`vec4`类型的颜色值（RGBA），或者选择丢弃该片元（使用`discard`关键字）。

片元着色器最早随可编程着色器架构在2001年前后进入实用阶段，DirectX 8.1引入的Pixel Shader 1.1是其早期形态，但功能极为有限，仅支持约8条指令。DirectX 9对应的Shader Model 2.0（2002年）将指令数提升至64条以上，真正使得实时光照计算在硬件上成为可行。现代GLSL和HLSL的片元着色器已无实际指令数限制，可执行复杂的物理渲染（PBR）计算。

片元着色器的重要性在于，它决定了画面最终的光照外观、表面材质质感和特效风格。由于屏幕上每个可见像素至少执行一次片元着色器（实际上由于深度测试，部分执行结果会被丢弃），在1920×1080分辨率下每帧可能涉及超过200万次调用，其计算效率直接影响GPU的渲染性能瓶颈。

## 核心原理

### 插值输入与内置变量

片元着色器的输入数据来自光栅化阶段对顶点属性的重心坐标插值。例如，三角形三个顶点分别具有纹理坐标`(0,0)`、`(1,0)`、`(0,1)`，则三角形内部某片元的纹理坐标由其重心权重`(λ₁, λ₂, λ₃)`计算为`uv = λ₁*(0,0) + λ₂*(1,0) + λ₃*(0,1)`。GLSL中通过`in`关键字声明的变量会自动接收插值结果，而内置变量`gl_FragCoord`提供该片元在窗口空间中的`(x, y, z, 1/w)`坐标，其中`z`分量即为深度缓冲中写入的深度值（范围0.0到1.0）。

### 纹理采样

纹理采样是片元着色器最高频的操作之一。GLSL使用`texture(sampler2D tex, vec2 uv)`函数从纹理对象中读取颜色，GPU硬件单元（Texture Unit）负责执行双线性或三线性过滤。Mipmap选择依赖GPU自动计算相邻片元间的UV偏导数`dFdx(uv)`和`dFdy(uv)`，据此推算LOD层级：`LOD = log₂(max(|dFdx|, |dFdy|) * textureSize)`。当片元着色器在动态分支（if语句）内部执行纹理采样时，GPU无法自动计算偏导数，需手动使用`textureGrad()`函数传入显式偏导数，否则结果未定义。

### Phong光照模型计算

片元着色器中实现Phong光照模型需要计算环境光（Ambient）、漫反射（Diffuse）和镜面反射（Specular）三个分量。完整公式为：

```
I = Ka*Ia + Kd*Id*max(dot(N,L),0) + Ks*Is*pow(max(dot(R,V),0), shininess)
```

其中`N`为归一化法线向量，`L`为指向光源的归一化向量，`R = reflect(-L, N)`为反射向量，`V`为指向摄像机的归一化向量，`shininess`通常取值16到256决定高光锐度。法线`N`需从顶点着色器以`in vec3 fragNormal`传入，但必须注意传入时应已完成法线矩阵变换（`normalMatrix = transpose(inverse(mat3(modelMatrix)))`），否则非均匀缩放会导致法线方向错误。

### 输出与帧缓冲写入

GLSL 1.30及以后版本通过`out vec4 fragColor`声明输出变量，替代了旧式内置变量`gl_FragColor`。在多渲染目标（MRT）场景下，可声明多个`layout(location = N) out vec4`变量，同时向G-Buffer的多个附件写入颜色、法线、深度等信息，这是延迟渲染（Deferred Shading）的基础机制。

## 实际应用

**卡通渲染（Toon Shading）**：通过对漫反射系数`dot(N,L)`进行阶梯化处理，将连续光照值映射为2到3个离散色阶。具体实现中，使用`floor(diffuse * levels) / levels`将光照强度离散化，`levels`通常取2或3，配合轮廓线检测实现日系卡通风格。

**透明度裁剪（Alpha Clipping）**：在片元着色器中采样纹理的Alpha通道后，通过`if(texColor.a < 0.5) discard;`丢弃透明片元，使植被、铁丝网等带镂空的物体无需混合操作即可实现透明效果。相比Alpha混合，`discard`在移动GPU上会破坏Early-Z优化，产生额外的性能开销。

**法线贴图（Normal Mapping）**：从法线纹理采样后，需将采样结果从切线空间变换到世界空间。采样值通过`normal = texture(normalMap, uv).rgb * 2.0 - 1.0`反映射到`[-1,1]`范围，再通过TBN矩阵（由切线T、副切线B、法线N构成的3×3矩阵）变换为世界空间法线，代入光照公式参与计算。

## 常见误区

**误区一：混淆片元与像素的关系**。片元（Fragment）不等同于最终屏幕像素。一个屏幕像素可能对应多个片元（如在MSAA多重采样抗锯齿中，每个像素有4或8个采样点，各自触发独立的片元着色器调用），片元着色器结果在解析阶段才合并为最终像素颜色。因此片元着色器的实际调用次数可能是像素数量的4到8倍。

**误区二：认为`discard`等价于输出透明颜色**。`discard`会完全放弃该片元的写入，深度缓冲也不会更新，而输出`vec4(color.rgb, 0.0)`则仍会更新深度缓冲（取决于写入设置），两者行为截然不同。使用`discard`实现植被渲染时，叶片后方物体的深度关系依然正确；而输出零透明度则可能导致深度冲突。

**误区三：在片元着色器中直接使用模型空间法线做光照**。模型矩阵包含旋转、缩放和平移时，平移分量不影响法线，但非均匀缩放会使法线不再垂直于表面。正确做法是将法线乘以法线矩阵（模型矩阵左上3×3的逆转置），而非直接乘以模型矩阵。这一错误在物体等比缩放时不会显现，容易被忽视。

## 知识关联

片元着色器依赖顶点着色器的输出作为输入来源——顶点着色器通过`out`变量声明的数据，经光栅化插值后成为片元着色器的`in`变量，变量名称和类型必须严格对应，否则链接着色器程序时会报错。理解顶点着色器中裁剪空间变换（MVP矩阵）与片元着色器中世界空间光照计算之间的数据流转，是掌握完整渲染管线的必要前提。

向前延伸，几何着色器可在片元着色器之前修改几何体（如生成粒子和毛发），其输出同样经过光栅化后进入片元着色器处理。表面着色器（Surface Shader）是Unity引擎对片元着色器光照计算部分的高级封装，它自动处理多光源、阴影接收等样板代码，本质上会被编译器展开为包含完整片元着色器逻辑的GLSL/HLSL代码。Uber Shader通过大量`#ifdef`预编译宏将多种材质模式合并进单一片元着色器，以减少Draw Call切换开销，是片元着色器工程实践中的重要组织模式。
