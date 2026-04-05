---
id: "micro-frontend"
concept: "微前端架构"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 5
is_milestone: false
tags: ["architecture", "module-federation", "isolation"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 微前端架构

## 概述

微前端（Micro Frontends）是将大型单体前端应用拆分为多个可独立开发、独立部署、独立运行的子应用的架构模式，最早由 ThoughtWorks 在 2016 年技术雷达报告中提出。其核心思想借鉴自后端微服务：将一个前端团队的单一代码仓库，拆分为多个团队可以分别负责的子系统，每个子应用可以选择不同的技术栈（如 React、Vue、Angular 混用）。

微前端架构的必要性体现在企业级应用的演进痛点上。当一个 SPA 项目积累了 200+ 个路由、50+ 名开发者共同提交代码时，每次发布都需要整体构建（构建时间可能超过 15 分钟）、任何一个模块的 bug 都会阻断全量发布。微前端通过将这些子模块变成独立可部署的单元，让电商系统的"商品详情"子团队能在不影响"购物车"团队的前提下独立上线。

## 核心原理

### 拆分策略

微前端的拆分维度通常有三种方式。**按路由拆分**是最常见的方式：容器应用（Shell App）根据 URL 前缀决定加载哪个子应用，例如 `/order/*` 加载订单子应用，`/product/*` 加载商品子应用。这种方式下子应用在运行时互不重叠。**按页面模块拆分**允许同一页面内同时渲染多个子应用，适用于 Dashboard 类页面，但需要严格管理 DOM 挂载点和 CSS 隔离。**按业务域垂直拆分**则将整个前端栈（含 BFF 层）按业务能力划分，每个团队端到端负责自己的业务切片。

### 集成方式

微前端集成有三个技术层面的实现路径：

**构建时集成**：通过 npm 包将子应用发布为组件库，在构建阶段被宿主应用引入。优点是类型安全、tree-shaking 有效；缺点是失去独立部署能力，实质上退化为 monorepo，违背微前端的核心价值。

**运行时集成（主流方案）**：包括 iframe 嵌入、JavaScript 动态加载、以及以 Single-SPA 和 qiankun 为代表的框架方案。qiankun 基于 Single-SPA 封装，通过 `import-html-entry` 解析子应用的 HTML 入口，动态注入 `<script>` 和 `<style>` 标签，子应用需暴露 `bootstrap`、`mount`、`unmount` 三个生命周期钩子函数。

**Module Federation（模块联邦）**：Webpack 5 在 2020 年引入的特性，允许一个构建产物在运行时从另一个独立部署的远程构建中加载模块。配置示例：`remotes: { orderApp: 'orderApp@https://cdn.example.com/remoteEntry.js' }`，宿主应用通过这个 `remoteEntry.js` 清单文件动态拉取子应用暴露的模块，实现真正的代码级别共享而非整包加载。

### 隔离机制

微前端最关键的技术挑战是**沙箱隔离**，包含两个层面：

**JS 沙箱**：防止子应用污染全局 `window` 对象。qiankun 提供两种沙箱模式：`LegacySandbox` 通过 Proxy 拦截对 `window` 的读写并记录变更，子应用卸载时恢复现场；`ShadowRealm` 模式（实验性）使用 ECMAScript 提案中的 `ShadowRealm` API 提供更彻底的隔离。

**CSS 隔离**：通过 `Shadow DOM` 或动态给子应用 CSS 添加属性选择器前缀（如 `[data-qiankun="order-app"] .container { ... }`）实现样式作用域。Shadow DOM 隔离彻底但会导致弹窗、全局 Toast 等组件无法穿透边界渲染。

### 通信机制

子应用间的通信有三种模式：**基于 URL 的通信**（query params 和 hash）适合轻量状态传递；**全局状态管理**使用宿主应用维护的共享 Store（qiankun 提供 `initGlobalState` API，返回 `onGlobalStateChange` 和 `setGlobalState` 方法）；**CustomEvent 自定义事件**通过 `window.dispatchEvent(new CustomEvent('userLogin', { detail: { userId: 123 } }))` 实现松耦合的发布-订阅通信，是技术栈异构场景下最通用的方案。

## 实际应用

**大型电商平台改造**：京东、阿里等平台将商品、交易、营销等子系统改造为微前端，每个子系统由独立团队用不同 React 版本维护，通过 qiankun 的路由分发实现统一入口。改造后各子系统的发布频率从每周 1 次提升到每天多次。

**AI 平台 Dashboard**：AI 工程平台通常包含模型训练监控、数据集管理、推理服务控制台等模块，各模块技术演进速度不同。使用 Module Federation 可以让推理服务控制台（需要 WebGL 图表库，包体积 2MB+）仅在用户导航到该模块时才触发加载，而非在主应用初始化时一次性打包。

**渐进式迁移遗留系统**：将 Angular.js 老应用的某一路由段注册为微前端子应用，同时新功能用 React 开发，两者并行运行在同一页面的不同 DOM 节点，实现按模块逐步替换而无需大爆炸式重写。

## 常见误区

**误区一：微前端等于 iframe**。iframe 确实提供了最强的隔离性，但它无法共享浏览器历史记录（导致前进/后退按钮行为异常）、无法共享 Cookie/LocalStorage 的同源策略、且子页面的弹窗会被 iframe 边框裁剪。微前端框架方案的核心价值恰恰是在保持一定隔离性的同时解决这些 iframe 的固有缺陷。

**误区二：子应用越多越好**。拆分粒度过细会导致共享依赖（如 React 18 运行时）在每个子应用中重复加载。若 10 个子应用各自打包 React（~130KB gzip），用户首屏需多下载 1.17MB。正确做法是通过 Module Federation 的 `shared` 配置声明共享单例：`shared: { react: { singleton: true, requiredVersion: '^18.0.0' } }`。

**误区三：微前端解决了代码耦合问题**。微前端是部署边界的隔离，如果子应用间通过全局状态频繁传递复杂对象、或者直接 import 彼此的内部模块，耦合依然存在。微前端的通信协议本身需要被纳入接口契约管理，否则一个子应用修改 `globalState` 的数据结构会级联破坏其他子应用。

## 知识关联

微前端架构建立在 **SPA 路由**机制之上：容器应用的路由监听（`history.pushState` 事件或 `hashchange` 事件）是触发子应用加载/卸载的驱动力，Single-SPA 的核心实现就是对这两种路由事件的劫持和重新分发。

对 **Webpack/Vite 打包工具**的理解直接决定微前端方案的选择：Module Federation 是纯 Webpack 5 特性，Vite 生态对应的方案是 `vite-plugin-federation`，但两者在处理 ESM/CJS 模块格式兼容性时存在差异。熟悉打包工具的 `externals` 配置、`output.library` 格式（`umd` vs `esm`）是正确配置子应用构建产物的前提——qiankun 要求子应用将 `output.library` 设为 `umd` 格式才能被宿主正确识别三个生命周期钩子。