---
id: "trigger-volume-engine"
concept: "触发体积"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["事件"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "S"
quality_score: 83.0
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


# 触发体积

## 概述

触发体积（Trigger Volume）是游戏物理引擎中一种特殊的碰撞形状，它能够检测其他物理对象进入、停留或离开其空间范围，但**不产生任何物理碰撞响应**——即不施加力、不阻挡运动、不改变对象的速度或方向。玩家或其他物体可以直接穿越触发体积，仿佛它不存在，但引擎会在后台静默记录这次"穿越"事件并触发相应回调函数。

触发体积的概念伴随着事件驱动游戏逻辑的需求而成熟。早期的2D游戏通过简单的矩形区域检测玩家坐标来实现类似功能，但这属于逐帧手动查询（Polling），在对象数量增多时复杂度以 $O(n^2)$ 级别恶化。随着 Unreal Engine 1（1998年）和后来的 Unity（2005年首发）等引擎引入基于物理层的事件回调机制，触发体积成为标准工具，将"进入特定区域"这一几何事件自动转化为游戏逻辑调用，彻底替代了大量的坐标范围判断代码。

触发体积的核心价值在于**将空间关系与游戏逻辑解耦**。一个关卡设计师无需编写每帧检测玩家位置的代码，只需在场景中放置触发体积并绑定回调，即可实现剧情触发、敌人生成、音效播放、传送门激活等所有"玩家到达某处"才发生的交互。

---

## 核心原理

### 碰撞标志位与物理层过滤

触发体积在物理引擎中本质上是一个将 `isTrigger` 标志位设为 `true` 的碰撞体（Collider/Shape）。以 Unity 为例，Box Collider 勾选 `Is Trigger` 后，底层的 **NVIDIA PhysX 4.1** 引擎会将其从**实体碰撞对（Solid Pair）**列表中移除，加入**触发器对（Trigger Pair）**列表。两类列表在求解器（Solver）阶段的处理完全不同：实体碰撞对会产生接触约束（Contact Constraint），需要经过迭代求解器（默认迭代 4 次位置修正 + 1 次速度修正）处理；而触发器对只执行 AABB 重叠检测（Axis-Aligned Bounding Box Overlap），不进入约束求解步骤，计算开销远低于真实碰撞。

宽相检测（Broad Phase）阶段采用 **SAP（Sweep-and-Prune）算法**，将所有 AABB 在三个坐标轴上的端点排序，时间复杂度为 $O(n \log n)$，相比逐对检测的 $O(n^2)$ 效率大幅提升。触发器对的 AABB 重叠测试判断条件为：

$$
\text{overlap} = (A_{max,x} \geq B_{min,x}) \wedge (A_{min,x} \leq B_{max,x}) \wedge (A_{max,y} \geq B_{min,y}) \wedge (A_{min,y} \leq B_{max,y}) \wedge (A_{max,z} \geq B_{min,z}) \wedge (A_{min,z} \leq B_{max,z})
$$

只有当三个轴向全部满足区间重叠时，才进入窄相（Narrow Phase）的精确形状测试。

### 三种标准回调事件

标准物理引擎为触发体积提供三个生命周期回调，以 Unity 的命名为典型参考：

| 回调函数 | 触发条件 | 调用频率 |
|---|---|---|
| `OnTriggerEnter` | 另一碰撞体首次进入体积的帧 | 仅一次 |
| `OnTriggerStay` | 另一碰撞体持续在体积内部 | 每个物理步长一次 |
| `OnTriggerExit` | 另一碰撞体离开体积的帧 | 仅一次 |

`OnTriggerStay` 默认在每个固定物理时间步（Unity 中默认为 **0.02 秒，即 50 Hz**）执行一次，而非每渲染帧执行——若游戏运行在 120 FPS，`OnTriggerStay` 每帧平均仍只调用 0.02/0.00833 ≈ 2.4 次物理步的频率，与渲染帧率无关。Unreal Engine 中对应的事件名为 `OnComponentBeginOverlap`、`OnComponentEndOverlap` 和 `OnActorBeginOverlap`，概念相同但颗粒度分为组件级（Component）和 Actor 级两层，允许更细粒度地控制哪些网格体部分参与重叠检测。

### 必要触发条件：至少一方需要 Rigidbody

触发体积并非对所有对象都能产生回调。在 PhysX 的规则中，触发器对必须满足：**两个物体中至少有一个拥有 Rigidbody（动力学 Dynamic 或运动学 Kinematic 均可）**。若两个静态碰撞体之间发生重叠，PhysX 不会产生任何触发事件，因为静态对静态的碰撞对在宽相检测之后不会进入窄相处理流程。这一底层规则直接决定了触发体积的使用约束：玩家角色控制器通常需要附带 Rigidbody（或设为 Kinematic），否则即使走进触发体积也不会触发任何事件。

---

## 关键公式与代码实现

### Unity C# 示例：检测点击区域触发剧情

以下代码展示了一个典型的触发体积使用模式——玩家进入 Boss 房间时播放过场动画，离开时停止：

```csharp
using UnityEngine;

[RequireComponent(typeof(Collider))]
public class BossRoomTrigger : MonoBehaviour
{
    [SerializeField] private Animator cutsceneAnimator;
    private int _enterCount = 0; // 用计数器处理多对象同时在区域内的情况

    private void Awake()
    {
        // 确保碰撞体标志位已设置为触发器
        GetComponent<Collider>().isTrigger = true;
    }

    // 仅对持有 "Player" tag 的对象响应，过滤掉子弹等无关对象
    private void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("Player")) return;
        _enterCount++;
        if (_enterCount == 1)
            cutsceneAnimator.SetTrigger("PlayBossIntro"); // 只在第一次进入时播放
    }

    private void OnTriggerExit(Collider other)
    {
        if (!other.CompareTag("Player")) return;
        _enterCount = Mathf.Max(0, _enterCount - 1);
    }

    // OnTriggerStay 在此场景不需要，避免每物理帧产生不必要的开销
}
```

上述代码中使用了 `_enterCount` 整数计数器而非布尔值，这是因为在多人游戏或多碰撞体角色（如带有单独碰撞体的武器）场景下，若仅用 `bool` 标记，第一个玩家离开时会错误重置状态，即使第二个玩家仍在区域内。

### Unreal Engine 蓝图逻辑等价描述

在 Unreal Engine 5 中，触发体积对应的 Actor 类为 `ATriggerVolume`，其内置形状为 `UBoxComponent`，默认尺寸 200×200×200 单位（Unreal Unit，1 UU = 1 厘米）。蓝图中将 `On Component Begin Overlap` 节点连接到 `Cast To BP_Character` 节点，再调用 `Play Cinematic` 序列，三个节点即可实现等价的剧情触发逻辑，无需编写 C++ 代码。

---

## 实际应用

### 典型应用场景

**1. 关卡流加载（Level Streaming）**：《荒野大镖客：救赎 2》（2018，Rockstar Games）使用大量触发体积控制开放世界区域的异步加载与卸载。当玩家骑马接近某区域边界约 200 米时，触发体积启动后台流式加载，确保玩家到达时区域已完整呈现，而无感知到任何加载停顿。

**2. AI 感知区域**：触发体积可用作 AI 的"听觉锥"或"视野边界"的粗略测试。敌人的 SphereCollider（Trigger）半径设为 15 米，`OnTriggerEnter` 时将目标加入"可感知列表"，再由精确射线检测（Raycast）二次过滤，大幅减少每帧的射线数量。

**3. 伤害区域（Damage Zone）**：岩浆、毒雾等持续伤害区域将伤害逻辑写在 `OnTriggerStay` 中，配合物理时间步长 0.02 秒，可精确控制伤害频率为每秒 50 次检查，再乘以 DPS（每秒伤害值）除以 50 即得每步的扣血量：

$$
\Delta HP_{per\_step} = \frac{DPS}{f_{physics}} = \frac{DPS}{50}
$$

例如 DPS = 10 点/秒时，每物理步扣 0.2 点血量，保证无论帧率如何波动，总伤害量恒定。

**4. 音频触发区域（Audio Trigger）**：进入洞穴时，触发体积的 `OnTriggerEnter` 切换混响预设（Reverb Preset）从"室外（Outdoor）"到"洞穴（Cave）"，同时将环境音乐淡出时间设为 2 秒，营造自然过渡效果。

---

## 常见误区

### 误区一：忽略 Rigidbody 必要条件导致回调静默失败

最常见的问题：在静态场景道具（如宝箱）上添加触发体积，但道具本身没有 Rigidbody，玩家角色也没有 Rigidbody（仅使用 CharacterController）。此时 PhysX 静态-静态规则导致回调**永远不会触发**，且 Unity 不会在控制台输出任何警告，表现为"什么都没发生"。解决方案：为玩家角色添加 `Rigidbody`（勾选 `Is Kinematic` 以禁止物理模拟影响移动逻辑），或为触发体积添加 Kinematic Rigidbody。

### 误区二：在 `OnTriggerStay` 中执行高开销操作

`OnTriggerStay` 以物理频率（默认 50 Hz）调用，若在其中执行 `FindObjectOfType<>()` 搜索、大量 GC 分配或复杂 AI 路径计算，会在物理线程上造成严重性能瓶颈。正确做法：`OnTriggerEnter` 时缓存所需引用，`OnTriggerStay` 中仅读取已缓存数据或执行 O(1) 操作。

### 误区三：混淆触发体积与碰撞体的层级遮罩（Layer Mask）

Unity 的 Physics Layer Collision Matrix 控制哪些层之间可以产生碰撞或触发事件。若忘记在矩阵中勾选"Player 层"与"Trigger 层"的交叉项，则即使 `isTrigger` 正确设置，回调同样不会触发。可通过 Edit → Project Settings → Physics → Layer Collision Matrix 检查，这是 PhysX 宽相阶段的第一道过滤，优先级高于 `isTrigger` 标志位本身。

### 误区四：触发体积与触发体积之间的事件

两个均设为 `isTrigger = true` 的碰撞体相互重叠时，PhysX **仍然**会产生触发事件（自 PhysX 3.3 版本起支持触发器-触发器对）。但在 Unity 5.x 之前版本中，此行为不被支持，升级引擎后可能产生意外的额外回调，需在版本迁移时留意。

---

## 知识关联

### 与物理射线检测（Raycast）的对比

触发体积和 Raycast 都能检测"某物是否在某处"，但使用场景不同：

| 特性 | 触发体积 | Raycast |
|---|---|---|
| 检测形状 | 任意 3D 体积（盒体、球体、胶囊等） | 无限细的射线或扫掠体 |
| 调用方式 | 事件驱动（自动回调） | 手动调用（主动查询） |
| 性能特点 | 常驻开销，对象多时宽相压力增加 | 按需调用，单次开销固定 |
| 典型用途 | 区域进入/离开检测 