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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

安全扫描（Security Scanning）是指在AI工程的CI/CD流水线中，通过自动化工具对代码、依赖项、容器镜像和运行时行为进行系统性漏洞检测的实践。其核心目标是在软件交付的每个阶段拦截安全缺陷，而非在生产部署后才发现问题。在AI系统中，安全扫描尤为重要，因为模型训练依赖大量第三方库（如PyTorch、transformers、numpy），每一个存在漏洞的依赖都可能成为攻击向量。

安全扫描按照检测时机和方式分为三大类：SAST（静态应用安全测试）、DAST（动态应用安全测试）和SCA（软件成分分析）。SAST起源于20世纪90年代的程序分析学术研究，最早在银行和航天软件中应用；DAST则模拟真实攻击者的黑盒行为；SCA随着开源软件爆炸式增长在2010年代成为主流。三者组合形成了"左移安全"（Shift Left Security）策略的技术基础，将安全检测从上线后前移到代码提交阶段。

将安全扫描集成到CI/CD流水线的价值在于：根据IBM Security研究，在开发阶段修复一个漏洞的成本约为生产阶段的15倍。对于AI模型服务来说，一个未修复的CVE（通用漏洞披露）可能导致数据泄露、模型劫持或推理服务被恶意利用，直接威胁业务合规性（如GDPR、等保三级要求）。

---

## 核心原理

### SAST：静态应用安全测试

SAST工具在不执行代码的情况下扫描源代码或字节码，通过数据流分析（Data Flow Analysis）和控制流图（CFG）检测注入漏洞、硬编码密钥等问题。在AI工程场景中，Bandit是专为Python设计的SAST工具，它使用抽象语法树（AST）解析代码，内置超过100条安全规则，例如规则B105会标记硬编码密码，B608会检测SQL注入风险。在CI/CD中集成Bandit的典型命令为：

```bash
bandit -r ./src -f json -o bandit-report.json --exit-zero
```

`--exit-zero`参数确保扫描结果以报告形式输出而不中断流水线，配合阈值配置决定是否失败构建（如高危漏洞数量大于0时中止）。

### SCA：软件成分分析

SCA专门针对项目依赖的开源组件，通过查询NVD（National Vulnerability Database）和OSV（Open Source Vulnerabilities）数据库匹配已知CVE编号。在AI项目中，`requirements.txt`或`pyproject.toml`中的每个包都是扫描对象。常用工具包括：

- **Safety**：扫描Python依赖，命令为`safety check -r requirements.txt --json`，数据库每日更新
- **Trivy**：由Aqua Security开发，支持扫描pip、conda、OS包及Docker镜像层，CVE数据库覆盖率超过90%
- **Snyk**：提供修复建议并可自动生成PR更新依赖版本

一个典型的SCA发现示例：`numpy<1.24.0`存在CVE-2021-41495（整数溢出漏洞），CVSS评分7.5（高危），SCA工具会输出受影响版本范围和推荐的修复版本。

### DAST与容器镜像扫描

DAST在应用运行时发送恶意构造的HTTP请求，检测XSS、SQL注入、SSRF等运行时漏洞。OWASP ZAP是最广泛使用的开源DAST工具，在AI推理服务（如FastAPI/Flask封装的模型API）部署到测试环境后，ZAP可以自动爬取API端点并执行主动扫描。集成命令示例：

```bash
docker run -t owasp/zap2docker-stable zap-api-scan.py \
  -t http://staging-api:8000/openapi.json -f openapi
```

容器镜像扫描是AI工程特有的重要环节，因为模型服务通常以Docker镜像交付。Trivy扫描镜像时会逐层分析每个Dockerfile指令引入的包，检测基础镜像（如`python:3.10-slim`）中的OS级别CVE和应用层依赖漏洞，输出格式包含漏洞ID、严重程度（CRITICAL/HIGH/MEDIUM/LOW）和修复版本。

### 流水线集成架构

