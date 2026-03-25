---
id: "cg-geometry-shader"
concept: "几何着色器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 几何着色器

## 概述

几何着色器（Geometry Shader）是OpenGL 3.2和Direct3D 10引入的可编程管线阶段，位于顶点着色器之后、光栅化之前。它是图形管线中唯一能够**生成新图元**的着色器阶段——顶点着色器只能移动顶点，片元着色器只能修改像素颜色，而几何着色器可以接收一个图元并输出零个或多个图元，甚至改变图元类型。

几何着色器由Direct3D 10（2006年随Windows Vista发布）首次引入硬件支持，OpenGL随后在3.2版本（2009年）正式将其纳入核心规范。在此之前，若要在GPU上动态生成几何体，开发者必须依赖CPU计算或渲染到纹理的复杂技巧。几何着色器的出现使得草地渲染、阴影体生成、法线可视化等技术可以完全在GPU端实现。

尽管几何着色器功能强大，但它在现代GPU架构上存在严重的性能瓶颈，以至于许多图形工程师将其称为"有害的功能"。理解它的工作原理和性能特性，有助于在正确场合使用它，或选择更高效的替代方案（如Transform Feedback或Compute Shader）。

---

## 核心原理

### 输入输出图元类型

几何着色器的输入图元类型必须与渲染调用中指定的图元类型匹配。支持的输入类型包括：
- `points`（1个顶点）
- `lines`（2个顶点）
- `lines_adjacency`（4个顶点，含邻接信息）
- `triangles`（3个顶点）
- `triangles_adjacency`（6个顶点，含邻接信息）

输出类型则只能是 `points`、`line_strip` 或 `triangle_strip` 三种之一，且**必须在着色器源码中静态声明**，例如：

```glsl
layout(triangles) in;
layout(triangle_strip, max_vertices = 18) out;
```

`max_vertices` 参数是几何着色器的关键限制：OpenGL规范要求至少支持256个顶点输出，但实际硬件通常在超过128个顶点时性能会急剧下降。每调用一次 `EmitVertex()` 输出一个顶点，每调用一次 `EndPrimitive()` 结束当前图元。

### 内置变量与着色器调用机制

几何着色器通过 `gl_in[]` 数组访问输入图元的所有顶点数据，其中 `gl_in[i].gl_Position` 包含经过顶点着色器变换后的裁剪空间坐标。着色器对**每个输入图元调用一次**，而非每个顶点调用一次——这与顶点着色器（每顶点一次）和片元着色器（每片元一次）的调用粒度截然不同。

一个典型的法线可视化几何着色器会接收每个三角形，沿面法线方向额外生成一条线段。计算公式为：

```
N = normalize(cross(v1 - v0, v2 - v0))
线段起点 = 三角形质心 = (v0 + v1 + v2) / 3
线段终点 = 质心 + N * length
```

此操作将三角形数量不变，但额外输出 `n_triangles` 条线段图元。

### 立方体贴图的单遍渲染

几何着色器最经典的实用场景之一是**单遍阴影贴图（One-pass Shadow Cube Map）**。渲染点光源阴影时，传统方法需要对场景进行6次渲染（对应立方体贴图的6个面）。使用几何着色器配合 `gl_Layer` 内置变量，可以在一次Draw Call中完成全部6次渲染：

```glsl
for(int face = 0; face < 6; ++face) {
    gl_Layer = face;
    for(int v = 0; v < 3; ++v) {
        gl_Position = shadowMatrices[face] * gl_in[v].gl_Position;
        EmitVertex();
    }
    EndPrimitive();
}
```

这里每个输入三角形被扩展为6个输出三角形（`max_vertices = 18`），每个三角形写入立方体贴图的不同层。

---

## 实际应用

**草地与毛发渲染**：将地面网格的每个顶点（`points` 图元）扩展为一个由3-5个三角形组成的草叶图元。草叶的弯曲方向、高度可通过噪声纹理采样确定，整个草地几何体无需存储在顶点缓冲区中，节省大量显存。

**Wireframe叠加渲染**：在几何着色器中通过重心坐标（Barycentric Coordinates）传递边距信息，让片元着色器根据距三角形边缘的距离绘制线框，而无需额外的渲染状态切换。具体做法是在输出中附加 `vec3 barycentric` 属性，分别赋值 `(1,0,0)`、`(0,1,0)`、`(0,0,1)`，片元着色器检查 `min(barycentric.x, barycentric.y, barycentric.z) < 0.02` 来判断是否绘制边缘。

**粒子系统公告板**：将点图元扩展为始终面朝摄像机的四边形（由2个三角形构成），避免了CPU每帧更新顶点位置的开销。

---

## 常见误区

**误区一：几何着色器适合大规模图元生成**。很多初学者认为几何着色器"能生成顶点"就适合做曲面细分。实际上，几何着色器的工作方式是**串行处理**的——现代GPU难以高效并行化几何着色器的可变输出长度。当扩展比例超过4-8倍时，性能通常比在CPU上预生成几何体更差。真正的大规模细分应使用专用的曲面细分着色器（Tessellation Shader，OpenGL 4.0引入）。

**误区二：`max_vertices`只是上限声明，可以随意填大**。`max_vertices`的值直接影响GPU为该着色器分配的输出缓冲区大小（Geometry Shader Output Buffer）。声明`max_vertices = 256`即使实际只输出3个顶点，驱动仍会为最坏情况预分配内存，导致寄存器压力增大、同时运行的着色器线程数（Occupancy）降低，在NVIDIA架构上可实测到30%以上的性能下降。

**误区三：几何着色器是片元着色器的"上游替代"**。几何着色器输出的仍然是图元，后续必须经过光栅化才能进入片元着色器。两者处于完全不同的管线阶段，几何着色器无法直接修改像素颜色，也无法访问帧缓冲区数据，这些操作属于片元着色器的职责范围。

---

## 知识关联

学习几何着色器需要先掌握**片元着色器**的工作原理，因为几何着色器输出的图元属性（如 `out vec3 fragNormal`）会经过光栅化插值后传入片元着色器的 `in vec3 fragNormal`——理解这条数据通路对调试几何着色器输出至关重要。

几何着色器输出图元时使用的 `gl_Layer` 和 `gl_ViewportIndex` 是连接**帧缓冲区附件（Framebuffer Attachment）**和**视口变换**的关键接口，用于实现立方体贴图渲染和VR中的双眼单遍渲染。

在现代图形开发实践中，几何着色器的许多功能正在被**网格着色器（Mesh Shader，DirectX 12 Ultimate / Vulkan 1.2 扩展）**取代。网格着色器允许以计算着色器式的并行模式生成网格，彻底解决了几何着色器的串行化性能问题，是理解几何着色器局限性之后自然的进阶方向。
