---
id: "security-scanning"
concept: "安全扫描"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 4
is_milestone: false
tags: ["sast", "dast", "vulnerability", "devsecops"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.4
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


# 安全扫描

## 概述

安全扫描是将SAST（静态应用安全测试）、DAST（动态应用安全测试）和SCA（软件成分分析）等自动化安全检测工具嵌入CI/CD流水线的工程实践，目标是在代码合并前就发现并阻断安全漏洞，而非等到生产部署后再进行修复。这种"左移安全"（Shift Left Security）的理念使得漏洞修复成本降低约6倍——NIST研究数据显示，在编码阶段修复一个漏洞的成本约为$80，而在生产环境修复同一漏洞的成本高达$7,600。

安全扫描在AI工程环境中面临特殊挑战：AI应用除常规Web漏洞外，还需要检测训练数据投毒、模型序列化文件（如Pickle格式）中的恶意代码、以及PyPI/Conda依赖链中的供应链攻击。2023年PyTorch的torchtriton依赖包遭受供应链攻击事件，正是因为缺乏SCA扫描而导致研究环境被污染。

在CI/CD流水线中，安全扫描通常被配置为流水线的强制检查门控（Gate），当扫描结果超过预设的CVSS（通用漏洞评分系统）阈值时，构建会被自动阻断，防止不安全的镜像流入下游环境。

## 核心原理

### SAST：静态应用安全测试

SAST在不运行代码的前提下，通过解析抽象语法树（AST）和数据流图来检测代码缺陷。针对Python AI项目，Bandit是最常用的SAST工具，它通过插件系统识别如`subprocess.call(shell=True)`这类命令注入风险，以及`pickle.loads(user_input)`这类反序列化漏洞。Bandit为每个发现项标记置信度（LOW/MEDIUM/HIGH）和严重性（LOW/MEDIUM/HIGH），在CI配置中通常设置`--severity-level medium --confidence-level medium`作为阻断条件，避免误报导致流水线过度阻断。

SAST的核心局限是无法检测运行时注入类漏洞，且对AI框架特定模式（如TensorFlow `tf.io.read_file`路径穿越）的识别需要自定义规则集补充。

### DAST：动态应用安全测试

DAST通过向运行中的应用发送恶意请求来发现漏洞，最具代表性的工具是OWASP ZAP（Zed Attack Proxy）和Nuclei。在CI/CD中集成DAST需要先在流水线中启动应用的测试实例（通常通过`docker-compose`启动），再触发ZAP的主动扫描。ZAP的API扫描模式可读取OpenAPI规范文件，自动生成针对AI推理服务每个端点的模糊测试用例，重点检测OWASP API Top 10中的BOLA（对象级别授权失效）和大量请求注入问题。

DAST扫描耗时通常在10-30分钟，因此在CI策略上常将其配置为仅在PR合并到main分支时触发，而非每次提交都执行。

### SCA：软件成分分析

SCA专门分析项目依赖的第三方库中的已知CVE漏洞，并识别许可证合规风险。`pip-audit`和Snyk是Python生态中主流的SCA工具。`pip-audit`查询PyPA Advisory Database，执行命令为：

```
pip-audit -r requirements.txt --format json --output audit-report.json
```

AI项目的依赖树通常极深，例如`transformers`库会间接引入60+个子依赖，SCA扫描需要展开完整的传递性依赖图（Transitive Dependency Graph）。CVSS评分≥7.0（高危）的漏洞应设为强制阻断，评分4.0-6.9（中危）可配置为警告但不阻断，给团队留出计划修复的时间窗口。

### 容器镜像扫描

AI工程的特殊性在于大量使用预构建的GPU基础镜像，如`nvcr.io/nvidia/pytorch:23.10-py3`，这类镜像内部可能包含数百个系统级依赖。Trivy是专为容器设计的扫描工具，能同时检测OS层（apt包）和应用层（Python包）的漏洞，在GitHub Actions中集成方式如下：

```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
    exit-code: '1'
    severity: 'CRITICAL,HIGH'
```

`exit-code: '1'`确保发现CRITICAL或HIGH漏洞时流水线返回非零退出码，从而阻断后续部署步骤。

## 实际应用

**AI推理服务的完整扫描流水线**：一个典型的配置是在GitHub Actions中按序执行四个安全步骤：①Bandit SAST扫描（约30秒）→ ②pip-audit SCA扫描（约60秒）→ ③Docker构建+Trivy镜像扫描（约3分钟）→ ④仅在main分支触发ZAP DAST扫描（约15分钟）。前三步在每次PR提交时执行，确保快速反馈；DAST仅在合并后执行，不影响开发节奏。

**Pickle文件的特殊处理**：AI模型权重文件如使用Pickle格式保存，应在SCA流程外额外运行`picklescan`工具扫描所有`.pkl`和`.pt`文件，因为常规SCA工具不检测二进制文件内容。picklescan通过解析Pickle操作码（opcode）识别`GLOBAL`指令中可疑的`__reduce__`调用，该攻击手法在2022年Hugging Face Hub上曾出现实际案例。

**漏洞豁免管理**：当某个CVE确认不影响实际部署环境时（如漏洞仅影响Windows平台，但服务运行在Linux容器中），应在`.trivyignore`或`pip-audit`的`--ignore-vuln`参数中记录豁免，并强制要求注释说明豁免理由和审批人，防止豁免列表成为安全盲区。

## 常见误区

**误区一：SAST零误报即安全**。SAST扫描通过率仅代表代码中无静态可检测的漏洞模式，但无法覆盖业务逻辑漏洞（如AI模型的未授权访问）和运行时配置错误（如S3存储桶公开暴露）。团队常误将SAST绿灯视为"安全审查通过"，导致跳过DAST和基础设施配置扫描。

**误区二：将所有CVE设为阻断导致流水线瘫痪**。直接将所有等级漏洞设为阻断条件后，团队发现流水线持续失败，最终选择完全禁用安全扫描。合理策略是：CVSS 9.0-10.0（严重）立即阻断；7.0-8.9（高危）阻断并要求48小时内提交修复计划；4.0-6.9（中危）记录到Issue但不阻断构建，给团队2-4周修复窗口。

**误区三：只扫描应用代码忽略基础镜像**。开发者往往只关注自己编写的Python代码的安全性，但AI项目依赖的CUDA基础镜像可能包含已知高危漏洞。Trivy扫描`nvcr.io/nvidia/pytorch:23.10-py3`镜像平均能发现200+个CVE，其中部分为高危，必须通过升级基础镜像版本或在Dockerfile中显式修复受影响的系统包来解决。

## 知识关联

安全扫描建立在CI/CD持续集成的流水线结构之上——没有自动化流水线，就无法实现扫描工具的触发、阻断和报告聚合。流水线中的`on: pull_request`触发器和`exit-code`机制是将安全扫描从可选步骤变为强制门控的技术基础。

Docker基础知识在容器镜像扫描环节至关重要：理解镜像层（Layer）结构有助于定位漏洞来源（是基础镜像层引入还是应用层引入），多阶段构建（Multi-stage Build）技术能有效减少最终镜像中的攻击面，例如将`python:3.10`开发镜像最终打包为`python:3.10-slim`运行镜像，可减少约70%的预装系统包数量，相应降低CVE暴露面。

安全扫描结果的长期管理通常与漏洞跟踪平台（如Dependabot、Snyk平台）集成，形成从发现→分配→修复→验证的闭环，这是DevSecOps成熟度模型中Level 3的标志性实践。