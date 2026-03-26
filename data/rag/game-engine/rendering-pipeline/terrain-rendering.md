---
id: "terrain-rendering"
concept: "地形渲染"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["地形"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.0
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

# 地形渲染

## 概述

地形渲染是游戏引擎渲染管线中专门处理大规模户外地表的技术体系，其核心挑战在于：地形数据量极大（一张4096×4096高度图包含1600万个采样点），但屏幕上实际可见的像素远少于此，必须通过层级细节系统在保真度与性能之间取得平衡。与普通网格渲染不同，地形几何体完全由高度场（Heightfield）驱动——XZ平面上的规则网格，每个顶点的Y坐标由高度图纹素决定，这一结构特性催生了专属的渲染算法。

地形渲染技术的演进历程清晰反映了硬件能力的进步。1997年的《雷神之锤II》依赖预计算BSP树处理室内场景，户外地形仅是简单网格。2001年Seumas McNally的ROAM（Real-time Optimally Adapting Meshes）算法通过二叉树动态分割三角形，实现了早期的自适应细节。2009年前后，GPU的曲面细分单元（Tessellation Unit）进入D3D11标准，使地形细节生成从CPU转移到GPU管线，彻底改变了地形渲染的架构。虚幻引擎5在2022年发布的Nanite虚拟几何体系统，则将地形渲染推向Virtual Heightfield Mesh方案。

地形渲染的工程意义在于它需要同时解决三个量级的问题：厘米级的近地面纹理细节、公里级的视距范围、以及毫秒级的帧时间预算。一款现代开放世界游戏的地形面积动辄达到64平方公里，如何在16ms内完成可见性剔除、几何生成、材质混合、阴影投射全流程，是地形渲染技术存在的根本原因。

## 核心原理

### GPU曲面细分（GPU Tessellation）

GPU曲面细分利用D3D11引入的三个可编程着色阶段：外壳着色器（Hull Shader）、固定功能细分器（Tessellator）、域着色器（Domain Shader）。地形网格首先以低分辨率的"控制面片"（Patch）提交，例如每个Patch覆盖16×16米，仅含4个角顶点。Hull Shader根据该Patch与摄像机的距离计算细分因子（TessFactor），距离越近TessFactor越大——典型配置下近处TessFactor=64，远处TessFactor=1。固定功能细分器按此因子在Patch内自动生成细分顶点，Domain Shader再对每个细分顶点采样高度图，完成实际的顶点位移。

这套流程的关键优势是几何数据量与渲染细节解耦：CPU每帧只提交数量固定的Patch（例如64×64=4096个），GPU根据视角动态决定每个Patch生成多少三角形。需要注意TessFactor在相邻Patch间必须匹配，否则边缘产生裂缝（T-Junction），实践中通过让相邻Patch的TessFactor取较小值的整数倍来避免。

### Clipmap与虚拟纹理

Clipmap是专为地形高度图和颜色纹理设计的流式LOD结构，由微软研究院在1998年的论文《Terrain Rendering Using GPU-Based Geometry Clipmaps》（Losasso & Hoppe，2004年SIGGRAPH正式发表）中提出。其结构是一组同心的正方形环形区域，每一级的像素间距是上一级的2倍——Level 0覆盖摄像机周围512×512纹素，Level 1以2倍间距覆盖更大范围，以此类推共7～9级。随着摄像机移动，各级Clipmap区域跟随滚动，仅更新发生变化的边缘条带（Update Region），避免了全量重上传。

虚幻引擎的Landscape系统使用的Heightmap Clipmap默认分辨率为2048×2048纹素，每次摄像机移动超过一个纹素间距时触发异步更新。与传统MIP链不同，Clipmap始终保持当前视点为中心，远距LOD不依赖摄像机朝向，适合任意方向的移动场景。

### Virtual Heightfield Mesh

Virtual Heightfield Mesh（VHM）是虚幻引擎5.0引入的地形渲染方案，其原理是将高度场的可见区域按屏幕空间误差动态生成网格，类似Nanite对多边形网格的处理思路，但专门针对高度场结构做了优化。VHM在GPU上执行一个两Pass的渲染：第一Pass用Compute Shader在屏幕空间计算每个像素所需的几何精度，生成一张"误差图"；第二Pass根据误差图决定每块地形的三角形密度，输出最终网格。

VHM的特别之处在于完全绕过了顶点缓冲区的CPU提交，地形几何完全在GPU内存中生成和消费，单帧几何生成延迟可控制在0.5ms以内（Epic在2022年GDC演讲中公布的数据）。VHM还原生支持虚拟纹理（Virtual Texture）——高度图和混合权重图通过页表机制按需加载，理论上支持无限尺寸的地形数据集。

## 实际应用

**虚幻引擎Landscape系统**：使用基于Clipmap的高度图流式加载，地形单元（Component）默认尺寸为63×63顶点，Section为31×31顶点，整个系统最大支持8129×8129顶点的地形（覆盖面积约8平方公里，分辨率1米/顶点）。材质混合通过最多8张权重图（Weightmap）控制，每张权重图的RGBA四通道分别存储4种地表材质的混合权重。

**Unity地形渲染**：Unity的Terrain组件使用基于四叉树的LOD系统，但从2021 LTS版本起引入了基于GPU Instance的DOTS Terrain（Burst编译器加速），将CPU地形LOD更新时间从约3ms压缩至0.3ms。Unity也提供Terrain Shader中的Layer Blend，支持最多8个混合层，通过高度混合（Height-based blending）避免不同材质之间的生硬过渡。

**地形阴影优化**：大规模地形的阴影图（Shadow Map）分辨率需求极高，常见做法是使用级联阴影贴图（CSM，Cascaded Shadow Maps），对地形近处使用2048×2048分辨率的阴影图，远处降至512×512，典型配置为4个级联，每级覆盖范围按对数分布（近级10m，远级3000m）。

## 常见误区

**误区一：TessFactor越高画质越好**。GPU曲面细分的TessFactor上限在D3D11中为64，意味着一个Patch最多生成64×64=4096个子三角形。若Patch本身在屏幕上只占100个像素，TessFactor=64会产生大量亚像素三角形，不仅没有视觉收益，还会触发GPU的过度绘制惩罚（Overdraw Penalty）并增加光栅化开销。正确做法是根据屏幕空间投影面积反算最优TessFactor，使每个三角形约占1～4像素。

**误区二：Clipmap与MIP贴图功能等价**。MIP贴图按固定的2的幂次缩小全图，而Clipmap始终以摄像机当前位置为中心保留最高精度数据。在飞行视角快速移动场景下，MIP贴图的低级别实际覆盖整个地形全局，而Clipmap的低级别仍然只在摄像机周围生效。这导致Clipmap的内存占用更低（固定大小的环形缓冲区），但需要持续的流式更新，而MIP贴图可以一次性上传后静止存储。

**误区三：Virtual Heightfield Mesh可完全替代传统Landscape**。VHM对高度场的假设是地表为单值函数（每个XZ位置对应唯一Y值），无法表达悬崖、洞穴、桥梁等几何结构。对于需要凹凸地下空间的场景，仍需以传统多边形网格配合地形渲染，VHM本质上是高度场渲染的极致优化，而非通用几何渲染方案。

## 知识关联

地形渲染建立在**渲染管线概述**所介绍的顶点-几何-光栅化流程之上：GPU Tessellation直接插入了Hull Shader和Domain Shader两个新阶段，理解这两个阶段需要熟悉标准渲染管线的顶点着色器输出格式（语义：SV_Position、TEXCOORD等）和从对象空间到裁剪空间的变换过程。Clipmap的流式更新机制依赖渲染管线的资源绑定模型，特别是纹理数组（Texture2DArray）和异步计算队列（Async Compute Queue）的工作方式。

地形渲染与**LOD系统**密切相关——Clipmap本质上是纹理域的LOD，GPU Tessellation是几何域的LOD，两者需要协调：当几何LOD降低时，对应的法线图精度也应同步降低，否则产生几何与法线信息不匹配的视觉错误（几何平滑但法线显示凹凸细节）。地形还与**遮挡剔除**系统交互：大型地形通常自身构成遮挡体，GPU端的Hierarchical Z-Buffer（HZB）遮挡剔除可以利用地形高度图快速判断低地物体（树木、建筑）是否被地形遮挡，从而减少不必要的Draw