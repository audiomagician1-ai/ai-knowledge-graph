---
id: "uasset-format"
concept: "UAsset格式"
domain: "game-engine"
subdomain: "serialization"
subdomain_name: "序列化"
difficulty: 3
is_milestone: false
tags: ["UE5"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# UAsset格式

## 概述

UAsset格式是Unreal Engine 5（及其前身UE4）用于存储游戏资产的专有二进制文件格式，文件扩展名为`.uasset`，其配套的`.uexp`文件用于存储实际的导出对象数据。这种格式将纹理、静态网格、蓝图、材质等各类资产统一编码为结构化的二进制字节流，使引擎能够在运行时高效加载和反序列化资产对象。UAsset格式不是简单的"内容打包"方案，而是与UE对象系统（UObject体系）深度耦合的序列化协议，每个字段的读写顺序都由`FArchive`类及其派生类严格管理。

UAsset格式在UE4时代基本定型，其文件头部的魔数（Magic Number）固定为`0x9E2A83C1`（4字节小端序），这是识别UAsset文件的首要标志。UE5引入了Zen存储（Zen Storage）和IoStore（`ucas`/`utoc`文件），将传统的单文件UAsset批量打包进容器，但单个UAsset文件的内部结构逻辑基本延续了UE4时期的设计。理解UAsset格式对于资产热重载、MOD制作、资产迁移工具开发以及运行时内存布局分析都有直接的实用价值。

## 核心原理

### 文件头（Summary Header）

UAsset文件最开头的区域是`FPackageFileSummary`结构体，包含了整个文件的元数据目录。其核心字段按顺序依次为：魔数（4字节，值`0x9E2A83C1`）、文件版本号`FileVersionUE4`（如UE4.27对应版本号517）、名称表偏移量`NameOffset`、名称表条目数`NameCount`、导入表偏移量`ImportOffset`、导入表条目数`ImportCount`、导出表偏移量`ExportOffset`、导出表条目数`ExportCount`，以及总资产大小`TotalHeaderSize`。引擎在加载任何资产前，必须先完整解析这个Summary，才能定位后续各表的位置。

### 名称表（Name Table）

名称表是UAsset格式的字符串池，存储文件中所有`FName`对象引用的字符串字面量。每条名称记录由一个带长度前缀的UTF-8字符串（或UTF-16，取决于最高位标志）和一个32位哈希值组成。名称表中的每个条目在运行时会被映射为`FNameEntryId`，代码中引用`FName`时只需记录一个整数索引，而非重复存储字符串本身，这大幅压缩了文件体积。例如一个包含100个相同`StaticMesh`字符串引用的文件，在名称表中该字符串只出现一次，其余位置存储其索引值（通常4字节）。

### 导入表与导出表

导入表（`FObjectImport[]`）记录此UAsset依赖的外部对象，每条记录包含：类包名（ClassPackage）、类名（ClassName）、外部对象索引（OuterIndex，负数表示引用其他UAsset）以及对象名称索引。导出表（`FObjectExport[]`）记录此UAsset自身拥有的UObject实例，每条记录包含：序列化大小`SerialSize`（字节数）、序列化偏移量`SerialOffset`、类索引`ClassIndex`（负数指向导入表，正数指向导出表自身）、标志位`ObjectFlags`（如`RF_Public=0x00000001`）等字段。导出表中第一个条目（索引0）通常是资产的"根对象"，即文件所代表的主资产对象。

### 属性序列化（Tagged Property Serialization）

UAsset中导出对象的实际属性数据使用"标记属性序列化"格式存储。每个属性按`(FName tag, int32 size, data)`三元组写入：先写属性名称在名称表中的索引（4字节index + 4字节number），再写属性类型名索引，再写该属性数据的字节长度（允许引擎跳过未知属性），最后写实际数据。属性列表以一个名称索引指向`None`（名称表中的"None"字符串）作为终止符。这种自描述格式使得新版引擎读取旧版资产时，可以安全跳过不认识的属性，而不会导致解析崩溃。

## 实际应用

**资产查看与调试**：工具UAssetGUI和FModel专门解析UAsset格式，通过读取Summary定位名称表、再逐条解析导出表，可以将任意`.uasset`文件的属性树可视化展示。开发者常用这类工具检查打包后资产是否包含预期数据，或比较两个版本资产的属性差异。

**自定义资产迁移**：将资产从一个项目迁移到另一个项目时，导入表中的外部包路径（如`/Game/Characters/Skeleton`）必须在目标项目中有对应资产，否则加载时引擎会报"Failed to find object"错误。迁移工具需要重写导入表中的包路径才能保证依赖链完整。

**运行时Pak加密**：UE5项目发布时，`.uasset`文件通常被打包进`.pak`归档并可选AES-256加密。Pak文件自身有独立的目录结构，但其内部存储的每个条目仍然是完整的UAsset二进制块，解密后可直接按上述格式解析，加密不改变UAsset内部格式。

## 常见误区

**误区一：`.uasset`文件包含完整资产数据**。实际上，从UE4.16开始，引擎默认将导出对象的序列化主体数据（`SerialOffset`指向的字节块）分离到同名的`.uexp`文件中，`.uasset`仅保留Summary和各种表的元数据。只有当项目设置`bSplitAttachmentsPerPackage=false`时，数据才留在`.uasset`里。工具解析时若只读`.uasset`而忽略`.uexp`，会得到空数据或错误偏移。

**误区二：版本号相同即格式兼容**。`FileVersionUE4`和`FileVersionUE5`只是大版本号，引擎还维护一套`FCustomVersionContainer`，存储各子系统（如Niagara、AnimGraph）的私有版本号列表，附加在Summary末尾。同样`FileVersionUE4=517`的两个文件，若自定义版本号不同，其属性数据可能有完全不同的序列化布局，强行用旧代码读新版本的自定义属性会得到错误数据。

**误区三：UAsset文件是跨平台通用的**。引擎在Cook过程中会针对目标平台（PC/PS5/Switch等）将UAsset转换为平台专属的Cooked格式，其中纹理数据以目标GPU压缩格式（如BC7、ASTC）存储，字节序也可能按目标平台调整。Editor中的UAsset（Uncooked）与Cooked UAsset虽然文件扩展名相同，但内部结构和可用属性集存在显著差异。

## 知识关联

UAsset格式的设计直接建立在**二进制序列化**基础之上：`FArchive`的运算符重载机制（`operator<<`）负责将C++结构体字段逐一读写为连续字节，UAsset的每个表项和属性数据块都是`FArchive`序列化的产物。理解`FArchive`的"保存/加载统一接口"模式是读懂UAsset各字段写入顺序的前提。

在工程实践中，UAsset格式与UE的**包系统（Package System）**紧密相连：一个`.uasset`文件对应一个`UPackage`对象，导入/导出表本质上是包间对象引用的序列化表达。此外，UE5的**IoStore格式**（`.ucas`+`.utoc`）是对传统UAsset批量存储的再封装，理解单个UAsset的结构有助于进一步分析IoStore容器的分块（Chunk）寻址逻辑。资产热重载（Hot Reload）机制也依赖于对UAsset Summary中时间戳和哈希字段的实时比对，判断磁盘上的文件是否发生变化。