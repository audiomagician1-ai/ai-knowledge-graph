---
id: "ta-pcg-world-partition"
concept: "世界分区与PCG"
domain: "technical-art"
subdomain: "pcg"
subdomain_name: "程序化生成"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 世界分区与PCG

## 概述

世界分区（World Partition）是虚幻引擎5引入的大世界管理系统，它将地图划分为固定尺寸的单元格（默认为12800×12800厘米，即128米×128米），并通过运行时流送（Runtime Streaming）按需加载这些单元格。当PCG（程序化生成）系统需要在这类开放世界中运行时，必须感知这套分区机制，否则生成逻辑会因数据未加载而产生空洞或崩溃。

PCG与World Partition的集成并非简单地"在大地图上运行PCG图表"，而是需要PCG图表理解哪些区域当前已流入内存、哪些区域的Landscape或样条数据尚未可用。虚幻引擎在UE5.1及之后的版本中专门为此引入了**PCG World Actor**和**PCG Volume**的流送感知模式，允许PCG组件跟踪World Partition的单元格状态并分批触发生成。

这种集成对技术美术的意义在于：一座面积10平方公里的开放世界地图，若不借助流送感知的PCG，就必须在编辑器中一次性生成所有植被、建筑碎片和道路细节，内存峰值往往超过64GB；而正确配置分区感知PCG后，生成工作可拆分到各个单元格，在运行时按玩家位置动态触发。

---

## 核心原理

### World Partition单元格与PCG的关系

World Partition将世界坐标空间切分为网格，每个网格单元格在加载时触发`FWorldPartitionCellLoader`事件。PCG系统通过监听`UWorldPartitionRuntimeHash`的单元格激活回调，得知某个128m×128m区域已完全加载，此时才调度该区域的PCG图表执行。

PCG图表中的数据采集节点（如`GetActorData`、`GetLandscapeData`）需要标记为**仅在单元格完全激活后才可采样**，否则Landscape高度数据可能只有部分LOD层级可用，导致生成的石块半悬浮在地表之上。在PCG图表属性中，`Execute On Grid`选项指定图表应在哪个层级的World Partition网格上执行——通常与加载半径保持一致，设为Runtime Grid的`Loading Range`值（默认约25600厘米）。

### PCG Partition Actor与流送生命周期

当启用了World Partition的地图中放置PCG Volume时，引擎会自动为每个PCG Volume的覆盖区域创建**PCG Partition Actor**。这些Partition Actor的空间范围与World Partition单元格对齐，确保一个Partition Actor中生成的SpawnedActor不会跨越两个流送单元格边界。

PCG Partition Actor的生命周期与所在单元格绑定：单元格卸载时，Partition Actor中生成的所有临时Actor同步销毁；单元格重新加载时，PCG系统检查磁盘上是否存有已序列化的生成结果（`bSerializeOutput = true`时），如果存在则直接读取，跳过重新计算，大幅减少流送时的CPU开销。这是大型开放世界中保持帧率稳定的关键机制。

### 边界处理与接缝消除

相邻PCG Partition Actor之间的边界（即单元格边缘）存在一个经典问题：两侧图表各自独立采样，可能在128m边界线上产生植被密度突变或重叠。解决方案是在PCG图表中使用**Bounds Modifier节点**，将采样区域向内收缩一定距离（通常为所用最大物体半径，例如大树的碰撞半径约300厘米），并通过Seed值锁定为基于世界坐标的哈希（`bUseSeedBasedOnPositionInWorld = true`），使两侧单元格的泊松分布采样结果在边界处自然衔接而不重叠。

---

## 实际应用

**大型地形植被系统**：以《黑神话：悟空》同类型的山地场景为参考，技术美术在UE5中配置一张128km²地形时，将植被PCG图表的`Grid Size`设为与World Partition一致的12800cm，图表内的Landscape采样节点使用`HierarchicalLOD 0`数据以保证精度。最终运行时每帧只有玩家周围约5×5个单元格（约40km²）处于活跃PCG执行状态。

**道路沿线建筑生成**：样条数据（Spline Actor）在World Partition中也具有流送边界，当道路样条横跨多个单元格时，PCG图表中的`GetSplineData`节点需要配合`Runtime Generation`设置为`Generate At Runtime`，并开启`Use Local Bounds For Spline Query`，使每个Partition Actor只查询与自身包围盒相交的样条段，避免跨单元格数据访问失效。

**运行时动态刷新**：在玩家游戏过程中破坏场景（如砍树）后需要本地更新PCG输出时，可对特定Partition Actor调用`CleanupLocalComponent()`后再`GenerateLocal()`，只重算被影响的128m单元格，而非刷新整张地图的PCG数据。

---

## 常见误区

**误区一：认为PCG Volume覆盖大区域就等同于启用了分区感知**

许多初学者将一个巨大的PCG Volume覆盖整张地图，误以为这样会自动利用World Partition进行分批生成。实际上，必须在PCG Volume的属性中将`Use World Partition Grid`显式设为`true`，引擎才会拆分出多个PCG Partition Actor。若该选项为关闭状态，即使地图启用了World Partition，PCG也会在地图加载时一次性计算所有区域，造成编辑器加载时长超过数十分钟，并极易内存溢出（OOM）。

**误区二：以为序列化输出可以完全替代运行时计算**

`bSerializeOutput`确实能让已生成结果缓存到磁盘，但序列化的是最终生成Actor的Transform和Mesh引用，而非PCG图表本身的中间数据。当底层Landscape高度或样条位置在编辑器中发生修改后，若忘记执行`Clean and Regenerate`，序列化缓存将与实际地形错位，出现树木悬空或插入地面的视觉错误，且在运行时不会自动检测到这种不一致，仅靠目视检查很难全面发现。

**误区三：将PCG Partition Actor的网格大小设得过小以追求精细控制**

有些技术美术将`PCG Partition Grid Size`从默认的12800cm改为3200cm（32m），期望获得更细粒度的流送控制。但这会导致Partition Actor数量按平方级增长：一张10km×10km的地图将产生约97656个Partition Actor，引擎在World Partition注册阶段的开销急剧上升，编辑器视口的物体统计面板中Actor数量会突破百万，反而拖慢加载速度。通常建议Partition Grid Size与World Partition的Runtime Grid保持一致或为其整数倍。

---

## 知识关联

**前置概念——运行时PCG**：理解世界分区与PCG集成的前提是掌握PCG的运行时生成模式（`Runtime Generation`），包括`Generate At Runtime`和`Regenerate On Overlap`两种触发方式。只有在运行时PCG的基础上，Partition Actor才能在单元格激活回调中自动触发生成；编辑器时生成（`Generate In Editor Only`）模式下的PCG图表无法响应World Partition的流送事件，也就无从实现动态分区。

**横向关联——Landscape与Nanite Tessellation**：PCG对分区地形的采样质量直接影响生成物体的贴地精度。开启Nanite的Landscape在World Partition加载后提供的碰撞数据与视觉LOD存在时序差异，PCG的`ProjectOnTerrain`节点有时需要延迟一帧执行才能拿到准确的物理高度，这在配置高密度植被系统时需要通过`Async Tracing`选项解决。

**工程实践延伸**：掌握本主题后，技术美术可进一步探索PCG与HLOD（Hierarchical Level of Detail）的联动——在远距离LOD层级使用PCG生成的静态网格代理替换Partition Actor中的详细几何体，实现从PCG动态生成到HLOD静态烘焙的无缝过渡，这是大型开放世界性能优化的完整链路。