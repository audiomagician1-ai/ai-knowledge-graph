---
id: "se-dependency-review"
concept: "依赖审查"
domain: "software-engineering"
subdomain: "code-review"
subdomain_name: "代码审查"
difficulty: 2
is_milestone: false
tags: ["供应链"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 依赖审查

## 概述

依赖审查（Dependency Review）是代码审查流程中专门针对第三方库引入的一种检查活动，具体评估三个维度：安全漏洞（CVE）、许可证合规性、以及库的维护活跃度。当开发者在Pull Request中新增或升级一个npm包、Python wheel或Maven artifact时，依赖审查负责拦截那些可能将风险引入项目的变更。

依赖审查作为独立议题被广泛讨论，源于2016年的"left-pad事件"和2017年Equifax数据泄露事件——后者直接原因是Apache Struts 2（CVE-2017-5638）未及时修补，造成约1.47亿条用户记录泄露。这两个事件迫使行业将第三方依赖视为一类独立的风险面，而非仅仅是功能代码的附属品。

依赖审查的价值在于拦截点靠前：在库被合并进主干并部署到生产之前介入，修复成本最低。相比之下，若生产环境已经运行含有已知高危漏洞的库，修补往往需要紧急发版，代价可达开发阶段修复成本的30倍以上（NIST统计数据）。

## 核心原理

### 安全漏洞评估

安全漏洞审查以CVE（Common Vulnerabilities and Exposures）编号为基础，结合CVSS（Common Vulnerability Scoring System）评分判断严重程度。CVSS v3评分范围为0.0至10.0，业界通常将7.0以上定义为高危，9.0以上为严重。审查时需关注直接依赖（direct dependency）和传递依赖（transitive dependency）——例如你的项目依赖库A，库A依赖库B，库B存在CVE，这同样是你的攻击面。

工具层面，`npm audit`、`pip-audit`、`OWASP Dependency-Check` 以及 GitHub 内置的 Dependabot 均可扫描已知CVE数据库（如NVD、OSV）。审查者在PR评论中应记录：受影响版本范围、漏洞类型（如远程代码执行、路径遍历）、是否存在已修复版本、以及是否有可用的缓解措施。

### 许可证合规性评估

许可证审查的核心逻辑是判断第三方库的许可证是否与本项目的分发模式兼容。常见许可证按传染性强弱排列：GPL-3.0（强传染，要求衍生品也必须开源）> LGPL-2.1 > MPL-2.0 > Apache-2.0 ≈ MIT ≈ BSD-2-Clause（宽松，允许商业闭源使用）。

商业项目引入GPL-3.0许可证的库，若将其静态链接，理论上须将整个项目开源，这是典型的许可证冲突场景。审查时需查阅`package.json`的`license`字段、Python包的`classifiers`，或直接检查库仓库根目录的LICENSE文件。`license-checker`（npm）、`pip-licenses`（Python）可批量导出依赖树的许可证清单，方便审查者快速定位异常条目。

### 维护状态评估

一个功能正常但已被废弃（abandoned）的库同样是风险：未来的安全漏洞将不会得到修复。评估维护状态的具体指标包括：最近一次提交距今是否超过12个月、是否有未回复超过90天的高优先级Issue、GitHub仓库是否被归档（Archived状态）、以及是否有后续替代库的官方说明。

例如，npm生态中`request`库于2020年2月宣布停止维护，此后任何新引入`request`的PR均应在审查时标记，并建议迁移至`axios`、`got`或原生`fetch`。维护状态评估不能仅看star数量，一个有50k star但两年无提交的库，其风险不低于一个低知名度的活跃库。

## 实际应用

**GitHub Actions中的自动化依赖审查**：GitHub提供官方Action `actions/dependency-review-action`，可在PR触发时自动对比基础分支与目标分支的依赖差异，若检测到CVSS评分≥7.0的漏洞或指定黑名单许可证（如GPL-3.0），直接将Check标记为失败，阻止合并。配置示例中`fail-on-severity: high`即对应此阈值。

**Python项目的许可证门控**：某金融公司在CI流水线中使用`pip-licenses --format=json`输出所有依赖的许可证，再用自定义脚本比对白名单（仅允许MIT、Apache-2.0、BSD）。一旦PR新增了LGPL许可证的库，流水线失败，法务团队收到通知，进行逐案豁免审批。

**供应链攻击的审查应对**：2021年`ua-parser-js`库被攻击者劫持账号，上传含挖矿代码的恶意版本（0.7.29、0.8.0、1.0.0）。依赖审查在此类场景中的作用是：锁定版本（lock file审查）、校验package hash（`integrity`字段），防止浮动版本（如`^1.0.0`）在安装时拉取恶意新版本。

## 常见误区

**误区一：只审查直接依赖**。许多团队在PR审查时只查看`package.json`中显式列出的包，忽视传递依赖。实际上，2021年`log4shell`（CVE-2021-44228，CVSS 10.0）影响的`log4j-core`库大量以传递依赖形式存在，直接依赖审查完全无法发现。正确做法是使用`npm ls <package>`或`mvn dependency:tree`展开完整依赖树进行审查。

**误区二：有修复版本就立即要求升级**。升级版本可能引入Breaking Change，破坏现有功能。审查时应同时评估：漏洞的实际可利用性（是否需要特定输入条件）、项目是否真正调用了受影响的代码路径，以及升级的测试成本。对于CVSS评分在4.0以下的中低危漏洞，记录并计划下一个迭代修复，通常比强制阻断合并更符合工程实际。

**误区三：许可证相同版本可以任意使用**。Apache-2.0 v1与Apache-2.0 v2存在GPL兼容性差异；Creative Commons许可证（如CC BY-SA）并不适用于软件代码，误引入会造成合规隐患。审查时应以SPDX标准标识符（如`Apache-2.0`、`MIT`）为准，而非仅凭库的名气或常规印象判断许可证类型。

## 知识关联

依赖审查是代码审查（Code Review）的一个特化子任务，与普通功能代码审查的最大区别在于：审查对象是外部引入的二进制制品或源代码，而非团队自身编写的逻辑。掌握依赖审查后，自然延伸至**软件物料清单（SBOM，Software Bill of Materials）**——SBOM是将整个项目依赖关系结构化记录为可机器读取文件（如CycloneDX、SPDX格式）的实践，是依赖审查结论的持久化形式，也是美国2021年行政令（EO 14028）要求联邦软件供应商提供的合规文件。

依赖审查还与**持续集成安全门控（Security Gates in CI/CD）**密切相关：手动审查处理PR级别的新增变更，而CI中的`dependabot`或`Renovate Bot`自动创建升级PR，两者配合形成依赖安全的闭环管理机制。理解依赖审查的三个评估维度（漏洞、许可证、维护状态），是后续学习软件供应链安全（Supply Chain Security）和零信任依赖管理策略的直接前提。