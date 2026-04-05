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
updated_at: 2026-03-27
---


# 游戏项目代码审查重点

## 概述

游戏项目代码审查与普通软件审查的本质区别在于：游戏需要以稳定的16.67ms（60帧/秒）或33.3ms（30帧/秒）完成每一帧的计算、渲染、物理模拟和脚本逻辑，任何单次审查疏漏导致的性能退化都可能引发玩家可感知的画面卡顿。因此，游戏项目的代码审查必须同时关注三个相互关联的维度：资源引用正确性、内存预算合规性、以及对帧率的影响程度。

该审查方法论在2000年代初随着主机游戏开发规模扩大而系统化，Unity和Unreal引擎社区分别将其提炼为可检查清单。Unity的Profiler工具和Unreal的Insights工具的普及，使得审查者可以在提交代码之前量化每段逻辑对帧时间（Frame Time）的具体贡献，从而让审查不再仅依赖经验判断。

在游戏团队中，一次未经严格审查的资源加载代码可能导致移动平台内存超出256MB的硬性预算上限而被系统强制终止（iOS OOM Crash），或者在主机平台上因纹理常驻内存过多而触发显存置换，造成几十毫秒的帧时间尖峰。这使得游戏代码审查具有远高于普通Web服务的紧迫性。

---

## 核心原理

### 资源引用检查

审查者需要识别代码中所有可能导致**意外资源常驻**的引用模式。在Unity项目中，最常见的陷阱是在`MonoBehaviour`字段上使用`public Texture2D myTexture`直接引用——这会使该纹理在场景加载时立即进入内存且永不自动释放。正确的审查标准是：凡是不在当前场景生命周期内持续使用的大型资源（纹理超过512×512、音频片段超过5秒），必须使用`AssetReference`（Addressables系统）或`Resources.Load`配合显式`Resources.UnloadUnusedAssets()`来管理。

审查时还需检查**循环引用**问题：当A场景的Prefab持有B场景资源的引用，而B又引用A的资源时，卸载任意一方都不会真正释放内存。审查者应在Pull Request中要求提交者附上Unity的Asset Dependency Graph截图，证明新增资源不形成跨场景循环依赖。

在Unreal项目中，`TObjectPtr<UTexture2D>`和裸`UTexture2D*`在垃圾回收语义上完全不同——前者受GC追踪，后者在某些版本中可能不被标记为根对象而提前回收，审查时需逐一核查所有新增的资源成员变量的指针类型。

### 内存预算合规性检查

每款游戏在立项时应设定平台内存预算，典型移动游戏的总预算约为**350MB**（iOS）到**512MB**（高端Android），其中纹理预算通常占40%～50%，约140MB～200MB。代码审查阶段需要验证新增资产是否已经过压缩格式审批：iOS强制要求ASTC格式（每像素0.89字节），Android推荐ETC2，未压缩的RGBA32纹理会消耗ASTC格式8倍的显存，这类错误必须在合并前拦截。

审查者应要求提交者在PR描述中填写**内存影响声明**，格式如下：
- 新增资源：`enemy_boss_texture.png`，压缩后显存占用：12MB
- 卸载时机：Boss战结束，通过`Addressables.Release(handle)`释放
- 净增常驻内存：0MB（随场景生命周期加载卸载）

对于C++游戏逻辑中的自定义内存分配，审查需检查是否使用了项目规定的内存池分配器（如`FMemory::Malloc`而非系统`malloc`），因为混用分配器会破坏内存追踪工具的统计准确性，导致内存预算监控数据失真。

### 帧率影响检查

帧率影响审查的核心是识别**帧循环热路径**（Hot Path）中的高开销操作。审查者需要特别警惕以下几类代码模式：

**Update函数中的查找操作**：`GameObject.Find()`在Unity中会遍历整个场景对象树，时间复杂度为O(n)，在含有2000个对象的场景中单次调用约耗时0.3ms，若每帧调用一次则独自消耗30帧预算的1.8%。审查规则：任何在`Update()`、`FixedUpdate()`或`LateUpdate()`中调用`Find`类函数的代码必须退回修改，改为在`Awake()`中缓存引用。

