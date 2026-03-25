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
quality_tier: "B"
quality_score: 44.4
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


# 顶点着色器

## 概述

顶点着色器（Vertex Shader）是图形渲染管线中第一个完全可编程的阶段，其核心职责是对每个输入顶点执行变换计算，将顶点从模型局部坐标系（Model Space）逐步变换到裁剪坐标系（Clip Space）。GPU会对网格中的每个顶点独立地并行调用一次顶点着色器，一个包含10,000个顶点的模型意味着顶点着色器将被调用10,000次。

顶点着色器随可编程渲染管线的诞生而出现。2001年DirectX 8.0首次引入了可编程顶点着色器，取代了之前固定功能管线中固化的顶点变换逻辑。在此之前，顶点的MVP变换由硬件以固定方式执行，开发者无法自定义顶点位置的计算过程。GLSL中顶点着色器以`void main()`为入口函数，其必须输出的内置变量`gl_Position`就承担着定义顶点最终裁剪坐标的职责。

顶点着色器的重要性在于它是影响顶点空间位置的唯一可编程入口。骨骼动画的蒙皮（Skinning）、地形的顶点位移（Vertex Displacement）、粒子系统的GPU端位置更新，都依赖顶点着色器在不修改CPU端网格数据的情况下实时改变几何形状。

## 核心原理

### 输入语义（Input Semantics）

顶点着色器的输入来自顶点缓冲区（Vertex Buffer），通过语义（Semantic）标识每个属性的含义。在HLSL中，常见输入语义包括：`POSITION`（顶点位置，通常为float3或float4）、`NORMAL`（法线向量，float3）、`TEXCOORD0`（第一套UV坐标，float2）、`COLOR`（顶点颜色，float4）。GLSL中使用`layout(location = 0) in vec3 aPosition`的方式，通过location编号与VAO中的属性绑定点对应。

每个顶点着色器的调用只能读取**当前顶点**的属性数据，无法访问相邻顶点的信息。这与几何着色器不同，几何着色器可以看到整个图元的全部顶点。

### MVP变换链与 gl_Position

顶点着色器最核心的计算是将顶点位置从模型空间变换到裁剪空间，经历三次矩阵变换，公式为：

$$\mathbf{p}_{clip} = M_{proj} \cdot M_{view} \cdot M_{model} \cdot \mathbf{p}_{local}$$

- **M_model（模型矩阵）**：将顶点从局部坐标系变换到世界坐标系，包含物体的平移、旋转、缩放信息。
- **M_view（观察矩阵）**：将顶点从世界坐标系变换到以摄像机为原点的观察坐标系，由摄像机的位置和朝向决定。
- **M_proj（投影矩阵）**：将观察坐标系中的顶点投影到裁剪坐标系，透视投影矩阵会使远处物体在w分量上产生较大值以实现近大远小效果。

最终写入`gl_Position`的是四维齐次坐标（x, y, z, w），光栅化阶段会将每个分量除以w，得到归一化设备坐标（NDC），x和y的范围均为[-1, 1]（OpenGL约定），z映射到深度缓冲区。

### 输出传递给片元着色器

顶点着色器除了必须输出`gl_Position`外，还可以输出任意用户自定义的varying变量，这些变量在传递给片元着色器之前会经过**插值**处理。例如，顶点着色器输出每个顶点的纹理坐标`vTexCoord`和世界法线`vNormal`，光栅化阶段会根据片元在三角形内的重心坐标对这三个顶点的输出值做线性插值，片元着色器接收到的是插值后的结果。在GLSL中，顶点着色器用`out vec2 vTexCoord`声明输出，片元着色器用`in vec2 vTexCoord`接收，变量名必须匹配。

## 实际应用

**顶点位移动画**：海浪、旗帜等效果可以完全在顶点着色器中实现。以海浪为例，顶点着色器读取顶点的xz坐标和uniform传入的时间变量`uTime`，用正弦函数 `pos.y = sin(pos.x * 0.5 + uTime) * waveHeight` 修改y分量后写入`gl_Position`，CPU端的网格数据始终不变，所有动画计算在GPU上完成。

**骨骼动画蒙皮**：每个顶点存储最多4个骨骼索引（`BLENDINDICES`语义）和对应的权重（`BLENDWEIGHT`语义），顶点着色器从骨骼矩阵数组（uniform数组或纹理）中取出对应骨骼的变换矩阵，按权重混合后再进行MVP变换。这是3D角色动画渲染的标准实现方式。

**视差遮蔽映射的切线空间构建**：顶点着色器中利用顶点的法线`N`和切线`T`构造TBN矩阵（Tangent-Bitangent-Normal），将光线方向从世界空间变换到切线空间后传给片元着色器，使片元着色器能在切线空间中进行高度图采样偏移计算。

## 常见误区

**误区一：认为顶点着色器可以创建或销毁顶点**。顶点着色器的调用次数完全由输入顶点缓冲区的顶点数量决定，每次调用只处理一个顶点并输出一个顶点的数据，不能增加或减少顶点数量。想要动态生成几何体需要使用几何着色器（Geometry Shader）或曲面细分着色器（Tessellation Shader）。

**误区二：混淆观察空间法线变换与位置变换**。将法线从模型空间变换到观察/世界空间时，不能直接使用模型矩阵M，必须使用其逆转置矩阵 $(M^{-1})^T$。当模型矩阵包含非均匀缩放（如x轴缩放2倍、y轴缩放1倍）时，直接用M变换法线会导致法线不再垂直于曲面，造成光照计算错误。

**误区三：认为varying变量的插值在顶点着色器中完成**。顶点着色器只负责计算和输出每个顶点的属性值，插值发生在光栅化阶段（Rasterization Stage），属于固定功能硬件的工作。顶点着色器无法控制插值的具体过程，但可以通过在GLSL中使用`flat`限定符声明输出为不插值（flat shading）。

## 知识关联

学习顶点着色器需要掌握**Shader概述**中关于渲染管线阶段划分的知识，理解为何顶点着色器处于片元着色器之前，以及uniform变量与attribute变量的区别——前者在整个drawcall中保持不变，后者每个顶点各不相同。矩阵乘法的基础线性代数知识是理解MVP变换链的前提，尤其是4×4齐次坐标矩阵的列向量约定与行向量约定（HLSL默认行主序、GLSL默认列主序，直接影响矩阵相乘的书写顺序）。

顶点着色器的输出直接决定了**片元着色器**的输入质量：顶点着色器传出的世界空间法线、切线空间向量、多套UV坐标是片元着色器进行光照计算（Phong、PBR）、法线贴图采样的原材料。理解顶点着色器的插值输出机制，是正确编写片元着色器中各种空间计算的基础。