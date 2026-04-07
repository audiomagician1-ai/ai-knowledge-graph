# 游戏CI/CD

## 概述

游戏CI/CD（持续集成/持续交付）是将自动化构建流水线专门适配于Unreal Engine 5（UE5）和Unity等游戏引擎项目的工程实践。与通用软件CI/CD的根本差异在于：游戏项目的版本库中同时存在**可编译代码**（C++/C#/HLSL着色器）与**大规模二进制资产**（4K纹理、骨骼网格体、PCM音频），单一中型3A项目的美术资产总量通常介于20GB至200GB之间，这使得标准Git工作流面临严重的性能瓶颈。

游戏CI/CD的系统性实践约形成于2012至2015年间。Unity在2014年发布Unity Cloud Build服务，首次为中小团队提供托管式游戏构建环境（Unity Technologies, 2014）。Epic Games则在UE4时代（2015年）引入**BuildGraph**系统，并在UE5（2022年正式发布）中持续完善，BuildGraph是一套基于XML任务图的跨平台构建编排框架，专为处理虚幻引擎复杂的多平台打包需求而设计（Epic Games, 2022）。

游戏CI/CD的价值在多平台发布场景下尤为突出：同一款游戏通常需要同时交付PC（Win64/macOS）、主机（PS5/Xbox Series X/Nintendo Switch）和移动端（iOS/Android）共六个构建目标，每个目标有独立的SDK版本要求、代码签名证书和包体限制（例如Google Play要求APK压缩包不超过150MB，超出部分需使用AAB格式或PAD扩展文件）。自动化流水线可将全平台发布构建周期从人工操作的3至5天压缩至4至8小时。

## 核心原理

### UE5 UnrealBuildTool与BuildGraph

UE5的构建系统由两个工具共同支撑：**UnrealBuildTool（UBT）**负责C++模块的编译依赖解析与增量构建，**UnrealAutomationTool（UAT）**负责打包、烘焙（Cook）和部署的高层编排。BuildGraph作为UAT的子系统，通过XML脚本定义有向无环图（DAG）形式的任务依赖关系。

一个典型的BuildGraph节点定义如下：

```xml
<Node Name="Compile Editor Win64" Produces="#EditorBinaries">
    <Compile Target="UnrealEditor" Platform="Win64" Configuration="Development"/>
</Node>
<Node Name="Cook Content Win64" Requires="#EditorBinaries" Produces="#CookedContent">
    <Cook Project="MyGame" Platform="WindowsClient"/>
</Node>
```

触发完整打包的UAT命令示例：

```bash
Engine/Build/BatchFiles/RunUAT.bat BuildGraph \
  -Script=Build/MyGame.xml \
  -Target="Package All Platforms" \
  -set:ProjectPath=/Game/MyGame.uproject \
  -set:OutputDir=./Artifacts
```

UBT的增量编译机制基于文件修改时间戳与`.ubt_action`动作缓存文件。冷启动全量编译一个中型UE5项目（约300万行C++代码）通常需要60至120分钟；在启用**Incredibuild**或**Unreal Horde**分布式编译后，同等工程量可压缩至8至15分钟。增量编译在单文件修改场景下通常只需3至8分钟。

### Unity命令行构建与BatchMode

Unity支持通过`-batchmode`标志启动无头构建进程，配合`-executeMethod`参数指定静态方法入口点：

```bash
/path/to/Unity \
  -batchmode -quit \
  -projectPath /ci/MyGame \
  -buildTarget Android \
  -executeMethod CI.BuildPipeline.BuildRelease \
  -logFile /logs/build.log \
  -nographics
```

在C#构建脚本中，`BuildPipeline.BuildPlayer()`是打包的核心API调用：

```csharp
BuildPlayerOptions opts = new BuildPlayerOptions {
    scenes      = new[] { "Assets/Scenes/Main.unity" },
    locationPathName = "Builds/Android/MyGame.apk",
    target      = BuildTarget.Android,
    options     = BuildOptions.Il2CPP
};
BuildReport report = BuildPipeline.BuildPlayer(opts);
if (report.summary.result != BuildResult.Succeeded)
    throw new Exception($"Build failed: {report.summary.totalErrors} errors");
```

