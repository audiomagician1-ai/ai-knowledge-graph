---
id: "logging-basics"
concept: "日志基础"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["logging", "debug", "structured-log"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 日志基础

## 概述

日志（Logging）是程序运行时将状态信息、事件记录和错误详情写入持久化存储的机制，与 `print()` 调试的本质区别在于：日志支持等级过滤、格式化输出、多目标路由（控制台/文件/远程服务），且在生产环境中可以不修改代码地动态调整输出详细程度。Python 标准库的 `logging` 模块自 Python 2.3 起就已内置，而 Node.js 生态则广泛使用 Winston 或 Pino 库。

日志记录的历史可以追溯到1980年代的 Unix syslog 协议（RFC 3164，2001年正式标准化），它定义了 0–7 八个严重级别，现代日志框架的等级体系均源于此。对 AI 工程而言，日志不仅用于排查推理错误，更是追踪模型调用延迟、token 消耗和数据管道吞吐量的核心工具——没有结构化日志，就无法对线上模型服务做有意义的性能分析。

## 核心原理

### 日志等级（Log Levels）

Python `logging` 模块定义了五个标准等级，对应的数值为：`DEBUG=10`、`INFO=20`、`WARNING=30`、`ERROR=40`、`CRITICAL=50`。只有等级数值 **大于等于** Logger 当前设定阈值的消息才会被处理。开发环境通常设为 `DEBUG`，生产环境设为 `WARNING` 或 `INFO`，这样可以在不重启服务的情况下通过修改配置文件切换日志详细程度。

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("模型输入 token 数: %d", input_tokens)   # 开发时可见
logger.info("推理完成，耗时 %.2f 秒", elapsed)
logger.warning("上下文长度接近上限: %d/4096", ctx_len)
logger.error("API 调用失败: %s", str(e))
```

使用 `logger.getLogger(__name__)` 而非直接用 `logging.warning()` 的原因是：前者以模块路径作为 Logger 名称（如 `my_project.inference.engine`），可以在层级上独立控制每个模块的日志等级，而后者始终操作根 Logger。

### 日志格式化（Formatting）

`logging.Formatter` 通过格式字符串控制每条日志的输出结构。一个完整的格式示例：

```python
fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
formatter = logging.Formatter(fmt, datefmt="%Y-%m-%dT%H:%M:%S")
```

`%(levelname)-8s` 中的 `-8` 表示左对齐、宽度为8字符，使多行日志对齐便于阅读。`%(asctime)s` 默认精度到秒，若需要毫秒级时间戳需改为 `datefmt="%Y-%m-%dT%H:%M:%S.%f"`（`%f` 是微秒，取前三位即毫秒）。对 AI 推理服务来说，毫秒级时间戳至关重要，因为单次 LLM 调用可能只需 200ms，秒级精度会淹没所有延迟信息。

### 结构化日志（Structured Logging）

结构化日志将日志输出为 JSON 等机器可解析格式，而非纯文本字符串。这使得 Elasticsearch、Loki 等日志聚合系统可以按字段查询（例如：`model_id="gpt-4" AND latency_ms > 500`），而纯文本日志只能做正则匹配。

Python 中使用 `python-json-logger` 库实现结构化日志：

```python
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
))
logger.addHandler(handler)

# 通过 extra 参数附加结构化字段
logger.info("推理完成", extra={
    "model_id": "gpt-4o",
    "latency_ms": 342,
    "input_tokens": 512,
    "output_tokens": 128
})
```

输出结果为一行 JSON：`{"asctime": "2024-01-15T10:23:45", "levelname": "INFO", "model_id": "gpt-4o", "latency_ms": 342, ...}`，每个字段均可索引查询。

### Handler 与 Logger 的分离

Logger 本身不决定日志写到哪里，这由 Handler 负责。`StreamHandler` 写到控制台，`FileHandler` 写到文件，`RotatingFileHandler` 在文件达到指定大小（如 10MB）时自动轮转并保留最近 N 个备份文件。一个 Logger 可以同时挂载多个 Handler，例如 DEBUG 以上写文件、ERROR 以上发送到告警系统，二者互不干扰。

## 实际应用

**AI 模型服务的日志实践**：在封装 OpenAI API 调用时，标准做法是在请求前记录 `INFO` 级别的模型参数（model、temperature、max_tokens），在请求后记录实际耗时和 token 用量，在捕获异常时记录 `ERROR` 并包含完整的请求 ID（`request_id`），便于关联用户反馈与后端日志。

**数据管道中的日志**：处理训练数据时，每处理 1000 条样本记录一次进度（`INFO`），遇到格式异常的样本记录 `WARNING` 并附上样本索引，而不是直接抛出异常中断整个流程——这正是日志与 `try/catch` 配合使用的典型场景：`except` 块捕获异常后调用 `logger.warning()` 记录问题，然后 `continue` 跳过该样本继续处理。

**避免在日志中泄露敏感数据**：用户输入、API Key、个人信息绝不能以 `DEBUG` 级别完整记录。正确做法是对敏感字段做截断（如只记录 API Key 的前8位）或哈希处理。

## 常见误区

**误区一：用 `print()` 替代日志**。`print()` 没有等级过滤，在生产环境中要么全部关闭（需要逐一删除）、要么全部输出（产生噪音）。而 `logging` 只需修改根 Logger 的等级即可一键静音所有 `DEBUG` 消息，不需要改动任何业务代码。

**误区二：在日志消息中使用 f-string 拼接**。`logger.debug(f"输入数据: {large_object}")` 即便该 `DEBUG` 消息因等级过滤不会被输出，`large_object` 的字符串化（`__str__`）**仍然会执行**，造成不必要的性能开销。正确写法是 `logger.debug("输入数据: %s", large_object)`，`logging` 模块只在确认消息会被输出时才执行格式化。

**误区三：一个模块只用一个全局 Logger**。在大型项目中应为每个模块创建独立的 Logger（`getLogger(__name__)`），这样可以精确控制某个噪音模块（如第三方库）的日志等级，而不影响自己代码的日志输出。

## 知识关联

日志基础直接依赖**错误处理（try/catch）**：`except` 块是调用 `logger.error()` 或 `logger.exception()`（自动附加堆栈跟踪）的主要场景，二者共同构成生产环境错误可观测性的完整链条。`logger.exception()` 与 `logger.error()` 的区别在于前者会自动调用 `traceback.format_exc()` 将完整堆栈附加到日志中，无需手动处理。

**调试基础**中学到的断点调试适用于本地开发，而日志是其在生产环境中的替代品——线上服务无法附加调试器，只能依靠日志重现问题现场。理解这一互补关系有助于判断何时用断点、何时在代码中预埋日志点。

掌握结构化日志后，自然引出**可观测性（Observability）**体系中的 Metrics 和 Tracing 概念：日志记录离散事件，Metrics 聚合连续指标（如 QPS、P99延迟），Tracing 追踪跨服务请求链路——三者合称"可观测性三支柱"，而结构化日志中的 `trace_id` 字段是打通日志与 Tracing 系统的关键纽带。