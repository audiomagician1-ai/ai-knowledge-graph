---
id: "anim-hand-ik"
concept: "手部IK"
domain: "animation"
subdomain: "ik-fk"
subdomain_name: "IK/FK"
difficulty: 3
is_milestone: false
tags: ["实战"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 手部IK

## 概述

手部IK（Hand Inverse Kinematics）是将反向运动学算法专门应用于角色手部骨骼链的技术，用于解决手掌、手腕与目标接触点之间的精确定位问题。与脚部IK主要处理地面接触不同，手部IK需要同时控制**位置**和**旋转**两个维度——手握门把手时手腕的朝向与手掌贴墙时完全不同，这使手部IK的目标通常需要一个完整的6自由度变换（Transform），而非仅仅是一个世界坐标点。

手部IK在游戏动画中的普及源于2000年代初期动作游戏的需求。早期《古墓丽影》（Tomb Raider，1996年首发）系列依赖预烘焙动画处理攀爬，但手部与壁面的穿插问题明显。随着双骨骼IK求解器（Two-Bone IK Solver）在2005年前后趋于成熟，开发者开始在运行时动态计算手部位置，使角色能够适应任意高度和角度的抓握点。Unreal Engine 4于2014年引入的"Hand IK Retargeting"节点，以及Unity 2019.1正式发布的Animation Rigging包中的`TwoBoneIKConstraint`组件，使手部IK成为现代角色动画管线的标准配置。

手部IK的核心价值在于打破动画与场景几何体之间的耦合。一段"推开门"的动画，若没有手部IK，在门把手高度偏移10厘米时就会出现手部悬空或穿模。手部IK允许美术师制作一套基础动画，然后由IK系统在运行时将手部修正到实际接触点，从而使同一套动画资产适配场景中的任意变体，显著降低动画师的重复劳动量。在现代AAA项目中，一个完整的手部IK系统往往能将"近战抓取"类动画的制作数量削减40%至60%。

---

## 核心原理

### 手部IK骨骼链结构

手部IK的骨骼链通常由**上臂（Upper Arm）→ 前臂（Forearm）→ 手腕（Wrist）**三块骨骼构成，共两段骨骼（即双骨骼IK的直接应用）。求解器以手腕骨骼的世界空间Transform作为末端执行器（End Effector），目标点则称为**IK Target**或**IK Effector**。

上臂骨骼的根节点即肩关节（Shoulder Joint），其世界空间位置记为 $P_s$；上臂长度（肩关节到肘关节距离）记为 $L_1$，通常在角色绑定时固定，标准成年人体比例下约为躯干高度的0.33倍；前臂长度（肘关节到腕关节距离）记为 $L_2$，约为 $L_1$ 的0.9至1.05倍。IK Target的位置记为 $P_t$，肩部到目标的距离 $d = |P_t - P_s|$。

### 双骨骼IK余弦求解

双骨骼IK的核心是利用余弦定理在由 $L_1$、$L_2$、$d$ 三边构成的三角形中求解肘部弯曲角度。完整推导如下：

$$\cos\theta_{elbow} = \frac{d^2 - L_1^2 - L_2^2}{2 \cdot L_1 \cdot L_2}$$

其中：
- $d$ 为肩部关节到IK Target的直线距离（单位：引擎场景单位，通常为厘米）
- $L_1$ 为上臂骨骼长度
- $L_2$ 为前臂骨骼长度
- $\theta_{elbow}$ 为肘关节的弯曲角度（0°表示手臂完全伸直）

当 $d > L_1 + L_2$ 时，$\cos\theta_{elbow} > 1$，目标超出手臂最大伸展范围，此时需要**Reach限制**逻辑将 $d$ 钳制为 $L_1 + L_2$，同时保留手臂朝向IK Target的方向，防止骨骼拉伸变形。当 $d < |L_1 - L_2|$ 时同理，目标过近，肘部角度超出物理限制，需要钳制到最小允许弯曲角。

例如，某角色上臂长度 $L_1 = 30\text{cm}$，前臂长度 $L_2 = 28\text{cm}$，当手部需要抓取距肩膀 $d = 45\text{cm}$ 的把手时，代入公式得 $\cos\theta_{elbow} = (45^2 - 30^2 - 28^2)/(2 \times 30 \times 28) = (2025 - 900 - 784)/1680 = 341/1680 \approx 0.203$，故 $\theta_{elbow} \approx 78.3°$，手臂呈明显弯曲状态，视觉上自然合理。

### 手腕旋转对齐

手部IK与脚部IK最大的差异是**手腕旋转必须匹配接触面法线**。攀爬垂直岩面时，手掌需朝向岩面法线方向；扶桌面时，手掌朝向重力方向 $(0, -1, 0)$；推开向内开合的门时，手掌法线与门面法线反向对齐。实现方式是为每个IK Target额外存储一个 `Rotation`（四元数）或 `Normal`（单位向量）数据，求解器在定位手腕位置后，再将手腕骨骼的朝向旋转至目标方向。

Unreal Engine中使用 `Rotate Bone` 节点配合 `Hand_IK_Target` 的旋转分量完成此步骤。Unity Animation Rigging的 `MultiRotationConstraint` 可绑定手腕骨骼跟随目标旋转，权重设为1.0时完全对齐，设为0.5时与原始动画混合，适合需要"部分修正"的场景（例如拾取轻微倾斜的物体时不需要完全对齐）。

### 肘部极向量（Pole Vector）控制

仅凭位置和末端旋转无法唯一确定手臂姿态——肘部可以朝向任意方向而不改变手腕位置，这一自由度在数学上对应三角形绕 $P_s$–$P_t$ 轴的旋转。**Pole Vector**（极向量）是一个额外的世界空间点 $P_{pole}$，用于约束肘部的朝向：肘关节将始终位于由 $P_s$、$P_t$、$P_{pole}$ 三点确定的平面内，且偏向 $P_{pole}$ 一侧。

手部IK中肘部极向量通常设置在角色身体前方偏外侧约30°的位置，确保肘部自然弯曲而非穿入躯干。攀爬动作中，极向量需要随身体姿态动态更新：当角色侧面贴墙时，肘部应向外侧打开；当角色正面攀爬时，肘部应朝向两侧。这通常通过将极向量绑定到一个随角色旋转偏移的虚拟骨骼（Virtual Bone）实现，该虚拟骨骼在角色局部空间中定义，运行时转换为世界空间后传入求解器。

### 接触点检测与IK Target更新

手部IK Target的来源有两种主要方式：

1. **射线检测（Raycast）**：从手部骨骼沿前方发射射线，击中面的坐标和法线直接作为IK Target的位置与旋转。适用于扶墙、推物体等场景。Unreal中 `Line Trace By Channel` 返回 `Hit Location` 和 `Hit Normal`，将这两个值传入IK Target的Transform。射线长度通常设置为角色手臂最大伸展距离的1.1倍，避免过短导致漏检或过长导致误触。

2. **预设锚点（Interaction Point）**：在可交互对象上手动标记抓握点（Grab Point），存储相对于对象的局部坐标。攀爬钢管时，游戏会将角色手部IK Target绑定到钢管预设的 `Left_Hand_Grab` 和 `Right_Hand_Grab` 锚点上。预设锚点的精度更高，但需要美术师或关卡设计师为每个可交互对象手工标注，工作量较大。

---

## 关键公式与参数模型

手部IK在工程实现中还涉及以下两个关键的数学工具：

**IK Target平滑插值（弹簧阻尼追踪）**：

$$P_{target}(t) = P_{target}(t-1) + \left(P_{goal} - P_{target}(t-1)\right) \cdot \left(1 - e^{-k \cdot \Delta t}\right)$$

其中 $P_{goal}$ 为本帧的目标位置，$k$ 为弹簧刚度系数（典型值为8至15，值越大响应越快但越容易抖动），$\Delta t$ 为帧时间间隔。此公式确保IK Target以平滑的指数曲线逼近目标，避免逐帧跳变造成的视觉抖动。

**IK权重渐变**：

$$w(t) = \text{clamp}\!\left(\frac{t - t_{start}}{T_{fade}},\ 0,\ 1\right)$$

其中 $t_{start}$ 为IK激活时刻，$T_{fade}$ 为渐变持续时间（接触开始时建议5至8帧，约0.08至0.13秒@60fps；脱离接触时建议12至15帧以避免手臂"弹回"感）。权重 $w$ 在0到1之间线性变化，可进一步用平滑阶跃函数（Smoothstep）替换线性插值以获得更自然的加减速感。

---

## 实际应用

### 攀爬系统中的双手IK

《刺客信条：起源》（Assassin's Creed Origins，2017年，Ubisoft Montreal开发）的攀爬系统为每块可抓取建筑表面预生成了密集的抓握点网格，网格间距约为角色手掌宽度的0.8倍，角色攀爬时系统实时为左右手分别选取最近的合法抓握点，双手IK Target各自独立更新，使双手能在任意石块形状上精确贴合。

实现时需注意**左右手IK的优先级**：当角色整体动画已确定骨盆位置时，先解算支撑手（负重更大的那只手，通常是当前帧承受角色重心方向的手）的IK，再解算辅助手的IK，避免两只手同时争抢导致肩部骨骼被过度拉伸。在Unreal Engine的动画蓝图中，这体现为将左右手IK节点串联而非并联——先执行右手IK，输出Pose后再传入左手IK节点继续处理。

### 扶墙与遮蔽动作

FPS游戏中的"倚墙探身"（Lean）动作使用手部IK将支撑手按压到墙面。具体流程：每帧对墙面进行球形扫描（Sphere Cast，半径约0.15米），获取最近接触点及其法线，将法线取反后得到手掌朝向，结合接触点坐标构成IK Target的完整Transform。当接触点消失（角色离墙）时，IK权重在0.2秒内（约12帧@60fps）线性淡出至0，回归原始动画姿态。

案例：《使命召唤：现代战争》（Call of Duty: Modern Warfare，2019年）中，角色贴墙瞄准时左手IK Target绑定到墙面射线检测结果，右手IK Target跟随枪械握把锚点，两套IK系统以不同权重同时运行，左手权重随贴墙程度（角色与