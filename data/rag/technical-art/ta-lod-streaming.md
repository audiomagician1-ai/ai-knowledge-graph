---
id: "ta-lod-streaming"
concept: "LOD与流送"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# LOD与流送

## 概述

LOD（Level of Detail，细节层次）与流送（Streaming）的结合，是现代大世界游戏中管理渲染资源的核心技术手段。单独使用LOD可以根据摄像机距离切换网格精度，但当场景规模超过单个关卡所能容纳的范围时，必须引入流送机制将世界分块按需加载，两者协同才能支撑数平方公里乃至更大规模的开放世界实时渲染。

Unreal Engine 5引入的World Partition系统将传统手动分割的Level Streaming自动化，把世界空间划分为固定尺寸的Cell（默认大小为128米×128米），每个Cell独立管理其内部Actor的加载与卸载。与此同时，HLOD（Hierarchical LOD）系统为这些Cell提供跨区域的低精度代理网格，使得未加载Cell也能以极低的面数出现在可见范围内，避免远景空洞。

理解LOD与流送的结合之所以重要，在于二者若配置不当会产生相互抵消的效果：LOD切换距离若大于流送加载距离，高精度LOD0网格会在对应Cell尚未加载时被请求，导致资源缺失或卡顿；反之若流送距离远大于LOD切换距离，大量Cell已加载但全部以LOD2渲染，造成内存浪费而无性能收益。

---

## 核心原理

### World Partition中的LOD分层架构

World Partition将Actor的运行时表现分为三个层次：Runtime Cell负责物理加载范围（默认加载半径约为512米）；Streaming Source（通常为玩家Pawn或摄像机Actor）驱动哪些Cell进入加载队列；HLOD Layer则在已卸载Cell的位置提供代理几何体。

HLOD0层代理通常由多个相邻Cell的静态网格合并生成，面数压缩比可达原始几何体的1:50甚至更高。引擎在构建HLOD时会自动合并材质并烘焙光照，生成的代理网格以Nanite或传统LOD链的形式存储于HLOD Actor资产中，切换判断依赖`HLODLayerTransitionScreenSize`参数（默认值0.1），即当代理网格的屏幕占比低于10%时保持显示HLOD代理，高于此值则触发对应Cell的完整加载流程。

### 流送距离与LOD距离的协调计算

在World Partition中，推荐将流送加载距离（`LoadingRange`）与LOD切换距离（`ScreenSize`阈值对应的世界空间距离）保持如下关系：

```
LoadingRange ≥ LOD0_WorldDistance × 1.5
```

其中`LOD0_WorldDistance`可通过公式近似估算：

```
D = (ScreenHeight × MeshDiameter) / (2 × tan(FOV/2) × ScreenSizeThreshold)
```

例如，对于直径10米的建筑、FOV=90°、目标屏幕尺寸阈值0.3，计算得`LOD0_WorldDistance ≈ 53米`。若`LoadingRange`设为128米，满足1.5倍关系，则LOD0在Cell加载完成后有足够的缓冲距离切换，避免加载瞬间直接显示LOD0引发的面数突增帧率抖动。

### Streaming Priority与LOD请求优先级

Unreal Engine的异步加载队列会根据`StreamingPriority`对Cell请求排序，数值越高越优先完成加载。在LOD与流送结合的场景中，技术美术需要将高频可见的前景Cell（玩家即将进入区域）的`Priority`设为较高值（如4或5），而仅用于HLOD代理显示的远景Cell保持默认值0，避免后台预加载占用带宽干扰近景Cell的LOD精度响应速度。

此外，Level Streaming Volume（传统流送方式）中的`MinTimeBetweenVolumeUnloadRequests`参数（默认2秒）决定了Cell从可见到触发卸载的最短间隔，与LOD切换的瞬时性形成节奏上的差异，需要在关卡设计时预留足够的过渡缓冲区域。

---

## 实际应用

### 大世界道路与建筑的分层策略

在《黑神话：悟空》类型的线性大场景或《Fortnite》类型的开放世界中，技术美术通常将沿路建筑分为三类处理：核心可交互建筑设置独立Cell并配置完整LOD0-LOD3链；背景装饰建筑合并入HLOD Layer并设置为仅HLOD显示，不触发完整Cell加载；地形本身使用Landscape LOD系统独立于World Partition的网格LOD，通过`LandscapeLODBias`参数在1到7之间调整分辨率。

### Nanite与流送的协同

启用Nanite的网格理论上不需要手动制作LOD链，引擎根据屏幕像素预算自动裁减三角形。但在World Partition流送场景中，Nanite网格所在的Cell在未加载状态下仍需HLOD代理，因此HLOD构建流程依然不可省略。技术美术需在HLOD Layer设置中指定代理生成方式为`MergeActors`或`SimplifyMesh`，后者面数更低，适合距离超过500米的HLOD1层级使用。

---

## 常见误区

**误区一：认为开启Nanite后无需配置LOD与流送的协调关系。**
Nanite解决的是已加载网格的屏幕空间精度问题，但它无法替代Cell级别的流送加载判断。若不设置HLOD Layer，已卸载Cell区域将出现空白，Nanite对此无任何补救能力。

**误区二：将流送加载距离设置为与LOD0切换距离完全相同。**
若二者相等，玩家移动至LOD0触发距离的瞬间Cell恰好开始加载，由于异步加载存在几帧到数十帧的延迟（在机械硬盘上可达500毫秒以上），这段时间内网格显示为空或以HLOD代理填充，产生明显的视觉弹出（Popping）。正确做法是保持1.5倍以上的安全余量。

**误区三：认为HLOD代理只需生成一层。**
对于视距超过1公里的场景，建议配置至少两层HLOD：HLOD0代理覆盖200-600米范围，面数约为原始的2%；HLOD1代理覆盖600米以上，面数约为原始的0.1%。单层HLOD在远景会导致代理网格面数过高，反而使GPU在远景三角形排队上浪费时间。

---

## 知识关联

本概念直接以HLOD系统为前提：HLOD的分层构建逻辑和`HLODLayerAsset`的配置方式是理解World Partition如何在未加载区域维持视觉连续性的基础。HLOD生成的代理网格质量直接决定了流送边界处视觉弹出的严重程度，因此HLOD构建参数（如`ProxyMeshVoxelSize`和`MergeDistance`）需要与流送加载半径联合调试，而非独立优化。

在LOD策略体系中，LOD与流送处于实际大世界项目落地的末端整合阶段，综合运用了静态网格LOD、HLOD、World Partition Cell管理以及异步加载队列等多项子系统的协调配置能力，是技术美术在开放世界项目中最终交付性能目标时必须掌握的工程化实践节点。