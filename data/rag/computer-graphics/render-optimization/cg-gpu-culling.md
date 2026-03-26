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
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
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

GPU剔除（GPU-side Culling）是将传统由CPU执行的视锥体剔除、遮挡剔除等判断逻辑，全部迁移到GPU端，通过Compute Shader并行处理场景中所有物体的可见性判断，并直接在GPU上构建最终的DrawCall列表的技术方案。与CPU剔除相比，GPU剔除消除了CPU→GPU之间的数据回读瓶颈，整个可见性判断结果留存在GPU显存中，直接驱动后续渲染。

该技术随着DirectX 11中Compute Shader的普及而逐渐成熟，并在DirectX 12和Vulkan引入`ExecuteIndirect`（DX12）与`vkCmdDrawIndirect`（Vulkan）之后获得了决定性的基础设施支持——这两个API允许GPU直接消费存储在Buffer中的DrawCall参数，无需CPU介入，从而使GPU剔除的完整闭环成为可能。虚幻引擎5的Nanite系统和Unity HDRP的GPU Driven管线均以此为核心思路构建。

在场景包含数万乃至数十万独立网格体的情况下，CPU剔除受限于单线程或有限并行度，往往成为帧时间的主要瓶颈。GPU剔除利用数千个Compute Shader线程同时处理物体包围盒，可在0.1~0.5ms内完成CPU需要3~10ms才能完成的剔除工作，极大释放了CPU资源，使CPU可以专注于游戏逻辑和物理计算。

---

## 核心原理

### Compute Shader并行剔除流程

GPU剔除的典型流程分为三个阶段。**第一阶段**：CPU每帧将场景中所有物体的包围球或AABB上传到一个结构化缓冲区（StructuredBuffer），格式通常为每对象16~32字节，包含中心点、半径/尺寸及物体索引。**第二阶段**：Dispatch一个Compute Shader，线程组配置通常为`[numthreads(64, 1, 1)]`，每个线程负责判断一个物体是否通过视锥体的6个平面测试（Frustum-Plane Test）：

```
distance = dot(plane.normal, sphere.center) + plane.d
visible = (distance > -sphere.radius)
```

六个平面全部通过则标记为可见，将该物体的DrawCall参数（顶点数、实例数、起始偏移）写入`AppendStructuredBuffer`。**第三阶段**：调用`ExecuteIndirect`，以上一步填充的Buffer直接驱动绘制，CPU完全不参与DrawCall数量的决策。

### 两遍式遮挡剔除（Two-Pass Occlusion Culling）

仅做视锥体剔除无法处理被遮挡的物体，GPU剔除通常结合Hierarchical Z-Buffer（HZB）实现遮挡剔除。具体分两遍执行：

**第一遍（Early Pass）**：使用上一帧的HZB作为遮挡参考（称为"时间重用"），对当前帧所有物体做剔除，渲染通过测试的物体并生成当前帧的深度图，随后将深度图降采样构建新的HZB。HZB是一个完整的Mip链，第0级为原始深度图，每个后续Mip为前一级的2×2最大深度值取max（保守性），典型分辨率从1080p深度图降采样至1×1约需10~11级Mip。

**第二遍（Late Pass）**：将第一遍中被剔除的物体，再次用当前帧的最新HZB进行测试，通过测试的"新可见物体"追加绘制。这样处理的目的是避免因使用上一帧数据导致的错误剔除（尤其是快速移动摄像机时），保证当帧画面正确性，代价是两次Dispatch开销，通常总计增加约0.2~0.8ms。

### Instance Compaction与DrawCall合并

GPU剔除的输出通常是一个稀疏的可见实例索引列表，需要通过**波前前缀和（Prefix Sum / Wave Scan）**将其压缩（Compaction）为连续的DrawCall参数Buffer。HLSL SM6.0引入的`WavePrefixCountBits()`内置函数可在单个Wave（通常32或64个线程）内完成局部前缀和，多Wave间通过原子操作（`InterlockedAdd`）完成全局计数。这一步决定了最终`ExecuteIndirect`所需的`DrawIndexedInstancedArguments`缓冲区的内容，每条记录为5个UINT（IndexCountPerInstance, InstanceCount, StartIndexLocation, BaseVertexLocation, StartInstanceLocation）。

