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
---
# 关卡优化

## 概述

关卡优化是指在关卡编辑器中，通过LOD（Level of Detail，细节层次）、视锥/遮挡裁剪、Draw Call合批与内存布局优化等手段，将已完成美术制作的关卡场景调整至目标平台可稳定运行的技术过程。它直接决定关卡在运行时的帧率、内存占用和加载时间三项核心指标，而非仅影响视觉效果。

这一领域的系统化方法成形于2000年代初期，随着《虚幻竞技场2003》引入可视化BSP裁剪工具而被广泛推广。Unity于2005年将静态合批（Static Batching）作为内置功能提供给独立开发者，使关卡优化不再是AAA团队的专属技术。现代关卡编辑器如Unreal Engine 5的World Partition系统，已将部分优化逻辑内嵌为自动化流程，但理解手动优化的底层机制仍是必须掌握的技能。

关卡优化的工作通常在**关卡性能分析**之后展开——分析阶段识别的瓶颈决定了优先处理LOD、裁剪还是Draw Call问题。一张关卡若在分析中显示GPU过载且Draw Call超过3000次，则合批优化优先级高于内存优化；若纹理内存超出显存预算，则需优先处理纹理流送和Mip设置。

---

## 核心原理

### LOD（细节层次）设置

LOD系统根据网格体与摄像机的屏幕空间占比，在不同精度的模型版本之间切换。Unreal Engine中使用**屏幕尺寸阈值（Screen Size）**来定义切换点，而非固定距离值：当一个静态网格的屏幕占比低于0.3（即占屏幕30%区域），切换至LOD1；低于0.1时切换至LOD2。

LOD模型的面数规则通常遵循"每级缩减50%~60%"：若LOD0为8000个三角形，则LOD1约为3500，LOD2约为1500，LOD3可低至300。在关卡编辑器中为大型场景物体（如建筑、植被）配置LOD时，LOD4或Imposter（广告牌替代）是远景密集物体的常用手段。Nanite技术（UE5）通过微多边形系统自动处理几何LOD，但对于蒙皮网格和半透明材质仍需手动配置LOD。

### 裁剪：视锥裁剪与遮挡裁剪

**视锥裁剪（Frustum Culling）**由GPU自动执行，剔除摄像机视野六面体之外的所有网格。关卡设计师可通过调整摄像机远裁剪平面（Far Clip Plane）数值来减少参与视锥测试的对象数量——将Far Clip从20000单位降至8000单位，在室内关卡中通常可减少40%~60%的渲染对象。

**遮挡裁剪（Occlusion Culling）**则更复杂：GPU或CPU预判哪些对象被其他不透明几何体完全遮挡。Unreal中的Hardware Occlusion Query会在渲染深度预通道后发送查询，延迟1~2帧返回结果，因此快速移动的摄像机可能出现短暂的"弹出"（Pop-in）现象。在关卡编辑器中，开启`r.HZBOcclusion 1`命令并设置合适的`Min Occlusion Pixels`阈值（默认为20像素），可平衡裁剪精度与查询开销。

对于封闭室内关卡，**预计算可见性体积（Precomputed Visibility Volume）**是比动态遮挡查询更高效的方案——编辑器在构建阶段计算空间网格中每个格子（默认200×200×150cm）的可见对象集合，运行时直接查表，避免GPU查询的延迟问题。

### Draw Call合批

每次CPU向GPU发出绘制一个网格体的指令称为一次Draw Call，过多的Draw Call会导致CPU提交命令的开销成为瓶颈。

**静态合批（Static Batching）**：将标记为Static的多个使用相同材质的网格合并为一个顶点缓冲区，运行时一次Draw Call绘制所有实例。代价是内存增加——每个静态合批网格在内存中保留独立拷贝，100个合批石块会在内存中保存100份顶点数据，因此静态合批适用于数量少但材质统一的大型物件。

