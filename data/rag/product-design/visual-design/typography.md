---
id: "typography"
concept: "字体排印学"
domain: "product-design"
subdomain: "visual-design"
subdomain_name: "视觉设计"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 字体排印学

## 概述

字体排印学（Typography）是研究如何通过文字的视觉呈现来传达信息的学科，涵盖字体选择、字号设定、行距调整、字间距控制以及段落编排等具体技术。它的核心目标是让文字既可读（Readable）又易读（Legible）——前者指读者能否顺畅阅读长段落，后者指读者能否在瞬间识别单个字符。

字体排印学的历史可追溯至1455年约翰内斯·古腾堡发明活字印刷术，他使用的哥特体（Blackletter）奠定了西方印刷排版的基础。20世纪初，包豪斯学校（Bauhaus）将无衬线字体系统化为现代设计语言，赫伯特·拜尔（Herbert Bayer）等人提出"通用字体"理念，极大影响了今天数字界面中无衬线字体的主导地位。

在产品设计领域，字体排印学直接影响用户完成任务的效率。研究显示，行距从1.0调整至1.5可使长文本阅读速度提升约8%，而字号低于12pt时错误率在小屏设备上会显著上升。掌握字体排印规则是构建设计系统（Design System）中文字规范的前提。

---

## 核心原理

### 字体分类与选择逻辑

西文字体主要分为衬线体（Serif）、无衬线体（Sans-serif）、等宽体（Monospace）和手写体（Script）四大类。衬线体如Times New Roman在笔画末端带有细小横线，引导眼睛横向移动，适合长篇印刷正文；无衬线体如Helvetica、Inter在屏幕低分辨率下边缘更清晰，是界面设计的主流选择。中文字体中，宋体对应衬线体逻辑，黑体对应无衬线体逻辑，在移动端正文推荐使用苹方（PingFang SC）或思源黑体（Source Han Sans）。

字体搭配遵循"对比原则"：标题与正文使用同族字体时应拉开字重差距（如Regular搭配Bold），或选用风格互补的两款字体（如衬线标题配无衬线正文），但同一页面不宜超过3种字体，否则视觉噪声会干扰信息层级。

### 字号层级系统

字号系统通常基于等比数列构建，经典的"模块化比例"（Modular Scale）使用1.25或1.414（√2）作为递进比率。以16px为基准字号时，按1.25倍递进可得：12px、16px、20px、25px、31px，分别对应辅助文字、正文、小标题、次级标题、主标题。

Material Design规范将字号层级明确定义为：Display（57px）、Headline（32px）、Title（22px）、Body（14-16px）、Label（11px）五个层级，每个层级搭配对应字重与行高。产品设计中通常将Body层级的字号定为最小可接受阅读字号——iOS Human Interface Guidelines规定最小可点击文字不低于11pt，正文推荐17pt（@1x屏）。

### 行距、字间距与可读性公式

行距（Line Height）的合理范围是字号的1.2至1.8倍。正文推荐1.4至1.6倍行距：字号16px时，行距设为24px（即1.5倍）是界面设计中最常见的设定。行距过小（低于1.2倍）导致上下行字母重叠区域增加，眼睛容易"跳行"；行距过大（超过2.0倍）则打断阅读节奏，使段落显得松散。

字间距（Letter Spacing / Tracking）规则与字号呈反比关系：**字号越大，字间距应适当收紧；字号越小，字间距应略微放宽**。具体数值上，标题（32px以上）的tracking可设为-0.5px至-1px，正文保持0，小于12px的辅助文字可设为+0.5px至+1px以提升识别率。

行长（Measure）也是可读性的关键变量。英文排版的理想行长为45至75个字符（每行），中文排版推荐每行18至36个汉字。超过这一范围时，眼睛在跨行时容易定位错误，导致重复阅读。

---

## 实际应用

**新闻资讯App正文排版**：正文使用思源黑体Regular，字号17px，行高26px（约1.53倍），每行约26个汉字，段落间距为行高的1.5倍（39px）。这一组合在6英寸屏幕上经过A/B测试，用户完整阅读率比14px/20px方案高出约12%。

**设计系统中的字体Token**：以Figma中构建设计系统为例，字体规范通常存储为Token变量：`font-size-body: 16px`，`line-height-body: 1.5`，`letter-spacing-body: 0`，`font-size-caption: 12px`，`letter-spacing-caption: 0.4px`。这种Token化方式使全局字号调整只需修改一个变量，而不必逐组件替换。

**深色模式下的字重补偿**：同一字体在深色背景（#121212底色）下的视觉重量会因光晕效应（Halation）而变粗，因此通常将正文字重从Regular降为Light，或将字号从16px降为15px，以维持与浅色模式相同的视觉密度。

---

## 常见误区

**误区一：认为字号越大可读性越高。** 字号超过一定阈值后，反而降低单屏可见信息量并增加跳行频率。在移动设备上，正文字号从16px增加到20px并不一定更易读，关键在于行距和行长的协同调整——字号放大而行距未相应放大，可读性会下降。

**误区二：将"字体"与"字型"混淆。** "字体"（Typeface）是指设计家族，如"Helvetica"；"字型"（Font）是指具体的单个变体文件，如"Helvetica Bold Italic 12pt"。在设计交付中混用这两个概念会导致开发环境中字重加载错误——工程师调用的是具体Font文件，而非Typeface家族名称。

**误区三：等宽字体适合所有数字显示场景。** 等宽字体（如Roboto Mono）因每个字符宽度相同，适合显示代码或数据表格中的数字列对齐，但用于正文段落时因字间距不均匀会产生视觉节律断裂，降低长文阅读流畅度。

---

## 知识关联

学习字体排印学需要先理解**视觉设计概述**中建立的视觉层级（Visual Hierarchy）概念——字号差异、字重变化正是构建视觉层级最直接的工具，字体排印学将这一概念具体化为可量化的数值规范。

字体排印学的间距与层级系统会直接影响后续学习**布局与栅格**时的内容区域划分：文字的行高和字号决定了栅格行（Row）的基础单位，8px栅格系统中行高24px（16px字号×1.5）正好是3个基础单元，这使文字与组件在垂直方向上自然对齐，避免像素偏移问题。掌握字体排印规则后，你将能为任何组件库制定完整的文字规范文档。