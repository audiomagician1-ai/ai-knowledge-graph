---
id: "anim-hair-sim"
concept: "毛发模拟"
domain: "animation"
subdomain: "physics-animation"
subdomain_name: "物理动画"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 毛发模拟

## 概述

毛发模拟（Hair/Fur Simulation）是物理动画领域中专门针对头发、毛皮、羽毛等细丝状结构的动态计算技术。其核心挑战在于：单根毛发直径通常在0.04–0.09毫米之间，一个人类角色头部约有10万根头发，逐根模拟在实时条件下完全不可行，因此工业界发展出了以"导向毛发"（Guide Hair）驱动整体毛发运动的层级化策略。

毛发物理模拟的理论基础可追溯到1986年Anjyo等人提出的弹性杆（Elastic Rod）模型，而现代制作流程中大量引用的是2007年由Florence Bertails发表的"Super-Helices"头发模型，该模型将每根毛发视为具有弯曲与扭转刚度的Kirchhoff弹性杆（Kirchhoff Elastic Rod），能够精确再现卷曲发型的弹跳行为。

毛发模拟在角色动画中的重要性体现在视觉可信度上：《冰雪奇缘》（2013）中Elsa的头发包含约14万根独立模拟股，使用Disney内部的Taz解算器处理；《狮子王》（2019）真实感版本的狮子毛皮则依赖Houdini的Vellum求解器在每帧计算数百万根毛发的碰撞响应。

---

## 核心原理

### 弹簧链模型（Mass-Spring Chain）

最基础也最广泛使用的毛发模拟方法是将单根毛发离散化为一系列质点（Particle）和弹簧（Spring）组成的链状结构。每根导向毛发通常被分割为8–16段，相邻质点之间存在三种约束：

- **拉伸弹簧（Stretch Spring）**：阻止相邻质点间距离变化，刚度系数 $k_s$ 通常设为极高值（接近刚性）以防止毛发伸长。
- **弯曲弹簧（Bend Spring）**：连接间隔一个节点的两个质点，控制毛发的抗弯刚度 $k_b$，决定发型的蓬松或贴合程度。
- **扭转弹簧（Torsion Spring）**：约束相邻段的相对旋转，对卷发（Curly Hair）模拟尤为关键。

每个质点的运动遵循牛顿第二定律：$m\ddot{\mathbf{x}} = \mathbf{F}_{gravity} + \mathbf{F}_{spring} + \mathbf{F}_{damping} + \mathbf{F}_{collision}$，时间积分通常采用Verlet积分或隐式欧拉法，以在稳定性和效率之间取得平衡。

### 导向毛发与插值系统

为了将模拟成本控制在可接受范围内，工业标准做法是：仅对数百至数千根"导向毛发"（Guide Hair）进行全物理模拟，其余数万至数十万根"渲染毛发"（Render Hair）则通过重心坐标插值（Barycentric Interpolation）跟随最近的3–5根导向毛发运动。Maya XGen、Houdini Grooming和Unreal Engine的Groom系统均采用这一分层架构，导向毛发与渲染毛发的比例一般在1:50至1:200之间。

导向毛发根部通常绑定（Pin）在角色皮肤网格的特定顶点上，毛发的运动传播方向从根部到发梢，根部的位移由角色骨骼动画驱动，而发梢则完全由物理解算决定，形成"动力学主导区域"随毛发长度增大的自然过渡。

### Alembic缓存工作流

由于毛发模拟计算量巨大，现代电影制作流水线普遍采用**预计算+Alembic缓存**的离线工作流。Alembic（.abc）格式由Sony Pictures Imageworks和Industrial Light & Magic于2011年联合发布，专为存储大规模几何动画数据设计，支持按帧缓存每根毛发所有质点的空间坐标。

一个典型的毛发缓存文件体量：《奇异博士》中Strange披风的毛发模拟生成的Alembic文件每帧约为200–400MB，全镜头缓存可达数百GB。正因如此，生产中通常只缓存导向毛发的Alembic数据，渲染时再在GPU上实时完成从导向毛发到渲染毛发的插值还原。Alembic文件内部使用HDF5或Ogawa两种存储后端，后者（Ogawa）在多线程读取速度上比HDF5快约3–5倍，是2013年后的推荐选项。

