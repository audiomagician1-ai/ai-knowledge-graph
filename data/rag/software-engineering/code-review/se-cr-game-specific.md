---
id: "se-cr-game-specific"
concept: "游戏项目审查重点"
domain: "software-engineering"
subdomain: "code-review"
subdomain_name: "代码审查"
difficulty: 3
is_milestone: false
tags: ["游戏"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.536
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 游戏项目审查重点

## 概述

游戏项目代码审查不同于普通软件的审查，需要专门关注三类核心指标：资源引用完整性、内存预算合规性，以及每帧执行开销对帧率的影响。这三类指标直接决定游戏能否稳定运行在目标帧率（通常为30fps或60fps），而传统软件审查关注的可维护性、接口设计等维度在游戏项目中必须让步于性能硬约束。

游戏审查规范在2000年代初随着主机游戏开发的工业化而形成体系。索尼、微软等平台商制定了"技术认证要求"（Technical Certification Requirements, TCR/TRC），其中明确规定：游戏提交前必须通过内存泄漏测试、帧率稳定性测试，这些外部约束倒逼团队将性能相关检查纳入日常代码审查流程。

游戏中一帧的预算时间极为有限：60fps对应约16.67毫秒/帧，30fps对应约33.33毫秒/帧。一段未经审查的粗糙代码——例如在Update循环中执行`GameObject.FindWithTag()`搜索全场景对象——可能单独消耗0.5毫秒以上，在复杂场景中叠加多处此类调用便足以导致帧率跌破阈值。因此，游戏代码审查员需要具备"以毫秒计的成本意识"。

---

## 核心原理

### 资源引用检查

资源引用检查的核心目标是防止以下两种缺陷：**野引用（悬空引用）**和**隐式同步加载**。

野引用指代码持有一个已被销毁或从未赋值的对象引用。在Unity引擎中，被销毁的`GameObject`在C#层并不变为`null`，而是变成一个重写了`==`运算符的"假null"对象。审查员必须识别如下模式：

```csharp
// 危险：enemy被Destroy后，此处不会触发NullReferenceException
// 但访问enemy.transform会报错
if (enemy != null) { enemy.transform.position = ...; }
```

正确做法是使用`enemy == null`前显式调用`ReferenceEquals`，或改用弱引用模式。

隐式同步加载是另一类高频缺陷。`Resources.Load<T>()`在主线程同步执行，加载一张2048×2048的压缩纹理可能阻塞主线程长达数十毫秒。审查时需确保所有非预加载资源均通过`Addressables.LoadAssetAsync()`或等效异步API加载，绝不允许在GamePlay逻辑路径中出现同步加载调用。

### 内存预算审查

移动平台游戏的可用RAM通常限定在1.5GB到2GB之间（以2023年主流Android中端机为参考基线），主机平台（如PS5）则有约13.5GB可用于游戏逻辑。审查员需要对照项目的**内存预算表**逐模块检查代码中的内存申请行为。

关键审查点包括：

1. **纹理格式合规**：移动端必须使用ASTC或ETC2格式，禁止使用未压缩RGBA32格式。一张1024×1024的RGBA32纹理占用4MB，而同等ASTC 6×6格式仅占约0.37MB——差距超过10倍。审查员看到`TextureFormat.RGBA32`或`TextureFormat.ARGB32`的硬编码应立即标记。

2. **对象池缺失**：频繁实例化和销毁GameObject会触发GC（垃圾回收）。Unity的GC会造成"GC刺峰"，在GC执行时可能占用5-10毫秒甚至更长，导致单帧超时。代码审查中，凡在循环或高频回调中出现`new`关键字创建引用类型、`Instantiate()`调用，均需确认是否有配套的对象池实现。

3. **音频内存开销**：`AudioClip`的`LoadType`设置错误是常见遗漏。超过5秒的背景音乐必须设置为`Streaming`而非`DecompressOnLoad`，否则会将整段PCM数据常驻内存。

### 帧率影响检查

帧率审查针对的是**热路径**（Hot Path）中的高成本操作，即每帧或每几帧必然执行的代码路径。

**Update方法审查规则**：任何在`Update()`、`FixedUpdate()`或`LateUpdate()`中调用的代码均属热路径。以下操作在热路径中应被标记为需审查项：

- 字符串拼接（触发堆内存分配）：`"Score: " + score.ToString()` 每帧生成新字符串对象
- LINQ查询：`enemies.Where(e => e.IsAlive).ToList()` 每帧创建新List
- 物理射线检测未限频：`Physics.RaycastAll()`在复杂场景每次调用可达0.1-0.3ms，若每帧调用多次且不做结果缓存，累计开销显著

**Draw Call与Overdraw审查**：渲染提交方面，审查员需检查动态合批条件是否被无意破坏。例如，不同`Material`实例（即便参数相同）会阻止合批，代码中`new Material(sharedMaterial)`的调用应被标记，建议改用`MaterialPropertyBlock`。

---

## 实际应用

**场景一：角色技能系统审查**
审查一个技能释放模块时，发现技能特效通过`Resources.Load()`在按键响应中同步加载。该调用会在技能触发瞬间阻塞主线程，造成可感知的卡顿。审查意见：将特效资源在关卡加载阶段通过Addressables预加载，技能触发时直接从缓存池取用实例。

**场景二：UI系统内存审查**
UI模块每次打开二级菜单时调用`Instantiate()`创建面板，关闭时`Destroy()`销毁。对照内存预算表，该操作在低端设备上每次触发约0.8MB的内存波动，并在3-5次操作后引发一次GC。审查意见：改为UI对象池，打开时`SetActive(true)`，关闭时`SetActive(false)`。

**场景三：寻路逻辑帧率审查**
AI寻路在每个敌人的`Update()`中调用`NavMesh.CalculatePath()`。10个敌人同时寻路时，该调用合计耗时约2.1ms/帧，占60fps帧预算的12.6%。审查意见：改用分帧分批计算，每帧至多为2个AI更新路径，其余AI使用上一帧缓存结果。

---

## 常见误区

**误区一：认为"能运行"等同于"通过审查"**
许多开发者在高端开发机上测试无问题便认为代码合格。但游戏需要在目标最低规格设备上达标。审查员必须以**目标最低规格设备的内存和CPU限制**作为评判基准，而非以开发机为准。一台搭载Intel i9和32GB内存的PC掩盖了大量移动端或主机端的性能问题。

**误区二：纹理压缩格式是"美术问题"而非"代码审查问题"**
代码中经常出现通过脚本动态创建纹理或修改纹理格式的逻辑（如`texture.format = TextureFormat.RGBA32`），这属于代码审查必须捕捉的问题。格式设置权不仅属于美术流程，运行时代码同样可以错误地修改格式，导致内存超预算。

**误区三：只审查C#/C++代码，忽略Shader代码的帧率影响**
自定义Shader中的过度复杂分支、过多采样次数同样是帧率杀手。一个在Fragment Shader中执行8次纹理采样加全屏后处理的效果，在移动GPU上可能独自消耗帧预算的40%以上。完整的游戏项目审查必须将Shader代码纳入帧率影响检查范围。

---

## 知识关联

游戏项目审查重点建立在对目标平台硬件规格的理解之上——不了解PS5有16GB GDDR6、Switch仅有4GB RAM，就无法判断某段代码的内存申请是否合规。与此同时，本文所述的三类检查点（资源引用、内存预算、帧率）也是性能分析工具（Profiler）输出报告的直接对应维度：Unity Profiler的Memory模块对应内存预算审查，CPU Usage模块中的PlayerLoop条目对应帧率影响审查，而资源引用问题则需结合Asset Bundle依赖图分析工具（如AssetGraph）辅助识别。掌握这些审查重点后，团队可将其结构化为**代码审查清单**，在Pull Request模板中强制要求提交者自查这三个维度，从而将性能问题拦截在合并阶段之前。