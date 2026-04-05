---
id: "vfx-niagara-collision"
concept: "碰撞检测"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
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


# 碰撞检测

## 概述

碰撞检测（Collision Detection）是Niagara粒子系统中用于判断粒子是否与场景几何体或其他物理对象发生接触的计算机制。与传统物理模拟中的刚体碰撞不同，Niagara的碰撞检测专为高并发粒子设计——单个特效场景中可能同时有数千乃至数万个粒子需要进行碰撞查询，因此系统在精度和性能之间进行了专门的工程权衡。

Niagara碰撞检测功能在UE4.20版本引入Niagara体系后随即成为粒子行为模块的标准组件，取代了旧版Cascade系统中相对粗糙的Collision模块。新系统通过GPU光线投射（Raycast）和深度缓冲（Depth Buffer Scene Depth）两种截然不同的技术路径实现碰撞，每种路径适用于不同的平台与精度需求。

掌握碰撞检测对于制作雨滴打在地面溅起水花、火星碰墙后改变方向、烟雾在障碍物边缘绕流等真实感特效至关重要。错误配置碰撞检测模块会导致粒子穿透地面、在空中异常停顿，或触发不必要的大量物理开销，这些问题在量产特效制作中极为常见。

---

## 核心原理

### 两种检测模式的底层差异

Niagara提供**Scene Depth Collision**和**Ray Traced Collision**两种检测模式，两者的计算方式根本不同。

**Scene Depth Collision** 利用已经渲染完成的深度缓冲图像进行碰撞判断：每帧读取GBuffer中的深度值，将粒子的世界坐标重投影到屏幕空间，与深度图中存储的场景深度值对比。若粒子深度超过场景深度，即判定为碰撞。这种方式的优点是完全在GPU上执行，开销极低，但存在一个关键限制：**仅限于摄像机可见的几何体**，处于屏幕外或被遮挡的表面无法被检测到。

**Ray Traced Collision** 从粒子当前位置向其运动方向发射射线，利用场景的加速结构（BVH树）精确查询交叉点。每次射线查询的精度更高，可检测屏幕外的几何体，但每条射线的计算代价约为Scene Depth方式的5到10倍，因此通常限制在粒子数量较少（建议低于2000个）的特效中使用。

### 碰撞响应计算公式

粒子发生碰撞后，新的速度向量由反弹系数（Restitution）和摩擦系数（Friction）共同决定。

反弹后速度的法向分量计算如下：

$$V_{n}' = -e \cdot V_{n}$$

其中 $V_{n}$ 为碰撞前速度在表面法线方向的分量，$e$ 为恢复系数（Restitution），范围0到1，值为0时粒子完全不弹起（如沙粒落地），值为1时完全弹性碰撞（如理想弹球）。

切向分量受摩擦影响：

$$V_{t}' = (1 - f) \cdot V_{t}$$

其中 $f$ 为摩擦系数（Friction），范围0到1。Niagara的`Collision`模块在**Particle Update**阶段执行上述计算，并将修正后的速度写回`Particles.Velocity`属性。

### Collision模块的关键参数

在Niagara编辑器中，`Collision`模块暴露以下参数供美术调整：

- **Collision Preset**：指定参与碰撞的物理通道，通常设为`Visibility`以命中所有可见几何体，或自定义通道仅与特定对象类型碰撞
- **Radius Scale**：粒子碰撞球半径相对于`Particles.SpriteSize`的缩放比例，默认值0.5意味着使用精灵尺寸的一半作为碰撞半径
- **Kill On Contact**：布尔值，开启后粒子在首次碰撞时立即进入Dead状态，常用于制作子弹击中效果
- **Response**：枚举值，包括Bounce（弹跳）、Stop（停止）、Kill（销毁）三种基础响应类型

---

## 实际应用

### 雨滴打地面效果

制作雨水特效时，将粒子的`Collision Mode`设为`Scene Depth Collision`，`Restitution`设为0.05（几乎不弹跳），`Friction`设为0.8。在`Collision`模块的**On Collision**事件针脚处连接`Spawn Particles at Location`，在碰撞坐标处生成第二个粒子系统（水花溅射）。整套设置可在不超过0.3ms的GPU时间内处理约8000个雨滴的碰撞。

### 火焰粒子沿斜面滑落

熔岩流或火星特效需要粒子在碰撞后沿表面方向继续运动。此时将`Restitution`设为0，`Friction`设为0.1，并在碰撞后通过`Apply Force Along Normal`的**负值**实现粒子"贴附"表面，同时在Spawn时启用`Alignment`到碰撞法线，使Sprite朝向与表面垂直，避免粒子悬浮在斜面上方的视觉错误。

### 与特定物理Actor交互

若需要粒子只与玩家角色胶囊体碰撞而忽略场景静态网格，需在项目设置的`Collision Channels`中新建自定义通道（如`ParticleHit`），为角色胶囊体的Response设为`Block`，为`WorldStatic`设为`Ignore`，再在Niagara的`Collision Preset`中指定该自定义通道。

---

## 常见误区

### 误区一：Scene Depth碰撞在主机平台完全可用

部分开发者将Scene Depth Collision视为"万能低开销方案"，但该模式要求深度缓冲在粒子更新阶段已完成写入。在移动平台（iOS/Android）的Forward Rendering管线下，深度预通道的时序与延迟渲染不同，常导致碰撞检测失效或出现一帧延迟偏移。正确做法是在移动端改用Ray Traced Collision并严格控制粒子数量在500以下。

### 误区二：Radius Scale越小碰撞越精确

将`Radius Scale`设为接近0的值并不会让碰撞"更准确"，反而会导致粒子在数值计算时穿透薄壁网格。这是因为当粒子的碰撞半径趋近于零时，单帧内粒子移动距离可能超过整个碰撞球直径（即"隧道穿透"问题），Niagara默认不进行子步长的连续碰撞检测（CCD）。建议`Radius Scale`最小值保持在0.2以上，或对高速粒子减小`Simulation Update Rate`。

### 误区三：碰撞事件与事件系统自动连通

`Collision`模块内的**On Collision**针脚并不等同于Niagara事件系统中的`Collision Event`。前者仅在同一Emitter内部触发局部逻辑，后者才能跨Emitter或通知蓝图。若需要在粒子碰撞时通知外部蓝图执行游戏逻辑，必须额外添加`Collision Event`模块并在`System`级别的`Event Handler`中配置接收方。

---

## 知识关联

**前置概念——力场与运动**：碰撞检测模块在`Particle Update`阶段执行，时序位于重力、风场等力场计算之后。粒子在碰撞发生时的速度向量直接来源于前一帧力场积分的结果，因此理解`Particles.Velocity`如何被力场模块逐帧修改，是正确预判碰撞响应结果的必要基础——若力场施加了异常大的加速度，碰撞的弹跳计算结果也会失真。

**后续概念——事件系统**：碰撞是触发Niagara事件最常见的来源之一。`Collision Event`模块将每次碰撞的位置、法线、速度打包成事件载荷（Payload），可被同一系统内其他Emitter订阅，用于在碰撞点生成次级粒子（如火花、烟尘），这一机制构成了复杂层级特效的核心联动手段。

**后续概念——碰撞物理**：当特效需要与物理模拟的刚体（如可破坏物体）产生真实的力交换时，仅靠Niagara内置碰撞检测已不足够，需要借助`Chaos Physics`体系中的粒子-刚体力传递接口，将Niagara粒子的动量转化为可作用于物理场景的冲量（Impulse）。