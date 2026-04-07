---
id: "anim-physics-perf"
concept: "物理动画优化"
domain: "animation"
subdomain: "physics-animation"
subdomain_name: "物理动画"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 物理动画优化

## 概述

物理动画优化是指在游戏引擎或动画系统中，通过降低物理模拟的计算精度、简化碰撞几何体或动态调整模拟细节级别，使物理动画在可接受的视觉质量下维持稳定帧率的一套技术策略。物理模拟（尤其是布料与布娃娃）的计算复杂度通常以 O(n²) 或更高量级增长，一件带有 500 个约束节点的布料在每帧可能需要迭代求解 8–10 次，单帧 CPU 耗时轻易超过 2ms，在同屏存在多个角色时会造成明显卡顿。

该领域的系统性方法最早随 Havok Physics（2000年商用化）和 PhysX（2006年被 NVIDIA 收购后普及）的广泛采用而逐步成型。这两个中间件都在其 SDK 中引入了物理对象的层级细节（Physics LOD）概念，允许开发者为同一个角色配置多套碰撞代理，随摄像机距离切换。早期主机游戏（如 PS3 时代）因 SPU 资源极为有限，物理优化甚至决定了一个场景能容纳的可交互角色上限。

理解物理动画优化的必要性在于：不加控制的物理模拟会打破"16.6ms/帧（60fps）"或"33.3ms/帧（30fps）"的帧预算。与渲染优化不同，物理计算绝大部分在 CPU 上串行执行（布娃娃约束求解、布料 PBD 迭代均如此），因此其瓶颈无法靠 GPU 硬件升级直接缓解，必须在算法和数据层面主动干预。

---

## 核心原理

### 物理 LOD（Level of Detail）

物理 LOD 是将渲染领域的 LOD 思想直接移植到物理模拟粒度上。具体做法是为同一角色或物体定义 3–4 套物理表示，根据到摄像机的距离或屏幕占比切换：

- **LOD0（近距离，≤5m）**：完整布娃娃（全部 20+ 个刚体骨骼关节）+ 高分辨率布料（256+ 粒子）；
- **LOD1（中距离，5–15m）**：简化布娃娃（仅保留脊椎、上臂、大腿等 8 个关键骨骼关节）+ 低分辨率布料（64 粒子）；
- **LOD2（远距离，>15m）**：完全禁用物理模拟，改用预烘焙动画或固定姿态插值；
- **LOD3（超远或不可见）**：冻结（Sleep）物理对象，不消耗任何模拟时间。

Unreal Engine 5 中通过 `USkeletalMeshComponent::SetPhysicsLOD()` 及 `RigidBody AnimNode` 的 `LOD Threshold` 参数实现上述切换，开发者可在 AnimGraph 中直接配置每个 LOD 层级的求解器迭代次数（默认 LOD0 为 8 次，LOD1 为 4 次）。

### 简化碰撞几何体（Simplified Collision Proxy）

物理引擎对碰撞检测的实际计算对象并非渲染网格，而是专门构建的**碰撞代理（Collision Proxy）**。碰撞代理的复杂度直接影响每帧的碰撞对检测（Broad Phase + Narrow Phase）耗时。常见简化策略包括：

1. **凸包分解（Convex Decomposition）**：将角色的手臂、腿部等肢体用 1–2 个凸包近似，单个凸包的三角面数通常控制在 32 面以内（PhysX 的 `PxConvexMeshDesc` 默认上限为 256 面，但实践中超过 64 面便会使 Narrow Phase 耗时翻倍）；
2. **胶囊体替代（Capsule Substitution）**：绝大多数人形角色的四肢可用胶囊体（Capsule）替代，胶囊体与胶囊体之间的碰撞检测仅需解析一个二次方程，远比多边形碰撞快；
3. **层级包围盒（BVH Pruning）**：对场景中静态碰撞体构建 BVH 树，布娃娃碰撞检测时先做 AABB 剔除，将参与 Narrow Phase 的候选对数从 O(n²) 降至 O(n log n)。

### 求解器参数调优

