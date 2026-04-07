# Unity Profiler

## 概述

Unity Profiler 是 Unity 引擎内置的运行时性能分析工具，首次引入于 Unity 3.x 系列，并在 Unity 2020 LTS（版本 2020.3）中经历重大架构重构——原有的单体式 Profiler 窗口被拆解为模块化面板体系（Profiler Modules），同时 Memory Profiler 被独立为 com.unity.memoryprofiler 扩展包（版本 1.0.0 于 2022 年正式发布）。Unity Profiler 的根本工作原理是**低侵入式采样**：引擎在每个采样点记录当前调用栈快照，而非对每条指令计时，这使得它能在不显著改变程序行为的前提下捕获帧内各系统的时间消耗分布。

Profiler 通过菜单 **Window → Analysis → Profiler**（快捷键 `Ctrl+7`）打开。连接真机时需在 Build Settings 中同时勾选 **Development Build** 与 **Autoconnect Profiler**，或在 Profiler 窗口的目标设备下拉列表中输入设备 IP（端口默认 54998–55511 范围内动态分配）。Editor 内录制与设备录制存在本质差异：Editor 录制时引擎本身的编辑器开销会混入数据，因此对于移动端性能评估，必须使用真机 Development Build 数据而非依赖 Editor 内的帧时间。

---

## 核心原理

### CPU Profiler 的采样机制与线程模型

CPU Profiler 默认以**instrumentation 注入**方式工作（区别于统计采样），Unity 引擎源码中预先插入了大量 `Profiler.BeginSample()` / `Profiler.EndSample()` 标记，记录每段代码区间的精确开始与结束时刻。Timeline 视图横轴为绝对时间（毫秒），纵轴按线程展开：**Main Thread** 负责脚本逻辑与引擎更新，**Render Thread** 负责向图形 API 提交命令，**Worker Thread（0~N）** 由 Unity Job System 调度，**Loading Thread** 专用于异步资源加载。

Hierarchy 视图中每个采样条目包含五列关键指标：

| 列名 | 含义 |
|------|------|
| Total % | 该函数及所有子调用占本帧 Main Thread 总耗时的百分比 |
| Self % | 仅函数自身逻辑（剔除子调用）的耗时占比 |
| Calls | 本帧内该函数被调用的次数 |
| GC Alloc | 本帧内该函数触发的托管堆分配字节数 |
| Time ms | 绝对毫秒数（含子调用） |

**GC Alloc 列是移动端优化最高优先级指标之一**。C# 运行时使用 Boehm GC（Unity 2019 之前）或 il2cpp 配合增量 GC（Unity 2019.1 引入，可在 Player Settings → Use incremental GC 开启）进行垃圾回收。当单帧 GC Alloc 超过托管堆阈值时，GC 会触发 Stop-The-World 暂停，在低端 Android 设备上可导致 10–40ms 的帧刺（spike）。通过 Profiler 的 **GC.Collect** 标记可精确定位触发帧。

### GPU Profiler 与渲染管线分析

GPU Profiler 依赖平台底层的 Timer Query 接口：在 PC DirectX 11/12 上使用 `D3D11_QUERY_TIMESTAMP`，在 Metal 上使用 `MTLCommandBuffer` 的 `GPUStartTime`/`GPUEndTime`，在 Vulkan 上使用 `vkCmdWriteTimestamp`。并非所有移动 GPU 都完整支持这些接口——Mali GPU 在 OpenGL ES 模式下通常无法返回 GPU 时间，需切换至 Vulkan 或使用 ARM Mobile Studio / Snapdragon Profiler 等厂商工具补充。

GPU Profiler 将渲染时间拆解为以下典型阶段（以 Universal Render Pipeline 为例）：
- **Opaque Pass**：不透明物体几何渲染，通常是 Draw Call 数量最多的阶段
- **Shadow Pass**：阴影贴图渲染，级联阴影（CSM）配置不当时会在此阶段出现显著超时
- **Transparent Pass**：透明物体渲染，Over-draw 问题集中暴露区域
- **Post Processing**：后期处理效果，Bloom 的高斯模糊卷积在低端 GPU 上开销极大

