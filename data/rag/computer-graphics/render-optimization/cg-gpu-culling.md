---
id: "cg-gpu-culling"
concept: "GPU剔除"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# GPU剔除

## 概述

GPU剔除是指将传统由CPU执行的可见性判断任务完全迁移至GPU端，通过Compute Shader对成千上万个渲染对象并行执行视锥剔除、遮挡剔除等操作，并直接在GPU内存中生成最终的间接绘制指令缓冲区（Indirect Draw Buffer），从而彻底规避CPU与GPU之间的回读（Readback）延迟。这一技术在2015年前后随着DirectX 12和Vulkan等现代图形API的普及而逐渐成为主流，Ubisoft在《刺客信条：起源》中公开分享的GPU Culling管线是业界最早的详细实现案例之一。

传统CPU端剔除的瓶颈在于：当场景物件数量超过10万时，CPU遍历所有物件的包围盒、执行视锥平面测试的时间开销会挤占主线程帧预算。GPU剔除通过一个Dispatch Call替代数万次CPU循环，将每个物件的AABB测试分配给一个独立的GPU线程，测试通过的物件ID被原子写入间接参数缓冲区，整个过程不涉及任何GPU→CPU的数据回传。

## 核心原理

### Compute Shader调度模型

GPU剔除的Dispatch通常以每个线程处理一个渲染实例的方式组织。假设场景有N个物件，则调度线程数为`ceil(N / 64)`个线程组，每组64个线程（这是NVIDIA和AMD共同推荐的波前/Warp友好尺寸）。每个线程读取对应物件的变换矩阵和包围盒数据，执行剔除逻辑后，通过`InterlockedAdd`原子操作向间接参数缓冲区写入Draw参数并递增实例计数器，最终由`DrawMeshTasksIndirect`或`DrawIndexedInstancedIndirect`消耗该缓冲区。

### 视锥剔除的GPU实现

视锥剔除在Shader内的标准做法是将物件的AABB 8个顶点变换至裁剪空间，判断是否与视锥的6个平面均不相交。更高效的方案是使用球形包围体（Bounding Sphere）：将球心变换至视图空间后，逐一与6个平面做点面距离测试，若球心距离某平面的有符号距离小于`-radius`，则该物件在该平面外侧，可以剔除。这一测试只需6次点积运算，相较AABB方法节省约60%的ALU指令。

### Hi-Z遮挡剔除集成

GPU剔除管线通常将Hi-Z（Hierarchical Z-Buffer）遮挡剔除作为视锥剔除之后的第二阶段。具体流程为：先渲染上一帧的深度缓冲，用Compute Shader生成其完整Mip链（每个Mip层取4个子像素的最大深度值），再在当前帧的剔除Shader中将物件包围球投影为屏幕空间矩形，根据矩形尺寸选取对应的Hi-Z Mip层级，采样该层级的最小深度值，若物件的近端深度大于采样深度（即被遮挡），则标记为不可见。这种方案的关键参数是Mip层级选择公式：`mip = ceil(log2(max(rect_width, rect_height)))`，确保单次采样即可覆盖整个投影矩形。

### 间接绘制缓冲区构建

Compute Shader输出的间接参数缓冲区格式由图形API严格规定。以`DrawIndexedInstancedIndirect`为例，每条绘制命令占用20字节，包含`IndexCountPerInstance`、`InstanceCount`、`StartIndexLocation`、`BaseVertexLocation`、`StartInstanceLocation`五个字段。多DrawCall场景下，GPU剔除Shader需维护一个全局原子计数器数组，每类网格对应一个计数器，通过`InterlockedAdd`安全地累积同类型物件的实例数量。

## 实际应用

在《战地》系列使用的Frostbite引擎中，GPU剔除管线将室外场景10万+草丛和植被实例的剔除时间从CPU端的约2ms压缩至GPU端不足0.3ms（GTX 1080级别硬件），帧同步开销几乎为零。

在移动端（如Mali G77 GPU），GPU剔除同样可行，但需注意将间接绘制参数缓冲区声明为`COHERENT`或使用显式内存屏障（`vkCmdPipelineBarrier`），确保Compute阶段写入的数据在后续Draw阶段可见，这一同步步骤是移动端GPU剔除最常见的调试难点。

Unity的GPU Driven Rendering（HDRP 12.0版本引入实验性支持）将所有StaticBatch物件迁入GPU剔除管线，要求物件必须提前烘焙至Cluster结构，每个Cluster包含64个三角面，以Cluster为单位执行剔除而非以物件为单位，进一步提升剔除粒度。

## 常见误区

**误区一：GPU剔除可以完全取代CPU剔除层级结构**。实际上GPU剔除仍需依赖CPU预先构建的空间数据结构（如BVH或Octree）来缩小输入物件集合。若将全场景百万物件不加过滤地全部提交给GPU剔除Shader，Compute Dispatch本身的调度开销和显存带宽消耗会抵消剔除收益。正确做法是CPU做粗粒度的空间裁剪（如只提交摄像机所在区块及相邻区块），GPU做细粒度的逐实例精确测试。

**误区二：Hi-Z遮挡剔除结果与CPU遮挡查询结果等价，可以互换使用**。Hi-Z遮挡剔除使用的是上一帧的深度缓冲，因此对于快速移动的遮挡物会存在一帧的误判延迟，可能错误剔除实际可见物件（漏剔）。这种Ghost Culling现象在高速运动场景下需要通过保守剔除（将包围盒略微放大1%~2%）或双缓冲深度图来缓解，而不能假设其正确性与CPU同步查询相同。

**误区三：GPU剔除在任何平台上只需一次Dispatch即可完成全部工作**。多Pass渲染（如阴影Map多个方向光）要求每个Pass独立执行一次GPU剔除，使用不同的视锥参数缓冲区。若共用同一个间接绘制缓冲区而不清空，会导致前一帧或前一个Pass的绘制指令残留，产生鬼影或崩溃。

## 知识关联

GPU剔除以遮挡剔除中的Hi-Z缓冲概念为基础，将原本在CPU端读回深度纹理进行查询的流程改为在Compute Shader内直接采样GPU端Hi-Z Mip链，避免了PCIe带宽瓶颈。理解遮挡剔除的视锥平面方程和深度比较逻辑，是正确编写GPU剔除Shader的前提。

在实现层面，GPU剔除与间接渲染（Indirect Rendering）技术高度耦合：GPU剔除产出的间接参数缓冲区必须配合`DrawIndirect`系列API才能在不回传CPU的前提下驱动后续渲染，这要求开发者对Modern Graphics API的命令缓冲区和资源屏障机制有扎实掌握。进阶方向包括Mesh Shader管线下的Amplification Shader（DirectX 12 Ultimate），其本质是将GPU剔除逻辑内嵌至可编程网格着色器阶段，进一步减少流水线中的中间数据量。