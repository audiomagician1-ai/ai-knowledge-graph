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

HTML（HyperText Markup Language，超文本标记语言）是构建网页内容结构的标准语言，由蒂姆·伯纳斯-李（Tim Berners-Lee）于1991年首次发布，当时仅包含18个标签。HTML不是编程语言，它不具备逻辑运算或变量存储能力，其唯一职责是通过标签（tag）描述文档的语义结构——哪里是标题、哪里是段落、哪里是图片链接。

HTML经过多个版本迭代，目前主流规范是HTML5，由WHATWG（Web超文本应用技术工作组）持续维护，于2014年由W3C正式推荐。HTML5引入了`<article>`、`<section>`、`<nav>`等语义化标签，以及`<canvas>`、`<video>`、`<audio>`等多媒体原生支持标签，彻底取代了过去依赖Flash插件的网页媒体方案。

在AI工程的Web前端方向中，HTML是模型推理结果展示界面的骨架。无论是展示大模型对话的聊天界面，还是可视化图表的容器，还是表单收集用户输入传递给后端API，HTML定义的DOM（文档对象模型）树是JavaScript操作页面的基础，也是浏览器渲染引擎解析页面的起点。

## 核心原理

### 标签、元素与属性的基本语法

HTML文档由元素（element）构成，每个元素通常由开始标签、内容和结束标签三部分组成，例如`<p>这是一段文字</p>`。部分元素为空元素（void element），只有开始标签，无法包含子内容，例如`<img>`、`<br>`、`<input>`、`<meta>`。

属性（attribute）写在开始标签内，以`名称="值"`的形式出现，用于为标签附加额外信息。例如`<a href="https://example.com" target="_blank">链接</a>`中，`href`指定跳转地址，`target="_blank"`指定在新标签页打开。属性值中双引号是HTML5推荐写法，单引号也合法，但完全省略引号仅在值不含空格时有效。

### HTML文档的基本骨架结构

一个合法的HTML5文档必须以`<!DOCTYPE html>`声明开头（不区分大小写），这行声明告知浏览器以标准模式（standards mode）而非怪异模式（quirks mode）渲染页面——两种模式在盒模型计算上存在关键差异。完整骨架如下：

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面标题</title>
  </head>
  <body>
    <!-- 可见内容放在这里 -->
  </body>
