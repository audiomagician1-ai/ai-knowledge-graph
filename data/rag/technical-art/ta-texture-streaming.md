---
id: "ta-texture-streaming"
concept: "纹理流送"
domain: "technical-art"
subdomain: "memory-budget"
subdomain_name: "内存与预算"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 纹理流送

## 概述

纹理流送（Texture Streaming）是一种按需动态加载纹理Mip层级的显存管理技术，其核心思想是：不将一张纹理的所有Mip层级同时驻留于GPU显存，而是根据摄像机距离、屏幕投影面积等实时参数，只加载当前帧实际需要的Mip层级。这项技术的现代实现以**虚拟纹理流送（Virtual Texture Streaming，VTS）**为代表，Unreal Engine 4.23起将其作为可选渲染特性正式引入，DirectX 11.2的Tiled Resources规范（亦称D3D11.2 Tier 2 Tiled Resources，2013年随Windows 8.1发布）也对底层硬件提供了原生支持。

纹理流送的出现直接源于分辨率军备竞赛带来的显存压力。一张4096×4096的RGBA无压缩纹理占用64MB显存；若改用BC7压缩（压缩比8:1），仍需8MB。当游戏场景同时存在500张此类纹理时，仅纹理一项即可消耗4GB显存，远超过去数代主流GPU的预算上限（GTX 1060仅有6GB VRAM）。纹理流送通过将"完整加载"改为"按需加载"，使可管理的纹理总量远超物理显存容量——Epic官方文档指出，启用Virtual Texture后，场景可寻址的纹理数据量可达物理显存的**数十倍**，例如在8GB显存的机器上管理超过200GB的纹理数据集。

参考文献：《Real-Time Rendering》（Akenine-Möller, Haines, Hoffman, 2018, 4th Edition, CRC Press）第23章对纹理流送的页表机制有系统性论述。

---

## 核心原理

### Mip层级请求计算

纹理流送的决策中枢是**Mip偏差计算（Mip Bias Calculation）**。引擎每帧对场景中每个可见网格的UV投影面积进行估算，得到一个"所需Mip等级"值。其数学基础来自OpenGL规范中对LOD的定义（OpenGL 4.6 Core Specification, Section 8.14），核心公式为：

$$\text{MipLevel} = \log_2\!\left(\frac{\text{TextureResolution}}{\text{ScreenCoveragePixels}}\right) + \text{MipBias}$$

以具体数值说明：一张512×512的纹理在屏幕上投影为32×32像素时，所需Mip层级为 $\log_2(512/32) = \log_2(16) = 4$，即只需加载Mip4（32×32，仅4KB，而Mip0为1MB），节省了约99.6%的显存。`MipBias`可由技术美术通过Unreal的`r.Streaming.MipBias`命令行参数手动偏移，正值强制使用更低精度的Mip（节省显存），负值则强制使用更高精度（提升质量，常用于截图模式）。

此计算结果每帧提交给引擎的**Streaming Manager**，由其维护一个优先级队列，依据"当前所需Mip等级"与"已加载Mip等级"之间的差值异步向磁盘或内存池发起加载/卸载请求。

### 虚拟纹理页表机制

虚拟纹理流送（VTS）引入了类似CPU虚拟内存的**页表（Page Table）**概念，最早由Sean Barrett于2008年在GDC演讲"Sparse Virtual Textures"中系统提出，随后被id Software的MegaTexture技术和Epic的Unreal VT采用。整张虚拟纹理被划分为固定尺寸的**Tile**（Unreal Engine中默认为**128×128像素**，可通过`r.VT.TileSize`调整为64或256），每个Tile对应物理纹理缓存（Physical Texture Cache）中的一个物理页。

GPU着色器不直接采样原始纹理地址，而是通过以下两步间接寻址：

1. **查询间接纹理（Indirection Texture / Page Table Texture）**：这是一张低分辨率纹理，每个像素记录一个Tile的物理缓存坐标（u, v）和当前已加载的Mip层级。对于一张16384×16384的虚拟纹理，间接纹理仅为128×128像素（缩小比例 = 16384/128 = 128），显存开销极小。
2. **采样物理缓存纹理（Physical Cache Texture）**：根据步骤1获得的物理坐标，从Physical Cache中取出实际像素数据。

这一结构实现了**Tile粒度的精确加载**：摄像机只看见一面墙的左半部分时，只需将左半部分对应的Tile加载到物理缓存，右半部分显存占用为零。相比传统流送每次必须加载整个Mip层级，VTS对大尺寸纹理（如4K、8K）的显存节省尤为显著，但代价是每次纹理采样增加了一次间接纹理查找，在移动端等带宽敏感平台需评估是否值得开启。

### 流送池与IO带宽预算

Unreal Engine通过控制台变量 `r.Streaming.PoolSize`（单位：MB）配置全局纹理流送池大小，该数值直接限制流送系统可占用的显存上限。流送池满载时，系统依据**LRU（Least Recently Used）**策略驱逐最久未访问的Mip数据。

IO带宽是另一个关键瓶颈：机械硬盘顺序读取约100–200 MB/s，NVMe SSD可达3000–7000 MB/s（如Samsung 990 Pro标称7450 MB/s读取速度）。当摄像机以高速运动时（如赛车游戏中以300 km/h行驶），每帧需加载的新Tile数量可能超过IO带宽上限，导致低精度Mip在屏幕上可见一段时间再被高精度Mip替换——这正是**纹理弹出（Texture Pop-in）**瑕疵的直接成因。Unreal提供了 `r.Streaming.MaxTempMemoryAllowed`（默认50MB）来限制单帧最大加载量，防止单帧IO峰值卡顿，但同时也延缓了精度恢复速度，技术美术需要根据目标存储介质在两者间权衡。

