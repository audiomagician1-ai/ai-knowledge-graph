---
id: "ue5-pak-system"
concept: "Pak文件系统"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 2
is_milestone: false
tags: ["资源"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Pak文件系统

## 概述

Pak文件系统是Unreal Engine用于将游戏资产打包成单一归档文件的核心机制，其文件扩展名为`.pak`。本质上，一个`.pak`文件是一个只读的虚拟文件系统容器，它将数以千计的独立`.uasset`、`.umap`等资产文件压缩并整合为一个二进制包，游戏运行时通过挂载（Mount）操作将其映射到虚拟路径`/Game/`下，无需解压即可随机访问其中任意文件。

Pak格式最早在UE3时代以类似形式出现，在UE4中被正式确立为标准发行打包方式，并延续至UE5。在UE5的项目中，使用`Project Launcher`或命令行工具`UnrealPak.exe`执行Cook + Package流程后，引擎会将所有Cooked资产生成一个或多个`.pak`文件，通常位于`Saved/StagedBuilds/[Platform]/[ProjectName]/Content/Paks/`目录下。

Pak系统的意义不仅在于减少发行包中的文件数量（避免操作系统文件句柄耗尽问题），更在于它支撑了DLC分发和热更新两大关键功能。通过在基础包之外独立生成补丁Pak，开发团队可以只向用户推送变更内容，而无需重新下载整个游戏包体。

## 核心原理

### Pak文件的内部结构

一个`.pak`文件由三部分组成：**文件数据区**、**索引区**和**尾部信息（Footer）**。Footer固定占据文件末尾的53字节（在启用签名验证后会有所扩展），其中记录了魔数（Magic Number：`0x5A6F12E1`）、版本号、索引区的偏移量和SHA1哈希值。引擎在挂载Pak时首先读取这个Footer以定位索引区，再通过索引区找到每个资产在数据区中的精确字节偏移，从而实现O(1)时间复杂度的随机访问。

索引区存储了每个文件的路径、压缩算法、压缩块信息、数据偏移量和大小等元数据。UE5默认使用Zlib或Oodle压缩算法，Oodle是Epic从UE4.23版本开始引入的高性能商业压缩库，在压缩率和解压速度上均优于Zlib，是主机和PC平台的推荐选项。

### 挂载优先级与覆盖机制

Pak系统通过挂载优先级（Mount Priority，一个整数值）来解决多个Pak之间的文件覆盖问题。当两个Pak包含路径相同的文件时，优先级数值**更高**的Pak中的版本生效。基础游戏Pak的默认优先级为`4`，DLC Pak通常设为`5`以上，热更新补丁Pak则设为更高值（如`10`），从而自动覆盖旧版本资产，无需卸载原始Pak。

在C++层，挂载操作通过`FPakPlatformFile::Mount()`函数完成，也可通过蓝图调用`Mount Pak File`节点实现。引擎启动时会自动扫描并挂载位于特定目录下的所有Pak文件，开发者也可以在运行时动态挂载从网络下载的补丁Pak。

### 加密与签名

UE5的Pak系统内置了AES-256加密和RSA签名两项安全机制。在`Project Settings > Packaging`中配置加密密钥后，打包工具会用AES-256加密Pak文件的索引区或全部内容，并用2048位RSA私钥对数据块进行签名。游戏运行时，引擎用硬编码在可执行文件中的公钥验证签名，防止第三方修改Pak内容。注意加密密钥必须在打包前通过`crypto.json`正确配置，否则加密后的Pak将无法被引擎识别。

## 实际应用

**DLC分发流程**：开发者在内容目录中新建`DLC_Chapter2`文件夹，将DLC资产放入其中，然后使用`UnrealPak.exe`命令仅对该目录执行打包：
```
UnrealPak.exe DLC_Chapter2.pak -Create=filelist.txt -compress
```
生成的`DLC_Chapter2.pak`可上传至CDN，客户端下载后放置到Paks目录，重启游戏或通过代码动态挂载即可访问DLC内容，基础包完全不受影响。

**热更新补丁**：使用`UnrealPak.exe`的`-diff`参数对比新旧版本的Pak，提取差异文件生成增量补丁包。补丁包文件名通常遵循`ProjectName-WindowsNoEditor_P.pak`这一命名约定（末尾的`_P`是约定俗成的补丁标识），引擎会自动赋予其更高的挂载优先级。

**移动平台分包**：Android平台的Google Play要求APK大小不超过100MB，开发者通过将资产分散到多个Pak文件（如`Pak0.pak`存放基础资源，`Pak1.pak`存放高清贴图）来实现按需下载，首次安装只需下载基础Pak即可启动游戏。

## 常见误区

**误区一：认为Pak文件可以在运行时被修改**。`.pak`文件被设计为完全只读的归档格式，引擎不提供任何向已挂载Pak中写入数据的接口。游戏运行时产生的存档、配置等可写数据必须存储在`SavedDir`（对应`FPaths::ProjectSavedDir()`）下的普通文件系统中，而非Pak内。试图将Pak用作运行时数据库是架构设计错误。

**误区二：认为补丁Pak会替换原始Pak中的物理文件**。优先级覆盖机制是纯粹的虚拟文件系统层面的逻辑，原始Pak的字节内容从不被修改。两个Pak同时保留在磁盘上，引擎只是在内存索引中记录"此路径优先读取哪个Pak的哪个偏移"。这意味着若不清理旧Pak，磁盘上会同时存在新旧两个版本的资产数据，导致磁盘占用持续增长。

**误区三：Editor模式下测试热更新行为**。在Editor中运行（PIE模式）时，引擎绕过Pak系统直接读取`Content/`目录下的原始`.uasset`文件，挂载逻辑完全不参与。只有在Standalone或打包后的Development/Shipping版本中，Pak系统才真正生效，因此热更新逻辑必须在实际打包版本中验证。

## 知识关联

**前置知识**：理解UE5构建系统（特别是Cook流程）是掌握Pak文件系统的必要前提。Cook过程将平台无关的`.uasset`转换为目标平台的二进制格式，这些Cooked资产才是最终被打入Pak的内容，跳过Cook直接打Pak是无效操作。

**后续知识**：Pak文件系统是UE5资源管理概述的物理层基础。理解了Pak的挂载机制和虚拟路径映射之后，才能进一步学习Asset Manager如何跨Pak追踪和异步加载资产、以及`Primary Asset`的注册与发现机制如何在多Pak环境下正确工作。此外，Chunk分配系统（在`Project Settings > Packaging`中配置Asset Chunk ID）直接决定了哪些资产被打入哪个Pak文件，是连接内容组织策略与物理Pak结构的桥梁。
