---
id: "vfx-vfxgraph-output"
concept: "输出模式"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
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


# 输出模式

## 概述

在 Unity VFX Graph 中，**输出模式**（Output Mode）决定了粒子系统最终以何种几何形态渲染到屏幕上。VFX Graph 提供了多种 Output Context 节点，包括 Output Particle Quad、Output Particle Mesh、Output Particle Line、Output Particle Strip 以及 Output Point（点云）等，每种模式对应不同的顶点构建方式和渲染管线路径。选择不同的 Output Context 直接影响 DrawCall 的 GPU 指令集、顶点着色器的输入布局以及内存带宽开销。

输出模式概念随 VFX Graph 在 Unity 2018.3 正式进入 Package Manager 预览版时一同引入，2019.3 版本起进入正式支持阶段。在早期粒子系统 Shuriken 中，渲染模式只有 Billboard、Stretched Billboard 等有限选项，而 VFX Graph 的 Output Context 架构将几何生成与着色逻辑完全分离，允许开发者在同一个 VFX Asset 中并联多个不同类型的 Output Context，从而在单次模拟计算后将同一批粒子数据输出为多种形态。

理解输出模式的关键在于：VFX Graph 在 GPU 上通过 **Compute Shader** 写入粒子属性缓冲区（Attribute Buffer），随后各 Output Context 分别读取该缓冲区并生成对应的几何体。因此，一个 Quad 输出和一个 Mesh 输出可以共享同一套 Update Context 的模拟结果，而不会重复执行物理或碰撞计算，这使得多输出模式组合成为一种零边际计算成本的视觉增强策略。

---

## 核心原理

### Output Particle Quad（四边形公告板）

Quad 是最常用的输出模式，每个粒子被展开为 2 个三角形（共 4 个顶点、6 个索引），由 GPU 的 Geometry Shader 或 Vertex Shader 中的实例化拉伸完成。Quad 输出支持 **Blend Mode** 设置（Alpha、Additive、Premultiplied 等），并提供 **Orient** 模块控制公告板朝向：`Face Camera Plane`、`Face Camera Position`、`Along Velocity` 以及 `Fixed Axis` 四种模式对应不同的矩阵计算方式。

在 Orient 模块缺失时，Quad 默认使用 `Face Camera Plane` 模式，即所有粒子的法线始终平行于摄像机近裁面。若需制作拉伸尾迹效果，应切换为 `Along Velocity` 并配合 `Scale Y` 属性放大纵向尺寸，此时顶点位置公式为：

```
P_top = Position + Velocity_normalized * ScaleY * 0.5
P_bot = Position - Velocity_normalized * ScaleY * 0.5
```

### Output Particle Mesh（网格实例化）

Mesh 模式将每个粒子替换为一个完整的静态网格实例，内部使用 **GPU Instancing** 调用 `DrawMeshInstancedIndirect`，实例数量等于存活粒子数。该模式要求在 Output Context 的 **Mesh** 属性槽中指定 `UnityEngine.Mesh` 资产，并可通过 **LOD** 属性设置使用第几级 LOD（值为 0 时使用最高精度）。

Mesh 输出的顶点数消耗 = 粒子数 × 单个网格顶点数，因此对于 5000 个粒子使用一个 512 顶点的网格，总提交顶点数约为 **256 万**，须谨慎控制。推荐在 Mesh 输出中开启 **Frustum Culling** 以跳过视锥体外的粒子实例，该选项位于 Output Context 的 Inspector 面板的 Cull 分组下。

### Output Particle Line（线段）

Line 模式将每个粒子渲染为一条线段，线段的两端由属性 `Target Position` 和粒子自身的 `Position` 决定。若未连接 `Target Position`，线段退化为零长度点。Line 模式常用于闪电、能量连接特效，配合 `Set Target Position from Transform` Block 可将线段末端绑定到场景中的 Transform 对象。

