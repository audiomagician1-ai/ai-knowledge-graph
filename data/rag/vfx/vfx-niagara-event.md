---
id: "vfx-niagara-event"
concept: "事件系统"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 事件系统

## 概述

Niagara事件系统是虚幻引擎Niagara特效框架中实现**粒子间通信**的专用机制，允许一个粒子发射器（Emitter）在特定时刻向外广播消息，由另一个发射器的粒子接收并响应，从而实现级联触发效果。与传统粒子系统中粒子只能单独行动不同，事件系统让粒子具备了"群体协作"能力——例如一颗子弹击中地面后，触发地面尘土发射器喷出碎石，碎石再各自触发火花发射器。

该机制在Niagara的初版设计（UE4.20，2018年）中即作为区别于旧版Cascade系统的核心差异化特性引入，正式解决了Cascade中不同粒子系统必须通过蓝图间接通信的繁琐问题。Niagara事件系统将通信逻辑内化到粒子系统本身，使整个特效行为可以完全自包含地在GPU或CPU上执行。

掌握事件系统是制作爆炸连锁、液体飞溅落地二次溅射、角色死亡触发粒子散落等复合特效的必要技能。它直接决定了一个Niagara系统能否在不依赖外部蓝图调度的情况下表现出有层次的物理反应链。

---

## 核心原理

### 事件的三要素：生成、传递与接收

Niagara事件系统由三个固定模块协作完成通信：

1. **Generate Event（事件生成器）**：挂载在"发送方"发射器的粒子更新（Particle Update）阶段，当满足特定条件（如碰撞发生、粒子死亡）时，向一个命名事件槽写入数据负载。
2. **Event Handler（事件处理器）**：挂载在"接收方"发射器上，声明它监听哪个命名事件槽，以及收到事件时执行的响应脚本。
3. **Payload（有效负载）**：事件携带的数据包，包含位置（`float3`）、速度（`float3`）、法线（`float3`）等自定义字段，接收方粒子可读取这些字段初始化自身属性。

三者通过一个用户自定义的**事件名称字符串**绑定，同一Niagara系统中可以存在多个不同名称的事件通道并行运作，互不干扰。

### 事件类型：Collision Event 与 Death Event

Niagara内置了两类最常用的标准事件模板：

- **Collision Event**：粒子触发碰撞检测后自动写入事件，负载中包含碰撞点世界坐标（`CollisionPos`）和碰撞法线（`CollisionNormal`）。接收方可将新粒子的初始位置精确设在碰撞点，速度方向按法线反射计算：`V_reflect = V - 2*(V·N)*N`。
- **Death Event**：粒子生命周期归零时触发，负载包含死亡时刻的位置与速度，常用于制作粒子"裂碎"成子粒子的效果。

除内置类型外，用户可在任意模块中使用`Write Event`节点自定义触发条件，例如粒子颜色通道超过阈值时广播一个"点燃"事件。

### 执行时序与帧同步

事件系统在单帧内的执行顺序严格遵循：**发送方Particle Update → 事件写入缓冲区 → 接收方Event Handler读取缓冲区 → 接收方生成新粒子**。这意味着同一帧内发生的碰撞，其二次特效粒子最早在**同一帧末尾**开始生命周期，视觉上零延迟。但这也导致一个限制：接收方发射器必须与发送方发射器位于**同一个Niagara系统（System Asset）**内，跨System的事件通信不被原生支持，需借助数据接口转接。

---

## 实际应用

### 子弹击中地面的二次溅射

在制作枪战特效时，"子弹"发射器开启碰撞检测，在粒子更新阶段挂载`Generate Collision Event`模块，命名为`BulletHit`。"地面尘土"发射器添加Event Handler，监听`BulletHit`事件，接收到后以`CollisionPos`作为新粒子的Spawn位置，以`CollisionNormal`偏转速度方向，生成数量设为`Burst: 15`颗碎石粒子。碎石粒子本身再各自挂载Death Event模块命名为`DustDeath`，触发第三层微小烟雾发射器，形成三级联动链。

### 火焰点燃相邻粒子

在火焰模拟中，每颗"火星"粒子在速度低于`0.5 m/s`时，通过自定义`Write Event`广播`Ignite`事件，负载携带当前位置。"木屑"发射器监听`Ignite`事件，接收到后将对应位置的木屑粒子的`bIsOnFire`属性设为`true`，进而切换渲染材质为火焰材质，实现视觉上的"火势蔓延"效果。

---

## 常见误区

### 误区一：认为事件可以跨Niagara系统直接通信

许多初学者尝试在系统A中生成事件、在系统B中接收，但Niagara事件通道是**系统内部私有缓冲区**，跨系统广播需要通过数据接口（Data Interface）中的User Parameter或Named Parameter传递，直接引用事件名称字符串无效且不会产生报错，只是静默失败。

### 误区二：每帧碰撞事件数量无限制

Collision Event每帧实际写入事件数量受`Max Events Per Frame`参数限制，默认值为**32**。当场景中大量粒子同帧碰撞时，超出32个的碰撞事件会被丢弃。若需更高密度的碰撞响应（如密集雨滴），必须显式将该值调高，否则地面溅射效果会在粒子密集时肉眼可见地减少。

### 误区三：Death Event的位置等于粒子最后的渲染位置

Death Event的负载数据在粒子生命归零的那一帧**开始**时写入，而粒子该帧还会经历完整的物理更新（速度积分、重力等），导致Death Event记录的位置比粒子最终消失的渲染位置偏早约一帧的位移量。在高速粒子场景下这一偏差肉眼可见，修正方式是在负载中加入`DeathPos = Pos + Vel * DeltaTime`作为预测位置。

---

## 知识关联

事件系统以**碰撞检测**为最主要的触发来源：只有发射器开启了碰撞检测模块，`Generate Collision Event`节点才有碰撞数据可写入；未开启碰撞的发射器只能使用Death Event或自定义条件事件。理解碰撞检测中`CollisionNormal`的坐标系定义（世界空间，指向碰撞面外侧），才能正确使用反射公式计算接收粒子的初始速度方向。

学完事件系统后，自然引出**数据接口（Data Interface）**的学习需求：当需要将事件触发的结果传递到Niagara系统外部（如通知蓝图、写入贴花系统、读取Skeletal Mesh骨骼位置）时，单靠事件系统的内部缓冲区不够用，必须通过数据接口建立Niagara与引擎其他子系统之间的数据桥梁。两者组合才能构建出"粒子碰撞→事件触发→数据接口写入RenderTarget→动态贴花显示弹孔"这类完整的跨系统特效管线。
