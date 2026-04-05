---
id: "cook-automation"
concept: "烘焙自动化"
domain: "game-engine"
subdomain: "editor-extension"
subdomain_name: "编辑器扩展"
difficulty: 3
is_milestone: false
tags: ["构建"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 烘焙自动化

## 概述

烘焙自动化（Bake Automation）是指在游戏引擎编辑器扩展体系中，通过脚本或命令行接口驱动光照贴图、导航网格、遮挡剔除体积等预计算数据的批量生成过程，无需人工在编辑器 GUI 中逐一点击"Bake"按钮。其核心价值在于将原本耗时数小时甚至数十小时的烘焙任务嵌入 CI/CD 流水线，使每次代码或美术资产提交都能触发可验证的构建结果。

烘焙自动化的实践雏形可追溯至 2012 年前后 Unity 引入命令行批处理模式（`-batchmode -quit`），允许通过静态方法 `[InitializeOnLoad]` 或 `BuildPipeline.BuildPlayer` 系列 API 在无头进程中执行资产处理。Unreal Engine 则在 4.x 时代通过 UnrealBuildTool 与 AutomationTool（`RunUAT.bat`）提供了等价能力，其中 `BuildCookRun` 命令可在单条指令内完成编译、Cook（即烘焙资产）和打包三个阶段。

在大型项目中，一个场景的光照烘焙可能涉及数百个光照贴图 Texel，手动管理极易因遗漏重烘导致线上版本与本地预览不一致。烘焙自动化通过强制将烘焙结果纳入版本控制比对，从根本上消除"在我机器上是好的"类问题。

---

## 核心原理

### 命令行无头烘焙接口

Unity 的无头烘焙依赖 `-executeMethod` 参数指定入口静态方法，典型调用形如：

```
Unity.exe -batchmode -quit -projectPath /proj -executeMethod BakeTools.BakeAll
```

在 `BakeTools.BakeAll` 方法内部，调用 `Lightmapping.BakeAsync()` 或同步版本 `Lightmapping.Bake()` 启动光照烘焙，并通过 `Lightmapping.bakeCompleted` 委托监听完成事件后退出。`-batchmode` 标志禁用所有 GPU 渲染窗口，但 GPU Lightmapper（Progressive GPU）仍可访问计算着色器，因此在有显卡的 CI Agent 上速度显著优于 CPU Progressive 模式（通常快 3–10 倍）。

Unreal 侧，`RunUAT BuildCookRun -cook -map=MapName -targetplatform=Win64` 会调用编辑器的 `-run=Cook` 模式，此过程中导航网格数据（Recast NavMesh）、预计算可见集（PVS）等均按地图配置自动生成并序列化到 `.uasset` 中。

### 差异构建（Incremental / Delta Bake）

全量烘焙在场景庞大时代价极高，差异构建通过比较资产哈希决定哪些对象需要重新烘焙。Unity Addressables 结合 Content Update Workflow 可生成 `addressables_content_state.bin`，其中记录了每个资产组的内容哈希；若某组哈希未变化，则跳过该组的烘焙与打包。

在自定义编辑器工具层面，差异构建的典型实现步骤为：

1. 在烘焙前对所有参与烘焙的 Mesh Renderer、Light 组件和 Lightmap Settings 序列化为 JSON 快照，计算 SHA-256 哈希值。
2. 与上次成功烘焙保存的哈希文件比对；若哈希相同，则跳过该场景并复用缓存的 `.exr` 光照贴图文件。
3. 仅对哈希变化的场景执行 `Lightmapping.Bake()`，完成后更新哈希文件并提交到构建产物存储（Artifact Storage）。

差异构建在包含 20 个以上独立场景的项目中可将平均 CI 烘焙时间从 4 小时压缩至 30–45 分钟。

### CI 集成与构建流水线设计

将烘焙任务接入 Jenkins、GitHub Actions 或 TeamCity 时，需注意以下三个 Unity/Unreal 特有的陷阱：

- **许可证激活**：`-batchmode` 下仍需有效的 Unity 序列号或浮动许可证服务器；可通过 Unity 官方提供的 `Unity.Licensing.Client` CLI 在 Agent 启动阶段完成激活，并在流水线结束后调用 `-returnlicense` 释放。
- **日志解析与错误检测**：Unity 批处理模式将所有错误输出到 `Editor.log` 而非 stderr，CI 脚本必须主动扫描该日志中的 `"Bake failed"` 或 `"Exception"` 关键字并以非零退出码终止流水线。
- **GPU 驱动隔离**：在无显示器的 Linux Agent 上使用 Progressive GPU Lightmapper 需配置虚拟帧缓冲（`Xvfb :99 -screen 0 1280x720x24 &`）并设置环境变量 `DISPLAY=:99`，否则 GPU 上下文初始化失败会静默回退至 CPU 模式，烘焙时间翻倍而无任何警告。

---

## 实际应用

**案例：多场景移动项目的每夜烘焙**

某采用 Unity 2022 LTS 开发的移动 RPG，包含 35 个独立场景，每个场景平均包含 180 个静态 Mesh Renderer。团队在 Jenkins 上配置每夜定时任务（Cron `0 2 * * *`），执行以下流程：

1. 从 Git LFS 拉取最新美术资产。
2. 运行差异哈希检测脚本，识别出当天有改动的 8 个场景。
3. 以 `-batchmode` 启动 Unity，依次对 8 个场景调用 `Lightmapping.Bake()`，使用 Progressive CPU（因 CI Agent 无独立 GPU）。
4. 烘焙完成后，将生成的 `.exr` 光照贴图和 `LightingData.asset` 提交至专用 `lighting` 分支，供主分支通过 git subtree 合并。
5. 若任一场景烘焙失败，Slack Webhook 自动推送包含场景名称和错误摘要的告警消息。

整个流程从原来每周人工烘焙一次（耗时 6 小时以上）压缩为每夜自动完成（平均 1.5 小时），并实现了烘焙结果的完整版本溯源。

---

## 常见误区

**误区一：`-batchmode` 等同于彻底无 GPU 运行**

许多开发者误以为 `-batchmode` 模式下所有 GPU 功能均不可用，因此在 CI 配置中不安装显卡驱动。实际上，`-batchmode` 仅关闭渲染窗口（Display），并不禁用 Compute Shader。Progressive GPU Lightmapper 在正确配置显卡驱动和 `DISPLAY` 环境变量后可在 `-batchmode` 下正常运行，速度通常是 CPU 模式的 5 倍以上。

**误区二：差异构建仅需比较文件修改时间戳**

用文件 `mtime` 做差异检测在 Git 工作流中完全不可靠——`git checkout` 和 `git lfs pull` 会将文件时间戳重置为操作时刻，导致所有资产每次都被判定为"已修改"。正确做法是基于文件内容哈希（SHA-256 或 xxHash）或 Git 对象 SHA-1 进行比较，确保只有内容真正变化的资产才触发重烘焙。

**误区三：烘焙产物不需要纳入版本控制**

部分团队将烘焙产物（`LightingData.asset`、`*.exr` 光照贴图）列入 `.gitignore`，依赖开发者本地烘焙。这导致不同开发者机器上因 CPU/GPU 差异产生像素级不一致的光照贴图，在运行时表现为场景切换时光照闪烁（Lightmap Atlas ID 不匹配）。烘焙产物应通过 Git LFS 统一存储，并与触发该次烘焙的资产提交形成一对一的 Tag 关联。

---

## 知识关联

烘焙自动化以**自动化工具**的基础能力为前提——具体指编辑器脚本 API（如 Unity 的 `AssetDatabase`、`EditorApplication`，Unreal 的 `IAutomationControllerManager`）和命令行参数体系。没有这些 API，`-batchmode` 下就无法以编程方式控制烘焙范围、读取烘焙进度或在失败时返回正确的退出码。

在知识图谱的横向关联上，烘焙自动化与**Addressables 构建自动化**共享"哈希差异比对→增量处理"的设计模式，但烘焙自动化处理的是预计算渲染数据（光照、遮挡、NavMesh），而非运行时加载的游戏资产包。此外，烘焙自动化生成的光照贴图 `.exr` 文件通常体积在 50–200 MB 之间，对 CI Agent 的磁盘 I/O 和 Git LFS 带宽有具体的基础设施要求，在设计流水线时需与 DevOps 团队就 Artifact Storage 策略（保留最近 N 次构建或按 Tag 保留）达成明确约定。