**GC分配检测**：在C#游戏代码中，每帧在堆上分配内存会加速垃圾回收触发频率，导致周期性的帧时间尖峰（GC Spike），通常表现为每隔数秒出现一次20ms以上的卡顿。审查者需要识别隐式装箱（如将`int`作为`object`参数传递）、LINQ在热路径中的使用、以及字符串拼接（`"HP: " + hp`会生成临时字符串对象）等模式。

**Draw Call数量**：每增加一个不参与静态批处理的Renderer组件，都可能增加1个以上的Draw Call。移动平台的经验阈值是每帧Draw Call不超过150次，主机平台不超过2000次。审查时需要确认新增的渲染对象是否已标记`Static`（适用于不移动的场景物件）或使用GPU Instancing（适用于大量重复网格）。

---

## 实际应用

**案例一：武器系统重构审查**
某FPS游戏审查一个武器切换系统的PR时，发现代码在每次切换武器时调用`Instantiate(weaponPrefab)`生成新武器模型，并在切换回来时`Destroy()`销毁。这一模式会在武器切换时产生约0.8MB的瞬时内存分配和GC压力，并带来约5ms的实例化开销。审查意见要求改用对象池（Object Pool），预先在初始化阶段生成所有武器实例并通过`SetActive(true/false)`切换显示状态，将帧时间影响降至0.1ms以下。

**案例二：音频资源加载审查**
某移动RPG提交的背景音乐加载代码使用`AudioSource.clip = Resources.Load<AudioClip>("bgm_dungeon")`，且没有对应的卸载逻辑。审查者通过AudioClip的Import Settings确认该文件为PCM未压缩格式，时长4分钟，内存占用高达42MB，且`Load In Background`选项未勾选（意味着加载时会阻塞主线程约120ms）。审查结论：必须改为Vorbis压缩（内存降至约3MB），使用`LoadAsync`异步加载，并在地牢场景卸载时显式释放。

---

## 常见误区

**误区一：帧率测试通过即代表代码合格**
许多开发者认为在本机运行流畅就说明代码没有性能问题，但这忽略了**低端设备降频**和**热积累**（Thermal Throttling）的影响。iPhone在持续运行15分钟后，CPU频率可能降至峰值的50%，此时原本耗时0.5ms的逻辑可能变为1ms。正确的审查标准是：对任何进入热路径的新增逻辑，必须提供在目标最低配置设备（如骁龙660或A12以下芯片）上的Profiler截图，而非开发机截图。

**误区二：AssetBundle/Addressables加载就不需要关注内存**
一些开发者误以为使用了异步资产加载系统就自动解决了内存问题。实际上，Addressables的`LoadAssetAsync`不会自动释放资产，每个`AsyncOperationHandle`必须在使用完毕后调用`Addressables.Release(handle)`，否则资产会永久驻留内存。审查中需要对每一个`LoadAssetAsync`调用追踪对应的`Release`调用，验证其在所有代码路径（包括异常退出路径）中均被执行。

**误区三：内存审查只需检查纹理**
纹理确实是内存占用的最大来源，但审查者不应忽视**网格顶点数据**（一个未经LOD处理的角色模型可能有80,000个顶点，占用约9.6MB CPU内存）、**动画Clip**（包含IK曲线的动画文件常达数MB）和**着色器Variant数量**（每个Shader Variant在首次使用时需要编译，可能导致首帧卡顿数百毫秒）。完整的内存审查清单应涵盖至少这五类资产类型。

---

## 知识关联

游戏项目代码审查的三个维度与若干上游开发阶段直接关联。**资源引用审查**依赖团队在立项阶段制定的资源命名规范和依赖管理策略，若项目未规定Addressables分组策略（按场景分组 vs 按资源类型分组），审查者将无法判断某个跨组引用是否合理。**内存预算审查**需要参照平台技术规格文档（如索尼的PlayStation First Party Technical Requirements）以及项目内部的`MemoryBudget.xlsx`基准文件来核对数字。**帧率影响审查**则需结合项目的Profiler基线数据——即在无新功能的版本上录制的各帧时间分布——才能判断