---
id: "se-nuget"
concept: "NuGet"
domain: "software-engineering"
subdomain: "package-management"
subdomain_name: "包管理"
difficulty: 2
is_milestone: false
tags: ["C#"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.7
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.5
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# NuGet

## 概述

NuGet 是 Microsoft 于 2010 年发布的 .NET 平台官方包管理器，最初作为 Visual Studio 扩展推出，后来成为 .NET 生态系统的标准基础设施。它允许开发者将可复用的代码库打包为 `.nupkg` 格式文件（实质上是带有特定元数据的 ZIP 压缩包），并通过统一的仓库系统分发和安装。

NuGet 的核心仓库是 nuget.org，截至 2024 年已托管超过 35 万个不同的包，累计下载量超过 4000 亿次。这使得 .NET 开发者可以不必重复实现 JSON 解析、HTTP 客户端、数据库驱动等通用功能，直接从 nuget.org 安装成熟的第三方实现。例如，`Newtonsoft.Json` 是历史上下载量最高的 NuGet 包之一，它提供了 .NET 的 JSON 序列化功能。

NuGet 解决的核心问题是依赖管理：当项目 A 需要库 X 的 2.0 版本，而库 X 又依赖库 Y 的 1.5 版本时，NuGet 会自动解析并安装整个依赖树，避免手动查找和配置 DLL 文件的繁琐工作。

---

## 核心原理

### 包的结构与 `.nupkg` 格式

每个 NuGet 包是一个重命名的 ZIP 文件，内部包含三类核心内容：
- `lib/` 目录：按目标框架分类的 DLL 文件，如 `lib/net6.0/MyLibrary.dll`
- `*.nuspec` 文件：XML 格式的元数据清单，描述包的 ID、版本号、作者、许可证和依赖关系
- `contentFiles/` 或 `tools/` 目录（可选）：安装时复制到项目的文件或构建脚本

`.nuspec` 中的版本号遵循语义化版本规范（SemVer），格式为 `主版本.次版本.补丁版本`，例如 `3.1.4`。主版本号递增表示有破坏性变更，次版本号递增表示新增功能但向后兼容，补丁号递增表示 Bug 修复。

### 项目文件中的包引用方式

现代 .NET（.NET Core / .NET 5+）项目使用 SDK 风格的 `.csproj` 文件管理 NuGet 依赖。包引用写在 `<PackageReference>` 元素中：

```xml
<ItemGroup>
  <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  <PackageReference Include="Microsoft.EntityFrameworkCore" Version="7.0.0" />
</ItemGroup>
```

旧式 .NET Framework 项目则使用独立的 `packages.config` 文件记录依赖，并将 DLL 实际复制到项目的 `packages/` 子目录。这两种方式的主要区别在于：SDK 风格将包缓存在全局目录（Windows 下为 `%USERPROFILE%\.nuget\packages`），多个项目共享同一份本地缓存，节省磁盘空间。

### 版本范围与依赖解析

NuGet 支持在 `<PackageReference>` 中指定版本范围，常见语法如下：

| 表达式 | 含义 |
|---|---|
| `13.0.3` | 精确指定 13.0.3 |
| `[13.0.3, )` | 13.0.3 或更高 |
| `[13.0.0, 14.0.0)` | 13.x 系列，不含 14.0.0 |
| `*` | 最新稳定版 |

当多个包依赖同一个库的不同版本时，NuGet 采用"最低适用版本"（Lowest Applicable Version）策略选择版本，而非自动使用最高版本。这个策略旨在保证构建的可重复性，但有时会导致项目使用较旧的间接依赖版本。

### 还原机制（Restore）

执行 `dotnet restore` 或在 Visual Studio 中构建项目时，NuGet 会读取 `.csproj` 中的 `<PackageReference>` 列表，从配置的包源（默认为 nuget.org）下载对应的 `.nupkg` 文件，解压到全局缓存目录，并生成 `project.assets.json` 锁文件（位于 `obj/` 目录）。该锁文件记录了完整的依赖解析结果，后续构建直接读取此文件，不需要重新计算依赖树。

---

## 实际应用

### 安装与卸载包

在 .NET CLI 中安装包使用以下命令：

```bash
dotnet add package Newtonsoft.Json --version 13.0.3
```

该命令会自动修改 `.csproj` 文件，添加对应的 `<PackageReference>`，并触发还原操作。卸载包则使用：

```bash
dotnet remove package Newtonsoft.Json
```

在 Visual Studio 中，NuGet 包管理器 UI（通过右键项目 → "管理 NuGet 包"打开）提供图形界面，可搜索 nuget.org 并一键安装。

### 发布自定义包到 nuget.org

企业或开源开发者可以将自己的库打包发布。流程为：
1. 在 `.csproj` 中设置 `<GeneratePackageOnBuild>true</GeneratePackageOnBuild>` 并填写 `<PackageId>`、`<Version>`、`<Authors>` 等元数据
2. 执行 `dotnet pack` 生成 `.nupkg` 文件
3. 使用 `dotnet nuget push MyPackage.1.0.0.nupkg --api-key <TOKEN> --source https://api.nuget.org/v3/index.json` 上传到 nuget.org

### 私有包源（Private Feed）

企业内部开发的库不适合公开到 nuget.org，可以搭建私有 NuGet 服务器。Azure DevOps Artifacts 和 GitHub Packages 均支持作为 NuGet 私有源。通过在项目根目录的 `nuget.config` 文件中配置 `<packageSources>`，可以让 `dotnet restore` 同时从 nuget.org 和私有源拉取包。

---

## 常见误区

### 误区一：将 `packages/` 目录提交到 Git 仓库

使用旧式 `packages.config` 的项目，如果将 `packages/` 目录一同提交到版本控制，会导致仓库体积膨胀数十甚至数百 MB。正确做法是在 `.gitignore` 中排除该目录，依靠 `dotnet restore` 在构建前自动还原。现代 SDK 风格项目的全局缓存目录（`~/.nuget/packages`）天然不在项目目录内，不存在此问题。

### 误区二：版本号中 `*` 通配符在 CI 环境中的风险

使用 `Version="*"` 会在每次还原时拉取最新版本，看似方便，实则导致构建不可重复——今天和明天的构建可能使用不同版本的依赖，引入意外的破坏性变更。生产项目应锁定到具体版本号，或启用 `<RestoreLockedMode>true</RestoreLockedMode>` 强制使用 `packages.lock.json` 中记录的精确版本。

### 误区三：混淆 NuGet 包版本与 .NET 运行时版本

安装 `Microsoft.AspNetCore.App 8.0.0` 这样的包并不意味着项目会使用 .NET 8 运行时；实际的运行时版本由 `.csproj` 中的 `<TargetFramework>net8.0</TargetFramework>` 决定。两者需要匹配，否则会出现目标框架不兼容（TFM mismatch）的还原错误。

---

## 知识关联

NuGet 与 `.csproj` 项目文件紧密结合，理解 `<TargetFramework>` 的值（如 `net48`、`net6.0`、`netstandard2.0`）有助于判断某个 NuGet 包是否与当前项目兼容——包的 `lib/` 目录下必须存在与项目目标框架兼容的子目录，否则安装会失败。

在更大的 .NET 构建体系中，NuGet 与 MSBuild 深度集成：`dotnet build` 在编译前会自动触发 NuGet 还原步骤，生成的 `project.assets.json` 直接被 MSBuild 读取以确定编译时引用哪些 DLL。掌握 NuGet 之后，可以进一步学习如何编写多目标框架（Multi-targeting）包，让同一个 `.nupkg` 同时支持 `.NET Framework 4.8` 和 `.NET 6`，这需要在 `<TargetFrameworks>` 中列出多个框架标识并为每个框架编写条件编译代码。