---
id: "ta-shader-math"
concept: "Shader数学基础"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Shader数学基础

## 概述

Shader数学基础是指在GPU着色器程序中直接运用的向量代数、矩阵变换、三角函数和空间几何方法的集合。这些数学工具并非抽象存在，而是直接对应GLSL/HLSL内置函数：`dot()`、`cross()`、`normalize()`、`mul()`、`sin()`等均是对数学概念的硬件加速实现。GPU的并行浮点运算单元（SIMD）专为这类计算优化，因此掌握这套数学语言是编写高性能Shader的前提。

这套数学体系在实时渲染领域于1980年代随光栅化管线的确立而系统化。Jim Blinn在1977年发表的凹凸贴图论文中首次在渲染上下文中明确使用切线空间（Tangent Space）变换，标志着Shader数学从纯理论向实用工程方向的转型。今天，Unity的ShaderLab和Unreal的HLSL都以这套数学体系为基础，每一个顶点着色器的输出都包含至少一次矩阵乘法。

学习Shader数学的意义在于它决定了你能否从"改参数"进化到"写算法"。理解点积与光照模型的关系，才能手写Lambert漫反射；理解旋转矩阵，才能在Shader中实现UV动画的任意角度旋转——这些都无法靠节点连线替代。

---

## 核心原理

### 向量运算与光照计算

向量是Shader中最频繁使用的数据结构，通常为`float3`或`float4`类型。**点积（Dot Product）**是光照计算的核心：

$$\vec{a} \cdot \vec{b} = |\vec{a}||\vec{b}|\cos\theta$$

在Lambert漫反射中，表面法线 $\vec{N}$ 与光照方向 $\vec{L}$（均已归一化）的点积直接给出漫反射强度：`diffuse = max(0.0, dot(N, L))`。当两向量均为单位向量时，点积结果即为夹角余弦，范围在[-1, 1]之间，`max(0, ...)` 截断背面贡献。

**叉积（Cross Product）**用于计算法线或构建正交基。在切线空间构建中，叉积 $\vec{T} \times \vec{B} = \vec{N}$ 将切线（Tangent）和副切线（Bitangent）组合出法线方向，这是法线贴图技术的数学核心。HLSL中 `cross(T, B)` 的返回向量垂直于两输入向量，方向遵循右手定则。

**向量归一化（Normalize）**在插值后必须重新执行。顶点着色器输出的法线经过光栅化插值后不再是单位向量，若不在片元着色器中调用 `normalize(N)`，点积结果将产生非物理的明暗梯度。

### 矩阵变换与坐标空间

Shader流水线涉及四个关键坐标空间：**模型空间（Object Space）→ 世界空间（World Space）→ 观察空间（View Space）→ 裁剪空间（Clip Space）**，每次变换对应一个4×4矩阵乘法：

$$\vec{v}_{clip} = M_{proj} \cdot M_{view} \cdot M_{model} \cdot \vec{v}_{local}$$

其中 $M_{model}$ 包含平移、旋转、缩放；$M_{view}$ 是相机的逆变换；$M_{proj}$ 执行透视除法前的变换。Unity中这三个矩阵组合为 `UNITY_MATRIX_MVP`（Unity 5.x之前）或通过 `UnityObjectToClipPos()` 函数封装。

法线变换不能直接乘以模型矩阵，必须使用**法线矩阵（Normal Matrix）**，即模型矩阵左上3×3部分的逆转置矩阵：$M_{normal} = (M_{model}^{-1})^T$。若模型矩阵含非均匀缩放（如X轴缩放2倍、Y轴缩放1倍），直接用模型矩阵变换法线会导致法线方向错误，产生错误的光照效果。

切线空间到世界空间的变换使用TBN矩阵：以切线 $\vec{T}$、副切线 $\vec{B}$、法线 $\vec{N}$ 为列构成的3×3矩阵，法线贴图中采样到的法线 `normalTS` 通过 `mul(TBN, normalTS)` 转到世界空间参与光照计算。

### 三角函数与UV动画

