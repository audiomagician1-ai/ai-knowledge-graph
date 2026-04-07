# Gradle

## 概述

Gradle 是一款专为 JVM 生态设计的自动化构建工具，以 Groovy DSL（`build.gradle`）或 Kotlin DSL（`build.gradle.kts`）作为构建脚本语言。与 Apache Maven 的纯 XML 声明式模型不同，Gradle 的构建脚本本质上是可执行的 Groovy/Kotlin 程序，允许开发者在脚本中嵌入条件分支、循环、闭包和自定义函数，从而实现 Maven 无法表达的复杂构建逻辑。

Gradle 1.0 版本于 2012 年 6 月正式发布，由 Hans Dockter 主导设计，核心架构借鉴了 Apache Ant 的灵活任务模型与 Apache Maven 的约定优于配置（Convention Over Configuration）理念，并在二者基础上引入了基于有向无环图的增量构建引擎。2013 年，Google 将 Gradle 选为 Android Studio 的官方构建工具，此举直接推动了 Gradle 在移动端开发社区的大规模普及。至 Gradle 8.x 时代，其已成为 Spring Boot、Kotlin 多平台（KMP）、Micronaut 等主流框架的默认构建方案。

Gradle 官方性能基准测试数据显示，在包含 500 个子模块的大型多项目构建场景中，开启增量构建与构建缓存后，Gradle 的构建时间可比等效 Maven 配置缩短 **85%–99%**（Gradle Inc., 2023）。这一性能优势源自其底层的 Task 输入/输出快照机制与远程构建缓存协议，而非简单的并行编译加速。

---

## 核心原理

### 三阶段构建生命周期

Gradle 的每次构建执行严格遵循三个串行阶段：

1. **初始化阶段（Initialization Phase）**：Gradle 读取 `settings.gradle(.kts)` 文件，确定本次构建涉及哪些项目（单项目或多项目），为每个项目创建对应的 `Project` 对象。
2. **配置阶段（Configuration Phase）**：Gradle 执行所有项目的 `build.gradle(.kts)` 脚本，构造完整的 Task 有向无环图（DAG）。**注意**：此阶段所有脚本顶层代码均会执行，与最终执行哪些 Task 无关，因此耗时操作绝不能直接置于脚本顶层。
3. **执行阶段（Execution Phase）**：Gradle 按 DAG 拓扑顺序执行被请求的 Task 及其所有依赖 Task。

理解配置阶段与执行阶段的区别是避免 Gradle 脚本性能陷阱的关键。错误地将文件 I/O 或网络请求写在配置阶段，会导致即使执行 `./gradlew help` 也触发不必要的开销（Muschko, 2020）。

### 有向无环图（DAG）任务调度模型

Gradle 将构建建模为 Task 的有向无环图 $G = (V, E)$，其中顶点集 $V$ 为所有 Task，有向边集 $E$ 表示依赖关系：若 Task $B$ 依赖 Task $A$，则存在有向边 $A \rightarrow B$。Gradle 使用 Kahn 算法对 DAG 进行拓扑排序，保证每个 Task 仅在其所有前驱 Task 完成后方可启动。

Task 间依赖通过以下三种关系声明，语义存在细微差异：

- `dependsOn`：硬性依赖，被依赖 Task 必须在本 Task 之前执行且必须成功。
- `mustRunAfter`：顺序约束，若两个 Task 同时被请求执行，则保证顺序，但不触发依赖 Task 的自动执行。
- `finalizedBy`：无论本 Task 成功还是失败，指定的 finalizer Task 都会在其后执行，常用于清理资源。

```kotlin
// build.gradle.kts 示例（Kotlin DSL）
tasks.register("integrationTest") {
    dependsOn("test")
    mustRunAfter("check")
    finalizedBy("generateTestReport")
}
```

### 增量构建：输入/输出快照机制

Gradle 的增量构建基于对 Task **输入（Inputs）** 和 **输出（Outputs）** 的内容快照。每次 Task 执行后，Gradle 将输入文件集合的 SHA-256 哈希树（Merkle Tree 结构）存储在 `.gradle/` 目录下的构建缓存数据库中。下次执行时，若输入哈希与上次完全一致且输出文件未被篡改，该 Task 被标记为 `UP-TO-DATE` 并跳过。

Task 的缓存键（Cache Key）计算公式如下：

$$\text{CacheKey} = \text{Hash}(\text{TaskClass} \| \text{GradleVersion} \| \text{Hash}(\text{Inputs}))$$

其中 $\text{Hash}(\text{Inputs})$ 为所有输入属性（文件内容哈希、系统属性、环境变量）的规范化聚合哈希。这意味着即使代码内容相同，不同 Gradle 版本或不同 Task 实现类产生的缓存键也不相同，从而避免缓存污染。

### 远程构建缓存（Remote Build Cache）

Gradle 支持将 Task 输出上传至远程 HTTP 缓存服务器（如 Gradle Enterprise / Develocity 或自建 Nginx 缓存节点）。当 CI 服务器完成构建并推送缓存后，本地开发者在执行相同 Git commit 的构建时，可直接从远程缓存拉取编译产物，Task 状态显示为 `FROM-CACHE` 而非 `UP-TO-DATE`。

```kotlin
// settings.gradle.kts 配置远程构建缓存
buildCache {
    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/cache/")
        isPush = System.getenv("CI") == "true"  // 仅 CI 环境推送缓存
        credentials {
            username = providers.environmentVariable("CACHE_USER").get()
            password = providers.environmentVariable("CACHE_PASSWORD").get()
        }
    }
}
```

---

## 关键方法与 DSL 语法

### 依赖管理：配置（Configuration）体系

