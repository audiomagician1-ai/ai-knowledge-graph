# CI/CD工具：Jenkins/GitHub Actions/GitLab CI在游戏测试中的配置

## 概述

CI/CD（Continuous Integration / Continuous Delivery）工具是游戏质量保障流水线的核心基础设施。Jenkins 于2011年从 Hudson 项目分叉独立，由 Kohsuke Kawaguchi 主导开发，至今仍是 Ubisoft、EA、Rockstar 等大型游戏工作室内网部署的首选 CI 引擎。GitHub Actions 于2019年11月正式 GA（General Availability），凭借与 GitHub 仓库的原生事件系统集成，迅速成为独立游戏团队和中型工作室的标配。GitLab CI 自2012年随 GitLab 平台一同推出，其最大特点是配置文件 `.gitlab-ci.yml` 与代码同仓存储，天然支持版本追溯。

三款工具在游戏测试场景下的共同目标是：每次代码提交后自动触发构建（Build）、静态分析（Lint）、单元测试（Unit Test）、冒烟测试（Smoke Test）和回归测试（Regression Test），将原本需要 QA 工程师手动执行4至8小时的验证流程压缩至流水线中并行完成，从而实现"提交即验证"的工程文化。

根据 Forsgren、Humble 与 Kim 在《Accelerate: The Science of Lean Software and DevOps》（2018）中的研究，部署频率高、变更前置时间短的团队，其产品质量和组织绩效均显著优于低效能团队。游戏行业的大型项目（如采用 Perforce + Jenkins 组合的 AAA 工作室）借助 CI 流水线，可将"集成炸版本"的平均修复时间（MTTR）从数天缩短至数小时以内。

---

## 核心原理

### 流水线配置语法与触发机制

三款工具均以 YAML 或 Groovy DSL 描述流水线阶段（Stage），但触发语法存在关键差异：

**Jenkins Declarative Pipeline**（`Jenkinsfile`，Groovy DSL）：

```groovy
pipeline {
    agent { label 'unity-2022' }
    triggers { pollSCM('H/5 * * * *') }  // 每5分钟轮询仓库
    stages {
        stage('Smoke Test') {
            when { branch 'develop' }
            steps {
                sh '/opt/Unity/Editor/Unity -batchmode -quit \
                    -projectPath . \
                    -runTests -testPlatform EditMode \
                    -testResults results/smoke.xml'
            }
        }
    }
}
```

**GitHub Actions**（`.github/workflows/game-ci.yml`）：

```yaml
on:
  push:
    branches: [develop, release/**]
  pull_request:
    branches: [main]
jobs:
  build-and-test:
    runs-on: self-hosted  # 必须使用自托管 Runner
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true  # 游戏大文件（贴图、音频）必须启用 LFS
      - name: Run Unity Tests
        run: |
          $UNITY_PATH -batchmode -runTests \
            -testPlatform PlayMode \
            -testResults results/playmode.xml
```

**GitLab CI**（`.gitlab-ci.yml`）：

```yaml
stages: [build, test, deploy]
unity_test:
  stage: test
  tags: [gpu, unity-2022]  # 指定配置了 GPU 的特定 Runner
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"
  script:
    - unity-editor -batchmode -runTests -testPlatform EditMode
  artifacts:
    reports:
      junit: results/*.xml  # 自动解析 JUnit 格式测试报告
```

游戏项目的典型触发策略是：向 `feature/*` 分支提交时只运行编辑器模式单元测试（约3至5分钟）；向 `develop` 提交时增加 PlayMode 集成测试（约15至30分钟）；向 `release` 提交时触发完整回归测试套件，包含真机设备测试（可能长达2至4小时）。

### Agent/Runner 与游戏专用构建环境

Jenkins 的执行节点称为 **Agent**，GitHub Actions 和 GitLab CI 均称为 **Runner**。游戏项目因以下三类需求无法使用云端共享 Runner：

