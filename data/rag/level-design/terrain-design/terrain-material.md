---
id: "terrain-material"
concept: "地形材质"
domain: "level-design"
subdomain: "terrain-design"
subdomain_name: "地形设计"
difficulty: 2
is_milestone: false
tags: ["材质"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 地形材质

## 概述

地形材质是关卡设计中专门用于地形网格表面着色与渲染的技术体系，其核心特征是通过**多层材质叠加混合**来模拟真实地表的复杂过渡——例如草地与泥土之间的自然渐变、岩石与雪地的交界地带。与普通静态模型的材质不同，地形材质需要在数百米乃至数公里的地形范围内保持纹理分辨率的合理性，同时支持设计师在编辑器中随时用"绘制笔刷"修改地表外观。

Splatmap（溅射图，亦称权重贴图）技术是地形材质的实现基础，最早在2000年代初期的游戏引擎（如Valve的Hammer编辑器和早期版本的Unity Terrain系统）中被广泛采用。它的本质是用一张RGBA格式的灰度贴图存储最多4层（或8层，通过多张Splatmap扩展）材质在地形每个像素位置的混合权重。这种方案极大地降低了地形纹理的存储成本，同时给美术人员提供了直观的绘制工作流。

了解地形材质的工作机制对关卡设计师至关重要，因为错误的材质分层顺序或Splatmap分辨率不足都会直接导致地形出现可见的"材质方块化"瑕疵，影响玩家的沉浸感。此外，材质层数的控制直接影响Draw Call数量，进而影响游戏的运行时帧率。

---

## 核心原理

### Splatmap 的数据结构

一张标准Splatmap是一张与地形高度图分辨率相同（常见规格为512×512、1024×1024、2048×2048像素）的RGBA贴图。其中R、G、B、A四个通道各自对应一层地形材质的**混合权重值**，取值范围为0.0到1.0。四个通道在同一像素点的权重之和必须等于1，用公式表示为：

> **R + G + B + A = 1.0**（对每个texel成立）

若需要超过4层材质，则额外生成第二张Splatmap（记录第5~8层），以此类推。Unity引擎在每增加4层材质时会额外增加一个Pass渲染，直接带来额外的Draw Call开销，这是控制材质层数不宜超过8层的实际工程原因。

### 多层材质混合的着色器逻辑

在着色器中，最终输出颜色由各层材质的Albedo（反照率纹理）与对应Splatmap通道权重相乘后求和得出：

> **Output = Layer0 × R + Layer1 × G + Layer2 × B + Layer3 × A**

法线贴图（Normal Map）、粗糙度（Roughness）等PBR属性同样遵循此加权求和逻辑。一个常见的性能优化技巧是对视野远处的地形强制将权重小于0.05的材质层权重归零，从而在远景着色器中跳过该层的纹理采样，减少GPU指令数。

### 纹理平铺与宏纹理叠加

由于地形面积庞大，单层材质纹理通常以较高的平铺频率（Tiling Rate）重复铺设（如每4米重复一次），否则单张纹理会被拉伸至模糊。但高平铺率会产生明显的重复感，因此设计师通常在地形材质系统中叠加一张低平铺率（如每64米一次）的**宏纹理（Macro Texture）**作为颜色变化层，用乘法混合（Multiply Blend）打破高频纹理的单调重复感。Unreal Engine 5的Landscape材质系统内置了"Landscape Layer Blend"节点，直接支持这种宏纹理叠加工作流。

---

## 实际应用

**Unity Terrain 材质绘制流程**：在Unity的Terrain Inspector中，设计师通过"Paint Texture"工具选择预定义的Terrain Layer（包含Albedo、Normal、Mask贴图及Tiling参数），用圆形笔刷在地形上绘制。每次笔刷操作实际上是在修改Splatmap对应通道的像素值。建议将最基础的底层材质（如裸土）放在第0层（R通道），因为Unity在第0层权重处理上有优化路径。

**Unreal Engine 5 的 Landscape 系统**：UE5允许在单个Landscape Material中通过"Layer Blend"节点堆叠任意数量的材质层，并支持基于高度的自动混合（Height-Based Blend）——例如设定低于海拔200米自动增加沙地权重，配合手绘Splatmap使用，大幅减少设计师的手工绘制工作量。

**《塞尔达传说：旷野之息》地形案例**：任天堂公开的GDC 2017演讲中提到，该游戏地形采用了基于高度与坡度的程序化材质分配：坡度超过45°的区域自动增加岩石材质权重，这正是通过在运行时动态修改Splatmap权重实现的，而非依赖全部手绘。

---

## 常见误区

**误区一：Splatmap分辨率越高越好**

Splatmap的分辨率并非越高越好。一张4096×4096的Splatmap在GPU显存中占用64MB（RGBA 8bit），而地形的材质细节瓶颈往往来自各层材质本身的纹理分辨率，而非Splatmap。对于1km×1km的地形，1024×1024的Splatmap即可在每米约1像素的密度下提供足够的材质区域分辨率；盲目提升Splatmap分辨率只会浪费显存而看不出视觉差异。

**误区二：材质层权重可以任意叠加超过1.0**

部分初学者误以为增加权重值可以"加强"某层材质的表现，但Splatmap的设计要求所有层权重之和严格等于1.0。引擎在写入Splatmap时会自动对权重进行归一化处理（Normalize），因此在同一位置同时刷高两层材质的权重，实际结果是两层材质按比例混合，而非叠加增强。

**误区三：地形材质层数越多细节越丰富**

每新增4层材质必然增加一个额外渲染Pass。在移动平台上，超过4层材质（即超过1张Splatmap）的地形在中低端设备上帧率下降可达15%~30%。关卡设计师应优先通过宏纹理、法线贴图细节和顶点颜色变化来丰富视觉层次，而非无节制叠加材质层。

---

## 知识关联

学习地形材质之前，需要掌握**地形设计概述**中的地形高度图概念——Splatmap的分辨率规格与高度图保持一致，理解高度图的像素-世界坐标映射关系有助于正确设定Splatmap密度。

地形材质与**地形高度雕刻**关系密切：坡度数据可从高度图实时计算得出，UE5的Landscape系统正是利用这一数据驱动基于坡度的自动材质权重分配，让悬崖面自动呈现岩石材质，减少手绘工作量。

在掌握Splatmap的基本工作原理后，进阶方向包括**程序化地形材质生成**（如基于World Machine或Houdini的离线Splatmap烘焙流程）以及**虚拟纹理（Virtual Texture）**技术——后者彻底改变了Splatmap的存储与流式加载方式，是当代AAA地形系统的标准做法。
