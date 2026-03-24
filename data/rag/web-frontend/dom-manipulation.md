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
content_version: 3
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

DOM（Document Object Model，文档对象模型）是浏览器将HTML文档解析为可编程树形结构的标准接口，由W3C于1998年发布DOM Level 1规范正式确立。每个HTML标签、属性、文本内容都被映射为树中的一个节点（Node），整棵树的根节点是`document`对象，所有JavaScript对页面结构的读写操作都必须通过这棵树进行。

DOM操作的本质是用JavaScript代码在运行时动态读取或修改这棵节点树——包括新增节点、删除节点、修改节点内容与样式，以及查找特定节点。对于AI工程中的Web前端开发，DOM操作是将模型推理结果、实时数据流和用户交互反馈呈现到页面上的直接手段。例如，将大语言模型的流式输出逐字追加到某个`<div>`元素中，或根据推理状态切换加载动画的显示与隐藏，都依赖精准的DOM操作。

DOM规范在历史演进中经历了Level 1（1998）、Level 2（2000，引入事件模型和CSS样式接口）、Level 3（2004）直至现代Living Standard的持续更新。理解原生DOM操作不仅有助于在无框架环境中直接操控页面，也是理解React虚拟DOM差量更新机制的前提基础。

---

## 核心原理

### 节点树结构与节点类型

HTML文档被解析后形成一棵以`document`为根的节点树，每个节点具有`nodeType`属性标识其类型：元素节点（`nodeType === 1`）、文本节点（`nodeType === 3`）、注释节点（`nodeType === 8`）是最常见的三种。元素节点对应HTML标签，文本节点保存标签内的纯文本内容，二者在树中是父子关系。例如`<p>Hello</p>`在DOM树中包含两个节点：一个`<p>`元素节点，其子节点是值为`"Hello"`的文本节点，而非只有一个节点。

节点间的关系通过以下属性访问：
- `parentNode`：父节点
- `childNodes`：所有子节点的实时`NodeList`
- `firstChild` / `lastChild`：第一个/最后一个子节点
- `nextSibling` / `previousSibling`：相邻兄弟节点

注意`childNodes`返回的是**实时集合**（live collection），对DOM的修改会立即反映其中，这与`querySelectorAll`返回的**静态NodeList**行为截然不同，混淆两者是循环操作中常见的bug来源。

### 查询节点的方法

浏览器提供多种查询API，性能和使用场景各有差异：

| 方法 | 返回类型 | 实时性 |
|---|---|---|
| `getElementById('id')` | 单个元素或null | — |
| `getElementsByClassName('cls')` | 实时HTMLCollection | 实时 |
| `getElementsByTagName('div')` | 实时HTMLCollection | 实时 |
| `querySelector('css选择器')` | 单个元素或null | 静态 |
| `querySelectorAll('css选择器')` | 静态NodeList | 静态 |

`querySelector`和`querySelectorAll`接受完整CSS选择器字符串，例如`document.querySelectorAll('ul.result-list > li[data-score]')`，灵活性最高，是现代代码中最推荐的查询方式。`getElementById`在实现上通常使用哈希表查找，在大型文档中速度比CSS选择器查询更快。

### 创建、插入与删除节点

创建节点使用`document.createElement(tagName)`，创建文本节点使用`document.createTextNode(text)`，创建包含HTML字符串的片段则推荐使用`DocumentFragment`：

```javascript
const fragment = document.createDocumentFragment();
for (let i = 0; i < 1000; i++) {
  const li = document.createElement('li');
  li.textContent = `Item ${i}`;
  fragment.appendChild(li);
}
document.querySelector('ul').appendChild(fragment);
```

上述写法将1000次DOM插入合并为1次，因为`DocumentFragment`本身不在文档树中，批量操作后只触发一次重排（reflow）。若改为每次直接`appendChild`到`<ul>`，则触发1000次重排，在复杂页面中性能差距可达数十倍。