1. **引擎授权**：Unity 和 Unreal Engine 均需要有效的浮动许可证（Floating License）或批量激活，云端共享节点无法持久保存激活状态。
2. **GPU 加速**：渲染截图对比测试（Visual Regression Test）、图形 API 兼容性测试需要实体 GPU，GitHub Actions 的 `ubuntu-latest` 镜像不提供 NVIDIA/AMD GPU 驱动。
3. **大型资产缓存**：一个中型 Unity 项目的 `Library` 目录可达20至50 GB，每次从零构建耗时过长，需要在固定自托管机器上持久缓存。

GitLab CI 通过 `tags:` 字段将 Job 路由到特定 Runner（如打了 `gpu` 和 `unity-2022` 标签的机器）；Jenkins 通过 `agent { label 'unity-2022' }` 实现相同效果；GitHub Actions 通过 `runs-on: self-hosted` 配合 Runner 标签筛选。

### 并行化与矩阵构建

游戏测试套件体量庞大时，串行执行会成为瓶颈。三款工具均支持矩阵构建（Matrix Build）来并行覆盖多平台：

**GitHub Actions 矩阵示例（同时构建 iOS / Android / PC）**：

```yaml
strategy:
  matrix:
    platform: [StandaloneWindows64, Android, iOS]
    unity_version: ['2022.3.10f1']
```

Jenkins 的 `parallel` 块实现相同效果：

```groovy
parallel {
    stage('PC Build')      { steps { /* ... */ } }
    stage('Android Build') { steps { /* ... */ } }
}
```

并行度 $P$ 与总测试时间 $T_{total}$ 的关系可由 Amdahl 定律近似估算：

$$T_{parallel} = T_{serial} \cdot \left( \frac{1-f}{P} + f \right)$$

其中 $f$ 是不可并行化的串行部分占比（如打包签名、上传分发步骤），$P$ 是并行 Runner 数量。当游戏项目有20%的步骤必须串行（$f=0.2$）时，即使将 Runner 数量从1增加到10，理论加速比也只能达到 $\frac{1}{0.2 + 0.08} \approx 3.57$ 倍，而非10倍。这一理论上限是合理规划 Runner 资源的重要依据。

---

## 关键配置方法与公式

### Unity 批处理模式测试命令参数

Unity 在 CI 环境中通过 `-batchmode` 参数以无头（Headless）模式运行，关键参数组合如下：

| 参数 | 含义 | 游戏测试场景 |
|---|---|---|
| `-batchmode -quit` | 无头模式，完成后自动退出 | 所有 CI 场景必选 |
| `-runTests` | 触发 Unity Test Runner | 执行 EditMode / PlayMode 测试 |
| `-testPlatform EditMode` | 仅运行编辑器测试 | 逻辑单元测试，无需渲染上下文 |
| `-testPlatform PlayMode` | 运行运行时测试 | 场景加载、物理、协程集成测试 |
| `-testResults path/result.xml` | 输出 NUnit/JUnit XML 报告 | 供 CI 工具解析失败信息 |
| `-buildTarget Android` | 指定构建目标平台 | 交叉编译 Android APK |

### 测试报告解析与质量门禁

三款工具均能解析 JUnit XML 格式的测试报告，并在测试失败时阻断 Pipeline（质量门禁 / Quality Gate）。

Jenkins 通过 `junit` 步骤收集报告：

```groovy
post {
    always {
        junit 'results/**/*.xml'
        // 失败率超过5%时标记为 UNSTABLE
        script {
            if (currentBuild.testResultAction.failCount > 0) {
                currentBuild.result = 'UNSTABLE'
            }
        }
    }
}
```

GitLab CI 通过 `artifacts: reports: junit:` 将测试结果直接显示在 Merge Request 页面，开发者无需打开外部 Jenkins 控制台即可看到哪条测试用例失败。

### 缓存策略：加速 Unity Library 目录

Unity 首次构建时需要将所有资产导入（Import）并写入 `Library` 目录，中型项目耗时30至90分钟。合理的缓存配置可将后续构建缩短至5至15分钟。

