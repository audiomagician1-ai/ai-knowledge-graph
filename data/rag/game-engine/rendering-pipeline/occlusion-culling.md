---
id: "occlusion-culling"
concept: "遮挡剔除"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
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

# 遮挡剔除

## 概述

遮挡剔除（Occlusion Culling）是渲染管线中的一项优化技术，其核心目标是在将几何体提交给GPU光栅化之前，提前判断哪些物体被其他物体完全遮挡，从而跳过这些不可见物体的绘制调用。与视锥剔除（Frustum Culling）不同，遮挡剔除处理的是"在视锥内部但被遮挡"的物体，这类物体在密集场景（如城市街道、室内关卡）中可能占总物体数量的60%以上。

遮挡剔除的概念最早在20世纪90年代随实时3D游戏的兴起而被系统研究。1997年，Tomas Akenine-Möller等人发表的相关论文奠定了硬件遮挡查询（Hardware Occlusion Query）的理论基础。2001年前后，随着DirectX 9和OpenGL扩展的支持，GPU层面的`GL_ARB_occlusion_query`接口正式进入主流引擎工具链。现代引擎如Unreal Engine 5和Unity HDRP均内置了多种遮挡剔除策略，但其选择与配置对性能表现影响极大。

遮挡剔除的价值在于削减**Draw Call数量**和**顶点处理开销**。一个城市场景中可能包含数万个建筑构件，但玩家在街道视角下实际可见的不超过总量的20%。若不进行剔除，GPU需要处理大量永远不会出现在帧缓冲中的片元，造成显著的带宽和计算浪费。

---

## 核心原理

### GPU遮挡查询（Hardware Occlusion Query）

GPU遮挡查询是最基础的硬件实现方式。其流程是：先渲染遮挡体（Occluder，通常是简化的包围盒），然后通过`glBeginQuery(GL_SAMPLES_PASSED, id)`与`glEndQuery`指令查询该区域通过深度测试的像素数量。若返回值为0，则认定该物体完全被遮挡，跳过其完整几何体的渲染。

然而，GPU查询存在严重的**CPU-GPU同步延迟**问题。由于GPU是异步执行的，CPU必须等待查询结果回读（`glGetQueryObjectiv`），这会导致流水线停顿，反而抵消剔除带来的收益。主流解决方案是使用**延迟查询（Conditional Rendering）**，即将上一帧的查询结果用于本帧的剔除决策，容忍一帧的误判误差。

### Hi-Z遮挡剔除（Hierarchical Z-Buffer）

Hi-Z是目前GPU驱动遮挡剔除中最主流的方案。其原理是在生成深度缓冲后，对其进行**多级Mipmap降采样**，每一级存储对应区域的**最大深度值（保守深度）**。对某一物体进行可见性测试时，取其包围盒在屏幕空间的投影范围，在对应层级的Hi-Z图中采样最大深度值 $Z_{max}$，若物体包围盒的最近深度 $Z_{obj}$ 满足：

$$Z_{obj} > Z_{max}$$

则该物体完全位于已知遮挡物之后，可安全剔除。这个测试完全在GPU Compute Shader中并行完成，避免了CPU-GPU回读的延迟。Unreal Engine的GPU Scene剔除系统（从UE5.0起正式启用）正是基于Hi-Z Compute pass实现每帧对数十万实例的剔除。

Hi-Z的局限性在于其**保守性（Conservative）**：它只能判定"一定不可见"，无法精确判定"一定可见"，存在假阳性（False Negative for culling），即部分被遮挡物体可能因采样精度问题被错误保留。

### Software Occlusion Culling（软件遮挡剔除）

Software Occlusion Culling完全在CPU端完成遮挡判定，代表实现是Intel在2014年开源的**Masked Software Occlusion Culling (MSOC)** 库，以及Epic在Unreal Engine中的Software Rasterizer。

其核心是在CPU上维护一张低分辨率（通常为256×128或512×256）的**软件深度缓冲**，利用SIMD指令（如AVX2）对遮挡体进行快速软件光栅化，然后对被测物体的包围盒执行深度比较。由于整个流程在CPU内存中进行，无需等待GPU回读，延迟为零。Intel的MSOC测试数据显示，在一个包含约10,000个三角形遮挡体的场景中，CPU端剔除耗时可控制在**0.5ms以内**（使用AVX2优化）。

