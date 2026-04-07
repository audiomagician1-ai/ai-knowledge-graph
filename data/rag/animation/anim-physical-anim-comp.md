---
id: "anim-physical-anim-comp"
concept: "Physical Animation组件"
domain: "animation"
subdomain: "physics-animation"
subdomain_name: "物理动画"
difficulty: 3
is_milestone: false
tags: ["引擎"]

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



# Physical Animation组件

## 概述

Physical Animation组件（`UPhysicalAnimationComponent`）是Unreal Engine提供的专用C++组件，用于在骨骼网格体的物理模拟与动画系统之间构建受控的弹性混合效果。其底层机制是通过PhysX/Chaos物理引擎的约束电机（constraint motor）在每个物理子步中向已激活物理模拟的骨骼刚体施加扭矩与力，使其持续"追逐"当前动画姿势，而非进入完全无控制的自由布娃娃（ragdoll）状态。

该组件以稳定API形式首次出现于UE4.14（2016年11月发布），专门解决游戏开发中"半布娃娃"（partial ragdoll）场景的控制问题——例如角色中弹时下半身倒地、上半身仍播放射击动画，或角色被推撞时肢体产生物理晃动而躯干继续跟随导航路径运动。传统布娃娃系统（`SetSimulatePhysics(true)`）一旦激活，角色姿态完全由刚体碰撞决定，动画数据被完全丢弃；而纯动画混合（Animation Blending）又无法响应真实碰撞冲量。Physical Animation组件填补了两者之间的空白，是实现"有物理质感的动作角色"的核心工具。

参考资料：Epic Games官方文档《Physical Animation Component》（docs.unrealengine.com，2023）；以及游戏物理动画领域的经典论著《Game Physics Engine Development》(Millington, 2010, CRC Press) 中关于约束电机驱动的相关章节。

---

## 核心原理

### 物理动画数据结构 FPhysicalAnimationData

所有参数配置通过`FPhysicalAnimationData`结构体传递，调用`ApplyPhysicalAnimationSettings`或`ApplyPhysicalAnimationSettingsBelow`时作为参数传入。结构体的关键字段及典型取值如下：

| 字段 | 类型 | 典型值 | 说明 |
|---|---|---|---|
| `bIsLocalSimulation` | bool | `true` | `true`=骨骼局部空间计算约束力，稳定性更高；`false`=世界空间，适合位置锚定 |
| `OrientationStrength` | float | 1000～10000 | 旋转追逐力，过高时碰撞刚度过大，过低时骨骼无法回正 |
| `AngularVelocityStrength` | float | 100～1000 | 旋转阻尼，防止骨骼在目标姿势附近震荡，建议约为OrientationStrength的1/10 |
| `PositionStrength` | float | 0（局部模式）或1000 | 仅`bIsLocalSimulation=false`时有效，控制位置追逐 |
| `VelocityStrength` | float | 100～500 | 线速度阻尼，配合PositionStrength防止位置超调 |
| `MaxLinearForce` | float | OrientationStrength × 10 | 施加线性力上限，防止极端碰撞产生爆炸性力反馈 |
| `MaxAngularForce` | float | OrientationStrength × 10 | 施加角力矩上限，建议与MaxLinearForce同量级 |

### 激活流程与绑定顺序

Physical Animation组件的生效依赖严格的调用顺序，共三步，缺一不可：

**第一步**：在`BeginPlay`之后调用`SetSkeletalMeshComponent`完成组件绑定：
```cpp
// 必须在BeginPlay或之后调用，不能在构造函数中调用
PhysicalAnimationComponent->SetSkeletalMeshComponent(GetMesh());
```

**第二步**：对目标骨骼以下的物理体开启物理模拟：
```cpp
// 第三个参数true表示包含目标骨骼自身
GetMesh()->SetAllBodiesBelowSimulatePhysics(FName("pelvis"), true, true);
```

