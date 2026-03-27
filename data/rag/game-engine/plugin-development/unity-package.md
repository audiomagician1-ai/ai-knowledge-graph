---
id: "unity-package"
concept: "Unity Package"
domain: "game-engine"
subdomain: "plugin-development"
subdomain_name: "插件开发"
difficulty: 2
is_milestone: false
tags: ["Unity"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Unity Package

## 概述

Unity Package 是 Unity 引擎官方包管理系统（Package Manager）所管理的标准化代码与资产分发单元，自 Unity 2018.1 版本起正式引入。每个 Package 以 `com.company.packagename` 格式的反向域名作为唯一标识符，并通过 `package.json` 清单文件描述其元数据、版本号及依赖关系。

Unity Package 的出现解决了传统 `.unitypackage` 格式的根本缺陷——旧格式将所有内容平铺导入到 `Assets` 目录，导致版本冲突和命名空间污染。新的 Package 系统将代码存储在项目之外的全局缓存目录（`~/.config/unity3d/cache` 或 Windows 下的 `%APPDATA%\Unity\cache`），实现了跨项目复用而不产生文件冗余。

Unity Package 还引入了 Assembly Definition（程序集定义，`.asmdef` 文件）机制，将 C# 源码编译为独立的 DLL 程序集，而非统一编译到 `Assembly-CSharp` 中。这一机制使增量编译时间从数十秒显著缩短，对大型项目尤为关键。

## 核心原理

### package.json 清单结构

每个 Package 的根目录必须包含 `package.json` 文件，其中最关键的字段包括：

- `name`：反向域名标识符，例如 `com.unity.render-pipelines.universal`
- `version`：遵循 [语义化版本规范（SemVer）](https://semver.org/)，格式为 `主版本.次版本.修订号`，例如 `14.0.8`
- `unity`：指定兼容的最低 Unity 编辑器版本，例如 `"2022.2"`
- `dependencies`：以对象形式列出所依赖的其他 Package 及其版本，Package Manager 会自动递归解析

```json
{
  "name": "com.mycompany.mytool",
  "version": "1.2.0",
  "unity": "2021.3",
  "dependencies": {
    "com.unity.mathematics": "1.2.6"
  }
}
```

### Assembly Definition 文件机制

`.asmdef` 文件以 JSON 格式定义一个 C# 程序集的编译规则。放置在某目录下的 `.asmdef` 文件会将该目录及其子目录内所有 `.cs` 文件编译进同一个独立程序集。核心字段包括：

- `name`：程序集名称，必须全局唯一，通常与 Package 名称对应
- `references`：显式列出该程序集依赖的其他程序集名称列表
- `includePlatforms` / `excludePlatforms`：控制平台特定编译，例如 `["Editor"]` 表示仅在编辑器环境下编译
- `autoReferenced`：设为 `false` 时，`Assembly-CSharp` 不会自动引用此程序集，强制使用显式引用

若一个 Package 同时提供运行时代码和编辑器扩展，标准做法是在 `Runtime` 子目录放置运行时 `.asmdef`，在 `Editor` 子目录放置编辑器 `.asmdef`，后者通过 `includePlatforms: ["Editor"]` 限制编译范围。

### Package 的来源与安装方式

Unity Package Manager 支持五种安装来源，各有不同的 `manifest.json` 写法：

1. **Unity Registry**：官方注册表，写法如 `"com.unity.cinemachine": "2.9.7"`
2. **Scoped Registry**：自定义 npm 兼容注册表，需在 `manifest.json` 的 `scopedRegistries` 字段声明服务器地址
3. **Git URL**：直接引用 Git 仓库，写法如 `"com.mycompany.tool": "https://github.com/user/repo.git#v1.0.0"`，`#` 后可指定 tag 或 commit hash
4. **本地路径**：以 `"file:../LocalPackage"` 格式引用本地文件夹，适合开发阶段调试
5. **内嵌 Package**：直接将 Package 文件夹放在项目的 `Packages/` 目录内，无需网络

## 实际应用

**开发可复用的编辑器工具**：假设团队需要在多个项目中共享一套关卡编辑工具，可将其打包为 `com.studio.leveleditor`。Runtime 程序集包含关卡数据结构，Editor 程序集包含自定义 Inspector 和窗口，通过 Git URL 在各项目的 `manifest.json` 中引用同一仓库的不同 tag，实现版本隔离。

**条件编译与平台适配**：在 `.asmdef` 中结合 `versionDefines` 字段，可根据某依赖 Package 是否安装、版本是否满足条件来动态定义预处理符号。例如，当检测到 `com.unity.inputsystem` 版本 `>=1.4.0` 时定义 `NEW_INPUT_SYSTEM`，从而在代码中用 `#if NEW_INPUT_SYSTEM` 切换实现，避免硬编码版本检查。

**打包与发布到 Scoped Registry**：使用 `npm pack` 命令可将 Package 目录打包为 `.tgz` 文件，配合私有 Verdaccio 服务器，团队成员只需在 `manifest.json` 中添加 `scopedRegistries` 条目即可通过 Package Manager UI 安装和更新工具，体验与 Unity 官方包完全一致。

## 常见误区

**误区一：认为 `.asmdef` 只影响编译速度，可以不加**。实际上，`.asmdef` 对 Package 是强制性要求——没有 `.asmdef` 的 Package 中的代码无法被 `Assembly-CSharp` 以外的其他程序集引用，因为跨程序集引用必须通过 `references` 字段显式声明。忽略 `.asmdef` 还会导致包内的 `Editor` 代码在构建时被错误打包进游戏包体，引发构建失败。

**误区二：混淆 `package.json` 版本与 Git tag 的对应关系**。通过 Git URL 安装时，Package Manager 读取的版本号来自仓库内 `package.json` 中的 `version` 字段，而非 Git tag 名称本身。若 `package.json` 写的是 `1.0.0` 但 Git tag 打的是 `v1.0.1`，Package Manager 显示和锁定的版本将是 `1.0.0`。正确做法是在每次发布时同步更新 `package.json` 中的版本号与对应的 Git tag。

**误区三：将 Package 的 `Samples~` 目录与普通目录混淆**。Package 中以波浪号结尾命名的目录（如 `Samples~`）不会被 Unity 自动导入，用户需通过 Package Manager UI 手动选择导入。若开发者将示例场景放在普通目录，每个安装该包的项目都会强制获得这些资产，污染项目内容；正确做法是始终将可选内容放在 `Samples~` 目录并在 `package.json` 的 `samples` 数组中注册。

## 知识关联

**前置基础——插件架构**：理解 Unity Package 需要先掌握 DLL 程序集的引用机制和 Unity 的双编译域（Editor Domain 与 Player Domain）概念。传统插件架构中对 `Plugins` 目录的约定（`Plugins/Editor` 中的代码仅在编辑器加载）在 Package 体系中被 `.asmdef` 的 `includePlatforms` 字段所取代，是从旧体系向新体系迁移的关键转换点。

**横向关联——Unity Registry 与 UPM 协议**：Unity 的包注册表基于 npm 协议的子集实现，因此私有注册表方案（如 Verdaccio、Azure Artifacts）均与 npm 生态直接兼容。理解 `manifest.json` 中的 `lock` 字段（`packages-lock.json`）可以帮助团队实现确定性构建，确保所有成员安装完全相同的依赖版本，这与前端工程中 `package-lock.json` 的作用完全类似。