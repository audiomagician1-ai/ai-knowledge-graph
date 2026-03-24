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
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 微前端架构

## 概述

微前端（Micro-Frontends）是一种将单体前端应用拆分为多个独立部署、独立开发的子应用的架构模式，由ThoughtWorks于2016年在技术雷达中首次提出。每个子应用可以由不同团队使用不同技术栈（React、Vue、Angular等）独立开发，最终通过一个容器应用（Shell App）组合呈现给用户。

这种架构的核心诉求来自大型前端项目的治理困境：当一个SPA代码库膨胀到数十万行时，构建时间可能超过10分钟，任何微小改动都需要全量重新部署。微前端通过按业务域拆分，使每个子应用的构建时间降低到1-2分钟，并支持独立版本发布。

微前端不等于简单的iframe嵌套。现代微前端框架（如qiankun、single-spa、Module Federation）在保证技术栈隔离的同时，提供共享路由、状态通信、样式隔离等机制，使多个子应用在同一页面内无缝协作，用户体验与SPA一致。

## 核心原理

### 拆分策略

微前端的拆分粒度直接决定架构的维护成本。常见策略有三种：

**按业务域垂直拆分**是最推荐的方式，例如将电商平台拆分为"商品子应用"、"订单子应用"、"用户中心子应用"，每个子应用对应一组相关路由（如 `/products/**`、`/orders/**`）。这种拆分边界清晰，团队职责明确。

**按页面拆分**适合迁移旧系统，将每个旧页面包装成独立子应用，逐步替换而不影响其他页面。

**按功能组件拆分**（Widget模式）将页面内的独立模块（如推荐组件、广告位）做成子应用，但这种方式通信复杂度高，仅在组件需要独立技术栈时使用。

拆分时需遵循**单一职责原则**：一个子应用不应依赖另一个子应用的内部模块，所有跨应用依赖必须通过公开接口进行。

### 集成方式

微前端有三种主要集成时机：

**构建时集成**：各子应用发布npm包，主应用统一安装依赖后构建。优点是最终产物优化充分，缺点是失去了独立部署能力——任何子应用更新都需要重新构建主应用，违背微前端的核心价值。

**运行时集成（JS Entry）**：主应用在浏览器端动态加载子应用的JS bundle。以qiankun为例，注册子应用时指定 `entry: 'https://sub-app.example.com'`，主应用在路由匹配时通过 `fetch` 获取子应用的HTML entry，解析其中的JS/CSS资源并动态插入DOM。

**Module Federation（模块联邦）**：Webpack 5引入的原生能力，通过在 `webpack.config.js` 中配置 `ModuleFederationPlugin`，子应用声明 `exposes` 导出模块，主应用声明 `remotes` 消费远程模块。与JS Entry不同，Module Federation支持共享依赖（`shared: ['react', 'react-dom']`），避免React等大型库被多次加载，是目前最接近原生语言链接机制的前端集成方案。

### 通信机制

子应用间通信需要严格约束，避免强耦合。主要有四种方式：

**CustomEvent（浏览器原生事件）**：通过 `window.dispatchEvent(new CustomEvent('orderCreated', { detail: { orderId: 123 } }))` 发布事件，其他子应用监听。优点是零依赖，缺点是无法追踪事件来源，调试困难。

**全局状态管理**：在Shell App中初始化一个共享store（如Redux store实例），通过 `props` 传递给子应用，子应用通过该实例读写状态。qiankun框架的 `initGlobalState` API实现了这一模式，提供 `setGlobalState` 和 `onGlobalStateChange` 两个方法。

**URL参数**：对于导航类通信（如子应用A跳转并携带参数给子应用B），直接使用URL查询参数是最可靠的方式，天然支持浏览器刷新后状态恢复。

**Props传递**：Shell App在激活子应用时注入props，适合传递用户信息、权限令牌等初始化数据，但只能单向传递。

### 样式与JS隔离

**样式隔离**：qiankun的 `strictStyleIsolation` 模式使用Shadow DOM将子应用渲染在独立的shadow root中，完全隔离CSS。但Shadow DOM会阻断部分第三方组件库（如Ant Design的Modal）的样式，因此更常用的是 `experimentalStyleIsolation` 模式——qiankun通过解析子应用CSS，给每条规则添加 `[data-qiankun="sub-app-name"]` 前缀选择器来限定作用域。

**JS隔离**：qiankun使用Proxy沙箱，为每个子应用创建一个代理对象替代 `window`，子应用对 `window.foo = 'bar'` 的写操作只作用于该代理对象，子应用卸载时代理销毁，不污染全局环境。Webpack的 `output.library` 配置决定子应用以何种格式导出生命周期钩子（`bootstrap`、`mount`、`unmount`），这三个钩子是single-spa规范的核心约定。

## 实际应用

**AI平台控制台**是微前端的典型场景：模型训练模块使用Vue 3开发，数据标注模块使用React开发，实验管理模块可能是收购公司的旧Angular代码。微前端架构允许三个团队各自维护技术栈，通过统一的Shell App将三个模块整合为一个控制台，用户无感知技术栈切换。

**渐进式迁移遗留系统**：将一个jQuery单体应用迁移至React时，可先用微前端框架将旧应用整体作为一个子应用，新功能模块逐步以React子应用形式上线，新旧模块共存运行，避免大爆炸式重写的风险。

**独立部署降低发布风险**：订单系统的bug修复只需重新部署订单子应用，其他子应用不受影响。结合灰度发布，可以让5%用户访问新版子应用，通过监控确认稳定后再全量切换。

## 常见误区

**误区一：把微前端当银弹，在小型项目中使用。** 微前端引入了子应用注册、沙箱隔离、跨应用通信等额外复杂度，并且多个子应用各自打包会导致bundle体积增大（即使Module Federation共享依赖，也有额外的运行时开销约25KB）。团队人数少于5人、代码库少于5万行的项目几乎没有使用微前端的收益，标准SPA加上良好的模块划分即可。

**误区二：认为子应用间可以随意共享组件。** 直接import另一个子应用的组件会在构建时形成强耦合，破坏独立部署能力。正确做法是将共享UI组件提取为独立npm包（Design System），所有子应用安装相同版本；或通过Module Federation的 `exposes` 机制在运行时共享，但需要明确版本兼容策略。

**误区三：混淆微前端与SPA子路由。** SPA子路由（如React Router的嵌套路由）是在同一个代码库、同一个构建产物内切换视图，所有代码在首次加载时全部下载。微前端的子应用在路由激活前完全不加载，资源完全独立，这是两者本质区别。单纯想要懒加载的场景应使用Webpack的动态 `import()` 而非微前端。

## 知识关联

**SPA路由**是微前端的前置基础：Shell App依赖客户端路由（History API）拦截URL变化，根据路由规则决定激活哪个子应用。理解 `popstate` 事件和 `pushState` API的工作原理，才能理解微前端框架如何劫持路由以管理子应用生命周期。

**Webpack/Vite打包工具**决定子应用以何种格式输出：子应用必须将 `output.libraryTarget` 设为 `umd`（Webpack）或等效格式，才能被主应用动态加载并调用 `bootstrap/mount/unmount` 生命周期。Module Federation更是直接内嵌于Webpack 5，理解 `entry`、`chunks`、`externals` 等打包概念是配置Module Federation的前提。理解这两个工具的输出格式与模块系统，是排查微前端加载失败问题的关键能力。
