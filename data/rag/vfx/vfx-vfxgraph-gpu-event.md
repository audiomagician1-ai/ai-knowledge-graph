---
id: "vfx-vfxgraph-gpu-event"
concept: "GPU事件"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# GPU事件

## 概述

GPU事件（GPU Event）是VFX Graph中一种允许粒子在GPU端直接触发子粒子生成的机制。与CPU事件不同，GPU事件的整个触发和生成流程完全发生在GPU内存中，不需要将数据回传CPU再重新发送，因此能在不造成显著性能瓶颈的前提下实现粒子级联（Particle Cascading）效果——即一个粒子"死亡"或满足特定条件时，在原位生成一批新粒子。

该机制在Unity VFX Graph 7.x版本（随Unity 2019.3正式发布）中引入，作为解决爆炸碎屑、烟花分裂、雨滴溅射等多层粒子效果的核心工具。在此之前，制作这类效果需要依赖多个独立粒子系统通过脚本协调，不仅逻辑复杂，且在粒子数量较多时CPU开销极大。GPU事件将这一协调逻辑完全迁移到GPU侧执行。

GPU事件的重要性在于它突破了传统GPU粒子系统"无状态传递"的限制。粒子的位置、速度、颜色、自定义属性等数据可以通过**Inherit Attribute**节点直接传递给子粒子，子粒子从父粒子的精确位置和状态出发，而不是从某个近似位置或全局起始点生成，这使得视觉上的连贯性和物理合理性远超传统多系统方案。

---

## 核心原理

### GPU事件的触发节点

VFX Graph中GPU事件通过两类专用节点触发：

- **GPUEvent OnDie**：当粒子的生命周期（Lifetime）归零时自动触发，最常用于爆炸、消散效果。
- **GPUEvent OnCollide**（需开启碰撞模块）：当粒子与深度缓冲或SDF碰撞时触发，常用于液滴落地溅射。

这两个节点输出一个`GPUEvent`类型的数据流，该数据流必须连接至独立的**Spawn Context**，这个Spawn Context的Spawn Mode必须设置为**GPU Event**（而非Constant Rate或Burst），否则连接不会生效。这与普通Output Context的连接方式有本质差异，初学者容易将两者混淆。

### 属性继承机制与Inherit Attribute节点

子粒子系统（通过GPU Event触发的Spawn Context所连接的Initialize Particle Context）默认不继承父粒子的任何属性。要让子粒子从父粒子的位置、速度等数据出发，必须在Initialize Particle Context中显式添加**Inherit Source Attribute**块（快捷方式：在Initialize Context的Block列表中点击`+`，选择`Attribute > Source > Get Source Attribute`）。

每个继承块只继承一个属性，常见的继承链如下：

```
父粒子 Position → 子粒子 Position（溅射起点）
父粒子 Velocity → 子粒子 Velocity（继承初速度方向）
父粒子 Color    → 子粒子 Color（颜色级联）
```

父粒子的任意**自定义属性（Custom Attribute）**，只要类型兼容，均可通过此机制传递。这是GPU事件比预制触发器强大得多的地方：整条粒子链上的语义信息（如"这是第几级爆炸"）可以编码进自定义浮点属性并逐级传递。

### 容量与性能约束

GPU事件生成的子粒子受其所在**Output Context对应粒子系统的Capacity（容量上限）**严格限制。Capacity值在VFX Graph中是静态编译时常量，单位为粒子个数。若父系统每帧有100个粒子死亡，每个粒子触发生成10个子粒子，子系统的Capacity至少需要设置为 `100 × 10 = 1000`，否则超出容量的粒子会被静默丢弃，不会报运行时错误，这是一个极难排查的bug来源。

GPU事件系统的内存结构使用**Append Buffer**（追加缓冲区），其容量固定分配在显存中。当事件触发速率超过子系统消耗速率时，缓冲区会溢出，因此对于生命周期极短的子粒子（如Lifetime < 0.1s的闪光），需要适当降低父粒子的触发频率或提高子系统Capacity。

---

## 实际应用

### 烟花三级爆炸

在烟花特效中，GPU事件可以实现三级级联：主弹体（Level 0）触发第一级星星粒子（Level 1，约50个），每个星星粒子死亡时触发闪烁微粒（Level 2，每颗3~5个）。整个效果约需 1 + 50 + 250 = 301 个粒子，但视觉密度等同于传统方案中数千个独立粒子。在VFX Graph中，只需两条GPU Event连接链即可实现，而无需任何C#脚本。

### 雨滴溅射（结合SDF交互）

当父粒子系统开启**Collide with Depth Buffer**模块后，雨滴粒子接触地面时触发**GPUEvent OnCollide**。子系统在碰撞点生成扁平圆形水花粒子，通过继承碰撞法线方向和碰撞点位置，水花的朝向与地面法线对齐。若地面使用了SDF网格（来自SDF交互前置知识），甚至可以将SDF梯度方向传递给子粒子，使水花贴合曲面法线方向扩散。

### 子弹击中特效

在TPS/FPS游戏特效中，子弹粒子命中表面时通过GPUEvent OnCollide触发三类子粒子：火花（高速短寿命）、烟雾（低速长寿命）、弹孔贴花（静止超长寿命）。三套子系统并联连接到同一个GPUEvent输出端口，实现一次碰撞同时触发多种视觉层。

---

## 常见误区

### 误区一：认为GPU事件会实时同步到CPU

GPU事件的整个生命周期发生在GPU侧，CPU**无法**在同一帧内读取"有多少个子粒子被触发"。若尝试通过`VFXEventAttribute`在脚本中监听GPU事件触发次数，将得到延迟一帧或根本获取不到数据的结果。如果确实需要CPU感知碰撞事件（如播放音效），必须改用CPU事件路径，代价是每帧显存→内存的数据回读开销。

### 误区二：子粒子Capacity不足时系统会报错

如前所述，Capacity溢出时VFX Graph**静默丢弃**超额粒子，既不抛出异常，也不在Console面板显示警告。调试GPU事件时，若子粒子数量明显少于预期，首先检查子系统Capacity设置是否满足 `峰值触发率 × 子粒子数量 × 子粒子最大生命周期` 的乘积。

### 误区三：多级GPU事件可以无限嵌套

技术上GPU事件支持二级嵌套（孙粒子），但**三级及以上嵌套（曾孙粒子）在当前VFX Graph实现中不受支持**，编译器会拒绝该图并报告"GPU Event chain depth exceeded"错误。需要三级效果时，应将第三级改为CPU触发的独立VFX资产，通过事件系统调用。

---

## 知识关联

**与SDF交互的联系**：GPUEvent OnCollide依赖粒子的碰撞检测模块，而SDF交互提供了比深度缓冲碰撞更精确的几何碰撞信息。两者结合时，SDF的符号距离梯度（∇SDF）可作为子粒子初速度方向的来源，使溅射效果在复杂几何体表面保持法线对齐。若不使用SDF，OnCollide只能依赖屏幕空间深度缓冲，在摄像机视野外的碰撞无法触发。

**与SubGraph复用的关联**：一套完整的GPU事件级联配置（父系统触发→属性继承→子系统初始化）通常由10~20个节点构成，在不同特效资产中重复构建成本很高。SubGraph允许将这套标准触发链封装为可复用模板，并通过暴露参数（如子粒子数量、继承属性选择）实现一个SubGraph服务多种级联场景的复用目标。SubGraph中的内部GPU Event连接在编译时会正确展开，不影响运行时性能。