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
---
# PWA基础

## 概述

PWA（Progressive Web App，渐进式网络应用）是2015年由Google工程师Alex Russell首次提出的一套Web应用构建规范。其核心思想是利用现代浏览器API，使网页应用具备原生App的离线访问、推送通知、可安装到桌面等能力，同时保留Web的跨平台、免安装分发优势。

PWA并非单一技术，而是三项核心技术的组合：Service Worker（服务工作者线程）、Web App Manifest（网络应用清单）、HTTPS安全协议。2017年Safari开始支持Service Worker，2018年Windows版Chrome支持PWA安装，标志着PWA进入主流应用阶段。目前全球已有Twitter Lite、Pinterest、Starbucks等大型应用采用PWA方案，Twitter Lite使PWA版本的数据流量减少了70%。

对于AI工程中的Web前端方向，PWA的价值在于：AI推理结果往往需要快速展示，离线缓存可让用户在网络中断后仍访问已加载的模型推理界面；推送通知可用于异步AI任务（如图像识别批处理）完成后主动通知用户；而响应式设计与PWA结合，能使AI前端产品同时覆盖桌面和移动端。

## 核心原理

### Service Worker 生命周期与缓存控制

Service Worker是运行在浏览器后台的独立JavaScript线程，与主页面线程完全分离，无法直接访问DOM。其生命周期分为三个阶段：**注册（Register）→ 安装（Install）→ 激活（Activate）**，激活后进入拦截网络请求的工作状态。

```javascript
// 注册 Service Worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js', { scope: '/' })
    .then(reg => console.log('SW registered:', reg.scope));
}
```

Service Worker通过Cache Storage API实现缓存策略，常见的有五种：
- **Cache First（缓存优先）**：适合静态资源，先查缓存，缓存不存在才请求网络
- **Network First（网络优先）**：适合频繁更新的API数据
- **Stale While Revalidate**：返回缓存内容同时后台更新缓存，适合AI模型元数据
- **Network Only**：强制走网络，适合支付等实时场景
- **Cache Only**：仅读缓存，适合完全离线场景

关键注意点：Service Worker只能在HTTPS或localhost下注册，这是浏览器的安全强制要求，HTTP环境下`navigator.serviceWorker`接口直接不可用。

### Web App Manifest 配置规范

Manifest是一个JSON文件，告诉浏览器如何在用户桌面安装和展示PWA。最小可用配置须包含`name`、`icons`（至少144×144px）、`start_url`、`display`四个字段。`display`字段决定应用启动方式：`standalone`（隐藏浏览器UI，最接近原生App）、`fullscreen`（全屏）、`minimal-ui`（保留最小导航控件）、`browser`（普通浏览器标签页）。

```json
{
  "name": "AI图像分析器",
  "short_name": "AI分析",
  "start_url": "/index.html?source=pwa",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1a73e8",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

HTML中通过`<link rel="manifest" href="/manifest.json">`引入。Chrome DevTools的Application面板可验证Manifest配置是否合法，以及当前PWA是否满足"可安装"条件（Installability criteria）。

### PWA可安装性触发条件

浏览器触发"添加到主屏幕"提示（`beforeinstallprompt`事件）需同时满足：① 已注册Service Worker且处于激活状态；② 存在合法Manifest且包含必要字段；③ 站点通过HTTPS访问；④ 用户在30秒内有过交互行为（部分浏览器要求）。

开发者可通过监听`beforeinstallprompt`事件延迟并自定义安装提示时机，而非依赖浏览器默认弹出：

```javascript
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault(); // 阻止默认提示
  deferredPrompt = e;
  showCustomInstallButton(); // 在合适时机显示自定义按钮
});
```

## 实际应用

**AI前端离线推理缓存**：当页面集成了TensorFlow.js模型时，可使用Cache First策略缓存模型权重文件（通常为`.json`+`.bin`格式），避免每次加载都重新下载数十MB的模型文件。Service Worker可在Install阶段预缓存模型资源：

```javascript
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('ai-model-v1').then(cache =>
      cache.addAll(['/model/model.json', '/model/weights.bin'])
    )
  );
});
```

**异步AI任务推送通知**：用户提交图像识别任务后可关闭页面，后台任务完成时通过Web Push协议（基于VAPID密钥认证）向Service Worker推送消息，Service Worker调用`showNotification()`弹出系统通知，点击通知可重新打开PWA并跳转至结果页。

**Lighthouse评分与PWA审计**：Google的Lighthouse工具（Chrome DevTools内置）提供专门的PWA审计项，满分100分的PWA需通过12项检查，包括页面在离线时返回200状态码、Manifest中包含苹果触控图标等。实际项目中Lighthouse PWA评分可作为CI流水线的质量门禁。

## 常见误区

**误区一：认为Service Worker会让所有请求都走缓存**。Service Worker只在其`scope`范围内拦截请求，且只有在`fetch`事件处理函数中明确调用缓存逻辑才生效。如果`sw.js`中没有注册`fetch`监听器，所有请求仍正常走网络，Service Worker不会自动缓存任何内容。

**误区二：以为PWA只能在移动端使用**。PWA在桌面端Chrome（Windows/macOS/Linux）和Edge上同样支持安装，安装后会出现在系统应用列表中，可独立窗口运行，与原生应用体验高度一致。对于AI工具类应用，桌面PWA的使用场景甚至多于移动端。

**误区三：混淆Service Worker更新与页面刷新**。当`sw.js`文件内容发生变化时，浏览器会下载新版本但不会立即激活——新Service Worker处于`waiting`状态，必须等所有使用旧SW的页面关闭后才自动激活。开发阶段可在`activate`事件中调用`self.skipWaiting()`强制跳过等待，但生产环境需谨慎，避免新旧缓存不一致导致页面异常。

## 知识关联

**与响应式设计的关系**：响应式设计（先决知识）解决了PWA在不同设备上的布局自适应问题。Manifest中的`display: standalone`模式下浏览器UI被隐藏，页面需要用CSS媒体查询独立处理不同分辨率的视口，尤其是iOS Safari的安全区域（safe-area-inset）需用`env()`函数处理刘海屏适配。二者共同作用才能使PWA在手机、平板、桌面三端呈现一致的高质量体验。

**在AI工程前端体系中的位置**：PWA将Web前端的技术边界从"需要网络的展示层"扩展到"具备离线能力的本地应用层"。在AI Web应用中，PWA与WebAssembly（用于在浏览器端运行AI推理）、IndexedDB（用于本地存储推理历史数据）形成完整的端侧AI前端技术栈，Service Worker可充当这些技术的协调调度层，管理资源加载优先级和后台同步逻辑。
