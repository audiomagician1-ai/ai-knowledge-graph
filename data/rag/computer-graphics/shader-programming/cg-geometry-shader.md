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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 几何着色器

## 概述

几何着色器（Geometry Shader）是OpenGL 3.2和Direct3D 10于2006年引入的可编程管线阶段，位于顶点着色器（或曲面细分着色器）之后、光栅化之前。它是GPU渲染管线中唯一能够**凭空生成新图元**的着色器阶段——顶点着色器只能移动已有顶点，片元着色器只能修改已有像素颜色，而几何着色器可以接收一个三角形并输出零个、一个或多个新的三角形、线段或点。

历史上，几何着色器最初被设计用于加速阴影体（Shadow Volume）生成和立方体贴图渲染（Cubemap Rendering）。在D3D10硬件发布时，NVIDIA和AMD都宣称几何着色器将革命性地降低CPU向GPU传输几何数据的带宽消耗。然而实际应用后，开发者很快发现其性能特征与预期相差甚远，这一教训成为GPU编程史上最重要的性能警示之一。

几何着色器之所以重要，不仅因为它的图元扩展能力，更因为它深刻揭示了GPU并行架构与串行数据依赖之间的根本矛盾。理解几何着色器的工作方式，能帮助开发者判断何时使用它是合理的，何时应当换用其他技术。

---

## 核心原理

### 输入图元与输出图元的类型系统

几何着色器以**完整图元**为输入单位，而非单个顶点。GLSL中使用 `layout(triangles) in;` 声明输入类型，可选类型包括：
- `points`（1个顶点）
- `lines`（2个顶点）
- `lines_adjacency`（4个顶点，含相邻信息）
- `triangles`（3个顶点）
- `triangles_adjacency`（6个顶点，含相邻信息）

输出类型通过 `layout(triangle_strip, max_vertices = 18) out;` 声明，其中 `max_vertices` 是几何着色器**必须静态声明**的最大输出顶点数，驱动程序以此分配寄存器空间。将 `max_vertices` 声明为256虽然合法，但即使实际只输出3个顶点，硬件仍可能按256个顶点分配资源，导致占用率（Occupancy）骤降。

### 图元扩展的执行模型

几何着色器的核心操作是 `EmitVertex()` 和 `EndPrimitive()` 两个内置函数。每次调用 `EmitVertex()` 将当前设置的所有输出变量值写入输出流，每次调用 `EndPrimitive()` 结束当前图元条带并开始新的条带。

以粒子系统的广告牌（Billboard）为例，输入一个点图元，几何着色器输出一个由4个顶点构成的三角形条带（等价于一个四边形）：

```glsl
layout(points) in;
layout(triangle_strip, max_vertices = 4) out;

void main() {
    vec4 pos = gl_in[0].gl_Position;
    EmitVertex(); // 左下角
    EmitVertex(); // 右下角
    EmitVertex(); // 左上角
    EmitVertex(); // 右上角
    EndPrimitive();
}
```

这种"一点变四顶点"的操作在CPU端只需传输1个顶点，节省了75%的顶点上传带宽，是几何着色器真正有收益的经典使用场景。

### 几何着色器的性能陷阱：写回内存的代价

几何着色器的性能问题根源在于其**输出必须写回片上缓存（On-Chip Buffer）或显存**，然后才能进入光栅化阶段。这与顶点着色器的输出可以直接流入固定功能单元不同。

具体来说，GPU执行几何着色器时面临一个根本困境：由于每个几何着色器实例输出的顶点数量不确定（可以是0到 `max_vertices` 之间的任意值），光栅化单元无法在几何着色器完成之前知道自己的工作量。GPU必须等待所有几何着色器实例完成，将结果写入一块临时缓冲区，再统一分配光栅化工作。这个"全局同步点"彻底破坏了流水线的并行性。

NVIDIA在其2012年的《GPU Pro 3》技术文档中指出，对于高密度三角形网格，启用几何着色器后的实际吞吐量可能下降至**不开启时的10%~30%**。Intel集成显卡因片上缓存更小，几何着色器的性能惩罚往往更为严重。

---

## 实际应用

**立方体贴图一遍渲染（Single-Pass Cubemap Rendering）**：传统方法需要对场景绘制6次（每个面一次），而使用几何着色器配合 `gl_Layer` 内置变量，可以在一次DrawCall中将同一个三角形复制到6个面，每个实例写入不同的层。这是几何着色器**性能正收益**的典型案例，因为它减少了6倍的DrawCall开销和CPU-GPU同步成本。

**法线可视化调试工具**：在开发阶段，几何着色器可以接收每个三角形的顶点，计算法线方向，然后额外发射一条从面心沿法线方向延伸的线段。这种调试用途因为不在生产渲染路径中，性能代价可以接受。

**阴影体挤压（Shadow Volume Extrusion）**：几何着色器可以接收 `triangles_adjacency` 输入，判断每条边是否为轮廓边（Silhouette Edge），然后沿光源方向挤压轮廓边生成阴影体四边形。CPU端只需传输原始网格，边界检测和挤压完全在GPU上完成。

---

## 常见误区

**误区一：几何着色器适合大量增加几何细节**
许多初学者认为，既然几何着色器能生成新顶点，就可以用它做曲面细分（把一个三角形拆成多个小三角形）。实际上，当输出顶点数超过约30个时，几何着色器的性能已经很差，且输出数据量越大，写回缓冲区的带宽压力越高。DirectX 11专门引入了**曲面细分着色器（Tessellation Shader）**阶段来替代几何着色器承担这一工作，因为Tessellation Shader有专用硬件单元，不存在写回内存的瓶颈。

**误区二：`max_vertices` 声明越小越好，因此可以不考虑最坏情况**
有开发者为了降低资源占用，将 `max_vertices` 设置得比实际最大输出量更小。这会导致**未定义行为（Undefined Behavior）**：多余的 `EmitVertex()` 调用会被静默丢弃，产生图形伪像但不报任何错误。正确做法是 `max_vertices` 必须等于实际可能输出的最大值，然后通过减少逻辑分支来控制实际输出量。

**误区三：几何着色器是片元着色器功能的上游替代**
几何着色器处理的是图元级别的几何操作，无法访问纹理坐标插值后的数据，也无法读取相邻片元的颜色值。许多效果（如屏幕空间轮廓描边、SSAO）看似是"图元级"操作，但因为需要光栅化后的深度或颜色信息，只能在片元着色器中用后处理实现，几何着色器在这些场景下完全帮不上忙。

---

## 知识关联

**与片元着色器的关系**：片元着色器处理光栅化后的离散像素，其输入（屏幕坐标、插值后的顶点属性）由光栅化阶段产生。几何着色器的输出顶点携带的变量（如 `out vec2 texCoord`）会经过光栅化插值，才成为片元着色器的 `in vec2 texCoord` 输入。因此几何着色器中定义的输出变量接口，必须与片元着色器的输入变量接口完全匹配，否则链接阶段会报错。

**与Transform Feedback的关系**：几何着色器的输出可以通过Transform Feedback机制写回到顶点缓冲对象（VBO），实现GPU粒子系统——粒子位置完全在GPU内存中更新和存储，CPU零参与。这是几何着色器在现代游戏引擎中仍然存活的重要原因之一，尽管在D3D12和Vulkan中，Compute Shader + DrawIndirect已经成为更高效的替代方案。