Unity的**Addressables**资产管理系统要求在`BuildPlayer`调用**之前**独立执行内容构建，否则运行时资产引用会指向Editor路径导致打包失败：

```csharp
AddressableAssetSettings.BuildPlayerContent(out AddressablesPlayerBuildResult result);
if (!string.IsNullOrEmpty(result.Error))
    throw new Exception($"Addressables build failed: {result.Error}");
```

### 大文件资产管理：Git LFS与Perforce

游戏CI/CD的版本控制方案必须专门处理二进制资产。主流方案对比如下：

- **Git LFS（Large File Storage）**：通过指针文件替换大文件本体，`.gitattributes`中声明`*.uasset filter=lfs diff=lfs merge=lfs -text`等规则。CI服务器需配置`GIT_LFS_SKIP_SMUDGE=1`避免每次拉取时下载全部LFS对象，改为按需拉取构建所需资产。
- **Perforce Helix Core**：业界大型游戏工作室（如育碧、EA）的主流选择，原生支持文件锁定（Exclusive Checkout）防止二进制资产合并冲突，流（Streams）机制支持按目录划分构建代理的同步范围，避免美术机器同步代码、程序机器同步全量4K纹理。

## 关键方法与配置

### 着色器编译缓存（DDC）

UE5的**派生数据缓存（Derived Data Cache, DDC）**是构建速度优化的关键机制。DDC存储着色器编译结果、材质烘焙数据等中间产物，其哈希键由源文件内容和平台配置共同决定：

$$\text{DDC\_Key} = \text{SHA256}(\text{SourceAsset} \| \text{PlatformConfig} \| \text{EngineVersion})$$

在CI环境中配置共享DDC（通常挂载为网络存储或S3兼容对象存储）可将着色器编译时间减少60%至80%。`Engine/Config/BaseEngine.ini`中的相关配置：

```ini
[DerivedDataBackendGraph]
Root=(Type=KeyLength, Length=120, Inner=AsyncPut)
AsyncPut=(Type=AsyncPut, Inner=Hierarchy)
Hierarchy=(Type=Hierarchical, Inner=Boot, Inner=Shared)
Shared=(Type=FileSystem, ReadOnly=false, Clean=false, Flush=false, \
        PurgeTransient=true, DeleteUnused=true, \
        Path=\\ci-storage\UE5-DDC\%ENGINE_VER%)
```

### 多平台构建矩阵（GitHub Actions示例）

```yaml
jobs:
  build-game:
    strategy:
      matrix:
        platform: [Win64, Android, iOS]
        config:   [Development, Shipping]
    runs-on: ${{ matrix.platform == 'iOS' && 'macos-14' || 'windows-latest' }}
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true
      - name: Cook & Package
        run: |
          Engine/Build/BatchFiles/RunUAT.bat BuildCookRun \
            -project=${{ github.workspace }}/MyGame.uproject \
            -targetplatform=${{ matrix.platform }} \
            -configuration=${{ matrix.config }} \
            -cook -stage -package -archive \
            -archivedirectory=./Artifacts/${{ matrix.platform }}_${{ matrix.config }}
```

iOS平台的CI构建还需要在macOS Agent上预配置`fastlane match`或手动导入`*.p12`开发者证书与`*.mobileprovision`描述文件到Keychain，否则Xcode代码签名步骤将失败。

### 构建产物版本化

构建产物（Artifact）应包含确定性版本号。常见方案是将Git提交哈希、流水线运行编号和日期戳合并编码：

```python
import subprocess, datetime, os
git_hash   = subprocess.check_output(['git','rev-parse','--short','HEAD']).decode().strip()
build_num  = os.environ.get('CI_PIPELINE_IID', '0')
date_str   = datetime.date.today().strftime('%Y%m%d')
version    = f"1.2.{build_num}+{date_str}.{git_hash}"  # 例如 1.2.47+20250314.a3f9c12
```

