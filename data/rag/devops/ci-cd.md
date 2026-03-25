---
id: "ci-cd"
concept: "CI/CD持续集成"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 5
is_milestone: false
tags: ["自动化"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.424
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# CI/CD持续集成

## 概述

CI/CD是Continuous Integration（持续集成）与Continuous Delivery/Deployment（持续交付/持续部署）的缩写，是一套将代码变更自动化测试、构建和发布的工程实践体系。持续集成的核心思想由Martin Fowler在2000年前后系统化总结，要求团队成员每天至少一次将代码合并到主分支，并通过自动化流水线立即验证每次合并的正确性。在AI工程场景中，CI/CD不仅处理应用代码，还需要管理模型文件、训练配置、数据版本等ML特有产物。

历史上，CI的实践最早可追溯到1991年Grady Booch提出的迭代开发理念，而第一个广泛使用的CI服务器CruiseControl于2001年发布。现代CI/CD工具链以Jenkins（2011年从Hudson分支而来）、GitHub Actions（2019年正式上线）和GitLab CI（2012年发布）为代表，已成为AI系统迭代上线的标准基础设施。

CI/CD在AI工程中的重要性超越普通软件工程，原因在于AI系统同时存在**代码漂移**和**模型漂移**两类问题。没有自动化流水线，一个新版本的推理代码可能悄然破坏线上模型的输入预处理逻辑，而手工发布流程根本无法在高频迭代中保障这类回归错误被及时发现。

---

## 核心原理

### 持续集成流水线的三阶段结构

一条标准CI流水线由**触发（Trigger）→ 构建（Build）→ 验证（Verify）**三个阶段组成。触发条件通常绑定到Git事件，例如`push`到`feature/*`分支或向`main`分支发起Pull Request时自动启动。构建阶段完成依赖安装（如`pip install -r requirements.txt`）和Docker镜像制作。验证阶段依次运行单元测试、集成测试和代码质量扫描，任何一步失败都会阻断后续流程并向开发者发送通知。

在AI工程中，验证阶段还需增加**模型冒烟测试（Model Smoke Test）**：用固定的20\~50条标注样本对新提交的推理代码运行一次端到端预测，断言关键指标（如F1、延迟P99）不低于预设阈值。这一步骤通常耗时不超过5分钟，却能拦截80%的模型接口兼容性问题。

### 持续交付与持续部署的区别

持续交付（Continuous Delivery）与持续部署（Continuous Deployment）在流水线末端有一个关键差异：**持续交付在部署前保留人工审批门控（Approval Gate）**，而持续部署则在所有自动化检查通过后立即将新版本推送到生产环境，无需人工干预。对于医疗、金融类AI系统，监管合规要求通常强制使用持续交付模式，以确保每次上线都有责任人签字确认。

### YAML流水线定义与关键配置语法

现代CI/CD系统通过代码化（Pipeline-as-Code）方式将流水线定义存储在仓库中。以GitHub Actions为例，一个AI服务的流水线文件存放于`.github/workflows/ci.yml`，核心字段结构如下：

```yaml
jobs:
  test:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/ --cov=src --cov-fail-under=80
  build:
    needs: test          # 声明依赖，test通过后才执行
    runs-on: ubuntu-22.04
    steps:
      - run: docker build -t mymodel:${{ github.sha }} .
```

`needs`关键字定义任务间的有向无环图（DAG）依赖关系，`github.sha`将每次提交的40位SHA哈希值注入镜像标签，保证镜像版本与代码提交一一对应，这是AI模型可追溯性的基础机制。

### 测试覆盖率门控与失败策略

CI流水线通常设置最低代码覆盖率阈值，例如`pytest-cov`中`--cov-fail-under=80`要求行覆盖率不低于80%，否则流水线返回非零退出码并标记为失败。对于AI推理服务，还应额外配置**性能回归门控**：在CI阶段使用Locust或`ab`工具对推理接口发起固定并发压测（如100并发×1000请求），若P95延迟超过上次基准的120%则阻断合并。

---

## 实际应用

**场景一：NLP模型服务的CI流水线**  
某团队维护一个基于BERT的文本分类服务，每次提交触发以下自动化步骤：①lint检查（flake8 + isort）②单元测试（pytest，覆盖率≥85%）③用100条固定测试集运行模型推理，断言准确率≥0.92④构建Docker镜像并推送至私有Harbor仓库，镜像标签格式为`bert-cls:2024.11.05-a3f9c2b`。整个流水线在GPU Runner上运行约8分钟。

**场景二：多环境流水线与环境变量隔离**  
生产级AI系统通常设置`dev`→`staging`→`prod`三套环境。CI流水线在合并到`develop`分支时自动部署到dev环境；向`main`分支合并并通过审批后，才将相同的镜像（不重新构建）推送至staging和prod，使用环境变量`MODEL_ENDPOINT`、`DB_CONNECTION_STRING`区分配置，而非重新打包镜像，确保"构建一次，到处运行"原则的严格落实。

**场景三：MLflow与CI/CD集成追踪实验**  
在CI验证阶段，可通过MLflow自动记录每次流水线运行的模型评估指标，并与上一个通过审批的版本对比。若新提交的特征工程代码导致AUC下降超过0.01，CI系统自动在Pull Request页面添加评论并阻断合并，将模型质量门控内嵌到代码审查流程中。

---

## 常见误区

**误区一：认为CI/CD等同于"自动跑测试"**  
不少工程师将CI/CD简化为仅在服务器上执行`pytest`。实际上，完整的CI/CD包含代码质量扫描、安全漏洞检测（如`trivy`扫描镜像中的CVE）、依赖许可证合规检查等多个质量门控，并通过流水线状态与Git分支保护规则联动，确保未通过CI的代码**物理上无法**合并到保护分支，而不仅仅是发出警告。

**误区二：AI项目中直接将模型权重文件提交到Git触发CI**  
大型模型文件（如PyTorch的`.pt`文件，动辄数GB）不应存储在Git仓库中，否则会导致CI触发时`git clone`耗时数十分钟，且严重膨胀仓库体积。正确做法是将模型权重存储在S3、GCS或MLflow Model Registry中，CI流水线通过模型版本号（如`model_version=v1.3.2`）在运行时拉取，Git仓库只保存版本号配置文件（如`model_config.yaml`，大小不超过几KB）。

**误区三：把持续部署直接用于所有AI系统**  
持续部署要求系统具备完善的自动回滚机制和充分的自动化测试覆盖，对于输出结果直接影响用户决策的AI系统（如信贷审批、医疗诊断），应优先选择持续交付模式并配合蓝绿部署策略，而非追求全自动化上线。

---

## 知识关联

CI/CD流水线的触发机制直接依赖**Git工作流（GitFlow）**的分支策略：GitFlow中的`feature`分支提交触发CI验证，`release`分支合并触发CD部署，两者的分支命名规范需在`.github/workflows`配置中精确匹配，否则流水线不会被正确激活。

掌握CI/CD后，可以进入**蓝绿部署**的学习——CI/CD负责构建并推送不可变镜像，蓝绿部署定义了如何用零停机方式切换新旧版本流量，两者共同构成AI服务安全上线的完整链路。**容器镜像仓库**（如Harbor、ECR）是CI流水线`docker push`步骤的目标存储，镜像的版本管理策略（保留最近10个标签、清理7天前的临时镜像）需与CI构建频率匹配设计。**GitOps**则在CI/CD基础上进一步将部署状态也纳入Git管理，Argo CD等工具会持续对比Git中声明的期望状态与集群实际状态，形成部署的闭环自动修复机制。**安全扫描**通常作为CI流水线中独立的并行Job运行，扫描结果通过SARIF格式上报到代码仓库的Security面板，不阻塞构建但会标记高危漏洞供人工审查。
