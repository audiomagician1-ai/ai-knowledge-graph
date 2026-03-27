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

在Niagara系统中，**参数（Parameter）**是指在模块脚本之间传递数据的命名变量，而**属性（Attribute）**特指附加在粒子实例上、随粒子生命周期存在的数据字段。两者最本质的区别在于作用域：参数可以存在于System、Emitter、Particle三个命名空间中，而属性专属于Particle命名空间，每一个活跃粒子都拥有独立的属性副本。

Niagara的参数与属性系统在UE4.20（2018年）随Niagara正式发布时引入，取代了旧版Cascade中通过"分布曲线"直接绑定数据的方式。Cascade时代只能通过固定字段（如颜色、速度）修改粒子行为，而Niagara允许用户在模块脚本中**自定义任意数据类型的属性**，包括Float、Vector3、Bool、Int32乃至结构体类型，极大扩展了粒子系统的表达能力。

参数与属性体系的重要性体现在：Niagara的所有模块逻辑，包括粒子的初始化、帧更新和事件响应，**全部通过读写参数与属性来实现数据流通**。一个Spawn模块如果不向`Particles.Position`属性写入初始位置，粒子就不会出现在任何地方；一个Update模块如果不读取`Particles.Velocity`并写回更新后的值，粒子就不会运动。

---

## 核心原理

### 命名空间与作用域规则

Niagara参数系统使用**点分命名空间前缀**来区分变量的作用域和生命周期，共有以下主要命名空间：

| 命名空间 | 前缀示例 | 存在周期 |
|---|---|---|
| 系统级 | `System.` | 整个System资产运行期间 |
| 发射器级 | `Emitter.` | 单个Emitter实例运行期间 |
| 粒子级（属性） | `Particles.` | 单个粒子从Spawn到Kill |
| 用户暴露 | `User.` | 由外部蓝图/C++赋值 |
| 引擎内置 | `Engine.` | 引擎自动提供，只读 |

`Particles.`命名空间下的变量就是粒子属性。当一个粒子被生成时，Niagara为该粒子分配一块连续内存，按属性定义顺序存储每个字段的值；当粒子被Kill时，这块内存释放。这种**结构体数组（SoA）**内存布局保证了SIMD向量化计算的高效性。

### 内置属性与自定义属性

Niagara提供一批**引擎内置粒子属性**，这些属性在渲染器中有直接对应的语义：

- `Particles.Position`（Vector3）：粒子世界位置
- `Particles.Velocity`（Vector3）：每帧位移量，单位cm/s
- `Particles.Color`（LinearColor）：RGBA颜色
- `Particles.SpriteSize`（Vector2）：Sprite渲染时的宽高，单位cm
- `Particles.NormalizedAge`（Float，范围0~1）：粒子归一化寿命

**自定义属性**通过在模块脚本的"Add Parameter"面板中选择`Particles.`命名空间并指定类型来创建。自定义属性一旦在任意模块中被写入，Niagara参数存储（Parameter Store）就会自动为其分配存储空间，无需手动声明结构体字段。

### 读写操作与模块接口的Map Get/Map Set

在Niagara模块脚本（HLSL/节点图）中，读取属性使用**Map Get节点**，写入属性使用**Map Set节点**。每个模块执行时，引擎将当前粒子的所有属性值传入Map Get，模块计算完毕后通过Map Set将新值写回。

关键约束：**同一帧内，同一属性在同一执行阶段（Particle Update）只有最后一次Map Set写入有效**。若两个模块都写入`Particles.Velocity`，执行顺序靠后的模块会覆盖靠前的结果，因此在Emitter的模块堆栈（Stack）中，模块顺序直接影响最终属性值。

`Emitter.`参数与`System.`参数在整个Emitter/System范围内共享同一份数据，所有粒子读取到的值相同，不能被粒子级模块写入——尝试在Particle Update阶段写入`Emitter.`参数会导致编译错误。

### 参数绑定与动态输入

