---
id: "ta-geometry-shader"
concept: "几何着色器"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
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


# 几何着色器

## 概述

几何着色器（Geometry Shader）是可编程渲染管线中位于顶点着色器之后、片元着色器之前的一个可选阶段，其最显著的特征是能够以**图元（Primitive）为单位**进行操作——它接收完整的图元（如一个三角形的三个顶点、一条线段的两个顶点，或一个点的单个顶点）作为输入，并能够输出零个、一个或多个全新的图元。这种"以少生多"或"以多变少"的能力是顶点着色器所不具备的，顶点着色器只能对单个顶点进行变换，无法创造新的顶点。

几何着色器由微软在 DirectX 10（2006年随 Windows Vista 发布）中引入，OpenGL 3.2（2009年）随后将其纳入核心规范。在此之前，要在GPU上动态生成几何体，开发者通常需要依赖CPU或Transform Feedback等复杂机制。几何着色器的出现让GPU端的程序化几何生成成为主流技术选项，广泛用于粒子系统、草地渲染、法线可视化调试工具等场景。

然而值得注意的是，由于几何着色器会打断GPU的并行流水线——GPU难以预测其输出顶点数量，导致动态负载不均衡——在现代图形管线中，它的性能往往不如将同等工作转移给计算着色器（Compute Shader）或曲面细分着色器（Tessellation Shader）。理解几何着色器的原理与局限，是技术美术在选择渲染方案时做出正确权衡的基础。

---

## 核心原理

### 输入与输出图元类型

几何着色器的函数签名中必须明确声明输入和输出的图元类型。在GLSL中，输入类型关键字包括：`points`（1个顶点）、`lines`（2个顶点）、`lines_adjacency`（4个顶点）、`triangles`（3个顶点）、`triangles_adjacency`（6个顶点）。输出类型则限于三种：`points`、`line_strip`、`triangle_strip`。

```glsl
layout(points) in;                          // 输入：点图元
layout(triangle_strip, max_vertices = 4) out; // 输出：三角形带，最多4个顶点
```

`max_vertices` 声明至关重要：它告知驱动程序每次调用最多输出多少个顶点，驱动据此在显存中为输出缓冲区分配空间。如果将此值设置过大（例如声明 `max_vertices = 256` 但实际只用到4个），会造成显存浪费并降低GPU着色器处理器的占用率（Occupancy）。

### 以点生成四边形（Billboard粒子原理）

最经典的几何着色器用法是**点扩展为公告板（Billboard）**。CPU只需提交一个 `GL_POINTS` 的VBO，每个粒子对应一个点图元。几何着色器接收该点后，根据摄像机朝向计算出四个角点，输出两个三角形（共4个顶点组成的 `triangle_strip`）：

```glsl
void main() {
    vec3 pos = gl_in[0].gl_Position.xyz;
    vec3 right = normalize(cross(u_CameraForward, u_Up)) * u_Size;
    vec3 up    = normalize(u_Up) * u_Size;

    gl_Position = u_MVP * vec4(pos - right - up, 1.0); EmitVertex();
    gl_Position = u_MVP * vec4(pos + right - up, 1.0); EmitVertex();
    gl_Position = u_MVP * vec4(pos - right + up, 1.0); EmitVertex();
    gl_Position = u_MVP * vec4(pos + right + up, 1.0); EmitVertex();
    EndPrimitive();
}
```

`EmitVertex()` 将当前设置好的 `gl_Position` 及所有 `out` 变量作为一个顶点写入输出流；`EndPrimitive()` 标记当前图元结束并开始新的图元。

### 草地渲染中的逐图元变换

在草地渲染场景中，地面网格的每个三角形或每个顶点都可以作为一株草的"种子"。几何着色器接收一个三角形，从其重心（Centroid）位置向上伸展出若干个细长三角形，模拟草叶形态。通过在着色器内使用三角形索引或顶点世界坐标作为随机数种子，可以让每株草的高度、倾斜方向、旋转角度各不相同，而CPU端无需为每株草单独提供数据。典型的草地几何着色器每个输入三角形可生成 3～5 株草，每株草由 3～5 对顶点（6～10个顶点）构成，`max_vertices` 通常设置在 30～50 之间。

