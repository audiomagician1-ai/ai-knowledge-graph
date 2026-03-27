---
id: "vfx-vfxgraph-force"
concept: "力与运动"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 力与运动

## 概述

在 Unity VFX Graph 中，**力与运动**指通过施加各类物理力（Force、Drag、Turbulence 等 Block）来驱动粒子位置和速度随帧更新的机制。与传统粒子系统不同，VFX Graph 的力作用于 GPU 线程上的每个粒子，可在单帧内并行处理数百万粒子的速度积分，而不依赖 CPU 的 FixedUpdate 物理步长。

这一机制源于 2018 年 Unity 引入 HDRP + VFX Graph 时为影视级特效设计的需求：需要在不启用 Unity Physics 引擎的前提下，让粒子表现出类物理行为。因此，VFX Graph 的力是**近似模拟**，而非严格求解物理方程，所有力的计算发生在 `Update Particle` 上下文（Context）的 Block 执行阶段。

掌握力与运动的意义在于：仅靠 Spawn 阶段赋予的初速度只能生成直线运动，而绝大多数特效（火焰上浮、爆炸扩散、飘动粒子）都依赖运行时持续施加的力来产生非线性轨迹。错误地将力 Block 放入 `Initialize Particle` 上下文只会在出生时执行一次，导致效果完全失效。

---

## 核心原理

### 1. 速度积分与力的累加模型

VFX Graph 在每个 `Update Particle` 帧中使用**欧拉积分**更新粒子运动：

```
velocity += force × deltaTime
position += velocity × deltaTime
```

`deltaTime` 由系统自动注入，对应当前帧时间间隔（秒）。多个力 Block 在同一 Update 上下文中**串行叠加**，最终 velocity 是所有 Block 贡献之和。因此，Block 的排列顺序影响计算结果——将 Drag 放在 Gravity 之前与之后，会因中间速度值不同而产生细微差异。

### 2. 内置力 Block 及其参数

**Gravity（重力）**：施加恒定加速度向量，默认值为 `(0, -9.81, 0)` m/s²，可绑定属性系统中的 Vector3 属性覆盖默认方向，用于模拟反重力或侧向重力场景。

**Linear Drag（线性阻力）**：公式为 `force = -drag × velocity`，`drag` 系数越大粒子减速越快。将 drag 设为 `2.0` 可让粒子在约 0.5 秒内接近静止（指数衰减特性）。Drag 不会让粒子反向运动，与 Wind 配合时先施加 Wind 再施加 Drag 可模拟空气阻力效果。

**Force Field（力场）**：引用场景中的 `VFX Force Field` 组件（需 HDRP），支持 Drag、Gravity、Vortex、Turbulence 四种子类型，影响半径和衰减曲线均可在组件 Inspector 中调整。粒子进入力场包围盒时才受到影响，可用于局部风洞或黑洞吸引效果。

### 3. 湍流与噪声驱动运动

**Turbulence Block** 是 VFX Graph 中最常用的非线性力来源，内部使用**Curl Noise**（旋度噪声）生成无散度的速度场，保证粒子在三维空间中形成涡旋流动而不聚集或发散。关键参数包括：

- **Intensity**：噪声速度的强度倍数，典型值 `0.5–3.0` 对应轻风到强乱流
- **Frequency**：噪声空间频率，值越高湍流细节越密集；`1.0` 对应约 1 米尺度的涡旋
- **Speed**：噪声场随时间平移的速率，产生动态流动感

Turbulence 与 Gravity 叠加时，可通过将 Intensity 设为粒子生命周期属性（`Age/Lifetime` 曲线采样）实现粒子刚出生时飘散、末期受重力主导下落的自然过渡。

### 4. 速度限制与稳定性

无限制地累加力会导致粒子速度爆炸（尤其在高 Turbulence Intensity 下）。VFX Graph 提供 **Clamp Velocity** Block，将速度向量模长限制在指定最大值内。建议在所有力 Block 之后添加此 Block，最大速度值依据效果需求设置，火焰类特效通常限制在 `5–10` m/s，爆炸冲击波可设至 `50` m/s 以上。

---

## 实际应用

**火焰上升效果**：在 `Update Particle` 中依次放置：① `Turbulence`（Intensity=1.5，Frequency=0.8）产生火舌摆动；② `Gravity`（值设为 `(0, -3, 0)` 而非默认 -9.81 以模拟热气上浮的净效果）；③ `Clamp Velocity`（Max=8）。配合 `Age over Lifetime` 缩小粒子 Scale，可还原篝火火苗形态。

**子弹穿透气流**：使用场景中放置的 `VFX Force Field` 组件，设置 Vortex 类型，绑定子弹 Transform 作为力场中心（通过脚本动态更新 `VFXForceField` 组件位置），粒子飞过时产生螺旋尾迹，无需编写任何 CPU 端的粒子运动代码。

**水面涟漪粒子**：将 Turbulence 的 Speed 参数绑定到随时间变化的正弦函数（通过 Custom HLSL 节点实现），使噪声场周期性反向平移，粒子呈现往复波动而非单向流动，适合水面泡沫或圣光粒子特效。

---

## 常见误区

**误区一：把力 Block 放入 Initialize Particle 上下文**
Initialize 上下文仅在粒子出生帧执行一次。将 Gravity 或 Turbulence 放在 Initialize 中，会让粒子只在出生瞬间获得一次速度增量，此后匀速直线运动，而非持续加速。力 Block 必须放在 `Update Particle` 中才能每帧持续作用。

**误区二：认为 Turbulence 等同于随机位移**
Turbulence 使用的 Curl Noise 是**空间连续**且**时间连续**的向量场，同一位置的相邻粒子会获得相似的速度方向，因此形成流线感。若改用逐粒子的随机偏移（如 `Random Number` 驱动 Set Velocity），粒子会各自随机抖动，丢失流体感。两者视觉效果差异明显，不可互换。

**误区三：Drag 系数与物理引擎的 Linear Drag 含义相同**
Unity Rigidbody 的 `linearDamping` 使用的是归一化阻尼（0=无阻力，1=临界阻尼），而 VFX Graph Drag Block 的 drag 值是直接乘以速度的系数（无量纲上限），设置为 `1.0` 并非"完全阻尼"，粒子仍会继续运动，只是每帧速度减少 `drag × deltaTime` 的比例。

---

## 知识关联

**前置知识——属性系统**：力 Block 的 Intensity、Direction 等参数可暴露为 VFX 属性（Exposed Property），由外部 C# 脚本通过 `visualEffect.SetFloat()`、`SetVector3()` 动态修改，实现运行时风向切换、技能触发爆炸力等交互逻辑。若未掌握属性绑定机制，力参数只能在编辑器中静态配置。

**后续方向——碰撞与交互**：粒子在力驱动下运动后，需要与场景几何体发生碰撞反弹，这依赖 VFX Graph 的 Collider Block 和 Depth Buffer Collision，碰撞响应中的摩擦力和反弹系数本质上也是对速度向量的修改，与力 Block 同属速度操控体系。

**后续方向——湍流与噪声**：Turbulence Block 底层的 Curl Noise 算法（基于 Perlin/Simplex Noise 的旋度计算）有更深层的参数可通过自定义 HLSL 节点覆盖，包括分形叠加层数（Octave）、持久性（Persistence）等，是进阶创作复杂流体特效的基础。