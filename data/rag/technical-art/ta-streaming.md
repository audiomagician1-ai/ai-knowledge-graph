---
id: "ta-streaming"
concept: "资源流送"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 资源流送

## 概述

资源流送（Resource Streaming）是一种在游戏运行时根据玩家位置和视野动态加载、卸载纹理、网格、音频和关卡区块的异步技术。与传统的一次性全量加载不同，流送系统会持续计算每个资源当前所需的细节层级（LOD），只将玩家实际可见或即将可见的数据从磁盘/网络传输到内存，从而将峰值内存占用降低40%~70%，同时消除玩家在过渡区域感受到的加载卡顿。

该技术的大规模商业化始于2001年前后。GTA III引入了以玩家坐标为圆心的"流送圆（Streaming Circle）"概念，在约200米半径内分层加载城市网格与纹理，这成为开放世界流送架构的范本。虚幻引擎4（UE4）在此基础上发展出Texture Streaming和Level Streaming两套独立管线；Unity则从2017年的2017.1版本起通过Addressables的前身AssetBundle正式支持异步流送工作流。

对技术美术而言，理解资源流送至关重要，因为错误的流送配置会在玩家快速移动时产生明显的纹理"弹出（Pop-in）"现象，这是玩家最直接感知到的画质劣化。技术美术既要保证视觉质量，又要让资源符合流送系统的吞吐量限制，因此必须掌握流送预算的制定与调试方法。

---

## 核心原理

### 1. Mip流送与纹理预算

纹理流送的最小操作单元是Mip级别（Mip Level），而非整张纹理。系统通过以下公式计算屏幕上每个纹理应该使用第几级Mip：

```
所需Mip = log₂(纹理分辨率 / 屏幕像素覆盖尺寸)
```

UE5的Texture Streaming系统维护一个全局纹理流送池（Texture Streaming Pool），默认大小为512 MB（可在`r.Streaming.PoolSize`中调整）。当池满时，系统会按优先级丢弃当前屏幕贡献度最低的高级Mip，保留低分辨率Mip作为降级显示。这就是为什么在流送池过小时，近处物体的纹理会短暂模糊——系统在等待异步读取完成前临时展示了低分辨率Mip。

### 2. 流送关卡（Level Streaming）与世界分区

UE引擎中，大型开放世界通过将场景切割成多个子关卡（Sublevel），并用`ULevelStreamingDynamic::LoadLevelInstanceBySoftObjectPtr`或蓝图中的`Load Stream Level`节点实现异步加载。关卡流送以"流送距离（Streaming Distance）"为触发依据，当玩家进入某个关卡的加载触发体积（Loading Trigger Volume）时，后台线程开始读取该关卡的.umap文件，完成后才在主线程进行Actor的BeginPlay注册。

UE5引入的World Partition系统将关卡流送颗粒度进一步细化为网格单元格（Cell），默认Cell尺寸为128×128米，玩家周围的Cell根据`r.WorldPartition.RuntimeStreaming.StreamingRange`自动管理加载/卸载，彻底替代了手动划分子关卡的工作流。

### 3. 网格流送与Nanite的交互

传统网格流送依赖LOD链（LOD0最精细，LOD4最粗糙），系统在运行时根据对象屏幕占比百分比切换LOD，通常以屏幕占比低于1%为LOD3到LOD4的切换阈值。启用Nanite的网格不需要预烘焙LOD链，Nanite自身的Cluster层级结构承担了流送职能——它将网格划分为约128个三角形的Cluster，在GPU端按虚拟化方式按需拣选，等效于自动化的网格流送。但要注意，Nanite Streaming不能完全替代关卡流送：场景中不可见区域的Nanite物体仍需通过关卡流送卸载Actor本身，否则碰撞和逻辑开销仍然存在。

### 4. 异步IO与流送吞吐量

流送性能的硬件瓶颈是存储设备的随机读取带宽。HDD的随机4K读取约为0.5~1 MB/s，而NVMe SSD可达1~3 GB/s；PS5的Kraken解压器配合定制SSD将原始I/O带宽提升至5.5 GB/s，这正是索尼为PS5量身设计流送架构的根本原因。技术美术在制作资源时需要配合压缩格式（如BC7/ASTC）降低单次读取的数据量，以减少IO等待时间。

---

## 实际应用

**开放世界纹理预算分配：** 在一个地表面积为16 km²的开放世界项目中，通常将地表地形纹理的基础Mip设为4096×4096，并强制流送禁止（Non-Streaming）使其常驻内存，而所有建筑和道具纹理则全部启用流送，单个资源的最大Mip限制为1024×1024，以此控制流送池占用在256 MB以内。

**流送优先级标注：** 对于玩家出生点附近的关键资源，技术美术应在UE5的纹理属性面板中将`Streaming Priority Offset`设为正值（如+8），使系统优先加载这些纹理，避免开场过场动画期间出现模糊纹理。

**流送距离调优：** 在赛车类游戏中，车辆时速可达300 km/h，标准的128米Cell加载范围远不够用。此时需将`Streaming Distance`提高至600~1000米，并配合异步预读（Async Prefetch）让系统提前2~4秒开始加载前方Cell，补偿IO延迟。

---

## 常见误区

**误区一：流送池越大越好。** 许多开发者将`r.Streaming.PoolSize`设置为2048 MB甚至更高，认为这能彻底消除模糊纹理。但流送池过大会挤占其他系统（如RHI资源、音频缓冲）的显存空间，在主机平台总显存只有8~16 GB的限制下，盲目扩大流送池反而会导致整体帧率下降或崩溃。正确做法是使用`stat Streaming`命令实测当前场景的真实纹理需求，按峰值需求的120%设置流送池上限。

**误区二：所有纹理都应该启用流送。** 对于UI纹理、后处理LUT（通常为256×16或512×512）、始终全屏可见的天空盒纹理，应设置为Non-Streaming常驻内存。这类纹理如果参与流送，系统每帧都会计算其Mip优先级却永远不会卸载，产生无效的CPU开销。

**误区三：关卡流送只需划分子关卡即可，无需考虑资源的物理布局。** 流送加载时间与资源在磁盘上的存储位置密切相关。如果同一个流送关卡的资产文件分散在数十个Package中，IO请求的随机寻址开销会成倍增加。应将同一流送关卡用到的纹理和网格打包进同一个Chunk，并在Project Settings的Packaging分组中通过Primary Asset Labels统一指定ChunkID。

---

## 知识关联

资源流送与**虚拟纹理（Virtual Texture）**有直接的技术依存关系：虚拟纹理将整张大型纹理（如8192×8192）划分为128×128像素的物理页，其按需加载物理页的机制本质上就是纹理流送的极细粒度版本，学习资源流送可以将虚拟纹理的页面调度逻辑看作流送系统的特例加以理解。反过来，传统Mip流送与虚拟纹理并不完全兼容——UE5中开启Runtime Virtual Texture的材质会绕过标准Mip流送路径，技术美术在同时使用两者时需要分别配置预算参数，避免双重计算导致显存超支。

在更宏观的性能优化体系中，资源流送是LOD系统、遮挡剔除和GPU实例化三者的上游依赖：只有资源被正确流送到内存后，LOD切换才有数据可用，遮挡剔除才能在剔除结果稳定的前提下避免频繁触发加载/卸载的抖动问题。