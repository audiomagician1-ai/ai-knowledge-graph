---
id: "component-lifecycle"
concept: "组件生命周期"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 4
is_milestone: false
tags: ["React"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 组件生命周期

## 概述

组件生命周期（Component Lifecycle）是指一个 React 组件从被创建、插入 DOM、更新状态或属性，到最终被销毁移出 DOM 的完整过程。每个阶段都有对应的钩子函数（Hook），允许开发者在特定时机执行副作用、初始化数据或清理资源。

React 16.3 版本是组件生命周期的重大分水岭。该版本将 `componentWillMount`、`componentWillReceiveProps`、`componentWillUpdate` 三个方法标记为 **unsafe**（不安全），原因是它们与 React 引入的 Fiber 并发渲染架构不兼容——在 Concurrent Mode 下，这三个方法可能被调用多次，导致副作用重复执行。React 17 保留了它们但加上了 `UNSAFE_` 前缀，提醒开发者迁移。

理解生命周期的意义在于：它决定了在什么阶段可以安全地访问 DOM、发起网络请求、设置定时器，以及在什么阶段必须清理这些资源以防内存泄漏。错误地在 `render` 阶段执行带副作用的操作是 React 应用中最常见的 Bug 来源之一。

---

## 核心原理

### 三大阶段划分

React 类组件的生命周期分为三个主要阶段：**挂载（Mounting）**、**更新（Updating）**、**卸载（Unmounting）**。

- **挂载阶段**：执行顺序为 `constructor` → `static getDerivedStateFromProps` → `render` → `componentDidMount`。其中 `render` 是纯函数阶段，不能有副作用；`componentDidMount` 是第一个可以安全操作 DOM 和发起 `fetch` 请求的位置。
- **更新阶段**：当 `props` 或 `state` 变化时触发，顺序为 `getDerivedStateFromProps` → `shouldComponentUpdate` → `render` → `getSnapshotBeforeUpdate` → `componentDidUpdate`。其中 `shouldComponentUpdate` 返回 `false` 可阻止后续渲染，是性能优化的关键切入点。
- **卸载阶段**：只有一个方法 `componentWillUnmount`，用于清理定时器 `clearInterval`、取消订阅、中止 `fetch` 请求（通过 `AbortController`）等。

### 函数组件的 useEffect 对应关系

React Hooks（16.8 引入）用 `useEffect` 统一替代了类组件的多个生命周期方法，映射关系如下：

- `useEffect(() => { /* 副作用 */ }, [])` → 等价于 `componentDidMount`，空依赖数组使其只在挂载后执行一次。
- `useEffect(() => { /* 副作用 */ }, [dep])` → 等价于 `componentDidUpdate` 中检测 `dep` 变化的逻辑。
- `useEffect` 返回的清理函数 → 等价于 `componentWillUnmount`，在组件卸载前执行。

需要注意：`useEffect` 的执行时机是**浏览器绘制之后**（异步），而 `useLayoutEffect` 的执行时机是 DOM 变更之后、浏览器绘制之前（同步），直接对应类组件的 `componentDidMount` 和 `componentDidUpdate` 的同步行为。

### getDerivedStateFromProps 的特殊性

`static getDerivedStateFromProps(props, state)` 是一个**静态方法**，意味着它内部无法访问 `this`，必须返回一个对象来更新 state，或者返回 `null` 表示不更新。这个设计是刻意的：静态方法强制开发者将 props 到 state 的派生逻辑写成纯函数，防止在此阶段触发副作用。它在每次渲染前都会被调用，包括挂载和更新两个阶段。

---

## 实际应用

### 网络请求的正确时机

在 `componentDidMount` 或 `useEffect(..., [])` 中发起数据请求是标准做法。以下是使用 `useEffect` 防止内存泄漏的完整模式：

```javascript
useEffect(() => {
  const controller = new AbortController();
  fetch('/api/data', { signal: controller.signal })
    .then(res => res.json())
    .then(data => setData(data))
    .catch(err => {
      if (err.name !== 'AbortError') setError(err);
    });
  return () => controller.abort(); // 卸载时取消请求
}, []);
```

这里的清理函数通过 `AbortController` 在组件卸载时终止正在进行的请求，避免在已卸载组件上调用 `setState` 导致 React 报错。

### shouldComponentUpdate 与 React.memo 的性能优化

在列表渲染场景中，若父组件频繁更新，子组件不必要的重渲染会严重影响性能。类组件可通过 `shouldComponentUpdate` 返回 `false` 跳过渲染；函数组件使用 `React.memo` 包裹，配合 `useCallback` 稳定函数引用，可将不必要的渲染次数降低 80% 以上（在大型列表场景中效果尤为显著）。

---

## 常见误区

### 误区一：在 render 方法中执行 setState

`render` 阶段是 React 的纯计算阶段，在此阶段调用 `setState` 会触发无限循环渲染（render → setState → render…），导致应用崩溃并抛出 "Maximum update depth exceeded" 错误。`setState` 只能在生命周期的**提交阶段**（如 `componentDidMount`、`componentDidUpdate`）或事件处理函数中调用。

### 误区二：混淆 useEffect 与 useLayoutEffect 的使用场景

许多开发者将所有 DOM 操作都放在 `useEffect` 中，导致页面出现短暂的视觉闪烁（flash of incorrect content）。原因在于 `useEffect` 在浏览器绘制**之后**执行，用户会先看到初始 DOM，再看到修改后的结果。需要同步测量 DOM 尺寸（如实现 tooltip 定位）或同步修改 DOM 样式时，必须使用 `useLayoutEffect`。

### 误区三：误解 componentWillUnmount 的清理职责

部分开发者认为只需要清理"明显的"资源（如 `setInterval`），而忽略了 WebSocket 连接、自定义事件监听器（`window.addEventListener`）、以及第三方库（如 D3、ECharts）的实例销毁。这些遗漏在单页应用（SPA）中会导致内存随页面切换持续增长，最终引发性能下降。

---

## 知识关联

**前置概念：React 基础**  
理解生命周期需要先掌握 React 的 `props`/`state` 区别、JSX 渲染机制以及虚拟 DOM 的 reconciliation（协调）过程——因为生命周期钩子本质上是 reconciliation 算法在特定 Fiber 节点处理完成时触发的回调。

**后续概念：前端状态机**  
组件生命周期可以被建模为一个有限状态机：组件在 `unmounted`、`mounting`、`mounted`、`updating`、`unmounting` 这五个状态之间转换，每个状态转换都对应特定的生命周期方法。学习 XState 等前端状态机库时，你会发现它的 `entry`/`exit` 动作与 `componentDidMount`/`componentWillUnmount` 在语义上完全对应，掌握生命周期的状态转换视角可以自然地过渡到用显式状态机管理复杂异步流程。