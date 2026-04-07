---
id: "mn-ch-platform-store"
concept: "平台商店适配"
domain: "multiplayer-network"
subdomain: "cdn-hotpatch"
subdomain_name: "CDN与热更新"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 平台商店适配

## 概述

平台商店适配（Platform Store Adaptation）是指游戏开发团队针对Steam、PlayStation Store、App Store等不同分发平台的审核规则、技术标准和更新发布流程，对游戏包体和热更新策略进行差异化配置的工程实践。不同平台对"什么内容必须走商店审核"有截然不同的规定，这直接决定了热更新架构的设计边界。

这一概念随着移动游戏兴起而变得复杂。苹果公司在2010年推出App Store时通过开发者协议第3.3.2条明确限制：不得通过下载代码改变应用的主要功能。2017年前后，腾讯、网易等大型手游公司在中国市场大规模使用Lua热更新绕过App Store审核，导致苹果在2017年9月集中下架了数千款违规应用，这次事件成为业界对平台商店适配规范化的分水岭。

平台商店适配的核心意义在于：一旦违规，轻则被下架，重则开发者账号永久封禁，所有已发布游戏全部失效。因此热更新系统的设计必须从立项阶段就以各平台白名单规则为边界条件，而不是上线后再补救。

## 核心原理

### 各平台的热更新权限边界

**Apple App Store**：苹果审核指南第2.5.2条明确规定，iOS应用不得下载可执行代码，但允许通过JavaScript或WebAssembly在沙盒环境内运行的脚本更新，以及Unity等引擎的资产包（AssetBundle）更新。因此iOS合规热更新的典型做法是：代码逻辑锁在App Store版本中，通过CDN分发只包含美术资源、配置表、音频文件的资产包。Lua脚本更新若不被引擎原生支持则属于违规。

**Google Play**：相对宽松，允许在一定条件下下载代码，但要求所有通过Google Play分发的应用的核心功能不得依赖应用商店外部的不可审查代码。2021年Google Play更新政策，明确允许Unity IL2CPP方案下的AssetBundle，但禁止在运行时动态加载原生so库。

**Steam**：对热更新没有代码层面的强制限制，开发者可以通过Steamworks SDK中的`ISteamApps::GetDlcDownloadProgress()`接口管理DLC下载，也可以完全绕过Steam自行部署CDN做资源更新。Steam唯一要求的是：通过其平台销售的游戏必须使用Steam的反作弊和成就系统接口，不允许静默替换核心游戏逻辑以规避VAC（Valve Anti-Cheat）检测。

**PlayStation Store**：索尼要求所有补丁（Patch）必须通过SIE（Sony Interactive Entertainment）的认证流程，认证周期通常为5至10个工作日。PS平台没有类似iOS的热更新沙盒机制，所有游戏逻辑更新必须打成完整Patch包提交认证，这意味着PS游戏几乎无法做到移动端那种每周更新的运营节奏。

### 版本号管理与平台同步策略

不同平台的版本号体系不互通，需要独立维护。iOS使用`CFBundleShortVersionString`（面向用户的版本号，格式为`主.次.修订`）和`CFBundleVersion`（构建号，单调递增整数）两套编号。App Store要求每次提交审核的构建号必须严格大于上一次，否则拒绝上传。

Steam使用Depot和Manifest体系管理版本，每个Depot对应一组文件，Manifest ID是该批文件的SHA-1哈希。热更新资源若托管在Steam CDN以外，必须在游戏客户端内维护一套独立的资源版本表（通常是JSON或protobuf格式的manifest文件），记录每个资源包的版本号、MD5和下载地址，与Steam的Manifest体系并行运作。

多平台同步发布时，常见做法是维护一个"平台发布日历"：PC端和Android端可同步推送热更新资源，iOS端若涉及新功能必须等App Store审核通过（通常7天左右）后才能开放对应内容开关，PS端则需要提前15天提交Patch。这种错峰机制通过服务器端的**功能开关（Feature Flag）**实现，同一个版本的客户端通过拉取不同平台的配置来决定是否展示新功能。

### 包体大小限制与分包策略

App Store对OTA（Over-The-Air，即非Wi-Fi）下载有200MB的限制（2019年前为150MB），超出部分必须分拆为On-Demand Resources（ODR）从苹果服务器按需下载，或在游戏启动后通过应用内CDN下载资源包。Google Play则通过Play Asset Delivery（PAD）机制支持将游戏资产分为Install-time、Fast-follow、On-demand三类交付模式，其中Fast-follow在安装后立即后台下载，On-demand在游戏内按需请求。

Steam对包体没有硬性上限，但Valve建议单个Depot不超过50GB以保障CDN分发效率。

## 实际应用

《原神》是多平台商店适配的典型案例。其iOS版本所有游戏逻辑均编译进可执行文件，通过CDN分发的热更新包仅包含场景资产（`.blk`格式的资源块）和配置数据，严格遵守App Store规定。PC（Steam/Epic）和Android端则额外支持通过CDN推送部分脚本逻辑配置。不同平台的大版本更新（如2.0、3.0）均需协调PS4认证时间，米哈游通常提前3周向SIE提交Patch申请，以确保各平台版本在同一天上线。

Unity游戏的典型适配流程是：使用Addressables系统管理资产，为iOS平台单独配置一套Profile，将Remote Load Path指向苹果ODR接口或游戏自己的CDN，并在构建Pipeline中通过`#if UNITY_IOS`预编译宏剔除在iOS上违规的Lua脚本加载逻辑，确保提交App Store的IPA包不包含任何动态代码执行路径。

## 常见误区

**误区一：认为Android和iOS可以用同一套热更新方案**。Google Play虽然相对宽松，但国内Android渠道（华为、小米、OPPO等应用商店）各自有独立的审核规定，部分渠道要求与Google Play一样严格，不能以为绕过iOS限制就等于兼容所有Android渠道。

**误区二：认为Steam上的游戏可以无限制地热更新逻辑代码而不产生合规风险**。Steam虽然不限制代码更新，但若游戏接入了EasyAntiCheat或BattlEye等第三方反作弊系统，这些系统对运行时代码完整性有校验要求，动态替换游戏逻辑模块会触发误报甚至封号机制，与反作弊合规是独立的约束维度。

**误区三：认为通过功能开关延迟发布新功能就能规避App Store审核**。苹果在2022年更新的审核指南中明确指出，若应用在审核期间隐藏功能、上线后激活，属于欺骗性行为，一旦被举报可导致下架和开发者资质撤销。功能开关只能用于**审核通过的功能**的灰度发布，不能用于提交未包含该功能的版本。

## 知识关联

平台商店适配以**版本管理**为前提：只有建立了清晰的版本树和分支策略，才能在同一代码库中维护iOS、Android、PC、主机四条并行的发布分支，并正确追踪哪些热更新资源已经通过各平台审核、哪些尚在等待。版本号的单调递增规则、Changelog的平台差异化记录，都是版本管理在平台适配场景下的具体落地要求。

在CDN与热更新的整体架构中，平台商店适配决定了CDN所分发内容的合规边界——CDN的技术能力决定了"能做什么"，而平台规则决定了"允许做什么"，两者的交集才是真正可落地的热更新方案。游戏服务器端的功能开关系统、资源版本表的格式设计、客户端的分包加载逻辑，最终都需要以各平台商店的审核条款为约束条件进行定制化开发。