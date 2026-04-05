---
id: "se-jenkins"
concept: "Jenkins"
domain: "software-engineering"
subdomain: "ci-cd"
subdomain_name: "CI/CD"
difficulty: 2
is_milestone: false
tags: ["平台"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Jenkins

## 概述

Jenkins 是一款基于 Java 开发的开源持续集成与持续交付服务器，最初由 Kohsuke Kawaguchi 于 2004 年作为 Hudson 项目在 Sun Microsystems 内部创建，2011 年因与 Oracle 的商标纠纷，社区将其分叉并正式更名为 Jenkins。它运行在 JVM 之上，默认监听 8080 端口，通过 WAR 包或 Docker 镜像即可独立部署。

Jenkins 的核心价值在于其"一切皆插件"的架构设计。截至 2024 年，Jenkins 插件中心（plugins.jenkins.io）托管了超过 1800 个插件，覆盖源码管理、构建工具、测试报告、部署目标等几乎所有 CI/CD 环节。这意味着同一个 Jenkins 实例可以同时服务于 Maven 构建的 Java 项目、Webpack 打包的前端项目和 Go 编译的微服务项目，而无需额外搭建独立的构建服务器。

Jenkins Pipeline 是 2016 年随 Jenkins 2.0 引入的首要特性，它将构建逻辑从 Web UI 配置迁移到版本控制中的 `Jenkinsfile` 文件，实现了"流水线即代码"（Pipeline as Code）的工程实践。

## 核心原理

### Jenkinsfile 两种语法风格

Jenkins Pipeline 提供**声明式（Declarative）**和**脚本式（Scripted）**两种语法。声明式语法以 `pipeline { }` 块为顶层结构，语法更严格，可读性强，是官方推荐的写法：

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package -DskipTests'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn test'
                junit 'target/surefire-reports/*.xml'
            }
        }
    }
    post {
        failure {
            mail to: 'team@example.com', subject: '构建失败'
        }
    }
}
```

脚本式语法以 `node { }` 块开头，使用完整的 Groovy 语言能力，灵活性更高但对编写者的 Groovy 知识要求更高。两种语法不能混用于同一 `Jenkinsfile` 的顶层，但声明式流水线内部可以通过 `script { }` 块嵌入脚本式代码片段。

### 关键指令与执行机制

声明式 Pipeline 的几个关键指令直接决定流水线的运行行为：

- **`agent`**：指定执行环境。`agent any` 表示在任意可用节点运行；`agent { docker 'maven:3.9' }` 表示在临时 Docker 容器中执行，容器销毁后不留痕迹。
- **`environment`**：在 `pipeline` 或 `stage` 级别声明环境变量，例如 `REGISTRY_URL = 'registry.example.com'`，所有 `steps` 中均可作为 `$REGISTRY_URL` 引用。
- **`when`**：条件执行某个 Stage，例如 `when { branch 'main' }` 使部署阶段仅在 main 分支触发时执行。
- **`parallel`**：在同一 Stage 内并行运行多个子 Stage，可将单元测试与代码扫描并行化，显著缩短总耗时。
- **`post`**：定义流水线或 Stage 结束后的回调，支持 `always`、`success`、`failure`、`unstable`、`changed` 五种条件。

### 插件生态的工作方式

Jenkins 插件以 `.hpi`（Hudson Plugin Interface）文件格式打包，本质是包含 Java 字节码和资源文件的 ZIP 归档。安装插件后 Jenkins 需要重启才能激活扩展点（Extension Point）。关键插件及其职责如下：

| 插件名称 | 用途 |
|---|---|
| Git Plugin | 从 Git 仓库检出代码，提供 `checkout scm` 步骤 |
| Pipeline: Shared Groovy Libraries | 跨项目复用 Groovy 函数库，通过 `@Library('my-lib') _` 引入 |
| Blue Ocean | 提供现代化可视化流水线 UI，取代经典的构建视图 |
| Credentials Plugin | 安全存储密码、SSH 密钥、API Token，通过 `withCredentials` 步骤注入 |
| Kubernetes Plugin | 动态在 K8s 集群中创建 Pod 作为 Jenkins Agent，实现弹性扩缩 |

**共享库（Shared Libraries）**是大型团队避免重复编写 Jenkinsfile 的标准手段。共享库遵循固定目录结构：`vars/` 下存放全局变量和函数，`src/` 下存放 Groovy 类。在 Jenkins 全局配置中注册共享库的 Git 地址后，各项目的 Jenkinsfile 即可直接调用库中定义的 `deployToK8s(env, version)` 等自定义步骤。

## 实际应用

**多分支流水线（Multibranch Pipeline）**是 Jenkins 处理 GitFlow 或 Trunk-Based Development 的专用 Job 类型。配置仓库地址后，Jenkins 会自动扫描所有分支和 Pull Request，为每个分支独立创建一条流水线，并在分支删除时自动清理对应的 Job。这使得每个 feature 分支的代码提交都能触发独立的构建和测试，而无需手动为每条分支创建 Job。

**与 Docker 结合的典型流程**：在 `agent { dockerfile true }` 模式下，Jenkins 读取仓库根目录的 `Dockerfile` 构建镜像并在其中执行所有步骤，彻底消除"在我电脑上没问题"的环境差异问题。构建完成后，使用 `docker.withRegistry('https://registry.example.com', 'registry-credentials')` 块将镜像推送到私有仓库，凭证 ID `registry-credentials` 由 Credentials Plugin 管理，明文密码不会出现在 Jenkinsfile 中。

## 常见误区

**误区一：将敏感信息直接写入 Jenkinsfile。**  
由于 Jenkinsfile 存储在 Git 仓库中，任何有仓库读权限的人都能看到硬编码的密码或 Token。正确做法是通过 Credentials Plugin 将凭证存储在 Jenkins 的加密 Keystore 中，在 Jenkinsfile 里只引用凭证 ID，使用 `withCredentials([usernamePassword(credentialsId: 'db-creds', usernameVariable: 'DB_USER', passwordVariable: 'DB_PASS')]) { }` 块在执行时注入。

**误区二：混淆 Jenkins Master 和 Agent 的职责。**  
Jenkins Master（也称 Controller）负责调度任务、存储配置和展示 UI，不应直接执行构建任务。在 Master 节点上运行 `sh 'mvn clean package'` 这类高负载操作会直接影响调度服务的稳定性。生产环境应配置专用 Agent 节点或使用 Kubernetes Plugin 动态创建 Pod Agent，Master 仅做协调器使用。

**误区三：认为 Blue Ocean 已取代经典 UI。**  
Blue Ocean 插件提供更友好的流水线可视化，但 Jenkins 官方已于 2022 年宣布停止 Blue Ocean 的主动开发，将新 UI 工作转移到 Jenkins 核心的"现代化界面"项目。依赖 Blue Ocean 进行新项目规划时需考虑其长期维护风险，核心功能应以经典 UI 和 Pipeline 语法为基准。

## 知识关联

Jenkins 流水线的**阶段（Stage）划分**直接承接流水线设计中制定的构建、测试、发布等阶段模型——流水线设计中规划的"何时并行、何时串行、何时设门禁"的决策，在 Jenkinsfile 的 `parallel` 块、`stage` 嵌套和 `input` 步骤中找到对应的实现语法。理解流水线设计中的"快速反馈"原则，有助于解释为何 Jenkins 中代码编译和单元测试应放在最早的 Stage，而集成测试和部署应置于后续 Stage。

Jenkins 对 **Groovy DSL** 的使用意味着理解 Groovy 的闭包（Closure）和委托（Delegate）机制，能帮助解读为何 `steps { sh '...' }` 这样的块语法是合法的 Groovy 代码而非独立语言。同时，Jenkins 与 Docker、Kubernetes 的集成是容器化部署实践的入口，Kubernetes Plugin 中 `podTemplate` 和 `containerTemplate` 的配置方式是后续学习 Kubernetes 工作负载调度的实际应用场景。