---

## 关键配置参数与调试命令

在Unreal Engine中，以下控制台变量是调试纹理流送时最常用的工具集：

```console
# 查看当前流送池使用情况（实时统计）
stat streaming

# 强制将所有Mip立即加载到最高精度（用于截图/性能分析基准）
r.Streaming.FullyLoadUsedTextures 1

# 设置流送池大小为2048MB
r.Streaming.PoolSize 2048

# 开启VT调试叠加层，用不同颜色显示各Tile的加载状态
r.VT.Borders 1

# 控制Mip偏移量：+2表示强制降低2级Mip以节省显存
r.Streaming.MipBias 2

# 显示虚拟纹理物理缓存的实时占用可视化
r.VT.Visualize 1
```

在Rider或Visual Studio调试Unreal源码时，`FStreamingManagerTexture::UpdateResourceStreaming()`函数是定位流送决策逻辑的入口，每帧调用一次，内部按优先级处理`FStreamingTexture`结构体数组的加载/卸载请求。

---

## 实际应用案例

**案例1：开放世界地形超大纹理**

《荒野大镖客：救赎2》（Rockstar Games, 2018）的地形系统采用了类Virtual Texture的分层流送方案，将地表反照率、法线、粗糙度分别编码为独立的Tile集合，使得单个地形区块可寻址的纹理数据达到TB级别而无需全部驻留显存。在Unreal Engine的类似场景中，技术美术通常将地形Runtime Virtual Texture（RVT）的物理缓存设置为1024×1024像素（即包含64×64个128px Tile），并将`r.VT.RVT.TileCountBias`设为-1以在内存敏感平台降低缓存占用。

**案例2：移动端纹理流送限制**

iOS/Android平台由于统一内存架构（UMA）的特点，CPU与GPU共享同一物理内存池，通常为4–12GB。Unreal Engine在移动端默认禁用Virtual Texture（因为额外的间接纹理查找在基于Tile的延迟渲染架构（TBDR）上会破坏分块缓存效率），转而依赖传统Mip流送，并将`r.Streaming.PoolSize`限制在256–512MB区间，同时强制最高Mip级别不超过2048×2048以控制峰值显存。

**案例3：过场动画的流送预取**

过场动画中角色特写会突然要求加载角色脸部4K纹理的Mip0，若依赖运行时流送则必然产生Pop-in。标准解决方案是使用Unreal的**流送提示体积（Texture Streaming Volume）**或在Sequencer中提前约0.5秒触发`Streaming Source`标记，令Streaming Manager预判性地在画面切换前完成Mip0的加载，将IO延迟隐藏在剪辑点之后。

---

## 常见误区

**误区1：流送池越大越好**

将`r.Streaming.PoolSize`设置为显存总量的90%会导致其他渲染资源（帧缓冲、深度缓冲、着色器资源等）显存不足，反而引发更频繁的资源驱逐和性能抖动。通常建议流送池不超过可用显存的**60%**，在8GB显卡上约为4800MB。

**误区2：Virtual Texture可以无限扩展纹理数量**

VT的物理缓存大小固定，当同屏可见的不同材质Tile数量超过物理缓存容量时，缓存命中率下降，系统陷入频繁换页（Thrashing）状态，GPU采样延迟急剧增加。Unreal建议单场景同时可见的VT材质数量不超过**物理缓存Tile数量的70%**，并通过`r.VT.MaxUploadsPerFrame`（默认32）限制每帧最大Tile上传数以避免带宽峰值。

**误区3：Mip流送对所有纹理类型均适用**

UI纹理、渲染目标（Render Target）和动态生成的程序化纹理默认不参与流送系统，强制对其启用流送会导致采样结果不稳定（因为引擎可能在使用过程中卸载其Mip数据）。在Unreal中，这类纹理应在资产设置中将**"Never Stream"**选项勾选为True。

---

## 知识关联

**前置概念——Mipmap策略**：理解纹理流送的前提是掌握Mipmap的生成方式（通常为Box Filter下采样）和存储格式（每级面积为上一级的1/4，完整Mipmap链总存储量约为原始纹理的**4/3倍**）。Mip流送的本质是选择性地将Mipmap链中的某一段区间加载到显存，而非全链加载。

**后续概念——加载优化**：纹理流送解决了"加载什么"的问题，而加载优化（Asset Streaming Optimization）进一步解决"何时加载"和"以何种顺序加载"的问题，涉及异步IO队列排优先级、关卡流送（Level Streaming）与纹理流送的协同调度，以及PS5/Xbox Series X的Velocity Architecture对SSD直通GPU带宽（5.5 GB/s原始 / 8-9 GB/s压缩）的新型流送范式。

**横向关联——GPU内存管理**：Vulkan的**Sparse Resource**（VkSparseImage）和DirectX 12的**Reserved Resource**提供了硬件级的稀疏纹理绑定支持，是VTS在现代图形API下的底层实现基础，允许将虚拟纹理地址空间中的特定页映射到或解除映射自物理显存，绕过传统纹理上传的整块搬运限制。