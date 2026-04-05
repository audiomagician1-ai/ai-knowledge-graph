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
quality_tier: "A"
quality_score: 79.6
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

# SSG与ISR：静态站点生成与增量静态再生成

## 概述

SSG（Static Site Generation，静态站点生成）是指在**构建阶段**（build time）预先将页面渲染为静态HTML文件的技术。与SSR在每次请求时动态渲染不同，SSG在`npm run build`执行时一次性生成所有页面的HTML，这些文件随后可直接部署到CDN，无需服务器实时计算。Next.js在2020年9.3版本中正式将SSG提升为一等公民，引入了`getStaticProps`和`getStaticPaths`两个专属API。

ISR（Incremental Static Regeneration，增量静态再生成）是Next.js 9.5版本（2020年8月）引入的机制，解决了纯SSG的核心痛点：**构建后数据无法更新**。ISR允许单个页面在后台按需或定时重新生成，而不需要重新构建整个站点。这意味着一个拥有10万个产品页面的电商站点，可以在无需全量重建的情况下，让某个商品页的价格数据在60秒内反映最新状态。

两者的区别在于生命周期：SSG的内容生命周期等于两次部署之间的间隔（可能是数天），而ISR的内容生命周期可精确控制到秒级。这两种机制均依赖Webpack/Vite在构建阶段的代码分割与模块图分析能力来确定哪些页面需要预渲染。

---

## 核心原理

### SSG的构建时渲染机制

SSG的执行流程分为三个阶段：**数据获取 → HTML生成 → 静态文件输出**。在Next.js中，`getStaticProps`函数只在Node.js环境中运行，其返回值被序列化为JSON并嵌入页面的`__NEXT_DATA__`脚本标签，供客户端hydration使用。

```javascript
// 此函数仅在构建时执行，永远不会暴露给浏览器
export async function getStaticProps() {
  const res = await fetch('https://api.example.com/products');
  const products = await res.json();
  return {
    props: { products },
  };
}
```

对于动态路由（如`/products/[id]`），必须配合`getStaticPaths`使用，显式声明需要预渲染的路径列表。`fallback: 'blocking'`选项表示对未预渲染的路径执行SSR降级处理；`fallback: false`表示未声明路径返回404；`fallback: true`则先返回loading状态再异步生成。

### ISR的"过期重验证"算法（Stale-While-Revalidate）

ISR本质上是HTTP缓存策略**stale-while-revalidate**在服务器渲染层的实现。配置核心是`revalidate`字段，单位为秒：

```javascript
export async function getStaticProps() {
  const data = await fetchData();
  return {
    props: { data },
    revalidate: 60, // 60秒后此页面被标记为"过期"
  };
}
```

工作流程如下：
1. 第一次请求：返回构建时生成的静态HTML（新鲜）
2. 60秒内的后续请求：继续返回同一份缓存HTML
3. 60秒后的第一个请求：返回**旧的**缓存HTML（用户无感知延迟），同时在后台触发页面重新生成
4. 重新生成完成后：下一个请求获得新HTML

这意味着ISR的数据最大延迟 = `revalidate`秒 + 重新生成所需时间。若重新生成失败，旧版本HTML将继续提供服务，不会出现503。

### ISR的按需重验证（On-Demand Revalidation）

Next.js 12.1版本引入了`revalidatePath`和`revalidateTag`API，允许通过Webhook触发指定页面的立即重新生成，绕过时间限制：

```javascript
// pages/api/revalidate.js
export default async function handler(req, res) {
  await res.revalidate('/products/42'); // 立即使该页面的缓存失效
  return res.json({ revalidated: true });
}
```

CMS（如Contentful、Sanity）可在内容发布时调用此API，实现**内容更新后秒级反映**到生产环境，同时保持静态文件的CDN分发优势。

---

## 实际应用

**博客与文档站点（纯SSG最佳场景）**：内容更新频率低（每周一次），所有页面在每次Git推送后重新构建。Gatsby框架专门针对此场景优化，其GraphQL数据层在构建时统一聚合所有数据源。构建一个1000篇文章的博客通常耗时30-120秒，生成的HTML可部署到Vercel、Netlify等平台的边缘CDN节点。

**电商产品页面（ISR典型场景）**：某电商平台有50万个SKU页面，不可能在每次价格变动时全量重建。设置`revalidate: 30`意味着价格更新最多30秒后反映到用户页面，同时首字节时间（TTFB）保持在50ms以内（因为CDN命中）。与SSR相比，ISR在高并发场景下可将服务器负载降低90%以上，因为大多数请求直接由CDN响应。

**新闻媒体站点**：突发新闻文章使用按需重验证（On-Demand ISR），记者点击"发布"按钮时CMS发送Webhook，触发`revalidatePath('/news/breaking-story')`，文章15秒内在全球CDN刷新。常规文章使用`revalidate: 300`（5分钟）的定时策略。

---

## 常见误区

**误区一：认为SSG页面完全不能有动态内容**。SSG只是HTML骨架是静态的，页面在浏览器中完成hydration后，仍然可以通过客户端`fetch`获取实时数据。典型模式是：用SSG生成产品页面的静态骨架（标题、描述、图片），再用`useEffect`客户端请求实时库存数量。这种"静态骨架+动态片段"模式不需要ISR也能解决部分动态需求。

**误区二：混淆ISR的`revalidate`与HTTP缓存的`max-age`**。`revalidate: 60`不等于设置`Cache-Control: max-age=60`。ISR的60秒是**服务器端**判断是否触发后台重生成的阈值，Next.js实际设置的HTTP响应头是`s-maxage=60, stale-while-revalidate`，允许CDN在超期后继续服务旧内容同时后台刷新。直接修改`Cache-Control`响应头可能破坏ISR的缓存行为。

**误区三：认为ISR可以替代所有SSR场景**。ISR无法处理**用户个性化内容**（如"您的购物车"）和需要请求时认证的页面。`getStaticProps`中无法访问请求的Cookie或Authorization Header，因此用户专属页面必须使用SSR（`getServerSideProps`）或客户端渲染。ISR的适用条件是页面内容对所有用户相同但需要定期更新。

---

## 知识关联

**与SSR的关系**：SSR（`getServerSideProps`）在每次请求时执行数据获取，TTFB通常为200-500ms；SSG+ISR在缓存命中时TTFB为10-50ms，但代价是数据存在`revalidate`秒的延迟窗口。Next.js允许同一项目中不同页面混用SSR、SSG和ISR，选择依据是"数据更新频率"和"是否需要请求级别的上下文"。

**与Webpack/Vite的关系**：SSG依赖打包工具完成构建时代码分割。Vite在开发模式使用ESM按需编译，但`vite build`时生成的静态资源哈希名称（如`index.abc123.js`）使得HTML可以设置极长的CDN缓存TTL（通常1年），与ISR的HTML层短缓存形成配合——JS/CSS永久缓存，HTML层按`revalidate`周期刷新。

**框架实现差异**：Astro框架的SSG默认输出0KB JavaScript的纯HTML，其"孤岛架构"（Islands Architecture）允许页面中单个交互组件hydrate而非整页hydrate，与Next.js ISR的整页重生成策略形成对比。Nuxt 3通过`useFetch`的`server: true`选项和`nitro`引擎实现类似ISR的缓存行为，配置API为`routeRules: { '/products/**': { swr: 60 } }`。