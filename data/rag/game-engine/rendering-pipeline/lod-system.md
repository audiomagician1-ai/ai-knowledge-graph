---
id: "lod-system"
concept: "LOD系统"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 2
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# LOD系统

## 概述

LOD（Level of Detail，细节层次）系统是游戏引擎渲染管线中用于动态调整场景对象几何精度的技术机制。其核心思想来源于一个简单的视觉事实：距离摄像机越远的物体，在屏幕上占据的像素越少，因此无需以全精度的网格（Mesh）来渲染它。LOD系统通过为同一个对象预先准备多套不同多边形数量的模型，在运行时按照距离或屏幕占比动态切换，从而节省GPU的顶点处理开销。

LOD技术由James Clark于1976年在论文《Hierarchical Geometric Models for Visible Surface Algorithms》中正式提出，距今已近50年。在早期的3D游戏中，《雷神之锤》（Quake，1996年）已经采用了简单的几何LOD来应对大场景渲染。现代引擎如Unreal Engine 5引入了名为"Nanite"的虚拟几何体系统，本质上是把LOD的粒度细化到了单个三角面级别的自动化极端延伸。

LOD系统在开放世界游戏中尤为关键。以《荒野大镖客：救赎2》为例，场景中单帧可见的植被数量超过数百万株，若不进行LOD管理，仅植被部分就会耗尽绝大多数帧预算。因此LOD并非可选优化项，而是大规模场景渲染的基础支撑技术。

---

## 核心原理

### 离散LOD与切换阈值

最经典的实现是**离散LOD（Discrete LOD）**，即为一个模型手工或自动生成若干个LOD级别，通常称为LOD0、LOD1、LOD2……LOD0为原始高精度模型，LOD1、LOD2依次降低。常见的多边形缩减比例为：LOD1约为LOD0的50%，LOD2约为LOD0的25%，LOD3约为LOD0的12.5%，以此类推。

切换依据通常有两种：**世界空间距离**和**屏幕空间覆盖率（Screen Size）**。Unity引擎中LOD Group组件使用屏幕覆盖率（值域0到1），例如当对象在屏幕上的投影高度低于屏幕高度的60%时切换到LOD1。使用屏幕覆盖率比距离更准确，因为同一距离下，大型建筑和小型道具在屏幕上的尺寸差异极大。

Unreal Engine中，LOD切换距离可以通过`r.StaticMesh.LODDistanceScale`这一控制台变量全局调整，该值默认为1.0，增大该值会让切换发生在更远的距离，适合针对高分辨率显示器或高清渲染进行调优。

### 过渡策略：避免"突变"问题

离散LOD切换时会产生视觉上明显的模型"跳变"，称为**LOD Pop**（级别弹出）。为消除这一问题，工程上演化出了两类过渡策略：

**Alpha Dithering（抖动透明过渡）**：在切换瞬间，新旧两个LOD同时渲染，旧LOD通过棋盘格状的抖动透明度逐渐消隐，新LOD以同样方式逐渐显现。该方法只需渲染两个LOD各约半数像素，额外开销约等于渲染一个完整LOD，性能代价可控。Unity HDRP和URP均内置了这种Cross-Fade模式，过渡动画时长默认为1帧到若干帧不等，可由`Fade Transition Width`参数控制。

**连续LOD（Continuous LOD / CLOD）**：通过渐进式网格（Progressive Mesh）算法（由Hugues Hoppe于1996年提出）在运行时实时增删顶点，实现多边形数量的连续变化，完全消除突变。代价是需要存储完整的渐进式网格数据结构，内存占用是离散LOD的2至3倍，且实时顶点合并操作对CPU有持续消耗，因此在商业游戏中较少直接使用，更多出现于仿真软件领域。

### HLOD：层次化LOD

在超大型场景（如城市级别的开放世界）中，单个对象的LOD并不够用，因为远处的城市街区可能包含数千个建筑，即使每个建筑都切换到LOD3，几千个低精度Mesh的DrawCall依然会构成瓶颈。**HLOD（Hierarchical LOD）**通过将一组相邻对象在远距离时合并为一个单一的低精度代理网格（Proxy Mesh）来解决这一问题。Unreal Engine的HLOD系统可以自动将一个格子区域（Cluster）内所有静态网格烘焙成单一Mesh和单一材质，将该区域的DrawCall从数百次降低至1次。《堡垒之夜》的地图使用了HLOD系统，使得远处的城镇区域可以以极低的渲染代价存在于场景中而不被Cull（剔除）掉。

