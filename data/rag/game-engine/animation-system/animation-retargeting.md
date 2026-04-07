---
id: "animation-retargeting"
concept: "动画重定向"
domain: "game-engine"
subdomain: "animation-system"
subdomain_name: "动画系统"
difficulty: 3
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 动画重定向

## 概述

动画重定向（Animation Retargeting）是指将为某一套骨骼系统制作的动画数据，重新映射并应用到另一套结构不同的骨骼系统上的技术。其核心挑战在于两套骨骼之间骨骼数量、命名、旋转轴向以及比例可能存在差异，重定向系统必须建立骨骼间的对应关系并在运行时或烘焙时完成姿势转换。

该技术最早在电影特效行业的动作捕捉管线中被广泛使用。Autodesk MotionBuilder 在 2000 年代初期将角色化（Characterize）工作流引入实时动画领域，定义了"源骨骼"和"目标骨骼"的标准化映射概念。游戏引擎随后吸收了这一思路：虚幻引擎（Unreal Engine）在 UE4.5 版本中正式内置了 IK Rig Retargeter 的前身，Unity 则通过 Humanoid Avatar 系统在 Unity 4.0 中实现了跨骨骼动画共享。

动画重定向的实际价值在于显著降低动画资产的制作成本。一套高质量的运动捕捉数据集，通过重定向可以同时驱动游戏中高挑精灵、矮壮矮人、四足怪物等多种体型迥异的角色，而无需为每个角色单独录制或手工制作动画。

---

## 核心原理

### 骨骼映射（Bone Mapping）

骨骼映射是重定向的基础步骤，负责建立源骨骼（Source Skeleton）与目标骨骼（Target Skeleton）之间的一对一或多对一对应关系。Unity 的 Humanoid Avatar 系统将人形骨骼分为 15 个必须骨骼（Required Bones，包括 Hips、Spine、Head 等）和 37 个可选骨骼（Optional Bones），映射时只要必须骨骼存在，即可完成基础重定向。Unreal Engine 5 的 IK Retargeter 则通过 IK Rig 中的 Retarget Chain 概念，将骨骼链（如整条脊椎链或整条手臂链）作为映射单元，而非逐个骨骼匹配，这样可以处理两套骨骼在中间节点数量上的差异。

### 参考姿势对齐（Reference Pose Alignment）

两套骨骼的绑定姿势（Bind Pose 或 T-Pose/A-Pose）中骨骼的旋转朝向往往不同。若直接传递旋转四元数，目标骨骼会出现严重扭曲。重定向系统通过计算**旋转偏移量（Rotation Offset）**来修正这一问题：

```
Q_target = Q_offset_inv × Q_source × Q_offset
```

其中 `Q_offset = Q_target_bind_inv × Q_source_bind`，即目标绑定姿势旋转的逆乘以源绑定姿势旋转。Unreal Engine 要求在配置 IK Rig 时为每套骨骼单独设置 Retarget Pose，本质上就是手动修正各骨骼在参考姿势下的朝向偏差。

### 比例适配（Proportional Scaling）

当源角色（如身高 180cm 的人类）的动画应用到体型差异极大的目标角色（如身高 80cm 的矮人）时，若直接传递骨骼的世界空间位移，矮人将迈出相对自身腿长极不自然的大步伐。比例适配有两种主流策略：

- **归一化方案**：将位移值除以源骨骼的参考长度，再乘以目标骨骼的对应参考长度。公式为 `D_target = D_source × (L_target / L_source)`，其中 `L` 代表对应骨骼链的静息长度。
- **根骨骼位移缩放**：仅对根骨骼（Root Bone）的位移按全身高度比例缩放，子骨骼旋转直接继承，这是 Unity Humanoid 的默认策略，适合大多数双足角色但对手臂触及特定位置的动画会产生误差。

### IK 后处理修正

纯骨骼旋转重定向无法保证脚部精确落地。现代重定向管线会在重定向完成后叠加一层 **IK 解算**（如 Two-Bone IK 或 Full Body IK），将脚部末端效应器（Effector）约束到地面，消除因腿长比例差异造成的脚步悬空或穿地问题。Unreal Engine 5 的 IK Retargeter 内置了 Full Body IK（FBIK）后处理节点，可在重定向链计算完毕后自动执行此步骤。

---

## 实际应用

**跨角色动画库共享**：《堡垒之夜》（Fortnite）拥有数百个外观迥异的皮肤角色，其底层使用统一的标准人形骨骼制作动画，通过重定向驱动所有皮肤角色，避免了为每个皮肤单独制作动画集的天文成本。

**动作捕捉数据再利用**：动捕演员通常只有一种体型，采集的 BVH 或 FBX 数据要应用到游戏中的各种角色时，需先通过重定向工具（如 MotionBuilder 的 Control Rig 或 UE5 的 IK Retargeter）将数据适配到目标角色骨骼。Mixamo 提供的免费动画库使用标准 Mixamo 骨骼制作，开发者需在 Unity 或 Unreal 中将其重定向到自己的角色骨骼上使用。

**运行时动态重定向**：在多人网络游戏中，服务器可只传输一套动画数据，客户端根据各自角色的骨骼比例在本地实时执行重定向解算，减少网络带宽消耗。

---

## 常见误区

**误区一：骨骼命名一致就能自动完成重定向**
部分开发者认为只要两套骨骼的命名相同（如都叫 `Spine_01`），重定向就会自动完美工作。实际上，骨骼命名只能帮助工具自动完成初步映射，但骨骼的局部旋转轴向（Local Axis Orientation）差异仍会导致参考姿势不对齐，仍需手动调整 Retarget Pose。

**误区二：重定向只适用于人形角色**
实际上重定向技术可以应用于任何具有骨骼系统的角色，包括四足动物、机械臂、面部骨骼等。Unreal Engine 的 IK Retargeter 并不限定角色类型，Unity 的 Generic Avatar 同样支持非人形骨骼重定向，只是需要手动配置映射关系而非依赖 Humanoid 的自动识别。

**误区三：重定向后不需要任何手工修正**
对于需要精确交互的动画（如角色抓取特定道具、双手剑握持姿势），重定向后末端骨骼的位置往往无法精确对齐目标位置。此时必须结合 AimOffset、AdditiveAnimation 或 IK 约束进行逐帧修正，纯重定向无法替代针对性的动画调整工作。

---

## 知识关联

动画重定向直接建立在**骨骼系统**的基础知识之上：理解骨骼层级（Bone Hierarchy）、局部空间与世界空间变换、以及绑定姿势的概念是正确配置重定向的前提。若对骨骼旋转的四元数表示和父子空间变换不熟悉，将难以诊断重定向后出现的骨骼扭曲问题。

在动画状态机（Animation State Machine）和混合树（Blend Tree）的应用场景中，重定向后的动画与原生动画在数据结构上完全一致，可直接接入现有的动画蓝图或 Animator Controller，无需为重定向动画单独设计播放逻辑。骨骼重定向与**姿势空间变形（Pose Space Deformation）**和**布料模拟**等技术的交互需要注意：这些依赖骨骼绝对位置的技术，在角色比例发生较大变化后可能需要重新校准权重参数。