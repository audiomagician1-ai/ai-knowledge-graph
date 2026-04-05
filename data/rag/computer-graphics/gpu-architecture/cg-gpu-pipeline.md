---
id: "cg-gpu-pipeline"
concept: "GPU硬件管线"
domain: "computer-graphics"
subdomain: "gpu-architecture"
subdomain_name: "GPU架构"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# GPU硬件管线

## 概述

GPU硬件管线（Hardware Pipeline）是指GPU内部将三角形顶点数据转变为屏幕像素的一系列有序处理阶段的物理实现。现代GPU将这条管线分为**固定功能单元（Fixed-Function Units）**和**可编程着色器单元（Programmable Shader Units）**两大类，前者执行逻辑固定的操作（如三角形裁剪、光栅化），后者执行开发者编写的GLSL/HLSL程序。

这条管线的概念成形于1990年代的专用图形加速卡时代。早期的3dfx Voodoo（1996年）几乎全部由固定功能单元构成，开发者只能在有限的参数范围内调整渲染效果。NVIDIA在2001年推出GeForce 3时引入了顶点着色器，2002年GeForce 4 Ti进一步加强，到2004年GeForce 6800实现了完整的像素着色器2.0支持，管线开始向可编程化倾斜。DirectX 11时代（2009年）又引入了外壳/域着色器，形成了今天我们熟知的五阶段可编程管线结构。

理解GPU硬件管线的意义在于：着色器程序的性能瓶颈、绘制调用（Draw Call）的开销、以及Early-Z剔除是否生效，都直接取决于开发者对各阶段硬件行为的掌握程度。

---

## 核心原理

### 固定功能阶段：不可编程但不可绕过

管线中有几个阶段至今仍是纯硬件固定逻辑：

- **输入装配（Input Assembler, IA）**：从顶点缓冲区和索引缓冲区读取数据，将原始顶点流组装成图元（点/线/三角形）。IA阶段不执行任何数学运算，纯粹是数据读取与重排。
- **光栅化（Rasterization）**：将裁剪空间中的三角形转换为屏幕空间的片段（Fragment）。GPU使用固定的边函数（Edge Function）算法：对像素中心点计算 $E(x,y) = (x - x_0)(y_1 - y_0) - (y - y_0)(x_1 - x_0)$，判断该点是否在三角形内部。这个步骤硬件每时钟周期可以并行检测数十个像素，不对外暴露编程接口。
- **重心坐标插值**：光栅化后GPU自动对顶点属性（UV、法线、颜色）做透视校正插值，公式为 $\phi = \frac{\alpha \phi_0 / w_0 + \beta \phi_1 / w_1 + \gamma \phi_2 / w_2}{\alpha/w_0 + \beta/w_1 + \gamma/w_2}$，其中 $w$ 为裁剪空间的 $w$ 分量。开发者无需也无法干预这一过程。

### 可编程阶段：五个着色器类型

完整的DirectX 11/OpenGL 4.0管线包含五种可编程着色器，按执行顺序排列：

1. **顶点着色器（Vertex Shader）**：每顶点执行一次，必须输出裁剪空间坐标 `gl_Position`。是最早被引入的可编程阶段（DirectX 8.0，2000年）。
2. **外壳着色器（Hull Shader / Tessellation Control Shader）**：控制细分因子，决定将一个补丁（Patch）细分为多少个子三角形。
3. **域着色器（Domain Shader / Tessellation Evaluation Shader）**：对细分后的每个新顶点计算其最终位置。
4. **几何着色器（Geometry Shader）**：可以生成或销毁图元，但因其破坏GPU并行性，实际性能常低于预期，现已较少使用。
5. **片段/像素着色器（Fragment/Pixel Shader）**：每个屏幕像素执行一次，输出最终颜色。DirectX 9的ps_3_0模型（2004年）首次允许在此阶段进行动态流控制（if/loop）。

### Early-Z与Late-Z的硬件机制

深度测试（Z-Test）在管线中可以在**两个位置**发生：

- **Early-Z**（像素着色器执行前）：如果深度测试失败，该片段被完全丢弃，无需执行像素着色器。这是最高效的路径。
- **Late-Z**（像素着色器执行后）：当像素着色器中含有 `discard` 指令或修改了深度值（`gl_FragDepth`），GPU无法在执行前确定最终深度，必须等像素着色器执行完毕才能做深度判断，Early-Z失效。

一个像素着色器哪怕只加入一行 `if(alpha < 0.5) discard;` 就会使该物体的所有像素回退到Late-Z路径，这是透明物体渲染开销较大的根本硬件原因。

---

## 实际应用

**Overdraw优化**：由于光栅化阶段会产生大量重叠片段，常见做法是先用只输出深度的"Z-Prepass"渲染一遍不透明物体，之后正式渲染时所有被遮挡像素直接被Early-Z淘汰，像素着色器调用量可减少50%以上。

**曲面细分应用**：在地形渲染中，外壳着色器根据三角形到摄像机的距离设置细分因子（通常在1到64之间，DirectX 11限制最大为64），近处地形获得高细节，远处保持低面数，所有细分由GPU硬件完成，不占用CPU带宽。

**几何着色器的陷阱**：NVIDIA的Maxwell架构（GTX 900系列，2014年）上测量显示，使用几何着色器进行粒子公告板（Billboard）扩展时，吞吐量仅为顶点着色器实例化方案的约30%~50%，原因是几何着色器打断了顶点着色器到光栅化之间的流水线并行性。

---

## 常见误区

**误区一：顶点着色器输出的是屏幕空间坐标**  
顶点着色器输出的是**裁剪空间（Clip Space）**坐标，后续由固定功能的"透视除法"单元将其转换为NDC（Normalized Device Coordinates），再由视口变换映射到屏幕坐标。开发者在顶点着色器中赋值给 `gl_Position` 的第四分量 `w` 不为1时，坐标还未完成变换。

**误区二：可编程阶段越多渲染越慢**  
启用外壳着色器+域着色器会增加管线阶段数，但如果细分使三角形数量适中且能替代大量顶点缓冲区数据，总体带宽消耗反而更低。性能瓶颈取决于哪个阶段的吞吐量成为短板，而非阶段数量本身。

**误区三：`discard` 只影响当前像素**  
GPU以2×2的像素四元组（Quad）为最小调度单位执行像素着色器。即使Quad中只有一个像素调用了 `discard`，其余三个辅助像素也已经被执行（用于计算偏导数 `dFdx/dFdy`）。因此在三角形边缘处大量使用 `discard` 会产生额外的着色器执行开销，这是像素四元组效率（Quad Occupancy）问题的根源。

---

## 知识关联

**前置概念—GPU架构概述**：理解SM（流式多处理器）如何调度Warp执行才能解释为何像素着色器以32个线程为单位并行运行，以及为何分支（如 `discard`）会导致Warp内线程发散。

**后续概念—GPU内存层级**：管线中每个阶段的数据读写（顶点缓冲区→IA、纹理采样→像素着色器、深度缓冲区→ROP）都涉及L1/L2缓存命中率，内存层级直接决定各固定功能阶段的实际延迟。

**后续概念—纹理单元**：纹理采样指令在像素着色器中执行，但实际采样硬件是独立的纹理单元（TMU），像素着色器向TMU发出请求后会暂停等待，理解这一协同关系需要先掌握管线中像素着色器的位置和职责。

**后续概念—ROP（渲染输出单元）**：管线的最后一个固定功能阶段，负责执行Late-Z测试、模板测试和混合（Blend）操作，其带宽直接决定帧缓冲写入速度，是1080p@60Hz高Overdraw场景下的常见性能瓶颈。