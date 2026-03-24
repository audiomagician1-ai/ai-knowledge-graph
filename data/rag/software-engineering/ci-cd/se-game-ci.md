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
---
# 游戏CI/CD

## 概述

游戏CI/CD（持续集成/持续交付）是针对游戏引擎（主要是Unreal Engine 5和Unity）构建特殊的自动化流水线，用于自动完成代码编译、资产烘焙（Cook）、平台打包（Package/Build）和分发的全流程。与普通Web应用的CI/CD不同，游戏CI/CD必须处理数十GB的贴图、模型、音频等二进制资产，以及针对PC、主机（PS5/Xbox Series X）、移动端（iOS/Android）等多平台的差异化构建需求。

游戏行业自动化构建的普及约从2015年前后随着Unity Cloud Build和Unreal Automation Tool（UAT）的成熟而加速。传统游戏团队依赖开发者手动在本地执行打包，单次PC+Android+iOS三平台构建可能耗费4-8小时并占用开发者工作站，极大浪费人力。现代游戏CI/CD将这一过程转移到专用构建服务器，使开发者提交代码后自动触发全平台构建并推送到测试设备。

游戏CI/CD的核心价值在于早期发现"构建破坏"（Build Break）。游戏项目中一个错误的材质引用、一段未编译的C++代码，或一个损坏的`.uasset`文件都会导致整个项目无法打包，而这类问题在大型团队中每天可能出现多次。自动化流水线确保每次提交后15-30分钟内即可获得构建状态反馈。

## 核心原理

### Unreal Engine 5的自动化构建工具链

UE5提供了名为**Unreal Automation Tool（UAT）**的命令行工具，其核心可执行文件位于`Engine/Build/BatchFiles/RunUAT.bat`（Windows）或`RunUAT.sh`（macOS/Linux）。执行游戏打包的标准命令格式为：

```
RunUAT.bat BuildCookRun -project="Game.uproject" -platform=Win64 -clientconfig=Shipping -cook -build -stage -pak -archive -archivedirectory="Output/"
```

关键参数说明：`-cook`触发资产烘焙（将编辑器格式资产转换为目标平台格式）、`-pak`将所有烘焙资产打包进`.pak`压缩包、`-clientconfig=Shipping`编译剥除调试符号的发布版本。烘焙阶段通常是整个构建中最耗时的部分，一个中型UE5项目的首次全量烘焙可能需要2-6小时，因此CI/CD中必须配置**派生数据缓存（DDC, Derived Data Cache）**的共享服务器，让增量构建只重新烘焙变化的资产。

### Unity的自动化构建方法

Unity的命令行构建通过`-executeMethod`参数调用项目中的C#静态方法来实现，例如：

```
Unity -batchmode -nographics -projectPath /path/to/project -executeMethod BuildScript.BuildAndroid -logFile build.log -quit
```

`BuildScript.BuildAndroid`是开发者在项目中编写的构建脚本，调用`BuildPipeline.BuildPlayer()`API。Unity CI/CD的特殊挑战是**License激活**：Unity Personal/Pro许可证为浮动授权，在无头（headless）CI服务器上需要通过`Unity -manualLicenseFile`流程预先激活，或使用Unity Build Automation（原Cloud Build）云服务规避本地License管理。Android构建额外需要配置`keystore`签名文件，通常将其加密后存储为CI系统的Secret变量（如GitHub Actions的`secrets.ANDROID_KEYSTORE_BASE64`）。

### 多平台构建矩阵与资产管理

游戏CI/CD流水线通常使用**构建矩阵（Build Matrix）**并行化多平台构建。在GitHub Actions中，一个典型的UE5多平台矩阵配置如下：

```yaml
strategy:
  matrix:
    platform: [Win64, Android, iOS]
    config: [Development, Shipping]
```

这会同时启动6个构建任务。但资产烘焙本身无法简单并行，因为不同平台的纹理压缩格式不同（PC使用BC7/DXT5，Android使用ASTC，iOS也使用ASTC但参数有差异），每个平台需要独立烘焙。为避免重复烘焙Editor格式资产，CI服务器通常将DDC目录挂载为持久化网络存储（如NFS或AWS EFS），烘焙缓存命中率可从0%提升到70-90%，构建时间可缩短50%以上。

