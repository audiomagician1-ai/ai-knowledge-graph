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
quality_tier: "S"
quality_score: 83.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 碰撞检测

## 概述

碰撞检测（Collision Detection）是物理引擎中确定两个或多个几何体是否发生空间重叠或接触的计算过程。其输出不仅是"是否碰撞"的布尔值，还包括接触点坐标、穿透深度（Penetration Depth）和接触法线（Contact Normal），这三项数据是后续约束求解器施加冲量响应的必要输入——缺少任何一项，刚体响应计算都无法正确执行。

碰撞检测算法的系统化发展始于1970年代计算机图形学研究。1988年，Gilbert、Johnson和Keerthi三人联合在《Journal of the ACM》发表论文"A fast procedure for computing the distance between complex objects in three-dimensional space"，将凸体间距离计算的时间复杂度从朴素的 $O(n^2)$ 降至接近线性，奠定了此后三十余年游戏物理引擎的理论基石（Gilbert, Johnson & Keerthi, 1988）。PhysX、Bullet、Havok等商业引擎在此基础上经过二十余年工程优化，形成了今天成熟的宽阶段-窄阶段两级流水线架构。

碰撞检测的计算代价在大规模场景中极为显著。若场景中存在 $N$ 个刚体，朴素的全对检测需要进行 $\frac{N(N-1)}{2}$ 次几何相交测试。对于含500个刚体的典型游戏关卡，这意味着每帧约124,750次完整凸体测试；若以60 Hz帧率运行，每秒约需执行748.5万次——仅此一项即可耗尽现代CPU单核的全部算力。这正是宽阶段剔除优化成为帧率稳定关键瓶颈的原因。

---

## 核心原理

### 宽阶段（Broad Phase）检测

宽阶段的目标是以极低代价快速排除绝对不可能碰撞的物体对，将候选碰撞对的数量从 $O(N^2)$ 压缩到接近 $O(N)$。最常用的包围体是**轴对齐包围盒（AABB，Axis-Aligned Bounding Box）**，其相交测试仅需6次标量比较：

$$
\text{overlap} = (A_{max}^x \geq B_{min}^x) \wedge (B_{max}^x \geq A_{min}^x) \wedge (A_{max}^y \geq B_{min}^y) \wedge (B_{max}^y \geq A_{min}^y) \wedge (A_{max}^z \geq B_{min}^z) \wedge (B_{max}^z \geq A_{min}^z)
$$

三轴任意一轴不满足区间重叠即可立即剔除，无需进入窄阶段。

**SAP算法（Sweep and Prune，扫描与剪枝）** 是现代引擎宽阶段最主流的实现方案，由Cohen等人于1995年提出。SAP将每个AABB在X、Y、Z三轴上的最小值和最大值作为端点插入排序列表，每帧只做增量更新（利用插入排序对接近有序数组的 $O(n)$ 特性）。当两个AABB在三轴区间全部重叠时，才标记为候选对。PhysX 4.x的SAP实现可在10,000个动态刚体场景中将候选对数量控制在数百对以内，宽阶段耗时不超过整帧物理预算的15%。

**动态AABB树（Dynamic AABB Tree）** 是Bullet引擎（Erwin Coumans, 2005年首发）的默认宽阶段实现。它将场景物体组织成自平衡二叉树，每个叶节点存储一个物体的AABB，内部节点存储子树的合并AABB，查询时自顶向下递归跳过不相交子树，单次查询复杂度为 $O(\log N)$，增量插入/删除也仅需 $O(\log N)$，对动态场景比静态BVH更具优势。

> **思考：** 若场景中99%的物体都是静态地形（地面、墙壁），只有1%是动态刚体，你会如何设计宽阶段以最大化效率？SAP与动态AABB树哪种更合适？

### 窄阶段（Narrow Phase）检测

窄阶段针对宽阶段筛出的少量候选对进行精确几何测试，输出完整的**接触流形（Contact Manifold）**——通常包含1至4个接触点，每个接触点携带世界坐标、穿透深度和接触法线。引擎针对不同形状组合选用不同算法以最大化性能：

| 形状组合 | 算法 | 典型耗时（微秒） |
|---|---|---|
| 球 vs 球 | 圆心距比较 | < 0.1 |
| 球 vs 平面 | 点面距公式 | < 0.1 |
| 胶囊 vs 胶囊 | 线段最近点 | ~0.2 |
| 凸多面体 vs 凸多面体 | GJK + EPA | ~2–10 |
| 网格 vs 凸体 | BVH + GJK | ~10–50 |

### GJK算法（Gilbert-Johnson-Keerthi）

GJK算法的核心依赖**闵可夫斯基差（Minkowski Difference）** 的性质：两凸体 $A$ 与 $B$ 相交，当且仅当其闵可夫斯基差

$$
A \ominus B = \{a - b \mid a \in A,\ b \in B\}
$$

包含原点 $\mathbf{0}$。GJK迭代构造 $A \ominus B$ 中包含或最接近原点的**单纯形（Simplex）**——在3D空间中最多为四面体（4个顶点）。每轮迭代调用**支撑函数（Support Function）**：

$$
s(\mathbf{d}) = \arg\max_{\mathbf{x} \in A \ominus B}\ \mathbf{x} \cdot \mathbf{d}
$$

沿搜索方向 $\mathbf{d}$ 找到闵可夫斯基差上最远点，再通过子单纯形分析更新 $\mathbf{d}$ 并剔除多余顶点。GJK的收敛通常在4至8次迭代内完成，与凸体的顶点数量无关。

