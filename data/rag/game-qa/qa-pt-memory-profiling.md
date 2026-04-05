---
id: "qa-pt-memory-profiling"
concept: "内存检测"
domain: "game-qa"
subdomain: "performance-testing"
subdomain_name: "性能测试(Profiling)"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 内存检测

## 概述

内存检测（Memory Profiling）是游戏性能测试中专门针对内存使用情况进行量化分析的技术手段，涵盖运行时内存占用追踪、内存泄漏定位、堆碎片化评估以及内存预算合规性验证四个具体维度。与GPU Profiling关注显存带宽和渲染管线不同，内存检测主要面向系统RAM和托管堆（Managed Heap）的分配行为。

该技术在游戏开发中的系统性应用可追溯到PS2/Xbox时代，当时主机RAM仅有32MB，开发团队被迫建立精确的内存预算表。Unity引擎于2012年在Profiler窗口引入Memory模块，Unreal Engine则通过`memreport`命令行工具提供详细的内存分类快照，这两套工具至今仍是工业标准。

内存检测在游戏QA流程中之所以不可或缺，是因为内存问题往往不会立即导致崩溃，而是随游戏时长累积——一款开放世界游戏在连续运行4小时后若出现300MB的内存泄漏，则可能在低内存设备上触发OOM（Out of Memory）强制关闭，而这类问题若不经系统性检测极难被常规功能测试发现。

---

## 核心原理

### 内存占用追踪

内存占用追踪的基本方法是在固定时间间隔（通常每帧或每秒）对进程的RSS（Resident Set Size）和PSS（Proportional Set Size）进行采样。在Android平台，测试工具通过读取`/proc/[pid]/smaps`文件获取分类内存数据，可区分Native Heap、Java Heap、Code段、Stack段等不同内存区域的独立占用量。

Unity环境下，内存分为托管内存（Mono/IL2CPP堆）和非托管内存（Native Plugin、音频缓冲、纹理上传缓冲）两大类，两者必须分别追踪。测试人员通常记录以下三个关键时间点的内存基线：游戏启动完成后（冷启动基线）、进入某个关卡稳定运行5分钟后（热态基线）、经历若干次场景切换后（循环压力基线）。若热态基线比冷启动基线高出超过20%且无法通过GC回收，则需进入泄漏分析阶段。

### 内存泄漏检测

内存泄漏指程序分配的内存因失去引用无法被垃圾回收器（GC）或释放函数（`free()`）回收，导致已用内存单调递增。检测方法的核心是**对象引用图分析**：通过内存快照（Memory Snapshot）对比两个时间点的堆状态，找出在两次快照间被分配但在第二次快照时仍无法被GC回收的对象集合。

Unity Memory Profiler（com.unity.memoryprofiler包，0.7.1版本后支持差异对比视图）可以直接展示两个`.snap`文件之间新增的持久对象，并按类型分组统计。一个典型泄漏案例：事件订阅未在`OnDestroy`中取消注册（`EventSystem.onClick -= handler`遗漏），导致已销毁的UI对象仍被事件系统持有引用，每次打开该UI界面就累积约2KB的托管内存。

检测步骤标准化为：①获取基准快照 → ②执行目标操作（如开关同一界面10次）→ ③触发GC（`GC.Collect()`）→ ④等待2秒 → ⑤获取比对快照 → ⑥分析差异报告中实例数量仍在增长的类型。

### 堆碎片化分析

碎片化（Fragmentation）指堆内存中存在大量不连续的空闲小块，导致即使总空闲内存充足，也无法满足一次较大的连续内存分配请求。碎片化率的计算公式为：

> **碎片化率 = 1 - (最大连续空闲块 / 总空闲内存)**

该值接近0表示碎片化轻微，接近1表示严重碎片化。在Unreal Engine中，可通过`stat memory`命令查看`MemoryFragmentation`指标；在Unity中，IL2CPP使用BoehmGC，碎片化问题比Mono更严重，因为BoehmGC不执行内存紧缩（Compaction）。

