---
id: "vfx-niagara-sim-stage"
concept: "Simulation Stage"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 53.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.5
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 模拟阶段（Simulation Stage）

## 概述

模拟阶段（Simulation Stage）是Niagara粒子系统中一种允许开发者在单帧内对粒子数据执行多次GPU计算Pass的机制。与标准的粒子更新（Particle Update）模块不同，模拟阶段可以在粒子缓冲区（Particle Buffer）上反复迭代，每次Pass的输出可以作为下一次Pass的输入，从而实现传统单Pass更新无法完成的复杂粒子行为。

这一功能最早在虚幻引擎4.25版本中随着Niagara的GPU模拟能力增强而正式引入。其设计动机源自流体模拟与粒子约束求解的需求——例如Position-Based Dynamics（PBD）算法要求在一帧内对粒子位置约束进行多次迭代求解（通常需要4到16次迭代才能收敛），单Pass的粒子更新完全无法满足这一要求。

模拟阶段的意义在于它将GPU计算着色器（Compute Shader）的多Pass调度能力暴露给了Niagara的可视化脚本系统，使技术美术师无需手写HLSL代码即可实现粒子弹簧约束、SPH流体压力求解、热传导模拟等算法。启用模拟阶段的Niagara系统必须运行在GPU模拟模式下，CPU模拟模式不支持此特性。

## 核心原理

### 迭代计数与粒子缓冲区双缓冲

每个模拟阶段节点（Simulation Stage Node）上有一个关键属性`Num Iterations`，用于指定该阶段在单帧内执行的完整Pass次数。引擎在每次迭代时，将整个粒子缓冲区作为Dispatch目标，线程数等于活跃粒子数量。为避免读写竞争，Niagara对粒子属性缓冲区采用Ping-Pong双缓冲策略：奇数Pass从Buffer A读取、写入Buffer B，偶数Pass从Buffer B读取、写入Buffer A，迭代完成后最终结果缓冲区被用于渲染。

### 数据接口与迭代索引

在模拟阶段内部，可以通过`Engine.Owner.SimulationStageIterationIndex`变量获取当前迭代的编号（从0开始计数）。这个变量对于实现松弛（Relaxation）系数的动态调整至关重要，例如在PBD求解中，前几次迭代使用较大步长快速收敛，后几次迭代使用较小步长精细修正。此外，`Engine.Owner.SimulationStageNormalizedIterationIndex`提供归一化的[0,1]范围迭代进度值，便于在插值计算中使用。

### 邻域数据接口的协同工作

模拟阶段本身仅提供迭代调度框架，要实现粒子间的相互作用（如碰撞检测、弹簧约束），必须配合Grid2D Collection或Neighbor Grid3D等数据接口使用。典型工作流为：第一个模拟阶段负责将粒子位置写入网格结构；第二个模拟阶段从网格中查询邻域粒子并计算约束力；第三个模拟阶段应用速度积分。这三个阶段在Niagara系统图中以链式顺序排列，均在GPU粒子更新阶段之后执行。

### 源类型与粒子子集迭代

`Iteration Source`属性控制每次迭代的线程分配方式，有三个选项：`Particles`（每个活跃粒子一个线程，最常用）、`Data Interface`（线程数由外部数据接口决定，如Grid2D的单元格数量）和`Direct Count`（手动指定固定线程数）。当设置为`Data Interface`并绑定Grid2D Collection时，每个线程对应一个网格单元而非一个粒子，这使得模拟阶段可以用于驱动网格场的独立计算，粒子只是从网格中采样数据。

## 实际应用

**布料模拟约束求解**：在Niagara布料特效中，将粒子视为布料顶点，粒子间弹簧约束通过模拟阶段以`Num Iterations = 8`进行PBD求解。每次迭代读取粒子当前位置，计算与相邻粒子的距离，若距离偏离静止长度则施加位置修正量，8次迭代后布料看起来具有真实的弹性形变而不会穿透。

**SPH粒子流体**：液体特效中的SPH（Smoothed Particle Hydrodynamics）算法要求分为密度计算和压力梯度计算两个独立Pass。第一个模拟阶段（Iteration Source = Particles）计算每个粒子的局部密度`ρ_i = Σ m_j · W(r_ij, h)`，结果写入自定义粒子属性`Density`；第二个模拟阶段读取`Density`属性，计算压力加速度并更新粒子速度。两个模拟阶段的分离确保了密度场在计算压力时是完全同步的全局快照。

**GPU粒子排序前处理**：在需要半透明粒子正确排序的场景中，可以用一个`Iteration Source = Direct Count`且迭代次数为1的模拟阶段，执行并行归约（Parallel Reduction）来计算所有粒子的深度范围，为后续排序Pass提供归一化参数。

## 常见误区

**误区一：认为Num Iterations越高效果越好**。提高迭代次数会线性增加GPU计算时间，在Adreno 640或Mali-G78等移动端GPU上，单系统超过4次迭代的模拟阶段很容易导致帧率跌破30fps。实际开发中应对目标平台进行GPU Profiling，在Unreal Insights的GPU轨道中观察`NiagaraSimStage`事件的耗时，而不是盲目堆砌迭代次数。

**误区二：混淆模拟阶段与粒子更新模块的执行顺序**。模拟阶段节点在Niagara图中的位置决定其是在标准粒子更新（Particle Update）之前还是之后执行。若将约束求解阶段放置在粒子更新之前，则物理模块（如Drag、Gravity）计算的速度变化还未应用于位置，约束求解将基于上一帧的旧位置数据，产生一帧的时序误差，表现为约束力抖动。

**误区三：认为模拟阶段可以在CPU模拟模式下降级运行**。CPU模拟模式的粒子更新是在工作线程上以串行方式逐模块执行的，没有Compute Shader调度机制，因此模拟阶段在CPU模式下会被完全跳过且不报错，导致特效行为与预期完全不符。必须在Niagara系统属性中将`Fixed Bounds`和`GPU Sim Debug`同时检查，并将模拟目标显式锁定为`GPU Compute Sim`。

## 知识关联

模拟阶段的使用以GPU模拟（GPU Simulation）为前提——粒子系统必须运行在`GPU Compute Sim`模式，且项目设置中须开启`Support Compute Skin Cache`以保证Compute Shader的正常调度。理解GPU模拟的双缓冲机制、粒子属性在显存中的布局（结构化缓冲区SRV/UAV的绑定关系）是正确使用模拟阶段的技术基础。

在掌握模拟阶段的迭代调度原理之后，邻域网格（Neighbor Grid3D）的学习将变得自然——邻域网格本质上是为模拟阶段的粒子间查询提供空间加速结构的数据接口，两者在SPH和PBD算法中形成标准的三阶段工作流：写入网格→迭代查询→积分更新。邻域网格的分辨率参数`Grid Resolution`直接影响模拟阶段每次Dispatch的线程访问模式，理解模拟阶段的线程-粒子映射关系是正确配置邻域网格Cell Size的必要条件。