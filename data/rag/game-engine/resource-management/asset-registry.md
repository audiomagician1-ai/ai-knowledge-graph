---
id: "asset-registry"
concept: "资产注册表"
domain: "game-engine"
subdomain: "resource-management"
subdomain_name: "资源管理"
difficulty: 2
is_milestone: false
tags: ["索引"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 资产注册表

## 概述

资产注册表（Asset Registry）是游戏引擎中负责维护项目内所有资产元数据的全局索引数据库。它并不加载资产的实际内容（如纹理像素、网格顶点），而是记录每个资产的路径、类型、标签、依赖关系等轻量级描述信息，使引擎能够在不触发完整资源加载的前提下查询和管理项目资产。

资产注册表的概念随着项目规模扩大而产生。在早期小型游戏项目中，开发者可以手工管理所有资源路径；但当资产数量超过数千个时，手工维护变得不可行。Unreal Engine 在 UE4 时代（2014年）将 Asset Registry 作为独立子系统引入，以解决大型开放世界项目中数十万资产的索引问题。Unity 的 AssetDatabase 也承担类似职责，在编辑器模式下为所有 `.meta` 文件构建索引。

资产注册表的价值在于将"资产存在性查询"与"资产内容加载"解耦。编辑器的内容浏览器、引用查找工具、烘焙管线等系统都依赖注册表做毫秒级查询，而无需将所有资产加载进内存。

---

## 核心原理

### 元数据存储结构

资产注册表本质上是一张以**资产路径为主键**的哈希表，每条记录称为 Asset Data（资产数据条目）。在 Unreal Engine 中，`FAssetData` 结构包含以下字段：

- `ObjectPath`：完整资产路径，如 `/Game/Characters/Hero/T_Hero_Diffuse`
- `AssetClass`：资产类型名，如 `Texture2D`、`StaticMesh`
- `AssetName`：不含路径的短名称
- `TagsAndValues`：键值对集合，存储自定义元数据（如纹理分辨率 `"TextureSize=2048x2048"`）

注册表将这张哈希表序列化为二进制缓存文件（在 UE 中为 `AssetRegistry.bin`），引擎启动时优先读取缓存，避免逐文件扫描硬盘。

### 依赖图的维护

资产注册表不仅记录单个资产，还维护资产之间的**有向依赖图**。每条依赖边区分类型：

- **Hard Reference（硬引用）**：资产 A 加载时必须同时加载资产 B，例如蓝图直接引用某个材质。
- **Soft Reference（软引用）**：资产 A 仅持有 B 的路径字符串，运行时按需加载。
- **Management Reference**：包管理层面的逻辑归属关系。

依赖图以邻接表形式存储，提供 `GetDependencies()` 和 `GetReferencers()` 两个方向的查询接口，时间复杂度为 O(d)，其中 d 为该资产的直接依赖数量。

### 增量更新与脏标记机制

资产注册表不会在每次文件变化时重建全量索引。当磁盘上某个 `.uasset` 文件被修改时，文件系统监听器（FileSystemWatcher）触发通知，注册表仅对该文件重新解析其头部元数据（Header），更新对应的 `FAssetData` 条目并将其标记为"已更新"。这种增量扫描使得在拥有 200,000+ 资产的项目中，单次增量更新耗时通常在 **10ms 以内**，而全量重建可能需要数分钟。

---

## 实际应用

**内容浏览器过滤搜索**：当开发者在 Unreal Engine 内容浏览器中输入 `class:Texture2D size>1024` 时，查询请求被转发给资产注册表，注册表扫描 `TagsAndValues` 字段完成过滤，整个过程不加载任何纹理内容，仅操作内存中的元数据表。

**烘焙依赖收集**：打包流程启动后，烘焙系统以目标关卡资产为起点，调用资产注册表的 `GetDependencies()` 接口递归遍历硬引用依赖图，收集需要打入包体的完整资产集合。若缺少注册表，烘焙系统必须逐一加载所有资产才能分析依赖，内存开销将增加数十倍。

**运行时瘦身版注册表**：在已发布的游戏中，资产注册表可以以精简形式嵌入发行包，仅保留路径和类型信息，供异步流式加载系统（如 Unreal 的 Chunk 系统）在下载内容包之前预先知晓其中包含哪些资产。

---

## 常见误区

**误区一：资产注册表等同于资源管理器（Resource Manager）**
资产注册表只存储元数据，不控制资产的加载、卸载和引用计数。真正负责内存中资产生命周期的是资源管理器（如 UE 的 `FStreamableManager` 或 Unity 的 `AssetBundle` 加载接口）。注册表告诉你"这个资产存在，它的类型是什么"，但不负责"把这个资产放进内存"。

**误区二：注册表中的依赖信息与运行时实际加载行为完全一致**
注册表的依赖图在编辑器保存资产时静态生成，记录的是**静态引用**。如果代码中使用字符串拼接动态构造资产路径，这条运行时依赖不会出现在注册表中。因此，烘焙阶段依赖注册表做依赖收集时，动态引用的资产会被漏掉，导致运行时出现资产找不到的错误。

**误区三：资产注册表在运行时 Build 中与编辑器 Build 行为相同**
编辑器模式下注册表是动态活跃的，实时监听文件变化。在 Shipping Build 中，注册表以只读的序列化二进制文件形式存在，不再监听任何文件系统事件，也不支持热重载。

---

## 知识关联

学习资产注册表需要先理解**资源管理概述**中资产文件格式（`.uasset` / `.meta`）的基本结构，因为注册表解析的正是这些文件的头部元数据而非完整内容。

掌握资产注册表的索引结构和依赖图表示方式后，可以进入**资源依赖分析**，该主题深入研究如何遍历注册表的依赖图来检测循环依赖、冗余资产和过度引用问题。注册表提供的 `GetReferencers()` 接口是依赖分析工具的直接数据来源。

在**资源性能分析**阶段，注册表的 `TagsAndValues` 中存储的资产属性（如纹理分辨率、网格面数）可被性能分析工具批量读取，无需加载资产本体即可扫描整个项目中不符合性能预算的资产，这是注册表在性能流程中的核心应用场景。