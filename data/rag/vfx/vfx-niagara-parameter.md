---
id: "vfx-niagara-parameter"
concept: "参数与属性"
domain: "vfx"
subdomain: "niagara"
subdomain_name: "Niagara系统"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 参数与属性

## 概述

在Niagara系统中，**参数（Parameter）**是数据的具名容器，**属性（Attribute）**则是绑定在特定命名空间下、随粒子生命周期存在的特殊参数。两者共同构成Niagara数据流动的基础单元。最简单的区分方式是：属性属于参数，但参数不一定是属性——"Particles.Velocity"是属性，而"User.SpawnRate"是用户参数，两者都是参数，但只有前者挂载在粒子命名空间下才叫属性。

Niagara参数系统在UE4.20版本随Niagara正式替代Cascade时一并引入，设计目的是解决Cascade中粒子数据硬编码、无法任意扩展的问题。Cascade的粒子模块只能读写固定的内置字段（位置、速度、颜色等），而Niagara允许开发者在任意命名空间下声明自定义float、vector、bool乃至结构体类型的参数，彻底开放了数据层的扩展性。

理解参数与属性的核心价值在于：Niagara的每一个模块脚本（Module Script）的输入输出，本质上都是在对参数进行读写操作。错误地理解参数的生命周期和可见性规则，会直接导致数据在阶段间无法传递，或产生竞态覆盖问题。

---

## 核心原理

### 命名空间（Namespace）决定生命周期

Niagara使用命名空间前缀来区分参数的所有者和存活范围，内置的主要命名空间如下：

| 命名空间 | 典型示例 | 存活范围 |
|---|---|---|
| `Emitter.` | Emitter.Age | 整个发射器生命周期 |
| `Particles.` | Particles.Position | 单个粒子生命周期 |
| `System.` | System.OwnerVelocity | 整个系统生命周期 |
| `User.` | User.SpawnRate | 外部（蓝图/C++）设置 |
| `Engine.` | Engine.DeltaTime | 引擎只读注入 |

`Particles.`命名空间的参数在粒子被Kill时自动释放，下一帧新生的粒子不会继承上一粒子的同名属性值，除非经过显式初始化。`Emitter.`和`System.`参数则跨粒子共享，修改它们会影响同一发射器或系统下的所有粒子。

### 参数类型与内存布局

Niagara参数支持以下基础类型：`float`、`int32`、`bool`、`FVector2D`、`FVector`、`FVector4`、`FLinearColor`、`FQuat`以及用户自定义的Struct。每个`Particles.`属性在GPU模拟中对应一列连续内存（Struct of Arrays布局，SOA），这意味着新增一个`Particles.MyFloat`属性会为该发射器的每个粒子槽位额外分配4字节，当粒子数量达到100万时，单个float属性即占用约3.8 MB显存。因此在移动平台上，减少不必要的自定义粒子属性是显著降低显存占用的直接手段。

### 读写规则与阶段可见性

Niagara将执行分为四个主要阶段：**System Spawn**、**System Update**、**Emitter Spawn**、**Emitter Update**、**Particle Spawn**、**Particle Update**（以及Event和Render阶段）。参数的可读写性遵循以下规则：

- `Particles.`属性只能在Particle Spawn和Particle Update阶段读写；在Emitter阶段无法访问单个粒子的属性。
- `Emitter.`参数可在Emitter Spawn/Update以及所有Particle阶段**读取**，但只能在Emitter阶段**写入**；若在Particle Update中写入`Emitter.`参数，Niagara编辑器会给出警告并标记为竞态写入（Race Condition Write）。
- `User.`参数在所有阶段均只读，只能由外部蓝图通过`SetNiagaraVariableFloat`等函数或`UNiagaraComponent`的参数绑定进行赋值。

