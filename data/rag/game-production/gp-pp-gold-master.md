---
id: "gp-pp-gold-master"
concept: "Gold Master"
domain: "game-production"
subdomain: "production-pipeline"
subdomain_name: "制作管线"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Gold Master（金主版本）

## 概述

Gold Master（简称 GM），中文通称"金主版本"或"压盘母版"，是游戏开发周期中的最终可发布版本——一旦通过认证，该版本的代码与资产将被冻结，不得再做任何修改，直接用于物理压盘或数字商店上架。这一术语源自唱片工业：早期母版录制在镀金光盘上，故名"Gold Master"。游戏行业在光碟主机时代（PlayStation 1 时期，约 1994 年起）正式沿用这一概念，因为实体光盘一旦压制就无法撤回，任何 Bug 都将永久存在于玩家手中。

Gold Master 与 Beta 里程碑的本质区别在于：Beta 版本是"功能完整但仍可修复"的状态，而 GM 是"法律与技术意义上已可交货"的状态。在主机平台（如 PlayStation、Xbox、Nintendo Switch），GM 版本必须通过平台方的 Lot Check（洛特检测）/ TCR / TRC 合规审查，未获认证编号（Submission ID）则严禁发行。PC 或移动端虽无硬件厂商审核，但依然需要内部 GM 签署流程（Sign-off）确保版本锁定。

GM 版本的重要性不仅在于技术完整性，更在于法律与商业后果：若在 GM 后发现 P0 级崩溃缺陷，团队须重新走完整个认证流程，平均耗时 2～4 周，直接推迟发售日并触发零售商违约条款。

---

## 核心原理

### GM 版本标准（Gold Master Criteria）

GM 标准是一份由制作人、QA 主管和发行商三方共同签署的验收清单，核心判定规则通常如下：

- **零 P0/P1 缺陷**：P0 = 游戏崩溃或数据丢失；P1 = 主线流程阻断。GM 候选版本（GM Candidate，简称 GMC）必须在连续 48～72 小时回归测试中保持零新增 P0/P1。
- **平台合规分数达标**：索尼 TRC（Technical Requirements Checklist）、微软 TCR（Technical Certification Requirements）和任天堂 LOT CHECK 均提供评分标准，任一必须项（Mandatory Item）不通过即判为失败。
- **首发版本内容锁定**：DLC、补丁内容已从 GM 分支剥离，主包体积符合平台限制（例如 PS5 蓝光碟单层上限约 100 GB）。
- **版本号冻结**：GM 版本须具备唯一可追溯的 Build ID，与 Git/Perforce 标签一一对应，不可覆盖。

### 认证提交流程（Submission Pipeline）

以 PlayStation 为例，标准提交流程分为五个阶段：

1. **提交 GMC**（GM Candidate）：将候选版本上传至索尼开发者门户（DevNet），填写 Submission Form，注明首发地区与评级（CERO/ESRB/PEGI）证书编号。
2. **Lot Check 自动扫描**：平台方工具自动检测约 200+ 条技术必须项，例如 PS Button 响应时间 ≤ 2 秒、存档图标格式、Trophy 配置完整性。
3. **人工功能测试**：平台 QA 团队按 TCR/TRC 逐条手工验证，典型周期为 5～10 个工作日。
4. **结果反馈**：Pass（发放 Lot Number，即可压盘）或 Fail（附缺陷报告，须修复后提交下一个 GMC，如 GMC2、GMC3）。
5. **Master Disc 生成**：获得 Lot Number 后，压盘工厂依据该编号生成实体母盘，或数字平台激活发布权限。

### 发布检查清单（Release Checklist）

GM 签署前须完成的发布检查清单通常包含以下具体条目：