GitHub Actions 缓存示例：

```yaml
- uses: actions/cache@v4
  with:
    path: Library
    key: Library-${{ hashFiles('Assets/**', 'Packages/**', 'ProjectSettings/**') }}
    restore-keys: Library-
```

缓存键（Cache Key）使用 `Assets/`、`Packages/` 和 `ProjectSettings/` 的哈希值生成，保证任意资产变更时缓存自动失效，避免使用过期 Library 导致的"幽灵构建失败"问题。

---

## 实际应用：游戏测试流水线完整案例

### 案例：Unity 手游项目的 GitLab CI 多阶段流水线

某中型手游团队（约30人）在 GitLab CI 上配置了如下四阶段流水线，覆盖从代码提交到测试报告分发的完整链路：

1. **静态分析阶段（约2分钟）**：运行 Roslyn Analyzer 检查 C# 代码规范，检测 `Debug.Log` 遗留调用（游戏发布版本中 Debug.Log 会显著影响性能），使用自定义规则阻断包含 `GameObject.Find()` 在 `Update()` 中调用的提交。

2. **编辑器测试阶段（约8分钟）**：运行全部 EditMode 测试，涵盖战斗公式验算（伤害计算、暴击概率曲线）、存档序列化/反序列化、网络协议 Buffer 编解码的单元测试，共约800个测试用例。

3. **PlayMode 集成测试阶段（约25分钟）**：运行场景加载测试（验证所有游戏关卡无空引用异常）、UI 自动化测试（使用 Unity UI Test Framework 模拟点击主界面按钮流程）、物理碰撞回归测试。

4. **构建产物验证阶段（约15分钟）**：构建 Android Debug APK，使用 `apkanalyzer` 工具检查包体大小是否超过预设阈值（例如首包不超过100 MB），并将 APK 上传至内部分发平台（如 Firebase App Distribution）。

整条流水线总耗时约50分钟，相比手动执行节省约6小时，且每个 Merge Request 均可在 GitLab 界面直接看到四个阶段的通过/失败状态。

### 案例：Jenkins + Perforce 在 AAA 项目中的配置

大型 AAA 游戏工作室通常使用 Perforce（P4）作为版本控制系统而非 Git。Jenkins 通过 Perforce Plugin（`p4-plugin`）监听 P4 Stream 上的 Changelist 提交事件：

```groovy
pipeline {
    agent { label 'ue5-build-farm' }
    triggers {
        perforce spec: 'stream://Main/...', 
                 credential: 'p4-credentials'
    }
    stages {
        stage('UE5 Editor Build') {
            steps {
                sh 'Engine/Build/BatchFiles/RunUAT.sh BuildEditor \
                    -project=MyGame.uproject \
                    -platform=Win64'
            }
        }
        stage('Automated Tests') {
            steps {
                sh 'Engine/Binaries/Linux/UnrealEditor \
                    MyGame.uproject \
                    -ExecCmds="Automation RunAll" \
                    -unattended -nopause'
            }
        }
    }
}
```

Unreal Engine 的自动化测试框架（Automation Test Framework）输出 JSON 格式报告，需要额外的 Jenkins 插件（如 `xunit` 插件）进行格式转换后才能在 Jenkins 界面显示测试趋势图。

---

## 常见误区

### 误区一：在共享 Runner 上运行 Unity/UE 构建

Unity 和 Unreal Engine 的许可证激活状态绑定到具体机器的硬件 ID。使用 GitHub Actions 默认的 `ubuntu-latest` 共享 Runner 会导致每次构建都需要重新激活（或使用 Unity Build Server License），且无法利用 Library 缓存加速构建。正确做法是始终使用配置了固定 License 和引擎工具链的自托管 Runner。

### 误区二：将游戏 Asset 文件直接提交到 Git，不配置 LFS

游戏项目中的贴图（.psd、.tga）、音频（.wav、.ogg）、预制体（.prefab）文