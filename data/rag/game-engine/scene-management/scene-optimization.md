---
id: "scene-optimization"
concept: "场景优化综合"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---




# 场景优化综合

## 概述

场景优化综合是游戏引擎场景管理中将**合批（Batching）、视锥剔除（Frustum Culling）、流式加载（Streaming）与层级细节（HLOD）**四类技术协同运用的整体策略。单独使用任一技术只能解决渲染管线的局部瓶颈，而综合策略的目标是使 CPU DrawCall 数量、GPU 像素填充率、内存驻留量三项指标**同时**控制在目标平台的预算范围内。

该策略的工程化实践始于 2010 年代大型开放世界游戏的爆发期。《荒野大镖客：救赎2》（Rockstar Games，2018）的 GDC 技术分享披露，其场景管理系统需要在同一帧内维护约 **30 万个**场景对象的可见性状态，仅靠单一剔除手段无法满足 30 FPS 的目标帧率；Unreal Engine 5 的 World Partition 系统（Epic Games，2021）则将开放世界的格网单元格固定为 **128 m × 128 m**，以此对接合批、HLOD、流式三套子系统的空间索引。

理解四类技术相互约束关系的核心在于量化其**副作用交叉项**：激进的静态合批会将剔除粒度从单对象扩大为整块合批 AABB，导致无效 DrawCall 提交率上升；过细的 HLOD 分层（超过 3 层）会使流式加载在单次相机快速移动中触发 4~6 次资产换入换出，I/O 带宽峰值可超出硬件限制。

参考文献：Akenine-Möller, T., Haines, E., & Hoffman, N.《Real-Time Rendering》(4th ed., CRC Press, 2018) 第 19 章系统性阐述了上述技术的组合代价模型。

---

## 核心原理

### 1. 合批与剔除的耦合关系

静态合批（Static Batching）将多个网格合并为单一 VBO，使 DrawCall 从 N 降为 1，代价是丧失了对合批内单个子网格的逐对象剔除能力。若合批后的包围盒（AABB）跨越相机视锥边界，渲染器必须提交整个合批，即使其中 80% 的子网格已位于视锥之外。

解决此耦合问题的标准做法是**分块合批（Chunk-Based Batching）**：将世界划分为固定边长的单元格，仅在单元格内部执行合批。Unreal Engine 默认 Cluster 半径为 **300 cm**，Unity DOTS 文档给出的经验数据表明，此策略可将无效提交比例控制在 **15% 以内**。

GPU Instancing 是合批的另一形式：它不合并几何体，而是用一次 `DrawInstanced` 调用渲染 N 个相同网格，每个实例可独立接受遮挡查询，因此与剔除系统的兼容性显著优于静态合批。Direct3D 12 的 `ExecuteIndirect` 指令允许 GPU 端直接根据遮挡结果裁剪实例列表，可将 CPU 与 GPU 之间的回读延迟从 2~3 帧降低至 0 帧。

### 2. HLOD 与流式加载的分层协作

HLOD（Hierarchical Level of Detail）为场景中的建筑群、植被群等生成多层代理网格。以 Unreal Engine 5 的 World Partition 为例，HLOD 0 层代理使用原始三角形数的约 **10%**，HLOD 1 层进一步降至 **1%**。流式加载系统依据相机距离决定哪一层驻留于显存：

- **距离 < 加载半径**：卸载 HLOD 代理，流式载入原始高精度资产
- **加载半径 ≤ 距离 < 卸载半径**：迟滞区间，两级资产同时驻留并执行 Alpha 淡出
- **距离 ≥ 卸载半径**：原始资产从显存驱逐，HLOD 代理接管渲染

迟滞区间的宽度通常设为过渡距离的 **10%~20%**。若不设迟滞区间，在相机速度超过 **15 m/s**（如载具场景）时极易触发"弹出（Popping）"——原始网格尚未流入而 HLOD 代理已卸载，帧间出现空洞闪烁。

### 3. 可见性系统作为综合调度的驱动核心

本策略所有子系统依赖可见性系统在每帧输出的**可见对象集合（Visible Set）**作为统一输入。可见性系统先经 BVH（Bounding Volume Hierarchy）完成视锥剔除，再通过 Hi-Z Buffer（Hierarchical Z-Buffer）执行遮挡剔除二次过滤，将 30 万对象压缩到实际需要提交的数千个对象。

可见性系统的输出同时驱动三条下游管线：
1. **合批调度器**：根据可见单元格列表重新确定本帧有效的合批范围
2. **流式管理器**：根据可见区域的扩展边界（含预测移动方向）触发异步 I/O 预取
3. **HLOD 选择器**：根据对象到相机的屏幕投影面积（Screen Size Ratio）决定使用哪级代理

---

## 关键公式与算法

### DrawCall 预算分配公式

设目标帧时间为 $T_{frame}$（ms），CPU 端场景遍历允许占用的最大时间比例为 $\alpha$（通常取 0.25），则 DrawCall 总数上限为：

$$N_{DC} \leq \frac{\alpha \cdot T_{frame}}{t_{DC}}$$

其中 $t_{DC}$ 为单次 DrawCall 的 CPU 提交开销（现代 API 下约为 **0.005~0.02 ms**）。以 PS5 平台、目标 60 FPS（$T_{frame} = 16.67$ ms）、$\alpha = 0.25$、$t_{DC} = 0.01$ ms 为例：

$$N_{DC} \leq \frac{0.25 \times 16.67}{0.01} \approx 417$$

