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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# React基础

## 概述

React是由Facebook（现Meta）工程师Jordan Walke于2013年5月在JSConf US上首次开源发布的JavaScript UI库。它的核心设计理念是**声明式渲染**——开发者描述"界面应该长什么样"，而非命令式地告诉浏览器"如何一步步修改DOM"。这一思路与jQuery时代的直接DOM操作截然不同。

React引入了**组件化（Component-based）**架构，将界面拆分为可复用的独立单元。每个组件管理自己的状态（state）和属性（props），组件树的数据单向流动（从父到子），避免了双向数据绑定导致的调试困难。截至2024年，React在npm的周下载量超过2000万次，是AI工程前端集成（如AI聊天界面、实时数据看板）的主流选择。

React之所以在AI工程前端中广泛应用，原因在于它的组件模型非常适合构建动态更新的界面——例如流式输出（streaming）的AI对话框需要频繁局部更新，React的虚拟DOM差量对比机制能高效处理这类场景，而无需手动操作DOM节点。

---

## 核心原理

### JSX语法

JSX是React特有的语法扩展，允许在JavaScript中直接书写类HTML标记。它**并非HTML**，而是`React.createElement()`函数的语法糖。例如：

```jsx
const element = <h1 className="title">Hello, AI</h1>;
// 等价于：
const element = React.createElement('h1', { className: 'title' }, 'Hello, AI');
```

注意两个关键差异：HTML中用`class`，JSX中必须用`className`；HTML中用`for`，JSX中用`htmlFor`。JSX表达式必须有**唯一根元素**，或使用`<React.Fragment>`（简写`<>`）包裹多个子元素，避免多余的DOM节点。

### 组件与Props

React组件分为**函数组件**和类组件两种形式，现代React（16.8版本之后）推荐全面使用函数组件。一个最简单的函数组件如下：

```jsx
function ModelCard({ modelName, accuracy }) {
  return (
    <div>
      <h2>{modelName}</h2>
      <span>准确率：{accuracy}%</span>
    </div>
  );
}
```

Props（属性）是从父组件向子组件传递数据的唯一方式，**Props是只读的**——子组件不能修改接收到的props。这一约束保证了数据流的可预测性。Props可以传递任意JavaScript值，包括字符串、数字、数组、对象，乃至函数（回调）和其他组件。

### State与useState

State是组件内部管理的可变数据。在函数组件中，通过`useState` Hook声明状态：

```jsx
const [count, setCount] = useState(0);
```

`useState`返回一个数组：当前状态值和更新函数。**调用`setCount`不会直接修改`count`变量**，而是触发组件重新渲染，React在下一次渲染时提供新的状态值。State更新是**异步批量处理**的——在React 18中，所有事件处理器内的多次`setState`调用会被自动合并（Automatic Batching），减少不必要的渲染次数。

### 事件处理与条件渲染

React事件使用驼峰命名（`onClick`而非`onclick`），传入函数引用而非字符串。条件渲染常用三种模式：

```jsx
// 1. 三元运算符
{isLoading ? <Spinner /> : <Result data={data} />}

// 2. 逻辑与短路
{error && <ErrorMessage text={error} />}

// 3. 提前返回
if (!data) return null;
```

在AI工程场景中，"正在请求模型API"与"已收到响应"两种状态的切换渲染极为常见，这三种模式是处理此类UI状态的标准手段。

---

## 实际应用

**AI对话界面的消息列表渲染**是React基础的典型应用场景。消息数组存储在父组件的state中，每条消息作为独立的`<MessageBubble>`组件渲染：

```jsx
{messages.map((msg) => (
  <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
))}
```

`key`属性是React列表渲染的必填项，必须使用稳定且唯一的标识符（如消息ID），**不能使用数组下标作为key**，否则在列表增删时会导致组件状态错位。

**实时数据看板**中，模型推理延迟、Token吞吐量等指标需要定期更新。通过`useState`存储指标数据，配合`useEffect`（React Hooks阶段深入介绍）定时轮询API，组件会在数据变化时自动重新渲染对应的图表子组件，而不影响页面其他部分。

---

## 常见误区

**误区1：直接修改state对象**

```jsx
// 错误
state.messages.push(newMessage);
setState(state);

// 正确
setState(prev => [...prev, newMessage]);
```

React通过`Object.is`比较前后两次state引用是否相同来决定是否重渲染。直接修改原对象后传入，引用未变，React认为状态没有改变，界面不会更新。这是初学者最高频的错误之一。

**误区2：认为JSX中可以使用任意JavaScript语句**

JSX的花括号`{}`只能包含**表达式**（有返回值），不能直接写`if`语句、`for`循环或`let`声明。`if-else`必须改写为三元运算符，循环必须使用`.map()`等返回数组的数组方法。

**误区3：混淆Props与State的使用场景**

并非所有数据都需要放入state。如果数据来自父组件且不在本组件内部改变，应使用props；如果数据随用户交互或异步请求改变，且变化需要触发重新渲染，才使用state。将所有数据都放入state会导致不必要的渲染和组件间同步困难。

---

## 知识关联

学习React基础需要扎实的**JavaScript基础**，特别是ES6+特性：箭头函数（函数组件的简洁写法）、解构赋值（props解构和useState返回值解构）、展开运算符（不可变state更新）以及数组方法（`.map()`、`.filter()`用于列表渲染）。**DOM操作**的前置知识帮助理解React为何要引入虚拟DOM层——直接操作真实DOM代价高昂，React通过在内存中维护虚拟DOM树并进行差量比对（Diffing）来最小化实际DOM操作次数，这一机制在**虚拟DOM原理**章节中将详细展开。

掌握组件、props、state和JSX之后，下一步是学习**React Hooks**——`useEffect`处理副作用（API调用、订阅）、`useContext`跨层传递数据、`useCallback`与`useMemo`进行性能优化。**组件生命周期**概念解释了组件从挂载、更新到卸载各阶段的行为，是理解Hooks执行时机的关键。**SPA路由**（如React Router v6）在此基础上实现无刷新页面导航，而**设计系统**则将组件化思想推进到企业级UI规范层面。