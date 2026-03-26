---
id: "se-prototype-game"
concept: "原型模式(游戏)"
domain: "software-engineering"
subdomain: "game-programming-patterns"
subdomain_name: "游戏编程模式"
difficulty: 2
is_milestone: false
tags: ["创建"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.429
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 原型模式（游戏）

## 概述

原型模式在游戏编程中的核心用途是**运行时克隆现有对象**，而非每次从零重新构建。当游戏需要瞬间生成数百只怪物、数千颗子弹或大量地图装饰物时，从原型直接复制比调用构造函数并逐一初始化快得多。原型模式的接口极其简洁：每个可克隆对象仅需实现一个 `clone()` 方法，返回自身的完整副本。

该模式在游戏领域的普及很大程度上源于 2009 年 Robert Nystrom 在其《游戏编程模式》（*Game Programming Patterns*）一书中对其与 Prefab 系统关系的系统阐述。Nystrom 特别指出，Unity 引擎的 `GameObject.Instantiate()` 函数本质上就是原型模式的直接实现——传入一个已配置好的对象（即"原型"），函数返回其深拷贝副本并将其放入场景。

游戏中大量实体（敌人、道具、特效粒子）具有相同的初始配置，但每个实例在运行时拥有独立状态（血量、位置、速度）。原型模式允许美术和策划人员在编辑器中配置好一个"模板对象"，程序员只需调用 `Instantiate(prefab, position, rotation)` 即可批量生产，做到数据驱动与代码解耦。

---

## 核心原理

### 克隆接口与浅拷贝/深拷贝的抉择

游戏中的原型克隆分为**浅拷贝（Shallow Copy）**和**深拷贝（Deep Copy）**两种，选择错误会导致严重 bug。浅拷贝仅复制对象的值类型字段和引用地址，多个克隆体共享同一份子对象（如共享一个 `Inventory` 列表）；深拷贝则递归复制所有子对象，每个克隆体拥有完全独立的数据。

对于敌人原型，血量（`int hp`）是值类型，浅拷贝即可正确复制；但背包（`List<Item> inventory`）是引用类型，必须深拷贝，否则所有克隆怪物共享同一个背包，击杀其中一只会让所有同类怪物同时掉落装备。

```csharp
// C# 中的深拷贝克隆示例（Unity 风格）
public class Enemy : MonoBehaviour, ICloneable {
    public int hp;
    public List<Item> loot;

    public object Clone() {
        Enemy copy = (Enemy)this.MemberwiseClone(); // 浅拷贝
        copy.loot = new List<Item>(this.loot);       // 手动深拷贝引用字段
        return copy;
    }
}
```

### Unity Prefab 系统作为原型模式的工业实现

Unity 的 Prefab 是原型模式最成熟的游戏引擎实现。一个 Prefab 文件存储的是完整的 GameObject 层级结构（包含 Transform、Collider、脚本组件及其序列化字段），它本身不出现在运行时场景中，只作为"模板"存在于磁盘。调用 `Instantiate()` 时，Unity 引擎在内存中对这份模板执行深拷贝，生成一个独立的运行时实例。

Prefab Variants（Prefab 变体，Unity 2018.3 引入）进一步扩展了原型的概念：子变体继承父 Prefab 的所有属性，只覆盖差异部分，类似面向对象的继承，但不需要编写任何代码。例如"精英哥布林"Prefab Variant 可以继承"普通哥布林"的动画、碰撞体，只修改 `hp = 200`（普通版为 `hp = 50`）和材质颜色。

### 对象池与原型模式的结合

游戏中频繁 `Instantiate` 和 `Destroy` 会触发垃圾回收（GC），导致帧率卡顿。标准做法是将原型模式与**对象池（Object Pool）**组合使用：启动时从原型克隆出固定数量的对象并放入池中，需要时从池中取用（`SetActive(true)`），用完归还（`SetActive(false)`），完全绕过运行时的内存分配与回收。Unity 2021 LTS 起内置了 `UnityEngine.Pool.ObjectPool<T>` 类，其构造函数的 `createFunc` 参数就是传入一个原型的克隆工厂函数。

---

## 实际应用

**子弹生成系统**：射击游戏中玩家每秒可能发射 10-20 颗子弹，若每颗都 `new` 一个对象并逐字段赋值，每帧分配的内存会迅速积累触发 GC。实践中预先配置一个"子弹原型" Prefab（包含 Rigidbody、碰撞体、伤害数值、特效引用），游戏启动时克隆 50 个放入对象池，射击时从池中取出并重置位置与速度，性能开销降低约 80%。

**程序化地图生成**：Roguelike 游戏（如《以撒的结合》）在每次游玩时随机生成关卡。房间装饰物（桌子、蜡烛、尸体）并非硬编码，而是维护一张"原型注册表"（`Dictionary<string, GameObject> prototypeRegistry`），地图生成算法按概率从注册表中取出对应原型并克隆到目标坐标，数据与生成逻辑完全分离。

**技能效果的参数化克隆**：RPG 中同一类型的火球术可能有"普通/强化/暴击"三个等级。通过在基础火球 Prefab 上克隆并修改 `damage`、`scale`、`particleColor` 三个参数，就能在运行时动态生成差异化的技能实例，无需为每个等级单独创建 Prefab 文件。

---

## 常见误区

**误区一：认为 `Instantiate` 总是深拷贝所有数据**
Unity 的 `Instantiate` 对 Prefab 上的序列化字段执行深拷贝，但对**静态变量**和**单例引用**不做任何拷贝——它们天生是所有克隆体共享的。若在敌人脚本中使用静态字段存储击杀计数，所有克隆体实际上修改的是同一个变量，这不是克隆 bug，而是对静态作用域的误解。

**误区二：Prefab Variant 等同于运行时克隆**
Prefab Variant 是编辑期（Edit-time）的原型继承，解决的是 Prefab 资产管理与配置复用问题；`Instantiate()` 是运行时（Runtime）的对象克隆，解决的是实例生成问题。两者都是原型模式的体现，但作用阶段完全不同。混淆二者会导致：试图在运行时通过修改 Variant 来影响已有实例（无效），或在编辑器中用大量独立 Prefab 替代 Variant（资产臃肿，后期维护困难）。

**误区三：原型模式可以替代工厂模式**
游戏中工厂模式负责**决定创建哪种类型**的对象（根据枚举、配置表选择不同 Prefab），原型模式负责**如何复制**一个已确定的对象。子弹工厂（`BulletFactory`）通过查表选出正确的子弹原型，再调用 `Instantiate` 克隆它——二者在游戏代码中通常协同出现，而非互相替代。

---

## 知识关联

原型模式的前置知识是 GoF 设计模式体系中的**原型模式（Prototype Pattern）**通用定义，其中 `ICloneable` 接口与 `Clone()` 方法的概念直接沿用到游戏实现中。理解浅拷贝与深拷贝的内存语义（堆栈布局、引用类型与值类型区别）是正确实现游戏克隆逻辑的基础，缺失这一知识点会导致本文"误区一"中的共享状态 bug。

在游戏编程模式体系内，原型模式与**对象池模式**紧密配合——原型解决"如何生成副本"，对象池解决"如何复用副本以避免 GC"，二者合用是游戏高频对象管理的标准解法。理解了原型模式在 Unity Prefab 系统中的实现方式后，学习**组件模式（Component Pattern）**会更为顺畅，因为 Prefab 的层级克隆本质上就是对组件树的递归复制。