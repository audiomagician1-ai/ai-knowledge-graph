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
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---



# Unity Package

## 概述

Unity Package（统一包）是Unity引擎通过 **Package Manager**（包管理器）分发和管理功能模块的标准化格式。每个Package本质上是一个包含特定元数据文件 `package.json` 的目录，其中声明了包的名称（必须遵循反向域名格式，如 `com.unity.inputsystem`）、版本号（遵循语义化版本规范SemVer，如 `1.4.2`）及依赖关系。

Unity Package Manager（UPM）于 **Unity 2018.1** 版本正式引入，在此之前开发者只能依赖 Asset Store 的 `.unitypackage` 格式，该格式无法声明依赖、无法版本控制、也无法与Git集成。UPM的出现彻底改变了Unity生态中功能模块的分发方式，使得Universal Render Pipeline、Input System等核心功能本身也以Package形式维护，开发者可以精确控制每项功能的版本。

从插件开发角度看，将插件制作为Unity Package的关键优势在于：通过 **Assembly Definition（程序集定义，`.asmdef`文件）** 精确划分编译边界，避免插件代码与用户项目代码产生不可控的编译依赖，同时支持条件编译平台过滤，大幅缩短增量编译时间。

---

## 核心原理

### package.json 结构与字段语义

`package.json` 是每个Unity Package的必需入口文件，位于包根目录。其关键字段包括：

- **`name`**：必须为反向域名格式（如 `com.mycompany.myplugin`），这是包的唯一标识符，不得含有大写字母。
- **`version`**：严格遵循SemVer格式 `MAJOR.MINOR.PATCH`，UPM依据此字段解析依赖兼容性。
- **`unity`**：声明最低兼容Unity版本，格式为 `"2021.3"`（不含补丁号）。
- **`dependencies`**：以 JSON 对象声明对其他Package的依赖，例如 `"com.unity.mathematics": "1.2.6"`。
- **`type`**：可设为 `"tool"` 或 `"library"`，影响Package在Package Manager窗口中的分类展示。

一个最简化的合法 `package.json` 示例：
```json
{
  "name": "com.example.myplugin",
  "version": "0.1.0",
  "displayName": "My Plugin",
  "unity": "2021.3"
}
```

### Assembly Definition 的编译隔离机制

`.asmdef` 文件（Assembly Definition File）控制Unity如何将脚本划分为独立的 `.dll` 程序集。在没有任何 `.asmdef` 的项目中，所有脚本被编译入默认的 `Assembly-CSharp.dll`，任何一处改动都会触发全部脚本重新编译。

在Package中放置 `.asmdef` 文件后，Unity只对该程序集内发生变动的代码进行重新编译。`.asmdef` 中的关键配置项：

- **`name`**：程序集名称，需全局唯一，通常与包名对应，如 `MyCompany.MyPlugin`。
- **`references`**：列出此程序集依赖的其他程序集名称（注意：引用的是程序集名，不是包名）。
- **`includePlatforms` / `excludePlatforms`**：白名单或黑名单控制平台范围，例如将 Editor 专用工具代码的 `.asmdef` 设置 `"includePlatforms": ["Editor"]`，确保该代码不被打入运行时构建。
- **`allowUnsafeCode`**：允许在该程序集内使用 C# `unsafe` 关键字，Package级别精确开启而非全局开启。

一个Package通常至少有两个 `.asmdef`：一个位于 `Runtime/` 目录下的运行时程序集，一个位于 `Editor/` 目录下仅限编辑器的程序集。

### 包的标准目录结构

UPM规范推荐以下目录布局，Unity工具链对这些目录名有特殊识别：

```
com.example.myplugin/
├── package.json
├── README.md
├── CHANGELOG.md
├── LICENSE.md
├── Runtime/
│   ├── MyPlugin.Runtime.asmdef
│   └── *.cs
├── Editor/
│   ├── MyPlugin.Editor.asmdef
│   └── *.cs
├── Tests/
│   ├── Runtime/
│   │   └── MyPlugin.Tests.asmdef
│   └── Editor/
└── Documentation~/    # 波浪线后缀使Unity不导入此目录中的资产
```

`Documentation~` 目录中的波浪线后缀是UPM的特殊约定，告知Unity Asset Database完全忽略该目录，避免为文档文件生成无用的 `.meta` 文件。

---

## 实际应用

### 通过 Git URL 分发私有插件

开发者可以在项目的 `Packages/manifest.json` 中直接以Git URL引用Package，无需发布到Unity注册表：

```json
{
  "dependencies": {
    "com.example.myplugin": "https://github.com/example/myplugin.git#v1.2.0"
  }
}
```

`#v1.2.0` 部分指定Git标签，实现版本锁定。这是企业内部插件分发的常见方案，完全绕过Unity Asset Store的审核流程。

### 嵌入式Package（Embedded Package）用于本地开发

在开发阶段，将Package目录直接放入项目的 `Packages/` 文件夹下（而非 `Assets/` 文件夹），UPM会以"嵌入式包"模式处理它。此时Package内容受版本控制，同时享有UPM的程序集隔离能力，调试完成后可直接发布为独立Git仓库。

---

## 常见误区

### 误区一：`.asmdef` 的 `references` 填写的是包名

实际上 `references` 字段填写的是**程序集名称**（即另一个 `.asmdef` 文件中 `name` 字段的值），而不是 `package.json` 中的包名。例如要引用 Unity Mathematics，应填 `"Unity.Mathematics"` 而非 `"com.unity.mathematics"`。混淆两者会导致编译时找不到引用，报出 `Assembly ... not found` 错误。

### 误区二：`package.json` 的 `version` 可以任意修改

SemVer规范要求：破坏性API变更必须递增MAJOR版本号，新增功能递增MINOR，仅修复Bug递增PATCH。若在已发布给用户的Package中随意修改版本号（例如修复Bug却直接跳到新MAJOR），会导致依赖该包的其他Package的版本约束计算出错，UPM的依赖解析器（基于PubGrub算法）可能拒绝解析或解析到错误版本。

### 误区三：把 Editor 代码放入 Runtime 程序集

若将含有 `UnityEditor` 命名空间的代码放入无平台限制的 `.asmdef` 所属目录，项目在进行非编辑器平台构建（如Android、iOS）时会因找不到 `UnityEditor` 程序集而**构建失败**。正确做法是在 `Editor/` 目录下放置单独的 `.asmdef` 并将 `includePlatforms` 设为 `["Editor"]`。

---

## 知识关联

Unity Package是插件架构知识的直接落地形式。**插件架构**中讨论的依赖隔离、接口边界等原则，在UPM中通过 `package.json` 的 `dependencies` 字段和 `.asmdef` 的 `references` 字段得到具体实现——前者在包的分发层面声明依赖，后者在C#编译层面强制隔离边界。

理解 `.asmdef` 的程序集划分机制，为进一步学习Unity的**测试框架（Unity Test Framework）** 奠定基础：UTFPackage本身（`com.unity.test-framework`）要求测试代码必须拥有独立的 `.asmdef` 并在其中将 `"testables"` 字段配置正确，否则无法被Test Runner发现。掌握Package的标准目录结构，也是理解 **Addressable Asset System** 如何与Package协作进行资产分发的前提——两者均使用UPM作为内容分发基础设施。