**第三步**：应用Physical Animation参数：
```cpp
FPhysicalAnimationData AnimData;
AnimData.bIsLocalSimulation = true;
AnimData.OrientationStrength = 3000.f;
AnimData.AngularVelocityStrength = 300.f;
AnimData.MaxAngularForce = 30000.f;
AnimData.MaxLinearForce = 30000.f;

PhysicalAnimationComponent->ApplyPhysicalAnimationSettingsBelow(
    FName("pelvis"),   // 从pelvis骨骼以下全部应用
    AnimData,
    true               // bIncludeSelf=true，pelvis自身也应用
);
```

若跳过第一步直接调用Apply函数，函数会**静默失败**，不输出任何错误日志，这是调试中最高频的陷阱。建议在编辑器下用`ensure(PhysicalAnimationComponent->GetSkeletalMesh() != nullptr)`进行断言验证。

### 力的计算机制与物理子步

Physical Animation组件在每个物理子步（physics substep，默认频率为每帧2次，最高可设为16次）中执行以下计算：

1. 从当前帧动画评估结果（Animation Pose）获取目标骨骼的世界空间或局部空间变换 $T_{target}$；
2. 获取物理刚体当前变换 $T_{current}$；
3. 计算姿势误差，对旋转部分应用 $\tau = k_o \cdot \Delta\theta - k_{av} \cdot \omega$，对位置部分应用 $F = k_p \cdot \Delta x - k_v \cdot v$；
4. 将计算所得扭矩 $\tau$ 和力 $F$ 分别限幅至 `MaxAngularForce` 和 `MaxLinearForce`，然后通过PhysX/Chaos的 `AddTorqueInRadians` / `AddForce` 接口施加到刚体上。

其中 $k_o$=`OrientationStrength`，$k_{av}$=`AngularVelocityStrength`，$k_p$=`PositionStrength`，$k_v$=`VelocityStrength`。这是一个**PD控制器**（Proportional-Derivative Controller）结构，$k_o$/$k_p$ 是比例项，$k_{av}$/$k_v$ 是微分项，缺少积分项（I项），因此在持续外力作用下骨骼会有稳态误差，这是设计上的取舍——避免积分项导致的力积累和不稳定性。

---

## 关键公式与参数调节方法

### PD控制器公式

旋转追逐力矩的计算公式为：

$$\tau = k_o \cdot \Delta\theta - k_{av} \cdot \omega$$

其中 $\Delta\theta$ 为目标旋转与当前旋转之间的角度差（弧度），$\omega$ 为当前骨骼刚体的角速度。系统稳定的临界条件近似为：

$$k_{av} \geq 2\sqrt{k_o \cdot I}$$

其中 $I$ 为骨骼刚体的转动惯量（由物理资产中的碰撞体尺寸和质量决定）。实践中，$k_{av} \approx k_o / 10$ 通常是欠阻尼但视觉上有弹性感的合理起点；若需要无震荡的过阻尼效果，可将 $k_{av}$ 提高至 $k_o / 3$。

### 参数调节的系统方法

**例如**，制作角色"中弹后上半身晃动、下半身继续行走"效果时，推荐从以下基准值开始调整：

- `OrientationStrength = 1500`，`AngularVelocityStrength = 150`（欠阻尼，产生弹性晃动感）
- `MaxAngularForce = 15000`，`MaxLinearForce = 15000`
- `bIsLocalSimulation = true`
- 仅对脊柱以上骨骼（`spine_01`、`spine_02`、`neck_01`、`head`、两臂）激活物理模拟，腿部骨骼不进行`SetAllBodiesBelowSimulatePhysics`

思考问题：如果把 `OrientationStrength` 调到50000而 `MaxAngularForce` 仍保持15000，骨骼的追逐行为会发生什么变化？（提示：MaxAngularForce起到了什么限制作用？）

---

## 实际应用案例

### 案例一：枪击受击反馈（Hit Reaction）

这是Physical Animation组件最典型的应用场景。当子弹击中角色上半身时：