当GJK判定两体相交后，再调用**EPA算法（Expanding Polytope Algorithm，Gino van den Bergen, 2001）** 膨胀单纯形以计算最小穿透向量（MTD, Minimum Translation Distance），从而得到穿透深度和接触法线。EPA的时间复杂度在最坏情况下为 $O(n \log n)$，但游戏场景中实际迭代次数通常不超过20次。

### SAT算法（Separating Axis Theorem，分离轴定理）

SAT基于以下定理：两凸体不相交，当且仅当存在某条轴（分离轴），使得两体在该轴上的投影区间不重叠。对于3D中两个各有 $m$ 和 $n$ 个面的多面体，候选分离轴共有 $m + n + 3mn$ 条（面法线 + 边叉积）。SAT逐一测试每条轴，只要找到一条分离轴即可立即返回"不相交"；若所有轴均重叠，则重叠最小的轴方向即为接触法线，对应的重叠量即为穿透深度。

SAT的优势在于对**箱体（OBB）** 等规则形状极为高效——两个OBB的分离轴测试仅需15条轴，整体测试时间不足1微秒。其劣势是对高多边形凸体（>50面）的候选轴数量爆炸，此时GJK通常更优。

---

## 关键算法实现

以下为GJK支撑函数的简化C++实现，展示其与形状解耦的设计：

```cpp
// 凸体支撑函数：沿方向d返回形状上最远点
// 对于凸多面体，时间复杂度O(V)，V为顶点数
glm::vec3 Support(const ConvexShape& shapeA, const ConvexShape& shapeB, 
                   const glm::vec3& direction) {
    // 闵可夫斯基差上的支撑点 = A的最远点 - B的反方向最远点
    glm::vec3 pointA = shapeA.FarthestPoint(direction);       // A沿d方向最远点
    glm::vec3 pointB = shapeB.FarthestPoint(-direction);      // B沿-d方向最远点
    return pointA - pointB;                                    // 闵可夫斯基差上的点
}

// GJK主循环（简化版，完整实现需处理退化单纯形）
bool GJK_Intersect(const ConvexShape& A, const ConvexShape& B) {
    glm::vec3 d = glm::vec3(1, 0, 0);                        // 初始搜索方向
    Simplex simplex;
    simplex.Add(Support(A, B, d));
    d = -simplex[0];                                           // 朝向原点

    for (int iter = 0; iter < 64; ++iter) {                   // 最多64次迭代
        glm::vec3 a = Support(A, B, d);
        if (glm::dot(a, d) < 0) return false;                 // 未过原点，不相交
        simplex.Add(a);
        if (UpdateSimplex(simplex, d)) return true;            // 单纯形包含原点
    }
    return false;
}
```

此实现清晰展示了GJK与具体形状的解耦：`FarthestPoint` 函数对球只需返回 $\mathbf{c} + r\hat{\mathbf{d}}$（圆心加半径方向），对胶囊、凸包等形状各自实现，主循环代码完全不变。

---

## 实际应用

**案例：Unity PhysX 中的碰撞层级配置**

Unity的物理引擎（底层为PhysX 4.x）通过Layer Collision Matrix控制哪些层之间需要做碰撞检测。假设场景中有500个敌人（EnemyLayer）和500个子弹（BulletLayer），若敌人之间不需要碰撞，在矩阵中禁用 Enemy×Enemy 这一对，SAP的候选对数量从约 $\frac{1000 \times 999}{2} \approx 499,500$ 对直接降至约 $500 \times 500 = 250,000$ 对（敌人×子弹），再加上各自内部的 $\frac{500 \times 499}{2} \approx 124,750$ 对子弹互碰（若也禁用则进一步减半）。合理配置Layer Matrix是大型战斗场景物理优化的第一步，成本几乎为零。

**案例：GJK在角色控制器中的应用**

第三人称角色在复杂地形行走时，引擎需要每帧检测角色胶囊体与地形三角网格的碰撞。PhysX的角色控制器（CharacterController）使用胶囊 vs 三角形的专用GJK实现，针对胶囊的解析支撑函数可在不到0.5微秒内完成单个三角形测试，配合BVH剔除后每帧通常只需测试8至20个三角形，总耗时不足10微秒。

---

## 常见误区

**误区1：认为AABB宽阶段已足够精确，可以跳过窄阶段**

AABB是最保守的包围体——一个旋转45°的细长骨骼剑，其AABB体积可能是实际几何体积的3倍以上，大量AABB重叠的候选对在实际几何上并未碰撞。跳过窄阶段会导致大量"幽灵碰撞"（Ghost Collision），使物体在未实际接触时即触发响应，角色无法走过本应穿越的缝隙。

**误区2：对所有凸体一律使用GJK，忽视形状特化算法**

球-球碰撞只需计算圆心距并与半径之和比较，耗时约0.05微秒；强行调用GJK处理球-球则需要完整的单纯形迭代，耗时约2微秒，性能相差40倍。引擎通常维护一张形状组合分发表（Dispatch Table），对球、胶囊、平面等基础形状使用解析算法，只有凸多面体间的测试才路由到GJK。

**误区3：混淆穿透深度与接触点坐标的坐标系**

EPA输出的穿透深度和法线是在**世界空间**中的，但约束求解器有时需要**局部空间**的接触点以计算力矩。开发者在实现自定义约束时若直接使用世界空间接触点计算局部力矩而