---

## 实际应用

**UE5 GPU Scene与Nanite前身**：虚幻引擎4.26引入的GPU Scene功能，即将每个Primitive的变换矩阵和包围盒维护在GPU端，配合`FParallelMeshDrawCommandPass`中的Compute Shader剔除，使得实例化渲染的剔除完全在GPU上完成。这是Nanite可见性管线的前期技术积累。

**Unity HDRP的GPU Occlusion**：Unity 2022 LTS的HDRP中，`GPU Resident Drawer`功能将场景中符合条件的Renderer持久存储在GPU上，每帧通过名为`OcclusionCulling.compute`的Shader进行两遍式剔除。其HZB构建采用CS Shader以`8×8`线程组降采样深度，相比传统的像素着色器降采样减少约40%的带宽消耗。

**移动端GPU剔除的折中方案**：移动端（如Adreno 740、Mali-G715）虽支持Compute Shader，但`ExecuteIndirect`等价API（OpenGL ES无原生支持，需Vulkan）的适配成本较高。常见做法是GPU完成剔除、结果回读到CPU、由CPU发出DrawCall，回读引入约1~2帧延迟，可见性判断精度略有下降，但相比纯CPU剔除仍可节省约60%的CPU剔除时间。

---

## 常见误区

**误区一：认为GPU剔除可以完全替代LOD系统**。GPU剔除仅判断物体"是否绘制"，不改变绘制时的几何复杂度。一个通过剔除测试的高面数Mesh仍会提交所有三角形进入光栅化阶段。正确做法是GPU剔除与GPU LOD选择同时进行——在同一个Compute Pass中，根据物体到相机的距离`d`和屏幕投影面积阈值，写入对应LOD级别的IndexBuffer偏移，两者结合才能真正控制渲染负载。

**误区二：认为GPU剔除对所有场景都有收益**。当场景物体数量少于约500个时，Dispatch Compute Shader的固定开销（约0.05~0.15ms）加上Buffer同步屏障（Pipeline Barrier）的代价，可能超过剔除本身节省的时间。GPU剔除的收益临界点通常在1000~3000个独立DrawCall以上，小型室内场景使用CPU剔除效率更高。

**误区三：以为使用上一帧HZB不会产生错误剔除**。当摄像机快速旋转或场景物体高速移动时，上一帧HZB中某区域的遮挡关系在当前帧已不成立，可能错误剔除本帧实际可见的物体（Ghost Culling）。这正是两遍式方案中Late Pass存在的根本原因——第一遍可以错误剔除，第二遍必须用当帧深度图修正，代价是部分物体产生一帧闪烁，实践中需要在剔除激进度和鬼影风险之间设置保守性系数（通常让包围盒膨胀2%~5%）。

---

## 知识关联

GPU剔除以**遮挡剔除**为前提知识：传统CPU端遮挡剔除（如软件光栅化遮挡体、硬件遮挡查询`GL_SAMPLES_PASSED`）建立了HZB和包围体可见性判断的核心概念，GPU剔除本质上是将这套判断逻辑的执行位置从CPU搬移到GPU Compute Shader，并借助Indirect Draw完成输出。理解CPU遮挡剔除中"保守性测试"和"时间一致性假设"的含义，是正确配置GPU剔除保守性参数的基础。

从渲染管线演进角度，GPU剔除是**GPU Driven Rendering**（GPU驱动渲染管线）的核心子系统，向上支撑Bindless渲染、Meshlet可见性管线（如DirectX 12 Mesh Shader中的Amplification Shader阶段，其本质即逐Meshlet的GPU剔除）和虚拟几何体技术（Nanite）。掌握GPU剔除中的Indirect Draw参数格式、HZB构建方法和Prefix Sum Compaction算法，是进入GPU Driven Rendering领域的必要技术储备。