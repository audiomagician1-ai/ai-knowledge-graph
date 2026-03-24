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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 烘焙自动化

## 概述

烘焙自动化（Bake Automation）是指通过脚本或命令行接口驱动游戏引擎编辑器，在无人值守的状态下批量执行光照贴图烘焙、导航网格生成、遮挡剔除数据预计算等离线计算任务的工程化方案。与手动在编辑器 UI 中点击"Bake"按钮不同，自动化方案将整个烘焙流程封装为可重复执行的脚本步骤，使其能够嵌入持续集成（CI）流水线，在每次代码或美术资产提交后自动触发。

该技术在 2010 年代中期随着 Unity 引入 `BuildPipeline` 和无头（Headless）批处理模式逐渐成熟，同期 Unreal Engine 也提供了 `UAT（UnrealAutomationTool）` 命令行烘焙接口。促成其普及的核心驱动力是大型项目的场景数量膨胀——一款 AAA 游戏可能包含 500 个以上需要独立烘焙光照的场景，纯手工操作的时间成本和人为遗漏风险已无法接受。

烘焙自动化的价值不仅限于节省时间：它为每次资产变更提供可追溯的烘焙结果基线，使质量检验（QA）团队能够通过对比前后帧的光照差异来定位因模型调整引入的漏光或接缝问题，从而将美术修改的回归成本从数天压缩到数小时。

---

## 核心原理

### 无头模式与编辑器命令行参数

烘焙自动化的第一步是以无头（Headless/Batchmode）模式启动编辑器，完全跳过渲染窗口和 UI 初始化。以 Unity 为例，典型的启动命令如下：

```bash
Unity -batchmode -quit -projectPath /path/to/project \
      -executeMethod BakeAutomation.BakeAllScenes \
      -logFile build.log
```

其中 `-batchmode` 禁用图形上下文，`-quit` 在方法执行完毕后自动退出进程，`-executeMethod` 指定入口静态方法。在 Unreal 中对应命令为 `UE4Editor-Cmd.exe ProjectName -run=ResavePackages -buildlighting`，其中 `-buildlighting` 标志会触发 Lightmass 全局光照计算。理解这两个参数的差异是区分 Unity 与 Unreal 烘焙自动化脚本的关键。

### 差异构建（Incremental/Dirty Bake）

全量烘焙在大型项目中耗时可达 8–24 小时，这使得 CI 每次提交触发全量烘焙在工程上不可行。差异构建策略通过比较资产的内容哈希（Content Hash）或修改时间戳，仅重新烘焙自上次成功构建以来发生变化的场景或光照组（Lighting Group）。

实现差异构建的关键数据结构是**烘焙清单（Bake Manifest）**——一个 JSON 或 CSV 文件，记录每个场景的路径、最后成功烘焙的 Git 提交哈希、烘焙耗时与输出文件大小。CI 脚本在启动烘焙前读取此清单，执行 `git diff HEAD~1 HEAD --name-only` 并与清单中的依赖列表做集合交运算，输出"脏场景"列表。只有出现在脏场景列表中的场景才会被送入烘焙队列，这一机制可将日常提交的烘焙时间从数小时缩短至 10–30 分钟。

### CI 集成与产物管理

将烘焙任务接入 Jenkins、GitLab CI 或 GitHub Actions 需要处理三个具体问题：**进程退出码、超时控制和产物上传**。

编辑器批处理模式在脚本抛出未捕获异常时，不一定返回非零退出码，因此需要在自动化脚本中显式调用 `EditorApplication.Exit(1)` 并配合 CI 步骤的 `exit_code` 检查。超时控制通常通过 CI 平台的 `timeout` 字段设置，建议为单场景烘焙设置 `90` 分钟上限，并将日志中的 `Bake failed` 或 `NaN lightmap` 字样作为额外的失败检测条件。

烘焙产物（`.exr` 光照贴图、`LightingData.asset`、NavMesh 数据）体积通常在 500 MB 至 5 GB 之间，不适合直接提交至 Git。主流方案是配合 Git LFS 或专用二进制资产管理服务（Perforce、Artifactory）存储产物，并在清单中记录产物的 SHA-256 校验和，以支持后续版本回滚。

---

## 实际应用

**Unity 项目的场景批量烘焙脚本**是最常见的落地形态。一段典型的 `BakeAutomation.cs` 会调用 `Lightmapping.BakeAsync()` 并注册 `Lightmapping.bakeCompleted` 回调，在回调中将当前场景的烘焙状态（成功/失败）写入 JSON 清单，然后加载下一个待烘焙场景，形成串行烘焙循环。整个脚本入口须标注 `[MenuItem]` 以便在编辑器内调试，同时保留不带 `[MenuItem]` 的纯静态方法供命令行调用。

**Unreal 大型开放世界项目**常将地图拆分为若干 World Partition 单元，每个单元独立烘焙，从而实现并行化。具体做法是在多台 Jenkins Agent 上分发烘焙任务，每台 Agent 负责一个地理区块，最终由主节点合并 `MapBuildData` 包。这种分布式烘焙方案可将原本 20 小时的全图光照烘焙压缩至 3–4 小时（以 8 台 Agent 为例）。

---

## 常见误区

**误区一：认为 `-batchmode` 等同于完整的无渲染环境**。实际上 Unity 的 `-batchmode` 仍然需要 GPU 驱动支持（用于某些基于 GPU 的渲染功能），在纯 CPU 的 Docker 容器中运行烘焙任务往往会因缺少显卡驱动而导致渐进式光照贴图（Progressive Lightmapper）回退到 CPU 模式，速度下降 3–10 倍。正确做法是在 CI 服务器上配置具有 NVIDIA 驱动的宿主机或使用 CUDA 容器镜像。

**误区二：差异构建仅需比较场景文件本身的修改**。烘焙结果实际上依赖场景中引用的所有网格、材质、光照探针配置和渲染设置。若仅检测 `.unity` 文件的变更而忽略被引用资产的变更，修改了一个共用材质的高光参数后场景文件未变，差异构建会错误地跳过重新烘焙，导致产物与实际场景不一致。依赖追踪须基于 `AssetDatabase.GetDependencies()` 递归获取完整依赖图，而非仅检查顶层文件。

**误区三：烘焙超时后直接 kill 进程即可安全恢复**。强制终止正在写入 `LightingData.asset` 的编辑器进程会产生损坏的部分写入文件，下次启动时编辑器可能因读取该损坏文件而崩溃，陷入死循环。自动化脚本应在烘焙开始前备份现有产物路径，超时触发时先删除不完整的输出再退出进程。

---

## 知识关联

**前置知识——自动化工具**：烘焙自动化脚本的编写依赖对编辑器扩展 API（`Editor` 命名空间、`AssetDatabase`、`Lightmapping` 类）的熟悉程度。掌握自定义菜单项、批处理入口方法和编辑器协程这三类编辑器扩展模式是编写稳定烘焙脚本的前提。差异构建中的哈希比较逻辑也复用了资产导入流水线（Asset Import Pipeline）中相同的内容哈希机制，理解资产 GUID 与内容哈希的区别可避免清单设计时的常见错误。

烘焙自动化在项目管线中处于美术资产提交与包体构建（`BuildPipeline.BuildPlayer`）之间的中间层。它产出的光照贴图和导航数据是后续打包步骤的直接输入，因此烘焙任务的稳定性和产物版本管理策略直接影响整个交付流水线的可靠性。将烘焙清单与版本控制系统的提交记录对齐，是实现可追溯性构建（Reproducible Build）的核心手段。