参数还可以通过**动态输入（Dynamic Input）**与外部数据源绑定。例如，将`Emitter.SpawnRate`绑定到`User.SpawnRateOverride`后，蓝图中调用`SetNiagaraVariableFloat("User.SpawnRateOverride", 50.0f)`即可在运行时动态控制发射率，而无需修改模块内部逻辑。这是Niagara实现运行时参数化的标准路径。

---

## 实际应用

**案例1：给粒子添加自定义"质量"属性实现重力变化**

在Spawn模块中，创建`Particles.Mass`（Float）属性并用随机范围`(0.5, 2.0)`初始化。在Update模块中，通过Map Get读取`Particles.Mass`和`Particles.Velocity`，计算重力加速度：`NewVelocity = OldVelocity + (980.0 * InverseMass * DeltaTime * GravityDirection)`，再Map Set写回。这样不同质量的粒子表现出不同的下落速度，而整个逻辑无需修改渲染器配置。

**案例2：User参数驱动颜色渐变**

在蓝图中设置`User.TeamColor`（LinearColor），在Niagara Particle Spawn阶段通过Map Get读取该User参数并写入`Particles.Color`。当蓝图在运行时切换队伍颜色时，新生成的粒子立即应用新颜色，已存在粒子保持原色——这展示了User参数与Particle属性的生命周期差异。

**案例3：Emitter.Age驱动粒子缩放**

`Emitter.Age`是引擎自动维护的Emitter级Float属性，记录Emitter累计运行时间（秒）。在Update模块中读取`Emitter.Age`并以`sin(Age * 3.14159)`映射到`Particles.SpriteSize`，可以让整批粒子同步脉冲缩放，因为所有粒子共享同一个`Emitter.Age`值。

---

## 常见误区

**误区1：认为"在模块中声明属性"等于"属性一定存在"**

Niagara采用**懒惰分配**策略：一个`Particles.`属性只有在至少被一个模块的Map Set节点写入时，才会被实际分配粒子内存。仅在Map Get中读取但从未写入的属性，其值为该类型的默认零值（Float=0, Vector3=(0,0,0)），不会产生报错，但会导致静默的逻辑错误。检查方式是在发射器的"Particle Attributes"面板中确认属性是否出现在列表里。

**误区2：混淆Particle属性与Emitter参数的写入权限**

初学者常在Particle Update阶段尝试累加`Emitter.AccumulatedDamage`来统计全局伤害，结果发现数值不正确或编译报错。正确做法是：粒子只能写入`Particles.`命名空间；若需要粒子影响Emitter级数据，应使用**Emitter Event**或**Event Handler**机制，通过事件将粒子数据传递到Emitter Update阶段处理。

**误区3：以为属性类型可以在运行时更改**

属性的数据类型（Float、Int32、Vector3等）在模块编译时固定，运行时只能修改值而不能修改类型。若将一个已在多处模块中使用的`Particles.CustomData`从Float改为Vector3，所有引用该参数的Map Get/Map Set节点都会出现类型不匹配错误，需要逐一手动修正。规划自定义属性时应预先确定所需精度与维度。

---

## 知识关联

**前置概念：Module脚本**
理解参数与属性必须先掌握Module脚本的节点图结构，因为Map Get和Map Set节点是Module脚本内部的专有节点——在Module脚本之外（如System/Emitter脚本）无法直接操作`Particles.`属性，只能通过模块间接访问。

**后续概念：生成模式（Spawn Mode）**
生成模式（Burst、Rate、Scripted等）决定粒子何时被创建，而粒子被创建的瞬间，Spawn阶段的模块将执行首次属性写入。理解属性的初始化时机（Spawn vs. Update）对于正确使用不同生成模式至关重要：Burst模式下所有粒子在同一帧Spawn，意味着若Spawn模块读取了`Emitter.Age`，所有Burst粒子的该属性初始值相同。

**横向关联：渲染器属性绑定**
Niagara Sprite渲染器、Ribbon渲染器等均通过固定的属性名称（如`Particles.Position`、`Particles.Color`）读取粒子数据，属性命名必须与渲染器期望的名称完全匹配，大小写敏感，否则渲染器将回退到默认值。