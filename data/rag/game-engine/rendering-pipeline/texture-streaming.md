---
id: "texture-streaming"
concept: "纹理流"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["资源"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
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



# 纹理流

## 概述

纹理流（Texture Streaming）是游戏引擎渲染管线中的一种内存管理技术，其核心思想是**按需加载纹理的不同细节层级（Mipmap）**，而不是将所有纹理以最高分辨率常驻于显存中。玩家当前视角所看到的物体，加载高分辨率纹理；远处或屏幕占比极小的物体，则只保留低分辨率版本，从而将有限的显存（通常4GB到24GB不等）用在刀刃上。

纹理流技术的商业化应用可追溯到2007年前后。虚幻引擎3（Unreal Engine 3）在当时率先将Texture Streaming集成为引擎级别的标准功能，使开发者无需手动管理每张纹理的显存占用。此后，Unity、CryEngine等主流引擎相继引入类似机制。到了虚幻引擎5，更进一步推出了**虚拟纹理（Virtual Texture，VT）**系统，将流式管理的粒度细化到纹理的单个"页面（Page）"级别。

纹理流之所以重要，是因为现代游戏中单个场景的纹理总容量往往高达数十GB，远超任何一代主流显卡的显存上限。没有纹理流，开发者要么被迫压缩纹理质量，要么场景规模受到严重限制。借助纹理流，2023年的《星空》（Starfield）等开放世界游戏才能在8GB显卡上流畅呈现数百平方公里的地貌细节。

---

## 核心原理

### Mipmap与LOD偏差计算

纹理流的基础数据结构是**Mipmap链**：一张2048×2048的基础纹理，会预生成2048→1024→512→256→…→1×1共12个层级，每一级的显存占用约为上一级的1/4。纹理流系统在每帧渲染时，根据物体在屏幕上的投影面积和摄像机距离，计算出所需的**最优Mipmap层级（TexelDensity / ScreenSize Ratio）**：

$$\text{MipLevel} = \log_2\left(\frac{\text{TextureResolution}}{\text{ScreenCoverage} \times \text{ViewportSize}}\right)$$

其中，`ScreenCoverage` 是物体在屏幕上所占的像素比例，`ViewportSize` 是视口分辨率。若计算结果为2.7，则系统会同时保留Mip2和Mip3，并在两者之间进行**三线性过滤（Trilinear Filtering）**插值，避免层级切换产生的画面跳变。

### 异步加载与流式调度

纹理流的加载过程必须**异步执行**，否则每次Mipmap切换都会造成主线程卡顿。引擎通常维护一个**流式请求队列（Streaming Request Queue）**，后台IO线程按优先级从磁盘（或包体）读取对应的Mipmap数据，再通过`DMA（直接内存访问）`传输到显存，整个过程对渲染线程透明。虚幻引擎5的流式系统中，`r.Streaming.MipBias` 是一个关键控制台变量，用于全局偏移Mipmap选择层级——将其设为正值可强制降低纹理质量以节省显存。

优先级策略通常综合考量三个因素：①物体与摄像机的距离；②物体上次可见的时间戳；③纹理在当前帧是否处于摄像机视锥体（Frustum）内。长时间不可见的纹理会被标记为"驱逐候选"，显存紧张时首先被卸载至系统内存或彻底释放。

### 虚拟纹理（Virtual Texture）

虚拟纹理是纹理流的进阶形态，借鉴了操作系统**虚拟内存分页**的思想。整张地形纹理被划分为固定大小（通常128×128或256×256像素）的**物理页面（Physical Page）**，显存中只保留一张固定大小的**物理纹理缓存（Physical Texture Cache）**，例如4096×4096像素。GPU通过查询一张**页表纹理（Page Table Texture）**，将虚拟UV坐标重定向到物理缓存中实际存储的位置。这套机制允许一张逻辑上"无限大"的地形纹理只占用固定显存，是《荒野大镖客：救赎2》等游戏实现超大地图高分辨率地表的关键支撑。

---

## 实际应用

**开放世界地形**：在UE5的Landscape系统中，地形通常使用Runtime Virtual Texture（RVT），地面颜色、法线、粗糙度分别存储在不同的虚拟纹理层。当玩家快速奔跑时，流式系统需要在约0.3秒内完成前方区块的Mipmap升级，否则玩家会看到短暂的模糊地表——俗称"纹理弹出（Texture Pop-in）"。

**影视级资产串流**：《堡垒之夜》第5章采用Nanite配合虚拟纹理，单个角色皮肤纹理逻辑分辨率高达8K，但实际占用显存不超过该角色在屏幕投影面积所需的物理页数，在低端设备上依然能保持稳定帧率。

**控制台内存预算**：PS5和Xbox Series X的显存分别为16GB GDDR6和10GB GDDR6，开发团队会在引擎中设定`TextureStreamingPool`上限（例如保留6GB专用于纹理流），并通过`stat TextureGroup`命令实时监控各类纹理的驻留状态，确保不超预算。

---

## 常见误区

**误区一：提高纹理预算就能消除Texture Pop-in**
显存预算增大只能让更多高分辨率Mipmap常驻，但Pop-in的根本原因在于**磁盘IO速度**跟不上摄像机移动速度。即使显存充裕，若NVMe固态硬盘的读取带宽或引擎的IO调度存在瓶颈，仍会出现低分辨率纹理短暂显示的问题。《赛博朋克2077》在HDD（机械硬盘）和SSD上的纹理弹出频率差异，正是这一原理的直接体现。

**误区二：虚拟纹理总是优于传统Mipmap流**
虚拟纹理的页表查询在Shader中引入了一次**额外的间接纹理采样（Indirect Texture Fetch）**，在Draw Call数量极多的场景下会增加GPU的纹理单元压力。对于面数少、纹理复用率高的室内场景，传统Mipmap流的开销反而更低。UE5文档明确指出，Runtime Virtual Texture更适合**地形和大面积地表混合材质**，而非所有物体类型。

**误区三：Mipmap层级越低（分辨率越高）画质越好**
Mipmap的存在本身是为了**消除远处物体的摩尔纹（Moiré Pattern）**锯齿。强制所有物体使用Mip0（最高分辨率）反而会在远处产生高频闪烁，同时浪费显存带宽。最优画质来自于为每个像素选择**texel:pixel比率接近1:1**的Mipmap层级，而非盲目追求高分辨率。

---

## 知识关联

**前置概念——渲染管线概述**：纹理流工作在渲染管线的光栅化阶段之前。理解顶点着色器输出UV坐标、片元着色器采样纹理的流程，有助于明白为何纹理流系统必须在"Draw Call提交给GPU之前"完成Mipmap的显存驻留，否则GPU在执行片元着色器时会采样到错误层级或产生显存越界。

**拓展方向**：纹理流与**LOD（Level of Detail）网格系统**协同工作——物体切换到低多边形LOD的同时，纹理流系统也会释放该物体对应的高分辨率Mipmap，两套系统共享同一套"距离-质量"曲线参数。此外，Nanite的虚拟几何体技术与虚拟纹理形成概念上的对称：前者对几何细节做按需加载，后者对纹理细节做按需加载，二者共同构成UE5"无限细节"渲染愿景的技术支柱。