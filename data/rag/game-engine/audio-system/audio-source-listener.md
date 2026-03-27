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
quality_tier: "B"
quality_score: 50.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
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

Audio Source（音频源）与 Audio Listener（音频听者）是游戏引擎空间音频系统中的两类核心对象，它们共同构成了"声音从哪里发出、从哪里被感知"这一物理模型的数字化抽象。Audio Source 代表场景中产生声音的实体，例如一把枪、一台发动机或一扇吱呀作响的门；Audio Listener 则代表接收声音的耳朵，通常绑定在玩家的摄像机或角色头部对象上。

这一模型最早在 OpenAL（Open Audio Library，2000年由 Creative Labs 发布）规范中以 `alSource` 和 `alListener` 的形式被明确定义。Unity、Unreal Engine 等主流引擎沿用了这套概念，但封装了底层 API，提供了组件化的工作流。在 Unity 中，一个场景同一时间只允许存在**一个激活的 Audio Listener**，若同时存在多个则引擎会发出警告并选择第一个生效。

理解这两类对象的意义在于：所有空间音效计算——音量衰减、多普勒频移、方向感——都以 Source 的世界坐标和 Listener 的世界坐标之间的**相对位置向量**为输入。没有这两者的空间关系，3D 音频就退化为与位置无关的 2D 平面声音。

---

## 核心原理

### Audio Source 的关键属性

一个 Audio Source 对象携带以下决定其声音行为的具体参数：

- **AudioClip**：挂载的原始音频资源，决定播放的内容本身。
- **Spatial Blend**（空间混合值）：取值范围 0.0（完全 2D）到 1.0（完全 3D），控制该 Source 参与空间计算的程度。将背景音乐设置为 0，将枪声设置为 1，是典型用法。
- **Min Distance / Max Distance**：定义衰减计算的起止半径，单位与引擎的世界单位一致（Unity 默认 1 单位 = 1 米）。
- **Pitch**：默认值 1.0，数值加倍则音调升高一个八度，常用于结合多普勒效应动态修改。
- **Loop**：布尔值，决定 AudioClip 播放结束后是否循环，引擎循环自动在最后一帧与第一帧之间执行无缝拼接。

### Audio Listener 的位置与朝向

Audio Listener 并非只有一个坐标点，它还携带**朝向（Orientation）**信息，由对象的 `Forward` 向量和 `Up` 向量共同定义。HRTF（头相关传递函数）算法依赖这两个向量来模拟声音从左侧还是右侧传来、从头顶还是脚下传来的心理声学差异。在 Unreal Engine 5 中，Listener 的朝向直接由绑定的 `PlayerCameraManager` 的旋转矩阵提供，每帧刷新一次。

### Source 与 Listener 的相对距离计算

音频引擎每帧计算从 Source 到 Listener 的欧氏距离：

$$d = \sqrt{(x_S - x_L)^2 + (y_S - y_L)^2 + (z_S - z_L)^2}$$

其中 $(x_S, y_S, z_S)$ 为 Audio Source 的世界坐标，$(x_L, y_L, z_L)$ 为 Audio Listener 的世界坐标。这个距离值 $d$ 随后被送入衰减模型（如线性衰减或对数衰减函数）来计算最终增益。值得注意的是，当 Source 与 Listener 均静止时，引擎通常会缓存上一帧的距离值跳过重算，以节省 CPU 开销。

### 多普勒效应的触发条件

多普勒频移由 Source 和 Listener 的**相对速度分量**（沿连线方向的分量）决定，公式为：

$$f' = f_0 \cdot \frac{v_{sound} + v_L}{v_{sound} - v_S}$$

其中 $v_{sound}$ 为引擎设定的声速（Unity 默认 340 m/s），$v_L$ 为 Listener 趋近速度，$v_S$ 为 Source 趋近速度。**只有当 Source 或 Listener 发生位移时该计算才会被触发**，静止场景中不产生频移。

---

## 实际应用

**赛车游戏引擎声音**：将 Audio Source 绑定在赛车的发动机骨骼节点上，Audio Listener 绑定在跟车摄像机上。当玩家被对手超越时，Listener 从 Source 后方移至前方，多普勒效应自动使引擎声从高频变低频，无需手动干预音调曲线。

**FPS 游戏脚步声定位**：在多人射击游戏中，每个敌方角色的脚部骨骼挂载一个 Audio Source，玩家角色头部挂载唯一的 Audio Listener。当敌人从玩家左侧绕行时，Source 与 Listener 的方位角变化驱动左右声道的增益差异，玩家通过耳机即可判断方位，而无需依赖视觉信息。

**过场动画的 2D 音乐保护**：在切换到过场动画期间，背景音乐 Audio Source 的 Spatial Blend 应设置为 0，否则若过场摄像机与音乐源的世界距离超过 Max Distance，背景音乐会意外静音——这是新手开发者常遇到的 Bug。

---

## 常见误区

**误区一：一个场景可以有多个 Audio Listener**
许多初学者误以为每个玩家角色都应该拥有自己的 Audio Listener 组件。实际上，Unity 等引擎的空间音频混音器在同一时刻只支持单一 Listener 参考点。在分屏多人游戏中，需要通过代码在切换焦点玩家时动态启用/禁用对应的 Audio Listener 组件，而不是同时激活两个。

**误区二：Audio Source 绑定对象销毁后声音会自动停止**
当 Audio Source 所在的 GameObject 被 `Destroy()` 时，正在播放的声音会立即中断，即使声音还有剩余时长。正确做法是使用 `AudioSource.PlayClipAtPoint()` 静态方法（Unity 内部会生成一个临时 GameObject 并在播放结束后自动销毁）来播放一次性音效，如爆炸声或角色死亡音效。

**误区三：Spatial Blend = 1 就能获得完美的 3D 定位**
将 Spatial Blend 设为 1.0 仅是启用空间计算的前提条件，最终定位效果还依赖于选用的衰减曲线类型、是否启用 HRTF 以及 Audio Listener 的朝向更新频率。若 Listener 绑定的 GameObject 的 Transform 更新发生在 `LateUpdate` 阶段之后，会导致一帧的朝向延迟，在高速旋转摄像机时产生轻微的声像漂移。

---

## 知识关联

学习 Audio Source 与 Listener 需要已掌握**音频系统概述**中的基本概念，特别是 AudioClip 资源格式与音频混音器通道的区别，因为 Audio Source 的输出会先路由到混音器通道再到达 Listener，两者并非直接相连。

掌握本模型后，下一步自然延伸到**空间音频（Spatial Audio）**：HRTF 算法如何利用 Listener 的朝向向量模拟双耳效果；以及**音频衰减模型**：具体的 `f(d)` 衰减函数如何将 Source 与 Listener 之间的距离 $d$ 映射为 0 到 1 的增益系数。**脚步声系统**则是将多个 Audio Source 动态实例化并绑定到角色骨骼节点的典型工程实践，其正确运行的前提正是理解 Source 位置对 Listener 感知的影响。