---
id: "ld-doc-intro"
concept: "LD文档概述"
domain: "level-design"
subdomain: "ld-documentation"
subdomain_name: "LD文档"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "reference"
    title: "An Architectural Approach to Level Design (2nd Edition)"
    author: "Christopher W. Totten"
    year: 2019
    isbn: "978-0815361367"
  - type: "reference"
    title: "Level Design: Processes and Experiences"
    author: "Christopher W. Totten (Editor)"
    year: 2017
    isbn: "978-1498745055"
  - type: "reference"
    title: "Game Design Workshop (4th Edition)"
    author: "Tracy Fullerton"
    year: 2018
    isbn: "978-1138098770"
scorer_version: "scorer-v2.0"
---
# LD文档概述

## 概述

关卡设计文档（Level Design Document, LDD）是将关卡设计者脑中的**空间构想、玩法意图和叙事编排**转化为团队可执行信息的核心载体。Christopher Totten 在《An Architectural Approach to Level Design》（2019, Ch.12）中指出："关卡设计文档的价值不在于它写得多完美，而在于它能让美术、程序和QA**不用口头询问**就能理解设计意图"。

在实际生产中，LDD 不是一份文档而是一**组**文档——从高层概览到具体遭遇战的细节，每种文档服务于不同受众和不同生产阶段。

## 核心概念

### 1. 关卡设计文档的类型体系

按生产流程排列：

| 文档类型 | 生产阶段 | 核心内容 | 主要受众 | 典型格式 |
|----------|---------|---------|---------|---------|
| **关卡概览文档（Level Overview）** | 预生产 | 关卡定位、核心体验目标、时长估算 | 制作人、主设计师 | 1-2 页文字 + 情绪板 |
| **关卡流程图（Level Flowchart）** | 预生产→白盒 | 空间连接关系、关键门/锁、分支路径 | 全团队 | 流程图工具（Draw.io/Miro） |
| **俯视图（Top-Down Map）** | 白盒 | 平面布局、比例尺、关键标注 | LD、美术、QA | 引擎截图 + 标注图层 |
| **遭遇战文档（Encounter Doc）** | 白盒→灰盒 | 敌人配置、触发条件、难度参数 | LD、战斗策划、程序 | 表格 + 示意图 |
| **脚本事件文档（Scripted Event Doc）** | 灰盒→正式 | 过场动画、对话触发、环境变化时序 | 叙事、程序、动画 | 时间线图 + 脚本伪代码 |
| **测试检查单（QA Checklist）** | 全程 | 验收条件、已知问题、回归测试项 | QA、LD | 勾选表 |

**关键洞察**：这些文档是**分层递进**的，不是彼此独立的。概览文档确定方向 → 流程图确定结构 → 俯视图确定空间 → 遭遇战/脚本确定细节。修改上层文档通常意味着下层需要更新。

### 2. 关卡概览文档的核心要素

一份有效的关卡概览应包含：

**核心体验目标（Experience Goal）**：
- 用一句话描述玩家的**情感体验**，而非机制。
- ✅ "玩家应感受到被围困的绝望，然后通过一个隐藏路径获得戏剧性翻转"
- ❌ "关卡包含 3 波敌人和 1 个Boss"（这是配置，不是体验目标）

**节奏曲线（Pacing Curve）**：
- Totten 引用建筑学概念"序列"（sequence）：空间体验应有节奏——紧张-释放-紧张的交替。
- 简单的 ASCII 节奏图：

```
强度
 ↑   ★Boss
 │  ╱╲
 │ ╱  ╲    ★遭遇2
 │╱    ╲  ╱╲
 │ 探索  ╲╱  ╲___ 叙事过场 ___
 │────────────────────────────→ 时间
 开始                        结束
```

**参考作品（Reference）**：
- 2-3 个具体的游戏关卡参考，标注要借鉴的具体元素。
- "参考《The Last of Us Part II》西雅图第一天的开放探索结构，特别是垂直空间利用。但我们的战斗密度更高，更接近《Doom Eternal》的竞技场节奏。"

**规模估算**：
- 预期游玩时间（首次/重玩）
- 预估美术工作量（资产数量级）
- 技术风险标注（"需要新的水体系统"、"依赖未完成的AI巡逻行为"）

### 3. 俯视图的标注规范

俯视图是 LD 日常沟通中使用频率最高的文档。有效的标注系统：

