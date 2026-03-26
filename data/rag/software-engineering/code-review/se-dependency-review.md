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
quality_tier: "B"
quality_score: 48.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.536
last_scored: "2026-03-22"
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

依赖审查（Dependency Review）是代码审查流程中专门针对第三方库和外部组件的评估环节，核心目标是在引入新依赖之前，系统性地检查其安全漏洞（CVE编号）、开源许可证合规性以及维护活跃度三个维度。与普通的逻辑代码审查不同，依赖审查的对象不是自己团队编写的代码，而是来自 npm、Maven、PyPI 等包管理生态系统的外部代码包。

依赖审查作为独立实践兴起于2010年代中期，2017年的 Equifax 数据泄露事件是重要转折点——攻击者利用 Apache Struts 框架中已知漏洞 CVE-2017-5638，最终暴露了约1.47亿条个人信息。此事件直接推动企业将"谁引入了这个库，谁审查过它"作为研发流程的强制检查点。

依赖审查的意义在于，现代应用程序中第三方代码的比例通常超过80%，自研代码反而是少数。如果只审查自己编写的代码而忽略依赖，等于只检查了一栋楼的内墙，却对承重结构视而不见。

## 核心原理

### 安全漏洞评估

安全审查的基础是 CVE（Common Vulnerabilities and Exposures）数据库与 CVSS（Common Vulnerability Scoring System）评分。CVSS 分值范围为 0.0 至 10.0，业界通常将 7.0 以上定义为高危，9.0 以上为严重。审查者需要核查拟引入版本是否存在已公开 CVE，以及该版本是否是修复了漏洞的最新稳定版。

工具层面，`npm audit`、`Snyk`、`OWASP Dependency-Check` 等可自动扫描 `package.json`、`pom.xml`、`requirements.txt` 等清单文件，输出已知漏洞列表和建议升级版本。GitHub 的 Dependabot 可在 Pull Request 阶段自动标记新增的高危依赖，做到"门控式"阻断。

### 许可证合规性检查

开源许可证直接影响商业产品的法律风险。常见许可证的传染性（Copyleft）程度从高到低排列为：**GPL-3.0 > LGPL-2.1 > MPL-2.0 > Apache-2.0 ≈ MIT**。其中 GPL-3.0 要求衍生作品必须以相同许可证开源，对于闭源商业软件属于不兼容许可证，审查时应直接拒绝引入。MIT 和 Apache-2.0 允许在闭源项目中使用，但 Apache-2.0 要求保留 NOTICE 文件。

审查时需记录每个新依赖的 SPDX 标识符（如 `MIT`、`Apache-2.0`），并与本项目的许可证白名单进行比对。工具 `liccheck`（Python）和 `license-checker`（Node.js）可自动提取依赖的许可证信息并生成合规报告。

### 维护状态评估

一个长期不维护的库即使当前没有已知漏洞，也是潜在风险——一旦出现零日漏洞将无法及时修复。评估维护状态的具体指标包括：

- **最近提交时间**：超过24个月无提交通常视为废弃（Abandoned）
- **issue 响应率**：核心 issue 长期无回应说明维护者不活跃
- **版本发布频率**：语义化版本（SemVer）中补丁版本的发布节奏反映了维护活跃度
- **下载量趋势**：npm trends 等工具显示的周下载量持续下降预示社区迁移

此外需关注该库是否有已知的"继任者"（如 `request` 库已于2020年被官方标记为废弃，推荐迁移至 `node-fetch` 或 `axios`）。

## 实际应用

**场景一：前端项目引入 UI 组件库**
工程师提交 PR，新增 `package.json` 中的 `antd@4.x` 依赖。审查者运行 `npx license-checker --summary` 确认 antd 使用 MIT 许可证，合规。再通过 `npm audit` 确认该版本无高危 CVE。最后检查 GitHub 仓库，近30天内有活跃提交和版本发布，通过审查。

**场景二：Java 微服务引入日志库**
2021年12月，`log4j-core 2.14.1` 被曝出 Log4Shell 漏洞（CVE-2021-44228，CVSS 10.0满分）。如果依赖审查流程中存在版本锁定检查，任何仍在 `pom.xml` 中使用该版本的 PR 将被自动拦截，强制要求升级至 2.17.1 或以上版本。

**场景三：Python 数据分析项目**
新引入 `pandas==1.3.0`，通过 `liccheck` 工具检查发现其使用 BSD-3-Clause 许可证，符合白名单。通过 `pip-audit` 确认无已知漏洞后合并。

## 常见误区

**误区一："只要版本号是最新的，就不需要检查漏洞"**
最新版本并不等同于安全版本。零日漏洞在被发现并修复之前，任何版本都可能受影响。此外，"最新版本"可能引入新的破坏性变更或尚未公开的安全问题。正确做法是以 CVE 数据库查询结果为准，而不是以版本号新旧为准。

**误区二："依赖的依赖（间接依赖）不需要审查"**
事实上，许多供应链攻击（Supply Chain Attack）正是通过间接依赖传递的。2021年的 `ua-parser-js` 事件中，攻击者劫持了该包的发布权限并注入恶意代码，所有间接依赖它的项目都受到波及。`npm audit` 和 `OWASP Dependency-Check` 均会递归扫描 lockfile 中的全部依赖树，审查范围应覆盖到 `package-lock.json` 或 `yarn.lock` 中的所有条目。

**误区三："许可证审查只在项目发布时做一次就够了"**
每次新增或升级依赖都可能带入新的许可证，且同一个包在不同版本之间可能更换许可证（如 HashiCorp 在2023年将其多个核心产品从 MPL-2.0 改为 BSL-1.1）。许可证检查应作为每个 PR 的自动化门控步骤，而非一次性审计。

## 知识关联

依赖审查在实践中与 **软件物料清单（SBOM，Software Bill of Materials）** 紧密配合——SBOM 是依赖审查的持久化输出，SPDX 和 CycloneDX 是两种主流 SBOM 格式。掌握依赖审查后，团队自然会产生"如何自动化维护 SBOM"的需求，这将引入 CI/CD 流水线中的供应链安全门控设计。

依赖审查也是 **代码审查检查清单（Code Review Checklist）** 中的固定条目之一，与逻辑正确性审查、性能审查并列，但其评估标准更加标准化，适合通过工具自动化完成大部分检查工作，审查者重点处理工具无法判断的"低维护度但业务上不得不使用"等灰色场景。