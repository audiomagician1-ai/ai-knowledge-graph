# 内存预算

## 概述

内存预算（Memory Budget）是游戏开发中用于限定并分配各类运行时内存占用的系统性约束体系，其核心任务是在纹理、网格、音频、代码段、运行时动态数据等资源类别之间预先划定配额，确保游戏在目标硬件上不触发操作系统的强制回收机制。与帧率预算或绘制调用预算不同，内存溢出不会导致性能优雅下降——超出物理内存上限的直接后果是进程终止（iOS的Jetsam内存回收）或虚拟内存换页（PC平台），二者都以游戏崩溃或数秒级卡顿为代价。

内存预算的历史根源可追溯至早期主机开发的极端约束环境。PlayStation 2（2000年发布）的32MB主内存迫使开发者以KB为单位规划每张纹理的MIP层级数量；Naughty Dog在《Jak and Daxter》开发中首次系统性地引入了"流式加载预算"概念，将关卡资源按距离摄像机的优先级动态换入换出，从而突破物理内存的硬性天花板（Gavin, 2002, GDC演讲《Jak and Daxter: A Postmortem》）。这一思路直接奠定了现代流式加载系统（Streaming System）的理论基础。

Jason Gregory在其著作《Game Engine Architecture》（第3版，2018）中明确将内存预算定义为"在既定硬件约束下，所有可能同时驻留于RAM中的资源总量的上界"，并指出该上界必须在项目预制作阶段（Pre-Production）即以文档形式固化，而非在收尾阶段被动优化。

## 核心原理

### 各平台实际可用内存数值

开发者必须区分"硬件物理容量"与"游戏实际可用量"——二者之差由操作系统内核、驱动程序与后台服务占用决定。

**主机平台**：PS5拥有16GB GDDR6统一内存，但索尼为操作系统和社交功能保留约2.5GB，游戏进程实际可用约13.5GB；Xbox Series X同为16GB，微软保留约2.75GB，游戏可用约13.25GB。Nintendo Switch搭载4GB LPDDR4，任天堂系统进程占用约1GB，游戏可用约3GB，切换为掌机模式时GPU降频但内存配额不变；注意Switch的CPU与GPU共享同一内存池，纹理与顶点缓冲区和程序栈竞争同一地址空间。

**移动平台**：iOS的内存管理尤为严苛。以iPhone 15 Pro（8GB RAM）为例，苹果的私有Jetsam策略在游戏进程RSS超过约2.0GB时发出`UIApplicationDidReceiveMemoryWarningNotification`，超过约2.8GB时直接发送`SIGKILL`。低端机型（iPhone SE第一代，2GB RAM）的崩溃阈值可低至约500MB。Android碎片化程度更高，搭载2GB RAM的低端机型（如联发科Helio G35机型）的`lowMemoryThreshold`通常设置为系统总RAM的15%，即约300MB，此时`onLowMemory()`回调触发，游戏必须立即释放非关键缓存否则面临OOM Killer。

**PC平台**：PC无固定上限，但DirectX 12的`IDXGIAdapter3::QueryVideoMemoryInfo`可查询当前GPU显存预算（`Budget`字段），该值会随其他进程动态变化。在16GB系统内存的典型配置上，游戏应将CPU侧目标峰值控制在4GB以内以兼顾低配用户。

### 内存的分类结构

内存预算的分配必须精细到子系统级别。一个典型的AA级游戏在Switch（3GB可用）上的分配框架如下：

| 资源类别 | 典型占比 | Switch绝对量（约）|
|------|---------|--------------|
| 压缩纹理（BC7/ASTC） | 40%~50% | 1.2GB~1.5GB |
| 网格与骨骼数据 | 10%~12% | 300MB~360MB |
| 音频（流式+驻留） | 8%~12% | 240MB~360MB |
| 引擎运行时与代码段 | 15%~20% | 450MB~600MB |
| 动态运行时（粒子/物理/AI） | 8%~12% | 240MB~360MB |
| 安全余量 | 5%~8% | 150MB~240MB |

开放世界游戏（如《塞尔达：王国之泪》）的纹理占比可突破55%，依赖高效的Tiled Resource和虚拟纹理技术来管理庞大的地形纹理集。相反，音乐节奏游戏（如《太鼓达人》系列）音频预算可超过25%，纹理和网格占比极低。

### 驻留内存与虚拟内存的区别

精确测量内存预算消耗需要理解两个操作系统层面的概念：

- **驻留内存（Resident Set Size, RSS）**：当前实际占用物理页面的字节总量，是内存预算检查的核心指标。
- **虚拟内存大小（Virtual Memory Size, VMS）**：进程地址空间的总映射量，包含已`mmap`但尚未访问的页面，不直接消耗物理内存。

游戏引擎在计算剩余预算时使用的基础公式为：

$$\text{剩余预算} = \text{平台硬上限} - \text{引擎基础RSS} - \sum_{i} \text{已加载资源}_i - \text{动态堆峰值估算}$$

其中"动态堆峰值估算"需要加入安全系数 $k$（通常 $k = 1.15 \sim 1.25$），以覆盖资源异步加载时的双缓冲峰值：

$$\text{安全动态堆} = k \cdot \text{当前动态堆大小}$$

Unreal Engine 5通过`stat memory`控制台命令输出以`FMemory::GetStats()`为基础的分类报告，区分`TextureMemory`、`MeshMemory`、`AudioMemory`等子项；Unity的Memory Profiler 1.1（2022年正式包，com.unity.memoryprofiler）支持双快照对比（Diff Two Snapshots），可精确定位两帧之间新增的托管堆分配。

