# 游戏项目审查重点

## 概述

游戏项目代码审查与通用软件审查存在根本性的性能约束差异：游戏主循环必须在固定时间窗口内完成所有逻辑处理，60帧/秒对应每帧预算为 $T_{frame} = \frac{1000ms}{60} \approx 16.67ms$，30帧/秒对应 $T_{frame} \approx 33.3ms$。这意味着任何一段新增代码若引入超过1ms的帧时间开销，就可能在性能敏感平台（如Nintendo Switch或中端Android设备）上直接导致丢帧（Frame Drop），产生玩家肉眼可见的画面撕裂或卡顿。

游戏项目代码审查必须聚焦三个高度相关的维度：**资源引用正确性**（防止意外内存常驻）、**内存预算合规性**（防止OOM崩溃）、**帧率影响量化**（防止逐帧性能退化）。这三个维度相互耦合——一次错误的强引用既造成资源泄漏（内存维度），又因垃圾回收或显存置换触发帧时间尖峰（帧率维度）。

该方法论的系统化工作可追溯至 Greg Costikyan 等人对游戏工程质量的早期讨论，但真正形成可操作的检查标准，是随着 Unity（2005年首发）和 Unreal Engine 4（2014年源码开放）的普及而逐步完善的。Rich Geldreich 在2012年发表的《Lessons Learned from the Trenches》（GDC 2012）中明确指出，现代游戏 AAA 项目中约35%的性能回归根源于代码审查阶段未拦截的资源引用错误（Geldreich, 2012）。

---

## 核心原理

### 资源引用检查的底层逻辑

审查者需要理解引擎的**对象生命周期模型**才能识别危险引用模式。在 Unity 中，资源可以通过三种方式被引用，其内存语义完全不同：

1. **强引用（Serialized Field）**：`public Texture2D myTex` 或 `[SerializeField] private AudioClip clip`。被 Inspector 序列化的引用会在场景加载时将目标资源强制加载到内存，且只要持有该 Component 的 GameObject 存在，资源就不会被 `Resources.UnloadUnusedAssets()` 回收。审查时凡见到 MonoBehaviour 字段直接引用超过 512KB 的纹理、音频或 Mesh，必须要求提交者说明该资源的预期驻留时长，若非全程常驻则强制改用 Addressables 异步加载。

2. **Addressables 弱引用**：`AssetReference` 持有资源的 GUID 而非实例，只有显式调用 `Addressables.LoadAssetAsync<T>()` 时才触发加载，并需要配对的 `Addressables.Release(handle)` 释放。审查重点在于检查是否存在**Handle 泄漏**——即调用加载但从未释放的代码路径，尤其在异常流程（catch block 或提前 return）中容易遗漏释放。

3. **Resources 文件夹引用**：`Resources.Load<T>()` 加载的资源在 `Resources.UnloadUnusedAssets()` 调用前不会释放，而该调用本身会触发全量扫描，在含有 5000+ 对象的场景中耗时可达 80ms～200ms，足以造成明显的帧率卡顿。审查策略是：新增的 `Resources.Load` 调用必须说明对应的卸载时机，且禁止在 Update 或帧循环内调用。

在 Unreal Engine 项目中，审查者必须区分以下三种指针语义：
- `UPROPERTY() UTexture2D* tex`：受 UObject GC 系统追踪，安全；
- `UTexture2D* tex`（无 UPROPERTY）：可能被 GC 提前回收，导致悬空指针崩溃；
- `TWeakObjectPtr<UTexture2D> tex`：弱引用，不阻止 GC，需在使用前调用 `.IsValid()`。

凡发现新增的 `UObject` 派生类成员变量缺少 `UPROPERTY` 宏标注，即为必须拦截的高危错误。

### 内存预算合规性的量化标准

每款游戏应在技术设计文档（TDD）中设定平台内存预算。典型数据如下：

| 平台 | 总内存预算 | 纹理预算 | 音频预算 | 代码+堆 |
|------|-----------|---------|---------|--------|
| iOS（iPhone 11） | 300MB | 120MB | 30MB | 150MB |
| Android 中端 | 350MB | 140MB | 35MB | 175MB |
| Nintendo Switch | 3.2GB（主机模式） | 1.2GB | 200MB | 1.8GB |
| PS5 | 13.5GB | 6GB | 512MB | 6.9GB |

代码审查阶段的内存合规检查核心是纹理格式验证。未压缩 RGBA32 纹理的内存占用公式为：

$$M_{uncompressed} = W \times H \times 4 \text{ bytes}$$

以 2048×2048 纹理为例，$M_{uncompressed} = 2048 \times 2048 \times 4 = 16MB$。采用 ASTC 6×6 格式压缩后，每像素约 0.89 字节，压缩后约 1.78MB，压缩比达到 **9:1**。审查时若发现纹理导入设置中 iOS 平台的 Format 字段不是 ASTC，Android 平台不是 ETC2/ASTC，即为必须退回修改的错误——此类纹理格式错误一旦进入主干，在集成测试阶段会导致 iOS OOM Crash（`EXC_RESOURCE RESOURCE_TYPE_MEMORY`）。

审查者还需检查 **Mipmap 配置**：UI 纹理（RenderTexture 或 UI Atlas）应禁用 Mipmap（`generateMipMaps = false`），因为 UI 元素不存在 LOD 距离，强制生成 Mipmap 会额外消耗 $M_{mip} = M_{base} \times \frac{1}{3}$ 的额外内存（等比级数求和），对 128×128 的 UI 图标而言增量微小，但对 2048×2048 的场景 UI 背景图，将额外浪费约5.3MB。