### 碰撞检测与响应

毛发与角色身体的碰撞是模拟中最耗时的部分。常见做法是用简化的**碰撞胶囊体（Collision Capsule）**代替精确网格，头部通常用5–15个胶囊体拼合近似。毛发间的自碰撞（Hair-Hair Collision）由于毛发数量庞大，通常通过体积排斥力（Volume Repulsion）或局部密度约束（Density Constraint）来近似实现，而非逐对检测，以将时间复杂度从 $O(n^2)$ 降低到 $O(n\log n)$。

---

## 实际应用

**电影制作（离线渲染）**：在Houdini中，使用Wire Solver或Vellum Hair Solver对导向毛发进行模拟，输出Alembic缓存后导入Katana进行渲染。Pixar的《勇敢传说》（2012）是第一部将女主角大量卷发作为核心视觉卖点的CG电影，其开发的Taz毛发系统能同时模拟11.1万根独立发束，每根发束再细分为约10根渲染毛发，总计约111万根渲染毛发。

**实时游戏引擎**：Unreal Engine 5的Groom系统配合Niagara粒子系统，可在运行时对数千根导向毛发进行基于位置的动力学（PBD，Position-Based Dynamics）模拟，典型帧预算为2–3毫秒（在RTX 3080上）。《赛博朋克2077》的NPC毛发采用约512根导向毛发配合LOD（Level of Detail）系统，近景切换到高精度物理模拟，远景退化为静态发型。

**布料与毛发协同模拟**：当角色同时具有飘动的斗篷（布料）和长发（毛发）时，需要处理两套模拟系统之间的双向碰撞，通常通过共享同一套碰撞代理几何体（Proxy Geometry）并在同一求解器内按顺序求解来实现，先解算布料、再解算毛发与布料的碰撞响应。

---

## 常见误区

**误区一：导向毛发数量越多模拟越真实**
增加导向毛发数量并不线性提升视觉质量。导向毛发的密度超过渲染毛发实际需要的覆盖密度后，多余的导向毛发仅增加计算负担而不改变最终结果。正确做法是先确定渲染毛发的目标密度，再反推导向毛发所需的最低覆盖密度，通常每平方厘米头皮区域1–3根导向毛发已足够驱动高质量插值。

**误区二：Alembic缓存存储的是渲染毛发**
实际生产中，Alembic几乎从不直接缓存数十万根渲染毛发的完整轨迹，因为这会产生不可接受的文件体量和读写速度问题。Alembic缓存存储的是导向毛发（数百至数千根）的质点坐标，渲染毛发的生成是在渲染阶段即时完成的程序化过程。混淆这两层会导致对缓存体量和读取速度产生严重的误判。

**误区三：毛发模拟与布料模拟可以用完全相同的参数逻辑**
虽然毛发和布料都使用弹簧约束，但毛发的拓扑结构是一维链状（1D Chain），而布料是二维网格（2D Mesh）。这导致毛发的弯曲刚度需要单独用"弯曲弹簧"跨节点连接来实现，无法直接套用布料模拟中基于三角形二面角（Dihedral Angle）的弯曲约束公式。对短发或硬质鬃毛，直接借用布料的弯曲参数往往导致毛发过度塌陷或抖动。

---

## 知识关联

**与布料模拟的联系与区别**：布料模拟是毛发模拟的直接前置知识——两者都使用质点-弹簧系统和时间积分，碰撞检测也共享相似的方法论。然而布料的弹簧网络是二维拓扑，而毛发的弹簧链是一维拓扑，这一根本差异决定了毛发必须额外处理发梢端的自由悬挂边界条件，以及根部固定点的约束处理方式。学习毛发模拟时，布料中掌握的隐式积分稳定性、碰撞代理体设置经验可以直接迁移。

**与程序化生长系统的关联**：毛发模拟的输入（毛发的静态梳理形状）通常来自XGen、Houdini Grooming等程序化毛发生长工具，模