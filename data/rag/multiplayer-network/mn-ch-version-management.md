---
id: "mn-ch-version-management"
concept: "版本管理"
domain: "multiplayer-network"
subdomain: "cdn-hotpatch"
subdomain_name: "CDN与热更新"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.469
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 版本管理

## 概述

版本管理（Version Management）是网络多人游戏热更新体系中的基础机制，专指对客户端程序、资源包、服务端逻辑分别维护独立的版本号，并在每次连接或下载时执行兼容性校验，以确保不同版本的客户端能与服务端正确通信。

版本号的形式化管理最早在桌面软件领域成型，语义化版本规范（Semantic Versioning，SemVer）于2010年由Tom Preston-Werner提出，定义了`MAJOR.MINOR.PATCH`三段式编号规则：MAJOR变化表示不兼容的API改动，MINOR表示向下兼容的功能新增，PATCH表示向下兼容的缺陷修复。手机网游将这一规范引入客户端/服务端通信后，又额外引入了**资源版本号**与**协议版本号**两个独立维度，使游戏版本体系扩展为四个相对独立的轨道并行演进。

版本管理直接决定热更新的可行范围。若客户端版本号低于服务端所能接受的最低兼容版本，服务端必须拒绝连接或强制引导更新；反之若服务端先于客户端升级，则需要为旧版本客户端保留旧协议的兼容窗口期，这个窗口通常以"最小支持版本"（MinSupportedVersion）字段明确记录在服务端配置中。

---

## 核心原理

### 版本号的四维结构

在多人游戏实践中，版本信息通常拆分为以下四个独立字段：

| 维度 | 典型字段名 | 变更触发条件 |
|------|-----------|-------------|
| 客户端包版本 | `client_version` | 安装包重新打包上传应用商店 |
| 资源版本 | `res_version` | CDN上的图片、音频、配置表热更新 |
| 协议版本 | `proto_version` | 客户端与服务端之间的消息格式改变 |
| 数据版本 | `data_version` | 游戏内配置数据（关卡、道具属性）变更 |

这四个维度的版本号各自独立自增，互不影响。一次只更新了某张贴图的CDN热更新仅推进`res_version`，而不需要改动`client_version`或`proto_version`。

### 版本比较算法

客户端启动后向服务端发送**版本握手请求**，携带自身四维版本信息。服务端执行如下比较逻辑：

```
if client.proto_version < server.min_proto_version:
    返回 ERROR_FORCE_UPDATE，断开连接
elif client.res_version < server.current_res_version:
    返回 RES_UPDATE_REQUIRED，携带差量更新清单
elif client.data_version < server.current_data_version:
    返回 DATA_UPDATE_REQUIRED，下发新配置表
else:
    返回 OK，允许进入游戏
```

协议版本的检查必须先于资源版本，因为协议不兼容时，后续所有通信消息均无法正确解析，继续握手毫无意义。

### 版本号的存储与下发

服务端通常维护一张**版本配置表**（version_config），存储在Redis或数据库中，字段至少包含：`current_version`、`min_supported_version`、`force_update_below`、`update_url`、`patch_md5`。客户端第一次启动或每次冷启动时，必须访问一个固定的**版本查询接口**（通常以HTTP GET形式暴露），该接口的域名往往独立于游戏主逻辑服务器，确保即使游戏逻辑服务器故障，版本检查与更新流程仍然可用。版本配置表的更新由运维人员通过后台管理系统操作，并非由代码部署自动触发，这一设计使运营团队可以精确控制每个版本的上线时刻。

### 多渠道版本隔离

安卓发行渠道（如华为应用市场、小米应用商店、谷歌Play）对安装包的审核进度不同，导致同一个游戏在不同渠道同时存在`1.4.2`和`1.4.3`两个包版本。版本管理系统必须在`client_version`之外增加`channel_id`字段，使服务端能为不同渠道设置独立的`min_supported_version`，避免已通过审核渠道的玩家因其他渠道尚未更新而被误判为需要强制更新。

---

## 实际应用

**《王者荣耀》热更新版本链**：该游戏将资源版本号设计为带日期前缀的字符串，例如`20231105_001`，方便运营人员直接从版本号判断更新发布日期，同时服务端保留过去14天内所有`res_version`的完整下载链接，使14天内未启动游戏的玩家仍能完成增量更新而无需重新下载完整包。

**灰度发布中的版本管理**：当一个新版本需要先向5%的用户开放时，服务端在版本配置表中增加`gray_ratio`字段，版本查询接口根据用户UID的哈希值决定是否向该用户下发新版本号。此机制完全依赖版本管理层，与游戏业务逻辑解耦。

**本地版本缓存**：客户端将上次成功校验的`res_version`和`data_version`写入本地持久化存储（如PlayerPrefs或本地JSON文件），下次启动时用本地缓存版本与服务端比对，仅当版本号不一致时才发起下载请求，避免每次冷启动都重新拉取完整资源清单（manifest文件体积可达数百KB）。

---

## 常见误区

**误区一：用客户端包版本号代替资源版本号**
部分初学者认为只要客户端版本号相同，资源就一定相同，因此不单独维护`res_version`。这种做法导致热更新后无法区分"已下载新资源"和"未下载新资源"的客户端，服务端无法确认玩家是否看到了最新的活动内容或已修复的UI，且无法对已更新与未更新的客户端实施差异化逻辑处理。

**误区二：所有版本号统一使用单一整数自增**
若四个维度共用同一个计数器，一次仅改动贴图的热更新会导致`proto_version`也自增，服务端误判为协议变更，触发不必要的强制更新流程，造成玩家流失。版本号的各维度必须**独立自增**，每个维度只对其对应的变更敏感。

**误区三：`min_supported_version`只需在发布新版本时更新一次**
实际上当服务端发现某个旧版本存在严重安全漏洞或作弊行为时，运营团队需要在不发布新包的情况下**紧急提升`min_supported_version`**，迫使使用问题版本的玩家立即更新。这要求版本配置表的修改能实时生效（通常配合Redis缓存的短TTL实现），而非依赖服务器重启。

---

## 知识关联

版本管理是**强制更新策略**的直接前提：只有当`client_version < force_update_below`条件在版本管理层被准确判断后，强制更新的跳转逻辑才有触发依据。没有清晰的版本号体系，强制更新策略将无从判断"何时必须更新"。

**补丁系统**以版本管理提供的`res_version`差值作为输入，计算`v1.0`到`v1.2`之间需要下载的差量文件列表；若版本管理层没有准确记录每个版本的文件清单哈希，补丁系统将无法生成正确的差量包。

**版本回滚**操作的本质是将服务端版本配置表中的`current_version`和`min_supported_version`字段同时回写到上一个稳定版本的值，使新版本客户端在版本检查时收到"需要降级"的特殊响应码（如`ERROR_VERSION_TOO_HIGH`），这是版本管理机制的逆向使用。

**平台商店适配**需要将各渠道的包版本号（如Google Play的`versionCode`整数字段、苹果App Store的`CFBundleShortVersionString`字符串字段）与游戏内部的`client_version`建立映射关系，确保商店显示版本与服务端兼容性检查使用的版本号语义一致。