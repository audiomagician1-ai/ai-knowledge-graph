---
id: "ssg-isr"
concept: "SSG与ISR"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 4
is_milestone: false
tags: ["next.js", "static-generation", "ssg"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# SSG与ISR：静态站点生成与增量静态再生成

## 概述

SSG（Static Site Generation，静态站点生成）是一种在**构建时**（build time）将页面预先渲染为纯 HTML 文件的前端渲染策略。与 SSR 在每次请求时动态执行服务端逻辑不同，SSG 在 `npm run build` 执行阶段就完成所有页面的 HTML 生成，部署后 CDN 直接响应静态文件，无需任何运行时服务器计算。

ISR（Incremental Static Regeneration，增量静态再生成）由 Vercel 团队在 2020 年随 Next.js 9.5 版本引入，是对纯 SSG 的关键扩展。ISR 解决了 SSG 最核心的痛点：内容更新必须触发全量重新构建。ISR 允许在不重新构建整个站点的前提下，按页面粒度异步更新静态内容，将"构建时静态"与"运行时按需刷新"结合为一套机制。

在 AI 工程与 Web 前端场景中，SSG 与 ISR 尤其适合内容驱动型产品：文档站、博客、AI 生成内容展示页、产品详情页等。其核心价值在于 Time To First Byte（TTFB）极低——静态文件由 CDN 边缘节点直接响应，延迟通常可降至 10ms 以内，而 SSR 节点往往需要 100~500ms 的服务端处理时间。

---

## 核心原理

### SSG 的构建流程

SSG 的工作流可以用以下步骤描述：

1. **数据获取阶段**：构建工具调用 `getStaticProps`（Next.js）或等效 API，从 CMS、数据库或文件系统拉取数据。
2. **路径枚举阶段**：对于动态路由（如 `/posts/[id]`），`getStaticPaths` 返回所有合法路径列表，构建器逐一生成对应 HTML。
3. **渲染输出阶段**：每个路径对应一个独立的 `.html` 文件和关联的 `.json` 数据文件，客户端 Hydration 时直接复用该 JSON，不再发起额外请求。

关键限制：`getStaticPaths` 必须在构建时返回完整路径集合。若站点有 10 万篇文章，构建阶段就需枚举并渲染 10 万个 HTML 文件，构建时间线性增长。

### ISR 的 Stale-While-Revalidate 机制

ISR 的底层采用 **stale-while-revalidate** HTTP 缓存语义，其逻辑如下：

```
用户请求 → CDN/服务器检查缓存年龄
  ├─ 年龄 < revalidate 秒数 → 返回缓存（stale 但有效）
  ├─ 年龄 ≥ revalidate 秒数 → 返回旧缓存（立即响应），同时后台触发重新生成
  └─ 缓存不存在（首次访问新路径）→ 按需生成，阻塞等待，生成后缓存
```

在 Next.js 中配置 ISR 的核心代码：

```js
export async function getStaticProps() {
  const data = await fetchArticle();
  return {
    props: { data },
    revalidate: 60, // 单位：秒，60秒后标记为过期
  };
}
```

`revalidate: 60` 意味着：**在某次请求后的 60 秒内**，所有访问均命中缓存；60 秒过后的首个请求仍获得旧页面，但会在后台触发异步重新渲染；下一个请求才会获得新内容。这种"最终一致性"模型意味着内容更新存在最多 `revalidate` 秒的延迟。

### On-Demand ISR（按需重验证）

Next.js 12.1 引入了 On-Demand ISR，允许通过调用 `res.revalidate('/posts/123')` 主动清除特定页面的缓存，而不依赖时间窗口。这在 CMS Webhook 场景中极为实用：编辑在 Contentful 或 Strapi 发布新内容后，CMS 触发 Webhook → Next.js API 路由调用 `revalidate` → 对应页面在下次请求时立即重新生成，延迟降至秒级甚至毫秒级，彻底消除固定 `revalidate` 时间窗口的等待。

### SSG 中的 `fallback` 策略

`getStaticPaths` 的 `fallback` 参数控制构建时未枚举路径的处理方式：

| fallback 值 | 行为 |
|---|---|
| `false` | 未枚举路径返回 404 |
| `true` | 首次访问显示加载态，后台生成后缓存 |
| `'blocking'` | 首次访问阻塞等待，生成完成后响应（类似 SSR，但之后缓存为静态） |

`fallback: 'blocking'` 与 ISR 结合使用时，可实现"仅构建热门页面，长尾页面首次访问时按需生成"的策略，兼顾构建速度与全量覆盖。

---

## 实际应用

**AI 内容展示平台**：假设一个平台每天由 AI 批量生成 500 篇文章，若使用纯 SSG，每次全量构建需渲染历史所有文章（可能超过 10 万篇），构建时间不可接受。使用 ISR + `fallback: 'blocking'` 的方案：仅在构建时生成最近 1000 篇，其余页面首次访问时按需生成并永久缓存；新增文章通过 CMS Webhook 触发 On-Demand ISR 更新。

**电商产品详情页**：商品价格和库存频繁变动，但商品描述、图片等内容相对稳定。可将静态内容用 SSG/ISR 渲染（`revalidate: 300`），而价格和库存在客户端通过 SWR 或 React Query 实时请求独立的 API 端点，实现"静态骨架 + 动态数据"的混合策略。

**技术文档站**：Nextra（基于 Next.js 的文档框架）使用纯 SSG，将 Markdown 文件在构建时全量转换为 HTML。文档更新通过 CI/CD 触发全量重新构建，因文档页数有限（通常不超过数百页），构建时间在 30 秒内，纯 SSG 足够。

---

## 常见误区

**误区一：ISR 等于"定时刷新"**  
`revalidate: 60` 并不意味着每 60 秒服务器就主动重新构建页面。实际上，重新构建只在"60 秒过期后有真实用户请求到来"时才被触发。若某页面 60 秒内无任何访问，不会消耗任何服务端资源。这是 ISR 与定时任务（cron job）的本质区别。

**误区二：SSG 页面完全不支持动态内容**  
SSG 只是服务端渲染部分静态化，客户端 Hydration 后页面是完整的 React 应用。个性化内容（用户信息、购物车）、实时数据（股价、在线人数）完全可以在客户端通过 API 请求填充。误将 SSG 与"纯静态无交互"画等号会导致不必要的架构妥协。

**误区三：ISR 在所有部署环境均可用**  
ISR 的 On-Demand 重验证和后台再生成依赖运行时 Node.js 服务器（或 Vercel 的 Edge Runtime）。若将 Next.js 项目导出为纯静态（`next export`），则 ISR 特性完全失效，`revalidate` 字段会被忽略。部署至 Netlify、AWS S3 等纯静态托管时，需确认平台是否支持 Next.js 的 ISR 运行时；Vercel 原生支持，其他平台需额外适配。

---

## 知识关联

**与 SSR 的关系**：SSR 在每次 HTTP 请求时执行 `getServerSideProps`，适合需要请求级别数据（如鉴权后的个人化内容）的页面；SSG 在构建时执行 `getStaticProps`，适合内容对所有用户一致的页面。ISR 是二者之间的折衷——内容具有时效性但不需要毫秒级实时更新时，ISR 是比 SSR 性能更优的选择，因为命中缓存的 ISR 页面响应时间与纯静态相同。

**与打包工具（Webpack/Vite）的关系**：Webpack（Next.js 默认）和 Vite（Nuxt 3、Astro 等框架采用）在 SSG 构建阶段负责模块打包、代码分割和资产优化。SSG 的构建性能直接受打包工具影响：Next.js 13+ 引入基于 Rust 的 Turbopack 将大型站点的 SSG 构建速度提升约 10 倍，解决了万级页面构建缓慢的瓶颈。理解打包工具的 Tree Shaking 和 Code Splitting 机制，有助于优化 SSG 输出的单页 JavaScript Bundle 体积，进而提升 Hydration 速度。