Line 模式不支持 Orient 模块，其宽度由 `Size X` 属性控制，但该宽度以**屏幕空间像素**为单位进行内部裁剪，在极远距离下线段可能细于 1 像素而消失。

### Output Particle Strip（条带）与点云

Strip 模式将具有相同 `Strip Index` 的粒子串联为连续的多边形条带，常用于烟雾尾迹和丝带特效。条带内相邻粒子共享顶点，节省索引带宽。

点云模式（Output Point）每个粒子仅提交 1 个顶点，以 `GL_POINTS`（OpenGL 路径）或等效指令渲染，适合星空、沙尘等高密度小点特效，粒子数可安全扩展至 **100 万级别**，而 Quad 模式在同等数量下顶点数将乘以 4。

---

## 实际应用

**火焰 + 火星组合**：同一 VFX Asset 中并联一个 Output Particle Quad（渲染火焰面片，使用 Additive Blend）和一个 Output Particle Mesh（渲染细小火星碎片，指定 Sphere Mesh），两者共享同一 Update Context 的速度与湍流计算，最终形成体积感火焰而无需额外物理模拟开销。

**激光束效果**：使用 Output Particle Line，将发射器位置设为 `Position`，目标物体的世界坐标绑定至 `Target Position`，再叠加一个 Output Particle Quad 做光晕 Sprite，两个输出层使用 Additive 模式叠加，可实现完整的激光视觉效果。

**大规模星域背景**：选择 Output Point 模式，将粒子数设置为 500,000，每帧 GPU 仅需提交 50 万个单顶点绘制指令，相比 Quad 模式减少 75% 的顶点数据传输量，在移动端 GPU 上帧率差异可达 8–12ms。

---

## 常见误区

**误区一：认为 Mesh 输出与 Quad 输出性能相当**
Quad 每粒子固定 4 顶点，而 Mesh 输出的顶点数取决于所指定网格的复杂度。若误将一个 2000 顶点的装饰性模型指定给 Mesh 输出并使用 1 万粒子，将产生 2000 万顶点提交，极易导致 GPU 顶点处理阶段成为瓶颈，而开发者往往误以为 GPU Instancing 能消除此开销。

**误区二：Strip 模式可直接替代 Trail Renderer**
Output Particle Strip 的条带顺序由粒子的 `Strip Index` 和 `Particle Index in Strip` 决定，若粒子生成顺序不连续（如使用 Burst 发射超过容量上限后循环覆盖），条带会产生跳变折叠。而 Unity 内置 Trail Renderer 依赖时间戳排序，两者的排序逻辑根本不同，不可直接互换。

**误区三：多个 Output Context 会重复执行 Update 模拟**
事实上，Update Context 的 Compute Shader 调度在一帧内只执行一次，所有并联的 Output Context 均从同一帧的 Attribute Buffer 读取数据。因此在一个 VFX Asset 中添加第二个 Output Context 的性能代价仅为额外的一次 DrawCall 和几何生成开销，而不是双倍的物理模拟成本。

---

## 知识关联

**前置概念——碰撞与交互**：碰撞系统（Collider Event、Depth Collision）在 Update Context 阶段修改粒子的 `Position`、`Velocity` 和自定义属性，这些修改后的属性值会直接传入各 Output Context 使用。例如碰撞后触发的颜色变化，需要在 Output Particle Quad 的 **Set Color over Life** 或直接读取碰撞标记属性来反映，碰撞逻辑与渲染逻辑严格分层、单向流动。

**后续概念——SDF 交互**：掌握输出模式后，SDF（Signed Distance Field）交互将在 Update Context 中引入空间查询节点（Sample SDF），根据 SDF 场的距离值修改粒子运动轨迹，最终仍由各类 Output Context 决定如何将这些被 SDF 塑形的粒子可视化。选择 Mesh 输出时，SDF 驱动的粒子可以表现为在 SDF 表面滑行的碎片实例；选择 Strip 输出时，则可生成沿 SDF 轮廓流动的条带轨迹。