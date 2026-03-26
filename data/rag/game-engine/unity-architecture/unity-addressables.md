---
id: "unity-addressables"
concept: "Addressables"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 2
is_milestone: false
tags: ["资源"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.5
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

# Addressables（可寻址资产系统）

## 概述

Addressables 是 Unity 于 2019 年正式发布的资源管理系统（Package 版本 1.0），用于替代传统的 `Resources.Load()` 和 AssetBundle 手动管理方式。它的核心设计思想是：给每个资源分配一个**字符串地址（Address）**，开发者通过这个地址异步加载资源，而不需要关心资源物理上存储在哪里——本地还是远程服务器。

在 Addressables 出现之前，Unity 项目的资源管理极为分散：`Resources` 文件夹会将所有资源打包进安装包导致包体膨胀，而原生 AssetBundle 又需要手动追踪依赖、手动引用计数、手动卸载，极易产生内存泄漏。Addressables 在底层仍然使用 AssetBundle 作为打包格式，但将复杂的依赖分析、加载、引用计数全部自动化。

对于任何包体超过 100MB 的 Unity 项目，Addressables 几乎是必选方案。它支持**热更新资源**（将资源托管在 CDN 服务器上，运行时按需下载），这对手机游戏的版本迭代至关重要，可以做到无需重新提交应用商店即可更新美术资源。

---

## 核心原理

### 地址与标签系统

每个资源在 Addressables 系统中拥有一个唯一的**地址字符串**，例如 `"Assets/Prefabs/Enemy.prefab"` 或自定义的 `"enemy_boss"`。地址本质上是一个键（Key），存储在**内容目录（Content Catalog）** 这个 JSON 文件中，该目录将地址映射到实际资源的物理位置。

除了单个地址，Addressables 还支持**标签（Label）**，例如给所有角色贴图打上 `"characters"` 标签，然后通过一次调用加载该标签下的全部资源。一个资源可以同时拥有多个标签，实现灵活的批量加载。

### 异步加载机制

Addressables 的所有加载操作均为**异步**，返回类型是 `AsyncOperationHandle<T>`。以下是典型的加载代码：

```csharp
AsyncOperationHandle<GameObject> handle = 
    Addressables.LoadAssetAsync<GameObject>("enemy_boss");
handle.Completed += (op) => {
    if (op.Status == AsyncOperationStatus.Succeeded)
        Instantiate(op.Result);
};
```

`AsyncOperationHandle` 封装了操作进度（`PercentComplete` 属性，范围 0.0f ~ 1.0f）和操作状态，也可在 `async/await` 协程中使用 `await handle.Task` 语法。异步设计避免了加载大型资源时主线程卡顿的问题。

### 引用计数与释放

Addressables 内部维护每个已加载资源的**引用计数**。每次调用 `LoadAssetAsync` 时计数 +1，每次调用 `Addressables.Release(handle)` 时计数 -1，计数归零后资源才从内存中卸载。这意味着开发者**必须**主动调用 `Release`，否则资源永远不会被卸载。`Addressables.InstantiateAsync()` 实例化的对象需要用 `Addressables.ReleaseInstance()` 而非普通的 `Destroy()` 来确保引用计数正确递减。

### 分组与打包策略

资源在编辑器中被组织成**组（Group）**，每个组对应一个 AssetBundle 打包单元。组的打包模式有两种关键设置：
- **Pack Together**：组内所有资源打成一个 Bundle，适合总是同时使用的资源（如某关卡的所有素材）。
- **Pack Separately**：每个资源单独一个 Bundle，粒度更细但 HTTP 请求数量增加。

依赖关系由系统自动分析：若 PrefabA 和 PrefabB 共享同一张贴图，Addressables 会自动将贴图提取到独立 Bundle 避免重复打包。

---

## 实际应用

**手机游戏关卡热更新**：将每个关卡的场景和美术资源分为独立的 Addressable 组，托管在阿里云 OSS 或 AWS S3 上。玩家首次进入新关卡时，系统通过 `Addressables.DownloadDependenciesAsync("level_3")` 下载资源包，显示进度条，下载完成后再加载关卡，整个过程无需更新 APK/IPA。

**角色换肤系统**：将每套皮肤的贴图和材质赋予相同标签 `"skin_fire"`，使用 `Addressables.LoadAssetsAsync<Texture2D>("skin_fire", callback)` 一次性加载该套皮肤的全部贴图资源，替换到角色材质上，使用完毕后统一释放。

**对象池集成**：在对象池中，通过 `Addressables.InstantiateAsync()` 预生成对象并存入池，回收时调用 `gameObject.SetActive(false)` 而非 `ReleaseInstance`，最终销毁整个池时才批量释放，避免频繁加载/卸载的性能开销。

---

## 常见误区

**误区一：使用 `Destroy()` 销毁由 Addressables 实例化的对象**  
通过 `Addressables.InstantiateAsync()` 创建的 GameObject，若直接调用 `Destroy(go)`，Unity 会销毁游戏对象但 Addressables 内部的引用计数不会递减，对应的 AssetBundle 永远留在内存中。正确做法是调用 `Addressables.ReleaseInstance(go)`，它会同时销毁对象并更新引用计数。

**误区二：认为 Addressables 系统中无需关心打包分组**  
初学者常将所有资源放入默认的 `Default Local Group`，导致整个项目打成一个超大 Bundle。这会使任何单个资源更新都需要重新下载整个 Bundle。合理的策略是按更新频率分组：基础框架资源（低频更新）和活动限定内容（高频更新）应分组。

**误区三：混淆地址加载和直接引用**  
在 Inspector 中将资源直接拖拽赋值给脚本字段，会使该资源始终被包含在主包中，绕过 Addressables 系统。要使 Addressables 真正生效，脚本字段类型应使用 `AssetReference` 而非直接的 `GameObject` 或 `Texture2D` 引用。

---

## 知识关联

学习 Addressables 需要先理解 **Unity 引擎的 Inspector 与 Asset 序列化机制**（即 Unity引擎概述中的资源管理基础），因为 `AssetReference` 类型在 Inspector 中的工作方式与普通对象引用有本质区别。

掌握 Addressables 后，可以自然过渡到**资源管理概述**这一更宏观的主题：Addressables 解决了"如何加载单个资源"的问题，而资源管理概述则研究如何设计整个项目的资源生命周期策略，包括内存预算规划、资源预加载时机、以及多平台差异化打包方案。Addressables 的 Content Catalog 机制也是理解**远程配置与热更新架构**的技术前提。