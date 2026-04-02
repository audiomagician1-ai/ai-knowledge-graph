---
id: "optimization-ld"
concept: "关卡优化"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 3
is_milestone: false
tags: ["性能"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 35.4
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.367
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 关卡优化

## 概述

关卡优化是指在关卡编辑器中，通过 LOD（细节层级）、视锥体裁剪、Draw Call 合批以及内存布局调整等技术手段，使关卡场景在目标硬件上达到稳定帧率的过程。与代码层面的算法优化不同，关卡优化直接作用于场景资产、光照烘焙数据和几何体摆放策略，是美术工作流与渲染管线之间的衔接环节。

关卡优化技术随着 3D 引擎的发展而逐步体系化。1996 年 Quake 引入 BSP 树与 PVS（Potentially Visible Set）预计算，标志着关卡优化从运行时蛮力剔除转向离线预计算可见性的范式转变。现代引擎如 Unreal Engine 5 和 Unity 6 将 LOD、遮挡剔除、GPU Instancing 等方案集成进编辑器工具链，关卡设计师可在编辑器内实时看到优化后的 GPU 统计数据（如 Triangle Count、Draw Call 数量）。

关卡优化的目标通常以具体指标锚定：移动端关卡要求单帧 Draw Call 控制在 100～200 以内，PC 端关卡的多边形预算一般在每帧 200 万～500 万三角面之间，主机平台则要求场景在 16.67 ms（60 FPS）或 33.33 ms（30 FPS）的帧时间预算内完成渲染。理解这些具体门槛，是关卡设计师在场景布置阶段做出正确取舍的前提。

---

## 核心原理

### LOD（Level of Detail）细节层级

LOD 技术通过为同一网格体准备多个精度版本，在摄像机距离超过阈值时自动切换低精度模型，从而减少远景几何体的三角面开销。在 Unreal Engine 中，LOD 切换距离由 `Screen Size` 参数控制：当网格体的屏幕占比低于设定阈值（例如 0.1，即占屏幕面积的 10%）时，引擎切换至下一级 LOD。通常一个资产会设置 LOD0～LOD3 共 4 级，LOD3 的三角面数量应为 LOD0 的 1/8 至 1/16。

关卡编辑器中的 LOD 优化不仅涉及静态网格体，还包括 Instanced Static Mesh（ISM）的 LOD 配置。大规模植被关卡（如开放世界草地）通过 Hierarchical Instanced Static Mesh（HISM）将数万株草的 LOD 切换批量管理，避免逐实例 CPU 调度开销。错误配置 HISM 的 Cull Distance 会导致数十万个草体实例全部进入 GPU，直接击穿帧率预算。

### 视锥体裁剪与遮挡剔除

视锥体裁剪（Frustum Culling）由引擎自动执行，凡是中心点或包围盒不在摄像机视锥 6 个裁剪面内的物体，均不提交渲染。关卡设计师的任务是确保场景物体的包围盒（Bounding Box）尽量紧凑，避免因艺术家误操作导致包围盒异常膨胀而绕过裁剪。

遮挡剔除（Occlusion Culling）则需要关卡设计师主动参与：在 Unreal Engine 中，`Precomputed Visibility Volume` 需要手动放置在玩家可到达的区域，编辑器构建时会在该体积内按网格间距（默认 200 cm）采样可见性数据，生成 PVS 表。若设计师遗漏在室内区域放置该体积，运行时将退回动态硬件遮挡查询（Hardware Occlusion Query），在 CPU-GPU 同步等待上引入 1～2 帧延迟。

### Draw Call 合批（Batching）

Draw Call 是 CPU 向 GPU 提交渲染指令的单次调用，过多的 Draw Call 会造成 CPU 端的驱动调度瓶颈。合批的核心条件是：相同材质（Material Instance）、相同网格体、相同渲染状态。

关卡编辑器中常用三种合批路径：
- **Static Batching**：将多个使用相同材质的静态物体合并为一个网格，节省 Draw Call，但合并后网格无法移动且内存占用翻倍。
- **GPU Instancing**：同一网格体的多个实例只提交一次 Draw Call，GPU 通过实例缓冲区读取各实例的 Transform，适合重复摆放的路灯、柱子等资产。Unreal Engine 在编辑器中将重复摆放的相同网格自动识别并启用 Instancing，条件是它们共享同一 Static Mesh 资产引用。
- **Dynamic Batching**：对每帧顶点数低于 300 的小网格体在 CPU 端合并，Unity 的 Dynamic Batching 要求单体网格顶点数不超过 900 个顶点位置属性。

### 内存优化

关卡的内存开销主要来自三部分：纹理显存（VRAM）、几何体顶点缓冲区和光照贴图（Lightmap）。纹理优化的核心参数是 `LOD Bias` 和 `Max Texture Size`，在关卡编辑器的 `World Settings` 中可以为整个关卡设置全局纹理流送池大小（Texture Streaming Pool）。Unity 的 `Texture Streaming` 系统以摄像机距离为依据，动态加载 Mip Level，确保 VRAM 使用量不超过设定上限（通常移动端设定为 256 MB）。

光照贴图的内存占用与 Lightmap Resolution 的平方成正比：将地板分辨率从 128×128 降至 64×64，内存占用减少 75%。关卡设计师应在编辑器的 Lightmap Density 可视化模式下，识别过度密集的 Lightmap 区域并逐一降级，而非盲目对所有物体应用统一分辨率。

---

## 实际应用

**开放世界地形关卡**：在 Unreal Engine 的大型地形关卡中，设计师将地形分割为若干 Landscape Component（默认每个分量 63×63 个顶点），并为每个分量配置 4 级 LOD。远景山脉在 LOD3 状态下三角面可降至 LOD0 的 1/16，配合 `Far Clip Plane` 将整体渲染距离限制在 100,000 cm，可将地形 GPU 开销控制在总帧时间的 30% 以内。

**室内关卡**：第一人称射击游戏的走廊型关卡大量依赖遮挡剔除。设计师通过在每个房间放置 `Precomputed Visibility Volume` 并将门洞设计为自然遮挡点，可使运行时可见 Draw Call 数量从全场景 2000 降至每帧 300 以下。房间之间的连接走廊宽度若小于 200 cm，则可以作为天然遮挡屏障，使两侧房间的内容互不可见。

**移动端关卡**：针对 Android 中端机型，关卡中单个物体的网格顶点数上限通常设定为 5000，全关卡纹理总量不超过 512 MB，并通过 `ETC2` 压缩格式将纹理 VRAM 占用压缩至未压缩格式的 1/4。

---

## 常见误区

**误区一：合批一定减少内存占用**
Static Batching 合并网格体可减少 Draw Call，但合并后的顶点缓冲区在内存中同时保留原始各子网格的拷贝和合并后的大网格，实际内存使用量增加而非减少。当场景中有 50 个小物件被合批，合批前每个物件内存为 10 KB，合批后总占用可能从 500 KB 增长至 900 KB，适用于 Draw Call 瓶颈明显而内存充裕的平台，不适用于内存受限的移动端关卡。

**误区二：LOD 切换越激进越好**
过早切换至低精度 LOD 会在摄像机拉近时产生明显的几何体"爆炸"（LOD Pop），破坏玩家沉浸感。LOD 切换阈值需与动画速度和摄像机移速配合调整：第一人称关卡中玩家移速约 600 cm/s，LOD 切换 Screen Size 阈值应设定在 0.05 以下，确保切换发生时物体在视野中足够小，肉眼不易察觉。

**误区三：遮挡剔除在任何关卡都能提升性能**
对于开阔的室外关卡（如足球场、沙漠），场景内大多数物体同时可见，Hardware Occlusion Query 的 CPU-GPU 同步开销反而高于其节省的渲染开销。此类关卡应禁用动态遮挡剔除，转而依赖 LOD 和 Cull Distance Volume 控制远景渲染量。

---

## 知识关联

关卡优化以**关卡性能分析**为前提：设计师必须先通过 GPU Profiler（如 RenderDoc 或 Unreal Insights）识别瓶颈类型（是 Draw Call 绑定、三角面绑定还是显存带宽绑定），才能选择正确的优化策略。对 Draw Call 瓶颈执行 LOD 优化收益极小，对三角面瓶颈执行合批同样收效甚微，错误诊断会导致优化工作完全无