在GitHub Actions或GitLab CI中，安全扫描阶段通常置于单元测试之后、镜像构建和部署之前，形成"安全门禁"（Security Gate）。一个标准的AI项目安全扫描阶段包含四个串行步骤：SAST扫描（约2-5分钟）→ SCA依赖扫描（约1-3分钟）→ 镜像构建 → 容器镜像扫描（约3-8分钟），总耗时通常控制在15分钟以内以不显著影响交付速度。扫描结果应上传至SARIF（Static Analysis Results Interchange Format）格式的报告，GitHub Security标签页可直接解析并展示漏洞详情。

---

## 实际应用

**场景一：AI模型服务的依赖漏洞管控**

某AI推荐系统使用`flask==1.0.0`，SCA扫描发现该版本存在CVE-2023-30861（会话Cookie安全缺陷），CVSS评分7.5。在GitLab CI配置中设置`allow_failure: false`，使高危漏洞直接阻断合并请求，强制开发团队将Flask升级至2.3.2后才能继续部署。

**场景二：训练脚本的密钥泄露检测**

AI工程师在训练脚本中硬编码了AWS Access Key用于访问S3训练数据，SAST工具（如detect-secrets或TruffleHog）在git pre-commit钩子和CI阶段双重拦截，扫描正则模式匹配`AKIA[0-9A-Z]{16}`格式字符串，在代码推送时即刻阻断并通知安全团队轮换密钥。

**场景三：模型推理API的DAST测试**

FastAPI搭建的模型推理服务暴露了`/predict`端点，接受JSON输入。DAST扫描发现该接口未对输入长度做限制（无`max_length`校验），攻击者可提交超大payload导致OOM崩溃。ZAP的主动扫描模式自动构造了8MB的畸形JSON请求，复现了DoS漏洞，推动团队在Pydantic模型中添加`Field(max_length=10000)`约束。

---

## 常见误区

**误区一：认为SAST误报率高、实际价值有限，因此跳过**

部分团队因SAST工具产生大量误报（Bandit在某些项目中误报率可达40%）而直接禁用，这是错误做法。正确处理是通过配置`.bandit`文件屏蔽特定规则或路径，例如对测试目录关闭B101（assert使用检测），而非全局禁用。误报管理是SAST工程化落地的必要步骤，而非否定其价值的理由。

**误区二：只扫描应用代码，忽略基础镜像的OS层漏洞**

许多AI团队只使用Bandit扫描Python代码，忽略了Docker镜像中`/usr/lib`下的系统库漏洞。实际上，`python:3.10`官方基础镜像历史上曾携带高危OpenSSL漏洞（CVE-2022-0778），仅扫描应用层代码完全无法发现此类问题。容器镜像扫描（Trivy或Grype）必须作为独立步骤在镜像构建后执行。

**误区三：将安全扫描视为一次性配置，不维护CVE数据库更新**

安全扫描工具的漏洞数据库需要持续更新，否则扫描结果会遗漏新发现的CVE。Trivy支持`--db-repository`指定数据库镜像来源，在离线环境中需要定期从`ghcr.io/aquasecurity/trivy-db`同步；Safety的本地数据库若超过14天未更新会产生告警。生产级安全扫描必须在CI配置中强制拉取最新漏洞数据库。

---

## 知识关联

**与CI/CD持续集成的关系**：安全扫描本质上是CI流水线中的一类特殊质量门禁，其触发时机、并行/串行策略和失败处理逻辑直接复用CI/CD的stage/job机制。理解GitHub Actions的`needs`关键字和GitLab CI的`stages`定义是正确编排安全扫描阶段的前提，例如容器镜像扫描必须配置`needs: [build-image]`以确保在镜像产物存在后才执行。

**与Docker基础的关系**：容器镜像扫描要求理解Docker镜像的分层结构（Union File System），Trivy正是通过解析每一层的`layer.tar`来识别引入了哪些软件包。此外，在CI中以Docker-in-Docker（DinD）方式运行DAST工具（如ZAP容器）需要掌握Docker网络配置，确保ZAP容器能访问同一compose网络中的待测服务。

安全扫描是AI工程DevSecOps实践的执行层，其扫描结果会向上驱动漏洞管理流程（如JIRA安全缺陷跟踪、SLA响应要求），也为合规审计（SOC2、ISO27001）提供可量化