---

## 关键检查清单与公式

### 帧率影响的量化评估方法

审查者判断一段逻辑是否"帧率安全"，需要基于 Big-O 分析和 Profiler 实测数据双重验证。

**Update 函数复杂度规则**：若某个 MonoBehaviour 的 Update 被 $N$ 个 GameObject 实例化（如敌人、粒子、NPC），则该 Update 的时间复杂度必须为 $O(1)$ 而非 $O(N)$ 或更高。若审查发现 Update 内存在 `FindObjectsOfType<T>()` 调用（该函数遍历全场景对象，时间复杂度 $O(n)$），或 `GetComponent<T>()` 调用（应缓存而非每帧查询），则必须要求修改。

**帧时间预算分配原则**（来自 Unity Technologies 官方性能指南，2021）：在 16.67ms 总预算中，典型分配为：
- CPU 游戏逻辑：约 3ms
- CPU 渲染准备（Culling + DrawCall 生成）：约 4ms  
- GPU 渲染：约 7ms
- 引擎开销 + 平台 OS：约 2.67ms

代码审查应要求新增的复杂逻辑系统（如寻路、AI 决策树、物理查询）提交 Unity Profiler 或 Unreal Insights 的截图，证明在目标平台上该逻辑的 CPU 耗时不超过分配预算。

**Draw Call 增量检查**：每个新增的渲染对象（Renderer 组件）若使用独立材质（Material 实例），将产生额外的 Draw Call。移动平台的 Draw Call 上限经验值约为 100～200 次/帧（超出后 GPU 驱动开销显著上升）。审查时需确认新增的渲染对象是否已启用 GPU Instancing（`material.enableInstancing = true`）或加入 Static Batching（对静态场景对象），否则 100 个相同外观的敌人会产生 100 个 Draw Call 而非 1 个。

---

## 实际应用

### 案例：移动游戏 Boss 关卡资源审查

某移动 RPG 团队在 PR #4821 中提交了 Boss 战关卡的代码，审查者发现以下问题：

**问题一：强引用导致 Boss 纹理在整个游戏生命周期内常驻**
```csharp
// 错误写法（审查应拦截）
public class BossController : MonoBehaviour {
    public Texture2D bossIdleTexture; // 4096x4096 RGBA32 = 64MB，全程常驻
}

// 正确写法（审查应要求改为）
public class BossController : MonoBehaviour {
    [SerializeField] private AssetReference bossTextureRef;
    private AsyncOperationHandle<Texture2D> _handle;
    
    async void OnBossEnterBattle() {
        _handle = bossTextureRef.LoadAssetAsync<Texture2D>();
        await _handle.Task;
    }
    
    void OnBossDefeated() {
        Addressables.Release(_handle); // 显式释放，GC 可回收
    }
}
```

**问题二：帧循环内的物理查询未批处理**

提交代码在 Update 中对 50 个敌人分别调用 `Physics.OverlapSphere()`，产生 50 次独立物理查询。审查建议改用 `Physics.OverlapSphereNonAlloc()` 并复用预分配数组，消除每帧约 50 次 GC Alloc，将该逻辑帧耗时从 2.3ms 降至 0.4ms（实测数据来自该项目 Profiler 记录）。

**问题三：音频片段格式错误**

新增 Boss 战 BGM（`boss_battle.mp3`，时长 3分42秒）的 Unity 导入设置为 `Decompress On Load`，这意味着 3.7MB 的压缩 MP3 在加载时会被解压为 PCM 格式驻留内存，实际占用约 38MB。审查应要求改为 `Compressed In Memory` + `Vorbis` 格式，运行时内存占用压缩至约 4MB（Geig & Creighton, 2013）。

---

## 常见误区

**误区一："游戏逻辑正确就可以合并，性能问题留到优化阶段再统一处理"**

这是游戏项目最致命的审查认知误区。性能问题具有**累积性**——100 个各自看似无害的 Update 函数，叠加后可能占用 8ms 的帧时间，超出逻辑预算的2.6倍。等到优化阶段才处理，面对数千次提交记录追溯回归源头的成本是审查阶段的20～50倍。Unity Technologies 的工程师 Valentin Simonov 在2019年的 Unite Berlin 演讲中引用内部数据：在 Unity 移动游戏项目中，80%的性能问题可在代码审查阶段通过规则检查拦截，但若推迟到 QA 阶段才发现，修复成本平均增加 4.7 倍（Simonov, 2019）。

**误区二："Addressables 系统自动管理内存，不需要审查手动释放逻辑"**

Addressables 的引用计数（Reference Count）机制要求每次 `LoadAssetAsync` 必须有对应的 `Release` 调用，两者必须严格配对。若同一资源被加载2次但只释放1次，引用计数为1，资源不会被卸载，形成内存泄漏。审查者应使用 Addressables Event Viewer 工具截图验证 PR 中新增的加载路径均有对应释放路径，包括 `OnDestroy`、异常分支和场景切换流程。

**误区三："纹理格式只影响磁盘大小，不影响运行时内存"**

导入格式直接决定 GPU 显存（VRAM）占用，而非仅影响安装包体积。ASTC 格式纹理在 GPU 中以压缩态存储和采样，不需要解压为 RGBA32 才能被 Shader 读取（GPU 硬件原生支持 ASTC 解码）。而 RGBA32 纹理无论磁盘压缩多优秀，在 GPU 中始终以原始像素尺寸 $W \times H \times 4$ 字节占用显存。混淆这一点会导致审查者错误判断纹理的内存影响。

**误区四："内存预算检查是