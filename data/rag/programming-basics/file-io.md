---
id: "file-io"
concept: "文件I/O"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["file", "read", "write", "stream"]

# Quality Metadata (Schema v2)
content_version: 4
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

# 文件I/O

## 概述

文件I/O（File Input/Output）是指程序与磁盘文件之间进行数据交换的操作机制，具体包括从文件读取字节或字符序列（输入），以及将数据写入文件并持久化到磁盘（输出）。与内存中的变量不同，文件数据在程序退出后依然存在，这使得文件I/O成为AI工程中保存训练数据、模型权重、日志记录和配置文件的基础手段。

文件I/O操作的概念可追溯到UNIX系统1969年的设计哲学："一切皆文件"（Everything is a file），该哲学将普通文件、目录、设备统一抽象为文件描述符（file descriptor）进行操作。Python在此基础上提供了内置的`open()`函数，其签名为`open(file, mode='r', encoding=None, buffering=-1)`，通过`mode`参数区分读（`'r'`）、写（`'w'`）、追加（`'a'`）和二进制（`'b'`）等模式。

在AI工程实践中，文件I/O的重要性体现在：一个典型的深度学习项目需要读取GB级别的训练语料、逐行解析CSV标注文件、保存`.pkl`或`.npy`格式的中间特征，以及实时追加训练日志。不掌握文件I/O，就无法处理任何超出内存限制的真实数据集。

---

## 核心原理

### 文件打开与关闭：`open()`与上下文管理器

调用`open()`后，操作系统会为该文件分配一个文件描述符，并在内核中建立文件表项记录当前读写位置（称为**文件指针**，file pointer）。每个进程默认最多可同时持有1024个文件描述符（Linux默认值，可通过`ulimit -n`查看），若不及时关闭文件，会造成描述符泄漏。

Python推荐使用`with`语句（上下文管理器）确保文件自动关闭：

```python
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()
# 离开with块后，即使发生异常，f.close()也会被自动调用
```

这等价于在`finally`块中调用`f.close()`，但代码更简洁。直接使用`f = open(...)`而不搭配`with`或`try/finally`，是AI工程代码中最常见的资源泄漏来源之一。

### 读取模式：整体读取 vs 逐行读取 vs 流式处理

文件读取有三种粒度，选择错误会直接导致内存溢出（OOM）：

| 方法 | 行为 | 适用场景 |
|------|------|---------|
| `f.read()` | 一次性读取全部内容到字符串 | 小文件（<100 MB） |
| `f.readlines()` | 将所有行读入列表 | 需要随机访问行号时 |
| `for line in f` | 逐行迭代，每次只保留一行在内存 | 大文件、流式处理 |

对于AI工程中常见的500万行训练数据文件，使用`readlines()`会将全部内容加载到内存，可能消耗数GB RAM；而使用`for line in f`迭代，内存占用始终约为单行大小（通常几百字节）。这种**流式读取**（streaming read）是处理超大语料库的标准做法。

`f.read(size)`可指定每次读取的字节数，例如`f.read(4096)`以4KB块读取，适合处理二进制文件（如模型权重的`.bin`文件）。

### 路径处理：`pathlib`与`os.path`

硬编码路径字符串（如`"/home/user/data.csv"`）是跨平台兼容性问题的根源，因为Windows使用反斜杠`\`而UNIX使用正斜杠`/`。Python 3.4引入的`pathlib.Path`类通过运算符重载解决了这一问题：

```python
from pathlib import Path

data_dir = Path("datasets") / "train" / "labels.csv"
# 等价于 "datasets/train/labels.csv"（自动适配操作系统分隔符）

print(data_dir.suffix)   # 输出: .csv
print(data_dir.stem)     # 输出: labels
print(data_dir.parent)   # 输出: datasets/train
data_dir.parent.mkdir(parents=True, exist_ok=True)  # 递归创建目录
```

`Path.glob("*.json")`可批量匹配文件，`Path.stat().st_size`返回文件字节大小，这两个方法在AI工程的数据预处理脚本中极为常用。

### 二进制模式与文本模式的本质区别

以`'r'`（文本模式）打开文件时，Python会自动进行换行符转换（Windows的`\r\n`→`\n`）并按`encoding`参数解码字节为Unicode字符串。以`'rb'`（二进制模式）打开时，Python返回原始`bytes`对象，不做任何转换。

读取NumPy的`.npy`文件、PyTorch的`.pt`文件或任何非文本格式，必须使用二进制模式：

```python
with open("model_weights.pt", "rb") as f:
    raw_bytes = f.read()  # 返回bytes，不是str
```

混淆两种模式是初学者常见错误：用文本模式打开PNG图片会因编码错误抛出`UnicodeDecodeError`。

---

## 实际应用

**场景一：逐行解析AI训练数据集**

处理JSONL格式（每行一个JSON对象，是Hugging Face数据集的常见格式）的大型语料库：

```python
import json
from pathlib import Path

def iter_jsonl(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"第{line_num}行解析失败: {e}")

for record in iter_jsonl("train_data.jsonl"):
    text = record["text"]
    # 后续处理...
```

这段代码结合了流式读取、路径处理和错误处理，是AI数据管道的典型模式。

**场景二：写入训练日志**

```python
with open("training_log.txt", "a", encoding="utf-8") as log_file:
    log_file.write(f"Epoch 5/100, Loss: 0.3421, Acc: 87.3%\n")
```

使用追加模式`'a'`而非`'w'`，保证每次运行不会覆盖历史记录。

---

## 常见误区

**误区一：认为`write()`会立即将数据写入磁盘**

调用`f.write()`实际上是将数据写入操作系统的**页缓存**（page cache），而非直接落盘。程序崩溃时，缓存中未刷新的数据会丢失。如需强制写入磁盘，需调用`f.flush()`（刷入内核缓冲区）再调用`os.fsync(f.fileno())`（强制落盘）。训练关键检查点时忽略这一点，可能导致模型文件损坏。

**误区二：用`'w'`模式打开已有文件时没有意识到文件被清空**

`open("results.csv", "w")`会在打开瞬间将文件截断为0字节，即使后续代码因错误未写入任何内容，原始数据也已永久丢失。正确做法是先写入临时文件，成功后再重命名（原子操作）：

```python
import os
with open("results_tmp.csv", "w") as f:
    f.write(data)
os.replace("results_tmp.csv", "results.csv")  # 原子替换
```

**误区三：混淆相对路径的基准目录**

`open("data/train.csv")`中的相对路径是相对于**当前工作目录**（`os.getcwd()`），而非脚本文件所在目录。当从不同目录调用脚本时，路径会失效。正确做法是以脚本的`__file__`属性为锚点：

```python
BASE_DIR = Path(__file__).parent
data_path = BASE_DIR / "data" / "train.csv"
```

---

## 知识关联

文件I/O建立在**错误处理（try/except）**之上：`FileNotFoundError`（文件不存在）、`PermissionError`（无读写权限）和`UnicodeDecodeError`（编码不匹配）是文件操作中最频繁出现的三类异常，必须通过异常捕获妥善处理。同时，文件I/O依赖**文件系统**概念（目录树、权限、绝对/相对路径）来理解路径操作的语义。

掌握文件I/O后，直接衔接的下一个主题是**数据序列化**：当需要将Python的字典、列表或NumPy数组持久化到文件时，`pickle`（二进制序列化）、`json`（文本序列化）和`numpy.save`（`.npy`格式）等序列化工具本质上都是对文件I/O的高层封装——它们负责将Python对象转换为字节序列，再通过`'wb'`模式的文件写入保存到磁盘。