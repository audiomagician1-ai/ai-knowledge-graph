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
quality_tier: "pending-rescore"
quality_score: 43.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 日志基础

## 概述

日志（Logging）是程序运行时将状态信息、事件和错误写入持久化记录的技术。与 `print()` 调试不同，日志系统提供等级过滤、时间戳、来源定位和多目标输出能力，使开发者无需修改代码即可控制输出粒度。Python 标准库中的 `logging` 模块自 Python 2.3（2003年）起内置，遵循 PEP 282 规范，是 AI 工程中追踪模型训练进度、记录推理延迟和捕获数据管道异常的基础工具。

日志区别于普通调试输出的关键在于其**持久性**和**可查询性**。一个深夜崩溃的训练任务不能靠事后打断点重现，但如果日志记录了每个 epoch 的 loss 值、学习率衰减时间点和 GPU 内存占用，工程师可以在事后完整还原故障现场。正因如此，生产环境中的 AI 系统必须在代码上线前就设计好日志策略，而不是出了问题再补。

## 核心原理

### 日志等级体系

Python `logging` 模块定义了五个标准等级，数值越高表示越严重：

| 等级 | 数值 | 典型用途 |
|------|------|----------|
| DEBUG | 10 | 模型参数形状、中间张量值 |
| INFO | 20 | epoch 完成、数据集加载成功 |
| WARNING | 30 | 学习率接近下限、验证集缺少标签 |
| ERROR | 40 | 批次处理失败、文件读取异常 |
| CRITICAL | 50 | 模型文件损坏、GPU 不可用 |

设置 `logger.setLevel(logging.INFO)` 后，所有 DEBUG 消息会被静默丢弃，而 INFO 及以上等级才会输出。这意味着开发阶段可将等级设为 DEBUG 获取详细信息，生产部署时切换到 WARNING 减少 I/O 开销，**无需改动任何业务代码**。

### 格式化：让日志可读且可解析

一条格式糟糕的日志形如 `loss下降了`，无法告诉你是哪个脚本、哪一行、什么时间发生的。推荐格式使用 `Formatter` 配置：

```python
import logging

formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

`%(asctime)s` 输出人类可读时间戳，`%(name)s` 记录 logger 名称（通常用模块名 `__name__`），`%(lineno)d` 精确定位代码行号。这三个字段组合后，一条 ERROR 日志会呈现为：

```
2024-03-15 02:17:43 | ERROR    | trainer:156 | Batch 4820 failed: CUDA out of memory
```

### 结构化日志：从文本到可查询数据

纯文本日志难以用程序批量分析。**结构化日志**将每条记录输出为 JSON 格式，使日志本身成为结构化数据：

```python
import json, logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
            # 附加上下文字段
            **getattr(record, 'extra', {})
        }
        return json.dumps(log_obj, ensure_ascii=False)
```

在 AI 工程场景中，可通过 `extra` 参数携带 `epoch`、`batch_id`、`loss` 等字段，之后用 `jq` 命令或 Elasticsearch 直接过滤出所有 loss > 2.0 的训练步骤，而无需写正则表达式解析文本。

### Handler：控制日志写往何处

单个 Logger 可以同时挂载多个 Handler，实现一次记录、多处输出：

```python
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 控制台只显示 WARNING 以上
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)

# 文件记录所有 DEBUG 信息
file_handler = logging.FileHandler('training.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
```

每个 Handler 可以独立设置等级和 Formatter，这是日志系统比 `print()` 灵活的核心机制之一。

## 实际应用

**AI 模型训练监控**：在每个 epoch 结束时用 INFO 记录 `train_loss`、`val_loss` 和耗时；用 WARNING 记录梯度爆炸（`grad_norm > 10.0`）；用 ERROR 捕获 `try/except` 中的数据预处理异常并记录出错的文件路径。结合结构化日志后，可用一行 shell 命令 `grep '"level": "ERROR"' training.log | wc -l` 统计整个训练过程的错误批次数量。

**数据管道调试**：在 ETL 流程中对每个数据源配置独立的 Logger（名称为 `pipeline.source_name`），利用 Logger 的层级继承关系（子 logger 自动向父 logger 传播消息），既能用 `logging.getLogger('pipeline')` 统一控制整个管道的输出，也能单独调低某个数据源的等级进行精细调试。

**FastAPI / Flask 服务集成**：在 AI 推理服务中，对每次请求记录 `request_id`、输入长度和推理耗时（毫秒级），用于定位 P99 延迟异常，这些字段通过结构化日志的 `extra` 参数注入，不影响业务逻辑代码的可读性。

## 常见误区

**误区一：用 `print()` 替代日志系统就够了**
`print()` 输出没有等级、没有时间戳、没有来源信息，且无法重定向到文件或监控系统。更关键的是，在多进程训练（如 PyTorch DDP）场景中，多个进程的 `print()` 输出会交错混乱，而 `logging` 模块内部使用线程锁保证写入原子性，并可通过 `RotatingFileHandler` 自动分割超过指定大小（如 10MB）的日志文件。

**误区二：日志记录越详细越好，全用 DEBUG 等级**
在紧密循环（如每个训练 batch）中记录大量 DEBUG 信息会产生严重的 I/O 瓶颈。实测在 100 iterations/s 的训练任务中，向磁盘写入每条 200 字节的 DEBUG 日志可将吞吐量降低 15-30%。正确做法是将高频事件的日志等级设为 DEBUG 并在生产中禁用，仅对关键里程碑（每 100 个 batch、每个 epoch）使用 INFO 记录汇总指标。

**误区三：在模块顶层调用 `logging.basicConfig()` 多次**
`logging.basicConfig()` 只有在 root logger 没有 handler 时才生效，多次调用后续的调用会被静默忽略。这导致不同模块尝试配置日志但实际生效的只有第一次调用，产生难以排查的配置冲突。正确做法是在程序入口（`main.py` 或 `__init__.py`）统一调用一次，各子模块只用 `logging.getLogger(__name__)` 获取 logger。

## 知识关联

日志基础以**错误处理（try/except）**为前提：`except` 块捕获到异常后，应用 `logger.error("message", exc_info=True)` 记录完整的堆栈跟踪（`exc_info=True` 参数会自动附加 traceback），而不是将异常静默吞掉或仅 `print(e)`。`exc_info` 参数使日志记录与异常处理的边界清晰：try/except 负责控制流，logger 负责可观测性。

从**调试基础**迁移到日志的核心转变是：调试器（debugger）是开发时交互式工具，日志是运行时被动记录工具。在无法连接调试器的远程训练集群或容器环境中，精心设计的日志是唯一的"眼睛"。掌握日志基础后，可进一步学习分布式追踪（如 OpenTelemetry）和指标监控（如 Prometheus），这些系统均以结构化日志的设计理念为基础，将可观测性从单机扩展到微服务架构。