`sin()` 和 `cos()` 在Shader中被大量用于周期性动画。UV旋转动画的核心是2D旋转矩阵：

$$\begin{pmatrix} u' \\ v' \end{pmatrix} = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix} \begin{pmatrix} u - 0.5 \\ v - 0.5 \end{pmatrix} + \begin{pmatrix} 0.5 \\ 0.5 \end{pmatrix}$$

减去0.5是将旋转中心平移到UV图像中心，旋转后再加回。`_Time.y` 是Unity中内置的时间变量（单位：秒），将其乘以速度系数后传入 `sin/cos` 即可实现持续旋转。

`atan2(y, x)` 返回向量与X轴的夹角（范围 $[-\pi, \pi]$），常用于极坐标UV映射和放射状遮罩：将片元坐标转为极坐标 `(r, θ)`，以 `θ / (2π) + 0.5` 作为U坐标可构建圆形渐变或扇形UI遮罩效果。

---

## 实际应用

**Phong高光计算**综合了向量归一化、点积和幂函数：反射向量 $\vec{R} = 2(\vec{N} \cdot \vec{L})\vec{N} - \vec{L}$，高光强度 `specular = pow(max(0, dot(R, V)), shininess)`，其中 `shininess` 通常取值8到256，控制高光锐利程度。HLSL内置 `reflect(-L, N)` 直接计算反射向量。

**波浪顶点动画**在顶点着色器中用 `sin(_Time.y * speed + positionWS.x * frequency)` 偏移顶点Y坐标，`positionWS.x` 作为相位使不同X位置的顶点波动产生空间延迟，形成水平传播效果。频率参数控制波峰密度，幅度参数控制波高。

**Triplanar投影贴图**使用世界空间法线的绝对值 `abs(N)` 作为三个坐标平面采样结果的混合权重：XZ平面权重为 `N.y`，XY平面权重为 `N.z`，YZ平面权重为 `N.x`，三个权重归一化后加权融合三个方向的UV采样，消除非均匀缩放地形上的贴图拉伸。

---

## 常见误区

**误区1：混淆行向量和列向量的矩阵乘法顺序。** HLSL默认行主序（Row-Major），矩阵乘法写作 `mul(vector, matrix)`；GLSL默认列主序（Column-Major），写作 `matrix * vector`。在Unity HLSL中 `mul(UNITY_MATRIX_MVP, float4(pos, 1.0))` 是正确的，而 `mul(float4(pos, 1.0), UNITY_MATRIX_MVP)` 会产生错误变换，但编译器不会报错，只会输出错误画面。

**误区2：在世界空间中直接用模型矩阵变换法线。** 很多初学者写出 `worldNormal = mul((float3x3)UNITY_MATRIX_M, normal)` 在含非均匀缩放时会得到歪斜的法线。正确做法是使用 `mul(normal, (float3x3)UNITY_MATRIX_I_M)`（乘以模型矩阵逆矩阵的转置等价于乘以逆矩阵后转置），Unity提供 `UnityObjectToWorldNormal()` 函数封装了这一正确计算。

**误区3：认为插值后法线仍是单位向量。** 两个单位向量的线性插值结果长度小于1（除非两者完全相同），因此必须在片元着色器中重新 `normalize`。遗漏这一步时，垂直光照下的球体边缘会出现明显变暗的光照错误，而非线性插值的弧形过渡。

---

## 知识关联

Shader数学基础直接建立在**Shader开发概述**所介绍的渲染管线结构之上——顶点着色器和片元着色器的功能分工决定了矩阵变换在顶点阶段执行、光照计算在片元阶段执行的原因。不理解管线的数据流向，就无法判断某个数学计算应当放在哪个着色器阶段。

掌握了本节内容后，可以直接进入**噪声函数**的学习。Perlin噪声和FBM（分形布朗运动）的实现需要用到向量的 `fract()`、`dot()` 和插值函数 `smoothstep()`——这些都是向量运算的延伸应用。噪声函数将本节的三角函数周期性和向量点积两个知识点结合，构建出伪随机的空间变化效果，是程序化纹理生成的起点。