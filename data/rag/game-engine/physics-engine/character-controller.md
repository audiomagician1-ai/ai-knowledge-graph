---
id: "character-controller"
concept: "角色控制器"
domain: "game-engine"
subdomain: "physics-engine"
subdomain_name: "物理引擎"
difficulty: 2
is_milestone: false
tags: ["角色"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 41.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 角色控制器

## 概述

角色控制器（Character Controller）是游戏引擎物理模块中专为可操控角色设计的运动组件，其核心特征是**绕过刚体动力学**，通过运动学（Kinematic）方式直接控制位移，同时保留与场景几何体的碰撞检测能力。与普通刚体相比，角色控制器不受重力、摩擦力、弹力等物理模拟影响，开发者完全通过代码逻辑驱动位移，从而实现手感精准、响应即时的角色移动。

角色控制器的概念最早在第一人称射击游戏时代得到系统化实现。Quake（1996年）时代的引擎已包含专用的玩家碰撞移动代码，其楼梯步进和斜面滑动算法成为后来专用角色控制器组件的原型。Unity在5.0版本之前使用CharacterController作为官方推荐的角色移动方案，PhysX引擎（Unreal Engine和Unity的底层物理库）中的`PxController`至今仍是工业级角色控制器的标准实现。

角色控制器的存在解决了一个实际矛盾：游戏角色需要稳定站立在不规则地形上、顺畅越过台阶、沿斜坡平滑滑动，而普通刚体在这些场景中会产生抖动、卡边、翻倒等无法接受的表现。角色控制器通过三个特定机制——胶囊体碰撞形状、楼梯步进、斜面处理——系统性地解决这些问题。

---

## 核心原理

### 胶囊体碰撞形状

角色控制器几乎统一采用**胶囊体（Capsule）**作为碰撞形状，而非方形包围盒或球体。胶囊体由一个圆柱体加两个半球端帽构成，在Unity的CharacterController中由`height`（总高，默认2米）和`radius`（半径，默认0.5米）两个参数定义。

选择胶囊体的原因非常具体：其底部的半球曲面能自动将角色从障碍物边缘"推滑"出去，避免角色被地面微小凸起卡住；圆形截面使角色在转弯时不会因碰撞体角点刮蹭墙壁；相比球体，胶囊体的高度可以调整以匹配人形角色的纵向比例。正因如此，哪怕是矩形外观的角色（如像素风游戏），底层碰撞体仍然推荐使用胶囊而非方盒。

### 楼梯步进（Step Offset）

楼梯步进是角色控制器允许角色**无需跳跃即可越过低矮障碍**的机制。其工作原理是：当控制器检测到前方存在高度低于`stepOffset`阈值的垂直障碍时，将角色直接抬升到障碍顶面，而非将其阻挡。

在PhysX的实现中，步进检测通过在角色脚部发射一条向下的射线来探测前方台阶高度，Unity CharacterController的`stepOffset`参数默认值为**0.3米**，意味着角色可以自动越过不超过30厘米的台阶。该参数必须小于`height - 2 * radius`，否则控制器会报错，因为步进高度不能超过胶囊体圆柱段长度。如果将`stepOffset`设置为0，角色将无法自动越过任何台阶，必须依赖跳跃逻辑。

### 斜面处理（Slope Limit）

角色控制器通过`slopeLimit`参数定义**角色可攀爬的最大斜面角度**，超过该角度的斜面会阻挡角色或使其沿斜面滑落。Unity中该参数默认值为**45度**。

当角色尝试移动到超过`slopeLimit`的斜面上时，控制器将水平位移分解为垂直于斜面法线的分量，只保留沿斜面切线方向的分量，结果是角色沿陡坡侧向滑动而非翻越。这一分解公式为：

$$\vec{v}_{slide} = \vec{v} - (\vec{v} \cdot \hat{n})\hat{n}$$

其中 $\vec{v}$ 为输入速度向量，$\hat{n}$ 为斜面法线单位向量，$\vec{v}_{slide}$ 为实际位移方向。对于可攀爬范围内的斜面，控制器则直接允许移动并附加一个沿斜面向上的位移分量，使角色贴合坡面行走。

---

## 实际应用

**第一人称射击游戏移动系统**：Unity中使用`CharacterController.Move(velocity * Time.deltaTime)`逐帧驱动角色位移，搭配手动编写的重力累加逻辑（`verticalVelocity -= gravity * Time.deltaTime`），完全绕过刚体物理，实现CS:GO风格的即时响应移动。

**平台跳跃游戏的土狼时间（Coyote Time）**：角色控制器的`isGrounded`属性在角色走出平台边缘后的1-2帧内仍可能返回`true`，开发者会特意利用或对抗这一行为，额外记录一个0.1~0.15秒的宽限计时器，允许玩家在离开平台后仍能起跳，提升手感。

**Unreal Engine的Character组件**：UE的`UCharacterMovementComponent`在角色控制器基础上预置了步进、斜面、游泳、飞行等多种移动模式的完整状态机，其`MaxStepHeight`默认为45厘米，`WalkableFloorAngle`默认为44度，开发者可在蓝图中直接调整这些参数而无需修改物理代码。

---

## 常见误区

**误区一：认为角色控制器会自动处理重力**。角色控制器本身**不施加重力**，它仅负责碰撞响应和移动。开发者必须在代码中手动维护`verticalVelocity`变量，每帧累加重力加速度（通常取-9.8 m/s²），再将其传入`Move()`。初学者常因忘记这一点，看到角色能无限漂浮在空中。

**误区二：混淆stepOffset与碰撞体大小的关系**。部分开发者调大`stepOffset`试图让角色越过更高的台阶，但当`stepOffset`超过胶囊体圆柱段高度时，控制器会失效甚至崩溃。正确做法是`stepOffset < height - 2 * radius`，越过高台阶应通过跳跃逻辑而非增大步进参数实现。

**误区三：对快速移动的角色依然使用角色控制器做穿墙检测**。角色控制器基于每帧离散位移检测碰撞，若角色单帧移动距离超过碰撞体直径（如子弹时间反转角色或高速传送），仍会发生穿透。此场景需要额外的扫掠测试（`Physics.CapsuleCast`）配合使用。

---

## 知识关联

**前置概念——碰撞形状**：理解为何选择胶囊体而非方盒或球体，需要先掌握各种碰撞形状的几何特性。胶囊体的底部半球是角色控制器自动越障能力的几何基础，球体会导致角色在平地上滚动，方盒则会在转角处卡顿，这些差异直接决定了角色控制器的设计选型。

**衍生应用——物理层（Physics Layer）与碰撞矩阵**：角色控制器在复杂场景中需要通过Layer Mask控制与哪些物体产生碰撞响应，例如让角色穿过触发器体积（Trigger）但阻挡于实体墙体。这是在角色控制器基础上进行场景交互设计的必要配套知识，涉及Unity中`CollisionDetectionMode`的配置以及Unreal中碰撞通道（Collision Channel）的设置。
