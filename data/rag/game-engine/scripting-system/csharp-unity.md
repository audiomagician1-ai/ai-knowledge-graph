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
quality_tier: "B"
quality_score: 45.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
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

Unity引擎从2005年起采用C#（以及当时的JavaScript和Boo）作为主要脚本语言，并于2017年起正式弃用UnityScript（JavaScript变体），将C#确立为唯一官方支持的脚本语言。Unity使用的C#运行时基于Mono项目，并在Unity 2018版本后逐步迁移至IL2CPP（Intermediate Language To C++ Plus Plus）编译后端，以提升跨平台性能。

在Unity中编写C#脚本与普通的C#程序有本质区别：脚本文件必须挂载到场景中的游戏对象（GameObject）上才能执行，脚本类通常继承自`MonoBehaviour`基类，通过Unity引擎在特定时机自动回调预定义方法来驱动游戏逻辑，而不是通过`Main()`入口函数启动。

这种设计使得程序员无需手动管理游戏主循环，Unity引擎每帧调用脚本中声明的特定方法，开发者只需在对应方法中填写业务逻辑即可。理解这套机制是编写任何Unity游戏逻辑的前提。

## 核心原理

### MonoBehaviour基类

`MonoBehaviour`是Unity脚本系统的基础类，位于`UnityEngine`命名空间下。继承它的类可以被添加为游戏对象的组件（Component），从而参与引擎的渲染循环与消息分发。

```csharp
using UnityEngine;

public class PlayerController : MonoBehaviour
{
    public float speed = 5.0f;
}
```

`MonoBehaviour`提供了对游戏对象的直接访问能力，例如`this.gameObject`、`this.transform`，以及组件查找方法`GetComponent<T>()`。值得注意的是，`MonoBehaviour`的实例不能通过`new`关键字创建，必须通过`AddComponent<T>()`或在编辑器中拖拽挂载，否则会触发Unity的警告并产生游戏对象引用丢失的问题。

### 生命周期方法

Unity为`MonoBehaviour`定义了一套严格的生命周期回调顺序，引擎在特定阶段自动调用这些方法。以下是最常用方法及其调用时机：

| 方法 | 调用时机 |
|---|---|
| `Awake()` | 对象实例化后立即调用，即使组件被禁用也会执行 |
| `OnEnable()` | 组件被启用时调用 |
| `Start()` | 第一帧`Update()`前调用，且组件必须处于激活状态 |
| `Update()` | 每帧调用一次，频率与帧率相同 |
| `FixedUpdate()` | 每隔固定时间（默认0.02秒，即50Hz）调用一次 |
| `LateUpdate()` | 所有`Update()`执行完毕后调用 |
| `OnDestroy()` | 对象销毁前调用 |

`Awake()`与`Start()`的区别在实际项目中至关重要：当两个脚本存在依赖关系时，应在`Awake()`中初始化自身数据，在`Start()`中引用其他组件，以避免因初始化顺序不确定导致的空引用异常。物理逻辑（如`Rigidbody`的操作）应放在`FixedUpdate()`中，而摄像机跟随角色的逻辑应放在`LateUpdate()`中，以确保在角色位置更新后再移动摄像机。

### 协程（Coroutine）

协程是Unity提供的一种在C#中实现时间分片执行的机制，基于C#的迭代器（`IEnumerator`）实现，而非真正的多线程。协程通过`StartCoroutine()`启动，使用`yield return`暂停执行并在下一个满足条件的时机恢复。

```csharp
IEnumerator FadeOut(float duration)
{
    float elapsed = 0f;
    Color startColor = renderer.material.color;
    
    while (elapsed < duration)
    {
        elapsed += Time.deltaTime;
        float alpha = 1f - (elapsed / duration);
        renderer.material.color = new Color(
            startColor.r, startColor.g, startColor.b, alpha);
        yield return null; // 等待下一帧
    }
}

// 启动协程
StartCoroutine(FadeOut(2.0f));
```

常用的`yield`语句包括：
- `yield return null`：等待下一帧
- `yield return new WaitForSeconds(1.5f)`：等待1.5秒
- `yield return new WaitForFixedUpdate()`：等待下一次`FixedUpdate()`
- `yield return new WaitUntil(() => isLoaded)`：等待条件为真

协程在Unity主线程上执行，因此可以安全访问Unity API，这是它与`Thread`的根本区别。

## 实际应用

**敌人巡逻AI**：利用`Update()`每帧检测玩家距离，当距离小于10单位时触发追逐行为，当距离大于20单位时通过协程平滑过渡回巡逻路径，同时在`OnDestroy()`中停止所有运行中的协程，防止引用已销毁对象引发的`MissingReferenceException`。

**UI加载界面**：使用协程配合`AsyncOperation`实现异步场景加载，通过`loadOperation.progress`属性（值域0到0.9，最后10%由引擎自动完成）更新进度条，整个过程在`LateUpdate()`之前的帧循环中进行，不阻塞渲染线程。

**角色初始化**：在`Awake()`中缓存`GetComponent<Rigidbody>()`的引用，避免在`Update()`中每帧调用`GetComponent`（该函数需遍历组件列表，频繁调用会产生明显性能开销），在`Start()`中读取存档数据并设置初始位置。

## 常见误区

**误区一：混淆`Awake()`和`Start()`的用途**  
许多初学者将所有初始化逻辑放在`Start()`中。当脚本A在`Start()`中调用脚本B的方法，而脚本B此时`Start()`尚未执行时，就会出现数据未初始化的错误。正确做法是：自身组件的变量初始化写在`Awake()`，依赖外部组件的操作写在`Start()`。

**误区二：认为协程是多线程**  
协程的所有代码仍在Unity主线程上顺序执行，`yield return`只是告诉引擎"暂时挂起，之后再回来"。两个协程中间不存在并发竞争，但也无法利用多核CPU并行计算。需要真正并行计算时，应使用C#的`Task`或Unity的Job System，但这些API访问Unity对象时需要额外同步。

**误区三：在`OnDestroy()`之后访问组件**  
当游戏对象被销毁后，其`MonoBehaviour`组件的C#对象仍然存在于内存中，但已与Unity引擎对象脱钩。此时访问`this.gameObject`或`this.transform`会抛出`MissingReferenceException`。Unity重载了`==`运算符，对已销毁对象的null检查会返回`true`，即`destroyedObj == null`为真，这与普通C#对象行为不同。

## 知识关联

学习本概念前需要掌握脚本系统概述中关于"引擎如何通过反射机制发现并调用脚本方法"的原理，Unity正是通过反射扫描继承自`MonoBehaviour`的类，找到`Awake`、`Update`等方法名并在对应时机回调。

掌握`MonoBehaviour`生命周期和协程之后，可以进一步学习Unity的事件系统（UnityEvent）、ScriptableObject数据容器（不继承`MonoBehaviour`，脱离场景独立存在）、以及Unity DOTS（Data-Oriented Technology Stack）中的ECS架构，它以组件数据与系统分离的方式替代了传统的`MonoBehaviour`模式，在处理数千个实体时性能提升可达数十倍。