在Module脚本内部，参数以引脚形式暴露：标注为`Output`的引脚会在模块执行后将结果写回对应命名空间，标注为`Input`的引脚则在模块执行前读取当前值。同一阶段内多个模块对同一属性的写入，按模块堆栈从上到下的顺序依次覆盖，最后一个写入的模块结果生效。

### 静态参数与动态参数

Niagara还区分**静态参数（Static Parameter）**和普通参数。静态参数以`static`关键字声明，其值在发射器编译时确定，不能在运行时更改，但可以驱动编译分支（类似C++的`constexpr`）。例如，用静态bool控制是否启用某条计算路径，编译器会直接裁剪掉未启用的分支，零运行时开销。这与普通bool参数在运行时做`if`判断有本质区别。

---

## 实际应用

**自定义粒子属性传递颜色渐变数据**：在Particle Spawn阶段用"Initialize Particle"模块写入`Particles.Color`初始值，再在Particle Update阶段用自定义模块读取`Particles.Age`与`Emitter.LifeTime`，计算归一化寿命比值`t = Age / LifeTime`，然后用`Lerp(Color_Start, Color_End, t)`写回`Particles.Color`。这里`Particles.Age`是Niagara内置属性，需要在发射器的Require属性列表中勾选"Particle Age"才会被自动计算。

**User参数驱动运行时爆炸强度**：在Niagara资产中创建`User.ExplosionForce`（类型float），在Particle Update的Force模块中将其读取为径向力乘数。游戏代码通过`NiagaraComponent->SetNiagaraVariableFloat(TEXT("User.ExplosionForce"), 5000.f)`在触发爆炸时实时注入值。注意参数名字符串必须包含`User.`前缀，否则查找失败、赋值静默忽略，这是初学者常见错误。

**Emitter参数统计存活粒子数**：利用`Emitter.AliveParticleCount`（Niagara内置的Emitter属性）在HUD中显示当前粒子数量，通过蓝图读取`UNiagaraComponent::GetNiagaraVariable`并转为`FNiagaraVariable`查询，可实现性能监控面板。

---

## 常见误区

**误区一：认为`Particles.`属性在粒子死亡后仍保留数据**。实际上，粒子被标记为Dead后，其占用的槽位在下一次Compact（粒子池整理）时会被新粒子复用，旧数据不会清零，而是直接被覆盖。因此不能假设新生粒子的自定义属性初始值为0，必须在Particle Spawn阶段显式初始化，否则会出现属性值"继承"了上一批粒子残留数据的幽灵问题。

**误区二：混淆`Emitter.`写入竞态**。多个粒子在同一帧的Particle Update阶段并行执行，若模块脚本写入`Emitter.`参数，不同粒子线程会争抢写入同一地址。Niagara编辑器虽然会显示警告，但不会阻止编译，结果是最终值随线程调度不确定——这种bug极难复现。正确做法是使用专用的Emitter Update模块来写入`Emitter.`参数，或改用支持原子累加的`Emitter.`参数配合Simulation Stage。

**误区三：`User.`参数与`System.`参数的混用**。`System.`参数由系统内部计算（如`System.Age`、`System.ExecutionState`），开发者不应尝试从蓝图写入`System.`命名空间的参数；而`User.`参数专为外部输入设计，具有完整的蓝图/C++ API支持。将自定义的外部控制变量声明为`System.`前缀，会导致蓝图侧的`SetNiagaraVariable`调用静默失效。

---

## 知识关联

**前置概念——Module脚本**：参数与属性是Module脚本的操作对象，Module脚本的每个输入输出引脚本质上就是对命名空间参数的读写声明。没有理解Module脚本的执行模型，就无法判断属性在哪个阶段可写。

**后续概念——生成模式（Spawn Mode）**：生成模式决定粒子何时触发Particle Spawn阶段，而Particle Spawn正是`Particles.`属性初始化的唯一合法时机。Burst生成、Rate生成以及Event生成各有不同的Spawn触发机制，直接影响属性初始化的执行频率和时机选择策略。