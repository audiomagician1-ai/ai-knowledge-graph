---
id: "vfx-opt-collision-cost"
concept: "碰撞开销"
domain: "vfx"
subdomain: "vfx-optimization"
subdomain_name: "特效优化"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 碰撞开销

## 概述

碰撞开销（Collision Cost）是指粒子系统在执行碰撞检测时所消耗的CPU/GPU运算资源，直接体现为每帧处理碰撞所需的毫秒数。在Unity的粒子系统中，当粒子数量从1000增至10000时，若同时启用了精确的Mesh碰撞体，碰撞检测的开销可呈指数级增长，而非线性增长，这是该问题区别于其他粒子性能问题的关键特征。

碰撞检测最早在粒子系统中作为可选模块出现，约在2010年代初期的主流引擎中被引入。彼时硬件限制迫使开发者只能对极少量粒子启用碰撞，其余使用视觉欺骗手段。随着GPU加速和多线程物理引擎的普及，碰撞检测的适用范围扩大，但随之带来的开销控制问题也成为特效优化的高频瓶颈。

碰撞开销直接影响游戏在中低端设备上的帧率稳定性。雨滴打地面、火焰贴着地形蔓延、弹壳落地弹跳——这些效果都依赖碰撞检测。一旦碰撞开销失控，帧率从60fps跌至30fps以下的情况在移动端极为常见，因此掌握其成本结构与简化策略对特效师来说至关重要。

---

## 核心原理

### 碰撞检测的两种模式及其开销差异

Unity粒子系统提供两种碰撞模式：**World Collision（世界碰撞）** 和 **Planes Collision（平面碰撞）**。

- **World Collision**：粒子向物理引擎发送射线检测（Raycast）请求，每个粒子每帧最多发射一条射线。若粒子数量为N，理论射线数为N，实际开销受`Max Collision Shapes`参数限制（默认值为256）。此模式会与场景中所有碰撞体交互，CPU占用较高。
- **Planes Collision**：系统仅针对开发者手动指定的有限平面（最多支持6个）进行数学平面方程检测，每粒子开销约为World Collision的1/10到1/5。

开销公式可简化表示为：

> **碰撞帧开销 ≈ N × C_per_particle + K**

其中 N 为活跃粒子数，C_per_particle 为每粒子单次碰撞检测成本（与碰撞类型和碰撞层数量相关），K 为固定初始化开销。当 N 超过某阈值后，C_per_particle 因缓存失效还会额外上升。

### 质量（Quality）参数对开销的影响

Unity粒子系统碰撞模块中的`Quality`参数分为Low、Medium、High三档，其本质差异在于射线长度和采样频率：

- **Low**：每帧仅检测粒子移动路径的起点，可能发生穿透（Tunneling），但每粒子约节省30%检测时间。
- **High**：在粒子移动路径上进行分段检测（Substepping），对高速粒子不发生穿透，但开销最高，不适合粒子数超过500的特效。

对移动设备而言，推荐默认使用Low质量，结合`Lifetime Loss`参数让穿透粒子快速消亡，从视觉上掩盖穿透问题。

### 碰撞层（Layer Mask）过滤机制

碰撞开销的一个常被忽视的来源是`Collides With`的Layer Mask设置。如果粒子系统的碰撞层设置为"Everything"，物理引擎需要遍历场景中所有Layer的碰撞体。将Layer Mask精确设置为仅包含地面、墙壁等必要Layer，可减少约40%–60%的碰撞查询时间，在拥有大量动态物体的场景中效果尤为显著。

### 发送碰撞事件（Send Collision Messages）的额外代价

勾选`Send Collision Messages`后，粒子每次碰撞都会触发`OnParticleCollision`回调。若回调函数中包含复杂逻辑（如生成子特效、访问外部组件），该回调的CPU时间可能远超碰撞检测本身。每帧100次碰撞事件对应100次C#函数调用，GC压力随之上升。非必要时应关闭此选项。

---

## 实际应用

**雨水特效优化**：典型的降雨特效可能每秒生成2000–5000个雨滴粒子。启用World Collision使每滴雨与地面产生水花，开销极大。常见解决方案是将雨滴的碰撞改为Planes模式，仅设置一个水平地面平面，并将Bounce设为0，同时将粒子Lifetime控制在触地即消失。这样整个雨水特效的碰撞开销可从约3ms/帧降至0.3ms/帧以下。

**弹壳弹跳特效**：弹壳需要真实弹跳效果，不能用平面替代。此时推荐将弹壳作为独立的刚体物理对象（而非粒子），彻底脱离粒子碰撞检测系统，或将启用碰撞的弹壳粒子数上限（`Max Particles`）设为不超过20个，超出后自动回收最旧的粒子。

**火焰贴地效果**：火焰粒子无需精确碰撞，常见做法是完全关闭粒子碰撞，改用与地形形状吻合的粒子发射区域（Shape模块配合Terrain采样），从视觉上实现贴地效果，碰撞开销降为零。

---

## 常见误区

**误区一：粒子数少就可以随意开启World Collision**
许多开发者认为粒子数只有50–100时，World Collision开销可以忽略不计。但实际情况是，World Collision的射线查询会打断GPU实例化渲染的批次合并，间接导致Draw Call上升。即便粒子数极少，在场景碰撞体复杂时，50个粒子的World Collision依然可能产生0.5ms以上的峰值开销，在移动端不可轻视。

**误区二：Planes模式只适合平坦地面**
很多人认为Planes碰撞仅能用于完全平坦的表面，其实Planes最多支持6个任意方向的平面，可以通过合理组合模拟盒型空间（6个面）或斜坡（倾斜平面）。配合粒子的模拟空间（Local/World切换），Planes模式能覆盖大量非平坦场景，不应过早放弃而转向开销更高的World Collision。

**误区三：关闭Collision模块就彻底消除了碰撞开销**
若粒子系统的`Trigger`模块保持开启状态，即便Collision模块已关闭，触发器重叠检测（Overlap Test）仍会持续运行并产生物理查询开销。需同时关闭Trigger模块，才能将该粒子系统的物理检测开销降至零。

---

## 知识关联

碰撞开销的理解建立在**模拟空间**概念之上：粒子以World Space模拟时，碰撞检测在世界坐标系中执行，射线与场景碰撞体的交互逻辑更复杂；以Local Space模拟时，碰撞检测随父对象变换，若父对象频繁移动，碰撞结果可能出现误差，但射线数量本身不变。选择正确的模拟空间是控制碰撞开销的前提条件。

在掌握碰撞开销的简化策略后，下一个需要关注的性能话题是**光源特效开销**。光源与碰撞检测的本质差异在于：碰撞检测是粒子数量驱动的线性（或超线性）开销，而光源特效开销由动态光源数量和实时阴影开关决定，二者的优化方向截然不同。特效中同时存在碰撞粒子和发光粒子时，需分别评估各自的帧预算占用，避免单方面优化后另一方成为新的瓶颈。