</html>
```

`<head>`内的内容不直接显示在页面中，但控制页面元数据：`<meta charset="UTF-8">`声明字符编码为UTF-8，防止中文乱码；`<meta name="viewport">`控制移动端视口缩放行为，是响应式设计的前提条件。

### 语义化标签与非语义化标签的区别

HTML5将标签分为语义化与非语义化两类。语义化标签如`<header>`、`<main>`、`<footer>`、`<nav>`、`<h1>`至`<h6>`、`<strong>`、`<em>`，其标签名本身传达了内容的含义；非语义化标签如`<div>`和`<span>`仅作为通用容器，本身不传达任何语义信息。

使用`<h1>`到`<h6>`构建标题层级时，页面中`<h1>`通常只出现一次，表示最重要的主标题，搜索引擎爬虫和屏幕阅读器（如NVDA、JAWS）都依赖这一层级关系解析页面结构。错误地使用`<b>`（粗体样式）代替`<strong>`（语义强调），会导致屏幕阅读器无法识别重点内容，这直接影响后续Web无障碍（a11y）的实现。

### 常用标签分类速览

- **文本内容**：`<p>`（段落）、`<h1>`-`<h6>`（标题）、`<blockquote>`（引用块）、`<code>`（代码）、`<pre>`（预格式化文本）
- **链接与媒体**：`<a>`（超链接）、`<img>`（图片，必须含`alt`属性）、`<video>`、`<audio>`
- **列表**：`<ul>`（无序列表）、`<ol>`（有序列表）、`<li>`（列表项）、`<dl>`/`<dt>`/`<dd>`（定义列表）
- **表格**：`<table>`、`<thead>`、`<tbody>`、`<tr>`（行）、`<th>`（表头单元格）、`<td>`（数据单元格）
- **表单**：`<form>`、`<input>`、`<textarea>`、`<select>`、`<button>`、`<label>`

## 实际应用

**AI对话界面的消息结构**：构建类ChatGPT的对话界面时，每条消息可用`<article>`包裹，用户消息和AI回复通过`class`属性区分样式，消息内的代码块使用`<pre><code>`标签对保持换行和缩进，这比直接用`<div>`嵌套在语义上更规范，也方便JavaScript通过`querySelectorAll('code')`批量添加代码高亮。

**数据展示表格**：在展示模型评测结果（如不同LLM在MMLU基准上的得分）时，使用`<table>`配合`<thead>`和`<tbody>`分隔表头与数据行，`<th scope="col">`的`scope`属性帮助屏幕阅读器理解列标题归属，这是从HTML结构层面就保证数据可访问性的做法。

**表单与API交互**：用户向AI服务提交提示词（prompt）时，`<form>`的`action`属性指定后端接口地址，`method`属性选择`GET`或`POST`（长文本必须用POST），`<textarea name="prompt" maxlength="4096">`限制输入长度以匹配模型上下文窗口限制。`<label for="prompt">`通过`for`属性与`<textarea>`的`id`属性关联，点击标签可聚焦到输入框，提升可用性。

## 常见误区

**误区一：认为`<br>`是段落分隔的正确用法**。很多初学者用连续的`<br><br>`来制造段落间距，实际上`<br>`仅表示同一段落内的换行（如诗歌、地址），两个独立段落应各自使用`<p>`标签包裹，再通过CSS的`margin`属性控制间距。混用`<br>`会破坏文档的语义结构，导致屏幕阅读器无法正确识别段落边界。

**误区二：把`<div>`当万能容器滥用，忽略语义标签**。"div soup"（div汤）是前端反模式的专有叫法，指页面结构全由嵌套`<div>`堆砌，没有任何语义信息。这种结构在SEO（搜索引擎优化）中处于劣势——Google的页面爬虫对`<article>`、`<section>`、`<nav>`赋予更高权重——同时也让CSS选择器和JavaScript DOM查询变得复杂脆弱。

**误区三：认为HTML只要在浏览器中显示正确就是合法文档**。浏览器的容错机制极强，会自动修复未闭合标签、错误嵌套（如`<p>`内嵌套`<div>`）等问题，但不同浏览器的修复策略不同，会导致跨浏览器显示差异。可以使用W3C官方的Markup Validation Service（validator.w3.org）检验HTML文档是否符合规范，尤其在需要确保`<canvas>`等HTML5特性正确工作时，文档结构合法性至关重要。

## 知识关联

HTML定义了页面的结构和内容，但不控制视觉样式（颜色、字体、布局）——这是CSS基础的职责范围。学习CSS时，需要先理解HTML的元素嵌套关系（父子、兄弟），因为CSS的选择器语法（如后代选择器`div p`、子选择器`div > p`）直接依赖HTML文档树的层级结构。

JavaScript基础的学习中，DOM操作（如`document.getElementById()`、`element.innerHTML`、`element.addEventListener()`）本质上是对HTML元素的读取和修改，理解`<input>`的`type`属性差异（`text`、`checkbox`、`radio`、`file`）和`<form>`的提交事件，是JavaScript表单处理的前提。

HTML5的`<canvas>`标签是Canvas与WebGL技术的入口点——`<canvas id="myCanvas" width="800" height="600">`创建一个800×600像素的画布，WebGL通过`canvas.getContext('webgl')`获取渲染上下文，整个GPU加速渲染管线都从这个HTML标签开始。Web无障碍（a11y）规范WCAG 2.1的大量技术要求（如为`<img>`提供`alt`文本、使用`<label>`关联表单控件、ARIA属性的正确使用）都需要在HTML层面落实，语义化HTML是无障碍实践的基础工作。