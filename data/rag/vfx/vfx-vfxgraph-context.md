---
id: "vfx-vfxgraph-context"
concept: "Context系统"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Context系统

## 概述

Context系统是Unity VFX Graph中用于组织粒子生命周期逻辑的核心执行框架。VFX Graph将粒子的完整生命周期划分为三个独立的执行阶段，每个阶段对应一个称为"Context"的容器节点，分别是**Initialize Particle**、**Update Particle**和**Output Particle**。这三个Context在图形编辑器中以竖向堆叠的方式排列，通过垂直流（Vertical Flow）箭头连接，形成一条完整的粒子处理管线。

Context系统的设计源于GPU计算着色器的执行模型。自Unity 2018.3版本引入VFX Graph以来，Context节点就承担着将高层逻辑映射到底层Compute Shader Dispatch调用的职责。每个Context在运行时会生成一次独立的GPU调度（Dispatch），意味着三大Context = 三次GPU Compute Pass，这一执行方式使粒子运算完全绕过CPU，实现百万级粒子的实时模拟。

理解Context系统的根本价值在于：它明确规定了"哪类操作只能在哪个阶段执行"。例如，设置粒子初始颜色必须在Initialize中完成，而每帧的物理积分运算则只能发生在Update中。违反这一阶段约束会导致逻辑错误或编译失败，因此Context是VFX Graph图表结构的基础骨架。

## 核心原理

### Initialize Particle Context

Initialize Particle在每个粒子被**首次生成**时执行且仅执行一次。它从上游的Spawn Context接收新生粒子的数量信号，并为每一个新粒子设置初始属性值，包括Position、Velocity、Color、Lifetime等。此Context写入的属性值会被存储到GPU粒子缓冲区（Particle Buffer）中，作为该粒子整个生命期的"出生状态"。

Initialize中有一个关键概念：**Capacity（容量）**。开发者必须在Initialize Context的检视面板中手动设定粒子池的最大容量（如65536个），VFX Graph会在运行时预先在GPU上分配这一数量的粒子数据槽位。Capacity一旦耗尽，新粒子将无法生成，直到旧粒子死亡释放槽位。这与CPU粒子系统的动态分配策略完全不同。

### Update Particle Context

Update Particle在**每一帧**对所有当前存活的粒子执行一次。此阶段承担所有随时间变化的运算，例如通过欧拉积分公式 `Position += Velocity × deltaTime` 更新位置，或通过 `Age += deltaTime` 累计粒子年龄。当粒子的Age超过其Lifetime时，Update阶段负责将该粒子标记为"死亡"并从缓冲区中回收。

Update Context还是接入外部力场（Force Fields）、碰撞检测（Collision）以及噪声扰动的指定位置。值得注意的是，Update是**可选的**——如果粒子生成后完全静止不需要逐帧更新，可以删除Update Context以节省一次GPU Dispatch开销，直接从Initialize连接到Output。

### Output Particle Context

Output Particle Context负责定义粒子的**渲染方式**，而非模拟逻辑。此Context并不修改粒子的模拟数据，而是读取粒子缓冲区中的属性，决定如何将每个粒子绘制到屏幕上。VFX Graph提供了多种Output类型，包括Output Particle Quad（公告板四边形）、Output Particle Mesh（网格粒子）、Output Particle Strip（条带拖尾）等，每种类型对应不同的顶点着色器配置。

一个VFX Graph资产可以包含**多个Output Context**并行存在，它们各自读取同一批粒子数据但以不同方式渲染，例如同时输出一个Quad层和一个发光Mesh层来构建复杂视觉效果。Output Context上方还暴露了混合模式（Blend Mode）、排序优先级（Sorting Priority）等渲染状态设置，这些参数直接影响最终的渲染Pass。

### Vertical Flow与数据流向

三大Context通过Vertical Flow（垂直数据流）严格按照 Initialize → Update → Output 的顺序连接。粒子属性（Attribute）通过这条垂直流在Context之间传递，但属性的写入权限受到阶段限制：Initialize和Update均可写入粒子属性，而Output Context对粒子缓冲区是**只读**的，任何试图在Output中写入Position等属性的操作都会被编辑器拒绝。

## 实际应用

**烟雾效果制作**：在Initialize Context中用"Set Lifetime Random"Block设置粒子寿命为2到5秒之间随机值，用"Set Size"设初始大小为0.1米；在Update Context中添加"Turbulence"Block产生噪声扰动，并用"Scale over Lifetime"让粒子在死亡前膨胀至0.8米；最后在Output Particle Quad中选择Additive混合模式并指定烟雾贴图。这三个Context的分工使烟雾逻辑清晰可维护。

**多阶段特效分离**：一个爆炸特效可以建立两套独立的Context链——第一套处理火花粒子（寿命0.3秒，Output为Quad），第二套处理碎片粒子（寿命1.5秒，Output为Mesh）。两套Context链共享同一个Spawn Context的触发信号，但彼此的Capacity、Update逻辑和渲染方式完全隔离，互不干扰。

## 常见误区

**误区一：认为Update Context是必须存在的**。许多初学者默认每个VFX Graph都需要完整的三段式Context链。实际上，对于纯静态的粒子效果（如固定位置的符文光点），完全可以省略Update Context，将Initialize直接连接到Output，减少一次每帧的GPU Dispatch开销，在移动平台上尤其有性能意义。

**误区二：在Output Context中尝试修改粒子运动**。由于Output是只读阶段，有开发者在Output中添加"Add Velocity"类Block，期望在渲染时偏移粒子，结果发现Block显示为红色报错。正确做法是将运动修改逻辑移入Update Context，Output只负责视觉表现参数如颜色映射或UV动画。

**误区三：混淆Capacity和每帧生成数量**。Capacity设置的是整个粒子池的**上限槽位总数**，而Spawn Context中的"Rate"参数控制**每秒生成速率**。将Capacity设为100但Rate设为200/秒，并不会每帧生成200个粒子，而是在约0.5秒内填满粒子池后停止新增，直到旧粒子死亡释放槽位。

## 知识关联

学习Context系统需要已掌握VFX Graph概述中的基本图形编辑界面操作，特别是如何在图表中创建和删除节点，以及理解Spawn Context如何向Initialize Context发送生成信号。没有这一基础，将无法理解Initialize为何只在特定时机触发。

Context系统是后续学习**Block与节点**的直接前提。Block是填充在Context内部的具体运算单元，每一个Block都有其合法的宿主Context范围——例如"Set Position Shape: Sphere"只能置于Initialize或Update中，"Set Color over Life"只能置于Output中。理解了三大Context的职责边界，才能判断某个Block应当放置在哪个Context内，以及为何VFX Graph编辑器会对放错位置的Block报错。此外，进阶学习GPU Event Context和Subgraph时，也需要以三大标准Context的执行模型为参照基准。