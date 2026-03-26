---
id: "html-basics"
concept: "HTML基础"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 2
is_milestone: false
tags: ["Web"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.469
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# HTML基础

## 概述

HTML（HyperText Markup Language，超文本标记语言）是用于描述网页结构的标准语言，由蒂姆·伯纳斯-李（Tim Berners-Lee）于1991年首次发布，最初版本仅包含18个标签。HTML不是编程语言，它不包含逻辑判断或循环结构，而是一种**标记语言**，通过标签（tag）为内容赋予结构含义，告诉浏览器"这段文字是标题""这里是一张图片""这些项目构成一个列表"。

当前的标准版本是**HTML5**，由W3C和WHATWG于2014年联合正式发布。HTML5引入了语义化标签（如 `<article>`、`<section>`、`<nav>`）、原生音视频支持（`<audio>`、`<video>`）以及Canvas绘图接口，彻底改变了网页开发方式。对于AI工程的Web前端开发，HTML是所有用户界面的起点——无论是模型推理结果展示页面、数据可视化仪表盘，还是训练进度监控面板，都必须以HTML文档为骨架。

## 核心原理

### 文档结构与DOCTYPE声明

每个合法的HTML5文档都必须以 `<!DOCTYPE html>` 开头，这行声明告知浏览器使用HTML5标准解析文档，而非更早期的怪异模式（Quirks Mode）。完整的最小HTML5文档结构如下：

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题</title>
  </head>
  <body>
    <!-- 可见内容写在这里 -->
  </body>
</html>
```

`<head>` 中的内容不直接显示给用户，但包含字符编码声明（`charset="UTF-8"` 防止中文乱码）、视口设置（移动端适配必须）和页面标题。`<body>` 中的内容才是浏览器渲染并呈现给用户的部分。

### 标签、元素与属性

HTML的基本语法单位是**元素（element）**，由开始标签、内容和结束标签三部分组成，例如 `<p>这是一个段落</p>`。部分标签是**自闭合标签（void element）**，没有内容和结束标签，如 `<img>`、`<br>`、`<input>`、`<meta>`。

**属性（attribute）**写在开始标签内，提供关于元素的额外信息，格式为 `name="value"`。几个对AI前端开发特别重要的属性：
- `id`：在文档中唯一标识一个元素，JavaScript通过 `document.getElementById()` 定位它
- `class`：为元素分配一个或多个类名，CSS和JavaScript批量操作时使用
- `data-*`：自定义数据属性，如 `data-model="gpt4"` 可在HTML标签中存储与元素相关的业务数据，供JavaScript读取

### 语义化标签与文档大纲

HTML5的语义化标签是与旧版HTML最显著的区别。使用 `<div>` 和 `<span>` 可以实现同样的视觉效果，但语义化标签让文档结构对机器（搜索引擎爬虫、屏幕阅读器）可理解。常用语义化标签对应的语义如下：

| 标签 | 含义 |
|------|------|
| `<header>` | 页面或区块的页眉 |
| `<nav>` | 导航链接区域 |
| `<main>` | 页面主体内容，每个文档只能有一个 |
| `<article>` | 独立完整的内容，如一篇博客文章 |
| `<section>` | 主题性内容分组 |
| `<aside>` | 与主内容相关但可独立存在的侧边内容 |
| `<footer>` | 页面或区块的页脚 |

标题标签 `<h1>` 到 `<h6>` 共6级，构成文档的层级大纲。正确的做法是每个页面只有一个 `<h1>`，下级标题按数字顺序递进，不可跳级使用（如从 `<h2>` 直接跳到 `<h4>`）。

### 表单与数据输入

HTML表单是收集用户输入的核心机制，在AI前端中常用于提交文本给模型推断、上传图片进行分类等场景。`<form>` 元素的两个关键属性是 `action`（数据提交的目标URL）和 `method`（`GET` 或 `POST`）。

`<input>` 标签的 `type` 属性决定了输入类型，HTML5新增了 `number`、`range`、`date`、`file`、`email` 等类型，浏览器会自动提供对应的输入界面和基础验证。例如：
```html
<input type="range" min="0" max="1" step="0.01" id="temperature">
```
以上代码可直接生成调节模型温度参数的滑块控件，无需任何JavaScript。

## 实际应用

**构建AI模型结果展示页面**：用 `<main>` 包裹主内容区，`<figure>` 和 `<figcaption>` 组合展示模型生成的图片及说明文字，`<table>` 结合 `<thead>`、`<tbody>`、`<tfoot>` 展示分类置信度排名。

**图片标签的完整写法**：`<img src="result.png" alt="模型预测热力图" width="600" height="400">`。`alt` 属性在图片加载失败时显示替代文字，同时供屏幕阅读器朗读，是无障碍访问的基础要求，不可省略。

**超链接与锚点**：`<a href="#conclusion">跳转到结论部分</a>` 中，`href` 以 `#` 开头表示页面内锚点跳转；`target="_blank"` 属性使链接在新标签页打开，但应配合 `rel="noopener noreferrer"` 防止安全漏洞。

## 常见误区

**误区一：混淆块级元素与行内元素的默认行为**。`<div>` 是块级元素，独占一行；`<span>` 是行内元素，与周围内容同行显示。初学者常把 `<span>` 当容器包裹大段内容，或期望 `<div>` 和其他内容并排，却不知道需要CSS介入。特别注意：`<p>` 标签内不能嵌套 `<div>`，浏览器会自动修复这种错误的嵌套，但修复结果往往不符合预期。

**误区二：把HTML标签当样式工具使用**。`<b>` 和 `<strong>` 视觉上都加粗，但 `<strong>` 表示内容"重要性"，屏幕阅读器会用重音朗读它；`<i>` 和 `<em>` 都显示斜体，但 `<em>` 表示"强调"。用 `<h3>` 只是因为字号合适，而非因为内容真的是三级标题，这破坏了文档大纲，影响SEO和无障碍性。样式调整应交给CSS，HTML标签只传达语义。

**误区三：认为HTML验证错误不影响实际效果**。浏览器的容错机制会自动修复许多HTML错误（如未闭合标签、错误嵌套），但不同浏览器的修复策略不同，导致同一份错误HTML在Chrome和Firefox中渲染结果不一致。使用W3C的在线验证器（validator.w3.org）检查HTML合法性，能在早期发现跨浏览器兼容问题。

## 知识关联

学习HTML之后，**CSS基础**负责控制HTML元素的视觉呈现——颜色、布局、动画，二者分工明确：HTML管结构，CSS管样式。**JavaScript基础**则赋予HTML动态能力，通过DOM（Document Object Model）API操作已解析的HTML文档树，例如 `document.querySelector('.result-box')` 选取class为 `result-box` 的元素并修改其内容。

本节学习的语义化标签和 `alt` 属性写法，直接构成**Web无障碍（a11y）**的基础实践，a11y规范WCAG 2.1中的多项成功标准（如1.1.1非文本内容）要求HTML结构正确表达内容语义。**Canvas与WebGL**需要在HTML中插入 `<canvas id="myCanvas" width="800" height="600"></canvas>` 作为绘图载体，JavaScript再通过 `getContext('2d')` 或 `getContext('webgl')` 获取绘图上下文，HTML提供的这个容器元素是一切图形渲染的起点。