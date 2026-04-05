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


# 服务端渲染（SSR）

## 概述

服务端渲染（Server-Side Rendering，SSR）是指在用户发起 HTTP 请求时，由服务器动态执行 JavaScript 框架逻辑、生成完整 HTML 字符串，再将该字符串作为响应体返回给浏览器的技术模式。与客户端渲染（CSR）不同，浏览器接收到的不是空白的 `<div id="app"></div>` 占位符，而是已填充真实数据的完整 DOM 结构，用户无需等待 JS bundle 下载和执行即可看到内容。

SSR 并非新概念——PHP、JSP、ASP 等传统技术在 2000 年代初就以模板引擎方式在服务端拼接 HTML。现代 SSR 的特殊之处在于它与前端框架（React、Vue、Svelte）深度结合，在服务端复用同一套组件代码，这一范式由 Next.js（2016 年发布）和 Nuxt.js（同年发布）推广普及，因此常被称为"同构渲染"（Isomorphic Rendering）或"通用渲染"（Universal Rendering）。

SSR 之所以在 AI 工程的 Web 后端场景中受到重视，是因为 AI 驱动的内容（如搜索结果摘要、推荐列表）需要在服务端完成模型推理后立即嵌入 HTML，确保搜索引擎爬虫（Googlebot 等）能直接抓取到语义内容，同时降低首屏内容绘制（FCP）时间，这对 SEO 和用户留存率有直接量化影响。

---

## 核心原理

### 1. 渲染流水线与 TTFB 的权衡

SSR 的完整流水线为：**接收请求 → 数据获取 → 组件树渲染 → 序列化为 HTML 字符串 → 传输 → 客户端水合（Hydration）**。在 React 中，`renderToString()` 方法同步遍历虚拟 DOM 树，将每个组件的 `render` 输出拼接为 HTML 字符串；`renderToPipeableStream()`（React 18 引入）则采用流式传输，允许服务器在完成根节点渲染后立即开始发送字节，不必等待整棵树渲染完毕。

TTFB（Time to First Byte）是 SSR 的核心性能指标。由于服务端需要完成数据库查询或 API 调用，TTFB 通常高于纯 CSR 的静态文件响应（CSR 可能 <50ms，SSR 数据库查询场景可能需要 200–800ms）。工程师需要通过 Redis 缓存数据层或 CDN 边缘缓存 HTML 片段来压缩这一延迟。

### 2. 水合（Hydration）机制

服务端返回的 HTML 是静态的，不含事件监听器。浏览器下载并执行 JS bundle 后，框架会执行"水合"过程：将内存中重建的虚拟 DOM 树与已有的真实 DOM 节点进行校验匹配（React 称之为 reconciliation），绑定事件处理器，使页面变为可交互状态。

水合的关键约束是**服务端与客户端输出的 HTML 必须严格一致**。若服务端渲染了 `<span>服务器时间: 2024-01-01</span>`，而客户端重新执行组件时生成了不同的时间戳，React 会抛出 Hydration Mismatch 警告，并强制重新渲染整棵子树，导致闪烁（FOUC）和性能损失。因此，依赖 `window`、`localStorage`、`Date.now()` 等浏览器专属 API 的代码必须用 `useEffect` 包裹，仅在客户端执行。

### 3. 数据获取模式与 getServerSideProps

在 Next.js 的 Pages Router 架构中，SSR 数据获取通过 `getServerSideProps` 函数实现，该函数在每次请求时于服务端执行，其返回值通过 `__NEXT_DATA__` 这个内联 `<script>` JSON 注入 HTML，同时作为组件 props。这套机制保证了水合时客户端无需二次请求数据。

```javascript
export async function getServerSideProps(context) {
  const { params, req, res } = context;
  const data = await fetchFromDB(params.id); // 仅在服务端执行
  return { props: { data } };
}
```

在 App Router（Next.js 13+）中，Server Components 模式进一步演化：组件本身即可标记为 `async`，直接 `await` 数据库调用，而无需将数据通过 props 传递，序列化开销更低。

---

## 实际应用

**电商商品详情页**：商品价格、库存状态需要实时从数据库读取，不能被 CDN 长期缓存。使用 SSR 时，每次访问 `/products/[id]` 均触发服务端查询，返回含真实价格的完整 HTML，爬虫可直接索引商品信息，对 Google Shopping 收录至关重要。

**AI 内容摘要页面**：在 RAG（Retrieval-Augmented Generation）系统的前端展示层，用户查询触发服务端向向量数据库检索，再调用 LLM API 生成摘要，最终将摘要文本嵌入 HTML 返回。这一场景中，SSR 允许将 API 密钥保留在服务端，避免暴露给浏览器。流式 SSR（`renderToPipeableStream`）还可配合 HTTP 分块传输（chunked transfer encoding）逐步输出 LLM 的流式响应，实现类 ChatGPT 的打字机效果而无需客户端 WebSocket。

**新闻媒体网站**：文章内容在发布后相对稳定，但阅读量、评论数等社交数据需要实时化。常见方案是 SSR 渲染文章主体 + 客户端 SWR（stale-while-revalidate）获取动态数据，兼顾 SEO 和交互性。

---

## 常见误区

**误区一：SSR 一定比 CSR 快**。SSR 减少的是 FCP（首次内容绘制）时间，但 TTI（可交互时间）未必更短——用户看到内容后仍需等待 JS 水合完成才能点击按钮。若 JS bundle 达到 1MB 以上，水合过程本身可能阻塞主线程超过 3 秒，体验反而劣于轻量 CSR 应用。

**误区二：SSR 对 SEO 总是必要的**。Google 的 Googlebot 自 2019 年起已能渲染 JavaScript，对于更新频率低的内容型页面，SSG（静态站点生成）在 SEO 效果上与 SSR 相当，且无服务端计算开销。SSR 真正不可替代的场景是**依赖请求上下文（cookie、用户身份）的个性化内容**。

**误区三：服务端组件等于 SSR**。React Server Components（RSC）是一种在服务端执行但**不包含水合步骤**的组件模型，它们不向客户端发送对应的 JS 代码。传统 SSR 的所有组件代码都需要在客户端重新执行以完成水合，而 RSC 永久留在服务端，两者的 bundle 分割策略和组件树结构完全不同。

---

## 知识关联

**前置概念衔接**：SSR 的水合过程直接依赖虚拟 DOM 的 diff 算法——服务端生成的真实 DOM 与客户端虚拟 DOM 的 reconciliation 是水合能否成功的关键。若对虚拟 DOM 的 fiber 节点结构不熟悉，Hydration Mismatch 的根因排查会极为困难。服务器基础概念中的 Node.js 事件循环也直接影响 SSR 性能：`renderToString` 是同步阻塞操作，高并发时会阻塞 Node.js 主线程，必须结合 Worker Threads 或水平扩容来应对。

**后续概念展开**：掌握 SSR 后，可进一步学习 SSG（静态站点生成）与 ISR（增量静态再生成）。SSG 是 SSR 在构建时而非请求时执行的变体，适合内容不频繁变化的场景；ISR（Next.js 独有特性）在 SSG 基础上引入了 `revalidate` 秒级时间窗口，实现"按需重新生成静态页面"，可理解为 SSR 与 SSG 在缓存策略维度上的连续谱系中的中间点。