---

## 实际应用

**Unity中的LOD Group组件**是离散LOD最直接的应用示例。开发者将LOD0、LOD1、LOD2等子对象挂载在父节点上，在LOD Group Inspector中拖动各级别的屏幕覆盖率阈值滑块即可完成配置。一个典型的角色模型配置为：LOD0约15000面（近距离），LOD1约5000面（中距离），LOD2约1500面（远距离），LOD3为一个公告板（Billboard，仅用一张始终朝向摄像机的贴图代替几何体，面数为2个三角形）。

**植被系统**是LOD应用最密集的场景。SpeedTree这一主流植被中间件默认为每株树生成5个LOD级别，最终LOD为一个Billboard。Unreal Engine的Foliage工具直接集成了SpeedTree的LOD数据管线，可在编辑器内预览每个LOD级别的三角面数和切换距离。

**汽车与载具模型**在赛车游戏中同样高度依赖LOD。《极限竞速：地平线5》中的赛车LOD0通常有50万到100万面，代表物理级精度的车身网格；LOD1约10万面用于近距离追赶视角；LOD2约2万面用于俯视图和远景跟随镜头。

---

## 常见误区

**误区一：LOD级别越多越好。**
增加LOD级别并不总是有收益。每个额外的LOD级别都需要美术制作时间（或自动化网格简化的质量损失）、额外的内存存储，以及运行时检测切换条件的逻辑开销。对于屏幕上覆盖率本来就很小的小道具（如地上的石子），即使设置了5个LOD级别，实际游玩中摄像机几乎不会进入LOD0和LOD1的触发范围，这些额外资产只会占用内存和打包体积而几乎不发挥作用。通常对于小型静态道具，2至3个LOD级别即为最优配置。

**误区二：LOD系统会自动处理动态物体的遮挡问题。**
LOD系统仅根据距离或屏幕占比切换模型精度，它与遮挡剔除（Occlusion Culling）是完全独立的两套机制。一个被建筑完全遮挡的对象，LOD系统仍然会按距离保留其某个LOD级别的网格，只有Occlusion Culling才能将其从渲染队列中完全移除。在室内场景中若只依靠LOD而不开启遮挡剔除，仍会产生严重的性能浪费。

**误区三：LOD切换只影响视觉质量，不影响物理和游戏逻辑。**
在一些引擎实现中，LOD切换可能连带触发物理碰撞体精度的切换。若配置不当，当角色从LOD0区域走到LOD1区域时，碰撞体的简化可能导致"卡墙"或"穿模"等物理错误。Unreal Engine允许为不同LOD级别指定独立的碰撞设置，正确的做法是远距离LOD仅保留用于射线检测的简单碰撞体，而非复杂的凸包碰撞。

---

## 知识关联

LOD系统的工作依赖于**渲染管线概述**中介绍的顶点处理阶段（Vertex Shading）和DrawCall提交机制——LOD切换的本质是在提交渲染命令之前替换即将传入顶点着色器的网格数据，因此必须在理解顶点缓冲区（Vertex Buffer）和索引缓冲区（Index Buffer）的前提下才能理解LOD对GPU负载的实际影响。

LOD系统与**视锥体剔除（Frustum Culling）**和**遮挡剔除（Occlusion Culling）**共同构成引擎的可见性管理体系：剔除技术决定"哪些对象需要渲染"，而LOD决定"需要渲染的对象以何种精度渲染"。学习LOD之后，理解这两类技术如何在渲染循环的同一阶段协作，能建立对场景渲染优化完整的宏观认识。

网格简化算法（如边坍缩算法Quadric Error Metrics，由Garland和Heckbert于1997年提出）是生成LOD资产的基础数学工具，若希望在引擎之外定制LOD生成流程（例如为特殊形状的模型获得更高质量的自动化LOD），深入该算法是自然的进
