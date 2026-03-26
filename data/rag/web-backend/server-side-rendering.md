---
id: "server-side-rendering"
concept: "服务端渲染(SSR)"
domain: "ai-engineering"
subdomain: "web-backend"
subdomain_name: "Web后端"
difficulty: 6
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 服务端渲染（SSR）

## 概述

服务端渲染（Server-Side Rendering，SSR）是指在用户请求到达时，由服务器动态执行 JavaScript 框架代码，将组件树渲染为完整的 HTML 字符串，随后将该 HTML 连同数据一起发送给浏览器的技术方案。与客户端渲染（CSR）不同，SSR 返回的 HTML 页面在浏览器解析时已包含完整内容节点，无需等待 JS 包下载和执行。

SSR 的概念并不新鲜，早期 PHP、ASP、JSP 等服务端模板引擎本质上就是服务端渲染。现代意义上的 SSR 特指将 React、Vue、Svelte 等前端框架在 Node.js 服务端执行的同构渲染模式，由 Next.js（2016年首发）和 Nuxt.js（2016年同期）将其推向主流。这类框架实现了"同构代码"——同一套组件代码既能在 Node.js 中渲染为 HTML，也能在浏览器端进行 Hydration（注水）激活。

SSR 对 AI 工程中的 Web 后端尤为关键：AI 应用往往需要在服务器端调用大模型 API 获取数据，再将结果嵌入页面返回，同时要求搜索引擎能抓取动态内容。SSR 恰好将数据获取、权限校验、内容生成全部集中在可信服务端完成，避免将 API 密钥暴露在浏览器端。

---

## 核心原理

### 请求-渲染-响应流程

当浏览器发出 GET 请求后，Node.js 服务器触发对应路由的数据预取函数（在 Next.js 中称为 `getServerSideProps`，在 Nuxt 3 中为 `useFetch` 的服务端执行路径）。数据就绪后，框架调用 `renderToString()`（React）或 `renderToNodeStream()`（流式版本）将虚拟 DOM 树序列化为 HTML 字符串。服务器在响应头中设置 `Content-Type: text/html`，将完整 HTML 返回。浏览器收到后立即可以渲染出有内容的页面，此时的关键指标 **FCP（First Contentful Paint）** 相比 CSR 通常可缩短 1–3 秒。

### Hydration（注水）机制

SSR 页面返回后并不具备交互能力，浏览器还需下载客户端 JS bundle 并执行 Hydration 过程。Hydration 的核心是 React 调用 `hydrateRoot()` 替代 `createRoot()`，它不会重新创建 DOM 节点，而是"认领"服务端已生成的 DOM，为其绑定事件监听器并恢复组件状态。如果客户端渲染结果与服务端 HTML 不匹配（例如使用了 `Math.random()` 或 `Date.now()`），React 会抛出 **Hydration Mismatch 错误**并强制重新渲染，这是 SSR 调试中最常见的问题之一。

### 数据序列化与脱水（Dehydration）

为避免浏览器端重复请求已在服务端获取的数据，SSR 框架会将服务端数据"脱水"后嵌入 HTML。具体做法是将数据对象通过 `JSON.stringify` 序列化，注入到 `<script>` 标签中：

```html
<script>
  window.__NEXT_DATA__ = {"props": {"pageProps": {...}}, "page": "/", ...}
</script>
```

客户端初始化时直接从 `window.__NEXT_DATA__` 读取，无需重发网络请求，这一过程称为数据"再注水"（Rehydration）。序列化数据体积过大（通常建议控制在 **50KB** 以内）会直接增加 HTML 体积，拖慢 TTFB（Time To First Byte）。

### 流式 SSR（Streaming SSR）

React 18 引入的 `renderToPipeableStream()` 支持流式 SSR：服务器不必等待所有数据就绪后再发送 HTML，而是先发送 Shell（页面框架），将慢速数据部分用 `<Suspense>` 包裹，等数据到达后通过同一 HTTP 连接追加对应 HTML 片段。这使得 **TTFB 可低至 200ms 以下**，即便页面内某个 AI 推理接口需要 3 秒才能返回，用户也能立即看到页面骨架。

---

## 实际应用

**AI 内容平台的搜索引擎优化**：以基于 GPT-4 生成文章摘要的新闻平台为例，若使用 CSR，Googlebot 只会抓取空白 `<div id="root">`；改用 SSR 后，每次请求在服务端调用 OpenAI API，将摘要填充进 `<meta>` 标签和正文 HTML，爬虫可直接读取完整内容，SEO 效果显著提升。

**Next.js `getServerSideProps` 接入数据库**：在 Next.js 13 之前的 Pages Router 中，`getServerSideProps` 是标准的 SSR 数据入口。该函数仅在 Node.js 端执行，可以直接使用 `pg`（PostgreSQL 客户端）或 Prisma ORM 查询数据库，查询结果作为 `props` 传入页面组件，不会有任何数据库凭据泄漏到客户端。

**个性化页面渲染**：电商平台根据 Cookie 中的用户 ID，在服务端查询个性化推荐商品，直接渲染到首屏 HTML 中。这一场景中 SSR 相比 CSR 减少了一次额外的 API round-trip，首屏个性化内容的展示时间缩短约 400–800ms。

---

## 常见误区

**误区一：SSR 一定比 CSR 更快**。SSR 改善的是 FCP，但 **Time To Interactive（TTI）** 不一定更短——页面虽然"看起来"有内容，但在 Hydration 完成前按钮是不可点击的。对于交互极重、数据实时变化的仪表盘类页面，SSR 带来的 Hydration 开销可能使 TTI 反而更长，此类场景选择 CSR 或 CSR + 骨架屏更合适。

**误区二：SSR 不消耗服务器资源**。服务端每次请求都需要执行 `renderToString()`，其 CPU 开销远大于仅返回静态文件或 JSON 的接口。高并发场景下未做缓存的 SSR 服务器极易因 CPU 占满而响应超时。正确做法是对不依赖用户身份的页面设置 `Cache-Control: s-maxage=60`，让 CDN 缓存渲染结果，或结合 ISR 策略降低服务端压力。

**误区三：Hydration 是"免费"的**。部分开发者认为服务端已渲染好 HTML，浏览器端就无需任何工作。实际上 Hydration 需要下载与 CSR 体积相当的 JS bundle，并遍历整棵 DOM 树完成事件绑定，在低端移动设备上这一过程可耗时 **2–5 秒**。React Server Components（RSC）架构通过减少需要 Hydration 的组件数量来缓解此问题。

---

## 知识关联

SSR 的正确执行依赖对**虚拟 DOM 原理**的理解：`renderToString()` 本质上是对虚拟 DOM 树的深度优先遍历序列化，理解 Fiber 节点结构有助于排查 Hydration Mismatch。**服务器基础概念**中的 HTTP 长连接、流式响应（chunked transfer encoding）是流式 SSR 的传输基础——`renderToPipeableStream` 依赖 Node.js 的 Writable Stream 接口将 HTML 分块发送。

掌握 SSR 之后，自然延伸到**SSG（静态站点生成）与 ISR（增量静态再生）**：SSG 是 SSR 在构建时一次性执行的变体，生成纯静态 HTML；ISR 则在 SSG 基础上引入 `revalidate` 时间窗口，允许后台按需重新生成页面，三者构成现代 Web 渲染策略的完整谱系，需根据页面数据的实时性要求、个性化程度和流量规模综合选择。