Unity的Umbra遮挡系统（在Unity 5之前的版本中广泛使用）则采用了**离线预计算**的方式：在烘焙阶段将场景划分为PVS（Potentially Visible Set）单元格，运行时直接查表而非实时计算，以离线时间换取运行时零开销，但代价是无法处理动态遮挡物。

---

## 实际应用

**室内场景（Portal Culling的前身）**：在《毁灭战士（Doom，1993）**中，id Software使用BSP树实现了早期的可见性剔除，本质是一种空间划分驱动的遮挡剔除。现代第一人称射击游戏的室内关卡设计中，美术师会刻意放置"遮挡物件（Occlusion Volumes）"——即引擎编辑器中标记为纯遮挡体的不可见几何体，仅参与Hi-Z或软件光栅化计算而不产生实际渲染输出。

**大世界地形渲染**：在开放世界游戏中，地形的起伏本身构成天然遮挡物。Unreal Engine的Nanite虚拟几何体系统在其内部剔除阶段使用了两次Hi-Z pass：第一个pass用上一帧的Hi-Z快速剔除大量Cluster，第二个pass对通过第一次剔除的Cluster再次精确测试，这种"两阶段剔除（Two-Phase Occlusion Culling）"将错误剔除率降至接近零。

**动态物体处理**：对于角色、车辆等动态物体，离线PVS方案完全失效。此时引擎通常对动态物体单独使用GPU Occlusion Query或Hi-Z测试，并结合物体的运动速度设置查询更新频率——静止物体每帧查询，高速运动物体则降低频率以减少开销。

---

## 常见误区

**误区一：遮挡剔除总是提升性能**

遮挡剔除本身有成本。GPU遮挡查询的回读同步会引入流水线气泡（Pipeline Bubble），在Draw Call数量本来不多（如少于500个）的场景中，剔除的收益往往不足以覆盖查询的开销。Hi-Z pass需要额外的Compute Dispatch和内存带宽，对于空旷的户外场景（遮挡率低），开启Hi-Z剔除反而会增加约0.3-0.8ms的帧耗时。

**误区二：Hi-Z剔除是精确的**

Hi-Z使用的是保守最大深度，且包围盒本身是物体的保守近似，双重保守性导致实际剔除率远低于理论最大值。一个物体只有95%的像素被遮挡，但其包围盒投影区域包含5%的可见区域时，Hi-Z无法将其剔除。这种情况在薄型物体（如栅栏、植被）上尤为突出。

**误区三：软件遮挡剔除比硬件方案更慢**

MSOC等现代软件方案使用SIMD并行化，在CPU核心数充足时，对静态遮挡物的处理速度可以超过带回读的GPU查询。尤其是在主机平台（如PS5的x86-64架构支持AVX2等宽SIMD），软件遮挡剔除是许多AAA游戏的首选方案，因为它避免了CPU-GPU同步气泡并支持完全动态的遮挡物更新。

---

## 知识关联

学习遮挡剔除需要先理解**渲染管线概述**中的深度测试（Depth Test）机制——Hi-Z本质上是将逐像素的深度比较提升到物体粒度的批量比较，没有对深度缓冲工作原理的理解，很难把握Hi-Z层级构建的逻辑。同样，视锥剔除（Frustum Culling）是遮挡剔除的前置步骤，通常先做视锥剔除将视锥外物体排除，再对视锥内物体执行遮挡剔除，两者在引擎的剔除管线（Culling Pipeline）中串联执行。

遮挡剔除的效果与场景的**遮挡复杂度（Occlusion Complexity）**直接相关，而这又与关卡美术设计强耦合。美术师在设计大型关卡时，应有意识地利用建筑物、地形等大型遮挡物形成"遮挡屏障"，以最大化剔除率——这一实践在《地平线：零之曙光（Horizon Zero Dawn）》的GDC演讲（2017）中有详细披露，其遮挡剔除系统在开放世界场景中达到了每帧剔除约70%可渲染实例的效果。