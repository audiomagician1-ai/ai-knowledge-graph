---
id: "se-service-locator"
concept: "服务定位器"
domain: "software-engineering"
subdomain: "game-programming-patterns"
subdomain_name: "游戏编程模式"
difficulty: 2
is_milestone: false
tags: ["依赖"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.481
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 服务定位器

## 概述

服务定位器（Service Locator）是一种软件设计模式，它提供一个全局访问点，让代码在不直接依赖具体实现类的情况下获取所需的服务对象。其核心思想是：系统中有一个中央注册表，客户代码向这个注册表请求"我需要一个音频服务"或"我需要一个日志服务"，注册表返回对应的实现对象，而请求方不关心返回的是真实实现还是替代品。

这个模式由 Martin Fowler 在 2004 年的文章《Inversion of Control Containers and the Dependency Injection pattern》中与依赖注入并列讨论，并在 Robert Nystrom 的《Game Programming Patterns》（2014年）一书中作为游戏开发中管理全局服务的推荐方案被专门收录。在游戏编程中，音频引擎、日志系统、事件总线等服务需要被游戏中几乎所有子系统访问，如果每个子系统都直接 `new AudioEngine()`，就会产生硬编码耦合，难以在测试时替换为静音的 Mock 对象。

服务定位器之所以在游戏开发中特别有价值，是因为游戏的测试与发布需要同一套代码支持"有声音"和"无声音"两种状态切换，以及在自动化测试中完全绕过真实的硬件访问。通过服务定位器，只需在游戏初始化阶段注册不同的服务实现，游戏逻辑层的代码无需任何修改即可切换行为。

## 核心原理

### 基本结构：注册表 + 接口 + 实现

服务定位器由三个要素构成。第一是**服务接口**，例如 `IAudio`，声明 `playSound(id)` 和 `stopSound(id)` 等纯虚函数。第二是**具体实现**，例如 `DirectAudio` 实现真实的声卡调用，`NullAudio` 实现什么也不做（所有方法体为空）。第三是**定位器类本身**，通常写成带静态方法的单例，例如：

```cpp
class Locator {
public:
    static IAudio& getAudio() { return *service_; }
    static void provide(IAudio* service) { service_ = service; }
private:
    static IAudio* service_;
};
```

客户代码只需调用 `Locator::getAudio().playSound(EXPLOSION_ID)`，完全不知道背后是 `DirectAudio` 还是 `NullAudio`。

### 空对象（Null Object）的关键作用

服务定位器模式的一个特别设计技巧是**在系统启动前将 `service_` 初始化为 `NullAudio` 实例**，而不是 `nullptr`。这避免了客户代码每次调用前都要判断指针是否为空的冗余检查。`NullAudio` 的 `playSound` 方法体为空，调用它不会崩溃也不会发声。这个技术在《Game Programming Patterns》第16章被称为"Null Service"，其本质是空对象模式（Null Object Pattern）与服务定位器的组合。如果初始化为 `nullptr`，游戏在注册真实服务之前触发任何音频调用都会导致段错误（segfault）。

### Mock 替换与测试

在自动化测试场景下，测试代码在每个测试用例的 `setUp()` 阶段调用 `Locator::provide(new MockAudio())`，`MockAudio` 不仅不发声，还会记录 `playSound` 被调用了几次、传入了什么 ID。测试结束后可以断言：`assertEqual(1, mockAudio.playCount)` 来验证爆炸事件确实触发了一次音效。这种替换能力是服务定位器与全局单例（Global Singleton）最本质的区别——单例的具体类型在编译期固定，无法在运行时替换实现。

### 注册时机与作用域

游戏通常在 `main()` 函数或引擎初始化阶段完成所有服务注册，这称为**Composition Root**（组合根）。部分框架支持分层定位器，例如关卡级服务（每个关卡有独立日志上下文）可以在父级定位器之上叠加，关卡卸载时弹出该层。Unity 引擎的 `ServiceLocator` 插件（Unity 6 Preview 版本中作为实验功能引入）正是采用了这种分层注册机制。

## 实际应用

**游戏音频切换**：在移动游戏中，当检测到设备静音开关打开时，调用 `Locator::provide(new NullAudio())`，此后所有游戏代码调用音频 API 均变为无操作，不需要在 `playSound` 的每个调用点添加 `if (!muted)` 判断。

**平台差异化渲染日志**：PC 版游戏注册 `FileLogger`，主机版游戏注册 `ConsoleLogger`（输出到调试主机），移动版注册 `CrashReportLogger`（发送到云端）。三个平台的游戏逻辑代码调用同一个 `Locator::getLogger().log(msg)`，由发布流程决定注册哪个实现。

**成就系统集成测试**：游戏的成就解锁需要网络请求，但在 CI/CD 自动化测试中不应真正发出网络请求。测试环境注册 `FakeAchievementService`，它在内存中记录解锁记录，测试用例可以在毫秒内验证"玩家首次击杀敌人是否触发了成就解锁逻辑"。

## 常见误区

**误区一：服务定位器就是全局变量的包装**。有人认为 `Locator::getAudio()` 与 `extern AudioEngine gAudio` 没有本质区别，只是换了个写法。关键差异在于：全局变量的类型在编译期固定为 `AudioEngine`，而服务定位器返回的是 `IAudio&` 接口引用，其实际类型可以在运行时通过 `provide()` 更换。这个区别使得 Mock 替换成为可能，全局变量版本做不到这一点。

**误区二：注册前调用返回 nullptr 没关系，判断一下就好**。如前文所述，正确做法是将默认服务初始化为 `NullAudio`（空对象），而不是依赖调用方检查 nullptr。要求每个调用方都写 `if (audio != nullptr)` 会在几百个调用点产生重复代码，而且一旦某处遗漏即触发崩溃。空对象模式将"无服务时的安全行为"封装在一处。

**误区三：服务定位器可以替代所有依赖注入**。服务定位器的依赖是隐式的——从函数签名上看不出 `void enemyDie()` 依赖了音频服务，只有进入函数体才能发现它调用了 `Locator::getAudio()`。依赖注入（构造函数注入）则将依赖写在构造函数参数中，依赖关系一目了然。因此，对于需要精细依赖管理的大型系统，服务定位器适合管理少数真正"全局"的服务（音频、日志），而非所有对象间依赖。

## 知识关联

服务定位器直接解决了"如何不用 `new ConcreteClass()` 就能获取服务"的问题，它依赖面向对象的**接口/抽象类**机制——如果没有 `IAudio` 这样的纯接口，`provide()` 注入不同实现的机制就无从实现。学习服务定位器后，自然的进阶方向是**依赖注入容器**（DI Container），它自动解析构造函数参数并完成注册，解决了服务定位器"隐式依赖"的缺陷。此外，服务定位器通常与**单例模式**对比学习：单例保证一个类只有一个实例且类型固定；服务定位器保证一个服务接口有一个当前绑定实现但类型可替换，二者解决不同维度的问题。在游戏引擎架构中，服务定位器也常与**事件系统**配合——事件总线本身就是一个全局服务，适合通过定位器访问。