物理模拟的核心是约束求解器，其精度由**迭代次数（Solver Iterations）**和**子步数（Substeps）**控制。以 PBD（Position Based Dynamics，布料常用）为例：

- 迭代次数 k 越高，布料的刚度和稳定性越好，但耗时线性增加，k=8 相比 k=4 耗时翻倍；
- 子步数 s 控制每帧内将物理时间步切成几段积分，s=2 比 s=1 稳定，但耗时×2；
- 实践经验：对屏幕占比低于 10% 的角色，将 k 从 8 降至 2、s 从 2 降至 1，通常视觉差异可忽略，但 CPU 节省可达 75%。

布娃娃的刚体约束（Articulation）求解器在 PhysX 5.x 中引入了 **TGS（Temporal Gauss-Seidel）**求解器，相比旧版 PGS 在相同迭代次数下稳定性提升约 30%，允许在不增加迭代次数的前提下改善关节抖动，间接达到优化效果。

### 异步物理与时间预算控制

将物理模拟移至**异步线程**执行是现代引擎的通行方案。Unreal Engine 的 `p.AsyncPhysicsTickEnabled=1` 开关启用后，物理更新与游戏线程并行，物理帧率可独立于渲染帧率（例如渲染 60fps 而物理固定 30fps）。此外，可为物理模拟设置**时间预算上限**（如 3ms），超出时自动降级：优先冻结屏幕边缘或被遮挡的物理对象，确保玩家视野内的核心角色获得足够的模拟资源。

---

## 实际应用

**《Horizon Zero Dawn》的机器人布娃娃优化**：游戏中倒地的机器人敌人全部启用了布娃娃物理，但开发团队将同屏激活布娃娃数量硬性限制为最多 **8 个**，第 9 个及之后的倒地敌人直接播放预录制的"假布娃娃"动画。每个活跃布娃娃在距离玩家 12m 以上时自动切换到仅保留 6 个骨骼关节的简化版本。

**《GTA V》的布料系统**：Rockstar 为 NPC 衣物设定了严格的布料粒子预算——主角衣物最多 128 粒子，路人 NPC 最多 32 粒子，且路人距离玩家超过 20m 后布料物理全部冻结，改用最后一帧的姿态做静态贴图混合。

**Unity DOTS Physics 的批处理优化**：在 Data-Oriented Technology Stack 中，物理组件以 SoA（Structure of Arrays）内存布局存储，使 Broad Phase AABB 检测能充分利用 SIMD 指令（AVX2 一次处理 8 对 AABB），相比传统 AoS 布局吞吐量提升约 4 倍。

---

## 常见误区

**误区一：认为禁用碰撞响应等同于禁用物理模拟**。将布娃娃骨骼的碰撞通道设为"No Collision"只是阻止了与其他对象产生碰撞事件，但刚体约束的积分计算仍在每帧执行，CPU 消耗并未减少。真正节省计算的方式是调用物理引擎的 `SetSimulatePhysics(false)` 或将对象置入 Sleep 状态，后者要求线速度和角速度均低于阈值（PhysX 默认 `sleepThreshold = 0.005`）才会自动触发。

**误区二：简化碰撞代理一定会造成穿模**。穿模的根本原因是物理步长过大（dt 过大导致高速物体"穿越"碰撞体），而非碰撞体本身的精度不足。将手臂碰撞体从 64 面凸包简化为胶囊体，在正确的子步设置（s≥2）下穿模概率不升反降，因为胶囊体的 Narrow Phase 计算更快，允许在相同帧预算内执行更多子步。

**误区三：物理 LOD 切换会产生明显跳变**。若直接在某帧瞬间将布娃娃从 20 骨骼关节切换到 6 骨骼关节，确实会产生跳变。正确做法是在切换时将高精度模拟结果**融合（Blend）**回动画骨骼 0.2–0.5 秒后再激活低精度版本，或在切换帧对物理关节施加阻尼（Damping 临时增大到 0.95）使其快速收敛到中性姿态，再接管低精度模拟。

---

## 知识关联

物理动画优化建立在对**布料模拟**和**布娃娃系统**工作原理的掌握之上：只有清楚布料的 PBD 