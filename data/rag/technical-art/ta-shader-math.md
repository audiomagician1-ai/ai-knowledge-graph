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

Shader数学基础是指在GPU着色器程序中用于描述几何形状、光照计算和空间变换的数学工具集合，核心包括向量运算、矩阵变换、三角函数以及坐标空间转换。这些数学运算直接对应GPU的硬件指令集——例如NVIDIA的CUDA核心和AMD的CU单元均原生支持SIMD（单指令多数据）浮点运算，使向量和矩阵操作在GPU上比CPU快数个数量级。

Shader数学的历史源头可追溯到1984年Jim Blinn在论文中系统化的齐次坐标（Homogeneous Coordinates）用于计算机图形学，以及1989年SIGGRAPH上Pixar发布的RenderMan着色语言首次将数学函数标准化为着色接口。现代HLSL和GLSL语言均内建了`float2/vec2`到`float4x4/mat4`等数据类型，将数学结构直接映射到GPU寄存器。

理解这些数学工具的意义在于：几乎所有视觉效果——从角色皮肤的次表面散射到水面的菲涅尔反射——本质上都是一组数学公式在每个像素上的并行求值。缺乏数学基础的Shader开发者往往只能复制现有代码，而无法从物理现象出发推导出新的着色逻辑。

---

## 核心原理

### 向量运算及其Shader语义

在Shader中，向量（Vector）不仅是数学对象，更承载着具体的物理意义。一个`float3`型向量可以是RGB颜色、世界空间位置或法线方向，运算规则完全相同，但语义截然不同。

**点积（Dot Product）** 是最频繁使用的操作，公式为：

$$\vec{A} \cdot \vec{B} = |\vec{A}||\vec{B}|\cos\theta$$

在Shader中，`dot(N, L)`（法线N与光线方向L的点积）直接给出漫反射强度因子，当结果为负时说明光线从背面照射。GLSL内建函数`dot()`底层编译为单条GPU指令`DP3`或`DP4`，计算一次点积的延迟约为1个时钟周期。

**叉积（Cross Product）** 用于在切线空间（Tangent Space）中构建法线贴图的TBN矩阵：`B = cross(N, T)`得到副切线（Bitangent）向量，三者组成正交基底。叉积结果`vec3`垂直于输入的两个向量，模长等于它们构成平行四边形的面积，这一性质在程序化生成曲面法线时尤为关键。

### 矩阵变换与MVP流水线

Shader中的矩阵运算核心是**MVP变换链**（Model-View-Projection），顶点着色器的标准操作为：

$$\vec{v}_{clip} = M_{projection} \cdot M_{view} \cdot M_{model} \cdot \vec{v}_{local}$$

**Model矩阵**（4×4）包含物体的位移、旋转和缩放，通常由引擎通过`cbuffer`或`uniform`传入Shader。当矩阵含有非均匀缩放时，法线向量不能直接乘以Model矩阵，而必须乘以其**逆转置矩阵**（Inverse Transpose），否则法线会发生错误偏斜——这是初学者最常踩的坑之一，GLSL中的对应变量是`gl_NormalMatrix`。

**投影矩阵**将视锥体（Frustum）映射到NDC（归一化设备坐标）空间，其中透视除法`w`分量的引入正是为了实现近大远小的透视效果。DirectX的NDC深度范围是`[0, 1]`，而OpenGL是`[-1, 1]`，两套API矩阵定义不同，移植时必须注意。

### 三角函数的Shader应用

`sin()`和`cos()`在Shader中最常用于创建周期性动画，例如顶点波形动画：

```glsl
float offset = sin(position.x * frequency + time * speed) * amplitude;
position.y += offset;
```

`atan(y, x)`（即atan2）用于将笛卡尔坐标转换为极坐标角度，是极坐标UV映射（如漩涡图案、雷达扫描效果）的基础操作，返回值范围为`[-π, π]`。

`smoothstep(edge0, edge1, x)`虽然形式上是多项式`3t² - 2t³`而非三角函数，但与`sin(π/2 * t)`在[0,1]区间内的曲线形状高度相似，是Shader中替代三角函数实现平滑过渡的首选，因为其GPU计算代价更低。

### 坐标空间转换

Shader开发中常见的坐标空间有5种：**局部空间（Object Space）→ 世界空间（World Space）→ 观察空间（View/Eye Space）→ 裁剪空间（Clip Space）→ NDC空间**。法线贴图额外引入**切线空间（Tangent Space）**，其优势在于可以将光照计算从世界空间压缩到贴图的局部坐标系，大幅减少采样计算量。

将世界空间光照方向转换到切线空间需要构建TBN矩阵并乘以光照向量：`vec3 lightTS = TBN * lightDir`，此处TBN为正交矩阵，其逆等于其转置，因此转换代价极低。

---

## 实际应用

**Phong光照模型** 完整依赖上述数学：漫反射 = `max(dot(N, L), 0)`，镜面反射 = `pow(max(dot(R, V), 0), shininess)`，其中反射向量 `R = reflect(-L, N)` 在HLSL/GLSL中是内建函数，底层计算为 `R = 2*(dot(N,L))*N - L`。

**UV动画与极坐标展开** 利用 `atan(uv.y - 0.5, uv.x - 0.5)` 将矩形UV转为角度，配合 `fract(angle / (2π) + time)` 实现旋转扫光效果，常见于技能施放的地面AOE特效。

**顶点描边（Outline Pass）** 通过在法线方向将顶点沿 `Normal * outlineWidth` 外扩实现，依赖法线在世界空间的正确归一化，归一化操作为 `normalize(N) = N / length(N)`，GPU原生支持`rsqrt`倒数平方根指令加速此操作。

---

## 常见误区

**误区一：将法线向量直接乘以含缩放的Model矩阵**
许多初学者直接用`mat3(modelMatrix) * normal`变换法线，在物体有非均匀缩放（如x轴拉伸2倍、y轴不变）时，法线会偏离正确方向。正确做法是使用Model矩阵左上角3×3子矩阵的逆转置矩阵，Unity中内建变量`unity_WorldTransformParams`提供了相关辅助数据。

**误区二：混淆`reflect()`函数的入射向量方向约定**
HLSL和GLSL的`reflect(I, N)`函数要求`I`是**指向表面**的入射方向（即从光源到表面），但物理分析时常以"从表面到光源"为正方向。将方向搞反会得到对称错误的高光位置，调试时需在Shader中输出中间向量进行验证。

**误区三：认为`normalize()`开销可忽略**
`normalize()`依赖平方根运算，在Fragment Shader中对每个像素调用代价不低。插值后的法线向量虽然在顶点处是单位向量，但插值后长度会小于1，是否在Fragment Shader中重新归一化取决于精度要求——低精度移动端场景可省略，高精度PBR渲染必须保留。

---

## 知识关联

**前置概念**：掌握Shader开发概述（包括Vertex/Fragment着色器的执行模型）后，才能理解为何矩阵乘法在顶点阶段执行而非片元阶段——每帧每个顶点仅运行一次MVP变换，而片元着色器每像素执行一次，前者数量远少于后者，将矩阵运算前移可节省大量GPU时间。

**后续概念**：噪声函数（如Perlin Noise和Value Noise）的实现大量使用本节的`fract()`、`dot()`、`smoothstep()`以及向量哈希运算。例如Perlin Noise的核心是计算采样点与周围8个晶格顶点的**梯度向量点积**，再用`smoothstep`进行三线性插值混合——这直接建立在向量点积和插值函数的理解之上。