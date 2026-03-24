---
id: "root-motion"
concept: "Root Motion"
domain: "game-engine"
subdomain: "animation-system"
subdomain_name: "动画系统"
difficulty: 2
is_milestone: false
tags: ["移动"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Root Motion（根骨骼驱动移动）

## 概述

Root Motion 是动画系统中的一种技术，允许角色的世界空间位置和旋转直接由动画片段中根骨骼（Root Bone）的运动数据来驱动，而不是由游戏逻辑代码单独控制。例如在一段跑步动画中，角色的脚步与地面接触的相对位移被烘焙进骨骼数据，播放时引擎读取这段位移并真实更新角色的 Transform，使动画表现与物理世界严格同步。

这项技术最初在主机游戏开发中普及，Unity 在 2010 年发布的 Mecanim 动画系统（Unity 4.x）将 Root Motion 作为一等公民纳入引擎工作流，Unreal Engine 的 Root Motion From Montage 功能也在 UE4 时代得到完善。在此之前，开发者通常需要手动在代码中偏移角色位置，导致动画滑步（Foot Sliding）问题极为普遍。

Root Motion 对于近身格斗、翻滚、攀爬等需要精确空间位移的动作至关重要。若一个格斗技能动画内置了向前冲刺 1.2 米的位移曲线，启用 Root Motion 后，角色在游戏中实际移动的距离和速度与动画师的设计完全一致，无需开发者猜测并硬编码速度值。

## 核心原理

### 根骨骼与位移提取

骨骼层级的最顶端节点称为根骨骼（通常命名为 `root` 或 `Hips`），所有其他骨骼都是其子节点。动画片段中每一帧都存储了根骨骼相对于上一帧的增量位移（Delta Position）和增量旋转（Delta Rotation）。引擎在每帧 Tick 时提取这个增量值：

> **Delta Position = RootPos(frame N) − RootPos(frame N−1)**

引擎将此增量应用到角色的世界坐标，同时将根骨骼本身在骨骼空间内归零（保持在原点），确保动画循环时角色不会因骨骼积累偏移而产生视觉跳变。

### In-Place 动画 vs Root Motion 动画

In-Place（原地）动画的根骨骼在整个片段中 XZ 平面坐标不变，移动完全由代码中的 `CharacterController.Move()` 或 `Rigidbody.velocity` 驱动。Root Motion 动画则将这段位移烘焙在骨骼轨道上，二者不可混用——若对一段 Root Motion 动画同时叠加代码速度，角色会以两倍速移动。区分这两种类型是使用 Root Motion 的前提。

### 旋转轴的处理

Root Motion 可以独立控制三个平移轴（X、Y、Z）和旋转轴（Y 轴偏航最常用）。Unity 的 Animator 组件提供了 `applyRootMotion` 布尔值，以及 `OnAnimatorMove()` 回调，开发者可在该回调中仅应用 Y 轴旋转（`animator.deltaRotation`）而忽略 Y 轴位移，满足平台游戏中角色跳跃时动画自带上升曲线但需物理引擎接管的需求。Unreal Engine 则通过 Root Motion Settings 面板的 **Force Root Lock** 与 **No Root Motion Extraction** 模式实现类似的细粒度控制。

### 循环动画的首尾对齐

一段 60 帧的跑步循环，若首帧根骨骼位于 (0,0,0)，尾帧位于 (0,0,1.5m)，则循环播放时引擎每次循环累积 1.5m 的位移，角色持续前进。动画师必须保证循环片段的骨骼姿态首尾匹配，但根骨骼的位移不必归零——正是这段不归零的净位移构成了 Root Motion 的每循环步进量。

## 实际应用

**格斗技能位移**：一个下劈攻击动画包含向前 0.8m 的冲步位移，启用 Root Motion 后角色在碰撞到墙壁时可被物理层自动阻挡，而 In-Place 方案需要开发者额外射线检测并手动停止位移。

**翻滚与闪避**：翻滚动画通常在第 12 帧到第 28 帧之间有剧烈的位移曲线，开发者可在 `OnAnimatorMove()` 中将该位移乘以一个 `dashMultiplier` 系数，在不修改动画源文件的情况下允许玩家升级获得更长的翻滚距离。

**过场动画与布景交互**：角色爬梯子、翻越障碍物的动画依赖 Root Motion 与特定位置的环境对齐（Warping），Unreal Engine 5 的 **Motion Warping** 系统基于 Root Motion 提取，可将动画的根骨骼轨迹实时扭曲以对齐目标位置，无需为每个障碍高度单独制作动画。

**网络多人游戏**：服务器端每帧同步 `deltaPosition` 而非绝对坐标，减少带宽；客户端对 Root Motion 进行预测，在延迟 100ms 以内的情况下动画与位置的一致性优于纯代码驱动方案。

## 常见误区

**误区一：Root Motion 会自动处理所有碰撞**

Root Motion 只负责将动画中的位移数据传递给角色控制器，碰撞检测仍需 `CharacterController` 或 `Rigidbody` 正常工作。若将角色的 `CharacterController` 禁用后启用 Root Motion，角色会穿透墙壁，因为位移被直接写入 Transform 而绕过物理层。

**误区二：Root Motion 动画必须重新导出才能修改速度**

可以在 Unity 的 Animator State 中勾选 **Multiply by Speed** 或在 Unreal 的蒙太奇中缩放播放速率，Root Motion 的提取量与播放速率成正比，1.5 倍速播放即产生 1.5 倍的每帧增量位移，无需返回 DCC 工具修改动画。

**误区三：Root Motion 适用于所有移动类型**

对于需要响应即时输入的持续跑步、游泳等状态，In-Place + 代码速度控制通常更灵活，因为代码速度可以在任意帧被修改。Root Motion 最适合时长确定、位移固定的一次性动作（如技能、交互），而非每帧都需要速度可变的循环状态。

## 知识关联

Root Motion 直接依赖**动画片段**（Animation Clip）的正确配置：片段必须在导入设置中标记根骨骼轨道为"Bake Into Pose"的对立选项——即不将位移烘焙到姿态，而是保留为可提取的 Root Motion 轨道。在 Unity 中，这对应 Animation Import Settings 里 **Root Transform Position (XZ)** 设为 "Original"。

在更高阶的动画系统中，Root Motion 是**动画状态机**过渡混合、**Inverse Kinematics（IK）** 地面对齐，以及 **Motion Matching** 技术的基础数据来源；Motion Matching 系统通过对比候选帧的根骨骼未来轨迹与角色期望轨迹来选帧，没有正确提取的 Root Motion 数据，该系统无法工作。