插入节点的现代API首选`element.append()`（支持多参数、支持字符串）和`element.prepend()`，而非旧式的`appendChild()`。删除节点使用`element.remove()`，或通过父节点调用`parentNode.removeChild(element)`（兼容IE的写法）。

### 修改内容与属性

修改节点内容有三个常用属性，其语义和安全风险不同：

- `textContent`：读写节点及所有后代的纯文本，**不解析HTML标签**，可防止XSS注入。
- `innerHTML`：读写节点的HTML字符串，**会解析并渲染标签**，直接赋值用户输入内容存在XSS风险。
- `innerText`：类似`textContent`但会触发重排以计算CSS可见性，性能较差。

修改元素属性使用`element.setAttribute('href', url)`，删除属性使用`element.removeAttribute('disabled')`。操作CSS类名推荐使用`element.classList` API：`classList.add('active')`、`classList.remove('hidden')`、`classList.toggle('expanded')`，比直接操作`className`字符串更安全且语义清晰。

---

## 实际应用

**流式输出文字渲染**：在AI聊天界面中，大语言模型通过Server-Sent Events返回分块文本时，前端需要不断将新内容追加到消息气泡元素中。正确做法是维护一个`<span>`元素引用，每收到新token就执行`span.textContent += newToken`，而非每次重建整个消息节点，以避免光标闪烁和不必要的重排。

**动态表格生成**：展示批量推理结果时，用`DocumentFragment`批量创建`<tr>`行并一次性插入`<tbody>`，比逐行`innerHTML +=`拼接快得多（后者每次赋值都销毁并重建整个子树）。

**加载状态切换**：推理请求发送时执行`loadingEl.classList.remove('hidden')`，收到响应后执行`loadingEl.classList.add('hidden')`，通过CSS控制显隐，比`display`属性直接赋值更利于过渡动画。

---

## 常见误区

**误区1：innerHTML赋值可以安全插入任意内容**
直接将用户输入或API返回的字符串通过`innerHTML`插入，会执行其中的`<script>`标签或`onerror`等事件属性，造成XSS攻击。应使用`textContent`插入纯文本，或使用`DOMPurify`库对HTML字符串消毒后再赋值给`innerHTML`。

**误区2：频繁操作DOM性能问题在于"操作次数"本身**
DOM操作慢的真正原因不是JavaScript访问DOM对象的开销，而是写操作触发浏览器的**重排（reflow）和重绘（repaint）**。读取布局属性（如`offsetHeight`）会强制浏览器刷新待处理的样式计算。在循环中交替读写布局属性（读→写→读→写）会导致"布局抖动"（layout thrashing），应将所有读操作集中在写操作之前执行。

**误区3：`NodeList`和`HTMLCollection`都会实时更新**
`getElementsByClassName`和`getElementsByTagName`返回实时HTMLCollection，在遍历时删除其中的元素会跳过节点；而`querySelectorAll`返回的静态NodeList则不受后续DOM变化影响，在遍历+删除的场景中更安全可预测。

---

## 知识关联

DOM操作依赖对JavaScript基础的掌握，尤其是对象引用、循环遍历和回调函数的理解——因为节点查询结果是对象引用，对其修改直接作用于页面，而非副本。

DOM操作是**事件处理**的前提：事件监听通过`element.addEventListener('click', handler)`绑定到特定DOM节点，事件冒泡和捕获机制都在节点树上传播，不了解树形结构就无法理解事件委托模式。

学习**React基础**后会发现，React的虚拟DOM（Virtual DOM）是对原生DOM操作的抽象优化——React在内存中维护虚拟节点树，通过diff算法计算最小变更集，最终批量调用原生DOM API应用更新，其优化思路与`DocumentFragment`批量插入的原理一脉相承。

**浏览器渲染原理**进一步解释了为何DOM写操作代价高昂：每次修改DOM可能触发渲染流水线中的样式计算、布局（reflow）、分层合成等步骤，理解这条流水线才能从根本上写出高性能的DOM操作代码。**浏览器存储机制**（如`localStorage`、IndexedDB）则是在DOM之外持久化数据的配套手段，与DOM操作共同构成完整的前端数据流转链路。
