---
id: "vfx-vfxgraph-collision"
concept: "碰撞与交互"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
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


# 碰撞与交互

## 概述

在 Unity VFX Graph 中，碰撞与交互系统允许粒子与场景几何体或深度缓冲图像发生物理响应，而不仅仅是在空间中自由飘散。VFX Graph 提供两种主要碰撞方式：**Collide with Depth Buffer**（深度缓冲碰撞）和 **Collide with Sphere/Plane** 等解析几何碰撞，前者利用相机深度纹理实现屏幕空间近似碰撞，后者在粒子仿真空间中进行精确几何求交。

深度缓冲碰撞技术最早随 GPU 粒子系统的普及而兴起，其本质是将相机渲染的深度图作为场景形状的近似代理。Unity 的 VFX Graph 在 2019.3 版本后将深度碰撞模块正式纳入 Block 系统，使艺术家无需编写 HLSL 代码即可配置粒子对场景表面的弹跳与附着行为。

碰撞与交互系统的重要性在于它将视觉效果从"叠加层"变为"场景参与者"：雨滴可以落到地面溅起水花，灰尘可以堆积在障碍物边缘，子弹击中墙壁时可以触发火花粒子。理解这一模块是制作具有物理可信度特效的关键步骤。

---

## 核心原理

### 深度缓冲碰撞（Collide with Depth Buffer）

该 Block 在 Update Context 中工作，每帧读取当前相机的 `_CameraDepthTexture`，将粒子的世界坐标投影到屏幕空间，与采样到的深度值比较。当粒子的投影深度大于或等于深度纹理中的值时，判定发生碰撞。

碰撞响应由两个关键参数控制：
- **Elasticity（弹性系数）**：范围 0～1，0 表示完全吸附（粒子停在表面），1 表示完全弹性反弹。反射速度向量由法线重建算法通过相邻深度采样点的差分计算得到。
- **Roughness（粗糙度）**：在弹射速度上叠加随机扰动，模拟不平整表面散射，值越高粒子弹射方向越随机。

深度缓冲碰撞的核心局限是**屏幕空间单面性**：被遮挡的几何体背面、摄像机视锥体外部区域均无法参与碰撞检测。这意味着粒子穿过建筑背后时不会产生碰撞响应。

### 解析几何碰撞（Collide with Sphere / Plane / AABox）

解析碰撞在粒子仿真坐标系中进行精确求交，不依赖相机信息，因此在任何视角下都成立。以球体碰撞为例，判定条件为：

```
distance(particle.position, sphere.center) <= sphere.radius + particle.radius
```

碰撞后速度的反射公式为：
```
v' = v - (1 + e) * (v · n̂) * n̂
```
其中 `e` 为弹性系数，`n̂` 为碰撞点法线单位向量，`v` 为碰撞前速度向量。解析碰撞的计算代价比深度缓冲碰撞高，但精度更稳定，适合数量在十万以下的精确物理特效。

### 碰撞事件触发（Collision Event）

VFX Graph 的碰撞系统与其 **Event 机制**深度集成。在 Update Context 的碰撞 Block 中，可以开启 **Kill on Collision** 选项，或者通过 **Trigger Event on Die** / **Trigger Event Rate** Block，在粒子碰撞销毁的瞬间向指定 Event 端口发送信号。

接收该事件的子系统（Spawner）会在碰撞坐标处生成新粒子，实现级联特效。例如：主系统发射"子弹粒子"，碰撞事件触发"火花"子系统，火花粒子自身死亡又触发"烟雾"子系统。这种多层事件链在一个 VFX Graph Asset 内通过 **Sub-output Context** 和 **GPU Event** 连接，整条链路完全在 GPU 上执行，无需经过 CPU 回调，延迟极低。

---

## 实际应用

**雨水溅落效果**：主粒子系统使用深度缓冲碰撞，Elasticity 设为 0.05 使水滴几乎不弹跳，碰撞后触发 GPU Event 生成溅射涟漪子系统。涟漪粒子使用 Flipbook 动画纹理，初始 Scale 较小并在 0.3 秒内放大至消失，营造真实水面交互感。

**粒子堆积在台阶边缘**：对场景中存在明显轮廓的几何体（如楼梯台阶），使用 Collide with Plane 配置多个平面碰撞，Elasticity = 0，Roughness = 0.8，使粒子落地后沿平面随机滑动并堆积，模拟沙尘或积雪的自然堆积形态。

**Boss 死亡爆炸链**：主爆炸粒子数量约 500 个，每个粒子碰撞死亡时 Trigger Event，每次事件生成 3～8 个次级火花，形成指数扩散的视觉层次。为防止粒子数量失控，次级系统设置 Capacity 上限为 8000，超出时旧粒子自动销毁。

---

## 常见误区

**误区 1：认为深度缓冲碰撞适用于第一人称视角下的全场景**
深度缓冲碰撞仅对相机可见的前向表面有效，对于 FPS 游戏中玩家背后的爆炸粒子，相机看不到的部分场景几何体会被完全忽略，粒子将穿透地面。解决方案是对关键碰撞面补充一个不可见的 Collide with Plane Block。

**误区 2：将碰撞事件误接到 Initialize Context 而非 Spawner**
GPU Event 输出端口必须连接到一个独立子系统的 **GPU Event Spawner**，而不能直接连接到同一系统的 Initialize Context。错误连接会导致 Graph 编译警告且碰撞事件不会生效，初学者常因此以为碰撞触发功能本身有 Bug。

**误区 3：对高密度粒子（百万级）使用解析碰撞**
解析几何碰撞为每个粒子每帧执行一次 GPU 线程内的求交运算。当粒子数量超过 100 万时，同时配置多个球体碰撞 Block 会造成 GPU 线程发散严重，帧率下降明显。百万粒子的环境碰撞应优先选择深度缓冲碰撞，将 GPU 计算量控制在合理范围内。

---

## 知识关联

**前置概念——力与运动**：碰撞响应的速度反射公式直接作用于粒子的 Velocity 属性，这一属性正是由 Constant Force、Turbulence 等力 Block 在每帧积分更新的。没有正确配置粒子的初始速度和重力，碰撞后的弹跳方向与距离将无法产生可信的物理感。

**后续概念——输出模式**：碰撞后的粒子状态（附着在表面的粒子）往往需要切换为 Mesh Surface Output 或 Decal Output，使其贴合几何表面渲染，而非使用默认的 Billboard Output 悬浮在空中。

**后续概念——碰撞物理**：本模块介绍的是 VFX Graph 层面的近似碰撞；碰撞物理模块将进一步讲解如何通过 C# 脚本将 Unity 物理引擎（PhysX）的碰撞结果以 Event 形式发送给 VFX Graph，实现 CPU 物理与 GPU 粒子的精确联动，适用于需要与刚体交互的高精度场景。