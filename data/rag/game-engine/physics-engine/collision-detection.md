---
id: "collision-detection"
concept: "碰撞检测"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["碰撞"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 碰撞检测

## 概述

碰撞检测（Collision Detection）是物理引擎中确定两个或多个几何体是否发生空间重叠或接触的计算过程。其输出不仅是"是否碰撞"的布尔值，还包括接触点坐标、穿透深度（Penetration Depth）和接触法线（Contact Normal），这三项数据是后续约束求解器施加冲量响应的必要输入。

碰撞检测算法的系统化发展始于1970年代计算机图形学研究。1988年，Gilbert、Johnson和Keerthi三人联合发表了著名的GJK算法论文，将凸体间距离计算的时间复杂度从O(n²)降至接近线性。游戏引擎中的碰撞检测正是以此为理论基础，经过PhysX、Bullet、Havok等商业引擎二十余年的工程优化，形成了今天成熟的宽阶段-窄阶段两级流水线架构。

碰撞检测的计算代价在大规模场景中极为显著。若场景中存在N个刚体，朴素的全对检测需要进行N(N-1)/2次几何相交测试。对于含500个刚体的典型游戏场景，这意味着每帧约124,750次测试，使宽阶段的剔除优化成为帧率稳定的关键瓶颈之一。

## 核心原理

### 宽阶段（Broad Phase）检测

宽阶段的目标是以极低代价快速排除绝对不可能碰撞的物体对，将候选碰撞对（Overlapping Pairs）的数量从O(N²)压缩到接近O(N)。最常用的数据结构是**轴对齐包围盒（AABB，Axis-Aligned Bounding Box）**，因其相交测试只需6次标量比较。

现代引擎最常采用**SAP算法（Sweep and Prune，扫描与剪枝）**实现宽阶段。SAP将每个AABB在X、Y、Z三轴上的最小值和最大值作为端点插入排序列表，每帧仅需增量更新已排序列表（利用插入排序对接近有序数组的O(n)特性），当两个AABB在三轴上的区间均重叠时，才标记为候选对。PhysX引擎的SAP实现可在10,000个刚体场景中将候选对数量控制在几百对以内。

另一种宽阶段方案是**层次包围盒（BVH，Bounding Volume Hierarchy）**，将场景物体组织成二叉树，自顶向下递归跳过不相交的子树节点。BVH对静态场景极为高效，但动态场景下每帧重构BVH的代价较高，因此Bullet引擎使用**动态AABB树（Dynamic AABB Tree）**实现O(log N)的增量更新。

### 窄阶段（Narrow Phase）检测

窄阶段针对宽阶段筛出的少量候选对进行精确的几何相交测试，输出完整的接触流形（Contact Manifold）。针对不同形状组合，引擎会选用不同算法：球-球碰撞只需比较圆心距与半径之和；球-平面只需一次点面距公式；凸多面体之间则主要依赖**GJK算法**和**SAT算法**。

### GJK算法（Gilbert-Johnson-Keerthi）

GJK算法利用**闵可夫斯基差（Minkowski Difference）**的性质：两凸体A与B相交，当且仅当其闵可夫斯基差 A⊖B = {a - b | a∈A, b∈B} 包含原点。GJK迭代构造A⊖B中包含或最接近原点的**单纯形（Simplex）**——在3D中最多为四面体——每轮迭代调用**支撑函数（Support Function）** s(d) = argmax{x·d | x∈A⊖B} 沿搜索方向d找到最远点。GJK的收敛通常在4至8次迭代内完成。当GJK判定两体相交后，再调用**EPA算法（Expanding Polytope Algorithm）**膨胀单纯形，精确计算穿透深度与接触法线。

### SAT算法（Separating Axis Theorem，分离轴定理）

SAT基于以下定理：两凸体不相交，当且仅当存在至少一条**分离轴**，使得两体在该轴上的投影区间不重叠。对于3D凸多面体碰撞，候选分离轴来自：物体A的所有面法线、物体B的所有面法线、以及A与B各边叉积生成的轴，共最多 mA + mB + mA·mB 条候选轴（mA、mB分别为两物体的边数）。一旦找到分离轴即可提前退出，因此SAT对于不相交的情形速度极快。SAT对AABB、OBB（朝向包围盒）等规则形状尤为高效，因其候选轴数量固定（OBB间仅需测试15条轴）。

## 实际应用

**角色与地形碰撞**：游戏角色通常使用**胶囊体（Capsule）**而非精确网格进行碰撞检测，因为胶囊体与三角形面的相交测试有解析解，且能平滑处理台阶和坡道。Unity引擎的CharacterController组件即内部使用半径0.3m、高1.8m的默认胶囊体。

**子弹穿透问题（Tunneling）**：高速运动的子弹在单帧内可能完全穿过薄墙，因为离散碰撞检测只检查帧首和帧末状态。解决方案是**连续碰撞检测（CCD，Continuous Collision Detection）**，通过对运动物体的扫掠体（Swept Volume）进行形状投射（Shape Cast）来找到首次接触时刻TOI（Time of Impact）。PhysX中仅对速度超过设定阈值的刚体激活CCD，避免全局性能开销。

**触发器（Trigger）优化**：在Unreal Engine中，触发器体积（Trigger Volume）只进行重叠查询而不生成接触流形，跳过了EPA阶段，使其代价仅为完整碰撞检测的约30%。

## 常见误区

**误区一：认为宽阶段AABB就是最终碰撞判定**。AABB相交仅代表"可能碰撞"，两个L形物体的AABB可能完全重叠而实际几何体并不接触。宽阶段只是代价极低的保守过滤器，必须由窄阶段GJK/SAT给出最终精确结论。忽略这一区别会导致大量"幽灵碰撞"（Ghost Collision）。

**误区二：认为SAT比GJK更准确或更通用**。SAT仅能测试凸多面体，且候选轴数量随多面体复杂度呈二次方增长，对高面数网格效率急剧下降。GJK通过支撑函数接口可处理任意凸形状（包括用公式定义的胶囊、椭球体），并不依赖显式的面/边枚举，适用范围更广。两者各有适用场景，SAT更适合OBB等简单规则形状，GJK更适合通用凸形状。

**误区三：认为连续碰撞检测（CCD）应该对所有物体默认开启**。CCD的计算代价约为离散检测的3至5倍，对于质量较大、速度较慢的静态环境几何体完全不必要。过度启用CCD会使帧时间预算超支，正确做法是仅对高速小体积刚体（如子弹、投射物）启用CCD标志。

## 知识关联

碰撞检测的前置知识是**刚体动力学**，特别是刚体的位姿表示（四元数旋转+位置向量）。碰撞检测算法中的支撑函数计算和AABB更新，都直接读取刚体每帧积分后的变换矩阵。不理解刚体的坐标系变换，就无法正确实现从世界空间到局部形状空间的投影转换。

碰撞检测的直接下游是**约束求解器**：窄阶段输出的接触点位置、穿透深度和接触法线被打包成接触约束（Contact Constraint），由求解器计算并施加法向冲量和摩擦冲量，最终修正刚体速度和位置。如果碰撞检测漏报或接触法线方向错误，约束求解器将产生物体互相穿透或被错误弹飞的仿真错误。

进一步深入后会接触到**破坏物理（Destructible Physics）**，它要求在运行时动态切割网格并为新生成的碎片实时构建凸包，这对碰撞检测的几何数据结构提出了增量更新的挑战——不再是静态预处理的支撑函数，而需要在Voronoi切割后毫秒级重建GJK所需的凸多面体表示。