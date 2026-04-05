---
id: "unity-overview"
concept: "Unity引擎概述"
domain: "game-engine"
subdomain: "unity-architecture"
subdomain_name: "Unity架构"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Unity引擎概述

## 概述

Unity Technologies由丹麦人David Helgason、Nicholas Francis和Joachim Ante于2004年在哥本哈根创立，最初以"Over the Edge Entertainment"为名开发一款名为《GooBall》的Mac游戏。当这款游戏商业失败后，三位创始人转而将开发过程中构建的内部工具打磨成一套通用引擎，于2005年在苹果全球开发者大会（WWDC）上正式发布Unity 1.0，彼时仅支持Mac OS X平台。

Unity的核心架构哲学是**"以组合替代继承"（Composition over Inheritance）**。不同于虚幻引擎以C++类层级继承为主干的设计，Unity采用GameObject-Component模型：所有场景对象都是空的容器（GameObject），功能通过挂载不同组件（Component）来叠加实现。这一决策使得非程序员（如美术、设计师）也能通过拖拽组件在编辑器中快速原型开发，从而奠定了Unity在独立游戏和移动端市场的统治地位。

Unity的跨平台能力是其商业成功的最大驱动力之一。截至Unity 2023版本，Unity支持超过20个目标平台，包括iOS、Android、PC、主机（PlayStation、Xbox、Switch）、WebGL及各类XR设备。其"一次编写，多端发布"的Build Pipeline让中小型团队得以用单一代码库覆盖多平台，这是Unity在2010年代移动游戏爆发期迅速占领市场的关键技术优势。

---

## 核心原理

### 版本演进脉络

Unity版本体系从Unity 5.x（2015年）开始进行重大架构重组，将原本捆绑销售的专业功能（如Physically Based Rendering、实时全局光照）向免费版本开放，以此换取市场占有率。2017年Unity转向年度版本命名制（Unity 2017、2018…），同年引入**可脚本化渲染管线（Scriptable Render Pipeline，SRP）**框架，允许开发者替换内置的渲染循环，由此催生了HDRP与URP两套官方渲染管线。

Unity 2019.3引入**包管理器（Package Manager）**全面成熟，将引擎功能拆分为独立的UPM包（com.unity.xxx），开发者可按需安装特定版本的Cinemachine、Input System、VFX Graph等模块，而无需更新整个引擎。这一拆解策略使引擎核心与功能扩展解耦，是Unity从单体架构向模块化生态转型的分水岭。

Unity 2020年代引入的**长期支持版（LTS）策略**规定：每年发布版本中，奇数小版本为技术预览，偶数小版本（如2020 LTS、2021 LTS、2022 LTS）享有两年安全补丁支持。大型商业项目通常锁定LTS版本以规避API变动风险。

### 内存与对象生命周期模型

Unity使用Mono或IL2CPP作为C#运行时。Mono模式在编辑器内调试方便，IL2CPP则将C#编译为C++再编译为原生代码，在iOS（App Store强制要求）和主机平台上使用。Unity托管堆（Managed Heap）与原生引擎堆分离，GameObject和Component存活于原生堆，C#侧持有的是指向原生对象的**薄包装指针**，这解释了为何对已销毁的GameObject调用`.name`会抛出`MissingReferenceException`而非空指针异常——C#引用本身非null，但底层原生对象已释放。

### 编辑器与运行时一体化架构

Unity编辑器本身用Unity引擎构建，编辑器UI（IMGUI/UIToolkit）、场景视图、Game视图共享同一套渲染基础设施。这带来了`[ExecuteInEditMode]`（Unity 2019后推荐用`[ExecuteAlways]`）特性——MonoBehaviour脚本可在编辑模式下执行Update逻辑，使程序化建模工具和实时预览成为可能。编辑器与运行时代码通过**Assembly Definition（.asmdef）**文件隔离，避免编辑器专用代码（如`UnityEditor`命名空间）被打包进发行版。

---

## 实际应用

**移动端休闲游戏开发**是Unity最典型的应用场景。《王者荣耀》早期版本、《神庙逃跑》及大量超休闲游戏均基于Unity构建。Unity的Asset Store提供超过70,000个商业资产包，可将从零到可发布原型的周期压缩至数周。

**XR（扩展现实）领域**中，Unity占据约60%的AR/VR内容市场份额（2022年Unity官方数据）。Meta Quest平台的大多数独立VR游戏、工业可视化应用和医疗训练模拟均使用Unity，其与AR Foundation（封装ARCore/ARKit的统一API层）的深度集成是重要原因。

**非游戏应用**方面，Unity已渗透至汽车设计可视化（宝马、大众使用Unity工业版）、建筑实时漫游、电影预可视化（Unity Reflect工具集）。Unity 2021起正式支持**Unity as a Library**，允许将Unity运行时嵌入原生iOS/Android应用，而非以全屏应用形式独立运行。

---

## 常见误区

**误区一：Unity"只适合做小游戏"**。这一认知源于Unity 3.x时代渲染能力的局限。HDRP管线下，Unity 2022可实现光线追踪（DXR）、GPU Lightmapper和电影级材质效果。《奥里与萤火意志》（Ori and the Will of the Wisps）和《逃出生天》（Escape from Tarkov）均为Unity开发的高质量产品，后者拥有复杂的弹道物理和大型开放世界。

**误区二：Unity脚本"只能用C#"**。Unity 4.x及更早版本曾支持JavaScript（UnityScript）和Boo三种语言，但自Unity 2017起官方彻底废弃UnityScript支持，目前C#是唯一受支持的用户脚本语言。混淆这段历史的开发者有时会误以为找到的UnityScript教程仍然有效。

**误区三：更新Unity版本"向下兼容"是安全的**。Unity的序列化系统对`.unity`场景文件和Prefab使用文本或二进制YAML格式，跨大版本升级（如从2019升至2022）会强制重新序列化并可能触发API废弃警告，部分第三方插件的Editor扩展在新版本会直接报错。大型项目升级前必须在独立分支充分测试，而非直接提交主干。

---

## 知识关联

学习Unity引擎概述之前，需要了解**游戏引擎概述**中关于游戏循环（Game Loop）、场景图（Scene Graph）和渲染管线抽象等通用概念，因为Unity对这些概念均有具体的实现方式（如`Update()/FixedUpdate()/LateUpdate()`三段式循环结构）。

在此基础上，**GameObject-Component系统**是Unity架构哲学的直接落地，理解本文介绍的"组合替代继承"原则后，学习者能更快把握为何Transform、Renderer、Collider被设计为平行组件而非继承关系。**URP渲染管线**和**VFX Graph**均构建于SRP框架之上，本文介绍的2017年SRP引入背景是理解这两者为何存在的前提。**Addressables**资产管理系统依赖Package Manager架构，而**Cinemachine**则是Package Manager模块化生态的典型代表——这两个方向在本文的版本演进脉络中均有技术根源。