### 法线与切线可视化

在调试TBN（切线-副切线-法线）空间时，几何着色器可将每个输入顶点扩展为一条线段：从顶点位置沿法线方向偏移固定距离（通常设为模型包围盒大小的5%，如 `0.05` 个单位）输出两个端点，直接在屏幕上绘制出法线箭头，无需修改任何CPU端代码或创建额外的调试Mesh。

---

## 实际应用

**Unity中的草地系统**：Unity的早期草地渲染（Unity 2019之前的Terrain Detail Mesh）内部使用几何着色器将稀疏的控制点扩展为草叶网格。现代Unity草地插件如 *Grass and Flowers Pack* 仍大量使用几何着色器，每帧在GPU端根据风场纹理（Wind Noise Texture）对草叶顶点施加偏移。

**粒子拖尾线条**：粒子系统中的速度拖尾效果可以用几何着色器实现：输入每个粒子的当前位置（点图元），结合传入的速度向量 `u_Velocity`，沿速度反方向生成一条 `line_strip`，线段长度与速度大小成正比，避免了CPU每帧动态更新拖尾顶点缓冲区的开销。

**阴影体（Shadow Volume）生成**：几何着色器可以检测轮廓边（Silhouette Edge）——当一条边连接的两个三角形中，一个朝向光源、另一个背向光源时，该边为轮廓边——并将其挤出（Extrude）生成阴影体侧面，实现Stencil Shadow Volume算法的完全GPU化。

---

## 常见误区

**误区1：几何着色器总是比CPU生成顶点更快**
这是最普遍的错误认知。几何着色器会序列化GPU的工作流：由于不同图元的输出顶点数可能不同，GPU无法提前规划输出缓冲区的地址，导致各并行处理单元必须等待协调，实际上会引入显著的同步开销。NVIDIA的测试数据表明，在每个几何着色器调用输出超过8个顶点时，其性能通常低于等效的实例化渲染（Instanced Rendering）方案。对于粒子Billboard，使用顶点着色器配合 `gl_VertexID % 4` 索引计算四个角点位置，配合实例化，往往是更优选择。

**误区2：max_vertices可以随意设大以防止溢出**
`max_vertices` 不仅是一个安全上限，它直接影响GPU为该着色器波（Wave/Warp）分配的寄存器和共享缓冲区大小。将 `max_vertices` 设为 `128` 而实际只输出 `4` 个顶点，会导致GPU将本可并行运行8个波的处理器资源只分配给2个波，Occupancy（占用率）下降至原来的25%，帧率可能因此腰斩。

**误区3：几何着色器在所有平台上均可用**
在移动端图形API中，Metal（iOS/macOS）自始至终不支持几何着色器；OpenGL ES 3.2才将其加入规范，且许多中低端移动GPU（如早期Mali系列）的实现性能极差。Vulkan中几何着色器作为可选特性（`geometryShader` feature bit）需要显式查询支持。技术美术在为跨平台项目选用几何着色器时，必须提供不依赖几何着色器的回退（Fallback）方案。

---

## 知识关联

**前置知识**：熟悉顶点着色器（Vertex Shader）的编写是理解几何着色器的必要前提——几何着色器的输入 `gl_in[]` 数组中的每个元素正是经过顶点着色器变换后的顶点数据，包括 `gl_Position`、`gl_PointSize` 等内置变量。理解顶点属性（`in vec3 aPosition`）如何通过顶点着色器传递到 `gl_in[]`，是正确编写几何着色器数据流的基础。

**横向关联**：几何着色器在图元扩展方面的功能，在现代管线中可以由**网格着色器（Mesh Shader）**（DirectX 12 Ultimate / Vulkan NV_mesh_shader）更高效地替代——网格着色器以类计算着色器的方式直接生成网格，彻底绕开了传统管线的串行瓶颈。此外，**Transform Feedback**（OpenGL）或**Stream Output**（DirectX）机制可以将几何着色器的输出捕获回缓冲区，用于粒子系统的多Pass物理模拟，这是几何着色器在特定场景下仍具备不可替代价值的技术方向。