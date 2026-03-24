---
id: "react-basics"
concept: "React基础"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 4
is_milestone: false
tags: ["React"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.412
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# React基础

## 概述

React 是由 Facebook（现 Meta）工程师 Jordan Walke 于 2011 年内部开发、2013 年 5 月在 JSConf US 上正式开源的 JavaScript UI 库。它的核心设计思想是**单向数据流**和**组件化**：将页面拆分为独立、可复用的组件，每个组件管理自身状态，通过 props 向下传递数据，而非直接操作 DOM。这一设计解决了当时主流 MVC 框架中双向绑定难以追踪数据变化来源的问题。

React 的版本演进对学习路径有直接影响：2016 年发布的 React 15 确立了类组件模式，2019 年 React 16.8 正式引入 Hooks，使函数组件具备了完整的状态管理能力，这是目前工业界的主流写法。2022 年的 React 18 引入了并发渲染（Concurrent Rendering），但这些高级特性建立在对基础概念的扎实理解之上。

React 在 AI 工程的 Web 前端场景中尤为重要：大量 AI 产品界面（如 ChatGPT、Vercel AI 工具链）均以 React 为基础构建，且 AI 生成的流式文本输出、动态图表渲染等场景恰好需要 React 的高效局部更新机制。

---

## 核心原理

### JSX：JavaScript 的 XML 扩展语法

JSX 并非独立语言，而是 Babel 会将其编译为 `React.createElement()` 调用。例如：

```jsx
const element = <h1 className="title">Hello</h1>;
// 等价于：
const element = React.createElement('h1', { className: 'title' }, 'Hello');
```

JSX 中使用 `className` 而非 `class`，因为 `class` 是 JavaScript 保留字。所有标签必须闭合（包括 `<img />` 等自闭合标签），否则 Babel 编译会报错。JSX 表达式须被单一根元素包裹，React 16 起可用 `<>...</>` 空标签（Fragment）避免额外 DOM 节点。

### 组件与 Props：构建 UI 的最小单元

React 组件本质上是一个接收 `props` 对象、返回 JSX 的纯函数（函数组件），或继承自 `React.Component` 的类（类组件）。**函数名必须首字母大写**，以区分原生 HTML 标签。

```jsx
// 函数组件示例
function UserCard({ name, score }) {
  return <div>{name} 的 AI 评分：{score}</div>;
}
```

Props 是**只读**的：子组件不能修改传入的 props。这一"单向数据流"规则使数据变化来源唯一可追溯。当需要在组件间共享状态时，应将 state 提升到最近的公共父组件（状态提升，Lifting State Up）。

### State：组件内部的可变数据

函数组件通过 `useState` Hook 管理本地状态。`useState` 返回一个二元数组：当前值和更新函数。

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0); // 初始值为 0
  return <button onClick={() => setCount(count + 1)}>点击次数：{count}</button>;
}
```

调用 `setCount` 会触发组件**重新渲染**（re-render）：React 对比前后两次渲染产生的虚拟 DOM 树差异，仅更新实际发生变化的 DOM 节点，这是 React 性能优化的基础机制。State 更新是**异步批处理**的——React 18 默认对所有事件中的多次 `setState` 进行批量合并，减少渲染次数。

### 条件渲染与列表渲染

React 没有内置的模板指令（如 Vue 的 `v-if`），条件渲染通过 JS 逻辑实现：

```jsx
// 三元表达式
{isLoading ? <Spinner /> : <DataTable data={rows} />}

// 短路运算符（仅在条件为真时渲染）
{error && <ErrorBanner message={error.message} />}
```

列表渲染使用 `.map()` 方法，每个列表项**必须提供唯一的 `key` prop**，React 用它在重新渲染时识别哪些元素发生了变化。使用数组下标作为 key 在列表项可能重排序时会导致 Bug，应优先使用数据的唯一 ID。

---

## 实际应用

**AI 对话界面的流式消息组件**是 React 基础概念的典型综合场景。一个消息列表组件将 `messages` 数组作为 state，每收到服务器推送的新词元（token）就调用 `setMessages` 更新最后一条消息的内容，React 的局部更新机制使页面只重绘新增文字所在的节点，而非整页刷新。

**数据大屏的图表切换**利用条件渲染根据用户选中的维度动态展示不同图表组件（如 `<BarChart />` 或 `<LineChart />`）。两个组件定义在同一位置时，切换会触发卸载与重新挂载；若需保留图表的过渡动画状态，需用条件隐藏（`style={{ display: 'none' }}`）而非条件渲染。

**表单受控组件**在 AI 工程中用于构建 Prompt 编辑器：将 `<textarea>` 的 `value` 绑定到 state，通过 `onChange` 事件实时更新，确保 React state 始终是界面的唯一数据来源（受控模式），便于在提交前对 Prompt 进行格式校验或字数统计。

---

## 常见误区

**误区一：直接修改 state 对象**

```jsx
// 错误：直接修改不会触发重新渲染
state.count = state.count + 1;

// 正确：使用 setState 传入新对象
setUser({ ...user, age: user.age + 1 });
```

React 通过对比前后 state 引用是否相同来判断是否需要重渲染。直接修改原对象不改变引用，React 检测不到变化，界面不会更新。

**误区二：混淆 props 与 state 的职责**

初学者常将所有数据都放入 state，包括可以从 props 或其他 state 推导出的数据（派生数据）。例如将 `fullName` 同时存为独立 state，并在 `firstName` 变化时手动同步——这导致数据不一致 Bug。正确做法是在 render 阶段直接计算：`const fullName = firstName + ' ' + lastName;`，不存入 state。

**误区三：忽视 key 的作用范围**

`key` 不仅用于列表，还可主动利用其"重置组件"的特性：向同一组件传入不同 `key` 会强制 React 销毁旧实例并创建新实例，这是切换不同用户 Profile 时重置所有内部 state 的最简洁方法，无需在 `useEffect` 中手动清空每个字段。

---

## 知识关联

**前置依赖**：JavaScript 的数组方法（`.map()`、`.filter()`）是理解列表渲染的直接基础；DOM 操作的知识帮助理解 React 为何要通过虚拟 DOM 抽象层来减少直接操作真实 DOM 的代价——这是 React 存在的原始动机。

**直接延伸**：本文介绍的 `useState` 是 React Hooks 体系的入门钩子，下一步学习 `useEffect`（副作用处理）、`useContext`（跨层传值）等 Hooks 时，组件与 state 的心智模型将被直接复用。组件生命周期的概念（挂载 → 更新 → 卸载）在函数组件中通过 `useEffect` 的不同写法来表达，理解本文的 re-render 触发机制是学习生命周期的前提。

**横向扩展**：虚拟 DOM 原理将揭示 React 协调算法（Reconciliation）如何利用 `key` 和组件类型进行 Diff 比较；SPA 路由（如 React Router v6）本质上是根据 URL state 进行条件渲染的高级封装；设计系统（如 shadcn/ui）则将组件化思想推向极致，建立在对 props 传递和组件组合模式的深刻理解之上。
