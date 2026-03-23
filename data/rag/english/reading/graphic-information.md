---
id: "graphic-information"
concept: "图表信息"
domain: "english"
subdomain: "reading"
subdomain_name: "阅读理解"
difficulty: 4
is_milestone: false
tags: ["应用"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 35.8
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.393
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 图表信息

## 概述

图表信息题是英语阅读理解中专门考查学生从柱状图、折线图、饼图、表格、信息图（infographic）等视觉化数据载体中提取、比较和推断信息的题型。与纯文字阅读不同，图表信息题要求考生同时解码视觉符号系统（图例、坐标轴、百分比标注）和英文标题、数据标签，属于"视觉文本"（visual text）的阅读范畴。

这一题型在标准化考试中的权重持续上升。以PISA（国际学生评估项目）为例，2018年测试框架明确将"阅读非连续性文本"（non-continuous text）列为核心阅读能力之一，其中图表类题目约占非连续性文本题的40%。在中国高考英语改革后的全国卷中，图表题通常以说明文或报告文章的附图形式出现，要求考生将图表数据与正文叙述相互印证。

掌握图表信息阅读的核心价值在于：现实英语语境中，科学期刊、商业报告、新闻报道大量使用图表辅助论证，能够快速读取图表中的峰值（peak）、谷值（trough）、趋势（trend）和比例关系（proportion），是学术英语（EAP）和职场英语的基础能力。

---

## 核心原理

### 1. 图表结构解码：四要素优先法

任何英语图表都包含四个必须优先定位的结构要素：

- **标题（title）**：界定图表描述的主题和时间范围，如 *"Percentage of Households with Internet Access, 2000–2020"*。标题中的时间段、地理范围、计量单位（%、million、per capita）直接决定数据的解读方式。
- **坐标轴标签（axis labels）**：X轴通常为分类变量（年份、国家、年龄段），Y轴为数值变量。混淆双轴是最常见的读题错误。
- **图例（legend）**：多组数据的图表中，图例区分各数据系列（如不同颜色代表不同国家）。
- **数据标注（data labels）**：部分图表在柱顶或折线节点标注具体数值，这些数字往往是判断"最大值/最小值"类题目的直接依据。

### 2. 数据比较的三种关系

图表题目中的问题几乎全部围绕以下三种数学关系设计：

**比较大小（comparison）**：识别最高值、最低值或排名。题目常用 *"Which country had the highest…"* 或 *"According to the chart, … was the least…"*。

**计算差值与比率（difference & ratio）**：例如题目问 *"How much greater was X than Y in 2015?"*，需要做减法；若问 *"X was approximately how many times that of Y?"*，需要做除法。饼图中，若某扇形标注为36%，则其与另一25%扇形的差值为11个百分点，二者之比约为1.44:1——这类精确计算在中等难度题中高频出现。

**趋势判断（trend）**：折线图和面积图专门考查趋势。英语描述趋势的词汇有严格的幅度区分：*rose sharply/dramatically*（急剧上升）vs. *increased slightly/gradually*（小幅上升）；*fluctuated*（波动）特指数据忽高忽低，不能用于单调变化的序列。

### 3. 信息图（Infographic）的特殊结构

信息图将文字说明、图标、图表混合排版，阅读路径不是从左到右的线性阅读，而是**分区块跳读（scanning by block）**。考生需要先识别信息图的分区标题（section header），再在目标区块内定位具体数据。例如，一张关于"全球咖啡消费"的信息图可能同时包含：左侧柱状图显示各国人均消费量、中间地图用颜色深浅表示产区分布、右侧文字框列出关键统计数据。题目问 *"Which country consumes the most coffee per person per year?"* 时，应直接跳读左侧柱状图，而非逐区阅读全图。

---

## 实际应用

**例题场景一：表格比较题**

某英语阅读题附有一张表格，列出2022年五个城市的平均房价（单位：thousand dollars）：

| City | 2020 | 2022 |
|------|------|------|
| A    | 320  | 410  |
| B    | 280  | 295  |
| C    | 450  | 430  |
| D    | 180  | 240  |

题目：*"Which city showed the greatest percentage increase from 2020 to 2022?"*

错误解法：直接找数值增幅最大的城市A（+90）。
正确解法：需计算**百分比增幅**（percentage increase = (新值−旧值)/旧值 × 100%）：A为28.1%，D为33.3%。答案是D，而非数值增量最大的A。

**例题场景二：折线图推断题**

折线图显示某网站2015–2022年用户数，2018年出现明显峰值后下降。题目问 *"Which of the following best describes the trend between 2018 and 2022?"*，正确选项应包含 *"declined"* 或 *"decreased"*，而非 *"fluctuated"*（因为该段数据单调下降，无波动）。

---

## 常见误区

**误区一：将"数值最大"等同于"增幅最大"**

如上文所示，绝对数值最大的项目不一定增幅最高。每当题目出现 *"grew the fastest"*、*"largest increase in percentage"* 等表述时，必须进行百分比计算，不能凭视觉判断柱子最高的那一项。

**误区二：把图表中未标注的数据当作"图表显示"的信息**

图表信息题中，只有图表**明确标注**的数据才算"图表信息"。例如，折线图只显示到2022年，题目选项若说 *"By 2025, the number will exceed…"* 属于推测，不是图表所示内容，通常是干扰选项。学生因主观推断而错选"图表未呈现的预测信息"是高频失分点。

**误区三：混淆"百分点"与"百分比变化"**

若某数据从40%上升到50%，变化量是**10个百分点（percentage points）**，但相对增幅是**25%（percentage change）**。英语题目中 *"increased by 10 percentage points"* 与 *"increased by 25%"* 描述的是同一变化，但表述完全不同，需要准确区分。

---

## 知识关联

图表信息阅读建立在**说明文阅读**的基础上：说明文阅读训练了学生识别"主题句—数据支撑—结论"这一论证结构，而图表信息题中，图表本身就是数据支撑层，正文是论证框架，两者结合考查的是学生将视觉数据映射回语言论证的能力。

图表信息阅读还与统计学基础词汇紧密相关，掌握 *mean、median、proportion、percentage、trend、correlation* 等高频学术词汇，是准确理解图表题干和选项的前提。在备考策略上，建议系统练习"数据描述类写作"（Task 1 of IELTS Academic），因为描述图表的写作练习能反向强化读图能力——能准确用英语写出折线图的趋势，意味着能准确读懂同类题目的选项表述。
