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
updated_at: 2026-03-26
---


# 沙箱模式

## 概述

沙箱模式（Sandbox Pattern）是游戏编程中一种将游戏对象的自定义行为隔离在受控环境中执行的设计模式。其核心思想是：为游戏实体（通常是基类定义的角色、NPC 或技能对象）提供一组有限的、预先批准的"沙箱操作"，这些操作封装了对游戏世界的合法访问接口，使得子类在实现自身行为时只能通过这些接口与外部系统交互，而无法直接调用任意全局函数或访问任意全局状态。

该模式由 Robert Nystrom 在其 2014 年出版的《Game Programming Patterns》（游戏编程模式）一书中正式归纳命名。在游戏开发实践中，随着游戏规模扩大，程序员面临一个普遍困境：每个 Boss、每个技能、每个 NPC 的行为逻辑各异，但它们都需要访问音效系统、粒子系统、物理系统等共享资源。若子类可以无约束地调用 `AudioEngine::Play()`、`PhysicsWorld::AddForce()` 等全局接口，代码依赖关系会迅速变成一张混乱的蜘蛛网，调试和维护成本极高。

沙箱模式通过强制所有行为代码只能调用基类提供的受保护方法，将对外部系统的依赖集中到基类中管理。这不仅减少了子类与具体底层系统之间的耦合，还为行为逻辑的测试创造了条件——只需替换基类的沙箱方法实现，即可在不启动完整游戏引擎的情况下测试任意子类行为。

---

## 核心原理

### 基类持有权限，子类只写逻辑

沙箱模式的典型结构由两层构成：**基类（Superclass）** 和 **子类（Concrete Subclass）**。基类定义一个纯虚方法 `activate()`（或 `update()`），由各子类实现具体行为；同时基类提供一组 `protected` 的沙箱方法，例如 `playSound(SoundId id)`、`spawnParticles(ParticleType type, Vector3 pos)`、`getHeroPosition()` 等。子类在 `activate()` 中只允许调用这些受保护方法，绝不直接引用音效管理器、渲染器或物理引擎的单例对象。

```cpp
class Superpower {
public:
    virtual ~Superpower() {}
    virtual void activate() = 0;

protected:
    void playSound(SoundId sound) { /* 委托给音效系统 */ }
    void spawnParticles(ParticleType type) { /* 委托给粒子系统 */ }
    double getHeroHealth() { /* 从游戏状态读取 */ }
};

class SkyLaunch : public Superpower {
public:
    void activate() override {
        playSound(SOUND_JUMP);
        spawnParticles(PARTICLE_DUST);
    }
};
```

在上例中，`SkyLaunch` 完全不知道 `AudioEngine` 或 `ParticleSystem` 的存在，它只与基类定义的那 3 个沙箱方法打交道。

### 沙箱方法的两种实现策略

基类的沙箱方法可以采用两种策略向子类提供底层系统访问：

**策略一：基类直接持有系统引用。** 基类构造时通过参数注入或全局服务定位器获取 `AudioSystem*`、`ParticleSystem*` 等指针，沙箱方法直接转发调用。这种方式集中管理依赖，基类内部可见的系统数量通常控制在 4~6 个以内，防止基类自身变得过于臃肿。

**策略二：通过服务定位器（Service Locator）间接访问。** 沙箱方法在调用时通过 `Locator::getAudio()` 动态查找服务。这种方式使基类无需在构造阶段绑定具体实现，便于在测试时替换为空实现（Null Service），对自动化测试友好。

### 子类数量爆炸时的扩展性

沙箱模式尤其适合"同一类型对象有大量行为变体"的场景。一款典型的 RPG 游戏可能有 50 种以上的技能，如果每种技能都继承同一个 `Superpower` 基类，所有技能都只能调用基类批准的沙箱方法，新技能的添加不需要修改任何现有系统，也不会引入新的全局依赖。新增一种技能的成本约等于：新建一个 `.cpp` 文件 + 实现一个 `activate()` 方法，复杂度为 O(1)。

---

## 实际应用

**技能系统**：最经典的应用场景。将每种技能实现为 `Superpower` 的子类，基类提供 `dealDamage(Target*, float)`、`heal(float)`、`addStatusEffect(EffectType)` 等沙箱方法。策划人员如果同时担任脚本编写者，只需学会调用这几十个沙箱方法，而无需了解整个引擎架构。

**NPC 行为脚本化**：许多游戏引擎（如 Unity 的早期 Corgi Engine 插件）使用类似模式，NPC 行为脚本继承基类后只能调用 `MoveTo(Vector2)`、`LookAt(Transform)`、`TriggerAnimation(string)` 等有限接口，防止脚本代码意外修改物理层参数或绕过碰撞检测系统。

**Mod 支持与用户自定义内容**：沙箱模式是游戏 Mod 系统的常见底层架构。通过将允许 Mod 访问的接口封装为沙箱方法，游戏可以对外开放有限的定制能力，同时防止 Mod 代码访问存档加密逻辑或网络通信模块等敏感系统。《Minecraft》的早期插件 API 设计中即包含类似的访问控制层思想。

---

## 常见误区

**误区一：认为沙箱方法越多越好。** 一些开发者为了"方便子类"，将几乎所有底层操作都暴露为沙箱方法，结果基类膨胀到拥有 30 个以上的 `protected` 方法。这反而消除了沙箱模式的意义——子类依然面对一个几乎无限制的接口集合，依赖关系变得不透明。正确做法是刻意限制沙箱方法数量，不超过当前子类群体实际需要的最小集合，通常 8~12 个方法足以覆盖大多数游戏技能系统。

**误区二：将沙箱模式与模板方法模式混淆。** 模板方法模式（Template Method Pattern）中，基类定义算法骨架，子类填充具体步骤，调用顺序由基类控制；而沙箱模式中，`activate()` 的执行流程完全由子类自主决定，基类只负责提供工具方法（沙箱），不干涉子类的逻辑组织。两者都使用继承，但控制权方向相反。

**误区三：沙箱模式等同于安全沙箱（Security Sandbox）。** 游戏编程中的沙箱模式是一种软件设计模式，其"隔离"是通过代码架构约定实现的，依赖编译期的访问控制（`protected` 关键字）。它并不提供操作系统级别的内存隔离或权限限制，无法防止恶意代码通过指针强制转换绕过访问限制。如果目标是运行不可信的第三方代码，需要使用虚拟机或操作系统级沙箱，而非本模式。

---

## 知识关联

沙箱模式天然与**服务定位器模式（Service Locator Pattern）**配合使用：基类的沙箱方法内部通过服务定位器查找具体系统，使基类本身也无需硬编码对特定系统实现的依赖，两种模式相互补充，共同管理全局状态的访问秩序。

在分层架构中，沙箱模式通常位于游戏对象行为层与引擎底层系统层之间，充当访问控制的中间人。若游戏同时使用**组件模式（Component Pattern）**，沙箱方法的作用范围需要仔细划定——技能组件的沙箱基类应只提供与该组件职责相关的操作，而非整个游戏世界的访问权。

对于需要在运行时动态加载行为脚本的游戏，沙箱模式可作为**字节码模式（Bytecode Pattern）**的高层替代方案：字节码模式通过虚拟机指令集限制行为能力，而沙箱模式通过 C++ 继承和访问修饰符实现类似目的，开发复杂度更低，适合团队规模较小、不需要热更新的项目。