**GPU实例化（GPU Instancing）**：向GPU传递一次几何数据和N份变换矩阵（位置、旋转、缩放），GPU并行绘制N个实例。相比静态合批，GPU实例化不增加内存中的网格拷贝，是大量重复物件（树木、路灯、石块）的首选方案。在Unity HDRP中，GPU Instancing需在材质属性中显式勾选启用；Unreal的HISM（Hierarchical Instanced Static Mesh）组件则同时提供实例化与LOD管理。

**Atlas合批**：将多张小纹理合并为一张Atlas贴图，使原本使用不同材质的对象共享同一材质，从而满足合批条件。关卡中的UI元素、散落道具通常使用此方法。

### 内存优化

关卡运行时内存主要由纹理、网格、音频三类资产占用。纹理通常占60%~70%，是优化的首要目标。

**Mip设置**：正确配置纹理的Mip偏置（Mip Bias）可减少显存占用。将一张2048×2048的地面纹理的`LOD Bias`设为1，则运行时实际加载1024×1024版本，显存占用减少75%（因Mip链的每级面积缩减四分之一）。

**纹理流送（Texture Streaming）**：Unreal和Unity均支持根据对象与摄像机的距离动态加载对应Mip级别，避免将全分辨率纹理常驻内存。关键参数是`Texture Streaming Pool Size`——若运行时频繁出现"Texture Streaming Pool Over Budget"警告，需要增加Pool大小或降低关键资产的纹理分辨率。

---

## 实际应用

**开放世界草地优化**：以一个10km²的开放世界关卡为例，草地使用HISM组件绘制，配置3级LOD（LOD0：12面/株，LOD1：4面/株，LOD2：广告牌），并在距摄像机50米外通过Cull Distance Volume彻底剔除个体草株，改由地面材质的混合层（Blend Layer）在视觉上延续草地效果，可将草地相关Draw Call从每帧6000次降至800次以内。

**城市室内关卡**：在走廊型室内关卡中，使用Precomputed Visibility Volume将每个房间的可见集合预计算完毕，相比动态遮挡查询节省约3ms的CPU帧时间，同时消除摄像机快速转动时的弹出瑕疵。将室内道具按材质归类后，通过Atlas合批将相同区域的Draw Call从450次降至120次。

---

## 常见误区

**误区一：对所有物体均开启静态合批**
静态合批在对象数量庞大时会导致内存爆炸。100个顶点数为5000的石块静态合批后，合并顶点缓冲区占用50万顶点数据的内存，而GPU实例化同样100个石块只需存储1份5000顶点数据与100个变换矩阵（每个矩阵64字节=6400字节），内存差异可达数十倍。选择合批方式时必须先确认对象数量级。

**误区二：LOD切换距离越远越好**
将LOD0到LOD1的切换距离设置得很远，认为这样可以保证画质。实际上，切换距离过远意味着即使对象在屏幕上仅占几十个像素时仍在渲染高精度模型，造成不必要的GPU负担。正确做法是以**屏幕空间占比**为基准，而非世界单位距离，因为透视投影下相同距离的对象在不同视角下屏幕尺寸差异极大。

**误区三：开启遮挡裁剪后室内关卡必然高效**
遮挡裁剪本身有性能开销：硬件遮挡查询（Hardware Occlusion Query）每帧需要向GPU发送几何查询并等待结果，若关卡中可遮挡对象较少（如开阔的户外场景），查询本身的开销可能超过裁剪所节省的渲染时间。对于植被密集的开放世界，Cull Distance Volume与LOD的组合往往比遮挡裁剪更高效。

---

## 知识关联

关卡优化依赖**关卡性能分析**提供的数据入口：GPU帧时间、Draw Call计数、内存预算报告直接指导优化策略的优先级排列，若跳过分析阶段盲目优化，可能将时间消耗在非瓶颈环节上。

完成关卡优化设置后，所有LOD配置、静态合批标记、预计算可见性数据都需要进入**关卡构建管线**进行最终Build——预计算可见性的构建、光照贴图烘焙和导航网格生成都在构建阶段执行，优化参数的修改必须触发重新构建才能生效。因此关卡优化与构建管线之间存在严格的数据依赖关系：在构建前频繁修改Precomputed Visibility Volume的格
