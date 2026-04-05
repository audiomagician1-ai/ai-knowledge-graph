---
id: "audio-source-listener"
concept: "Audio Source与Listener"
domain: "game-engine"
subdomain: "audio-system"
subdomain_name: "音频系统"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Audio Source 与 Listener

## 概述

Audio Source（音频源）与 Audio Listener（音频听者）是游戏引擎空间音频系统中的两类核心对象，共同构成一套"发声者—接收者"物理模型。Audio Source 代表场景中产生声音的位置，例如爆炸点、说话的角色、流水的河流；Audio Listener 则代表接收声音的耳朵，通常挂载在玩家控制的摄像机或角色头部上。引擎通过实时计算这两个对象之间的三维位置关系，决定玩家最终听到的音量、方向感和音调变化。

这套模型直接源自现实声学中的点声源理论，并由 Miles Sound System、DirectSound3D（1996年随 DirectX 3.0 发布）等早期音频 API 引入游戏开发领域。Unity 将其实现为 `AudioSource` 组件与 `AudioListener` 组件；Unreal Engine 则分别对应 `UAudioComponent` 和 `APlayerController` 内置的 Listener 位置。理解这两个对象的属性与交互方式，是实现一切空间音效（3D 音效、方向感、多普勒效果）的前提。

一个场景中通常只允许存在**一个激活的 Audio Listener**，但可以有数十乃至数百个 Audio Source 同时存在。若场景中存在两个激活的 Listener，Unity 会在控制台报出警告并随机选择其中一个生效，这是初学者常见的配置错误。

---

## 核心原理

### Audio Source 的关键属性

Audio Source 的最基础属性是其**世界坐标位置**，引擎每帧都会读取该位置并参与空间音频计算。除位置外，以下属性直接影响声音行为：

- **Spatial Blend（空间混合值）**：取值范围 0.0～1.0，0 表示纯 2D（无方向感，始终等音量），1 表示纯 3D（完整应用距离衰减与方向计算）。将一个背景音乐的 Spatial Blend 误设为 1 会导致玩家走远后背景音乐消失。
- **Min Distance / Max Distance**：定义衰减曲线的起止范围，单位与场景单位一致（Unity 默认 1 单位 = 1 米）。Min Distance 内音量保持最大，超过 Max Distance 后音量归零。
- **Pitch**：控制播放速率，1.0 为原速，0.5 为降低一个八度，2.0 为升高一个八度。多普勒效果本质上就是引擎动态修改 Pitch 的结果。

### Audio Listener 的工作机制

Audio Listener 本身不播放任何声音，它的唯一职责是提供**接收点的世界坐标与朝向**。引擎在每帧音频更新时，会遍历所有激活的 Audio Source，根据 Listener 位置计算每个 Source 相对于 Listener 的**方位角（Azimuth）**和**仰角（Elevation）**，再将结果送入 HRTF（头部相关传输函数）或简化的平移算法，输出左右声道的差异化信号。

Listener 的**朝向**同样至关重要：当 Audio Source 位于 Listener 正后方时，引擎会通过微小的频率滤波（削减高频）模拟人耳对后方声源的感知衰减，与正前方声源产生可感知的差异。

### Source 与 Listener 之间的距离计算

引擎使用欧几里得距离公式计算 Source 与 Listener 之间的直线距离：

$$d = \sqrt{(x_s - x_l)^2 + (y_s - y_l)^2 + (z_s - z_l)^2}$$

其中 $(x_s, y_s, z_s)$ 为 Audio Source 的世界坐标，$(x_l, y_l, z_l)$ 为 Audio Listener 的世界坐标。该距离 $d$ 随后被代入衰减曲线（线性、对数或自定义曲线），得出当前帧的音量系数。注意这是**直线距离**，不考虑遮挡物——声音穿墙问题正是因此而产生，需要额外的遮挡/混响系统来补偿。

### 多普勒效果的触发条件

当 Audio Source 或 Audio Listener 具有非零速度时，引擎会应用多普勒频移公式。Unity 的多普勒效果强度由 `AudioSource.dopplerLevel`（0 = 关闭，1 = 物理真实值）和全局 `AudioSettings.dopplerFactor` 共同控制。一辆以 30 单位/秒速度接近 Listener 的赛车，其引擎音频的感知音调会随接近而升高，远离时降低，这一效果完全由引擎自动计算，无需手动修改 Pitch。

---

## 实际应用

**NPC 对话系统**：将 `AudioSource` 挂载在 NPC 的头部骨骼节点上，Spatial Blend 设为 1，Max Distance 设为 15 米。当玩家（Listener）走近时音量自然增大，走远后淡出，无需任何额外脚本控制音量。

**环境音效**：篝火、瀑布等固定音源将 `Loop` 属性设为 true，AudioSource 放置于场景中的物理位置。瀑布的 Max Distance 可以设为 50 米，而篝火的 Max Distance 通常只需 8～10 米，以匹配各自在现实中的传播范围。

**过场动画中的 Listener 切换**：在过场动画中，摄像机会切换到不同拍摄机位。此时需要将 AudioListener 组件在各摄像机之间动态转移（或禁用旧的、启用新的），否则所有 3D 音效都将从玩家角色的固定位置评估，而非跟随镜头移动，造成声画方向不一致。

---

## 常见误区

**误区一：在每个角色上都添加 AudioListener**
多人游戏本地调试时，开发者有时会为每个角色预制体都挂载 AudioListener，导致场景中出现多个激活的 Listener。引擎只会采用其中一个，其他角色的空间音频计算将全部基于该"随机选中"的 Listener 位置，产生完全错误的方向感。正确做法是只在主摄像机或玩家头部保留一个 Listener，并在角色切换时做好组件的启用/禁用管理。

**误区二：Spatial Blend = 0 等同于没有 AudioSource**
将 Spatial Blend 设为 0（2D 模式）只是使声音不受距离和方向影响，但 AudioSource 依然受 `Volume` 属性、`AudioMixer` 路由和 `AudioSource.mute` 等参数控制。背景音乐应使用 Spatial Blend = 0，但仍需正确配置到 Music 混音总线，而非与音效共享同一混音通道。

**误区三：Max Distance 越大越好**
将所有 AudioSource 的 Max Distance 设为 1000 米，会导致引擎对场景中所有声源都进行完整的空间音频运算，哪怕它们距离玩家极远。正确的做法是根据声源的现实传播距离设置合理的 Max Distance，引擎会在该距离之外自动停止对该 Source 的混音计算，节省 CPU 资源。

---

## 知识关联

**前置概念——音频系统概述**：了解游戏引擎音频管线（加载、解码、混音、输出）之后，AudioSource 对应管线中的"播放节点"，AudioListener 对应最终混音的"采样点"，两者共同决定哪些声音以何种参数进入混音器。

**后续概念——空间音频**：在 Source/Listener 基础距离模型之上，空间音频进一步引入 HRTF 滤波、房间混响（Reverb Zone）和声音遮挡（Occlusion）机制，这些高级特性全部依赖 AudioSource 的位置与 AudioListener 的朝向作为输入参数。

**后续概念——音频衰减模型**：AudioSource 的 Min Distance、Max Distance 以及衰减曲线类型（Logarithmic、Linear、Custom）共同定义了完整的衰减模型，是对本节距离计算公式的细化与扩展。

**后续概念——脚步声系统**：脚步声系统需要在角色的每只脚接触地面时，在该脚的世界坐标位置动态创建或激活一个临时 AudioSource，使脚步声从脚部位置发出而非从角色中心发出，从而产生真实的空间感。这一机制直接运用了 AudioSource 位置动态更新的能力。