| 检查项 | 负责方 | 标准 |
|--------|--------|------|
| 首发日 Day-1 补丁与 GM 主包兼容性 | 工程 + QA | 全平台无崩溃 |
| 年龄评级证书有效期 | 制作人 | ESRB/PEGI/CERO 均已到位 |
| 本地化文本终审 | 本地化主管 | 无遗漏占位符（如 `[TODO]`、`XXX`） |
| 音频许可证到期日 | 法务 | 所有授权音乐覆盖发售后 ≥ 5 年 |
| 防作弊与反盗版模块版本 | 安全工程 | 与商定版本一致 |
| 服务器端配置快照 | 后端工程 | 与 GM 客户端版本号绑定 |

---

## 实际应用

**案例 1：《赛博朋克 2077》的 GM 教训**  
CD Projekt Red 于 2020 年 12 月发布的 GM 版本因 PS4 平台严重性能问题，索尼随后将其从 PS Store 下架——这是平台方极少见的"撤销上线"操作。这一事件直接推动了行业对"主机性能专项 GMC 测试"的重视，多家 AAA 开发商随后增设了针对 Base Console（非 Pro/X 增强型主机）的专属 GMC 回归套件。

**案例 2：数字发行的 GM 流程简化**  
Steam 平台无独立 Lot Check 环节，开发商在 Steamworks 后台上传 Build 后，内部执行 GM 签署即可解锁"上线"权限。典型流程为：制作人在 GM 签署文件上附上 Build ID（如 `steamdb.info/build/XXXXXXXX`），并由 QA 主管确认最终回归测试报告，整个周期最短可压缩至 24 小时。

**案例 3：Nintendo Switch 卡带容量与 GM 的关系**  
Switch 游戏卡带规格（1GB / 2GB / 4GB / 8GB / 16GB / 32GB）须在 GM 提交前 6～8 周向任天堂预订，因为卡带芯片交货周期较长。若 GM 版本包体超过预订容量，开发团队必须削减内容或将部分资源转为强制下载——这一硬件约束使 GM 的包体管理成为独立的里程碑任务。

---

## 常见误区

**误区 1："Day-1 补丁可以弥补 GM 的缺陷，所以 GM 标准可以放松"**  
这一想法忽视了两个事实：第一，实体光盘用户在补丁下载前仍会遭遇 GM 版本的缺陷；第二，索尼和微软对 Day-1 补丁同样有独立的 TCR/TRC 合规审核，若补丁本身引入新的必须项违规，将形成"补丁也需修复补丁"的连锁延误。GM 版本的质量底线不因补丁存在而降低。

**误区 2："GM 版本一旦通过认证就不能再改动任何文件"**  
实体压盘版的 GM 确实完全冻结，但数字版（如 Steam、Epic Games Store）可以在不重新走认证流程的情况下推送新 Build——这并非"修改 GM"，而是通过补丁机制发布后续版本（Post-GM Patch），两者在版本管理上须严格区分，分支命名规范通常为 `release/gm` 与 `release/patch-1.0.1`。

**误区 3："内部 Sign-off 等同于平台认证通过"**  
内部 GM 签署只代表开发商认为版本达标，并不具备平台法律效力。在主机平台，未获 Lot Number / Submission ID 的版本即便内部签署完毕，也无法进入压盘或上架流程。曾有团队将"内部 GM 签署日期"误当作"可对外宣传的发售保证"，导致对外承诺与平台审核周期冲突，最终被迫公开推迟发售。

---

## 知识关联

**前置概念：Beta 里程碑**  
Beta 里程碑确立了"功能完整、内容锁定"的状态，是进入 GMC 测试循环的前提。Beta 阶段遗留的 P2/P3 缺陷必须在 GMC 提交前全部降级或关闭，否则平台 Lot Check 的人工测试极可能将其升级为 P1。

**后续概念：上线后运维**  
GM 签署并不意味着团队工作结束。上线后运维（Live Ops）团队从 GM 锁定版本出发，建立热修复（Hotfix）分支和服务器端配置更新机制。GM 版本的 Build ID 成为线上版本追踪的基准锚点，所有后续补丁的兼容性均以 GM 版本为基线进行回归测试。两者之间存在明确的版本控制交接节点：GM 分支合并入 `main` 后，`release/live` 分支正式接管后续迭代。