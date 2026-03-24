---
id: "dom-manipulation"
concept: "DOM操作"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 3
is_milestone: false
tags: ["JS", "浏览器"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# DOM操作

## 概述

DOM（Document Object Model，文档对象模型）是浏览器将HTML文档解析后生成的树形数据结构，每个HTML标签、属性和文本内容都对应树中的一个节点（Node）。JavaScript通过`document`全局对象作为入口访问并操控这棵树，实现页面内容的动态增删改查。DOM规范由W3C于1998年首次发布（DOM Level 1），目前主流浏览器支持的是DOM Level 3及Living Standard版本。

DOM的意义在于它将静态HTML文档转化为可编程对象。在DOM出现之前，网页内容一旦渲染完毕便无法通过脚本修改；有了DOM，JavaScript才能在不刷新页面的情况下更新用户界面，这是所有现代Web应用——包括React、Vue等框架——的底层运行基础。理解原生DOM操作，是理解框架"帮你做了什么"的前提。

## 核心原理

### DOM树的节点类型

DOM树包含12种节点类型（`nodeType`属性用整数标识），其中最常用的三种是：元素节点（`nodeType === 1`，对应HTML标签）、文本节点（`nodeType === 3`，对应标签中的文字）、注释节点（`nodeType === 8`）。正因为文本节点独立存在，`<p>Hello</p>`中实际有两个节点：`<p>`元素节点和`"Hello"`文本节点。忽略这一点经常导致遍历子节点时出现空白文本节点的意外。

### 查询节点

现代DOM提供多种查询API，性能和用途各异：

- `document.getElementById('id')`：按ID精确查找，返回单个元素，是最快的查询方式。
- `document.querySelector('.btn')`：接受CSS选择器字符串，返回第一个匹配元素。
- `document.querySelectorAll('li.active')`：返回静态`NodeList`，不随DOM变更自动更新。
- `document.getElementsByClassName('item')`：返回**动态**`HTMLCollection`，DOM变更后集合自动刷新——在循环中删除元素时若不注意这一点，会导致无限循环或跳项。

### 增删改节点

**创建**：`document.createElement('div')` 创建元素节点，`document.createTextNode('text')` 创建文本节点，两者尚未被插入文档，存在于内存中。

**插入**：`parent.appendChild(child)` 追加到末尾；`parent.insertBefore(newNode, referenceNode)` 插入到指定节点之前；更现代的`element.insertAdjacentHTML('beforeend', htmlString)` 允许直接插入HTML字符串，比连续调用`createElement`效率更高。

**删除**：`parent.removeChild(child)` 是传统方式；ES2020后推荐`element.remove()`，无需持有父节点引用。

**修改属性与内容**：`element.setAttribute('class', 'active')` 设置属性；`element.textContent` 修改纯文本内容（自动转义HTML特殊字符）；`element.innerHTML` 解析并插入HTML字符串，但直接赋入用户输入的字符串会引发XSS注入攻击。

### 批量操作与性能

每次直接修改DOM都会触发浏览器重新计算样式（Recalculate Style）或重排（Reflow），代价较高。常见优化手段是使用`DocumentFragment`：先将多个节点附加到`DocumentFragment`上，再一次性将其插入真实DOM，整个过程只触发一次重排。例如渲染100条列表项时，使用`DocumentFragment`的耗时通常比逐条`appendChild`减少60%以上。此外，批量修改样式时应操作`element.className`或`element.classList`，而非逐属性修改`element.style`。

## 实际应用

**动态表单验证**：在用户失焦（`blur`事件）时，用`querySelector`获取输入框，检查其`value`属性，然后用`insertAdjacentHTML`在输入框后插入错误提示`<span>`，或用`element.classList.add('error')`切换样式类，无需刷新页面即可给予反馈。

**无限滚动列表**：结合`IntersectionObserver` API监听列表末尾的哨兵元素，当其进入视口时，用`DocumentFragment`批量创建新列表项并`appendChild`到容器，实现数据懒加载与DOM节点的按需创建。

**富文本编辑器的光标操作**：contenteditable元素依赖DOM的`Range`和`Selection`对象定位光标，`document.createRange()`和`window.getSelection()`是这类场景的核心API，编辑器框架如Quill、Slate底层均依赖这套机制。

## 常见误区

**误区一：innerHTML与textContent混用导致安全漏洞**
将用户提交的内容通过`element.innerHTML = userInput`写入DOM，会执行其中的`<script>`标签或`onerror`事件处理器，构成XSS漏洞。正确做法是当内容为纯文本时始终使用`textContent`，或在插入前通过`DOMPurify`等库做白名单清洗。

**误区二：混淆静态NodeList与动态HTMLCollection**
`querySelectorAll`返回的`NodeList`是查询时的快照，不随后续DOM变更更新；而`getElementsByClassName`返回的`HTMLCollection`是动态的。若在`for`循环中用`HTMLCollection`的`length`作为终止条件，同时在循环体内删除元素，由于集合实时缩短，将导致部分元素被跳过，应先将其转换为数组（`Array.from(collection)`）再遍历。

**误区三：以为DOM操作是同步完成的**
调用`appendChild`后，节点确实同步加入DOM树，但浏览器的实际绘制（Paint）是异步批处理的。因此在`appendChild`之后立即读取元素的`offsetHeight`，虽然能得到正确值（因为读操作会强制同步布局），但这种"强制同步布局"（Forced Synchronous Layout）恰恰是性能瓶颈的来源，应尽量将读操作集中在写操作之前完成。

## 知识关联

DOM操作依赖JavaScript基础中的对象模型和原型链知识，`HTMLElement`继承自`Element`继承自`Node`这条原型链决定了哪些方法在哪类节点上可用。

掌握DOM操作后，学习**事件处理**时会直接用到`addEventListener`绑定到特定DOM节点，以及事件冒泡与委托的原理——委托模式本质上是对DOM树父子关系的利用。学习**React基础**时，你会发现React的虚拟DOM（Virtual DOM）正是为了减少真实DOM操作次数而设计的抽象层，理解真实DOM的代价才能理解虚拟DOM的价值。**浏览器渲染原理**则进一步解释了为何频繁的DOM写操作会触发重排（Reflow）和重绘（Repaint），以及如何通过CSS合成层（Compositor Layer）将动画代价降至最低。而**浏览器存储机制**（如`localStorage`）的数据常被读出后渲染到DOM节点，两者在实际应用中紧密协作。
