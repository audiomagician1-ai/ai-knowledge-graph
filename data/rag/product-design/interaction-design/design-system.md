# 设计系统

## 概述

设计系统（Design System）是将产品界面中的视觉语言、交互模式、组件库与设计规范整合为一套可复用、可跨团队协作维护的共享体系。它不仅仅是一个 UI 组件库，而是涵盖设计令牌（Design Token）、使用指南、无障碍规范、品牌语义和工程代码实现的完整生态。一个成熟的设计系统至少包含三个层次：原子级别的令牌定义（如颜色、间距、字体比例）、分子级别的组件规范，以及页面级别的布局模式与交互规则。

设计系统的概念在 2010 年代中期随大规模 Web 产品复杂度的急剧增长而正式成形。2014 年 Google 发布 Material Design，其核心思想"纸张与墨水"隐喻为界面提供了物理一致性；2016 年 IBM 推出 Carbon Design System，系统化地将企业级产品的访问性与数据密度问题纳入规范体系；2019 年 Shopify 开源 Polaris，将设计令牌与商家体验价值观（如"减少认知负担"）直接挂钩。这三个里程碑将"设计系统"从内部工具转变为行业标准基础设施。

据 Sparkbox 2021 年设计系统调查报告，采用设计系统的团队报告 UI 开发速度平均提升 34%，跨团队视觉一致性问题下降超过 50%（Sparkbox, 2021）。Nathan Curtis 在其著作《Modular Web Design》（2009）中最早系统阐述了模式库与组件复用的经济学逻辑，被视为设计系统领域的奠基性文献之一。

---

## 核心原理

### 设计令牌：系统的原子单位

设计令牌（Design Token）是将设计决策以命名变量的形式存储的机制，是连接 Figma 等设计工具与前端代码实现的关键桥梁。Salesforce 工程师 Jina Anne 与 Jon Levine 于 2014 年在 Lightning Design System 项目中首次公开提出并系统化这一概念（Anne & Levine, 2014）。

令牌通常分为三层：

- **全局令牌（Global Token）**：存储原始值，例如 `color.blue.500 = #0057FF`、`space.4 = 16px`。
- **别名令牌（Alias Token）**：赋予语义上下文，例如 `color.action.default` 引用 `color.blue.500`，`color.danger.default` 引用 `color.red.600`。
- **组件令牌（Component Token）**：与具体组件绑定，例如 `button.background.primary` 引用 `color.action.default`。

这种三层架构的核心优势在于：主题切换（Theme Switching）时只需修改别名层的引用关系，无需逐一改动全局值或组件实现。Style Dictionary（Amazon 开源工具）和 Figma Variables 均基于此三层模型运作，能够将同一份令牌文件编译为 CSS Custom Properties、iOS Swift 常量、Android XML 资源等多个平台的输出格式。

令牌的命名规范本身也是一门学问。W3C 设计令牌社区组（Design Tokens Community Group）正在制定的 DTCG 规范草案建议采用 `{category}.{property}.{variant}.{state}` 的层级命名模式，以保证令牌在工具链之间的互操作性。

### 8pt 网格系统与间距公式

大多数成熟设计系统采用 **8pt 网格系统**作为间距的基础公式。其数学逻辑如下：

$$
S_n = 8 \times n \quad (n = 0.5, 1, 1.5, 2, 3, 4, 6, 8, \ldots)
$$

即间距序列为 4px、8px、12px、16px、24px、32px、48px、64px……。这一序列之所以选择 8 作为基数，原因在于主流屏幕分辨率（1x、1.5x、2x、3x）均能整除 8，从而避免像素级渲染时的次像素模糊（Sub-pixel Rendering）问题（Marcotte, 2010）。

Google Material Design 3 在此基础上引入了**响应式间距令牌**，通过 `compact`、`medium`、`expanded` 三个断点分别映射不同的间距乘数，使同一组件在手机（360dp）与桌面（1440px）下呈现不同的视觉密度，但底层 8pt 基数不变。

### 组件状态机模型

设计系统中的每个交互组件本质上是一个有限状态机（Finite State Machine, FSM）。以按钮（Button）为例，其状态集合为：

$$
Q = \{Default,\ Hover,\ Focused,\ Active,\ Loading,\ Disabled,\ Error\}
$$

组件规范文档必须为 $|Q|$ 中的每个状态定义明确的视觉表现差异。以 Primary Button 的背景色为例：

| 状态 | 令牌引用 | 典型值 |
|------|----------|--------|
| Default | `button.bg.primary.default` | #0057FF |
| Hover | `button.bg.primary.hover` | #0047D4 |
| Active | `button.bg.primary.active` | #0038AA |
| Disabled | `button.bg.primary.disabled` | #99BBFF（opacity 0.5）|

如果规范文档缺失任何一个状态的定义，工程师将不得不自行决策，这是导致不同页面"同一按钮视觉不一致"的最常见根因。

---

## 关键方法与工具链

### 原子设计方法论

Brad Frost 于 2013 年在其博客文章《Atomic Web Design》中提出原子设计（Atomic Design）方法论（Frost, 2013），将 UI 分解为五个层级：

1. **原子（Atoms）**：HTML 最基本元素，如输入框、标签、图标。
2. **分子（Molecules）**：由原子组合形成的简单功能单元，如"搜索框 = 输入框 + 按钮"。
3. **有机体（Organisms）**：由分子与原子组合的复杂界面区域，如导航栏、表单区块。
4. **模板（Templates）**：有机体在页面骨架中的布局排列，强调内容结构而非真实内容。
5. **页面（Pages）**：模板与真实内容的组合，用于测试设计决策的真实效果。

