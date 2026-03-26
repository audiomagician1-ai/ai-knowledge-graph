---
id: "se-flaky-tests"
concept: "不稳定测试"
domain: "software-engineering"
subdomain: "tdd"
subdomain_name: "测试驱动开发"
difficulty: 2
is_milestone: false
tags: ["维护"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.517
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 不稳定测试（Flaky Test）

## 概述

不稳定测试（Flaky Test）是指在代码未发生任何变更的情况下，多次运行同一测试用例时，结果会随机出现"通过"或"失败"交替出现的测试。这种测试的核心特征是**结果不确定性**：相同的测试代码、相同的被测代码、相同的环境，却产生不同的输出。Google 在 2016 年发布的研究报告显示，其内部约 **1.5%** 的测试运行存在不稳定问题，而在大规模持续集成系统中，不稳定测试每天会触发数千次错误的构建失败警报。

不稳定测试最早作为独立研究课题被关注，是在 2012 年前后随着持续集成（CI）实践的普及而兴起的。当测试套件规模扩大到数万个用例时，工程师发现频繁的"误报失败"严重干扰了真实缺陷的发现效率。Netflix、Spotify 等公司相继公开了各自的 Flaky Test 治理方案，使其成为测试驱动开发（TDD）领域的重要工程问题。

不稳定测试的危害不仅仅是"浪费时间重跑"。当开发团队习惯了"这个测试失败是正常的，再跑一次就好"的心态后，真正的回归缺陷会被淹没在噪声中，导致生产环境出现本可在 CI 阶段发现的问题。这种"狼来了"效应会从根本上破坏 TDD 工作流中测试红绿循环的可信度。

---

## 核心原理

### 不稳定测试的五大根本原因

**1. 时序与并发依赖**  
测试中存在对执行时间的隐式假设是最常见的原因，占所有 Flaky Test 的约 **45%**（根据 2020 年 CMU 对 24 个开源项目的统计）。典型场景包括：使用固定的 `Thread.sleep(500)` 等待异步操作完成，而在 CI 服务器负载高时 500ms 不足以完成操作；或者多线程测试中存在竞态条件（Race Condition），读取共享状态的顺序每次不同。

**2. 测试执行顺序依赖**  
测试用例之间存在隐性的状态耦合。例如，测试 A 向数据库写入了一条记录，测试 B 假设数据库为空，若测试框架改变执行顺序（如 JUnit 5 默认使用 `MethodOrderer.Random`），测试 B 就会随机失败。诊断方法是使用 `--random-seed` 参数固定随机种子，若指定特定种子后失败可重现，则确认是顺序依赖问题。

**3. 外部资源与网络依赖**  
测试直接调用真实的第三方 API、数据库连接或文件系统，导致网络抖动、服务限流或文件锁定时出现失败。这类测试的识别特征是失败日志中包含 `SocketTimeoutException`、`ConnectionRefusedException` 等网络异常，而不是断言失败（`AssertionError`）。

**4. 时间与日期敏感**  
测试中使用 `new Date()` 或 `LocalDate.now()` 获取当前时间，导致测试在特定日期（如月末、闰年2月29日、时区切换日）失败。经典案例是某团队的测试在每月最后一天失败，因为代码计算"当月第一天到今天"的天数时，在31天的月份里超出了预期范围。

**5. 资源泄漏与内存状态污染**  
前一个测试未正确释放资源（如未关闭数据库连接、未清理静态变量、未重置单例对象），导致后续测试读取到脏数据。在 Java 中，未在 `@AfterEach` 中清理的 `static` 字段是最常见的污染来源。

### 不稳定测试的检测方法

检测 Flaky Test 的标准方法是**多次重复运行（Rerun Detection）**：对同一测试不改变任何代码，连续运行 N 次（通常取 N=10 或 N=50），若通过率既不是 100% 也不是 0%，则判定为不稳定测试。

自动化工具方面：
- **pytest-rerunfailures**：Python 生态中通过 `--rerun-failures=3` 参数自动重跑失败测试
- **Gradle 的 `--rerun-tasks`** 以及 **flaky-test-handler** 插件：专门用于标记和隔离不稳定测试
- **DeFlaker**（Java）：通过对比覆盖率数据识别"未被当前变更影响却失败的测试"

---

## 实际应用

### 修复策略一：消除时序假设

将 `Thread.sleep(固定毫秒)` 替换为**轮询等待（Polling Wait）**机制。在 Selenium 测试中，用 `WebDriverWait` 替代固定等待：

```java
// 错误写法（不稳定）
Thread.sleep(2000);
element.click();

// 正确写法（稳定）
new WebDriverWait(driver, Duration.ofSeconds(10))
    .until(ExpectedConditions.elementToBeClickable(locator))
    .click();
```

### 修复策略二：隔离外部依赖

对于网络和数据库依赖，在单元测试层级引入 **Mock/Stub**（如 Mockito、WireMock），在集成测试层级使用 **TestContainers** 启动隔离的 Docker 容器，确保每次测试使用独立的数据库实例，初始状态完全一致。

### 修复策略三：隔离而非立即修复

当团队资源有限，无法立即修复所有不稳定测试时，可使用框架提供的标注机制临时隔离：JUnit 5 中使用 `@Disabled("Flaky: #issue-123")`，pytest 中使用 `@pytest.mark.skip`，并配合 Issue 跟踪系统记录根因，防止问题被遗忘。这是一种**止血措施**，目标是让主干构建恢复绿色，后续专项修复。

---

## 常见误区

**误区一：重跑通过了就代表没问题**  
许多团队配置 CI 为"失败时自动重跑，重跑通过则标记为成功"。这会掩盖不稳定测试的存在，让问题越积越多。正确做法是在重跑通过的同时，**记录该次运行为疑似 Flaky**，并推送到专门的监控看板，每周进行人工评审和修复排期。

**误区二：不稳定测试是测试代码写得差，与被测代码无关**  
约 **20%** 的不稳定测试根因实际上是**被测代码本身的并发 Bug**。测试通过 Mock 隔离后变得稳定，并不意味着原始问题消失，而是被掩盖了。遇到并发相关的 Flaky Test 时，需要同时审查被测代码的线程安全性，而不仅修改测试断言逻辑。

**误区三：删除不稳定测试比修复它更合理**  
Flaky Test 在被修复之前，其覆盖的功能路径仍然具有测试价值。直接删除会造成覆盖率盲区。正确流程是：隔离 → 分析根因 → 修复 → 重新纳入流水线，而非直接删除。Google 内部数据显示，被修复的 Flaky Test 中有 **37%** 此前捕获过至少一次真实的生产 Bug。

---

## 知识关联

学习不稳定测试需要先理解**测试隔离原则**——每个测试用例应当独立设置（Setup）和清理（Teardown）自身状态，这是 TDD 中 F.I.R.S.T 原则中 "I（Independent，独立性）" 的直接体现。理解了隔离原则，才能诊断出测试顺序依赖和状态污染这两类最常见的 Flaky 根因。

掌握不稳定测试的诊断与修复后，自然衔接到**测试替身（Test Double）**的深入学习——包括 Mock、Stub、Spy、Fake 的精确区分与正确使用。不稳定测试中因外部依赖引发的问题，绝大多数需要通过合理引入测试替身来根治，而不是调整重试逻辑来回避。