---
id: "ta-mem-leak-detect"
concept: "内存泄漏检测"
domain: "technical-art"
subdomain: "memory-budget"
subdomain_name: "内存与预算"
difficulty: 3
is_milestone: false
tags: ["调试"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 内存泄漏检测

## 概述

内存泄漏（Memory Leak）是指程序在运行过程中动态分配的内存未能被正确释放，导致可用内存持续减少的现象。在游戏和实时渲染应用中，即便是每帧仅泄漏 1KB 的资源，经过 3600 帧（约 60 秒）后累积泄漏量也将达到 3.5MB，长时间运行后会引发显著的性能下降乃至崩溃。与内存池管理关注"分配策略"不同，内存泄漏检测专注于验证"已分配内存是否被归还"这一问题。

内存泄漏检测技术最早在 1990 年代随 C++ 程序的普及而系统化发展。1992 年发布的 Purify 工具首次将二进制插桩（Binary Instrumentation）技术应用于内存追踪，奠定了现代检测工具的基本原理。在技术美术工作流中，纹理、网格、渲染目标（Render Target）等 GPU 资源的泄漏尤其隐蔽，因为这些资源不由操作系统垃圾回收机制管理，必须依赖专门工具才能发现。

对于技术美术而言，内存泄漏检测是控制游戏内存预算的防线之一。一个未被发现的 512×512 RGBA 纹理泄漏（占用约 1MB VRAM）在加载卸载关卡时重复累积，会直接压缩给其他高优先级资源的预算空间。

## 核心原理

### 引用计数与标记清除

最基础的泄漏检测原理是**引用计数（Reference Counting）**：每个资源对象维护一个整数计数器，每次被引用时 +1，引用解除时 -1，计数归零时触发释放。泄漏检测即检查程序退出时或资源卸载后是否存在计数仍大于 0 的对象。Unreal Engine 的 `TSharedPtr<T>` 和 Unity 的 `UnityEngine.Object` 均基于类似机制。

**标记清除（Mark-and-Sweep）**则用于检测循环引用导致的泄漏：从根节点集合出发遍历所有可达对象并标记，扫描结束后未被标记的对象即为泄漏候选。Lua 脚本的垃圾回收器使用三色标记法（Tri-color Marking），在游戏逻辑脚本中可捕获由循环引用引发的 Lua 对象泄漏。

### 内存快照对比法

在游戏引擎语境下，最实用的泄漏检测方式是**前后快照对比（Snapshot Diffing）**：在某操作（如加载/卸载一个关卡）前后各采集一次内存分配快照，然后对比差集。差集中持续存在的分配记录即泄漏嫌疑项。

Unity Profiler 的 Memory 模块支持"Take Sample"功能，可对比两次快照中 `ManagedHeap`、`NativeAllocations` 和 `GraphicsDriver` 三个独立区域的变化。Unreal Engine 则通过控制台命令 `obj list` 配合 `memreport -full` 导出完整对象列表，操作前后的 diff 可精确定位未销毁的 UObject 实例。实际操作中建议将同一操作重复执行 5~10 次，排除缓存预热的干扰，只有每次循环都稳定增长的分配才是真正的泄漏。

### 地址消毒器与插桩工具

**AddressSanitizer（ASan）** 是由 Google 于 2011 年开源的运行时内存错误检测工具，通过编译时插桩（Compile-time Instrumentation）在每次内存访问前插入合法性检查代码。其典型开销约为原程序运行速度的 1.5~2 倍、内存占用增加约 3 倍，但可精确报告泄漏的分配调用栈（Allocation Callstack）。在 UE4/UE5 项目中，可通过编译选项 `-fsanitize=address` 启用 ASan，配合 LeakSanitizer（LSan）在程序退出时输出所有未释放块的详细信息。

**Valgrind** 的 Massif 工具则提供堆内存随时间变化的可视化曲线（Heap Profile），横轴为程序执行快照点，纵轴为字节数，峰值点周围的调用树往往揭示泄漏的根源函数。

### GPU 资源泄漏检测

GPU 端泄漏检测需要独立工具。**RenderDoc** 的 Resource Inspector 面板可列出当前帧所有存活的 D3D12/Vulkan 资源对象及其创建时的调用栈。**PIX for Windows** 的 GPU Captures 功能可对比两次捕获之间新增但未销毁的资源描述符（Resource Descriptor），常用于定位 RenderTexture 在相机切换后未调用 `Release()` 的问题。在 Unity 中，每个未手动释放的 `RenderTexture` 对象会在 Profiler 的 `RenderTexture.active` 路径下持续占用 VRAM，可通过帧调试器验证。

## 实际应用

**场景一：角色换装系统的纹理泄漏。** 一个换装系统在运行 50 次换装操作后报告 VRAM 占用从 800MB 攀升至 1.2GB。使用 Unity Memory Profiler 2.0 对比第 1 次和第 51 次换装前后的快照，发现 `NativeAllocations` 区域新增了 50 份 `Texture2D` 实例，定位到代码中 `AssetBundle.LoadAsset<Texture2D>()` 之后缺少对旧纹理调用 `Resources.UnloadAsset()` 的逻辑。修复后每次换装的净分配变化归零。

**场景二：关卡流送中的粒子系统泄漏。** 在 Unreal Engine 项目中，使用关卡流送（Level Streaming）反复加载卸载同一关卡，运行 `memreport -full` 10 次后对比报告，发现 `ParticleSystemComponent` 数量每轮增加 12 个。追踪至某个粒子蓝图在 `BeginDestroy` 事件中未正确注销计时器句柄，导致计时器持有对粒子组件的强引用，阻止 GC 回收。将计时器句柄改为弱引用后泄漏消除。

**场景三：材质实例的隐性泄漏。** 技术美术在运行时通过 `Material.SetFloat()` 创建动态材质实例，但在对象销毁时未调用 `Destroy(material)`。在 Profiler 中 `Material` 类的实例计数随游戏时长线性增长，使用 Memory Profiler 的 "Objects" 视图按类型过滤后一览无余，15 分钟游戏会话积累了 340 个孤立材质实例，占用约 27MB 托管内存。

## 常见误区

**误区一：对象被置为 null 就等于内存被释放。** 在 C# 和 Lua 中，将变量赋值为 `null` 或 `nil` 只是解除了该变量对对象的引用，对象本身是否被回收取决于是否还存在其他引用路径。事件委托（Event Delegate）是最常见的隐藏引用来源——若一个 MonoBehaviour 订阅了静态事件但在销毁时未取消订阅，垃圾回收器将无法回收该对象，但 Profiler 的托管堆快照会明确显示该对象仍然存活且被事件系统持有。

**误区二：依赖引擎自动 GC 可以完全规避泄漏。** Unity 的垃圾回收仅负责托管内存（Managed Heap），对 `Texture2D`、`RenderTexture`、`ComputeBuffer` 等 Native 资源无效。这些对象在托管侧的封装器（Wrapper）可能被 GC 回收，但底层 Native 分配在未显式调用 `Destroy()` 或 `Release()` 之前永远不会被释放，VRAM 的消耗会持续存在。这也是为什么 Memory Profiler 需要单独区分 `ManagedHeap` 和 `NativeAllocations` 两个数据视图。

**误区三：运行时无泄漏报告代表没有泄漏。** AddressSanitizer 和 Valgrind 的 LeakSanitizer 默认在程序正常退出时才输出泄漏报告，若程序因崩溃而中止则不会生成报告。此外，周期性但非单调递增的内存波动有时会掩盖缓慢泄漏，建议配合 **长时运行压测（Soak Test）**，将同一场景运行 30 分钟以上，在 Profiler 时间线上观察内存曲线是否具有上升趋势，斜率为正即可怀疑存在泄漏。

## 知识关联

内存泄漏检测建立在**内存池管理**的概念基础之上：当使用自定义内存池时，泄漏检测需同时追踪"从系统申请的总块数"与"归还给系统的总块数"，两者之差即为活跃分配数，若活跃分配数在操作前后不一致即为泄漏。内存池的分配/释放接口（如 `PoolAlloc()`/`PoolFree()`）是插桩检测的天然埋点，比追踪系统级 `malloc`/`free` 的颗粒度更粗但噪声更小。

在纹理流送（Texture Streaming）和资源热