该版本号需同时写入UE5的`DefaultGame.ini`的`ProjectVersion`字段和Unity的`PlayerSettings.bundleVersion`，确保崩溃报告（Bugsnag/Firebase Crashlytics）中的堆栈符号化能精确匹配构建产物。

## 实际应用

### 案例：《原神》类手游的双引擎混合CI

某国内头部手游采用Unity主引擎 + 自研渲染插件（部分C++）的架构，其CI流水线分为三个阶段：

1. **代码合规阶段**（约8分钟）：对C#脚本执行Roslyn静态分析，检测`Update()`中的GC Alloc、协程滥用等移动端性能反模式；对Shader执行Mali Offline Compiler（mali_sc）检查指令数，超过256条ALU指令的着色器触发警告。

2. **资产构建阶段**（约45分钟）：分布式执行Addressables内容构建，按资产分组（Atlas/Audio/Scene/Prefab）并行构建16个内容包，汇总生成`catalog.json`；同步执行Android AAB打包与iOS IPA构建，两个平台并行节约约20分钟。

3. **自动化测试阶段**（约30分钟）：在无头Unity实例中运行EditMode和PlayMode测试套件（NUnit框架），以及基于**Unity Test Framework**的性能基准测试，记录关键场景的帧时间、DrawCall数和GPU内存占用，与基准提交对比超过15%回退则阻断合并。

### 案例：UE5多人游戏的Dedicated Server构建

UE5多人游戏需要同时打包Client和Server目标，Server构建不包含渲染模块，包体通常比Client小40%至60%。CI脚本需分别调用：

```bash
# 打包Linux Dedicated Server（部署至云服务器）
RunUAT.bat BuildCookRun -project=MyGame.uproject \
  -server -serverplatform=Linux -serverconfig=Shipping \
  -cook -stage -package -archive

# 打包Win64 Client（发布至Steam）
RunUAT.bat BuildCookRun -project=MyGame.uproject \
  -clientconfig=Shipping -targetplatform=Win64 \
  -cook -stage -package -archive -compressed
```

Server端构建完成后，CI流水线自动通过SSH将新版本部署至测试服，执行GameServer健康检查（连接握手协议验证），通过后才允许Client构建进入QA分发流程。

## 常见误区

**误区一：直接将通用CI模板应用于游戏项目**

通用Node.js或Java项目的CI配置假设代码仓库小于500MB且无需特殊缓存策略。游戏项目若未配置Git LFS带宽限制，每次完整克隆可能消耗数十GB流量，导致CI分钟数暴增。正确做法是在`checkout`步骤设置`--filter=blob:none`实现部分克隆，或使用Perforce的工作区映射精确控制同步范围。

**误区二：忽略Addressables内容构建的顺序依赖**

Unity的Addressables内容构建（`BuildPlayerContent`）必须在`BuildPlayer`之前完成，且两者必须使用**相同的构建目标（BuildTarget）**。如果CI脚本先切换BuildTarget再执行Addressables构建，会因Library缓存失效导致额外的全量资产重导入，浪费30至60分钟。

**误区三：未区分Development与Shipping构建配置**

UE5的Development构建保留了Console命令、日志输出和ProfileGPU接口，其可执行文件体积通常比Shipping大30%至50%，且性能存在可测量的差异（约5%至15%的帧时间开销）。CI流水线中用于性能基准测试的构建必须使用Shipping配置，否则测试数据不具备参考价值。

**误区四：将代码签名证书硬编码在仓库中**

iOS `*.p12`私钥和Android `*.jks`密钥库文件不应存储在版本控制系统中。正确实践是通过CI平台的Secret管理（GitHub Actions Secrets、GitLab CI Variables或HashiCorp Vault）注入敏感凭证，在构建机器上临时创建Keychain条目，构建完成后立即清除。

**误区五：DDC缺失时不设置超时**

在CI环境中若共享DDC不可达（网络故障），UE5的Cook过程会回退到本地重新编译全部着色器，将Cook时间从15分钟扩大到90分钟以上。应在BuildGraph中为Cook节点设置合理的超时阈值，并配置DDC不可用时的告警通知，而非静默降级。

## 知识关联

**与DevO