这意味着即使合批后仍有超过 417 个 DrawCall，也会导致 CPU 帧时间超预算，需要进一步提升合批率或切换至 GPU-Driven Rendering。

### 流式加载优先级调度伪代码

```python
# 每帧执行一次，按加载优先级对待流入资产排序
def streaming_priority_update(camera_pos, camera_velocity, assets):
    for asset in assets:
        # 预测相机 0.5 秒后位置
        predicted_pos = camera_pos + camera_velocity * 0.5
        dist = distance(predicted_pos, asset.world_pos)

        # 屏幕占比作为优先级权重
        screen_ratio = asset.radius / max(dist, 0.001)

        # 综合距离与屏幕占比计算优先级分数
        asset.priority = screen_ratio / dist

    # 按优先级降序，每帧最多触发 MAX_IO_REQUESTS 次 I/O
    sorted_assets = sorted(assets, key=lambda a: -a.priority)
    for asset in sorted_assets[:MAX_IO_REQUESTS]:
        if not asset.loaded:
            async_load(asset)
```

此调度算法中 `MAX_IO_REQUESTS` 在主机平台通常设为 **8~16**（受限于 NVMe SSD 队列深度），PC 平台可放宽至 **32**。

---

## 实际应用

### 案例一：《赛博朋克 2077》城市街道场景

CD Projekt Red 在 2022 年的技术博客中公开了其场景优化数据：Night City 单个街区包含约 **4.2 万个**独立网格对象。未优化时 DrawCall 峰值达 **12,000 次/帧**，优化后通过以下组合策略降至 **820 次/帧**：

- 静态建筑外立面采用分块合批（块大小 16 m），DrawCall 降低 **73%**
- 动态霓虹灯牌改用 GPU Instancing，同类型灯牌合并为单次调用
- 建筑内部在视锥外时触发 Portal Culling，剔除率达 **68%**
- 500 m 以外的建筑群切换至 HLOD 1 层代理（三角形数降至原始的 0.8%）

### 案例二：Unreal Engine 5 Nanite 与传统 HLOD 的边界

Nanite（UE5，2021）通过虚拟化几何体（Virtualized Geometry）在 GPU 端实现了逐像素的几何剔除，理论上可以取代传统 HLOD。然而 Nanite 对半透明材质、蒙皮网格（Skeletal Mesh）不支持，这两类对象在植被风吹动画、角色着装等场景中大量存在，仍需回退到传统 HLOD + 流式策略。因此 UE5 项目的实际做法是：**不透明静态网格交给 Nanite，其余对象走传统四类技术组合**。

---

## 常见误区

### 误区一：合批粒度越大 DrawCall 越少越好

错误实践是将整个关卡的所有静态网格合并为一个超级合批（Super Batch），DrawCall 确实降为 1，但合批后的单个 AABB 覆盖整张地图，视锥剔除完全失效，GPU 每帧须光栅化全部几何体。在 1080p 分辨率下，若场景总三角形数为 **5,000 万**而实际可见三角形仅 **400 万**，过度合批会使 GPU 填充率浪费 **92%**，帧率反而大幅下降。

正确做法：合批粒度对齐流式加载的单元格边界（如 128 m），保证剔除系统能以单元格为最小粒度工作。

### 误区二：HLOD 层数越多过渡越平滑

每增加一层 HLOD，流式系统需要管理额外一套代理资产的显存生命周期，并在相机移动时多触发一次换入换出。当 HLOD 超过 **3 层**时，距离阈值区间通常压缩至 **20~30 m**，玩家行走速度（约 1.5 m/s）在此区间内的停留时间不足 **15 秒**，此层 HLOD 几乎没有机会稳定显示，反而引入了额外的 I/O 和显存开销。大多数 AAA 项目实际采用 **2 层 HLOD** 作为上限。

### 误区三：遮挡剔除与合批无关

部分开发者误以为遮挡剔除（Occlusion Culling）只影响最终渲染提交，与合批无关。实际上，若遮挡剔除在合批之后执行，则被遮挡的子网格已经合入大批次中，无法被单独剔除；只有当遮挡剔除在合批**之前**完成，才能先裁减对象集合，再对剩余可见对象进行合批，最大化两项技术的协同收益。Unity 的 DOTS Hybrid Renderer 明确将遮挡剔除排在合批流水线前级，正是基于这一原因。

---

## 关键公式汇总

### 内存驻留预算方程

设显存总容量为 $M_{total}$，帧缓冲与 G-Buffer 固定占用为 $M_{fixed}$，则可用于场景资产的动态预算为：

$$M_{scene} = M_{total} - M_{fixed}$$

HLOD 代理与原始资产在迟滞区间内同时驻留，若迟滞区内资产数量为 $k$，单个原始资产显存为 $S_{hi}$，对应 HLOD 代理为 $S_{lo}$，则迟滞期间额外占用为：

$$\Delta M_{hysteresis} = k \cdot (S_{hi} + S_{lo})$$

当 $M_{scene} - \Delta M_{hysteresis} < M_{reserve}$（安全余量，通常为总容量的 **10%**）时，需要缩减迟滞区间宽度或降低 $k$ 的上限。

---

## 知识关联

### 与可见性系统的依赖关系

场景优化综合的所有调度决策均以**可见性系统**的输出作为前置输入（参见"可见性系统"章节）。可见性系统提供的 BVH 树结构同时被合批的空间分块索引和流式加载的距离查询复用，两套系统共享同一棵加速结构可节省约 **15~20%** 的 CPU 遍历时间（Unity DOTS 性能白皮书，2022）。

### 与渲染管线阶段的对应关系

| 优化技术       | 主要作