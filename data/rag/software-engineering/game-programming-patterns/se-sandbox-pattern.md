---
id: "se-sandbox-pattern"
concept: "沙箱模式"
domain: "software-engineering"
subdomain: "game-programming-patterns"
subdomain_name: "游戏编程模式"
difficulty: 3
is_milestone: false
tags: ["安全"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.519
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 沙箱模式

## 概述

沙箱模式（Sandbox Pattern）是游戏编程中一种让游戏对象拥有自定义行为同时将其操作权限严格隔离的设计模式。其核心思想是：父类提供一组受保护的操作集合（称为"沙箱操作"），子类通过覆盖一个抽象方法来实现各自的行为，但子类只能调用父类提供的操作，无法直接访问全局系统或引擎底层接口。这样一来，行为的多样性由子类保证，而系统安全性和可维护性由父类统一管理。

该模式的概念源自操作系统领域的"沙盒"隔离思想，在游戏编程中由 Robert Nystrom 在其 2014 年出版的《Game Programming Patterns》一书中正式整理为一种独立模式。Nystrom 使用"超级英雄技能"场景来阐释该模式：每个英雄子类（`SkyLaunch`、`Tornado` 等）覆盖 `activate()` 方法实现独特技能，但所有技能操作——如播放音效、移动角色、生成粒子——都只能通过 `Superpower` 父类提供的受保护方法调用，而非直接访问 `AudioSystem::play()` 或 `ParticleSystem::spawn()` 等全局单例。

沙箱模式在游戏项目中尤为重要，因为游戏代码天然具有大量平行的行为变体——武器、技能、敌人 AI 等。若每种行为都直接耦合到全局系统，则修改任何一个底层系统就可能导致数百个行为类需要同步修改。沙箱模式将这种维护代价集中到父类一处，大幅降低了子类的耦合度。

## 核心原理

### 受保护操作集合（沙箱操作）

父类的核心职责是定义一套受保护的方法（`protected` 修饰），这些方法代表了子类被允许执行的所有操作。例如：

```cpp
class Superpower {
protected:
    void playSound(SoundId sound, double volume);
    void spawnParticles(ParticleType type, int count);
    void move(Vector velocity);
    Entity& getEntity();
};
```

子类只能通过这些接口与游戏世界交互。父类内部持有对 `AudioSystem`、`ParticleSystem` 等全局系统的引用，但这些引用对子类完全不可见。这种设计将"知道系统如何运作"的责任限定在父类，子类只需关注"我想要什么效果"。

### 抽象沙箱方法

父类声明一个纯虚方法作为子类实现行为的入口点：

```cpp
class Superpower {
public:
    virtual ~Superpower() {}
    virtual void activate() = 0;  // 沙箱方法
};
```

子类只需覆盖 `activate()`，所有逻辑都写在这一个方法内。整个继承体系中，公开接口只有 `activate()` 一个，对外部代码而言所有超能力是同质的，调用方无需了解具体子类的内部行为。

### 依赖注入与初始化

父类中的全局系统引用通常通过两种方式注入：**构造函数参数传入**或**两段式初始化（init 方法）**。Nystrom 推荐使用静态方法将系统引用存储在父类静态成员中，例如：

```cpp
class Superpower {
public:
    static void init(ParticleSystem* particles, AudioSystem* audio) {
        particles_ = particles;
        audio_ = audio;
    }
private:
    static ParticleSystem* particles_;
    static AudioSystem* audio_;
};
```

这样所有子类实例共享同一组系统引用，避免每个实例都持有冗余指针，内存开销为 O(1) 而非 O(n)（n 为实例数量）。

### 隔离边界的强制性

沙箱模式的隔离依赖编程语言的访问控制机制（C++ 中为 `protected`/`private`，Java 中类似）。父类持有系统引用的成员变量声明为 `private`，受保护操作声明为 `protected`，子类物理上无法绕过这一限制直接访问全局状态。这与接口模式的区别在于：接口模式约束的是外部调用者，而沙箱模式约束的是内部子类实现者。

## 实际应用

**游戏技能系统**是沙箱模式最典型的应用场景。以一款 RPG 游戏为例，可能有 50 种以上的技能各自继承 `Skill` 父类，覆盖 `cast()` 方法。父类提供 `dealDamage(float amount)`、`applyBuff(BuffType, float duration)`、`summonUnit(UnitId)` 等约 10 到 20 个沙箱操作。当游戏引入伤害减免系统时，开发者只需修改父类的 `dealDamage()` 实现，所有 50 种技能的伤害计算自动同步更新。

**敌人 AI 行为**同样适用此模式。每种敌人覆盖 `update()` 方法实现自己的决策逻辑，但移动、攻击、生成特效等具体操作都通过父类 `Enemy` 提供的受保护方法执行。这使得 AI 程序员专注于行为逻辑，而引擎程序员可以独立优化底层移动和渲染系统，两者通过沙箱操作接口解耦。

**脚本化行为**场景中，沙箱模式可以配合热重载使用。父类提供的受保护操作构成了脚本能够调用的 API 白名单，脚本系统运行时只暴露这些接口，防止脚本代码意外访问文件系统或网络等敏感资源。

## 常见误区

**误区一：将沙箱模式等同于通用的模板方法模式。** 模板方法模式的重点是父类定义算法骨架、子类填充特定步骤，父类主动调用子类方法以控制执行顺序；而沙箱模式中父类不调用子类的内部逻辑，只是提供操作工具箱。沙箱方法 `activate()` 的执行时机和流程完全由子类自己决定，父类不施加顺序约束。

**误区二：沙箱操作越多越好。** 有些开发者为了让子类"更灵活"而不断向父类添加受保护方法，最终父类膨胀为一个包含数十个方法的上帝类。Nystrom 明确指出，当父类的受保护操作超过一定数量时，应考虑将部分操作提取为独立的"辅助类"，由父类持有这些辅助类的引用，再通过一个 `protected` 方法暴露给子类，保持父类接口精简。

**误区三：认为沙箱模式只适用于深层继承体系。** 实际上，沙箱模式在只有两层（父类 + 子类）的扁平继承结构中效果最佳。引入三层以上的继承后，中间层既是子类（使用父类沙箱操作）又是父类（为孙类提供操作），职责混乱，维护复杂度急剧上升。项目中应将继承深度控制在 2 层。

## 知识关联

沙箱模式依赖面向对象中的继承和访问控制机制，但不需要其他设计模式作为前置知识，是游戏编程模式中入门难度最低（本文标注难度为 3/9）的模式之一。

该模式与**子类沙箱**（Subclass Sandbox，即 Nystrom 书中的原名）实际上是同一概念的不同译名。在实现层面，父类通常会组合使用**服务定位器模式**（Service Locator）来管理对 `AudioSystem` 等全局服务的访问，两者配合能进一步降低父类对具体系统类型的耦合。若项目中行为变体数量极多且需要运行时动态组合，则应考虑转向**组件模式**（Component Pattern），将固定继承关系替换为灵活的组件挂载，这是沙箱模式在复杂度升级时的自然演进路径。