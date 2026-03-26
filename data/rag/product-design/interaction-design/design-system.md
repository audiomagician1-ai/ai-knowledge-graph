---
id: "design-system"
concept: "设计系统"
domain: "product-design"
subdomain: "interaction-design"
subdomain_name: "交互设计"
difficulty: 4
is_milestone: false
tags: ["系统"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 33.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.314
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 设计系统

## 概述

设计系统（Design System）是一套统一的设计语言与实现规范的集合，包含可复用的组件库、设计令牌（Design Tokens）、交互准则和文档体系。它不仅仅是一个组件库，而是连接设计师与工程师协作的"单一可信来源"（Single Source of Truth）。2013年前后，随着前端开发规模化以及多平台产品的涌现，Google的Material Design（2014年发布1.0版）和Salesforce的Lightning Design System（2015年）成为行业内最早系统化的设计系统实践案例，推动了这一概念的普及。

设计系统的价值在于消除产品团队中反复出现的"设计漂移"问题——即不同团队在开发同一产品时各自造轮子，导致按钮样式出现7种以上变体的混乱现象。通过为按钮、颜色、字体、间距等元素建立唯一规范，一个成熟的设计系统可将UI开发速度提升30%–60%（Figma 2022年用户调研数据），同时保证跨平台视觉一致性。

## 核心原理

### 设计令牌（Design Tokens）

设计令牌是设计系统的原子单位，将颜色、字号、间距等视觉决策抽象为与平台无关的命名变量。例如，`color.primary.500 = #0050FF` 是一个语义化令牌，它在iOS端转译为Swift的`UIColor`、在Web端转译为CSS变量`--color-primary-500: #0050FF`、在Android端转译为`@color/primary_500`。

令牌分三层结构：**全局令牌**（Global Tokens，如`blue.500 = #0050FF`）、**别名令牌**（Alias Tokens，如`color.interactive = {blue.500}`）和**组件令牌**（Component Tokens，如`button.background.default = {color.interactive}`）。Style Dictionary是由Amazon开源的令牌转译工具，可将一份JSON格式的令牌文件自动输出为CSS、iOS、Android等多平台格式。

### 组件库的原子设计方法论

Brad Frost于2013年提出的原子设计（Atomic Design）是组件库构建的核心方法论，将UI元素分为5个层级：**原子**（Atom，如单个按钮、输入框）、**分子**（Molecule，如搜索框=输入框+按钮）、**有机体**（Organism，如导航栏）、**模板**（Template，布局骨架）和**页面**（Page，真实内容填充的模板实例）。这一分层思想直接影响了Ant Design等主流设计系统的组件目录结构。

在React技术栈中，组件变体通常通过Props枚举实现，例如`<Button variant="primary" size="md" state="disabled" />`，其中`variant`、`size`、`state`三个维度的组合决定了组件的所有状态矩阵。一个标准按钮组件至少需要覆盖 4种尺寸 × 5种语义变体 × 4种交互状态 = 80种状态场景。

### 设计规范文档（Design Spec）与可访问性

设计系统的规范文档必须包含WCAG 2.1的可访问性要求，具体体现为：文本与背景色对比度不低于4.5:1（AA级标准），焦点状态（Focus State）必须有不小于3px的可见轮廓，触控热区（Touch Target）最小尺寸为44×44px（符合Apple HIG规范）。

Figma中的"变体组件"（Component Variants）功能是维护设计规范的主要工具，允许设计师将同一组件的所有状态置于一个组件集合中，通过属性面板切换状态，而无需手动管理数十个独立组件帧。

## 实际应用

**企业级设计系统案例——Ant Design**：阿里巴巴在2016年发布Ant Design 1.0，定义了"自然、确定性、意义感、生长性"四大设计价值观，以及`8px`为基础单位的空间栅格系统。其颜色系统包含12个基础色相，每个色相生成10级色阶，共120个颜色令牌。在React实现中，Ant Design v5引入CSS-in-JS方案，通过`ConfigProvider`组件将设计令牌注入到整个应用树，支持在运行时动态切换主题。

**多品牌主题化场景**：当一家公司同时维护主品牌App和白标（White-label）产品时，设计系统的多主题能力至关重要。实现方式是将品牌层令牌（Brand Tokens）与语义层令牌分离，不同品牌只需替换品牌层的40–60个核心令牌即可完成整个产品视觉风格的切换，而无需修改任何组件代码。

## 常见误区

**误区一：设计系统等于组件库**。许多团队将"建设设计系统"等同于"在Storybook中搭建组件库"。实际上组件库只是设计系统的工程实现层，完整的设计系统还必须包含：设计令牌定义、Figma设计组件与代码组件的同步机制、贡献规范（Contribution Guidelines）、变更日志（Changelog）以及消费团队的使用文档。缺乏文档和治理流程的组件库会在6–12个月内出现"设计债务"积累。

**误区二：设计令牌只是CSS变量的别称**。CSS变量是设计令牌在Web平台的一种输出格式，而非设计令牌本身。设计令牌存储在平台无关的JSON或YAML格式中，可以通过Style Dictionary、Theo等工具转译为任意平台的格式。如果直接在CSS中维护变量而跳过平台无关的令牌层，则一旦需要支持React Native或iOS原生平台，就需要重新手动同步所有变量。

**误区三：设计系统建成后无需维护**。Shopify的Polaris、IBM的Carbon Design System每年均发布多个Major版本，持续对令牌命名约定、组件API和可访问性标准进行迭代。设计系统需要专职的"设计系统团队"（通常为2–5人）持续运营，包括处理消费团队的Issue、审查组件贡献请求和发布版本升级迁移指南。

## 知识关联

**与前置知识的关系**：React基础知识决定了组件库的Props设计方式和组件状态管理模式；CSS-in-JS（如Emotion、Styled-components）或TailwindCSS的掌握程度直接影响设计令牌在工程侧的实现路径——CSS-in-JS支持运行时主题切换，TailwindCSS则通过`tailwind.config.js`的`extend`字段将设计令牌映射为工具类。Material Design作为一个成熟的设计系统案例，为理解设计系统的层级结构和文档标准提供了直接参照。

**与后续概念的衔接**：组件库建设（Component Library）是在设计系统框架下细化单一组件的开发标准，涵盖组件的Props API设计、测试覆盖和Storybook文档规范；设计令牌（Design Tokens）专题会深入探讨W3C Design Tokens Community Group正在制定的令牌格式标准规范（`.dtcg`格式）；品牌设计则从设计系统的视觉层出发，探讨如何在设计令牌的约束下构建差异化的品牌个性。