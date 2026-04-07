---
id: "anti-cheat-plugin"
concept: "反作弊插件"
domain: "game-engine"
subdomain: "plugin-development"
subdomain_name: "插件开发"
difficulty: 3
is_milestone: false
tags: ["安全"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 反作弊插件

## 概述

反作弊插件是游戏引擎插件体系中专门用于检测和阻止玩家非法修改游戏内存、注入外挂程序或篡改网络数据包的安全组件。与普通功能插件不同，反作弊插件需要在操作系统内核层和用户层双重工作，因此其集成复杂度远高于音频或渲染类插件。目前市场占有率最高的两款商业反作弊解决方案是 **Easy Anti-Cheat（EAC）** 和 **BattlEye（BE）**，前者由 Epic Games 于 2018 年收购后向使用 Unreal Engine 的开发者免费开放，后者则被《绝地求生》《彩虹六号》等头部游戏采用，合计保护超过 500 款游戏。

反作弊插件之所以值得单独作为一类插件研究，原因在于它的工作机制与普通插件完全相反：大多数插件通过暴露 API 来增强游戏功能，而反作弊插件必须对自身实现细节严格保密，防止外挂开发者通过逆向工程绕过检测。这一"安全与透明度"的矛盾要求开发者在集成时必须遵循供应商提供的封闭式 SDK 流程。

## 核心原理

### EAC 集成流程与 SDK 结构

EAC 的 SDK 以动态库（`EasyAntiCheat_EOS.dll` 在 Windows 平台，`libEasyAntiCheat_EOS.so` 在 Linux）形式分发，开发者不能直接调用其内部函数，而是通过一个称为 **EOS（Epic Online Services）句柄** 的不透明指针与其交互。集成的第一步是在游戏启动器中调用 `EAC_Launcher` 可执行文件，该启动器负责在游戏进程启动前注入反作弊驱动；游戏客户端本身通过调用 `EOS_AntiCheatClient_AddNotifyMessageToServer` 回调函数，将客户端生成的完整性报告定期上报给游戏服务器。

服务器端需要集成 `EOS_AntiCheatServer` 模块，通过 `EOS_AntiCheatServer_BeginSession` 初始化会话，并监听 `EOS_AntiCheatServer_AddNotifyClientActionRequired` 回调——当 EAC 认定某个客户端存在作弊行为时，服务器插件会在此回调中收到包含玩家句柄和处罚建议的结构体，由服务器逻辑决定是踢出还是封禁。

### BattlEye 集成与 RCON 配置

BattlEye 的集成方式与 EAC 存在显著差异：BE 通过 **BEService** 系统服务安装内核级驱动，并要求游戏可执行文件在构建阶段向 BE 官方服务器提交数字签名白名单申请，未注册的游戏进程无法激活 BE 保护。插件开发者需要修改游戏引擎的启动参数，在 `GameServer.ini` 中添加 `BattlEye=1` 字段，并将 `BEServer.dll` 放置在固定的 `BattlEye/` 子目录下。

BE 还支持通过 **RCON（Remote Console）协议** 进行运行时管理，默认端口为 `2302`（可配置）。反作弊插件开发者可以在此基础上构建管理工具，通过发送格式为 `#ban [PlayerID] [Duration] [Reason]` 的命令字符串实现自动化封禁流水线。BE 的封禁列表存储在 `bans.txt` 文本文件中，每行格式为 `IP/GUID minutes reason`，插件需要定期同步此文件以保持封禁数据一致性。

### 内存完整性校验机制

两款反作弊系统都使用**周期性内存签名扫描**来检测代码注入，但实现思路不同。EAC 侧重于检测已知外挂进程的特征哈希（维护一个持续更新的黑名单数据库），而 BattlEye 更依赖**行为分析**，通过监控游戏进程的系统调用序列来识别异常模式，例如 `VirtualAllocEx` + `WriteProcessMemory` + `CreateRemoteThread` 三连调用序列高度关联于 DLL 注入行为。

插件开发者在自定义扩展时必须避免使用上述系统调用组合，否则自身插件可能被反作弊系统误判为外挂。解决方案是在插件初始化时通过 EAC/BE 提供的白名单注册接口（EAC 对应 `EOS_AntiCheatClient_AddExternalIntegrity`）注册插件模块的数字签名，使反作弊驱动在扫描时跳过已认证的模块。

## 实际应用

**Unreal Engine 项目集成 EAC** 的典型步骤：在 `.uproject` 文件的 `Plugins` 数组中添加 `{"Name": "OnlineSubsystemEOS", "Enabled": true}`，然后在 `DefaultEngine.ini` 中配置 `[OnlineSubsystemEOS] bUseEAS=true`。构建时 UE 的 Plugin Manager 会自动将 EAC 启动器可执行文件复制到 `Binaries/Win64/` 目录。

**Unity 项目使用 EAC** 则需要手动调用 `EAC_Loader` 的 C# P/Invoke 封装，因为 Unity 没有原生 EOS 插件，开发者通常通过 `[DllImport("EasyAntiCheat_EOS")]` 导入 `EAC_Initialize()` 和 `EAC_Shutdown()` 函数，并在 `Application.quitting` 事件中确保正确卸载，否则会导致 BE/EAC 驱动服务残留在系统中影响下次启动。

**服务器端自动封禁插件**是最常见的二次开发场景：开发者编写一个轮询 BattlEye RCON 接口的后台插件，当检测到 BE 上报的可疑评分（Score）超过阈值（通常设为 `>= 85` 满分 `100`）时，自动执行 30 天临时封禁并写入日志，供运营人员复审。

## 常见误区

**误区一：认为集成反作弊插件后无需服务器端验证。** 许多开发者集成 EAC 或 BE 后放松了服务器逻辑，认为客户端已被保护。事实上，EAC/BE 主要防止**客户端本地作弊**（内存修改、速度外挂），但无法阻止**数据包伪造**攻击——攻击者可以完全绕过反作弊客户端，直接向服务器发送非法数据包。服务器端的数值合法性校验（如移速上限检测、伤害范围验证）仍然是必需的。

**误区二：在插件代码中直接使用反射或动态加载 EAC 模块。** 部分开发者为了实现热重载，尝试在运行时动态 `LoadLibrary` EAC 的 DLL，这会导致 EAC 的完整性校验失败，因为 EAC 要求其模块在进程启动阶段由专用启动器加载，而不是由游戏代码在运行时自行加载。正确做法是将 EAC 初始化逻辑置于引擎最早的启动钩子（如 UE 的 `PreInitPreStartupScreen`），而非任何可热重载的游戏模块中。

**误区三：混淆 EAC 免费版与完整版的功能差异。** Epic 面向 EOS 开发者提供的免费 EAC 版本不包含**服务器端反作弊分析**功能，即 `EOS_AntiCheatServer` 模块需要签订商业协议才能激活。免费版仅支持客户端完整性验证，如果开发者期望服务器主动踢出可疑玩家而未签署协议，该功能将静默失败而非报错，这一陷阱曾导致多个独立游戏上线后实际无服务器端保护能力。

## 知识关联

反作弊插件建立在**第三方库集成**的基础之上：EAC 和 BattlEye 的 SDK 均以预编译二进制库形式分发，开发者需要熟练掌握动态库链接、平台特定的构建脚本配置（CMake 或 UBT）以及 P/Invoke/FFI 跨语言调用约定，这些都是第三方库集成的核心技能。在此之上，反作弊插件还额外要求开发者理解操作系统进程隔离模型和代码签名机制，因为 BattlEye 的内核驱动在 Windows 11 环境下需要启用 **HVCI（Hypervisor-Protected Code Integrity）** 兼容模式，否则驱动加载会被操作系统拒绝，这是纯粹的第三方库集成知识无法覆盖的领域。