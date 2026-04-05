---
id: "ta-hlod"
concept: "HLOD系统"
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


# HLOD系统

## 概述

HLOD（Hierarchical Level of Detail，层级细节）是一种将场景中多个独立网格体合并为单一代理网格（Proxy Mesh）的优化技术。与传统LOD只对单个物体进行多精度替换不同，HLOD在空间层次上对**一组物体**进行聚合处理——当摄像机距离足够远时，整栋建筑群或整片树林会被合并成一个低面数的整体网格来渲染，从而将数百个DrawCall压缩为1个。

HLOD的概念最早在游戏引擎工业化流程中于2000年代中期被提出，Unreal Engine 4.20版本（2018年）正式将HLOD作为内置工具集成，允许开发者通过HLOD Outliner自动划分层级并生成代理网格。Unity则通过DOTS与场景分级加载在2019年后逐步支持类似架构。HLOD最重要的使用场景是开放世界游戏：《堡垒之夜》大地图、《黑神话：悟空》的山地地形等项目均依赖HLOD来维持远景的帧率稳定。

HLOD的价值在于两点：第一，它直接减少GPU提交的DrawCall数量，在主机与PC平台上，DrawCall过多比面数过多更容易造成CPU侧的渲染瓶颈；第二，代理网格可以预先烘焙光照与遮挡信息，避免动态光照在远距离物体上的无效计算。

## 核心原理

### 空间层级划分（Cluster分组）

HLOD系统首先对场景进行空间分簇（Clustering）。在Unreal Engine中，默认按照"簇大小（Cluster Size）"参数将场景网格体划分为若干矩形区域，典型设置为512×512单位一个簇。每个簇内的静态网格体被合并为一个HLOD Actor。层级（Level）可以嵌套：第0级HLOD将相邻建筑合并，第1级HLOD再将多个第0级代理网格合并，形成真正的树状层级结构。层级深度通常为2~3级，超过3级后代理网格的生成收益递减。

### 代理网格生成（Proxy Mesh Generation）

生成代理网格的核心算法是**网格合并（Merge）+ 减面（Screen Size Reduction）**。引擎收集簇内所有子网格，合并其顶点缓冲区与索引缓冲区，然后按照目标屏幕占比（通常为0.3%~2%屏幕面积）自动进行减面。Unreal的代理网格生成工具（ProxyLOD）基于Voxel Remeshing算法，将原始几何体体素化（体素分辨率可设，默认300），再从体素重建低面数外壳，最终面数通常为原始网格总面数的1%~5%。材质方面，所有子网格的贴图被烘焙合并为一张Atlas，分辨率多为512×512或1024×1024，以保证单次DrawCall完成渲染。

### LOD切换与过渡控制

HLOD的切换距离由**屏幕尺寸阈值（Screen Size Threshold）**控制，而非固定的世界坐标距离。计算公式为：

```
ScreenSize = (物体包围球直径 × 投影矩阵缩放因子) / 屏幕分辨率宽度
```

当ScreenSize低于设定阈值（例如0.05，即屏幕宽度的5%）时，引擎切换至HLOD代理网格，同时隐藏所有子物体。为避免突变（Popping），Unreal提供了Dither LOD过渡选项，在0.5~1.0秒内对两个状态做抖动混合。HLOD层级间的切换阈值必须与子物体的LOD0切换阈值严格对齐，否则会出现两套几何体同时可见的重叠穿帮。

## 实际应用

**开放世界城镇区域**：假设一片区域有300栋建筑，每栋有LOD0~LOD3共4级，远景时300个LOD3网格仍产生300次DrawCall。启用HLOD后，300栋建筑被合并为6~8个代理网格Actor，DrawCall降至个位数，GPU顶点处理量从约120万面降至约8000面。

**植被群落**：树木与草地通常数量极大。HLOD可将一片森林的1000棵树合并为1个代理网格，配合Impostor（公告板面片）技术，在超远距离呈现正确的树冠轮廓，而非使用完整几何体。

**调试工作流**：在Unreal Engine中，开启HLOD Outliner（窗口 > 层级细节），可以可视化每个簇的包围盒并手动将错误分组的物体移动到正确的簇中。生成完成后，使用命令`r.HLOD 0`可在运行时完全禁用HLOD以进行对比测试。

## 常见误区

**误区一：HLOD只是"多个物体的LOD3"**。这个理解忽略了HLOD的跨物体合并本质。普通LOD只替换单个网格的精度，DrawCall数量不变；HLOD将N个网格合并为1个，DrawCall数量从N降为1。两者解决的瓶颈完全不同——前者减少GPU顶点处理，后者减少CPU提交开销。

**误区二：代理网格越精细越好**。代理网格的目的是在远距离欺骗眼睛，面数过高会抵消HLOD节省的渲染开销。当代理网格的ScreenSize仅有1%时，观察者根本无法分辨800面与80面的差异，但80面版本节省的显存与顶点处理量更为显著。建议代理网格面数控制在每个簇不超过2000个三角形。

**误区三：HLOD可以替代Occlusion Culling**。HLOD减少的是可见远景物体的渲染开销，而Occlusion Culling处理的是被遮挡的不可见物体。两者在渲染管线中作用阶段不同，HLOD代理网格本身仍需接受遮挡剔除测试，并非开启HLOD就能省略遮挡系统的配置。

## 知识关联

**前置概念——LOD切换策略**：理解屏幕尺寸阈值如何控制单个网格的LOD切换，是配置HLOD切换阈值的直接基础。HLOD的ScreenSize参数与标准LOD的同名参数语义完全相同，但作用的对象从单个网格变为整个簇的代理网格。若不熟悉标准LOD切换机制，HLOD的切换距离调试将无从下手。

**后续概念——LOD与流送（Streaming）**：HLOD生成的代理网格本身可以作为流送的常驻资产（Always Loaded），而高精度子网格则按照玩家位置按需流入。这种"HLOD常驻 + 子网格流送"的组合模式是大型开放世界场景管理的标准架构，Unreal Engine的World Partition系统正是将HLOD与关卡流送深度耦合，实现无缝大世界的技术基础。