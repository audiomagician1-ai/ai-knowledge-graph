---
id: "cg-indirect-draw"
concept: "间接绘制"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 4
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
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


# 间接绘制

## 概述

间接绘制（Indirect Draw）是一种由GPU而非CPU决定绘制参数的渲染技术。在传统的直接绘制模式下，CPU调用 `DrawIndexedPrimitive` 时必须明确传入顶点数量、实例数量和偏移量；而间接绘制将这些参数预先写入一个GPU可访问的缓冲区（Argument Buffer / Draw Indirect Buffer），GPU在执行管线时直接从该缓冲区读取参数，CPU不再参与每帧的具体绘制决策。

间接绘制的概念随GPU计算能力的增强而出现。OpenGL 4.0（2010年）引入了 `glDrawArraysIndirect` 和 `glDrawElementsIndirect`，DirectX 11.1 引入了 `ExecuteIndirect` 的前身，而 DirectX 12 和 Vulkan 则将 `ExecuteIndirect` / `vkCmdDrawIndexedIndirect` 提升为一等公民，使GPU-Driven Rendering成为可能。

这一技术的核心价值在于彻底消除CPU-GPU同步瓶颈。传统渲染管线中CPU每帧需要遍历场景中所有物体、完成视锥剔除后提交数以千计的Draw Call；而间接绘制允许Compute Shader在GPU端直接完成剔除并填写绘制参数，CPU仅需提交一次间接绘制命令，从而将大场景的Draw Call数量从数千次压缩到个位数。

---

## 核心原理

### Indirect Buffer 的数据结构

间接绘制的核心是一个名为 `DrawIndexedIndirectCommand`（Vulkan）或 `D3D12_DRAW_INDEXED_ARGUMENTS`（DX12）的结构体，其布局如下：

```
struct DrawIndexedIndirectCommand {
    uint32_t indexCount;      // 本次绘制使用的索引数量
    uint32_t instanceCount;   // 实例化数量
    uint32_t firstIndex;      // 索引缓冲区中的起始偏移
    int32_t  vertexOffset;    // 顶点的基础偏移
    uint32_t firstInstance;   // 实例ID起始值
};
```

CPU在初始化阶段将场景中所有可能的物体槽位预先分配好，Compute Shader在运行时决定将 `instanceCount` 填写为 1（可见）还是 0（剔除），从而在不改变缓冲区大小的情况下动态控制哪些物体被绘制。`firstInstance` 字段还可以用于索引GPU端的变换矩阵数组，实现每实例数据的无CPU传递。

### GPU-Driven Culling 与参数填写

间接绘制的威力来自GPU端剔除管线。一个典型的实现分为三个Compute Dispatch步骤：

1. **视锥剔除**：每个线程处理一个物体的包围球，用6个平面方程 $d_i = \vec{n_i} \cdot \vec{c} + r$ 判断物体是否在视锥体外，若剔除则将对应的 `instanceCount` 置零。
2. **遮挡剔除（HZB）**：将物体的包围盒投影到上一帧的Hierarchical Z-Buffer（分辨率从 512×512 到 1×1 的Mip链），采样对应层级的深度值，若整个包围盒均被遮挡则剔除。
3. **Prefix Sum紧凑化**（可选）：使用并行前缀和算法将稀疏的可见物体列表压缩为连续数组，再写入 Indirect Buffer，避免 GPU 执行大量 `instanceCount=0` 的空绘制。

### Multi-Draw Indirect 与命令计数

DirectX 12 的 `ExecuteIndirect` 和 Vulkan 的 `vkCmdDrawIndexedIndirectCount` 支持在一次API调用中执行多条间接绘制命令。后者接受一个额外的 Count Buffer，由GPU在运行时写入实际绘制数量 N，随后GPU连续执行 Indirect Buffer 中前 N 条命令。这使得CPU甚至不需要知道最终有多少物体通过了剔除测试，整个过程对CPU完全透明。

---

## 实际应用

**《荒野大镖客：救赎2》（2018）** 的地形与植被系统是间接绘制的标志性案例：场景中数十万棵树木和草丛通过GPU Culling + Indirect Instancing渲染，CPU端植被系统的Draw Call数量控制在100以内，而传统方式需要提交超过10万次Draw Call。

**UE5的Nanite**虚拟化几何体系统同样依赖间接绘制。Nanite在Compute Shader中完成Cluster-level的可见性判断后，将每个可见Cluster的绘制参数写入Indirect Buffer，再通过一次 `ExecuteIndirect` 绘制整个场景。这使得场景中多边形数量从每帧预算转变为纯粹的像素着色成本。

在移动端，Vulkan 的 `VK_EXT_multi_draw` 结合间接绘制可以将角色装备系统（通常包含20-50个材质分区）的Draw Call合并为1次，在高通Snapdragon 8 Gen系列上测量到约0.3ms的CPU帧时间节省。

---

## 常见误区

**误区一：间接绘制总是比直接绘制快**

间接绘制引入了Compute Shader的Dispatch开销和Indirect Buffer的内存读写。当场景物体数量少于约200个时，CPU端剔除+直接提交的总开销往往低于启动GPU Culling Pass的固定成本。间接绘制的收益曲线在物体数量超过2000-5000个时才开始明显优于传统方式。

**误区二：`firstInstance` 只是实例化的起始偏移**

许多开发者将 `firstInstance` 仅理解为 `gl_InstanceID` 的偏移量，而忽视了它在GPU-Driven架构中作为**物体索引**的关键用途。通过将 `firstInstance` 设置为物体在全局变换矩阵数组中的槽位索引，单次 `DrawIndexedIndirect` 可以在不绑定任何Per-Object常量缓冲区的情况下，让顶点着色器用 `gl_BaseInstance`（GLSL）直接寻址正确的变换数据，这是Bindless架构的基础操作。

**误区三：间接绘制消除了所有CPU-GPU同步**

Indirect Buffer 的初始化仍需CPU上传物体列表（通常是每帧场景变化的增量更新），Count Buffer的回读（如需在CPU端显示可见物体数量用于调试）会强制GPU-CPU同步，造成数帧的Pipeline Stall。生产环境中应使用 `QueryPool` 的异步统计查询替代直接回读。

---

## 知识关联

**前置概念：深度缓冲**

间接绘制中的HZB遮挡剔除直接依赖深度缓冲的Mipmap化结果。上一帧的深度缓冲经过逐级 `max` 降采样后形成HZB，Compute Shader在剔除阶段读取物体AABB投影区域对应的HZB层级，若包围盒的最近深度值大于HZB中的存储值，则确认遮挡。没有深度缓冲的层次化存储，GPU端遮挡剔除无法实现。

**后续概念：Mesh Shader**

间接绘制将绘制参数的控制权交给了GPU，但顶点着色器仍然按照固定的三角形流水线运行。Mesh Shader（DirectX 12 Ultimate / Vulkan NV_mesh_shader，RTX 20系列起支持）进一步将几何体的**生成**也移入GPU，Amplification Shader（Task Shader）承担了类似间接绘制中Compute Culling的角色，直接在GPU上决定每个Meshlet是否需要展开为完整几何体，使GPU-Driven管线从"控制绘制参数"进化为"动态生成绘制几何"。