### 内存分析的三层模型

Unity 内存体系分为三层，Profiler 对应三个不同工具：

1. **托管堆（Managed Heap）**：C# 对象分配，由 CPU Profiler 的 GC Alloc 列跟踪，总量可在 Memory Profiler 模块中查看 **Used Total** 下的 **Mono** 行。
2. **本机堆（Native Heap）**：Unity 引擎内部的 C++ 对象（纹理、网格、音频缓冲区），在 Memory Profiler Package 的 **Objects** 视图中可按类型排序，识别最大占用者。
3. **图形内存（GPU Memory）**：纹理与渲染目标在 VRAM 中的占用，通过 Memory Profiler 的 **Graphics** 分类展示，需特别关注未压缩纹理（RGBA32 格式 1024×1024 = 4MB）与 ETC2/ASTC 压缩纹理之间的差异。

---

## 关键方法与公式

### 帧率目标与帧时间预算

帧率目标 $f$（fps）对应的帧时间预算 $T$（ms）为：

$$T = \frac{1000}{f}$$

60fps 目标对应 $T = 16.67\text{ ms}$，30fps 对应 $T = 33.33\text{ ms}$。在移动端，CPU 帧时间与 GPU 帧时间的总和受限于 $T$，但两者并非串行关系——CPU 和 GPU 通常流水线并行执行，实际瓶颈取决于哪侧先超出预算。通过 Profiler 的 **Gfx.WaitForPresentOnGfxThread** 标记（CPU 等待 GPU 完成）可判断当前是 **GPU Bound** 还是 **CPU Bound**：若该标记耗时占主线程 30% 以上，则为 GPU 瓶颈。

### 自定义 Profiler 标记的正确用法

在业务代码中插入自定义采样点使用以下 API（Unity 2018.1 引入的非托管版本，不产生 GC 分配）：

```csharp
using Unity.Profiling;

static readonly ProfilerMarker s_MarkerAI = new ProfilerMarker("AI.PathFinding");

void UpdateAI()
{
    using (s_MarkerAI.Auto())
    {
        // 寻路计算逻辑
    }
}
```

相比旧版 `Profiler.BeginSample(string)` API，`ProfilerMarker` 使用 `ProfilerMarker.Auto()` 返回的 `struct`（值类型）不分配堆内存，且支持在 Burst Job 中使用——这是 Unity 官方文档（Unity Technologies, 2021, *ProfilerMarker API Reference*）明确标注的性能差异点。

### Memory Profiler 快照比对

Memory Profiler Package 支持拍摄两帧快照（Snapshot）并进行 **Diff** 比对，找出两个时间点之间新增的对象类型和数量。其计算逻辑为：

$$\Delta_{\text{objects}} = \text{Snapshot}_B - \text{Snapshot}_A$$

例如在关卡加载前后各拍摄一次快照，若 Diff 视图中 `Texture2D` 条目显示 `+45`，则表明加载过程中有 45 张纹理被创建但尚未释放，可据此排查资源泄漏。

---

## 实际应用案例

### 案例一：定位移动端 GC Spike

某款 Unity 2021.3 手机游戏在战斗中出现周期性卡顿，每隔约 15 秒出现约 30ms 的帧刺。开发者使用 Profiler 录制真机数据后，在 CPU Timeline 中找到 **GC.Collect** 调用，通过上层调用栈追溯到 `EnemyManager.Update()` 中每帧调用 `FindObjectsOfType<Enemy>()` 所致——该 API 每次调用都返回新数组，产生约 2KB GC Alloc/帧，15 秒内累积触发 GC 阈值。解决方案：改用预先缓存的 `List<Enemy>` 并在敌人生成/销毁时手动维护，GC Alloc 降至零，帧刺消失。

