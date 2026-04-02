---
id: "se-game-ci"
concept: "游戏CI/CD"
domain: "software-engineering"
subdomain: "ci-cd"
subdomain_name: "CI/CD"
difficulty: 3
is_milestone: true
tags: ["游戏"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 游戏CI/CD

## 概述

游戏CI/CD是将持续集成与持续交付的自动化流程专门适配于游戏引擎（如Unreal Engine 5和Unity）的工程实践，其核心挑战在于游戏项目同时包含代码（C++/C#）和大规模二进制资产（纹理、模型、音频），这使得标准的代码型CI/CD方案无法直接套用。一个典型的AAA手游项目资产总量可达数十GB，传统Git仓库无法高效处理，必须借助Git LFS或Perforce等大文件存储方案配合构建系统。

游戏CI/CD实践在2015年前后随着Unity Cloud Build等托管服务的出现逐渐普及，Epic Games则在2019年为UE4/UE5推出了BuildGraph——一个基于XML的任务图执行系统，专为虚幻引擎的多平台构建设计。在此之前，大型游戏工作室通常依赖自研的批处理脚本完成打包，缺乏标准化流程，构建失败难以追溯。

游戏CI/CD的重要性体现在多平台发布的复杂性上：同一款游戏可能需要同时输出PC（Windows/macOS）、主机（PS5/Xbox Series X）、移动端（iOS/Android）共五到六个构建目标，且各平台有各自的签名证书、SDK版本和包体限制，自动化流水线能将这一过程从数天压缩至数小时。

## 核心原理

### UE5 BuildGraph与UnrealBuildTool

UE5的自动化构建依赖两个核心工具：**UnrealBuildTool（UBT）**负责C++代码的编译和模块依赖管理，**BuildGraph**负责定义跨节点的任务依赖图。BuildGraph的XML脚本中通过`<Node>`标签定义构建节点，`<Agent>`标签分配执行机器，典型命令如下：

```
Engine/Build/BatchFiles/RunUAT.bat BuildGraph -Script=Build/Build.xml -Target="Package Game" -set:Platform=Win64
```

UBT会根据`.uproject`文件中的模块声明生成Makefile等效的构建指令，增量编译时只重新编译变更文件，冷启动全量编译一个中型UE5项目通常需要40到90分钟，而增量编译可压缩至5分钟以内。

### Unity的自动化打包流水线

Unity提供**Unity Build Automation（原Cloud Build）**和本地命令行两种方式。命令行模式通过`-batchmode`标志触发无头构建，配合`-executeMethod`指定静态方法入口：

```
Unity -batchmode -quit -projectPath /path/to/project -executeMethod BuildScript.BuildAndroid -logFile build.log
```

在Unity项目中，`BuildPipeline.BuildPlayer()`是打包的核心API，接收`BuildPlayerOptions`结构体，其中`scenes`字段指定打包场景列表，`target`字段指定`BuildTarget.Android`等平台枚举。Unity的**Addressables**资产管理系统要求在打包前单独执行`AddressableAssetSettings.BuildPlayerContent()`，否则热更新资产不会被正确纳入包体，这是游戏CI/CD中最常见的遗漏点之一。

### 资产处理与缓存策略

游戏CI/CD与普通软件CI/CD的最大差异在于**资产导入缓存**的管理。Unity的Library文件夹存储所有导入后的资产，大小通常是原始资产的1.5到3倍，在CI环境中若每次构建都重新导入，仅此步骤就可能耗时30分钟以上。常见做法是将Library文件夹挂载到缓存卷，通过资产哈希判断是否需要重新导入。UE5的等效机制是**Derived Data Cache（DDC）**，其路径由`Engine.ini`中的`[DerivedDataBackendGraph]`配置，Shared DDC可指向网络共享路径供多台构建机共用，显著降低材质编译和贴图压缩的重复开销。

### GitHub Actions与游戏构建的集成

在GitHub Actions的`workflow.yml`中，游戏构建任务通常需要配置`runs-on: self-hosted`以使用具备GPU和大内存的私有Runner，因为iOS/Android构建需要XCode或Android SDK，以及至少16GB内存应对UE5的链接阶段。构建产物（APK、IPA、.exe安装包）通过`actions/upload-artifact`上传，但应注意GitHub Actions的免费层对Artifact存储有500MB限制，游戏包体动辄数百MB，需要配置外部存储如AWS S3或阿里云OSS。

## 实际应用

**手游多渠道打包**：一款Android手游常需要同时生成Google Play版本（AAB格式）和国内各渠道的APK（需内嵌不同渠道号）。在CI流水线中，可通过矩阵策略`matrix: channel: [googleplay, huawei, xiaomi]`并行触发多个Unity命令行进程，每个进程通过`-define:CHANNEL_HUAWEI`等编译宏区分渠道逻辑，最终将所有包体上传至分发平台。

**UE5多平台构建分发**：一个PC+主机同步发布的项目通常在Jenkins或GitHub Actions中配置跨平台Stage：Win64编译在Windows Runner上执行，PS5构建需要在索尼授权的开发机上运行，流水线通过BuildGraph的Agent标签路由任务。构建完成后，包体自动推送至Steam的SteamPipe或主机平台的开发者门户。

**自动化冒烟测试**：游戏CI/CD流水线在打包后通常集成Gameplay Automation测试，UE5可通过Gauntlet测试框架在无头模式下运行游戏并采集帧率、崩溃日志等指标；Unity则通过TestRunner的`PlayMode`测试验证核心逻辑，测试失败会阻断构建并通知钉钉或Slack频道。

## 常见误区

**误区一：直接用标准Git存储所有资产**。游戏二进制资产（PSD、FBX、WAV）单文件可达数百MB，若不启用Git LFS，仓库克隆时间会超过构建时间本身，且Git对二进制文件无法进行增量传输。正确做法是在`.gitattributes`中为`*.psd`、`*.fbx`、`*.uasset`等扩展名配置Git LFS追踪，或对超大型项目迁移到Perforce，将代码与资产分开管理。

**误区二：在CI中对所有提交都触发全量打包**。UE5全量打包单次可耗时2到4小时，若每次代码提交都触发，构建队列会迅速积压。正确策略是分层触发：代码变更仅触发编译和单元测试（约15分钟），合并到`develop`分支才触发增量打包，标签推送（如`v1.2.0-rc1`）才触发全平台发布包构建。

**误区三：忽略代码签名证书的安全存储**。iOS的`.p12`证书和Android的`.keystore`文件若硬编码在仓库中，一旦代码泄露将导致签名私钥外泄。正确做法是使用GitHub Actions Secrets或HashiCorp Vault存储证书Base64编码值，在构建步骤中动态解码写入磁盘，构建完成后立即删除临时文件。

## 知识关联

游戏CI/CD建立在**CI/CD概述**中流水线触发、阶段划分等基础概念之上，但将其中的"构建"阶段替换为游戏引擎特有的UBT/BuildGraph调用，将"测试"阶段扩展为包含帧率采集的Gameplay测试。**GitHub Actions**提供了声明式的工作流语法和矩阵构建能力，是游戏CI/CD最常见的编排平台，但需要通过Self-Hosted Runner突破算力和SDK限制。**资产处理管线**是游戏CI/CD中耗时最长的环节，DDC和Library缓存策略直接决定流水线总时长，与资产处理管线的衔接点在于将`uasset`编译和贴图压缩纳入有向无环图的节点调度中。**GitOps**的版本化配置理念在游戏CI/CD中体现为将BuildGraph XML脚本、`ProjectSettings`、`DefaultEngine.ini`等配置文件全部纳入版本控制，使每一次历史构建都可通过Git commit哈希完整复现。