原子设计方法论与设计令牌三层架构形成天然对应：全局令牌对应原子，别名令牌对应分子/有机体的语义，组件令牌对应有机体和模板的具体实现。这种双轨并行的结构使大型系统在扩展时不会陷入"样式爆炸"（Style Explosion）的困境。

### 无障碍对比度计算

WCAG 2.1（Web Content Accessibility Guidelines）AA 级标准要求：正文文字的**相对亮度对比度**（Contrast Ratio）不得低于 4.5:1，大文字（18pt 或 14pt 粗体以上）不得低于 3:1（W3C, 2018）。

对比度计算公式为：

$$
CR = \frac{L_1 + 0.05}{L_2 + 0.05}
$$

其中 $L_1$ 为较亮颜色的相对亮度，$L_2$ 为较暗颜色的相对亮度。相对亮度 $L$ 的计算基于 sRGB 色彩空间的线性化：

$$
L = 0.2126 \cdot R_{lin} + 0.7152 \cdot G_{lin} + 0.0722 \cdot B_{lin}
$$

在设计系统中，所有语义色令牌（如 `color.text.primary`、`color.background.surface`）在定义时就应预先通过上述公式验证其配对对比度，而非等到组件开发完成后再做无障碍检查。Figma 插件 Contrast 和命令行工具 `color-contrast-checker` 均可批量验证令牌配对，适合集成到 CI/CD 流水线。

### 设计系统的治理模型

设计系统的治理（Governance）决定了系统的长期健康度。Nathan Curtis 与 Jina Anne 将治理模型分为三类（Curtis, 2020）：

- **集中式（Centralized）**：由专职设计系统团队统一维护，适合大型组织（如 Atlassian Design System 有超过 20 名专职成员）。贡献渠道单一，质量高，但响应速度慢。
- **联邦式（Federated）**：各产品线派代表参与核心系统决策，兼顾一致性与灵活性，是 Spotify、Airbnb 等中大型公司的主流选择。
- **分布式（Distributed）**：无专职团队，任何人均可提交组件，依赖社区质量审核。适合开源项目，但一致性难以保证。

---

## 实际应用

### 案例：Shopify Polaris 的令牌迁移

2022 年，Shopify 对 Polaris 进行了 v10 大版本升级，将原有的 Sass 变量体系完整迁移至 CSS Custom Properties 令牌体系，共涉及 **350+ 颜色令牌**的重命名与语义重新定义。其迁移策略分三个阶段：第一阶段建立新旧令牌的映射表（Alias Bridge）使旧代码仍能运行；第二阶段通过自动化 codemod 脚本批量替换代码库中的 200,000+ 处令牌引用；第三阶段弃用旧令牌并在三个月内强制完成清理。这一迁移案例被 Polaris 团队发布在官方工程博客中，成为大型设计系统版本升级的教科书级参考。

### 案例：微软 Fluent Design System 的跨平台令牌

微软 Fluent Design System 面临的挑战是需要将同一套视觉语言跨越 Web（React）、Windows（WinUI 3）、iOS（Swift UI）、Android（Jetpack Compose）四个平台统一落地。其解决方案是在令牌层引入**平台映射层（Platform Mapping Layer）**，即在别名令牌与组件令牌之间增加一层"平台适配令牌"，允许同一语义在不同平台上输出不同的技术格式（CSS 变量、Swift 颜色资产、Android Color Resource），而品牌一致性由最上层的别名令牌统一保证。

例如：表单组件在 Web 上的圆角为 `4px`，而在 iOS 上映射为 `8px` 以匹配平台视觉惯例，但两者均引用同一个语义令牌 `shape.corner.control`，品牌层面的一致性通过令牌命名而非令牌数值来维护。

---

## 常见误区

**误区一：设计系统等于组件库**。许多团队将设计系统的建设范围等同于"把 Figma 组件做齐"，忽略了令牌层和规范文档层。结果是设计稿中的组件与工程代码中的组件各自演化，半年后产生严重的设计债（Design Debt）。完整的设计系统必须包含设计工具侧、代码侧和文档侧三端的同步更新机制。

**误区二：一次性建成，长期不维护**。设计系统是一个持续演进的产品，而非一次性交付物。Spotify 曾在 2018 年因设计系统维护资源不足导致 Encore 系统内出现 3 套并行的按钮变体共存，最终不得不启动专项清理项目耗费数个季度才完成收敛。设计系统需要明确的版本语义（Semantic Versioning）和弃用政策（Deprecation Policy）。

**误区三：令牌命名过于具体**。将令牌命名为 `color.blue.button` 而非 `color.action.primary` 是典型的语义欠缺错误——一旦主题色从蓝色改为绿色，所有引用该令牌的地方命名便立刻产生语义歧义，增加认知成本。令牌命名应该描述**用途**而非**外观**。

**误区四：忽视黑暗模式的令牌双轨设计**。部分团队在建设之初仅定义亮色模式的令牌，待需要支持暗黑模式时才发现需要全量重构别名令牌层。正确做法是在系统设计初期就将 `color.background.surface` 同时定义 `light` 与 `dark` 两套值，通过 CSS `prefers-color-scheme` 或 `data-theme` 属性在运行时切换，令组件代码无需感知主题状态。

---

## 知识关联

设计系统与以下知识领域存在深度交叉：

- **视觉层级与排版比例**