---
id: "ta-mobile-memory"
concept: "移动端内存"
domain: "technical-art"
subdomain: "memory-budget"
subdomain_name: "内存与预算"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 移动端内存

## 概述

移动端内存管理是游戏技术美术在手机平台开发中必须面对的硬性约束体系。与主机平台不同，iOS和Android设备没有统一的内存规格——iPhone 6仅有1GB RAM，iPhone 13 Pro拥有6GB RAM，而Android设备碎片化更为严重，低端机型可能仅有2GB总内存，游戏可用内存不足600MB。这种极端的硬件差异要求技术美术必须为不同档位设备制定独立的资产预算方案。

移动端内存管理的独特难点在于操作系统的主动干预机制。iOS和Android都采用内存压力驱动的进程回收策略，而非固定配额制度。当系统内存紧张时，后台应用会被静默终止，前台应用如果不及时响应内存警告同样面临被杀风险。这与主机平台中开发者拥有确定性内存空间的体验有根本性区别，移动端的可用内存本质上是一个动态变化的竞争资源。

## 核心原理

### iOS内存限制与OOM机制

iOS使用内核层的Jetsam机制（又称OOM Killer的iOS实现）来管理内存压力。系统会为每个进程维护一个内存优先级队列，当物理内存不足时，按优先级从低到高依次终止进程。对于游戏开发而言，关键指标是"内存崩溃阈值"——在iPhone 6上这个值约为600MB，在iPhone X上约为1.2GB，超过此阈值游戏会收到SIGKILL信号直接崩溃，用户看到的现象与普通崩溃完全相同，没有任何错误提示。

iOS提供了`applicationDidReceiveMemoryWarning`回调作为最后的释放机会。技术美术团队应与程序员约定，在此回调触发时优先卸载哪些资产——通常的策略是释放当前场景未使用的纹理缓存、降低音频缓冲区大小，以及卸载离线区域的地图数据。Unity中对应的是`Application.lowMemory`事件，Unreal Engine则通过`FCoreDelegates::GetMemoryTrimDelegate`接收此通知。

### Android内存限制与Low Memory Killer

Android的内存回收机制称为Low Memory Killer（LMK），运行在Linux内核层。每个进程被分配一个oom_adj值（范围-17到15），数值越大越容易被杀死。前台游戏进程的oom_adj通常为0，但当系统内存低于特定阈值（称为minfree，默认配置下约为72MB空闲内存时触发）时，LMK开始按oom_adj从高到低回收进程。

Android提供了`onTrimMemory()`回调，其参数级别比iOS更为细化：`TRIM_MEMORY_RUNNING_LOW`（剩余内存中等紧张）、`TRIM_MEMORY_RUNNING_CRITICAL`（系统即将开始杀进程）、`TRIM_MEMORY_COMPLETE`（进程即将被杀死）。技术美术需要了解这些级别，以便与程序员共同制定分级的资产卸载策略，而非等到最极端情况才一次性释放所有资源。

### 移动端纹理内存的特殊计算方式

移动端GPU普遍采用Tile-Based Deferred Rendering（TBDR）架构，物理上共享CPU和GPU内存（Unified Memory Architecture）。这意味着一张2048×2048的ASTC 4x4压缩纹理占用约2.67MB显存，这部分显存直接来自系统RAM，而非独立显存池。相比之下，PC平台的独立显卡拥有完全分离的VRAM。在移动端，纹理内存、Mesh内存、音频内存和代码内存全部竞争同一个物理内存池，技术美术的纹理预算直接影响系统整体稳定性。

## 实际应用

**分档内存预算制定**：针对一款中度手游，典型的三档预算策略如下——高端机（3GB+ RAM）纹理预算300MB，中端机（2GB RAM）纹理预算180MB，低端机（1-1.5GB RAM）纹理预算120MB。技术美术需要为每档设备准备对应分辨率的纹理图集，通常低端机使用512×512图集替换高端机的1024×1024图集，内存占用直接减少75%。

**内存警告响应的资产分级**：在实际项目中，技术美术应将游戏资产标记为三个优先级：不可卸载（角色基础模型、UI核心图集）、可延迟卸载（上一个场景的环境纹理）、立即卸载（特效粒子纹理缓存、过场动画资产）。当`applicationDidReceiveMemoryWarning`触发时，程序首先卸载第三级资产，通常可以释放50-80MB，为系统提供足够缓冲。

**Android设备碎片化应对**：通过`ActivityManager.getMemoryClass()`可以查询设备声明的应用内存上限（通常为96MB、128MB或256MB），通过`Debug.getNativeHeapSize()`可以实时监控Native堆使用量。技术美术可以要求在游戏启动时读取这些值，动态选择加载哪套资产配置。

## 常见误区

**误区一：认为设备总RAM等于可用内存**。一台标注4GB RAM的Android手机，操作系统本身占用约1.2-1.5GB，后台服务和常驻应用再占用500-800MB，游戏实际可用内存可能只有1.2GB左右。技术美术在制定预算时应以"可用内存"而非"总内存"为基准，实际测试比查规格表更可靠。

**误区二：以为收到内存警告后还有充裕时间处理**。iOS的`applicationDidReceiveMemoryWarning`触发到进程被杀死之间可能只有数百毫秒，并非提供了几秒钟的操作窗口。在此回调中执行耗时的资源卸载操作（如同步磁盘IO）反而可能导致主线程卡死，加速被杀进程。正确做法是在回调中只做标记，由异步线程执行实际的资产释放。

**误区三：认为iOS和Android的内存行为一致**。两个平台的触发机制、阈值和回调时机存在显著差异。iOS更倾向于在接近崩溃阈值时才发出警告，而Android的`onTrimMemory`会在内存压力积累过程中多次触发。针对两个平台应制定独立的内存测试流程，而非共用一套QA标准。

## 知识关联

移动端内存管理建立在主机内存限制的基础概念之上，但引入了主机平台所没有的动态竞争机制和操作系统主动干预层。从主机端学到的纹理压缩格式选择（如ASTC vs ETC2）、Mipmap内存计算方式，在移动端同样适用，但需要额外考虑统一内存架构下CPU/GPU共享的影响。

在实际工作流中，移动端内存知识需要与资产打包策略（如Addressables的资产分组粒度）、场景流式加载设计，以及渲染管线的Drawcall批处理策略紧密协作。一个典型的技术美术工作成果是产出不同设备档次的内存预算文档，规定每类资产在各档位设备上的数量上限和单体大小限制，作为美术团队制作规范的硬性约束条件。