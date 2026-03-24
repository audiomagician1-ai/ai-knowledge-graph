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
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 烘焙自动化

## 概述

烘焙自动化（Bake Automation）是指在游戏引擎编辑器扩展体系中，将光照贴图烘焙、导航网格生成、遮挡剔除体积计算等预计算任务集成到无人值守的构建流水线中的技术体系。与手动在 Unity Editor 或 Unreal Editor 中点击"Bake"按钮不同，烘焙自动化通过命令行参数、脚本 API 或外部进程触发引擎以 headless（无头）模式完成全部预计算工作，并将结果产物（如 `.exr` 光照贴图、`NavMesh.asset`、`OcclusionCullingData.asset`）纳入版本控制或制品仓库。

这一做法最早随 Unity 2017 引入 `-batchmode -executeMethod` 命令行参数体系而在业界普及。Unreal Engine 在 4.14 版本加入了 `BuildLighting` 命令行开关，使大型开放世界关卡能够在农场机器上批量并行烘焙而无需打开编辑器 UI。烘焙自动化的意义在于：一套 100 万面的场景完整光照烘焙可能耗时 4–8 小时，若依赖美术手动触发，极易因忘记烘焙或烘焙版本不匹配导致线上 Bug；而将烘焙纳入 CI/CD 流水线后，每次场景资产变更提交即可自动触发并验证结果。

## 核心原理

### Headless 引擎调用与编辑器脚本

Unity 烘焙自动化的入口是 `Lightmapping.BakeAsync()` 或同步版本 `Lightmapping.Bake()`，需在继承自 `Editor` 命名空间的静态方法中调用，并通过以下命令行启动：

```
Unity.exe -quit -batchmode -projectPath /path/to/project \
          -executeMethod BakeTools.AutoBake \
          -logFile build.log
```

`-quit` 标志确保烘焙完成后进程以退出码 0 退出，CI 系统（Jenkins、GitLab CI 或 GitHub Actions）可据此判断成功与否。Unreal 对应的命令为：

```
UnrealEditor-Cmd.exe MyProject.uproject \
    -run=ResavePackages -lighting -buildlighting \
    MapName -allowcommandletrendering
```

关键点在于这两套 API 都会绕过 GUI 渲染循环，仅执行预计算内核，因此可在无 GPU 显示输出的服务器节点上运行（需驱动支持或使用虚拟帧缓冲）。

### CI 集成与产物管理

将烘焙嵌入 CI 流水线需要解决三个工程问题：触发策略、产物存储和失败通知。触发策略通常采用路径过滤——只有当 `Assets/Scenes/` 或 `Content/Levels/` 目录下的文件发生变更时才触发烘焙 Job，否则复用缓存产物。以 GitLab CI 为例：

```yaml
bake_lightmaps:
  rules:
    - changes:
        - "Assets/Scenes/**/*"
        - "Assets/Lighting/**/*"
  script:
    - ./unity_bake.sh
  artifacts:
    paths:
      - Assets/Scenes/**/*.exr
      - Assets/Scenes/**/*.asset
    expire_in: 30 days
```

烘焙产物体积通常在数百 MB 至数 GB，直接存入 Git 会导致仓库膨胀，因此业界惯例是将产物上传至 Git LFS 或专用制品服务器（Artifactory、AWS S3），并在 CI 配置中记录产物指纹（SHA-256）以供后续构建步骤拉取。

### 差异构建（Incremental / Delta Bake）

差异构建是烘焙自动化中最能节省成本的技术。其核心思路是：在全量烘焙前，对比当前提交与上一次烘焙成功提交之间的场景文件差异，仅重新烘焙受影响的区域或子场景。

Unity 的多场景烘焙 API 支持按 Scene 粒度单独调用 `Lightmapping.BakeMultipleScenes(string[] scenePaths)`，因此差异构建脚本只需：

1. 通过 `git diff --name-only HEAD~1 HEAD` 获取变更文件列表；
2. 将变更文件映射到所属 Scene；
3. 仅将这些 Scene 传入 `BakeMultipleScenes`。

Unreal 的 World Partition 系统从 5.0 版本起支持按 Cell 级别的增量光照重建，通过 `-buildlightingonly -MapsOnly=<Level>` 参数锁定单个子关卡。实践中，差异构建可将日常迭代的烘焙时间从 6 小时压缩到 15–30 分钟，但需要维护一份"烘焙清单"记录每个 Scene/Cell 最后一次成功烘焙时对应的 Git commit hash。

## 实际应用

**大型 MMO 项目的夜间烘焙流水线**：某款包含 200 个关卡场景的手机 MMO 采用如下策略——白天美术提交资产，每晚 22:00 由 Jenkins 定时任务拉取主干，执行差异构建脚本，对当日变更的 12–30 个场景重新烘焙，产物上传 S3，第二天早上程序员拉取最新包含烘焙贴图的构建进行集成测试。全量烘焙保留为每周一次，利用 8 核 Xeon 机器并行跑约 11 小时。

**导航网格自动化验证**：除光照外，NavMesh 也是烘焙自动化的重要目标。CI 流水线在每次关卡几何变更后调用 `NavMeshBuilder.BuildNavMeshAsync()`，并通过自定义断言检查生成的 NavMesh 是否覆盖率超过 95%（相对于预定义的可行走面积基准），低于阈值则将 CI Job 标记为失败并通知关卡设计师。

## 常见误区

**误区一：在 batchmode 下直接使用异步 API 不做等待**。`Lightmapping.BakeAsync()` 返回一个协程，在 `-batchmode` 下 Unity 的 `EditorCoroutineUtility` 并不会自动 tick，必须在 `EditorApplication.update` 回调中轮询 `Lightmapping.isRunning` 状态，或改用同步的 `Lightmapping.Bake()`，否则进程会在烘焙完成前就因 `-quit` 标志退出，留下空白的光照贴图文件。

**误区二：将烘焙产物直接提交进 Git 主分支**。光照贴图 `.exr` 文件格式为二进制，单张可达 64MB，200 个场景意味着仓库每次全量烘焙增加数 GB 历史记录。正确做法是配置 `.gitattributes` 将 `*.exr` 标记为 Git LFS 指针对象，或完全不提交产物而依赖 CI 制品服务器按 commit hash 检索。

**误区三：差异构建忽略共享光照资产的依赖传播**。若多个场景共用同一个 `LightingSettings.asset` 或 HDR 天空盒贴图，修改该共享资产后差异脚本若只检查 `.unity` 场景文件本身的变更则会漏掉所有依赖这些共享资产的场景。正确实现需要构建一张资产依赖图（可通过 `AssetDatabase.GetDependencies()` 获取），将共享资产的变更扩散到所有依赖它的场景，再计算最终需要重烘的场景集合。

## 知识关联

烘焙自动化建立在**自动化工具**（编辑器脚本、命令行调用、CI 配置文件）的基础能力之上——理解如何编写 Unity 的 `MenuItem` 静态方法或 Unreal 的 `Commandlet` 是实现烘焙入口的前提。进一步地，烘焙自动化与**资产管线自动化**高度协同：光照贴图压缩格式（ETC2 vs ASTC）的选择需在烘焙完成后由纹理导入器自动处理，这要求烘焙脚本与贴图后处理脚本按顺序编排在同一流水线中。差异构建中的依赖图分析技术与**增量构建系统**（如 Gradle、Bazel 的输入哈希追踪机制）原理一致，理解后者有助于设计更健壮的烘焙缓存失效策略。