## 关键方法与公式

### 纹理内存的精确估算

纹理是内存预算中最大的单类消耗，必须在资产制作阶段即建立计算规范。一张分辨率为 $W \times H$、使用BC7压缩（压缩比8:1于未压缩RGBA32）的纹理，含完整MIP链（共 $\lfloor \log_2(\max(W,H)) \rfloor + 1$ 级），其内存占用为：

$$\text{纹理内存} = \frac{W \times H \times \text{BPP}_{\text{compressed}}}{8} \times \frac{4}{3}$$

其中 $\frac{4}{3}$ 为MIP链系数（级数无穷极限），BPP（bits per pixel）对BC7为1 bit/pixel。例如一张4096×4096 BC7纹理含MIP链的内存占用为：

$$\frac{4096 \times 4096 \times 1}{8} \times \frac{4}{3} \approx 2.67 \text{MB}$$

而未压缩RGBA32同尺寸同MIP链纹理占用为：

$$\frac{4096 \times 4096 \times 32}{8} \times \frac{4}{3} \approx 85.3 \text{MB}$$

二者相差约32倍，直接印证了为何主机开发规范通常强制要求所有运行时纹理使用块压缩格式。

### 音频内存的双轨策略

音频内存管理采用"驻留（Resident）+ 流式（Streaming）"双轨策略：高频短促音效（步伐声、界面音效，时长 < 2秒）解码为PCM驻留在RAM中，保证零延迟；长音乐轨（BGM）保持Vorbis/Opus压缩格式在存储介质上，仅解码当前播放缓冲区（典型约128KB~256KB双缓冲）进入内存。Wwise引擎的官方建议（Audiokinetic, 2023）是将流式音频的内存I/O缓冲池控制在总音频预算的15%以内，剩余用于驻留资产池。

### 内存碎片的度量：碎片率指数

长时间运行的游戏（开放世界沙盒）面临严重的内存碎片问题。碎片率 $F$ 可由以下公式度量（Randolph, 2014, 《Game Programming Patterns》相关技术报告）：

$$F = 1 - \frac{\text{最大连续可用块大小}}{\text{总空闲内存}}$$

当 $F > 0.5$ 时，即使总空闲量充足，大型资源（如整关卡的纹理图集）也可能因无法找到足够大的连续块而分配失败。对策是使用线性分配器（Linear Allocator）配合帧边界重置，或池分配器（Pool Allocator）对固定大小对象进行预分配。

## 实际应用

### 案例：《黑神话：悟空》的主机内存适配

以《黑神话：悟空》（2024年）为例，该游戏基于Unreal Engine 5构建，使用了Nanite虚拟几何体和Lumen全局光照，这两项技术均有显著的内存开销——Nanite的流式几何缓冲区在PS5上约占200MB~400MB常驻内存，Lumen的辐射缓存（Radiance Cache）约占300MB~500MB。游戏在PS5版本的实际可用内存约13.5GB中，需要为这两项技术预先划定预算后，再分配其余资源，导致纹理预算相比同等规模的非UE5游戏缩减了约15%。

### 案例：Switch平台的动态分辨率与内存联动

Nintendo Switch的内存预算管理与分辨率策略强耦合。以掌机模式（720p目标）为例，帧缓冲区（双缓冲，720p RGBA16F）占用约12.4MB，而以电视模式（1080p）为目标时占用约27.9MB。部分开发商（如《异度之刃3》开发商Monolith Soft）采用动态分辨率，将帧缓冲固定为1080p大小预分配（避免动态分配碎片），但通过渲染分辨率缩放（0.5x~1.0x）节省GPU带宽，内存开销保持恒定，以换取预算的确定性。

### 开发流程中的预算门控（Budget Gating）

健全的内存预算管理流程应将预算检查集成进持续集成（CI）管线。每次提交触发自动化内存报告生成，若任一资源类别超出预设阈值（如纹理内存超出分配值的5%），则构建标记为警告；超出15%则阻断合并（Block Merge）。Epic Games的《Fortnite》团队公开分享了其"内存预算警察"（Memory Budget Police）自动化工具，在每次资产提交时运行纹理内存估算脚本，将超标资产退回给美术人员并附带具体的降低分辨率建议（Epic Games Unreal Fest, 2023）。

## 常见误区

**误区一：以编辑器内存数值代替设备实际数值。** Unreal Engine编辑器进程本身额外占用约1GB~2GB内存（反射系统、Slate UI、Live Coding模块），Unity Editor的托管堆在场景切换时不会完整释放。必须在目标设备的Development Build上使用平台专属工具（如PS5的Razor GPU/Memory、iOS的Instruments Allocations模板）采集真实RSS数据。

**误区二：忽视异步加载期间的峰值内存。** 当新场景的资源正在异步加载而旧场景资源尚未释放时，内存占用会短暂翻倍——这一"双峰"现象在低内存设备上极易触发崩溃。正确做法是在场景转换点强制执行同步卸载（`Resources.UnloadUnusedAssets()` + `GC.Collect()`在Unity中，或UE的`FlushAsyncLoading()` + 显式`ConditionalBeginDestroy()`），再开始加载新资源。

**误区三：将安全余量设为零。** 部分团队为了追求画质最大化而耗尽全部预算。操作系统后台进程（推送通知处理、系统UI）会动态占用额外内存，在极端情况下可达数十MB。iOS App Store审核指南（Apple, 2023, Technical Q&A QA1747）明确建议游戏在收到内存警告后应在30秒内将RSS降低至少10%，意味着游