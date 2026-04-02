---
id: "build-pipeline-ld"
concept: "关卡构建管线"
domain: "level-design"
subdomain: "level-editor"
subdomain_name: "关卡编辑器"
difficulty: 3
is_milestone: false
tags: ["管线"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.393
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 关卡构建管线

## 概述

关卡构建管线（Level Build Pipeline）是指将关卡从可编辑的原始状态转换为可供玩家运行的最终发布状态的完整自动化流程，涵盖资产依赖收集、光照烘焙计算和最终打包压缩三个主要阶段。不同于实时预览中所见的编辑器状态，构建管线的输出是经过静态优化、去冗余处理后的二进制资产集合。

关卡构建管线的概念随着3D游戏规模的扩大而逐渐成形。早期如id Software在开发Quake（1996年）时，便已将BSP编译、光照计算与地图打包分离为独立步骤，形成了现代构建管线的雏形。如今在Unreal Engine 5和Unity等主流引擎中，构建管线已高度集成，但其底层逻辑依然遵循"依赖解析→计算烘焙→打包输出"的三段式结构。

理解关卡构建管线对于任何需要发布正式版本的项目至关重要。一次失败的构建往往不是因为关卡设计本身存在问题，而是因为资产引用路径断裂、光照图分辨率超出平台限制，或打包配置遗漏了必要的流送层。掌握管线的每个环节，可以将原本数小时的排错时间压缩到分钟级。

---

## 核心原理

### 资产依赖管理

资产依赖管理是构建管线的第一步，其核心任务是构建一张**依赖有向无环图（Dependency DAG）**，枚举关卡文件（`.umap` / `.unity` / `.vmf`）直接或间接引用的所有资产。在Unreal Engine中，这一过程由`AssetRegistry`模块负责，它通过扫描`.uasset`文件头部的`ImportTable`来还原完整依赖链，而非递归读取资产内容本体。

依赖管理中最常见的陷阱是**软引用与硬引用的混淆**。硬引用（Hard Reference）会导致被引用资产在关卡加载时同步载入内存；软引用（Soft Reference / Lazy Reference）则只保存路径字符串，在运行时按需异步加载。若将应软引用的大型音频资产错误地设置为硬引用，会导致关卡首次加载时间膨胀，且该问题仅在完整构建后才能通过内存分析工具发现，编辑器模式下往往不易察觉。

构建系统在依赖解析完成后会生成一份**Asset Manifest文件**，记录本次构建涉及的所有资产的GUID、版本哈希和目标平台标记。增量构建（Incremental Build）正是依赖这份清单比对上次构建结果，跳过未修改资产的重新处理，可将大型项目的二次构建时间缩短60%至80%。

### 光照烘焙阶段

光照烘焙将实时光照计算的结果预先存储为**Lightmap纹理**，以牺牲动态灵活性换取运行时的渲染性能。在Unreal Engine的Lightmass系统中，烘焙过程通过蒙特卡洛路径追踪计算间接光照，结果以每Texel一条辐射度采样的方式写入UV2通道对应的光照图集。

光照烘焙质量由**光照图分辨率（Lightmap Resolution）**和**质量预设（Quality Preset）**共同决定。Lightmass的生产级别（Production Quality）相比预览级别（Preview Quality），间接光照采样数从默认的64次提升至512次，导致烘焙时间差距可达8倍以上。关卡中每个静态网格体的`Lightmap Resolution`属性需单独配置：近景道具通常设为64×64或128×128，大型建筑外墙可设为256×256或512×512，超出512×512的单体光照图会触发引擎警告，原因是这将导致光照图集打包失败或产生大量空白填充。

光照烘焙的另一关键产物是**Distance Field Shadow Map**和**Volumetric Lightmap**。前者为动态物体提供接触阴影，后者则为可移动Actor在烘焙场景中提供准确的环境光遮蔽（AO）数据，两者均在打包时一并写入关卡的`.umap`共生文件中。

### 打包与平台适配

打包（Packaging/Cooking）阶段将编辑器格式资产转换为目标平台的运行时格式。以纹理为例，PC平台使用DXT1/BC1（不透明纹理，1:8压缩比）或DXT5/BC3（含Alpha通道，1:4压缩比），iOS使用ASTC，Android则同时需要ASTC和ETC2格式以兼容不同GPU型号。关卡构建系统的Cook步骤会根据目标平台描述文件（Target Platform Profile）自动选择压缩格式并重新生成纹理Mip链。

打包配置中另一个直接影响关卡可玩性的设置是**Streaming Chunk分配**。在Unreal Engine的数据层（Data Layers）或传统的关卡流送（Level Streaming）框架下，每个子关卡可被分配到不同的Pak Chunk ID。Chunk 0是默认的启动必需包，如果将大量关卡资产误分配至Chunk 0，则会导致游戏初始安装包体积异常膨胀，在移动平台尤为致命。正确的做法是仅将主菜单和首个可玩关卡的资产保留在Chunk 0，其余内容按关卡章节分配至Chunk 1、Chunk 2等后续包中。

---

## 实际应用

**场景：Open World关卡首次发布构建**

一个典型的开放世界关卡构建流程可分为以下步骤：

1. **依赖扫描**：运行`AssetAudit`工具，输出关卡引用的3000+资产清单，确认无断链引用（Missing Reference）。
2. **光照烘焙**：将World Partition分区拆分为若干Tile分别提交Lightmass分布式农场（Swarm Agent），总耗时约4至8小时（取决于场景规模）。
3. **Cook**：在`Project Launcher`中选择目标平台（如PS5），执行Cook-On-The-Fly或完整Cook，期间引擎会针对每个引用资产调用对应的`AssetCooker`。
4. **打包验证**：构建完成后运行`PakExplorer`工具检查各Chunk内容分布，核对光照图集总大小是否超出平台显存预算（通常PS5光照图预算上限约512MB）。

---

## 常见误区

**误区一：编辑器中"效果正常"等于构建后效果正常**

编辑器使用Preview光照或动态全局光照（Lumen）预览，而构建后的关卡使用烘焙光照图。若关卡设计师在编辑器中调整了静态光源强度但未重新烘焙，构建包中的光照图将与编辑器所见完全不同。规避方法是在关键里程碑前强制执行一次完整的Production级别烘焙并用独立的Standalone Play测试，而非依赖PIE（Play In Editor）模式。

**误区二：增量构建总是安全的**

增量构建依赖资产哈希比对，但部分引擎层面的全局参数变更（如修改Post Process材质全局混合权重、更换默认物理材质库）不会更新资产哈希，导致增量构建漏掉必要的重新Cook步骤。对于发布候选版本（Release Candidate），应始终执行清理后的完整构建（Clean Build），而非依赖增量结果。

**误区三：光照图分辨率越高越好**

光照图分辨率并非线性提升质量。将静态网格体的光照图分辨率从256提升至512，纹理内存占用增加4倍，但在观察距离超过10米后视觉改善几乎不可察觉。正确的做法是使用`Lightmass Importance Volume`精确控制关键区域的采样密度，而非无差别拉高全局分辨率。

---

## 知识关联

关卡构建管线建立在**关卡优化**工作的成果之上：LOD设置、遮挡剔除体积（Occlusion Volume）和材质复杂度优化均发生在构建之前，如果关卡优化阶段留下过多高面数网格体或过度绘制的半透明层，Cook后的实际运行时开销将无法通过构建管线本身弥补。

构建管线中的Streaming Chunk策略与**关卡流送（Level Streaming）**架构紧密关联，Chunk的划分边界应与流送关卡的加载触发区域对齐，否则会出现资产在逻辑上属于后加载关卡但因Chunk分配失误被强制预加载的情况。

对于使用CI/CD自动化构建的团队，关卡构建管线通常被集成进Jenkins或TeamCity流水线，通过`RunUAT BuildCookRun`命令行接口触发，并将构建日志中的光照图超限警告和断链错误作为流水线阻断条件（Gate Condition），确保每个提交分支均通过构建验证后才能合入主干。