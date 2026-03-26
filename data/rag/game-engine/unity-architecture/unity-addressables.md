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

Unity Addressables 是 Unity 于 2019 年正式发布的资产管理系统（包名 `com.unity.addressables`，随 Unity 2019.3 进入正式版），它用一套统一的"地址"（Address）字符串替代了传统的直接引用和 `Resources.Load` 路径，使开发者无需关心资产的实际物理存储位置即可异步加载任意资产。这套系统建立在 `AssetBundle` 的基础之上，但把打包、依赖管理、运行时加载等繁琐操作全部封装起来，极大降低了大型项目的资产管理复杂度。

历史上，Unity 开发者有两条路：把资产放进 `Resources` 文件夹（简单但导致包体臃肿、无法热更新）或手动管理 `AssetBundle`（灵活但依赖关系极难维护）。Addressables 正是为了填补这两条路之间的鸿沟而设计的，它在幕后自动生成并维护 AssetBundle，开发者只需通过 `AssetReference` 或字符串地址访问资产。

Addressables 在移动游戏和需要热更新的项目中尤为重要：资产可以分组托管在远程 CDN 上，客户端首次启动时只下载核心包，其余内容按需拉取，能将初始包体压缩 30%～60%。同时，异步加载 API 避免了大资产在主线程阻塞造成的卡顿，这对 60 FPS 的流畅体验至关重要。

## 核心原理

### 地址（Address）与标签（Label）

每个被标记为 Addressable 的资产都会获得一个唯一的字符串地址，例如 `"UI/MainMenuBackground"`。运行时调用 `Addressables.LoadAssetAsync<Sprite>("UI/MainMenuBackground")` 即可异步加载该精灵。地址可以手动指定，也可默认使用资产的 GUID 或相对路径。

标签（Label）则允许一次性操作一组资产：给所有主城场景资产打上 `"Zone_City"` 标签，调用 `Addressables.LoadAssetsAsync<GameObject>("Zone_City", callback)` 即可批量加载。标签与地址可同时作为查询键，系统内部通过哈希表实现 O(1) 的键查找。

### 组（Group）与打包策略

Addressables 以"组（Group）"为单位管理资产，每个组对应一个或多个 AssetBundle。每个组有两个关键设置：**Build Path**（构建输出路径，可指向本地或远程 URL）和 **Load Path**（运行时加载路径，支持 `{UnityEngine.AddressableAssets.Addressables.RuntimePath}` 等变量）。

内置的打包策略有三种：**Pack Together**（整组打成一个 Bundle）、**Pack Separately**（每个资产独立成 Bundle）和 **Pack Together By Label**（按标签分 Bundle）。Pack Separately 会导致 Bundle 数量爆炸（影响 HTTP 请求并发数），而 Pack Together 则会导致细微改动就使整个 Bundle 失效，实际项目中通常按功能模块选择 Pack Together By Label。

### 异步加载与引用计数

Addressables 的所有加载操作均返回 `AsyncOperationHandle<T>`，可通过 `handle.Task`（.NET Task）或在协程中 `yield return handle` 两种方式等待完成。加载完成后通过 `handle.Result` 获取资产对象。

系统内部维护一套引用计数机制：每次 `LoadAssetAsync` 使引用计数 +1，必须调用对应的 `Addressables.Release(handle)` 或 `Addressables.ReleaseInstance(gameObject)` 使计数 -1，当计数归零时 Bundle 才会从内存卸载。忘记 Release 是 Addressables 内存泄漏的最主要原因。关键公式如下：

```
内存驻留条件：引用计数(Bundle) > 0
卸载触发条件：引用计数(Bundle) == 0 且 UnloadUnusedAssets 被调用
```

### 内容更新流程（Remote Content Update）

远程内容更新依赖两个 Catalog 文件：**本地 Catalog**（随包体发布）和**远程 Catalog**（托管在服务器，包含最新资产地址映射）。运行时 `Addressables.InitializeAsync()` 会先检查远程 Catalog URL（在 AddressableAssetSettings 中配置），若远程版本更新则下载新 Catalog，后续加载请求自动重定向到 CDN 上的新 Bundle，无需重新提交应用商店审核。

## 实际应用

**角色皮肤的按需加载**：将所有角色皮肤归入 `"Skins"` 组并设置为远程加载。玩家购买皮肤后，客户端调用 `Addressables.LoadAssetAsync<Material>("Skin_KnightGold")`，首次调用自动从 CDN 下载对应 Bundle（约 2-5 MB），后续调用命中本地缓存（位于 `Application.persistentDataPath/com.unity.addressables` 目录下）。

**场景的异步加载**：Addressables 支持直接加载场景，`Addressables.LoadSceneAsync("Scenes/BossRoom", LoadSceneMode.Additive)` 以叠加模式异步加载关卡场景，返回的 `AsyncOperationHandle<SceneInstance>` 在卸载时调用 `Addressables.UnloadSceneAsync(handle)` 即可，系统自动处理依赖 Bundle 的卸载。

**预加载与进度显示**：在加载界面期间调用 `Addressables.DownloadDependenciesAsync("Zone_Forest")` 预先下载某关卡的所有依赖 Bundle，通过 `handle.GetDownloadStatus()` 获取 `DownloadStatus.Percent` 字段（0.0 ～ 1.0）驱动进度条 UI。

## 常见误区

**误区一：地址字符串可以随意修改**。地址字符串一旦在代码或配置文件中被引用，修改它会导致运行时 `InvalidKeyException`，且编译期不会有任何报错。推荐使用 `AssetReference` 拖拽引用（Inspector 序列化）代替硬编码字符串，或者维护一个静态常量类统一管理所有地址字符串。

**误区二：Release 一次就能立即释放内存**。调用 `Addressables.Release` 仅使引用计数减一，若同一 Bundle 内的其他资产仍被持有，Bundle 不会卸载。而且 Unity 的资产卸载依赖 GC 和 `Resources.UnloadUnusedAssets`，Release 后内存可能不会立即下降，这不代表泄漏，需通过 Memory Profiler 包确认引用计数真正归零后再做判断。

**误区三：Addressables 与 Resources 可以混用且无性能差异**。`Resources.Load` 是同步阻塞调用，而 Addressables 是异步的，混用会导致代码架构撕裂（同步/异步边界难以处理）。此外，`Resources` 文件夹内的资产即便未被引用也会被打入包体，而 Addressables 按组独立打包，按需分发，两者的包体管理逻辑根本不同，不能视为等价替代。

## 知识关联

学习 Addressables 前需掌握 **Unity 引擎的基础资产系统**——了解什么是 AssetBundle、Prefab、Scene Asset，以及 Unity 编辑器中 Inspector 与 Project 窗口的基本操作；否则"组打包策略"和"Bundle 依赖"将难以理解。

Addressables 之后自然延伸到**资源管理概述**这一更宏观的话题：如何设计整个项目的资产分组策略、如何搭建 CDN 热更新管线、如何在多平台（iOS/Android/PC）之间切换加载路径，以及如何结合 Addressables Profiler（Unity 2022 起内置）分析运行时 Bundle 占用情况。此外，Addressables 的异步加载模式也为后续学习 Unity Job System 和异步场景管理打下实践基础——两者都依赖 `AsyncOperation` 和 C# `async/await` 的配合使用。