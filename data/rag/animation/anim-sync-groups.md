---
id: "anim-sync-groups"
concept: "同步组"
domain: "animation"
subdomain: "blend-space"
subdomain_name: "BlendSpace"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 同步组（Sync Group）

## 概述

同步组（Sync Group）是Unreal Engine动画蓝图中专门用于协调多个循环动画播放进度的机制，其核心功能是让BlendSpace中的Walk和Run等步行类动画在混合时保持脚步节奏一致，避免出现"脚步滑步"（foot sliding）现象。当速度参数从Walk过渡到Run时，若不使用同步组，Walk动画可能处于左脚着地阶段，而Run动画却处于右脚离地阶段，两者叠加会产生明显的脚步错位视觉问题。

同步组的概念由Epic Games在Unreal Engine 4.2版本中正式引入动画系统。在此之前，开发者需要手动调整动画帧率或使用根运动（Root Motion）来解决步幅对齐问题，流程繁琐且不稳定。同步组将这一协调逻辑封装成统一接口，大幅降低了角色运动动画的制作门槛。

在1D BlendSpace中配置Walk（典型参数范围0~150 cm/s）和Run（150~600 cm/s）时，同步组通过统一的"归一化时间轴"让所有参与混合的动画以相同的相位（phase）推进，而非以各自的原始帧率独立播放。这使得两段动画的"步态周期"始终保持同步，混合权重无论怎样变化，左右脚的着地时机都能对应一致。

---

## 核心原理

### 领导者与追随者机制（Leader / Follower）

同步组内部采用"领导者-追随者"模型来决定以哪一段动画的播放速度为基准。在任意帧中，**混合权重最高的动画自动成为领导者（Leader）**，其余动画均为追随者（Follower）。追随者不会按照自身的原始帧率播放，而是将自己的归一化进度强制对齐到领导者当前的归一化时间位置。

举例说明：Walk动画长度为1.2秒/循环，Run动画长度为0.8秒/循环。若当前混合权重Walk占60%（领导者），则追随者Run的播放速度会被拉伸，使得Run在Walk走完一个完整步态周期时恰好也完成一个循环，而不是Run自顾自在0.8秒内播完。

### 归一化时间轴与步态标记（Anim Notify）

同步组依赖**归一化进度值（0.0~1.0）**来描述动画在一个循环中的位置，而不是绝对的秒数或帧号。Walk动画在0.0时左脚着地、0.5时右脚着地，Run动画需要在相同的0.0和0.5位置也分别设置左右脚着地的Anim Notify标记（通常使用`SyncMarker`类型的Notify）。只有当两段动画在相同的归一化位置拥有相同的步态标记，同步组才能做到真正的语义对齐——此时即便领导者切换，脚步过渡也不会发生跳帧。

### 同步组名称与分配规则

在Unreal Engine动画蓝图的AnimGraph中，每个动画序列节点都有一个`Sync Group`属性，开发者需要将Walk和Run节点的Sync Group Name设置为**同一个字符串**（例如`LocomotionSyncGroup`），它们才会被纳入同一同步域。不同名称的同步组之间完全独立，互不影响。若某个动画节点的Sync Group留空，则该节点完全不参与任何同步逻辑，以自身帧率独立播放。

同一BlendSpace内部的动画节点可以在资产内直接启用`Use Sync Groups`选项，由BlendSpace编辑器自动将所有子动画纳入同一同步域，无需逐一手动配置。

---

## 实际应用

### Walk-Run混合中的配置步骤

在1D BlendSpace（速度轴0~600 cm/s）中配置步行-跑步动画时，典型流程如下：
1. 打开Walk动画，在第0帧添加`SyncMarker`通知，命名为`LeftFootDown`；在中间帧（约第15帧，若共30帧）添加`RightFootDown`标记。
2. 对Run动画执行相同操作，在其帧序列的对应相位位置放置同名标记。
3. 在BlendSpace资产设置面板中，将`Sync Group Name`填写为`LocomotionSyncGroup`，并确保`Sync Group Type`设置为`Via Sync Marker`模式。

完成以上配置后，当角色速度在Walk区间（如120 cm/s）时，系统自动选取Walk为领导者；速度超过150 cm/s进入混合区间后，随着Run权重上升，领导者会在某一帧自动切换为Run，而Walk继续以追随者身份对齐Run的步态周期，保证过渡无缝。

### Crouch Walk与正常Walk的同步

同步组不仅限于Walk和Run，Crouch Walk（蹲走）动画同样可以加入`LocomotionSyncGroup`。由于Crouch Walk步幅较短（典型动画时长约1.6秒/循环），若不同步，与正常Walk混合时会出现明显的"双腿打架"问题。将Crouch Walk纳入同一同步组后，系统会在运行时动态拉伸其播放速度以匹配领导者节奏，消除该问题。

---

## 常见误区

### 误区一：同步组会统一所有动画的播放速率

很多初学者误以为同步组会把所有动画"强制播放到同一帧"。实际上，同步组调整的是各动画的**归一化进度**，而不是绝对帧号。Walk有30帧、Run有24帧，同步组让两者的归一化位置（0.0~1.0）始终一致，但各自实际播放的帧号是不同的。若强行统一帧号，步态标记将毫无意义，同步也会失效。

### 误区二：步态标记名称不同也能同步

有开发者将Walk的标记命名为`L_Foot`，Run的标记命名为`Left_Foot`，认为位置对应即可。这是错误的——同步组的`Via Sync Marker`模式要求两段动画的**标记名称完全一致**，大小写也不可不同。名称不匹配时系统会静默回退到基于权重的普通混合，脚步同步失效，且不会弹出任何报错提示，排查困难。

### 误区三：只要速度曲线顺滑，不用同步组也行

部分开发者认为只要把BlendSpace的速度采样点设计得足够密集（如每10 cm/s一个采样），过渡就会足够顺滑，无需同步组。实际上，步态错位是**相位问题**，而不是权重插值问题，无论采样密度多高，只要两段动画在混合瞬间相位不对齐，就会出现可见的脚步抖动，采样密度无法解决这一根本问题。

---

## 知识关联

同步组建立在**1D BlendSpace**的基础之上，1D BlendSpace提供了速度轴与多段动画的权重计算逻辑，而同步组在此权重计算完成后介入，修正各动画的归一化播放进度。没有BlendSpace的混合框架，同步组的领导者-追随者机制无从挂载。

在角色运动系统的更复杂形态中，同步组与**运动扭曲（Motion Warping）**技术配合使用，可在保持步幅对齐的同时进一步适配不规则地形；与**状态机（State Machine）**配合时，同步组可确保从Idle状态切换到Walk状态的起步帧也能以正确的步态相位进入循环，而不是从动画的第0帧强行开始，防止起步瞬间出现腿部抖动。理解同步组的领导者切换规则，也是后续学习**惯性化混合（Inertialization）**时理解相位连续性问题的重要前提。