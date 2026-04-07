---
id: "vfx-niagara-emitter"
concept: "Emitter与System"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Emitter与System

## 概述

在Unreal Engine的Niagara特效框架中，**System（系统）** 是最顶层的资产容器，而**Emitter（发射器）** 是嵌套在System内部的功能单元，负责定义一类粒子的行为逻辑。一个Niagara System可以包含一个或多个Emitter，每个Emitter独立管理自己的粒子生命周期，但它们共享同一个System级别的时间轴和世界空间坐标。这种两层嵌套结构是Niagara区别于旧版Cascade系统的核心设计之一——Cascade中每个粒子系统只有一套发射逻辑，而Niagara允许多Emitter协作产生复杂效果。

Niagara系统于Unreal Engine 4.20版本进入公开预览，并在UE 4.26版本正式取代Cascade成为官方推荐特效工具。System与Emitter的分层架构从设计之初就是为了支持**数据驱动型特效**：美术师可以在一个System中组合烟雾Emitter、火焰Emitter和火星Emitter，三者同步播放，形成完整的篝火效果，而不需要在关卡中放置三个独立的Actor。

这种层级关系的实际意义在于：System级别的参数（如整体播放速度、世界位置）对所有子Emitter生效，而Emitter级别的参数（如粒子颜色、粒子数量上限）只影响本Emitter内部的粒子。理解这个边界是正确组织Niagara特效资产、避免参数覆盖冲突的前提。

---

## 核心原理

### System的结构与职责

一个Niagara System资产（文件扩展名为`.uasset`，内容浏览器中显示为橙色火焰图标）包含以下三个固定层级：

1. **System级堆栈（System Stack）**：包含`System Spawn`和`System Update`两个执行阶段，控制整个System的初始化与每帧更新逻辑，例如设置System的存活时长或响应游戏事件触发整体停止。
2. **Emitter列表**：按从上到下的顺序排列，Emitter之间的渲染顺序默认与列表顺序一致，编号从0开始。
3. **用户暴露参数（User Exposed Parameters）**：System级别可向外部Blueprint或C++暴露变量，供关卡蓝图在运行时动态修改，例如`User.Color`或`User.SpawnRate`。

System本身不直接生成粒子，所有粒子都由其内部的Emitter负责产生。

### Emitter的四个执行阶段

每个Emitter内部有四个固定的脚本执行阶段，理解这四阶段是正确配置Emitter的基础：

| 阶段 | 触发时机 | 典型用途 |
|---|---|---|
| **Emitter Spawn** | Emitter首次激活时执行一次 | 初始化Emitter级别变量 |
| **Emitter Update** | 每帧执行一次 | 控制每帧生成多少粒子（SpawnRate） |
| **Particle Spawn** | 每个粒子诞生时执行一次 | 设置粒子初始位置、速度、颜色 |
| **Particle Update** | 每帧对每个存活粒子执行 | 施加重力、更新粒子颜色随时间变化 |

这四个阶段在Emitter编辑器左侧的**选择堆栈（Selection Stack）** 中以垂直顺序排列，每个阶段下可添加若干Module脚本，按从上到下的顺序依次执行。

### Emitter的继承机制

Niagara支持**Emitter继承（Emitter Inheritance）**，允许一个子Emitter继承父Emitter的所有Module配置。在内容浏览器中右键点击已有Emitter并选择"Create Child Emitter"即可创建子Emitter。子Emitter默认锁定父级Module，只能在父级留出的`Override`插槽中修改参数，无法删除父级Module。这种设计常用于制作特效变体——例如一个基础火焰Emitter派生出"蓝色火焰"和"绿色火焰"两个子版本，共享粒子运动逻辑，只修改颜色曲线。

### System与Emitter的数据命名空间

Niagara使用命名空间（Namespace）区分不同层级的变量访问权限：

- `System.`前缀：只能在System堆栈中读写，Emitter可读取但不能写入
- `Emitter.`前缀：该Emitter私有，其他Emitter无法直接访问
- `Particles.`前缀：每个粒子实例独立持有的属性，如`Particles.Position`、`Particles.Age`
- `User.`前缀：从外部传入的参数，所有层级均可读取

跨Emitter通信必须通过System级别的**事件（Event）** 系统或**数据接口（Data Interface）** 实现，不能直接在Emitter之间共享`Emitter.`命名空间变量。

---

## 实际应用

**篝火特效的多Emitter组织方式**：在一个名为`FX_Campfire`的Niagara System中，美术师通常会创建四个Emitter：`EM_Fire`（主火焰，使用Sprite渲染器，粒子数上限约200）、`EM_Smoke`（烟雾，使用Sprite渲染器，粒子数上限约50，`Emitter.Age`延迟0.5秒后激活）、`EM_Embers`（火星，使用Mesh渲染器，粒子数上限约30）、`EM_Heat_Distortion`（热浪扭曲，使用专用材质的Sprite渲染器，单粒子常驻）。四个Emitter共享System的世界坐标，当关卡蓝图调用`Set Niagara Variable Float`修改`User.Intensity`时，四个Emitter的SpawnRate同时缩放。

**运行时动态增减Emitter的替代方案**：Niagara System一旦烘焙，无法在运行时增减Emitter数量，但可通过将不需要的Emitter的`SpawnRate`设置为0或调用`SetEmitterEnable`节点来模拟启用/禁用效果，这是制作可配置特效预设时的标准做法。

---

## 常见误区

**误区一：认为每个Emitter是独立的Actor，可以单独移动**

Emitter不是场景Actor，它没有独立的Transform组件。Emitter中所有粒子的世界位置由System Actor的Transform决定，如果需要某个Emitter的粒子从不同位置发射，必须在该Emitter的`Particle Spawn`阶段使用`Add Velocity`或`Shape Location` Module来偏移粒子的初始位置，而不是移动Emitter本身。

**误区二：在Emitter Update阶段修改`Particles.Position`**

`Particles.Position`属于每粒子数据，在`Emitter Update`阶段（该阶段每帧只执行一次，不遍历粒子）修改`Particles.Position`不会产生任何效果，必须在`Particle Update`阶段才能逐粒子修改位置属性。许多初学者因此误认为位置偏移Module失效，实际上是放置阶段错误。

**误区三：将System参数与Emitter参数混淆**

在Niagara编辑器中，System堆栈显示在Emitter列表上方，两者共用同一个编辑器面板，容易造成"我添加的Module是System级还是Emitter级"的困惑。判断方法是查看左侧选择堆栈的缩进层级：顶层的`System Spawn/Update`属于System级，缩进在具体Emitter名称下方的`Emitter Spawn/Update/Particle Spawn/Particle Update`属于该Emitter级。

---

## 知识关联

学习Emitter与System的层级关系需要以**Niagara系统概述**为基础，了解Niagara的整体设计目标和编辑器界面布局，否则难以辨认System堆栈与Emitter堆栈在UI上的位置差异。

掌握本概念后，下一步是学习**Module脚本**——Module是填充在Emitter四个执行阶段中的功能单元，理解Emitter阶段的执行顺序（Emitter Spawn → Emitter Update → Particle Spawn → Particle Update）是正确排列和调试Module执行逻辑的直接前提。此外，Emitter的命名空间规则（`Emitter.`、`Particles.`、`User.`）也是后续学习**Scratch Pad Module**和**动态输入（Dynamic Input）** 时变量作用域问题的重要参考依据。