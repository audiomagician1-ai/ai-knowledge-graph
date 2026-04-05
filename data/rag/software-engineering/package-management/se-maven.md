---
id: "se-maven"
concept: "Maven/Gradle依赖"
domain: "software-engineering"
subdomain: "package-management"
subdomain_name: "包管理"
difficulty: 2
is_milestone: false
tags: ["JVM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Maven/Gradle 依赖管理

## 概述

Maven 和 Gradle 是 JVM 生态系统中两大主流构建工具，专门解决 Java/Kotlin/Scala 项目中第三方库的获取、版本管理和冲突解决问题。Maven 于 2004 年由 Apache 发布，使用 XML 格式的 `pom.xml` 文件声明依赖；Gradle 于 2012 年发布，使用基于 Groovy 或 Kotlin DSL 的 `build.gradle` 文件，构建速度比 Maven 快约 2-10 倍（得益于增量编译和构建缓存机制）。

这两套工具的核心价值在于"坐标定位"机制：每个依赖库由 `groupId:artifactId:version`（简称 GAV）三元组唯一标识。例如 `com.google.guava:guava:32.1.2-jre` 明确指向 Google Guava 库的特定版本，开发者无需手动下载 JAR 文件，工具会自动从中央仓库拉取并缓存到本地。

## 核心原理

### 仓库体系与依赖解析流程

Maven/Gradle 的依赖解析遵循固定的仓库查找顺序：首先检查**本地仓库**（默认路径为 `~/.m2/repository`，Gradle 为 `~/.gradle/caches`），若未命中则访问**远程仓库**。最权威的远程仓库是 Maven Central（`https://repo1.maven.org/maven2`），托管了超过 500 万个构件。企业内部通常还会部署 Nexus 或 Artifactory 作为私有仓库代理。

Gradle 中配置仓库的写法如下：

```groovy
repositories {
    mavenCentral()
    maven { url "https://jitpack.io" }
}
```

### 传递依赖（Transitive Dependency）

传递依赖是指：当项目引入库 A，而库 A 自身依赖库 B 时，构建工具会自动将库 B 也纳入编译路径，无需开发者手动声明。例如引入 Spring Boot Starter Web 2.7.x 时，系统会自动传递引入 Spring MVC、Jackson、Tomcat 等共计数十个 JAR 文件。

这种机制通过递归读取每个库的 `pom.xml` 或 Gradle 模块元数据实现。传递依赖的层级理论上无限制，但在大型项目中可能导致"依赖地狱"——不同路径引入同一库的不同版本，产生版本冲突。

### 依赖版本冲突解决策略

**Maven** 采用"最短路径优先"（Nearest Definition）原则：在依赖树中，离根节点最近的版本声明胜出。若路径长度相同，则先声明者优先（First Declaration Wins）。

**Gradle** 默认采用"最高版本优先"（Highest Version Wins）策略：在所有传递依赖中自动选择版本号最大的那个，通常能更好地避免兼容性问题。开发者也可以通过强制锁定版本：

```groovy
configurations.all {
    resolutionStrategy {
        force 'com.fasterxml.jackson.core:jackson-databind:2.15.2'
    }
}
```

### 依赖作用域（Scope）

Maven 定义了 6 种作用域，最常用的三种为：
- `compile`（默认）：编译和运行时均可用，并传递给下游模块
- `test`：仅在测试编译和执行阶段可用，典型库为 JUnit 5（`junit-jupiter:5.9.3`）
- `provided`：编译时需要但运行时由容器提供，典型场景是 Servlet API

Gradle 对应的配置名称为 `implementation`（替代旧版 `compile`）、`testImplementation`、`compileOnly`。其中 `implementation` 与旧版 `compile` 的关键区别在于：`implementation` 不向上游模块暴露传递依赖，从而减少不必要的重新编译。

## 实际应用

**场景一：在 Spring Boot 项目中引入 MyBatis**

在 Maven `pom.xml` 中写入：
```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.1</version>
</dependency>
```
保存后，IDE（如 IntelliJ IDEA）触发自动导入，Maven 从 Central 仓库下载该 JAR 及其所有传递依赖（包括 mybatis-core、spring-jdbc 等），整个过程无需手动管理任何 JAR 文件。

**场景二：排除有安全漏洞的传递依赖**

假设某传递依赖引入了有 CVE 漏洞的 `log4j:log4j:1.2.17`，可在 Gradle 中排除：
```groovy
implementation('org.example:some-lib:1.0') {
    exclude group: 'log4j', module: 'log4j'
}
```
在 Maven 中使用 `<exclusions>` 标签实现同样效果。

**场景三：使用 BOM 统一管理版本**

Spring Boot 提供 BOM（Bill of Materials）文件，在 Gradle 中引入后，Spring 生态系列库无需单独声明版本号：
```groovy
implementation platform('org.springframework.boot:spring-boot-dependencies:3.1.4')
implementation 'org.springframework.boot:spring-boot-starter-web' // 无需写版本
```

## 常见误区

**误区一：`implementation` 和 `api` 可以随意混用**

Gradle 的 `api` 配置会将依赖暴露给所有依赖本模块的上游模块（即传递导出），而 `implementation` 不会。在多模块项目中滥用 `api` 会导致任何一个底层依赖的版本变化都触发整个项目的全量重编译，大型项目的构建时间可能从几分钟膨胀到几十分钟。

**误区二：版本号越新越好，直接用 `LATEST` 或 `+`**

Maven 支持使用 `LATEST` 关键字，Gradle 支持 `2.+` 这类动态版本，表示自动使用最新版本。这在 CI/CD 环境中极其危险——同一套代码在不同时间构建可能引入破坏性变更，导致"在我机器上能跑"的经典问题。正确做法是锁定精确版本，并通过 `gradle/wrapper/gradle-wrapper.properties` 或 Maven 的 `<dependencyManagement>` 节统一管理版本号。

**误区三：本地仓库缓存永远可信**

如果曾经错误地将一个损坏的 JAR 上传到本地仓库，或网络中断导致下载不完整，之后的构建会直接使用缓存中的损坏文件并产生难以排查的错误。可执行 `mvn dependency:resolve -U`（Maven）或 `gradle --refresh-dependencies`（Gradle）强制重新从远程仓库拉取，跳过本地缓存。

## 知识关联

**与语义化版本（SemVer）的关系**：Maven/Gradle 的版本冲突解决策略依赖于版本号的可比较性。遵循 SemVer（`主版本.次版本.修订号`）规范的库能让工具更准确地判断向后兼容性，`MAJOR` 版本号变更意味着破坏性 API 变更，工具在自动升级时应当保守对待。

**与 SNAPSHOT 版本的关系**：以 `-SNAPSHOT` 结尾的版本（如 `1.0.0-SNAPSHOT`）是开发中的不稳定版本，Maven 默认每天最多从远程仓库检查一次更新，而正式发布版本一旦上传到 Maven Central 便不可修改（不可变构件原则）。理解这一区别有助于正确配置 CI 流水线中的快照仓库和发布仓库。

**与多模块项目（Multi-Module Project）的关系**：在包含多个子模块的 Maven 或 Gradle 项目中，父 POM / 根 `build.gradle` 通过 `<dependencyManagement>` 或 `subprojects {}` 块统一声明各子模块共用的依赖版本，避免不同子模块各自引入同一库的不同版本而产生运行时类加载冲突。