QA团队在检测碎片化时，通常在游戏运行1小时后强制分配一块16MB的连续内存块，若分配失败但当前空闲内存超过50MB，则可判定存在严重碎片化问题。

### 内存预算管理

内存预算是为每类资产和系统预先分配的最大内存上限，例如一款面向2GB RAM设备的手游，典型预算分配为：纹理≤350MB、音频≤80MB、代码与引擎≤150MB、运行时缓冲≤100MB、安全余量≥150MB。测试人员的职责是验证每个关卡在最大负载下是否超出对应预算分项，而非仅看总量是否超限。

---

## 实际应用

**开放世界游戏的区域切换测试**：在大地图游戏中，测试人员从地图西端步行至东端，全程以30秒为间隔记录内存快照。若发现内存在穿越3个区域边界后累计增长超过80MB且未下降，则可定位为流式加载（Streaming）系统存在资产卸载延迟或泄漏，需检查`AddressableAssets.Release()`调用时序。

**移动端OOM崩溃复现**：在搭载3GB RAM的Android测试机上运行游戏，同时通过`adb shell dumpsys meminfo [package]`每10秒采集一次PSS数据，绘制内存时序曲线。若在游戏进行约45分钟时PSS超过1.4GB（Android系统对应用的典型OOM阈值约为物理内存的50%），则需分析此前5分钟内的对象分配热点。

**托管堆扩张监控**：Unity的托管堆只扩张不自动收缩，每次扩张步长为前次堆大小的1.5倍。若初始堆为4MB，经历若干次扩张后可能达到4→6→9→13.5MB…测试中若发现托管堆在一次战斗场景后从8MB扩张至24MB，则需检查战斗逻辑中是否存在每帧创建临时List/Dictionary等GC压力操作。

---

## 常见误区

**误区一：GC.Collect()后内存归零即视为无泄漏**
手动调用`GC.Collect()`并观察内存下降，并不能证明系统无泄漏。托管堆向操作系统归还内存的时机由运行时控制，不由GC决定。正确做法是对比两次快照中**对象实例数量**的变化，而非仅看内存总量数字——即使内存数字相同，若某类对象实例数从50个增长到200个，仍存在引用堆积问题。

**误区二：只检测托管内存，忽略Native内存**
在Unity项目中，纹理、音频Clip、AssetBundle的内存占用不在托管堆中，而在Native内存区域。曾有案例中Unity Profiler显示托管堆仅60MB，但实际进程内存超过800MB，差值全部来自未释放的AssetBundle Native对象。检测时必须同时查看`Profiler.GetTotalReservedMemoryLong()`（托管+引擎保留）和`Profiler.GetTotalUnusedReservedMemoryLong()`两个API的返回值。

**误区三：内存碎片化等同于内存泄漏**
碎片化导致的"可分配内存减少"与泄漏导致的"已用内存增加"是两种完全不同的机制。泄漏的标志是总已用内存单调递增；而碎片化可能在总已用内存稳定的情况下仍导致大块分配失败。两者的修复方向截然相反：泄漏需要修复引用管理，碎片化需要调整分配策略（如使用对象池固定大小分配）或启用内存紧缩。

---

## 知识关联

内存检测与**GPU Profiling**共用快照时间戳对齐的分析方法，但GPU Profiling中的显存（VRAM）占用与本文讨论的系统RAM是两套独立的存储资源，显存满载不等于RAM满载，两者需分别建立预算体系。在实际测试中，高纹理质量设置会同时消耗VRAM（GPU侧）和RAM（CPU侧缓存副本），这是连接两个测试领域的典型交叉点。

内存检测的结论直接影响**加载时间测试**的分析维度：若内存碎片化严重，场景加载时的大块连续内存申请会触发频繁的GC和堆扩张，导致加载时间异常延长。加载时间测试中出现的不规律耗时尖峰，有相当比例可追溯到内存状态不良（高碎片化或堆空间不足），因此在进行加载时间测试前，建议先完成目标关卡的内存预算验收，确保在内存状态干净的基线下采集加载数据。