1. 调用`ApplyPhysicalAnimationSettingsBelow(FName("spine_01"), AnimData, true)`激活上半身物理追逐；
2. 同时通过`AddImpulseToAllBodiesBelow`或直接操作`UPrimitiveComponent::AddImpulse`在命中骨骼上施加冲量（典型值：轻武器100～300 kg·cm/s，重武器1000～5000 kg·cm/s）；
3. 物理追逐力会在0.3～0.8秒内将骨骼拉回动画姿势，产生"被击中后弹回"的视觉效果；
4. 到达预设时间后，调用`SetAllBodiesBelowSimulatePhysics(FName("spine_01"), false, true)`关闭物理，角色完全回到动画控制。

### 案例二：依墙站立（Leaning Against Wall）

角色靠墙时，墙面的碰撞反力会推开与墙体重叠的手臂。此时Physical Animation的追逐力会持续拉手臂回到动画中的姿势（如贴墙掩护姿势），形成手臂"压在墙上"的真实感，而不是动画手臂穿插进墙体。`OrientationStrength`需适当降低至500～1000，以使物理碰撞能够明显推开手臂，否则追逐力过强会导致手臂硬穿墙壁。

### 案例三：全身布娃娃过渡（Ragdoll Blend-In）

角色死亡时，直接切换至完全布娃娃会产生姿势跳变。利用Physical Animation组件可实现平滑过渡：先以高`OrientationStrength`（5000）激活全身物理，然后在1秒内通过`ApplyPhysicalAnimationSettingsBelow`逐帧将`OrientationStrength`从5000线性降低至0，最终骨骼追逐力消失，角色平滑进入完全布娃娃状态，无姿势突变。

---

## 常见误区

### 误区一：误以为Physical Animation组件会自动开启物理模拟

`UPhysicalAnimationComponent::ApplyPhysicalAnimationSettingsBelow`**不会**自动对骨骼开启物理模拟。若未调用`SetAllBodiesBelowSimulatePhysics`，组件会绑定约束但无骨骼进入物理状态，效果为零。必须手动分别调用两个函数。

### 误区二：在世界空间模式下忽略PositionStrength

当`bIsLocalSimulation = false`时，骨骼在世界空间中追逐位置，此时若`PositionStrength = 0`，骨骼只追逐旋转而不追逐位置，会导致骨骼在空间中漂移，看起来像关节脱臼。世界空间模式下`PositionStrength`应与`OrientationStrength`同量级。

### 误区三：MaxAngularForce/MaxLinearForce设置过低导致追逐失效

若`OrientationStrength = 3000`而`MaxAngularForce = 100`，则追逐力会被立即钳制到100，实际效果相当于`OrientationStrength = 100`。`MaxAngularForce`的物理意义是**安全上限**而非驱动力，应设置为`OrientationStrength`的5～20倍，确保在小角度误差时不触发钳制。

### 误区四：在构造函数中调用SetSkeletalMeshComponent

`UPhysicalAnimationComponent`的`SetSkeletalMeshComponent`需要目标`USkeletalMeshComponent`已完成初始化，构造函数阶段组件尚未完全注册，此时调用会导致绑定失效。正确时机为`BeginPlay`或更晚。

---

## 知识关联

### 与布娃娃系统的关系

Physical Animation组件是布娃娃系统（`USkeletalMeshComponent::SetSimulatePhysics`）的**上层控制层**，而非替代品。布娃娃系统负责将骨骼物理体切换至`Simulating`状态（使其响应碰撞与重力），Physical Animation组件则在物理体进入模拟后向其持续施加追逐力。两者必须协同使用：缺少布娃娃激活则Physical Animation无作用，缺少Physical Animation则布娃娃完全失控。

### 与动画蓝图AnimGraph的关系

Physical Animation组件工作在**物理层**，与AnimGraph的`AnimDynamics`节点工作在**动画层**是完全不同的两套系统。`AnimDynamics`在动画求值阶段模拟骨骼运动，不