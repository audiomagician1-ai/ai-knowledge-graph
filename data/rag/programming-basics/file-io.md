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
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 文件I/O

## 概述

文件I/O（File Input/Output）是指程序与磁盘文件之间进行数据交换的操作集合，包括打开文件、读取内容、写入数据和关闭句柄四个基本步骤。与内存中的变量不同，文件I/O操作的数据在程序退出后仍然持久存在，这使其成为AI工程中保存模型权重、读取训练数据集、记录实验日志的基础手段。

文件I/O的概念源于早期操作系统的"一切皆文件"设计哲学，Unix系统在1969年将设备、管道、网络套接字统一抽象为文件描述符（File Descriptor），用整数0、1、2分别代表标准输入、标准输出和标准错误。现代Python的`open()`函数内部同样依赖操作系统提供的文件描述符机制，在Linux上可通过`/proc/self/fd/`目录直接观察当前进程打开的所有文件句柄。

在AI工程场景中，一个典型的ImageNet数据集包含超过1400万张图片，单次全量读入内存完全不可行，必须依赖流式文件I/O逐批加载。正确掌握文件I/O不仅关乎功能实现，还直接影响数据管道的吞吐量和内存占用，是构建高效训练循环的前提。

## 核心原理

### 文件打开模式与编码

Python的`open()`函数接受`mode`参数控制读写行为，常用模式包括：`'r'`（只读，默认）、`'w'`（覆盖写入）、`'a'`（追加）、`'b'`（二进制）、`'+'`（读写兼容）。模式可以组合使用，如`'rb'`用于读取`.npy`或`.pkl`等二进制格式，`'w+'`则在写入后仍可回读。

`encoding`参数至关重要但常被忽视。UTF-8是互联网标准，能表示Unicode全部1,114,112个码点；而Windows系统默认使用GBK/CP936编码，如果在Windows上读取Linux生成的中文CSV文件时不指定`encoding='utf-8'`，会触发`UnicodeDecodeError`。正确写法为：

```python
with open('data.txt', 'r', encoding='utf-8') as f:
    content = f.read()
```

### 上下文管理器与资源释放

使用`with`语句（上下文管理器协议）打开文件是强制要求，而非风格偏好。文件对象实现了`__enter__`和`__exit__`魔法方法，确保即使在读写过程中抛出异常，`__exit__`也会自动调用`f.close()`释放文件描述符。Linux系统默认每个进程最多同时持有1024个文件描述符（可通过`ulimit -n`查看），在并行数据加载场景下若忘记关闭文件，很快就会触发`OSError: [Errno 24] Too many open files`错误。

### 流式读取（逐行与分块）

对于大文件，有三种读取策略，其内存特征截然不同：

- `f.read()`：一次性读入全部内容为单个字符串，内存占用等于文件大小。
- `f.readlines()`：返回包含所有行的列表，内存占用同样等于文件大小。
- `for line in f`：利用文件对象的迭代器协议，每次只从内核缓冲区取出约8KB数据，内存占用接近常数。

对于二进制大文件（如视频、音频），应使用分块读取：

```python
CHUNK_SIZE = 65536  # 64KB，匹配操作系统页面大小的倍数
with open('video.mp4', 'rb') as f:
    while chunk := f.read(CHUNK_SIZE):
        process(chunk)
```

64KB的分块大小是经验值，与操作系统的4KB内存页对齐，能最大化磁盘I/O效率。

### 路径处理：`pathlib` vs `os.path`

Python 3.4引入的`pathlib.Path`对象以面向对象方式替代了字符串拼接路径，解决了Windows使用`\`、Unix使用`/`的跨平台问题。关键操作对比：

| 操作 | `os.path`（旧） | `pathlib`（推荐） |
|------|----------------|-----------------|
| 拼接路径 | `os.path.join(a, b)` | `Path(a) / b` |
| 获取文件名 | `os.path.basename(p)` | `p.name` |
| 获取后缀 | `os.path.splitext(p)[1]` | `p.suffix` |
| 判断存在 | `os.path.exists(p)` | `p.exists()` |

在AI工程中，`Path('data') / 'train' / 'images'`这样的写法比字符串拼接更清晰，且`p.glob('**/*.jpg')`可递归匹配所有JPEG文件，常用于构建数据集文件列表。

## 实际应用

**训练日志追加写入**：实验过程中需要持续记录每个epoch的loss值，使用`'a'`模式追加写入CSV文件，不会覆盖历史记录。结合`flush=True`参数或`f.flush()`调用，可强制将内核缓冲区数据立即写入磁盘，防止程序崩溃时丢失最后几行日志。

**批量读取`.npy`文件**：NumPy的`np.load('weights.npy')`底层调用的正是二进制文件I/O，以`'rb'`模式读取并解析NumPy自定义的`.npy`格式头部（魔数为`\x93NUMPY`，占6字节）。处理包含数千个分片的大型数据集时，将文件路径列表预先排序并使用`pathlib.Path.glob()`生成，可确保每次运行的数据顺序一致，保证实验可复现性。

**逐行解析大型文本语料**：处理百GB级别的NLP预训练语料（如Common Crawl子集）时，必须使用`for line in f`迭代器模式，配合`line.strip()`去除换行符后交给tokenizer处理，全程内存峰值仅为单行文本大小，不会因数据集体量增大而OOM。

## 常见误区

**误区一：混淆文本模式与二进制模式导致数据损坏**

在文本模式（`'r'`/`'w'`）下，Python会自动进行换行符转换：Windows上`\r\n`读入后变为`\n`，写出时`\n`变回`\r\n`。如果用文本模式读取`.pkl`或`.bin`文件，这种自动转换会破坏二进制数据中恰好等于`0x0D 0x0A`的字节序列，导致反序列化失败并报出难以诊断的错误。处理任何非纯文本文件必须使用`'rb'`或`'wb'`模式。

**误区二：`f.write()`完成后数据不一定已写入磁盘**

操作系统为提高性能，`write()`调用通常只是将数据写入内核的页面缓存（Page Cache），而非立即落盘。调用`f.flush()`只将Python层缓冲区推给操作系统，调用`os.fsync(f.fileno())`才会强制操作系统将页面缓存刷写到物理磁盘。对于模型检查点（checkpoint）保存，建议在`f.flush()`之后追加`os.fsync()`，否则系统断电可能导致checkpoint文件损坏。

**误区三：用字符串拼接代替`pathlib`导致跨平台路径错误**

`'data' + '/' + 'train'`在Windows上会生成无效路径，而`Path('data') / 'train'`会根据当前操作系统自动选择分隔符。更隐蔽的问题是，手动拼接的路径字符串无法直接调用`.exists()`、`.mkdir(parents=True, exist_ok=True)`等方法，导致代码中充斥着`os.path`与字符串的混用，增加维护成本。

## 知识关联

文件I/O建立在**错误处理（try/except）**之上：`FileNotFoundError`、`PermissionError`、`IsADirectoryError`是文件操作中最常见的三类异常，应针对性地捕获而非使用裸`except`。**文件系统**知识为路径的绝对/相对表示、目录遍历操作提供了底层语义支撑，理解inode机制有助于解释为何同一文件可以有多个硬链接却只有一份数据。

掌握文件I/O后，下一个学习目标是**数据序列化**：JSON、Pickle、MessagePack、Parquet等格式本质上都是将Python对象转换为字节流后，通过文件I/O写入磁盘的约定。理解`open()`的二进制模式和`io.BytesIO`内存文件对象，是进一步学习`pickle.dump(obj, f)`和`json.dump(obj, f)`的直接前提。
