---
id: "design-doc-intro"
concept: "设计文档概述"
domain: "game-design"
subdomain: "design-docs"
subdomain_name: "设计文档"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "Game Design Workshop"
    author: "Tracy Fullerton"
    year: 2018
    isbn: "978-1138098770"
  - type: "textbook"
    title: "The Game Design Document"
    author: "Jason W. Bay"
    year: 2020
  - type: "conference"
    title: "One Page Designs"
    authors: ["Stone Librande"]
    venue: "GDC 2010"
scorer_version: "scorer-v2.0"
---
# 设计文档概述

## 概述

游戏设计文档（Game Design Document，GDD）是将游戏创意从"脑中想法"转化为"团队可执行规范"的核心载体。Tracy Fullerton 在《Game Design Workshop》（2018）中将其定义为"一份活的蓝图，描述游戏的每个系统、机制和体验目标，使所有团队成员对'我们在做什么'达成共识"。

然而，GDD 的形态在过去 20 年发生了剧变。1990 年代的 GDD 动辄 300-500 页（《DOOM Bible》1992 年版长达 200+ 页），而现代敏捷开发中，Stone Librande 在 GDC 2010 的经典演讲 "One Page Designs" 中展示了暴雪的做法：**整个游戏系统浓缩到一页纸上**——SimCity 团队用一页纸设计文档替代了传统 GDD，迭代速度提升了 4 倍。

## 设计文档的七种类型

| 文档类型 | 篇幅 | 受众 | 生命周期 | 用途 |
|---------|------|------|---------|------|
| 概念文档（Concept Doc） | 1-3 页 | 管理层/投资者 | 立项阶段 | "为什么做这个游戏" |
| 一页纸设计（One-Pager） | 1 页 | 全团队 | 贯穿全程 | 核心玩法的视觉化摘要 |
| 游戏设计文档（GDD） | 20-100+ 页 | 设计/开发团队 | 预制作→持续更新 | 完整的系统规范 |
| 技术设计文档（TDD） | 10-50 页 | 程序团队 | 预制作→Alpha | 架构和实现方案 |
| 关卡设计文档（LDD） | 5-20 页/关卡 | 关卡/美术/QA | 制作阶段 | 单个关卡的详细规范 |
| UI 线框图（Wireframe） | 按屏幕数 | UI/UX/前端 | 预制作→Beta | 界面流程和布局 |
| 用户故事（User Stories） | 1-3 句/条 | Scrum 团队 | Sprint 级别 | 单个功能的验收标准 |

**核心区别**：概念文档回答 **Why**（为什么做），GDD 回答 **What**（做什么），TDD 回答 **How**（怎么做），LDD 回答 **Where**（在哪里做）。

## GDD 的核心结构

经过行业 30 年演化，成熟 GDD 的标准章节（Fullerton 2018）：

```
1. 游戏概述
   ├─ 电梯演讲（1-2 句核心卖点）
   ├─ 目标平台与受众
   ├─ 对标作品（"X meets Y"）
   └─ 独特卖点（USP）

2. 核心机制
   ├─ 核心循环（Core Loop）图示
   ├─ 每个机制的规则描述
   ├─ 输入→处理→输出流程
   └─ 数值框架（初始参数范围）

3. 游戏世界
   ├─ 世界观/背景设定
   ├─ 关卡/区域列表与流程图
   └─ 艺术风格参考（Mood Board）

4. 角色/实体
   ├─ 玩家角色能力列表
   ├─ NPC/敌人行为描述
   └─ 物品/装备系统

5. UI/UX 流程
   ├─ 屏幕流程图（Screen Flow）
   ├─ HUD 布局
   └─ 菜单层级

6. 技术需求
   ├─ 引擎选择依据
   ├─ 网络架构（如适用）
   └─ 平台特殊要求

7. 项目计划
   ├─ 里程碑定义
   ├─ 团队结构
   └─ 风险清单
```

## 一页纸设计的力量

Stone Librande（GDC 2010）的方法论彻底改变了行业实践：

**核心理念**：如果你不能在一页纸上解释清楚，说明你自己还没想清楚。

