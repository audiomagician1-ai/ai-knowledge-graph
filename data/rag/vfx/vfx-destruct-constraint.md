---
id: "vfx-destruct-constraint"
concept: "约束系统"
domain: "vfx"
subdomain: "destruction"
subdomain_name: "破碎与销毁"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 约束系统

## 概述

约束系统（Constraint System）是破碎模拟中用于维持碎片间物理连接关系的机制，通过在相邻碎片之间设置虚拟的刚性或柔性"绑定"，使破碎体在受力前保持完整的几何形态。在 Houdini 的 Voronoi 破碎工作流中，约束系统以独立的几何节点形式存在，其数据结构包含每对相邻碎片的连接中心点、法线方向及各种强度属性。

约束系统的概念源自 20 世纪 90 年代的刚体动力学研究，早期 Maya nCloth 和 PhysX 引擎中已有雏形，但直到 Houdini 12 引入 Bullet Solver 并在版本 16 以后将约束作为独立的 `ConstraintNetwork` 几何体处理，现代特效制作中的精细控制才真正成为可能。

约束系统的价值在于：它决定了破碎对象"如何断裂"而非"断裂成什么形状"——碎片形状由 Voronoi 分割决定，但断裂的时机、顺序和传播路径完全由约束系统的参数控制。一个写实的混凝土柱倒塌与一个玻璃破碎的差异，本质上是约束系统参数配置的差异。

---

## 核心原理

### 连接力（Connect Force）与约束类型

约束系统中每条约束边（Constraint Edge）代表两块碎片之间的一根"虚拟螺栓"，携带三类物理连接力：

- **法向力（Normal Force）**：沿碎片接触面法线方向的拉压力，抵抗碎片被拉开或压合；
- **切向力（Tangential Force）**：平行于接触面的剪切力，抵抗碎片侧向滑动；
- **扭矩（Torque）**：抵抗碎片绕接触轴旋转。

在 Houdini `ContraintNetwork` 中，这三类力分别对应 `stiffness`、`dampingratio` 与 `breaktype` 属性。约束类型分为 `glue`（无弹性的刚性连接）、`spring`（带弹性系数 k 的弹簧连接）和 `hard`（绝对刚性，不允许任何相对位移）三种，不同类型对应截然不同的断裂行为。

### 断裂阈值（Break Threshold）

断裂阈值是约束系统中最关键的量化参数，表示约束被切断所需的最小冲量（单位：kg·m/s 或以无量纲的"强度值"表达）。Houdini Bullet Solver 中通过 `strength` 属性控制，典型取值范围如下：

| 材质类型 | 推荐 strength 范围 |
|---------|-----------------|
| 薄玻璃 | 100–500 |
| 砖墙（单砖）| 5,000–20,000 |
| 钢筋混凝土柱 | 50,000–200,000 |

断裂判断发生在每个 Bullet 子步（substep）的末尾，求解器计算约束当前承受的冲量，若超过 `strength` 则将该约束标记为 `broken = 1` 并在下一子步中彻底移除。这意味着增加 substep 数量（通常从默认值 1 提高至 3–5）会使断裂判断更加精细，尤其影响高速碰撞场景中的断裂位置准确性。

### 传播（Propagation）机制

单点冲击往往不会让整个结构瞬间崩解，而是通过约束链的传播逐步扩散破坏——这是现实中混凝土结构倒塌呈现"波纹状"断裂的物理原因。在 Houdini 中，传播通过 `Constraint Network SOP` 节点的 **Propagate** 选项实现：

1. **阈值传播**：当一条约束断裂后，将其邻近约束的 `strength` 值乘以一个衰减系数（propagation factor，常用值 0.3–0.8），使周围约束更易断裂；
2. **深度限制**：`Max Propagation Depth` 参数（整数，通常设为 2–5）限制传播向外扩散的层数，防止整体结构因一次小冲击而全部崩塌；
3. **各向异性传播**：可对不同方向的邻接约束设置不同衰减系数，模拟木材沿纹理方向更易断裂的特性。

传播参数的调整直接影响破坏效果的视觉节奏：factor 过高会导致"链式反应"式的爆炸感过强，过低则使结构显得过于坚固，需根据材质和导演意图反复迭代。

---

## 实际应用

**建筑爆破场景**：在制作高楼控制爆破特效时，通常将建筑底层柱的约束 `strength` 设为 0，同时在 `Constraint Network SOP` 中用 Attribute Wrangle 按楼层高度逐渐增大强度值，配合 `propagation factor = 0.6`，模拟爆破波从底部向上传播的滞后效果。

**弹孔与局部破碎**：子弹击中玻璃的效果要求约束在冲击点附近快速断裂，外围缓慢开裂。具体做法是在约束网络上通过 `PointProximity` 将距冲击点 5cm 以内的约束 `strength` 降低至正常值的 1/10，并设置 `Max Propagation Depth = 4`，同时保留外框约束不受传播影响，形成"蜘蛛网"状开裂图样。

**交互式实时破碎（游戏引擎）**：在 Unreal Engine 的 Chaos Physics 系统中，约束系统对应 Field System 中的 `Breaking Field`，其 `Strain Threshold` 参数与 Houdini 的 `strength` 概念等价，但计算单位不同，移植资产时需要按引擎文档重新标定数值。

---

## 常见误区

**误区一：认为增大碎片数量等同于提高破碎精度**
碎片数量（Voronoi 点数）只影响几何细分，而不影响断裂的动力学行为。实际上，碎片数从 500 增加到 5,000 并不会让断裂传播更真实，反而会因约束边数量呈平方级增长（O(n²) 关系）导致 Bullet 求解器计算时间急剧上升。提升破碎真实感的正确方式是精调 `strength` 分布和传播参数，而非盲目增加碎片数。

**误区二：将 `glue` 约束的 `strength = 0` 等同于"无约束"**
`strength = 0` 的 glue 约束在第一个 substep 就会立即断裂，碎片表现为从初始帧开始自由散落。这与"完全不创建约束"在视觉上相近，但在计算上仍会消耗约束求解的开销，并且可能引入初始帧的一帧穿插问题。正确移除约束应在 `Constraint Network SOP` 层级通过属性过滤删除对应约束几何体，而非设置零强度。

**误区三：约束断裂后碎片一定会飞散**
约束断裂仅代表两碎片之间不再有虚拟连接力，但碎片仍受重力、摩擦和碰撞的影响。若 Bullet Solver 的 `Friction` 参数设置较高（如 0.8 以上），大量约束断裂后的碎片可能因相互摩擦而堆叠停止，而非飞散。制作爆炸性破碎效果时，需同时调低摩擦系数并施加 `Pop Force` 或 `Fan Force` 等外力场。

---

## 知识关联

**与碎片（碎片与残骸）的关系**：碎片几何形状由 Voronoi 或布尔切割预先定义，约束系统则在这些已确定形状的碎片之间建立动力学连接。没有预先生成的碎片几何体，`Constraint Network SOP` 无法找到有效的连接点，因此碎片生成是约束系统的必要前置步骤。

**与簇组管理（Cluster）的关系**：当碎片数量过多时，直接对每对相邻碎片建立独立约束会导致约束边数爆炸。簇组管理（Clustering）将若干碎片合并为刚性簇，约束只建立在簇与簇之间，将约束数量从 O(n²) 降低至 O(k²)（k 为簇数，k ≪ n），在不牺牲宏观断裂表现的前提下大幅提升求解速度。约束系统的传播参数在簇层级与碎片层级的配置逻辑完全相同，但强度阈值需要按簇的平均质量重新校准。