## 实际应用

**典型游戏CI/CD工作流**：开发者向`develop`分支推送包含新关卡资产的提交后，GitHub Actions触发流水线：第一步用`dotnet` CLI编译UE5的C++游戏模块（约5-15分钟）；第二步运行`RunUAT BuildCookRun`烘焙并打包Win64 Development版本（增量约20-40分钟）；第三步将`.pak`文件上传至内部测试服务器，并通过Slack Webhook发送附带构建日志链接的通知消息。若任一步骤返回非零退出码，流水线标记失败并@相关提交者。

**移动端签名与分发**：iOS构建在CI中需要将`.p12`证书和`.mobileprovision`配置文件注入macOS Keychain，这通常通过`security import`命令完成。Android APK/AAB构建后可自动上传至Firebase App Distribution供测试人员下载安装，或推送至Google Play内部测试轨道，整个过程通过`fastlane supply`命令完成，无需人工登录Google Play Console。

**构建产物版本管理**：游戏构建产物通常以`GameName_Platform_BranchName_CommitHash_Timestamp`格式命名，如`MyGame_Win64_develop_a3f7b2c_20241125_143022`，并存储于S3或Artifactory，保留最近30个构建版本。这使得QA团队可以精确复现某个历史版本的行为。

## 常见误区

**误区一：将游戏CI/CD等同于普通应用CI/CD，忽视资产烘焙阶段**。许多初次为游戏项目搭建流水线的工程师直接套用Web应用的CI模板，只配置代码编译步骤而跳过资产烘焙。结果是CI报告"构建成功"，但实际生成的可执行文件运行时崩溃，因为游戏运行时需要的`.pak`资产文件从未被正确生成。正确做法是必须在流水线中包含完整的`-cook -pak`步骤。

**误区二：在CI服务器上启用完整的UE5编辑器界面**。UE5的`UnrealEditor.exe`在无显示器的CI服务器上默认会尝试初始化渲染子系统并弹出GUI，导致进程挂起。正确做法是所有CI构建命令必须通过`RunUAT`或添加`-unattended -nullrhi`参数以无头模式运行，`-nullrhi`禁用渲染硬件接口，允许在无GPU的构建机器上执行烘焙。

**误区三：用Git LFS直接在CI中拉取所有游戏资产**。一个中型UE5项目的Git LFS资产可能超过50GB，若每次CI触发都执行`git lfs pull`全量拉取，单次网络传输耗时可能超过实际构建时间。正确方案是维护一台持久化的构建服务器（而非每次从干净镜像启动的临时Runner），使该服务器保持LFS资产的增量同步，或使用Perforce等专为游戏设计的版本控制系统，其`p4 sync`命令天然支持增量文件同步。

## 知识关联

游戏CI/CD以**CI/CD概述**中的流水线阶段概念（触发→构建→测试→部署）为基础框架，但将每个阶段替换为游戏引擎专有工具链：普通CI的`npm run build`对应游戏CI的`RunUAT BuildCookRun`，普通CI的单元测试对应游戏的自动化截图对比测试（UE5的Gauntlet框架或Unity的Graphics Test Framework）。

**GitHub Actions**的矩阵构建（`strategy.matrix`）和加密Secret机制在游戏CI/CD中被密集使用：矩阵用于并行多平台构建，Secret用于存储代码签名证书、商店API密钥和DDC服务器地址。GitHub Actions的`self-hosted runner`是游戏CI的首选部署方式，因为游戏构建需要大量本地存储（DDC可能占用100GB+）和高性能CPU，托管Runner的资源配置通常不满足要求。

**资产处理管线**的概念直接映射到CI中的烘焙（Cook）阶段：资产处理管线定义了原始资产（`.fbx`、`.psd`、`.wav`）如何转换为引擎可用格式，而CI中的烘焙步骤则进一步将引擎格式资产转换为目标平台运行时格式，是资产处理管线的最终执行环节。理解贴图压缩格式差异（BC7 vs ASTC）和音频格式差异（PCM vs ADPCM）有助于分析为什么同一资产在不同平台的烘焙时间差异显著。
