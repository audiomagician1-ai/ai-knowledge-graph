---
id: "pub-pr-console-submission"
concept: "主机送审"
domain: "game-publishing"
subdomain: "platform-rules"
subdomain_name: "平台规则"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 主机送审

## 概述

主机送审是指游戏开发商在将游戏发布到PlayStation、Xbox或Nintendo Switch平台之前，必须通过平台方设置的技术合规性审查流程。三大主机平台分别使用不同的认证体系：索尼的**TRC**（Technical Requirements Checklist）、微软的**TCR**（Title Certification Requirements）、任天堂的**LOT CHECK**。这些认证流程不仅检验游戏的技术稳定性，还包括内容规范、UI交互标准、网络功能等数十项乃至数百项具体要求。

主机送审制度起源于任天堂在1980年代为应对"雅达利冲击"（Atari Shock）而建立的质量管控体系。1983年北美游戏市场崩溃后，任天堂于1985年推出NES时引入严格的第三方游戏授权审查机制，此后索尼和微软分别在PS1和Xbox时代跟进建立各自的认证体系。今天的主机送审流程已演化为数百页技术文档所规定的系统性工程，是主机平台区别于移动端开放市场的核心门槛机制。

对于发行商而言，主机送审的周期和成本直接影响上线计划。PlayStation的首次送审周期通常为**5个工作日**，但若Fail（未通过）则需要修复后重新提交，整个认证周期可能延伸至数周甚至数月，直接导致发售日期推迟及额外开发成本。

---

## 核心原理

### TRC / TCR / LOT CHECK 的结构差异

三大平台的认证文档在结构上存在显著差别。PlayStation的TRC文档通常包含**MANDATORY（强制要求）**和**CONDITIONAL（条件要求）**两类条目，前者是所有游戏必须满足的绝对标准，后者仅在游戏使用了特定功能（如网络、DLC）时触发。Xbox TCR同样分为强制与推荐，但Xbox的认证通过**XGS（Xbox Game Studios）认证门户**线上提交，流程比PlayStation更自动化。任天堂的LOT CHECK则以提交**ROM母版**为核心，由任天堂内部团队实际运行测试，审查标准相对不透明，开发者需要持有有效的任天堂开发者账号（Nintendo Developer Portal账号）才能获取完整的LOT CHECK条目清单。

### 常见强制性要求类别

各平台TRC/TCR条目数量庞大，但以下几类是最常见的强制性审查重点：

- **系统功能集成**：游戏必须正确响应系统级操作，例如PS5要求游戏在收到"休眠模式"信号后15秒内保存进度并完成挂起；Xbox要求游戏在接收到系统叠加层（Guide Button）呼出信号时立即暂停或最小化。
- **崩溃与稳定性**：PS4/PS5平台的TRC明确规定，游戏在送审测试期间不得出现任何未处理异常导致的强制退出（CUSA错误码类型崩溃），否则直接标记为Critical Fail。
- **存档与数据安全**：TRC要求游戏必须处理存储设备已满、存档文件损坏等异常状态，不能因此导致游戏崩溃或数据丢失。
- **trophy/成就规范**：PlayStation规定每款游戏必须包含至少一个Platinum Trophy（铂金奖杯），且所有Trophy描述不得有文字错误；Xbox成就的总Gamerscore须等于**1000G**（基础版）。
- **额定评级标志显示**：游戏主界面必须在规定位置显示ESRB/PEGI/CERO等区域评级标志，且标志尺寸不得低于平台规定的最小像素值。

### 送审提交流程

以PlayStation为例，整个送审流程分为以下几个阶段：

1. **开发者注册与权限获取**：通过PlayStation Partners（partners.playstation.com）申请发行商账号，获得Dev Kit（开发机）及TRC文档访问权限。
2. **自检（Self-Assessment）**：发行商必须使用官方提供的TRC自检表，逐条核对并填写说明，生成自检报告后一并提交。
3. **构建版本提交**：上传符合规范的Master Submission Package，包含游戏ROM/package文件、自检报告、评级证书、营销资产。
4. **平台方审查**：索尼QA团队对提交版本进行测试，通常5个工作日内返回Pass或Fail结果；若Fail，反馈报告将注明具体的TRC条目编号及复现步骤。
5. **迭代修复与重提**：开发商修复问题后重新提交，平台方对修改内容进行针对性复查（Recheck），收费通常低于首次全量审查。

---

## 实际应用

**典型Fail案例——存档异常**：某款独立RPG在送审PlayStation 4时收到Fail反馈，问题定位在TRC条目"SAVE-05"：当存储空间不足时，游戏弹出提示框后若玩家选择"忽略"，游戏直接崩溃而非正常继续运行。开发团队修复逻辑判断分支后重新提交，第二次通过。此类问题在首次送审中极为常见，建议在送审前专门针对边界存储条件做回归测试。

**跨平台同步送审的时间规划**：若一款游戏计划在PS5、Xbox Series和Switch三平台同日发售，实践中建议在目标发售日**至少提前8周**完成最终Gold Master构建，预留各平台同步送审及至少一次Fail修复的缓冲时间。三个平台的认证不能"合并"提交，必须分别向各平台独立进行，任何一个平台Fail都不影响其他平台的审查进度。

**任天堂LOT CHECK的特殊要求**：Switch游戏的LOT CHECK对**主题内容的区域分级一致性**要求极严，若游戏在日本使用CERO D评级，而提交的内容版本中包含仅在欧美版本开放的血腥表现，LOT CHECK会直接拒绝，要求提交区域差异化构建版本。

---

## 常见误区

**误区一：通过TRC自检就等于会通过平台审查**
TRC自检报告是开发商自行填写的，平台QA团队会用实际操作验证每一项关键条目。自检勾选"Pass"的条目，在平台实测中仍可能因边界情况（如特殊手柄配置、特定网络环境）被判定为Fail。自检报告的作用是帮助开发商系统整理状态，而非替代平台方的独立测试。

**误区二：主机送审只检查"Bug"**
TRC/TCR包含大量非Bug类要求，例如UI字体最小磅数规定（PS5要求HUD文字不得小于某一可读阈值）、手柄振动强度上限、语言文本的完整性（不得出现占位字符如"XXXXXX"）。这些不是传统意义上的程序Bug，却是导致Fail的高频原因，尤其对首次送审的独立开发团队而言容易被忽视。

**误区三：Xbox认证比PS更宽松**
微软Xbox的TCR在某些条目上实际更为严格，尤其是**辅助功能（Accessibility）**相关要求。自2022年起，Xbox TCR新增了多项无障碍游戏功能的强制性条目，包括字幕显示选项、色盲模式支持等，而这些在PlayStation TRC中仍属推荐而非强制。

---

## 知识关联

学习主机送审之前，应先掌握**应用审核应对**的基本思路，包括如何系统整理审查反馈、管理修复迭代周期，以及如何与平台开发者支持团队沟通——这些技能在主机送审流程中同样直接适用，但主机平台的沟通渠道更为正式，所有沟通须经由官方Partner Portal的工单系统进行。

完成主机送审的学习后，下一个重要议题是**内购规则**。主机平台对游戏内付费功能有独立于TRC技术审查之外的商业政策审查：PlayStation对DLC定价区间、Xbox对订阅型Pass内容的包含规则、任天堂对随机抽取内容（扭蛋机制）的信息披露要求，都是在通过TRC后还需单独合规的内容，两者的审查流程互相独立但时间节点高度交织。