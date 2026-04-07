---
id: "cg-vertex-shader"
concept: "顶点着色器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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



# 顶点着色器

## 概述

顶点着色器（Vertex Shader）是GPU渲染管线中第一个可编程阶段，它对输入的每一个顶点独立执行一次，负责将顶点从模型本地坐标空间变换到裁剪空间（Clip Space）。在DirectX 9时代（2002年），顶点着色器作为可编程单元首次以标准化形式出现在硬件规范中，取代了此前固定功能管线中写死的矩阵变换逻辑。

顶点着色器的核心任务是输出一个**必填的**裁剪空间位置（gl_Position / SV_Position），如果没有输出这个值，后续的光栅化阶段将无法确定三角形应该覆盖哪些像素。除位置外，顶点着色器还可以输出法线、UV坐标、颜色等插值数据，这些数据会在光栅化时被硬件自动进行重心坐标插值，然后传入片元着色器。

顶点着色器在学习Shader编程时处于入门位置，因为它的输入来源（顶点缓冲区）和输出目标（裁剪空间位置）都有明确的数学定义，不涉及采样、混合等复杂状态，是理解GPU坐标变换链的最佳切入点。

---

## 核心原理

### 输入语义：从顶点缓冲区到着色器变量

顶点着色器的输入来自**顶点缓冲区（Vertex Buffer）**，每个顶点由一组属性构成。在GLSL中，这些属性用 `in` 关键字声明；在HLSL中，通过语义（Semantic）标注，如 `POSITION`、`NORMAL`、`TEXCOORD0`。

```hlsl
// HLSL 顶点输入结构示例
struct VertexInput {
    float3 position : POSITION;   // 模型空间位置
    float3 normal   : NORMAL;     // 模型空间法线
    float2 uv       : TEXCOORD0;  // 纹理坐标
};
```

语义名称本质上是CPU端顶点布局描述（InputLayout / VAO）与着色器变量之间的绑定桥梁。`TEXCOORD0` 到 `TEXCOORD7` 共8个插槽可以复用，传递任何float2/float3/float4数据，并不限于UV坐标。

### MVP变换：顶点着色器的核心数学

顶点着色器中最经典的操作是MVP（Model-View-Projection）矩阵变换：

$$\mathbf{p}_{clip} = M_{proj} \cdot M_{view} \cdot M_{model} \cdot \mathbf{p}_{local}$$

- **M_model（模型矩阵）**：将顶点从模型本地空间变换到世界空间，包含平移、旋转、缩放。
- **M_view（观察矩阵）**：将世界空间顶点变换到以摄像机为原点的观察空间，数学上等价于对世界做摄像机逆变换。
- **M_proj（投影矩阵）**：将观察空间映射到裁剪空间。透视投影矩阵使远处物体的w分量变大，产生近大远小效果；正交投影矩阵保持w=1。

最终输出的裁剪坐标 `(x, y, z, w)` 经过GPU自动执行的**透视除法**（除以w），得到NDC（Normalized Device Coordinates）：x、y、z 均落在 [-1, 1] 范围内（OpenGL约定）或 x、y 在 [-1,1]、z 在 [0,1]（DirectX约定）。

法线变换不能使用模型矩阵，必须使用其**逆转置矩阵**（Inverse Transpose of Model Matrix），原因是法线是协变量，在不均匀缩放下用模型矩阵会导致方向错误。

### 输出语义与顶点到片元的数据传递

顶点着色器的输出（GLSL的 `out`，HLSL的 `struct` 返回值）会在光栅化阶段由GPU对三角形内所有像素进行**线性插值**。但这个插值在透视投影下存在误差，GPU实际执行的是**透视正确插值（Perspective-Correct Interpolation）**，以 `attribute/w` 的加权平均再乘以插值后的w来修正。这一特性对纹理坐标的正确采样至关重要——GLSL 中插值由 `smooth`（默认）、`flat`、`noperspective` 三个限定符控制。

---

## 实际应用

**基础位置变换（Unity HLSL示例）**

```hlsl
float4 vert(VertexInput v) : SV_POSITION {
    return mul(UNITY_MATRIX_MVP, float4(v.position, 1.0));
}
```

在Unity中，`UNITY_MATRIX_MVP` 是引擎预设的MVP合并矩阵；注意顶点位置扩展为 `float4` 时w=1（点），而方向向量w应设为0（向量不应被平移影响）。

**顶点动画：蒙皮骨骼动画**

骨骼蒙皮（Skinning）完全在顶点着色器中完成，每个顶点存储最多4根骨骼的索引和权重（`BLENDINDICES`、`BLENDWEIGHTS` 语义）。着色器读取骨骼矩阵数组，按权重混合变换后得到最终位置，这是游戏角色动画的工业标准实现方式，避免了每帧在CPU端处理数十万个顶点的开销。

**顶点着色器中的Gerstner波**

海面模拟可以在顶点着色器中通过Gerstner波公式 $x = X + Q \cdot A \cdot D_x \cdot \cos(\omega D \cdot P + \phi t)$ 对顶点位置进行偏移，无需纹理采样，仅靠数学公式就能在每个顶点处产生真实感波浪运动。

---

## 常见误区

**误区1：认为顶点着色器可以直接输出像素颜色**

顶点着色器输出的颜色（如 `COLOR0` 语义）只是插值传递给片元着色器的中间数据，并非直接写入帧缓冲。实际决定像素最终颜色的是片元着色器（Fragment/Pixel Shader），顶点着色器无法直接访问或写入渲染目标。Gouraud着色是一种例外的视觉效果——它在顶点计算光照然后插值——但它仍然需要片元着色器把插值结果写入帧缓冲。

**误区2：混淆w=0与w=1的含义**

向量（方向）传入顶点着色器时应将w设为0，这样在模型矩阵乘法中平移项（矩阵第4列）不会影响方向。如果错误地把法线设为 `float4(normal, 1.0)`，在含有平移的变换矩阵下法线方向会被错误偏移，导致光照计算出现明显错误。

**误区3：顶点着色器每帧只执行一次**

顶点着色器的执行次数等于**绘制调用中顶点总数**，而非顶点缓冲区中唯一顶点数。使用索引缓冲区时，同一顶点可能因不同三角形多次引用而被多次调用（不开启后变换缓存的情况下）。现代GPU有**变换后顶点缓存（Post-Transform Cache）**来减少重复计算，通常缓存16~32个最近顶点结果。

---

## 知识关联

**前置知识——Shader概述**：Shader概述建立了渲染管线各阶段的整体框架，明确了顶点着色器在管线中位于输入装配（Input Assembler）之后、光栅化之前的精确位置，以及GLSL/HLSL语言基础。没有这个框架，理解"裁剪空间"和"语义绑定"为何存在会比较困难。

**后续知识——片元着色器**：顶点着色器的输出结构体，直接定义了片元着色器的输入结构体。两者通过语义名称一一对应：顶点着色器输出的 `TEXCOORD0` 插值后成为片元着色器读取的 `TEXCOORD0`。掌握顶点着色器的输出语义类型和插值限定符，是正确编写片元着色器采样逻辑的前提。此外，顶点着色器中传出的世界空间法线、切线、副切线（用于法线贴图的TBN矩阵构建），将在片元着色器的光照计算中被直接使用。