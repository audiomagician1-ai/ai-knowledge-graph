---
id: "spatial-partitioning"
concept: "空间分区"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 2
is_milestone: false
tags: ["索引"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 空间分区

## 概述

空间分区（Spatial Partitioning）是游戏引擎场景管理中将三维世界划分为多个子区域，以加速空间查询的一类数据结构与算法。其核心思想是：若某个物体不在特定区域内，与该区域相交的查询便可直接跳过该物体，将碰撞检测、渲染可见性判断、射线投射等操作的最坏复杂度从 $O(n)$ 降至 $O(\log n)$ 甚至接近 $O(1)$。

空间分区的理论根基来自 Jon Bentley 于1975年在《Communications of the ACM》发表的论文《Multidimensional binary search trees used for associative searching》，其中提出了 k-d 树（k-dimensional tree）的完整构造与查询算法。BSP（Binary Space Partitioning）树由 Henry Fuchs、Zvi Kedem 和 Bruce Naylor 于1980年的 SIGGRAPH 论文《On Visible Surface Generation by A Priori Tree Structures》中引入计算机图形学，之后被 id Software 用于 Quake（1996）引擎，实现了室内场景的实时可见性预计算。Quake 的 `.bsp` 编译工具链 QBSP 将关卡几何体离线切割为 BSP 树，生成的文件格式被 Valve 的 Source 引擎沿用至今。

未经空间分区优化的场景在规模扩大时代价极为惨烈：若场景中存在 $n = 10000$ 个碰撞体，暴力两两配对的潜在测试次数为 $n(n-1)/2 \approx 5 \times 10^7$ 次/帧；引入均匀网格或八叉树后，平均测试次数可压缩至数百次量级，使 60 fps 的物理更新成为可能。

---

## 核心原理

### 均匀网格（Uniform Grid）

均匀网格将世界空间切割为边长固定的单元格（Cell），每个物体依据其 AABB（轴对齐包围盒）注册到所有被覆盖的单元格中。查询时仅检索目标区域所覆盖的单元格集合，物体均匀分布时时间复杂度接近 $O(1)$。

关键参数是**格子边长 `cellSize`**，工程经验建议将其设为场景中最大移动物体直径的 1.5～2 倍。若 `cellSize` 过小，单个大物体跨越的格子数爆炸（一个直径 10 m 的对象在 0.5 m 格子中需注册 $8000$ 个格子）；若 `cellSize` 过大，每格包含物体过多，退化为暴力遍历。均匀网格对静态、密度均匀的场景（如 RTS 游戏的单位空间管理）效果极好，但对具有极端稀疏区域的开放世界地图内存浪费严重。

### 四叉树与八叉树（Quadtree / Octree）

八叉树（Octree）递归地将三维 AABB 沿 X、Y、Z 轴的中点各切一刀，将父节点分裂为 8 个子节点；四叉树（Quadtree）是其二维对应，分裂为 4 个子节点，常用于地形高度图的 LOD 管理。

分裂条件通常为：节点内物体数量超过阈值（常用 8～16 个），**且**当前深度未超过最大深度（常用 8～12 层）。设根节点包围盒边长为 $L$，则第 $d$ 层节点的边长为：

$$
\ell_d = \frac{L}{2^d}
$$

深度 $d = 10$ 时，最细粒度格子边长为根节点的 $1/1024$。若根节点代表 1024 m 的场景，最小叶节点精度为 1 m，恰好满足典型角色碰撞需求。

Unreal Engine 5 中，世界场景的 Actor 可见性和碰撞查询由层级式 Octree 管理，源码位于 `Engine/Source/Runtime/Core/Public/Math/GenericOctree.h`，其模板参数 `OctreeSemantics` 允许用户自定义元素的 AABB 获取方式与叶节点容量。

### BSP 树（Binary Space Partitioning Tree）

BSP 树使用任意方向的超平面（不限于轴对齐）将空间递归分为"正面"与"背面"两个半空间，适合表达多边形拓扑复杂的室内几何体。分割平面方程为：

$$
ax + by + cz + d = 0, \quad (a,b,c) \text{ 为单位法向量}
$$

判断点 $P = (x_0, y_0, z_0)$ 位于平面哪一侧，只需计算符号值 $s = ax_0 + by_0 + cz_0 + d$：$s > 0$ 在正面，$s < 0$ 在背面，$s = 0$ 恰好在平面上。

BSP 树的核心优势是可以**离线预计算正确深度排序**（画家算法），这正是 Quake 时代解决室内场景"可见性集合"（PVS, Potentially Visible Set）问题的关键。QBSP 编译一张中等复杂度关卡通常需要数分钟 CPU 时间，但换来运行时每帧 $O(\log n)$ 的精确可见性查询。BSP 树的缺陷在于：当场景多边形被分割平面切穿时，会产生**T-junction**（T 型接缝），总多边形数膨胀；动态对象频繁更新时重建代价不可接受，因此现代引擎仅将 BSP 用于静态场景或编辑器碰撞几何体。

---

## 关键公式与算法

### AABB 与格子的映射

将 AABB 最小角 $P_\min = (x_\min, y_\min, z_\min)$ 映射到均匀网格单元格索引的公式：

$$
(i, j, k) = \left\lfloor \frac{P_\min - W_\min}{\text{cellSize}} \right\rfloor
$$

其中 $W_\min$ 为世界空间原点偏移。对 AABB 的最大角同理，遍历 $[i_\min, i_\max] \times [j_\min, j_\max] \times [k_\min, k_\max]$ 所有格子完成注册。

### 八叉树插入的伪代码

```python
class OctreeNode:
    MAX_OBJECTS = 8   # 分裂阈值
    MAX_DEPTH   = 12  # 最大深度

    def insert(self, obj, depth=0):
        if self.is_leaf():
            self.objects.append(obj)
            # 超出阈值且未达最大深度时分裂
            if len(self.objects) > self.MAX_OBJECTS and depth < self.MAX_DEPTH:
                self.subdivide()          # 创建 8 个子节点
                for o in self.objects:
                    self.push_down(o, depth + 1)
                self.objects.clear()
        else:
            # 找到与 obj.aabb 相交的子节点并递归插入
            for child in self.children:
                if child.bounds.intersects(obj.aabb):
                    child.insert(obj, depth + 1)

    def query_frustum(self, frustum, result):
        if not frustum.intersects(self.bounds):
            return                        # 整个子树剔除
        if self.is_leaf():
            result.extend(self.objects)
        else:
            for child in self.children:
                child.query_frustum(frustum, result)
```

`query_frustum` 的剔除效果直接体现在视锥剔除（Frustum Culling）阶段：一棵深度为 8 的八叉树在典型相机角度下可剔除约 85%～95% 的叶节点，将可见性测试的物体数从数万压缩至数百。

---

## 实际应用

**案例：《我的世界》（Minecraft）区块系统**

Minecraft 将无限世界划分为 16×16×256（Java 版，1.18 后扩展为 16×16×384）的区块（Chunk），本质上是均匀网格的二维变种加垂直叠加。每个区块独立管理其内部方块的光照传播和碰撞网格，客户端仅加载以玩家为中心、半径为"视距"（默认 8 区块 = 128 m）的区块，其余区块完全不参与渲染或物理计算。这一设计使游戏可以在消费级硬件上管理"事实上无限"的世界。

**案例：Unreal Engine 5 的 World Partition**

UE5 引入的 World Partition 系统以 $100 \times 100$ m（可配置）的 Cell 网格将整个关卡分块，结合流送（Streaming）机制按相机距离动态加载/卸载 Cell，其底层正是均匀网格空间分区的工程化实现。官方文档指出，《黑客帝国觉醒》技术演示地图面积约 97 km²，正是依赖 World Partition 实现无缝流送。

**案例：物理引擎的宽相（Broad Phase）**

Nvidia PhysX 与 Bullet Physics 均在碰撞检测管线的"宽相"阶段使用空间分区剔除不可能相交的物体对。PhysX 默认采用**SAP（Sweep and Prune）**算法结合轴排序列表，而 Bullet 提供 `btDbvtBroadphase`（动态包围体树，类似松散八叉树）和 `bt32BitAxisSweep3`（均匀网格变种）两种可选后端，用户可根据场景密度特征手动切换。

---

## 常见误区

**误区1：八叉树一定优于均匀网格**

均匀网格在物体密度**均匀**且尺寸**相近**时，其 $O(1)$ 的插入与查询常数因子远小于八叉树的递归开销。例如 RTS 游戏中数百个尺寸相近的单位，均匀网格通常比八叉树快 2～3 倍，因为后者需要额外的指针追踪和动态内存分配。

**误区2：BSP 树可以处理动态场景**

BSP 树的构建是 NP-hard 问题（寻找最优分割顺序），实践中使用启发式（如选择分割多边形数最少的平面），编译时间以分钟计。将 BSP 用于每帧更新的动态物体是不现实的；现代引擎仅用 BSP 处理**编译期确定的静态几何体**（如关卡碰撞网格），动态对象另设 Octree 或 DBVT 层管理。

**误区3：深度越大，八叉树查询越快**

过深的八叉树（$d > 12$）会导致叶节点边长极小，一个跨多格的大型物体（如直径 50 m 的爆炸效果）需要被注册进大量叶节点，插入和删除开销反而急剧上升。正确做法是引入**松散八叉树（Loose Octree）**：将每个节点的实际 AABB 扩大为其名义尺寸的 $2\times$（扩大系数 $k=2$ 是常用值），使得 87.5% 以上的物体只需存储在单个节点中，避免跨节点重复注册（参见 Ulrich, 2000，《Loose Octrees》，*Game Programming Gems*）。

**误区4：空间分区替代场景图**

空间分区与场景图（Scene Graph）解决的是不同问题：场景图管理物体的层级变换（父子坐标系），空间分区加速空间查询。两者在引擎中通常**并行存在**——场景图的叶节点（Mesh Component）向空间分区结构注册其 AABB，更新变换时同步更新注册信息。

---

## 知识关联

**前置概念——场景图（Scene Graph）**：场景图中每个节点的 World AABB 是空间分区注册的基本输入。理解场景图的变换传播机制（从局部坐标到世界坐标的矩阵级联）有助于理解为何 AABB 需要在 Transform 更新后重新计算并重新插入空间分区结构。

**后续概念——视锥剔除（Frustum Culling）**：视锥剔除的高效实现依赖八叉树或 BVH 的层次遍历，`query_frustum` 函数（见上方代码）正是视锥剔除的核心子程序。六平面测试（Six-Plane Test）对每个八叉树节点的 AABB 执行，单次测试仅需 6 次点积和比较。

**后续概念——环境查询系统（EQS）**：Unreal Engine 的 EQS（Environment Query System）在寻路和 AI 决策中大量使用空间查询