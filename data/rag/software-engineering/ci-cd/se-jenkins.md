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
quality_tier: "B"
quality_score: 45.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
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

Jenkins 是一款用 Java 编写的开源持续集成/持续交付（CI/CD）服务器，最初由 Kohsuke Kawaguchi 于 2004 年在 Sun Microsystems 以 "Hudson" 之名创建，2011 年因与 Oracle 的商标纠纷更名为 Jenkins，并由社区独立维护至今。Jenkins 的核心二进制文件（`.war` 包）可独立运行于任何支持 Java 8+ 的环境，也可部署在 Tomcat 等 Servlet 容器中，默认监听 8080 端口。

Jenkins 之所以在 CI/CD 领域长期占据重要位置，在于其插件生态的规模：截至 2024 年，Jenkins 官方插件中心托管超过 **1800 个**插件，覆盖从 Git 拉取代码、Maven/Gradle 构建、Docker 镜像推送到 Kubernetes 部署的完整链路。团队可以用 Jenkinsfile 将整条流水线以代码形式存储在版本库中，实现"流水线即代码（Pipeline as Code）"的实践，让构建逻辑与应用代码同步演进。

## 核心原理

### Jenkinsfile 与 Pipeline DSL

Jenkinsfile 使用基于 Apache Groovy 的领域特定语言（DSL）编写，分为两种语法风格：**声明式（Declarative）**和**脚本式（Scripted）**。声明式语法以 `pipeline { }` 块为根，结构严格；脚本式语法以 `node { }` 块为根，灵活性更高但错误提示较弱。

声明式 Jenkinsfile 的最小骨架如下：

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
        stage('Deploy') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'docker-hub',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS')]) {
                    sh 'docker push $USER/myapp:latest'
                }
            }
        }
    }
    post {
        failure {
            mail to: 'team@example.com', subject: 'Build Failed'
        }
    }
}
```

`agent` 指令决定流水线在哪里执行：`agent any` 表示在任意可用 Node 上运行；`agent { docker 'maven:3.9' }` 表示在临时启动的 Docker 容器内运行，容器结束后自动销毁。`post` 块支持 `always`、`success`、`failure`、`unstable`、`changed` 五种条件，分别对应不同的收尾逻辑。

### 主从架构（Controller/Agent）

Jenkins 采用 **Controller-Agent** 架构（旧称 Master-Slave）。Controller 负责调度任务、存储配置和展示 UI；Agent（工作节点）负责实际执行构建步骤。Agent 通过 **JNLP（TCP 50000 端口）** 或 **SSH** 与 Controller 建立连接。每个 Agent 可配置"执行器（Executor）"数量，表示并发构建能力。在 Kubernetes 环境中，Jenkins Kubernetes 插件可动态创建 Pod 作为临时 Agent，构建完成后 Pod 自动回收，避免资源闲置。

### 插件加载与更新机制

Jenkins 的插件以 `.hpi` 或 `.jpi` 格式存储在 `$JENKINS_HOME/plugins/` 目录下。Jenkins 在启动时通过类加载器为每个插件创建独立的 `PluginClassLoader`，防止插件间类冲突。插件的依赖关系在 `MANIFEST.MF` 中以 `Plugin-Dependencies` 字段声明，Jenkins 会在安装时自动解析并下载传递依赖。使用 **Jenkins Configuration as Code（JCasC）** 插件，可以将 Jenkins 的系统配置（包括插件列表、凭证、Agent 配置）写成 YAML 文件，实现配置的版本化管理。

## 实际应用

**Java 微服务的多分支流水线**：使用 Jenkins 的 Multibranch Pipeline 项目类型，Jenkins 会自动扫描 Git 仓库中的所有分支和 Pull Request，对含有 Jenkinsfile 的分支逐一创建独立的流水线实例。`feature/*` 分支只跑单元测试，`main` 分支额外执行 Docker 镜像构建和推送至 Harbor 镜像仓库，所有步骤均在 Jenkinsfile 的 `when { branch 'main' }` 条件块内控制，无需维护多份配置文件。

**共享库（Shared Library）复用构建逻辑**：企业内多个团队若需共用相同的构建步骤（如统一的安全扫描、发布通知），可将 Groovy 函数封装在 Jenkins Shared Library 中。Shared Library 存储在独立 Git 仓库，目录结构固定为 `vars/`（全局变量/函数）和 `src/`（Groovy 类），在 Jenkinsfile 中以 `@Library('my-shared-lib') _` 一行引入，团队即可调用 `vars/deployToK8s.groovy` 中定义的 `deployToK8s()` 函数，避免重复编写相同逻辑。

## 常见误区

**误区一：把所有逻辑写进 Jenkinsfile 的 `sh` 步骤**。部分团队将数百行 Shell 脚本内联在 Jenkinsfile 中，导致可读性极差且无法单独测试。正确做法是将复杂脚本提取为仓库内独立的 `.sh` 文件或 Makefile 目标，Jenkinsfile 中的 `sh` 步骤只做调用，保持 Jenkinsfile 层面的逻辑简洁，并在 Shared Library 中封装可复用的高阶操作。

**误区二：混淆 `environment` 块与 `withCredentials` 的使用场景**。`environment { FOO = 'bar' }` 中定义的变量会以明文出现在构建日志和环境变量转储中；而密码、Token 等敏感信息必须存储在 Jenkins Credentials Store 中，通过 `withCredentials` 步骤注入，Jenkins 会自动在日志中用 `****` 遮盖这些值，防止泄漏。

**误区三：忽视 Jenkins Controller 的资源限制**。Jenkins Controller 本身不应承担繁重的构建任务，其 JVM 堆内存建议设置为 `-Xmx4g` 起步（大型实例可到 8g），并通过 `-XX:+UseG1GC` 启用 G1 垃圾收集器降低停顿时间。将 Controller 的执行器数量设置为 `0`，强制所有构建任务下发到 Agent，是生产环境的推荐配置。

## 知识关联

Jenkins 建立在**流水线设计**的概念之上：流水线设计中确定的阶段划分（如 Build → Test → Deploy）直接映射为 Jenkinsfile 中的 `stage` 块，而并行阶段的设计则对应 Jenkins 声明式语法中的 `parallel` 步骤。理解了流水线的串行/并行结构后，才能合理安排 Jenkinsfile 中的阶段顺序以缩短反馈时间。

在横向对比中，Jenkins 的竞争产品包括 GitLab CI（使用 `.gitlab-ci.yml` YAML 配置，无需独立服务器）、GitHub Actions（以 `.github/workflows/*.yml` 定义，原生集成 GitHub 事件触发）以及 Tekton（基于 Kubernetes CRD 的云原生流水线）。Jenkins 相比这些方案的核心优势在于插件生态的广度和私有化部署的灵活性，代价是运维复杂度更高：Controller 升级、插件兼容性维护和 `$JENKINS_HOME` 备份均需人工介入。对于计划迁移到云原生 CI/CD 的团队，理解 Jenkins 的 Jenkinsfile 语法也有助于理解后续 Tekton Pipeline 和 ArgoCD 工作流的设计思想，因为"任务（Task）→流水线（Pipeline）→触发器（Trigger）"的概念模型在各工具间高度一致。