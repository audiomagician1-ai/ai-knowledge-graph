---
id: "sfx-am-obstruction-occlusion"
concept: "遮挡与阻隔"
domain: "game-audio-sfx"
subdomain: "audio-middleware"
subdomain_name: "音频中间件"
difficulty: 4
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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


# 遮挡与阻隔

## 概述

遮挡（Obstruction）与阻隔（Occlusion）是游戏音频中两个不同的几何声学处理概念，均由Wwise、FMOD等音频中间件提供内置支持。两者的共同目标是模拟现实中声波在传播路径上受到物理障碍物影响时所产生的音色与音量变化，但计算逻辑和声学含义存在本质区别。

遮挡（Occlusion）描述的是声源与听者之间存在完全封闭的障碍物时，声音绕过或穿透该障碍的总体衰减效果。典型场景是墙体另一侧的爆炸声——声波无法沿直线到达听者，只能通过墙体振动传导，因此低频成分保留、高频被大量吸收。遮挡（Obstruction）则描述部分遮挡的情形：声源与听者之间有障碍物存在，但存在绕射路径，声音可绕过障碍物到达听者，高频损失相对较少，主要影响直达声的强度。

这两个参数在1990年代末期随着3D游戏音频引擎的普及而被规范化，Wwise将它们分别以0.0到1.0的归一化浮点数表示，并通过游戏代码的射线检测（Raycast）结果实时驱动，使玩家在不同空间位置时感知到动态变化的声学环境。

---

## 核心原理

### Obstruction 与 Occlusion 的声学差异

在Wwise的内部处理架构中，Obstruction（遮挡）仅作用于声音的**直达声（Dry Path）**，不影响发送到混响总线的**湿声（Wet Path）**。这意味着当Obstruction值为1.0时，玩家仍能听到房间的混响尾音，但直达声被完全截断，产生"声音从房间里飘出来"的环境感。

Occlusion（阻隔）则同时衰减直达声与湿声路径。当玩家与声源被一堵混凝土墙完全隔开时，Occlusion值趋向1.0，混响信号也随之降低，模拟整个声场被物理障碍物阻断的效果。两者的信号流差异如下：

- **Obstruction = 1.0**：Dry Bus音量 → 衰减至最大截断值；Wet Bus → 不受影响
- **Occlusion = 1.0**：Dry Bus音量 → 衰减；Wet Bus → 同比例衰减

### 射线检测与参数映射

游戏引擎（Unity/Unreal）通常在每帧或每隔若干帧向声源方向发射1至3条射线，根据射线命中的碰撞体数量和材质属性计算出0.0–1.0的原始遮挡值。音频程序员再将该原始值通过一条**自定义曲线**映射为Wwise的Obstruction/Occlusion参数，该映射曲线的形状决定了过渡的平滑度——非线性曲线能避免玩家在临界点产生突兀的音量跳变。

Wwise API中驱动这两个参数的函数为`AK::SoundEngine::SetObjectObstructionAndOcclusion()`，需要传入GameObjectID、听者ID、Obstruction值和Occlusion值四个参数，可在C++或GameObjectAudioEmitter组件层面以15–30Hz的频率更新。

### 低通滤波器的隐式应用

当Occlusion值提升时，Wwise内部会对湿干两条路径施加**低通滤波（Low-Pass Filter, LPF）**，其截止频率随Occlusion值升高而降低。在Wwise默认配置中，Occlusion = 1.0对应的LPF截止频率约为800 Hz，模拟高密度材质（如混凝土）对高频声波的强吸收特性。设计师可在Wwise的Property Editor中调整Occlusion对LPF截止频率和音量的影响曲线，实现不同材质的差异化音色表现。

---

## 实际应用

**室内/室外转换场景**：在第一人称射击游戏中，玩家从室外走进建筑物时，室外敌人的枪声需要经历从Occlusion = 0.0平滑过渡至Occlusion = 0.85的过程。实现方式是在门框位置设置触发体积（Trigger Volume），进入后以0.3秒的线性插值推高Occlusion参数，使枪声逐渐变得低沉、模糊。

**部分遮挡场景**：玩家躲在掩体（岩石、车辆）后方时，通过向声源发射三条射线（中央射线 + 上下偏移各15°），若三条中有一条未被阻挡，则Obstruction值设为0.4而非1.0，保留部分直达声清晰度，同时让声源的混响感维持完整，真实还原绕射效果。

**门缝透声**：当NPC对话声源在关闭的门后时，Occlusion = 0.7配合LPF处理，使对话仍具可辨识性（保留基频100–800 Hz），但失去高频清晰度（>2 kHz大量衰减），避免玩家完全听不到剧情信息。

---

## 常见误区

**误区一：将Obstruction与Occlusion当作同一参数使用**
许多初学者直接用一个参数同时替代两者，统一作用于全部信号路径。这会导致在部分遮挡场景中混响信号被错误截断，房间感消失，声场变得"干燥"且不自然。正确做法是根据射线检测的命中比例分别为Obstruction（有绕射路径时）和Occlusion（完全封闭时）赋值。

**误区二：以为衰减曲线（Attenuation）已经覆盖了遮挡效果**
衰减曲线描述的是声音随**距离**的音量变化，完全基于声源与听者的空间距离，不考虑中间障碍物的存在。即使声源距离很近（如1米外的墙后），若没有Occlusion/Obstruction处理，声音仍会以"无遮挡"的正常音量到达听者。两个系统须同时运作。

**误区三：认为更新频率越高越好**
将Obstruction/Occlusion的更新频率设为每帧（60Hz）会增加CPU上的射线检测负担。实际项目中通常每隔2–4帧更新一次（即15–30Hz），并配合参数平滑插值，在人耳无法察觉的时间尺度（约50ms）内完成过渡，兼顾性能与感知质量。

---

## 知识关联

**前置概念：衰减曲线**
Obstruction与Occlusion的最终音量输出是在衰减曲线计算完毕后叠加的：引擎先用声源-听者距离查阅衰减曲线得到基础音量系数，再将Obstruction/Occlusion参数以乘法形式施加于该系数上，因此两者属于串联而非并联的处理环节。

**后续概念：辅助发送（Auxiliary Sends）**
Occlusion对Wet Bus的衰减操作实际上是通过调整辅助发送（Auxiliary Send）的增益来实现的。理解辅助发送的总线路由方式，才能精确控制Occlusion影响哪些混响总线、影响幅度如何分配。在多房间混响架构中，设计师会为每个房间创建独立的辅助发送，Occlusion则选择性地压低非本房间的发送电平。

**后续概念：几何遮挡（Geometry-Based Occlusion）**
本文描述的是基于射线检测的近似遮挡，属于轻量实现。Wwise Spatial Audio模块提供的几何遮挡系统可直接将引擎网格提交为声学几何体，自动计算衍射路径（Diffraction Path）和透射系数，是当前遮挡处理的更精确方案，但CPU开销也显著更高。