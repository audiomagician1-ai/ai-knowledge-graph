---
id: "vfx-niagara-neighbor-grid"
concept: "邻域网格"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 邻域网格

## 概述

邻域网格（Neighbor Grid 3D）是Niagara粒子系统中用于实现粒子间空间交互的数据结构模块，其本质是将三维空间划分为规则的网格单元，使每个粒子能够高效查询其周围邻近粒子的属性与位置。与逐对遍历（O(n²)复杂度）相比，邻域网格将空间查询的平均复杂度降低至O(n·k)，其中k为每个网格单元平均容纳的粒子数量，在粒子数量超过几百个时性能优势极为显著。

该模块在UE4.26版本随Niagara正式进入生产就绪状态时得到完善，并在UE5中进一步整合到Simulation Stage工作流程中。邻域网格的设计思路借鉴了计算流体力学（CFD）中的空间哈希（Spatial Hashing）技术，将连续空间离散化后存储粒子索引，从而在GPU上并行执行大规模粒子交互计算。

邻域网格的核心价值在于支持群体模拟、碰撞响应、流体模拟等需要粒子感知彼此存在的特效场景。没有它，Boids鸟群算法、SPH流体压力计算、粒子间排斥力等效果要么不可实现，要么计算开销高到无法实时运行。

## 核心原理

### 网格划分与分辨率参数

邻域网格通过三个参数定义空间分割精度：**World Cell Size**（世界单元大小）、**Grid Resolution**（网格分辨率，即X/Y/Z三轴的单元数量）以及**Maximum Neighbor Count**（最大邻居数量，默认值通常设为8或16）。World Cell Size直接决定查询半径的有效范围——一个粒子只能感知到同一单元或相邻26个单元内的粒子（三维中的Moore邻域）。若World Cell Size设为50UE单位，则粒子的有效感知半径上限约为50×√3 ≈ 86.6单位。

### 写入阶段：Neighbor Grid 3D Set

在Simulation Stage的**写入迭代（Write Pass）**中，每个粒子执行`Neighbor Grid 3D Set Cell/Attribute`节点，将自身的粒子ID写入对应网格单元。此阶段的关键公式为单元索引计算：

```
Cell Index = floor((ParticlePosition - GridOrigin) / WorldCellSize)
```

写入时会发生**原子竞争写入（Atomic Write）**，GPU上多个粒子可能同时尝试写入同一单元，因此Maximum Neighbor Count限制了每个单元能存储的粒子ID上限，超出部分会被丢弃。这意味着粒子密度不应超过每单元预设容量，否则产生查询丢失。

### 读取阶段：Neighbor Grid 3D Get与邻居遍历

在**读取迭代（Read Pass）**中，粒子通过`Neighbor Grid 3D Get Neighbor`节点遍历周围单元中存储的粒子ID，再用这些ID通过`Direct Read`方式读取目标粒子的位置、速度等属性。标准遍历模式是嵌套循环遍历当前单元及相邻单元（最多27个单元 × Maximum Neighbor Count次查询），因此Maximum Neighbor Count的值直接影响GPU线程的循环次数和性能开销。实际项目中此值通常控制在4~32之间以平衡精度与性能。

### GPU执行依赖与Simulation Stage绑定

邻域网格**必须在Simulation Stage内使用**，无法在普通的Particle Update模块中直接访问，原因是Simulation Stage提供了有序的多Pass执行保证——写入Pass必须在读取Pass之前完成，避免同一帧内读写数据竞争。Niagara在内部通过`SimStage`执行顺序标签确保这一依赖关系，用户需在Emitter的Simulation Stage设置中手动将写入模块的执行顺序排在读取模块之前。

## 实际应用

**Boids群体行为模拟**：实现鸟群/鱼群效果时，每帧先将所有粒子位置写入邻域网格，再在读取Pass中查询每个粒子的邻居，分别计算分离力（Separation）、对齐力（Alignment）、聚合力（Cohesion）三个向量并加权叠加到粒子速度上。整个系统可流畅运行10000+粒子，而不使用邻域网格时500个粒子的逐对计算已造成明显帧率下降。

**SPH流体表面张力**：在粒子化流体模拟中，压力计算需要对每个粒子求解Müller等人2003年提出的SPH核函数：`W(r, h) = 315/(64πh⁹) × (h²-|r|²)³`，其中h为平滑长度，对应邻域网格的World Cell Size。邻域网格确保只对核函数支持域内的粒子进行积分，大幅减少无效计算。

**粒子间碰撞与排斥**：角色周围的魔法护盾粒子效果中，粒子需要相互排斥以形成均匀分布，通过邻域网格查询距离小于阈值的邻居粒子，施加反向排斥力，可实现自组织的粒子壳层效果，粒子数量在2000~5000时实时性能表现良好。

## 常见误区

**误区一：World Cell Size越小精度越高**。缩小单元尺寸会导致每个粒子能查询到的邻居减少，当粒子间距超过单元尺寸时，相邻粒子反而落入不同单元无法互相感知。正确做法是将World Cell Size设为期望感知半径的0.8~1.2倍，而非追求最小值。

**误区二：可以在同一Pass中同时读写邻域网格**。部分开发者尝试在单个Simulation Stage模块中同时执行写入和查询操作，这会导致读取到的数据是当前帧未完成写入的脏数据，产生一帧延迟或错误的邻居信息。写入和读取必须分属两个独立的Simulation Stage迭代，且写入Stage的Source设为`Particles`而读取Stage同样设为`Particles`但执行顺序在后。

**误区三：Maximum Neighbor Count可以无限增大以提升准确性**。该参数的实际上限受GPU显存和每线程寄存器数量约束，盲目设为64或128会导致着色器寄存器溢出（Shader Register Spill），反而造成性能骤降而非线性下降。UE官方文档建议在多数场景中将此值保持在16以内。

## 知识关联

邻域网格直接依赖**Simulation Stage**才能工作，理解多Pass执行模型、迭代源（Iteration Source）设置和数据依赖顺序是正确配置邻域网格的前提。Simulation Stage的写入/读取分离概念在邻域网格中得到最典型的体现。

掌握邻域网格后，**音频可视化**作为后续应用方向，可以将音频频谱数据写入类似的网格结构（Audio Data Interface），驱动粒子根据空间位置响应不同频率的音频能量，这种将外部数据映射到空间查询结构的思维方式与邻域网格的空间索引哲学一脉相承。此外，邻域网格也是实现Niagara中GPU粒子与CPU粒子混合交互的桥梁——CPU侧粒子写入网格后，GPU粒子同样可以查询到这些数据，实现跨执行模式的粒子通信。