Gradle 通过**依赖配置（Dependency Configuration）**区分不同作用域的依赖，Java 插件默认提供以下核心配置：

| 配置名称 | 编译期可见 | 运行期可见 | 传递给消费者 |
|---|---|---|---|
| `implementation` | ✓ | ✓ | ✗（不暴露给依赖本项目的上层模块） |
| `api` | ✓ | ✓ | ✓（暴露给上层，需 `java-library` 插件） |
| `compileOnly` | ✓ | ✗ | ✗ |
| `runtimeOnly` | ✗ | ✓ | ✗ |
| `testImplementation` | ✓（仅测试） | ✓（仅测试） | ✗ |

`implementation` 与 `api` 的区别是 Gradle 依赖管理中最易混淆的概念：使用 `implementation` 声明的依赖不会泄漏到上层模块的编译类路径，从而在修改底层库时仅触发直接依赖该库的模块重新编译，而非整个依赖树的全量重编译。

### Gradle Wrapper 版本锁定

`gradle/wrapper/gradle-wrapper.properties` 中的 `distributionUrl` 字段精确锁定构建工具版本：

```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-bin.zip
distributionSha256Sum=194717442575a6f96e1c1befa2c30e9a4fc90f701d7aee33eb879b79e7ff05c0
```

`distributionSha256Sum` 字段（Gradle 4.2+ 引入）对下载的 Gradle 发行包进行 SHA-256 校验，防止供应链攻击中的中间人篡改。在零信任安全环境下，这一校验尤为重要。

### Convention Plugin 模式：多模块项目的配置复用

在包含数十个子模块的大型项目中，直接在每个 `build.gradle.kts` 中重复声明插件和依赖会导致严重的配置漂移。Gradle 推荐的解决方案是在 `buildSrc/` 目录或独立的构建逻辑模块中编写 **Convention Plugin**：

```kotlin
// buildSrc/src/main/kotlin/myproject.kotlin-library-conventions.gradle.kts
plugins {
    kotlin("jvm")
    `java-library`
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    testImplementation(kotlin("test"))
    testImplementation("io.mockk:mockk:1.13.10")
}
```

所有子模块只需 `plugins { id("myproject.kotlin-library-conventions") }` 即可继承统一的编译器版本、测试框架配置和代码规范插件，单处修改即可同步至全部模块。

### 配置缓存（Configuration Cache）

Gradle 7.4 引入稳定的配置缓存功能，将配置阶段的 Task DAG 序列化存储。再次执行相同命令时，Gradle 跳过整个配置阶段直接进入执行阶段，对于拥有数百个子模块的项目可将总构建时间进一步缩短 **30%–60%**。启用方式：

```bash
./gradlew build --configuration-cache
# 或在 gradle.properties 中持久化启用
org.gradle.configuration-cache=true
```

配置缓存对脚本的约束较为严格：不允许在 Task action 中访问 `Project` 对象（应改用 `Provider` API 惰性求值），需要逐步迁移遗留脚本。

---

## 实际应用案例

### 案例一：Android 多风味（Product Flavor）构建矩阵

Android 项目中，Gradle 的 `productFlavors` 与 `buildTypes` 组合生成构建变体（Build Variant）矩阵。例如，定义 `free`/`paid` 两种风味与 `debug`/`release` 两种构建类型，Gradle 自动生成 `freeDebug`、`freeRelease`、`paidDebug`、`paidRelease` 四个变体，每个变体拥有独立的源集（Source Set）、资源目录和依赖配置：

```kotlin
android {
    flavorDimensions += "tier"
    productFlavors {
        create("free") { dimension = "tier"; applicationIdSuffix = ".free" }
        create("paid") { dimension = "tier"; versionNameSuffix = "-paid" }
    }
}
dependencies {
    "paidImplementation"("com.example:premium-analytics:2.1.0")
}
```

这种构建矩阵能力在 Maven 中需借助 Profile 机制模拟，且无法达到同等的源集隔离粒度。

### 案例二：Spring Boot 项目的可执行 JAR 打包

Spring Boot Gradle 插件（`org.springframework.boot`）通过重写 `bootJar` Task，将依赖 JAR 嵌套打包为可执行的 Fat JAR，内部使用自定义类加载器（`JarLauncher`）按层加载依赖，同时支持 OCI 镜像分层（Layered JAR）以优化 Docker 构建缓存命中率：

```kotlin
tasks.bootJar {
    layered {
        isEnabled = true
    }
    archiveFileName.set("app.jar")
}
```

---

## 常见误区

### 误区一：在配置阶段执行耗时操作

新手常将网络请求或文件读取直接写在 `build.gradle.kts` 顶层（配置阶段），导致每次执行任何 Gradle 命令（包括 `./gradlew tasks`）都触发这些操作。正确做法是将其包裹在 `doFirst`/`doLast` 块内，或使用 `providers.exec()` 等惰性 API。

### 误区二：滥用 `api` 配置暴露内部依赖

将所有依赖声明为 `api` 会使依赖图中所有上层模块的编译类路径包含底层实现细节，任何底层库的版本变更都会触发全量重编译，彻底丧失 `implementation` 带来的编译隔离优势。经验规则：仅在返回类型或参数类型属于该依赖库时才使用 `api`。

### 误区三：混淆 `UP-TO-DATE` 与 `FROM-CACHE`

`UP-TO-DATE` 表示 Gradle 在本地检测到输入/输出未变化，跳过执行；`FROM-CACHE` 表示本地无有效输出但从构建缓存（本地或远程）恢复了产物。二者效果等价但来源不同——理解这一区别有助于诊断 CI 构建缓存未命中问题。

### 误区四：忽略 Kotlin DSL 的类型安全优势

许多团队出于惯性继续使用 Groovy