### 案例二：SRP Batcher 与 GPU 性能

某开放世界场景在 URP 下 GPU 耗时达 22ms（目标 16.67ms）。Frame Debugger 显示共有 1200+ Draw Calls，但 Profiler 的 **SRP Batch** 计数器仅有 80 次批合并。检查发现场景中约 60% 的材质使用了包含 `[MaterialProperty]` 覆写的非标准 Shader，这些 Shader 不兼容 SRP Batcher。将 Shader 改造为 SRP Batcher 兼容格式（所有每物体属性放入 `UnityPerMaterial` CBUFFER）后，Draw Call 等效量降至 350，GPU 帧时间降为 14.2ms（Unity Technologies, 2022, *Universal Render Pipeline Performance Guide*）。

### 案例三：使用 Profiler Recorder API 进行自动化性能回归测试

Unity 2020.2 引入了 `ProfilerRecorder` API，允许在运行时以代码方式读取 Profiler 计数器数值，无需打开 Profiler 窗口：

```csharp
using Unity.Profiling;

ProfilerRecorder mainThreadTimeRecorder;

void OnEnable()
{
    mainThreadTimeRecorder = ProfilerRecorder.StartNew(
        ProfilerCategory.Internal, "Main Thread", 15);
}

void OnDisable() => mainThreadTimeRecorder.Dispose();

double GetAverageFrameTimeMs()
{
    double sum = 0;
    for (int i = 0; i < mainThreadTimeRecorder.Count; i++)
        sum += mainThreadTimeRecorder.GetSample(i).Value;
    return (sum / mainThreadTimeRecorder.Count) * 1e-6; // 纳秒转毫秒
}
```

该 API 可集成到自动化测试框架（如 Unity Test Framework）中，在每次 CI 构建后自动断言帧时间不超过预设阈值，实现性能回归检测。

---

## 常见误区

### 误区一：Editor 内的 Profiler 数据等同于真机性能

Editor 内录制时，Unity Editor 本身的渲染（Scene 视图、Inspector 刷新）会消耗额外 CPU 时间，并且 Editor 运行在 JIT 模式（IL2CPP 与 Mono JIT 的性能差异可达 2–5 倍）。移动端真机通常使用 IL2CPP 编译，其 C++ 编译优化可显著提升脚本性能但不改变 GC 模式。因此 Editor 内的帧时间数据只适合相对比较（改动前后对比），不能作为目标平台绝对性能的参考。

### 误区二：GC Alloc 为零即代表无内存问题

GC Alloc 为零仅表明**托管堆**在本帧没有新的 C# 对象分配，但**本机堆泄漏**（Native Leak）不会反映在此列中。例如，每帧调用 `Resources.Load()` 而不配合 `Resources.UnloadUnusedAssets()` 会导致本机堆中纹理和网格持续累积，Profiler 的 GC Alloc 列为零，但 Memory Profiler 的 **Native Objects** 计数会持续增长，最终触发 OOM（Out of Memory）崩溃——这在 iOS 设备上因系统无交换分区而尤为危险。

### 误区三：Deep Profile 模式是日常分析的标准选项

Deep Profile 模式通过在**所有** C# 函数入口和出口插入钩子，提供完整调用栈，但这会引入约 10–20 倍的额外运行时开销，导致帧时间严重失真。Deep Profile 仅适合在已确定某个大类（如"AI 系统"）存在瓶颈后，进一步精确定位具体函数时短暂启用。日常性能监控应使用普通采样模式配合 `ProfilerMarker` 手动标记关键路径。

### 误区四：忽视 Render Thread 与 Main Thread 的通信开销

许多开发者聚焦 Main Thread 耗时，却忽视 **Gfx.WaitForPresentOnGfxThread** 与 **Gfx.WaitForGfxCommandsFromMainThread** 这两个跨线程同步标记。前者表示 Main Thread 在等待 GPU Present，后者表示 Render Thread 在等待 Main Thread