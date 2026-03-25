---
id: "qa-at-test-reporting"
concept: "测试报告"
domain: "game-qa"
subdomain: "automation-testing"
subdomain_name: "自动化测试"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 测试报告

## 概述

测试报告是自动化测试执行完毕后，将测试结果以结构化、可视化方式呈现的输出文档。在游戏QA自动化流水线中，测试报告的核心价值在于将数百条用例的通过/失败状态、执行耗时、错误堆栈信息聚合为可供团队快速决策的数据视图，而不是让工程师逐行翻阅原始日志。

测试报告标准化的历史可追溯到2001年JUnit引入XML格式报告模板。JUnit的`<testsuite>`和`<testcase>`标签结构至今仍是CI/CD工具（如Jenkins、GitHub Actions）读取测试结果的通用格式。现代游戏QA领域更多采用HTML或Allure这类富交互报告框架，能够嵌入截图、录屏和性能曲线，使报告从"通知结果"升级为"诊断工具"。

测试报告在多机并行执行之后尤为关键。当测试用例分布在8台机器上并发运行时，单台机器只有部分结果，报告聚合层负责将所有分片结果合并，计算全局通过率（Pass Rate），并以趋势折线图展示连续多个构建版本中失败用例数的变化，帮助团队判断某次提交是否引入了回归缺陷。

---

## 核心原理

### 报告数据结构与字段定义

标准JUnit XML格式的最小有效报告包含以下必填字段：

```xml
<testsuite name="GameLoginTest" tests="50" failures="3" errors="1" time="42.7">
  <testcase name="testLoginWithValidCredentials" classname="LoginSuite" time="0.85">
    <failure message="Assert error">Expected HP=100, got HP=0</failure>
  </testcase>
</testsuite>
```

- `tests`：本次执行的总用例数
- `failures`：断言失败数（逻辑错误，用例运行完毕但结果不符预期）
- `errors`：异常错误数（用例执行中途抛出未捕获异常）
- `time`：整个测试套件的总耗时（秒）

`failures`与`errors`的区别直接影响缺陷定级：failure通常指游戏逻辑Bug，error则可能是测试环境问题或脚本本身的缺陷，两者在报告中必须分开统计。

### 通过率与趋势分析

通过率公式为：

**Pass Rate = (tests - failures - errors - skipped) / tests × 100%**

单次通过率的绝对值意义有限，趋势才是关键指标。游戏项目通常在报告系统中维护一条**基线通过率**（Baseline Pass Rate），例如设定为95%。若某次构建的通过率跌破基线，报告系统触发报警通知，阻断该版本进入下一阶段集成测试。

Allure报告框架额外提供了**缺陷重试率**（Retry Rate）维度：若某条用例连续3次执行中有2次失败、1次通过，Allure将其标记为"Flaky"（不稳定用例），并在报告仪表盘中单独列出。游戏QA中Flaky测试高发于依赖网络延迟或帧率波动的场景，必须在报告中隔离显示，避免污染整体通过率数据。

### 报告中的附件与上下文信息

优质测试报告不仅包含布尔型的通过/失败，还应附加失败时的上下文证据：

- **截图**：失败发生时游戏界面的瞬间快照，Selenium/Appium均支持在`onTestFailure`回调中自动截图并附加到报告节点
- **日志片段**：失败用例前后各50行的控制台输出，帮助定位是崩溃前的内存错误还是逻辑判断错误
- **性能数据**：帧率（FPS）、内存占用的时序曲线，尤其在游戏性能回归测试中，报告需要将帧率曲线嵌入对应测试步骤

---

## 实际应用

**战斗系统回归测试报告**：某款手游每次服务端版本更新后，触发包含320条战斗逻辑用例的自动化套件。报告按功能模块分组，分别展示"技能伤害计算""Buff叠加逻辑""掉落物生成"三个子套件的通过率。上次版本更新中，报告显示"Buff叠加逻辑"子套件通过率从98%骤降至61%，精确定位到17条失败用例均涉及同类型Buff叠加上限的边界判断，使开发团队在30分钟内锁定Bug根因。

**多平台并行报告合并**：游戏同时运行在iOS 16、Android 13、PC三个平台的并行测试后，Allure的`allure generate --clean ./allure-results`命令将三个平台各自输出的JSON结果文件合并为一份HTML报告，并以平台标签（Tag）维度展示各平台的差异化失败用例，这对于定位平台特定Bug（如仅在iOS上复现的渲染问题）至关重要。

**每日构建趋势看板**：Jenkins的JUnit趋势插件从最近30次构建的XML报告中提取失败数，生成折线图。游戏QA团队设置规则：若连续3个构建失败用例数呈上升趋势，自动向Slack频道推送警报，无需人工每天检查报告。

---

## 常见误区

**误区一：通过率100%等于质量达标**

测试报告显示通过率100%时，团队容易产生"测试已覆盖所有问题"的错误认知。实际上，高通过率可能源于测试用例本身覆盖不足，或断言条件过于宽松（例如只断言接口返回200状态码，而未验证返回的游戏角色数据内容）。报告应结合代码覆盖率数据（Coverage Report）一起查阅，仅凭通过率无法评估测试设计质量。

**误区二：将Flaky用例直接标记为Pass忽略**

部分团队为维持高通过率的"好看数字"，将不稳定用例设置为自动重试3次后只要1次通过即计为成功。这会导致报告掩盖真实的不稳定问题。Flaky用例背后往往是游戏逻辑中存在竞争条件（Race Condition）或测试环境配置缺陷，应在报告中单独追踪其重试率，而非将其折算为通过状态。

**误区三：把报告生成耗时计入测试执行时间**

Allure报告在处理含大量截图的大型套件时，`allure generate`步骤本身可能消耗30~60秒。若将这段时间混入测试执行总时长上报，会错误抬高每条用例的平均耗时，干扰并行执行效率的优化判断。报告生成应作为独立的Pipeline步骤，与测试执行步骤分开计时。

---

## 知识关联

测试报告直接依赖**并行执行**阶段的产出：并行执行将测试用例分片到多个Worker上运行，每个Worker输出独立的结果文件（JUnit XML或Allure JSON），报告模块的首要任务是将这些分片结果合并。并行执行的分片策略不合理（例如某个Worker分到了所有慢用例）会导致报告中出现Worker耗时严重不均衡的问题，可通过报告中的"用例耗时分布直方图"发现并反馈给调度层优化。

学习测试报告之后，下一个概念**Mock与Stub**解决的是让测试用例在脱离真实游戏服务器的情况下独立运行的问题。理解测试报告中`errors`字段频繁出现"Connection Refused"或"Timeout"类错误后，团队会自然产生"如何消除测试对外部依赖"的需求，这正是引入Mock与Stub技术的出发点——通过Mock掉服务端接口，使每条用例的失败原因只可能来自游戏客户端逻辑本身，让报告中的失败信息更加纯粹、可信。