---
id: "pwa-basics"
concept: "PWA基础"
domain: "ai-engineering"
subdomain: "web-frontend"
subdomain_name: "Web前端"
difficulty: 5
is_milestone: false
tags: ["移动端"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# PWA基础

## 概述

PWA（Progressive Web App，渐进式Web应用）是由Google工程师Alex Russell于2015年提出的一套Web应用增强标准，旨在让Web应用具备原生应用的用户体验。其核心理念是"渐进式"——应用在支持新特性的浏览器中提供完整功能，在旧版浏览器中也能正常降级运行，不会因兼容性问题导致白屏或崩溃。

PWA的技术基础建立在三大支柱之上：Service Worker（服务工作线程）、Web App Manifest（Web应用清单）和HTTPS安全协议。三者共同构成了PWA区别于普通Web页面的核心能力边界。2018年iOS 11.3开始支持Service Worker，标志着PWA真正实现跨主流平台覆盖，包括Chrome（从版本40起陆续支持各项PWA特性）、Firefox、Safari和Edge。

PWA的工程意义在于它将离线访问、消息推送、桌面安装等原本只属于原生App的能力以纯Web技术栈实现，使得开发团队无需分别维护iOS/Android/Web三套代码库，单一代码库即可覆盖所有平台，大幅降低多端开发成本。

## 核心原理

### Service Worker：离线能力的引擎

Service Worker是PWA实现离线访问的关键技术。它是一个在浏览器后台独立线程中运行的JavaScript文件，完全脱离主线程，因此无法直接访问DOM。Service Worker通过拦截网络请求（fetch事件）并返回缓存内容，实现离线可用性。其生命周期分为三个阶段：

1. **安装（Install）**：Service Worker首次注册时触发，通常在此阶段预缓存静态资源
2. **激活（Activate）**：旧版SW被新版替换后触发，通常在此清理过期缓存
3. **运行（Active）**：处于激活状态，拦截受控页面的所有网络请求

注册Service Worker的标准代码如下：

```javascript
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js', { scope: '/' })
    .then(reg => console.log('SW registered:', reg.scope));
}
```

`scope`参数决定Service Worker的作用范围，默认为SW脚本文件所在目录。

### 缓存策略：平衡新鲜度与可用性

PWA通过Cache API实现精细化缓存控制，常见的五种缓存策略各有适用场景：

- **Cache First（缓存优先）**：优先返回缓存，缓存未命中再发网络请求，适合字体、图片等不频繁更新的静态资源
- **Network First（网络优先）**：优先请求网络，网络失败才读缓存，适合用户动态数据（如购物车、消息列表）
- **Stale While Revalidate（过期重验证）**：立即返回缓存内容同时在后台更新缓存，适合对实时性要求不严格的内容
- **Cache Only**：仅从缓存读取，适合纯离线应用场景
- **Network Only**：绕过缓存直接请求网络，适合支付等强一致性场景

使用Workbox库（Google维护）可以极大简化缓存策略的配置，只需几行声明式代码即可替代复杂的Service Worker手写逻辑。

### Web App Manifest：安装与外观定义

`manifest.json`是一个JSON格式的配置文件，定义PWA安装到设备主屏后的外观与行为。以下是关键字段说明：

```json
{
  "name": "我的应用",
  "short_name": "应用",
  "start_url": "/index.html?utm_source=pwa",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3367D6",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

`display`字段控制浏览器UI的显示模式：`standalone`隐藏浏览器地址栏，使应用看起来与原生App一致；`fullscreen`进一步隐藏系统状态栏；`browser`保留完整浏览器UI。Chrome会在用户满足特定条件（同一站点访问≥2次、间隔≥5分钟）时自动触发"添加到主屏"横幅提示（A2HS）。

### HTTPS强制要求

Service Worker具有拦截所有网络请求的能力，若部署在不安全的HTTP环境下，极易被中间人攻击利用。因此浏览器规定Service Worker只能在HTTPS环境（或localhost开发环境）下注册运行。这是PWA的硬性安全约束，非可选项。

## 实际应用

**Twitter Lite**是PWA工程实践的标杆案例。2017年Twitter将其移动Web端改造为PWA后，会话页面加载时间降低33%，推文发送量增加75%，跳出率下降20%。其核心实现是将时间线数据采用Network First策略缓存，将静态JS/CSS资源采用Cache First策略处理。

**AI工程场景中的PWA应用**：将AI推理结果展示界面构建为PWA，可在网络不稳定的工厂或医疗环境中离线展示最近一次推理结果，Service Worker缓存最后N条推理记录，通过Background Sync API在网络恢复后将离线期间产生的用户标注数据批量同步回服务器。

**Lighthouse审计工具**是Google提供的PWA合规性检测工具，集成于Chrome DevTools，从性能（Performance）、可访问性（Accessibility）、最佳实践（Best Practices）、SEO和PWA五个维度输出0-100分评分，PWA维度包含12项检查项，包括manifest配置完整性、Service Worker注册状态和HTTPS部署情况。

## 常见误区

**误区一：Service Worker会自动更新**
很多开发者认为修改`sw.js`文件后用户会立即获得新版本。实际上，即使SW文件内容已变更，旧版SW会持续控制所有已打开的页面，新SW只会在所有旧页面关闭后才被激活。若需立即生效，必须在安装阶段调用`self.skipWaiting()`，在激活阶段调用`clients.claim()`，并在前端监听`controllerchange`事件提示用户刷新页面。

**误区二：PWA的离线能力会自动覆盖所有页面**
Service Worker的拦截范围仅限于`scope`所定义的路径范围内，且只有被预缓存或运行时缓存命中的资源才能离线访问。如果开发者没有在`install`事件中显式缓存必要资源，用户在离线状态下依然会看到浏览器默认的"无网络连接"错误页，而非自定义的离线页面。

**误区三：响应式设计即可满足PWA要求**
虽然响应式设计是PWA推荐的UI适配手段（manifest的`display: standalone`模式下视口宽度可能与预期不同），但响应式CSS本身并不赋予应用任何离线能力、消息推送能力或可安装性。PWA的核心能力来自Service Worker和Manifest，响应式设计解决的是多屏幕尺寸下的视觉适配问题，两者针对不同层次的问题。

## 知识关联

**与响应式设计的关系**：响应式设计（Responsive Design）通过CSS媒体查询解决多设备屏幕尺寸适配，而PWA在此基础上增加了离线能力和可安装性。实现PWA时需要响应式布局确保安装到主屏后的应用在各尺寸设备上正确展示，`manifest.json`中的`viewport`设置也需与页面`<meta name="viewport">`保持一致。

**与Web性能优化的关联**：PWA的缓存策略是Web性能优化的有效手段之一。Cache First策略可将静态资源的响应时间从几百毫秒降低到几毫秒（直接读取本地Cache Storage），配合HTTP/2 Server Push和代码分割，构成现代Web性能优化的完整方案。Lighthouse的Performance评分与PWA评分高度相关，优化PWA时两者需协同考虑。

**与Web Push通知的延伸**：掌握PWA基础后，可进一步学习Push API和Notifications API，实现在应用未打开状态下向用户推送消息。这依赖于Service Worker在后台持续运行的能力，是PWA超越普通Web页面用户留存能力的核心机制。