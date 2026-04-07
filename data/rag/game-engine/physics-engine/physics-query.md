---
id: "physics-query"
concept: "物理查询"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["查询"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 96.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 物理查询

## 概述

物理查询（Physics Query）是游戏引擎物理系统提供的一类主动探测接口，允许开发者在不创建刚体或碰撞对象的前提下，向物理场景发射几何形状并同步获取与场景中碰撞体的相交信息。与被动的碰撞回调（Collision Callback）不同，物理查询由游戏逻辑代码主动触发，返回命中点世界坐标、接触法线方向、命中距离参数 `t`、被命中对象引用等具体数据，且结果在同一帧内立即可用。

物理查询的概念最早在 NVIDIA PhysX 2.x 版本中以 `NxScene::raycastSingleShape` 等函数形式正式成型。2010 年 PhysX 3.0 的架构重构将所有查询接口统一归入 `PxScene` 的查询体系，形成了 **Raycast、Sweep、Overlap** 三大类接口的现代标准架构，并引入了两级过滤机制（层掩码 + 查询回调）。Unity 自 2.x 起、Unreal Engine 自 UE3 起均直接封装了 PhysX 的查询层。Unreal Engine 4 的 `UWorld::LineTraceSingleByChannel` 函数族至今仍是行业参考实现，而 Unity 6 在底层已将默认物理后端切换为 PhysX 5.1，查询接口 API 保持向后兼容。

物理查询的不可替代性在于**同步性**：绝大多数游戏玩法逻辑——命中判定、视线检测、角色站立检测、AI 感知范围——都要求在单帧（通常 16.67ms 或 8.33ms 预算）内返回精确几何信息。传统碰撞事件机制依赖物理步进后的异步回调，无法满足这一约束。

参考资料：Erin Catto 在 GDC 2010《Computing Distance Using GJK》中系统阐述了 Sweep/Overlap 查询的数学基础；《游戏引擎架构》（Game Engine Architecture，Jason Gregory，2018，电子工业出版社）第 13 章对物理查询系统有完整的工程描述。

---

## 核心原理

### Raycast（射线检测）

Raycast 向场景投射一条无限细的射线，数学定义为：

$$P(t) = \text{origin} + t \cdot \hat{d}, \quad t \in [0,\ \text{maxDistance}]$$

其中 $\hat{d}$ 为单位化方向向量，$t$ 为射线参数。物理引擎处理流程分两阶段：

1. **宽相（Broad Phase）**：对场景中所有启用 `PxQueryFlag::eSTATIC` 或 `eANY_HIT` 标志的形状，用射线与其轴对齐包围盒（AABB）做相交测试，时间复杂度 $O(\log N)$（PhysX 使用 SAP 或 BVH 加速结构）；
2. **窄相（Narrow Phase）**：对通过宽相的候选形状执行精确射线-凸多面体或射线-三角网格测试，返回最小 $t$ 值即为最近命中距离。

命中点计算：$\text{hitPoint} = \text{origin} + t_{\min} \cdot \hat{d}$

Raycast 提供三种命中模式：
- **Single**：返回最近命中，$O(\log N + K)$，$K$ 为窄相候选数；
- **Any**：返回任意一个命中（不保证最近），一旦找到即提前退出，性能比 Single 高约 20%–40%；
- **All**：收集所有命中并按 $t$ 升序排列，用于穿透弹道或激光穿透多层墙壁场景。

### Sweep（扫掠检测）

Sweep 将一个实心几何体（球体、胶囊体、Box 或凸多面体）沿方向 $\hat{d}$ 滑动距离 $d_{\max}$，检测运动路径上最早发生接触的碰撞体。其数学本质是**闵可夫斯基和（Minkowski Sum）**：

$$\text{Swept Volume} = \text{QueryShape} \oplus \text{Ray}(0 \to d_{\max} \cdot \hat{d})$$

对两个凸体 $A$（查询体）和 $B$（场景体）的 Sweep，等价于对 $A \oplus (-B)$ 执行 Raycast——即先求闵可夫斯基差，再做射线检测。各形状的性能差异显著：

| 查询形状 | GJK 平均迭代次数 | 相对耗时（PhysX 基准） |
|----------|----------------|----------------------|
| 球体     | 1–3 次         | 1×（基准）            |
| 胶囊体   | 3–6 次         | 1.4×                 |
| Box      | 8–15 次        | 2.8×                 |
| 凸多面体 | 10–20 次       | 4.5×                 |

Unity 中的 `Physics.CapsuleCast` 是 Sweep 的典型用例，角色控制器（Character Controller）用它检测移动路径上的障碍物，胶囊形状与人形角色碰撞体一致，精度与性能兼顾。

### Overlap（重叠检测）

Overlap 测试一个**静置**几何体是否与场景中的碰撞体相交，不涉及运动方向，返回所有重叠碰撞体的引用列表。PhysX 的 `PxOverlapHit` 结构只含 `actor` 和 `shape` 两个字段，**不返回接触点或穿透深度**——若需穿透深度，应改用 `PxScene::computePenetration`。

内部实现上，PhysX 对凸体 Overlap 使用 **SAT（Separating Axis Theorem）**而非 GJK：两个凸多面体之间最多测试 $m + n + m \cdot n$ 条分离轴（$m$、$n$ 分别为两体的面数），对常见的 Box-Box 组合（各 3 面）最多测试 $3 + 3 + 9 = 15$ 条轴，一旦找到分离轴即提前终止。Overlap 常用于范围技能（爆炸半径 5m 内所有单位）和传送前目标点安全性校验。

---

## 关键公式与代码示例

### 射线命中点与反射方向计算

入射射线方向 $\hat{d}$，命中点法线 $\hat{n}$，反射方向为：

$$\hat{r} = \hat{d} - 2(\hat{d} \cdot \hat{n})\hat{n}$$

该公式在弹跳子弹、激光反射等玩法中直接使用命中结果的 `normal` 字段即可实现。

### Unity C# 代码示例

```csharp
// Raycast Single：检测鼠标指向的物体
void Update()
{
    Ray ray = Camera.main.ScreenPointToRay(Input.mousePosition);
    RaycastHit hit;
    // layerMask = ~(1 << 2) 排除 IgnoreRaycast 层（Layer 2）
    int layerMask = ~(1 << 2);
    if (Physics.Raycast(ray.origin, ray.direction, out hit, 100f, layerMask))
    {
        // hit.point    : 命中点世界坐标
        // hit.normal   : 命中面法线
        // hit.distance : 射线参数 t（等于 origin 到 hitPoint 的距离）
        Debug.DrawLine(ray.origin, hit.point, Color.red);
        Debug.Log($"命中: {hit.collider.name}, 距离: {hit.distance:F2}m");
    }
}

// SphereCast Sweep：角色前方障碍检测（半径 0.5m，距离 2m）
bool CheckObstacle(Vector3 origin, Vector3 direction)
{
    RaycastHit sweepHit;
    return Physics.SphereCast(origin, 0.5f, direction, out sweepHit, 2f);
}

// OverlapSphere：爆炸范围 5m 内所有碰撞体
void Explode(Vector3 center)
{
    Collider[] targets = Physics.OverlapSphere(center, 5f,
        LayerMask.GetMask("Enemy", "Destructible"));
    foreach (var col in targets)
    {
        col.GetComponent<IDamageable>()?.TakeDamage(100);
    }
}
```

---

## 查询过滤系统

物理查询支持两级过滤机制，两级均需通过才会进入窄相测试：

**第一级：层掩码（Layer Mask）**
以 32 位整数的位运算在宽相阶段完成过滤，零额外性能开销。Unity 支持最多 32 个物理层，Unreal Engine 使用 `ECollisionChannel` 枚举提供 32 个通道，其中前 18 个为引擎保留通道，`ECC_GameTraceChannel1` 至 `ECC_GameTraceChannel14` 供项目自定义。

**第二级：查询过滤回调（PxQueryFilterCallback）**
对通过层掩码的每个候选形状调用 `preFilter` 回调，开发者可在此检查自定义标签、动态游戏状态（如"无敌帧"期间跳过角色碰撞体）。回调返回 `PxQueryHitType::eNONE`（跳过）、`eTOUCH`（记录但继续）或 `eBLOCK`（阻挡，终止搜索）。滥用 `preFilter` 回调（每帧对 500+ 候选形状逐一回调）会导致 CPU 端性能瓶颈，建议优先通过层掩码缩小候选集。

---

## 实际应用

**1. 第一人称射击命中判定**
典型 FPS 游戏中，`Physics.Raycast` 从摄像机原点沿准心方向发射，`maxDistance` 设为武器有效射程（如步枪 500m，手枪 50m）。命中后读取 `hit.rigidbody` 判断是否为可击杀目标，读取 `hit.textureCoord`（需 Mesh Collider 且开启 `convex = false`）获取贴图坐标以播放弹孔特效。

例如，《Apex Legends》使用 Respawn 自研引擎 Source 衍生版，射线命中判定在服务端以 20 tick（每帧 50ms）频率重放客户端时间戳对应的场景快照，避免客户端预测与服务端不一致导致的幽灵子弹问题。

**2. 角色控制器站立检测**
角色控制器每帧在脚底向下发射一条长度为 0.1m 的 Raycast（或 SphereCast，半径等于角色碰撞胶囊底部半径 0.3m），检测地面法线夹角：若法线与世界 Y 轴夹角 $\theta < 45°$ 则判定为可行走斜坡，否则触发滑落逻辑。Unity 内置 `CharacterController` 组件的 `slopeLimit` 参数默认值即为 45°。

**3. AI 视线检测（Line of Sight）**
AI 感知系统中，从 NPC 眼睛位置向玩家位置发射 Raycast，使用 `Any` 模式（找到任意遮挡即返回），检测是否被静态遮蔽物阻断。Unreal Engine 的 `AIPerceptionComponent` 内部每 0.1 秒执行一次此类检测，并对多个感知目标进行批量查询以均摊开销。

**4. 传送目标点合法性校验**
《传送门》类玩法中，每帧用 `Physics.OverlapBox` 在传送目标位置测试玩家碰撞体大小的 Box 是否与任何实体碰撞体重叠，若重叠则禁用传送提示 UI。此处使用 Overlap 而非 Sweep，因为目标点是静态候选位置，无需方向信息。

---

## 常见误区

**误区 1：在每帧 Update 中对场景内所有角色各自执行 OverlapSphere**
OverlapSphere 对 $N$ 个角色各查询一次的开销为 $O(N \log M)$（$M$ 为场景形状总数），当 $N = 200$、$M = 5000$ 时，每帧窄相候选测试量可达数万次。正确做法是将范围感知改为事件驱动（角色进入特定区域触发），或使用空间分区数据结构（如八叉树）在游戏逻辑层预筛选，将 Overlap 的候选集控制在 20 以内。

**误区 2：将 Sweep 的 `sweepHit.distance` 直接作为安全移动距离**
`distance` 返回的是几何接触点对应的扫掠距离，物体移动时若直接移动该距离会导致碰撞体穿透（浮点精度问题）。PhysX