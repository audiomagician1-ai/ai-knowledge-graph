---
id: "se-observer-game"
concept: "观察者模式(游戏)"
domain: "software-engineering"
subdomain: "game-programming-patterns"
subdomain_name: "游戏编程模式"
difficulty: 2
is_milestone: false
tags: ["事件"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 观察者模式（游戏）

## 概述

观察者模式在游戏开发中是一种让游戏对象之间实现松耦合通信的设计方式：当某个游戏对象（Subject/被观察者）的状态发生改变时，所有注册了监听的对象（Observer/观察者）都会自动收到通知并做出响应。这种机制在游戏中最典型的三大应用场景是成就系统、事件总线和UI数据绑定。

该模式由GoF（Gang of Four）在1994年出版的《设计模式》中正式定义，但它在游戏工业中的爆发式应用要追溯到2000年代初期大型RPG游戏的成就系统普及。Xbox 360于2005年推出的成就（Achievement）框架让成就系统成为游戏标配，而驱动这类系统的正是观察者模式——游戏逻辑无需感知成就模块的存在，成就模块只需"旁听"游戏事件即可解锁奖励。

游戏中用观察者模式的核心原因是**避免代码间的硬依赖**。如果角色的战斗代码直接调用成就系统的`unlock()`函数，那么拆掉成就系统时战斗代码也会崩溃。用观察者模式后，战斗代码只广播一个`ENEMY_KILLED`事件，任何监听这个事件的系统——成就、任务、统计、UI——都能独立响应，互不干扰。

---

## 核心原理

### 基本结构：Subject、Observer与注册机制

游戏中的观察者模式由三个角色构成。**Subject**维护一个观察者列表，并提供`addObserver(Observer* o)`和`removeObserver(Observer* o)`两个方法。**Observer**是一个接口，只有一个`onNotify(Entity& entity, Event event)`方法。**具体观察者**实现这个接口并在`onNotify`中处理自身关心的事件类型。

```cpp
// 观察者接口
class Observer {
public:
    virtual void onNotify(const Entity& entity, Event event) = 0;
};

// 成就系统作为具体观察者
class Achievements : public Observer {
public:
    void onNotify(const Entity& entity, Event event) override {
        if (event == EVENT_ENTITY_FELL && entity.isHero()) {
            unlock(ACHIEVEMENT_FELL_OFF_A_BRIDGE);
        }
    }
};
```

Subject的`notify()`方法遍历观察者列表并逐个调用`onNotify`，这是一次**同步、顺序调用**，所有观察者会在同一帧内得到通知。

### 游戏成就系统的实现细节

成就系统中，成就的触发条件通常由事件类型（`Event`枚举值）加上Entity状态共同决定。以"从桥上掉落"这一成就为例，物理系统广播`EVENT_ENTITY_FELL`，成就系统在`onNotify`里判断该Entity是否是玩家英雄：两个条件同时满足才解锁成就。这意味着成就系统需要持有游戏状态的读取权限，但**无需修改任何战斗或物理代码**。

在实践中，成就系统的观察者通常作为单例，在游戏初始化时一次性注册到所有它关心的Subject上，并在游戏退出时自行注销，以避免空悬指针问题（Dangling Observer）。

### UI数据绑定与事件总线

游戏UI（血量条、金币显示、地图标记）是观察者模式的另一主战场。角色的`Health`属性作为Subject，`HpBarUI`作为Observer注册其上。当`Health`从100变为75时，Subject调用`notify()`，`HpBarUI`收到通知后仅更新渲染数值，完全不关心是谁造成了伤害。

更大型的游戏通常使用**事件总线（Event Bus）**变体：一个全局的`EventQueue`替代各个Subject直接持有观察者列表。事件发布者把事件压入队列，事件总线在每帧`update()`时统一分发。这种方式将同步通知改为**异步、延迟一帧**的通知，避免在通知链中途修改游戏状态导致的不一致问题，但同时引入了时序复杂度。

### 观察者列表的内存管理

游戏中Observer的销毁是常见陷阱。当一个敌人对象被销毁但它的指针仍留在Subject的`observers_`列表中时，Subject下次调用`notify()`会产生未定义行为。解决方案有两种：一是在析构函数中强制调用`removeObserver(this)`；二是使用弱引用（`weak_ptr`）存储观察者，每次通知前先检测指针是否仍然有效。在Unity引擎中，`UnityEvent`通过内部引用追踪机制自动处理这个问题，C# 的`event`关键字也提供了类似保障。

---

## 实际应用

**Steam成就系统集成**：游戏代码中的战斗、收集、探索模块各自广播事件，一个专门的`SteamAchievementObserver`监听全部事件类型，在满足条件时调用`SteamUserStats()->SetAchievement("ACH_WIN_ONE_GAME")`。整个Steam集成代码与游戏逻辑完全隔离，删除或替换成就平台只需替换这一个观察者类。

**RPG任务追踪**：任务系统注册为怪物击杀、道具拾取、区域进入等Subject的观察者。玩家接受"击杀10只狼"任务时，任务对象动态调用`wolfSubject.addObserver(this)`；任务完成时调用`removeObserver(this)`，不会在任务结束后继续浪费通知开销。

**实时UI更新**：在一个射击游戏中，子弹数量（Ammo）是Subject，弹药UI、换弹提示音效、控制器震动这三个系统分别作为独立Observer。开枪扣动扳机的代码只调用`ammo_.subtract(1)`，剩余三个响应完全由观察者自主处理，新增"弹药不足警告灯"功能只需新增一个Observer，不改任何已有代码。

---

## 常见误区

**误区一：通知链中修改观察者列表**
在`notify()`的遍历过程中，某个Observer的`onNotify()`内部触发了另一个`addObserver()`或`removeObserver()`调用，会导致迭代器失效或跳过通知。正确做法是在`notify()`遍历前对`observers_`列表做一份拷贝，或使用"待处理队列"延迟变更到遍历结束后执行。

**误区二：把所有事件都合并进一个超级Subject**
开发者有时为了"方便"将所有游戏事件汇聚到一个全局`GameEventManager`，导致每个Observer的`onNotify`中塞满了`switch(event)`分支。正确方式是让每个有意义的游戏状态对象（角色、关卡、物品）各自作为独立Subject，Observer只注册它真正关心的Subject，而非接收全部噪音事件。

**误区三：误以为观察者模式与命令模式等价**
命令模式（游戏）将操作封装为可撤销的对象（如"移动命令"），用于输入处理和操作历史记录；观察者模式关注的是状态变化的广播与响应。两者可以组合使用——命令执行完成后广播一个事件，观察者响应该事件——但它们解决的是完全不同的问题。

---

## 知识关联

**与通用观察者模式的关系**：通用观察者模式定义了Subject/Observer的抽象结构，游戏中的版本在其基础上强调**每帧生命周期管理**（注册/注销时机与帧循环的协调）和**内存安全**（游戏对象的高频创建销毁要求更严格的指针管理），这是纯设计模式教材不涉及的游戏特有约束。

**与命令模式（游戏）的关系**：命令模式通常作为输入层的前端，将玩家输入转化为命令对象并执行；命令执行后产生的游戏状态变化可以通过观察者模式向后端的成就、UI、任务系统广播。两个模式在游戏架构中形成一个完整的"输入→执行→广播→响应"管线。

**通向子类沙箱的过渡**：观察者模式解决了不同系统间的通信问题，但当一个游戏中存在数百种技能或行为、每种都需要发出不同事件时，如何组织每个行为类的内部结构就成为新问题。子类沙箱模式通过在基类中提供一组受保护的"沙箱方法"（包括广播事件的接口），让子类专注于行为逻辑而不暴露在完整的系统访问权限中，是对观察者事件发布端的进一步封装。