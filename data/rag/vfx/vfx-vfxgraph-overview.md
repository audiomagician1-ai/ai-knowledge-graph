---
id: "vfx-vfxgraph-overview"
concept: "VFX Graph概述"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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


# VFX Graph 概述

## 概述

VFX Graph 是 Unity 引擎自 2018 年正式推出的节点式可视化粒子特效编辑系统，基于 GPU 计算着色器（Compute Shader）运行，能够在单帧内处理数百万个粒子。与 Unity 早期的 Particle System（Shuriken）不同，VFX Graph 将粒子的全部运算从 CPU 转移到 GPU，从根本上突破了传统粒子系统在数量规模上的瓶颈。

VFX Graph 的核心设计理念是"所见即所得"的节点编辑：用户通过拖拽、连线不同功能节点来描述粒子的生命周期行为，不需要编写 HLSL 着色器代码即可实现复杂的粒子运动逻辑。这套系统最初与 HDRP（高清渲染管线）绑定，从 Unity 2021.2 版本起，VFX Graph 正式扩展支持 URP（通用渲染管线），使其覆盖范围大幅扩大到移动端和中端项目。

VFX Graph 的重要性在于它将原本需要程序员编写 GPU 粒子系统才能实现的百万级粒子特效，变成了美术和技术美术可以独立完成的可视化工作流。《赛博朋克 2077》《死亡搁浅》等 3A 级游戏中密集的人群粒子、体积光效均使用了类似 GPU 粒子架构，而 VFX Graph 将这一能力带入了 Unity 工作流。

---

## 核心原理

### GPU Compute Shader 驱动机制

VFX Graph 的所有粒子数据（位置、速度、颜色、生命值等）存储在 GPU 显存中的缓冲区（GraphicsBuffer）内，而不是传统 CPU 内存。每帧更新时，Unity 调度一组 Compute Shader 来并行计算每个粒子的状态变化。以 GTX 1060 级别显卡为例，VFX Graph 在维持 60fps 的条件下可稳定运行约 100 万个粒子，而同等条件下 Shuriken CPU 粒子系统通常上限约 3 万个粒子。这一差距来源于 GPU 数千个并行线程与 CPU 单线程模拟之间的本质架构差异。

### 节点图结构与 Context 组织

VFX Graph 的可视化界面本质上是一张有向无环图（DAG），由多种节点类型构成。最顶层的组织单位是 **Context 节点**（如 Spawn、Initialize、Update、Output），这些 Context 构成粒子生命周期的主干流程。在 Context 内部，可以插入 Block 节点来定义具体行为（例如"Set Velocity Random"Block 用于随机化速度）。Context 与 Context 之间通过流程箭头连接，而属性值则通过独立的数据线在 Operator 节点与 Block 之间传递。这种双轨结构——流程流与数据流分离——是 VFX Graph 与 Shader Graph 等其他节点工具的重要区别。

### 容量预分配与内存管理

VFX Graph 采用固定容量预分配策略：每个 VFX Asset 在创建时必须在 Initialize Context 中设定粒子容量上限（Capacity）。例如设定 Capacity = 500,000，系统会在 GPU 显存中预留固定大小的缓冲区，无论实际存活粒子数量是否达到上限，这块显存始终被占用。这意味着将 Capacity 随意设为 1,000,000 会造成约 160~320MB 的显存占用（取决于每粒子属性数量），即使屏幕上只有一个粒子。因此，合理规划 Capacity 是 VFX Graph 性能调优的首要任务。

---

## 实际应用

**爆炸特效**：制作枪口焰特效时，可在 Spawn Context 中设置 Single Burst 模式，一次性发射 500 个粒子，Initialize Context 中使用"Sphere"形状随机化初始位置（半径 0.05m），Update Context 中叠加 Drag Force Block（阻力系数 2.0）和 Turbulence Block 产生翻滚感，Output Context 选择 Quad 输出并绑定发光贴图，整个流程无需一行代码即可完成。

**与 Timeline 集成**：在过场动画中，VFX Graph Asset 可被 Timeline 的 Visual Effect Track 直接控制，通过 Activation Track 精确到毫秒级地触发粒子爆发时间点。例如在第 3.2 秒触发一次 SendEvent，在 VFX Graph 内部接收该 Event 来激活特定的 Spawn Context，实现剧情特效与镜头的精确同步。

**自定义属性传递**：使用 Exposed Property（暴露属性）可以将 VFX Graph 内部参数（如颜色 Color、强度 Float、中心点 Vector3）暴露给外部 C# 脚本，通过 `visualEffect.SetVector3("Center", transform.position)` 的方式实时驱动特效跟随角色位置，从而实现动态交互型粒子效果。

---

## 常见误区

**误区一：VFX Graph 可以在任何 Unity 项目中使用**

VFX Graph 依赖 Scriptable Render Pipeline（SRP）架构，无法在 Unity 内置渲染管线（Built-in Render Pipeline）项目中运行。如果项目使用的是默认 Built-in 管线，打开 VFX Graph 资产后粒子将无法渲染，只显示空白。在开始使用 VFX Graph 前，必须先确认项目已切换至 HDRP 或 URP，并安装对应版本的 `com.unity.visualeffectgraph` 包（版本号需与 SRP 版本对齐，如 SRP 14.x 对应 VFX Graph 14.x）。

**误区二：粒子数量越少，VFX Graph 相比 Shuriken 越有优势**

VFX Graph 的 GPU 计算存在固定调度开销（Draw Call 准备、Compute Dispatch 启动），当粒子数量少于约 500 个时，这些开销会使 VFX Graph 的实际性能低于 CPU 粒子系统 Shuriken。对于 UI 粒子、少量装饰性粒子，Shuriken 反而是更合适的选择。VFX Graph 的优势区间是单个 Effect 粒子数超过 5,000 个的场景。

**误区三：VFX Graph 节点等同于 Shader Graph 节点**

两者的节点均呈现为可视化连线形式，但运行时机和目的完全不同。Shader Graph 节点在渲染每个像素时执行，输出颜色；VFX Graph 节点在粒子逻辑更新阶段执行，输出粒子属性（位置、颜色、大小等）。一个 VFX Graph Asset 的 Output Context 内部可以嵌入一个 Shader Graph 材质来控制粒子外观，即两者是层叠关系而非替代关系。

---

## 知识关联

学习 VFX Graph 不需要任何先修知识，但了解 Unity 基础操作（GameObject、Component、Package Manager）将加快上手速度。在 VFX Graph 内部，最关键的下一个学习目标是 **Context 系统**：理解 Spawn、Initialize、Update、Output 四种 Context 的职责划分和数据传递规则，是构建任何实质性粒子效果的前提。Context 系统决定了"粒子何时出生、初始状态如何、每帧如何更新、最终如何渲染"这四个核心问题的回答方式，而这四个问题贯穿了 VFX Graph 中所有特效制作的全过程。