一页纸设计的构成要素：
- **视觉为主**：图表、流程图、示意图占 70%+，文字仅做注释
- **核心循环居中**：页面中央是 Core Loop 图——一目了然游戏在"玩什么"
- **数值边界**：关键参数范围标注（不是精确值，是范围）
- **对标截图**：2-3 张参考游戏截图标注"我们要这个感觉"

实例——暴雪 SimCity（Librande 是首席设计师）：一页纸上包含城市模拟的资源流向图、区域类型矩阵、灾难触发条件，整个核心设计一目了然。新成员看 10 分钟就能理解游戏在做什么——传统 GDD 需要 3-5 天通读。

## 活文档 vs 死文档

| 特性 | 活文档（Living Doc） | 死文档（Dead Doc） |
|------|---------------------|-------------------|
| 更新频率 | 每次 Sprint 更新 | 写完后几乎不动 |
| 格式 | Wiki/Confluence/Notion | Word/PDF |
| 版本控制 | 内建历史记录 | 手动命名"v2_final_final" |
| 协作方式 | 多人实时编辑 | 单人撰写→邮件分发 |
| 跟踪 | 变更通知到相关人员 | 没人知道改了什么 |
| 结局 | 随项目进化 | 写完后被遗忘在硬盘上 |

**行业趋势**：2015 年后，Confluence + Jira 的组合在大型工作室（EA、育碧、Riot）中替代了 Word GDD。独立团队常用 Notion 或 HackMD。

关键数据：育碧蒙特利尔的内部调查（2019）显示，使用 Wiki 格式 GDD 的项目中 78% 的开发者"每周至少查阅一次设计文档"，而使用 Word 格式 GDD 的项目仅 23%。

## 谁写文档、什么时候写

| 阶段 | 产出文档 | 主要撰写者 | 审阅者 |
|------|---------|-----------|--------|
| 立项/Pitch | 概念文档 + 一页纸 | 创意总监/主策划 | 制作人/管理层 |
| 预制作 | GDD 初版 + TDD + 美术圣经 | 设计团队 + 技术总监 | 全团队 Review |
| 制作 | LDD + 用户故事 + UI 线框图 | 关卡策划 + UI 设计师 | 系统策划 + QA |
| Alpha | 数值平衡文档 + QA 测试计划 | 数值策划 + QA Lead | 设计总监 |
| 上线后 | 运营设计文档（Live Ops） | 运营策划 | 全团队 |

## 常见误区

1. **"先写完 GDD 再开发"**：瀑布式思维。现代流程是 GDD 随原型同步进化——先做 Prototype，验证核心机制，再将验证结果写入 GDD。否则你会花 3 个月写一份最终被推翻的文档
2. **GDD 写得越详细越好**：过度规范会抑制创意空间。Warren Spector（《杀出重围》设计师）说："GDD 应该告诉团队'不要做什么'，而不是规定每个细节"
3. **只有策划需要读 GDD**：程序需要知道系统边界，美术需要知道视觉目标，QA 需要知道预期行为。GDD 的真正读者是 **全团队**——如果某个章节只有策划能看懂，那它写得不好

## 知识衔接

### 先修知识
- **游戏设计概述** — 需要理解游戏设计的基本概念才能有效撰写设计文档

### 后续学习
- **GDD结构** — 深入 GDD 各章节的撰写规范和模板
- **一页纸概念** — Stone Librande 方法论的完整实践
- **UI线框图** — 界面设计流程和交互原型工具
- **流程图设计** — 系统逻辑和玩家流程的可视化
- **用户故事** — 敏捷开发中的需求拆解技术

## 参考文献

1. Fullerton, T. (2018). *Game Design Workshop* (4th ed.). CRC Press. ISBN 978-1138098770
2. Librande, S. (2010). "One Page Designs." GDC 2010.
3. Rogers, S. (2014). *Level Up! The Guide to Great Video Game Design* (2nd ed.). Wiley. ISBN 978-1118877166
4. Ryan, T. (1999). "The Anatomy of a Design Document." Gamasutra.
5. Schell, J. (2019). *The Art of Game Design* (3rd ed.). CRC Press. ISBN 978-1138632059