**空间标注**：
- 颜色编码：可到达区域（绿）、危险区域（红）、不可到达/装饰区域（灰）
- 比例尺标注：至少在图上标出一个已知尺寸（"这个走廊宽 3m"）
- 高度信息：用等高线或颜色深浅表示垂直层次

**玩法标注**：
- 玩家出生/目标点：明确的图标
- 敌人位置和巡逻路径：不同颜色的点和线
- 掩体/可互动物体：统一图标
- 门/锁/钥匙关系：标准符号（门=实线框，锁=×，钥匙=★）
- 触发区域：虚线框 + 触发条件文字

**Fullerton 的建议**（*Game Design Workshop*, 2018, Ch.14）："俯视图不需要好看——它需要**准确**和**可更新**。如果更新一次需要一天，团队会停止更新它。"

### 4. 文档的版本管理

LDD 最大的实践问题是**文档过时**。解决方案：

**就近原则**：
- 关卡参数尽量在引擎中配置（DataTable/ScriptableObject），不在文档中硬编码
- 文档记录"设计意图"，引擎保存"当前数值"
- 这样改参数不需要同步改文档

**版本控制集成**：
- LDD 放在与代码相同的版本控制系统中（Git/Perforce）
- 每次关卡重大迭代时更新文档并关联 commit
- 用 Markdown 而非 Word——方便 diff 和 merge

**活文档（Living Document）**：
- 不追求"完美的初始文档"。第一版只需要概览 + 流程图
- 随生产推进逐步补充遭遇战和脚本细节
- Totten 建议："宁可有一份只有 60% 内容但持续更新的文档，也不要一份完美但从不更新的文档"

### 5. 文档驱动 vs 引擎驱动的工作流

两种主流方法论的对比：

| 维度 | 文档驱动 | 引擎驱动 |
|------|---------|---------|
| **流程** | 先写完文档 → 再进引擎搭建 | 直接在引擎中搭白盒 → 回填文档 |
| **适用** | 大团队（20+ LD）、多关卡并行 | 小团队（1-5 LD）、快速迭代 |
| **优势** | 评审成本低、方向风险小 | 空间感直觉更准确、迭代更快 |
| **劣势** | 文档→实际的转译损耗 | 缺乏记录，知识在人脑中 |
| **代表** | Ubisoft（Assassin's Creed） | id Software（Doom） |

**实践建议**：大多数团队采用混合方式——概览和流程图先于搭建，但遭遇战细节在白盒测试后补写。

## 常见误区

1. **"文档越详细越好"**：过度详细的文档维护成本极高。关卡迭代时（平均 3-5 次大改）文档跟不上就变成误导性信息——比没有文档更危险。
2. **"写完就不管了"**：LDD 不是一次性交付物。Gregory 指出 50% 以上的关卡设计问题来自"文档说的和游戏里做的不一致"。
3. **"只写给自己看"**：常见的初级 LD 错误。文档的价值是让**其他人**理解你的设计。如果美术看不懂你的空间标注，那标注就没用。
4. **"用 PowerPoint 就够了"**：PPT 难以版本控制、难以全文搜索、难以多人并行编辑。Markdown + Git 或 Notion/Confluence 是更好的选择。
5. **在文档中硬编码数值**：敌人血量、伤害数值、触发距离等参数应该在引擎 DataTable 中配置，文档只记录设计意图（"这波敌人的压力应该中等"）。

## 知识衔接

### 先修知识
- **关卡设计概述** — 理解关卡设计的目标、流程和术语

### 后续学习
- **关卡概览文档** — 深入预生产阶段的文档方法
- **关卡流程图** — 空间结构和关键路径的可视化
- **俯视图设计** — 平面布局的标注规范和工具
- **遭遇战文档** — 战斗设计参数的文档化方法
- **脚本事件文档** — 叙事和脚本事件的时序描述

## 延伸阅读

- Totten, C. W. (2019). *An Architectural Approach to Level Design* (2nd ed.), Ch.12: "Documenting Level Design". CRC Press. ISBN 978-0815361367
- Totten, C. W. (Ed.) (2017). *Level Design: Processes and Experiences*. CRC Press. ISBN 978-1498745055
- Fullerton, T. (2018). *Game Design Workshop* (4th ed.), Ch.14: "Playtesting". CRC Press. ISBN 978-1138098770
- World of Level Design: [Documentation Best Practices](https://worldofleveldesign.com/) — 实用 LDD 模板和案例
- GDC Vault: "Level Design Documentation" talks — 来自 Naughty Dog、Valve、Ubisoft 的工业实践分享
