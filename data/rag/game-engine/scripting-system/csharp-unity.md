---
id: "csharp-unity"
concept: "C#在Unity中的使用"
domain: "game-engine"
subdomain: "scripting-system"
subdomain_name: "脚本系统"
difficulty: 2
is_milestone: false
tags: ["Unity"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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


# C#在Unity中的使用

## 概述

Unity引擎从2005年发布起便采用C#作为主要脚本语言（早期也支持JavaScript和Boo，但这两者已于Unity 2017版本后被弃用）。C#在Unity中的使用并非标准的C#控制台程序写法，而是依托一套名为**Mono**（后期过渡至IL2CPP）的运行时环境，配合Unity特有的类库运作。开发者编写的每一个脚本文件都是一个继承自`MonoBehaviour`的类，通过挂载（Attach）到游戏对象（GameObject）上才能在场景中生效。

C#在Unity中的核心特殊之处在于：代码执行的入口不是传统的`Main()`函数，而是由Unity引擎在特定时机自动调用的**生命周期方法**。这意味着开发者必须理解Unity的帧循环机制，才能正确控制游戏逻辑的初始化、更新和销毁时序。此外，Unity引擎对C#的多线程支持有严格限制——大多数Unity API只能在主线程上调用，这催生了独特的**协程（Coroutine）**机制来处理异步和延时逻辑。

## 核心原理

### MonoBehaviour：脚本的基础类

`MonoBehaviour`是`UnityEngine`命名空间下的抽象基类，所有可挂载到GameObject的脚本都必须直接或间接继承它。一个最简单的Unity脚本骨架如下：

```csharp
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    void Start() { }
    void Update() { }
}
```

继承`MonoBehaviour`后，脚本实例由Unity的场景管理器统一管理，**不能**使用`new PlayerController()`来创建实例，而必须通过`AddComponent<PlayerController>()`或在Inspector面板拖拽挂载。`MonoBehaviour`提供了`enabled`属性、`gameObject`引用、`transform`快捷访问等数十个内置成员，这些都是标准C#类所没有的。

### 生命周期方法的执行顺序

Unity的生命周期方法有严格的调用顺序，理解错误会导致空引用或初始化时序Bug。主要生命周期方法按调用先后排列：

1. **Awake()** — 对象被实例化时立即调用，即使脚本`enabled = false`也会执行，适合初始化本对象自身的数据。
2. **OnEnable()** — 脚本组件被启用时调用。
3. **Start()** — 第一帧`Update`之前调用，且仅调用一次，适合引用其他已初始化的组件。
4. **FixedUpdate()** — 固定物理时间步长调用，默认间隔为**0.02秒（50次/秒）**，物理计算（Rigidbody）应放在此处。
5. **Update()** — 每帧调用一次，间隔由帧率决定（不固定）。
6. **LateUpdate()** — 同帧内所有`Update()`执行完毕后调用，适合相机跟随逻辑。
7. **OnDisable()** / **OnDestroy()** — 组件禁用或对象销毁时调用，适合释放资源或取消事件订阅。

`Awake`与`Start`的关键区别常被误用：当场景中对象A需要引用对象B的某个在`Awake`中初始化的数据时，A应在`Start`中获取该引用，而非`Awake`（因为多个对象`Awake`的执行顺序不保证）。

### 协程（Coroutine）机制

Unity协程基于C#的迭代器（`IEnumerator`）语法实现，通过`yield return`暂停执行，在下一个特定时机恢复，全程运行在**主线程**上，而非新开线程。基本用法：

```csharp
IEnumerator FadeOut()
{
    float alpha = 1f;
    while (alpha > 0f)
    {
        alpha -= Time.deltaTime;
        // 设置透明度...
        yield return null; // 暂停到下一帧
    }
}

void Start()
{
    StartCoroutine(FadeOut());
}
```

`yield return`后可接不同对象来控制恢复时机：
- `yield return null` — 等待下一帧`Update`后
- `yield return new WaitForSeconds(2f)` — 等待2秒（受`Time.timeScale`影响）
- `yield return new WaitForFixedUpdate()` — 等待下一次`FixedUpdate`
- `yield return new WaitForEndOfFrame()` — 等待当前帧渲染完毕

协程需要通过`StartCoroutine()`启动、`StopCoroutine()`停止，且对象或组件被禁用时协程自动终止。

## 实际应用

**场景切换后的持久化对象**：使用`DontDestroyOnLoad(gameObject)`可让对象在场景切换时不被销毁，通常在`Awake`中配合单例模式实现全局管理器（GameManager）。

**碰撞检测回调**：`MonoBehaviour`提供`OnCollisionEnter(Collision col)`、`OnTriggerEnter(Collider other)`等物理事件方法，Unity物理引擎在检测到碰撞时自动调用，参数`Collision`或`Collider`包含碰撞点、法线、碰撞对象等具体数据。

**UI事件响应**：将脚本挂载到Canvas下的Button对象，通过`OnClick()`事件绑定或实现`IPointerClickHandler`接口，处理用户交互——这是Unity UI系统（uGUI）特有的事件分发机制。

**协程实现倒计时**：
```csharp
IEnumerator Countdown(int seconds)
{
    for (int i = seconds; i >= 0; i--)
    {
        countdownText.text = i.ToString();
        yield return new WaitForSeconds(1f);
    }
    LoadNextScene();
}
```
此模式比在`Update()`中用浮点数累加更直观，代码结构也更清晰。

## 常见误区

**误区一：混淆`Awake`与`Start`的使用场景**
许多初学者将所有初始化逻辑都写在`Start()`中，当两个脚本在`Start`中互相依赖对方的数据时，就会出现竞态问题。正确做法是：初始化自身私有变量在`Awake`，获取外部组件引用在`Start`，这利用了Unity保证所有`Awake`在任何`Start`之前完成的执行顺序保证。

**误区二：在协程中执行阻塞操作等同于多线程**
协程只是在主线程上模拟"分时执行"，`yield return`之间的代码块仍然阻塞主线程。如果在两个`yield return`之间执行了耗时100ms的循环，游戏帧率就会下降。真正的后台线程需使用C# `System.Threading`或Unity的`Job System`，但这些线程中不能调用`UnityEngine` API（如`GameObject.Find`会抛出异常）。

**误区三：`Update`中使用`Time.deltaTime`的场合判断错误**
物理相关的移动代码（如`Rigidbody.AddForce`）应在`FixedUpdate`中执行，此时使用`Time.fixedDeltaTime`（固定值0.02秒）；非物理的Transform移动可在`Update`中使用`Time.deltaTime`。将物理代码放入`Update`会导致帧率变化时物理行为不稳定，这是Unity C#使用中高频出现的性能与逻辑错误。

## 知识关联

本文档建立在**脚本系统概述**的基础上，后者介绍了为何游戏引擎需要脚本语言，以及脚本与引擎之间的通信原理。掌握C#的`MonoBehaviour`生命周期和协程后，开发者能够直接应用于Unity项目中的物理系统（`FixedUpdate`+`Rigidbody`）、动画状态机触发（`Animator.SetTrigger`）、资源异步加载（`UnityWebRequest`配合协程）等所有具体功能模块，因为这些系统的调用入口都依赖于本文所述的生命周期方法框架。协程机制与Unity 2019.3引入的`async/await`原生支持也存在对应关系——理解`yield return`的暂停-恢复原理有助于后续学习`UniTask`等现代异步模式。