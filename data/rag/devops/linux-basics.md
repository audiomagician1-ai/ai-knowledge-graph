---
id: "linux-basics"
concept: "Linux基础命令"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 2
is_milestone: false
tags: ["运维"]

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
updated_at: 2026-03-26
---



# Linux基础命令

## 概述

Linux基础命令是在Linux操作系统的Bash（Bourne Again Shell，1989年由Brian Fox为GNU项目开发）或其他Shell环境中直接输入、立即执行的单行指令集合。与图形界面操作不同，这些命令通过标准输入（stdin，文件描述符0）接受参数，将结果输出到标准输出（stdout，文件描述符1），并将错误信息发送至标准错误（stderr，文件描述符2）。

Linux命令按来源分为两类：内建命令（built-in）和外部命令。`cd`、`echo`、`exit`等内建命令直接由Shell解释器处理，不需要创建子进程；而`ls`、`grep`、`awk`等外部命令实际上是存储在`/bin`、`/usr/bin`等目录中的可执行文件，Shell通过`fork()`系统调用创建子进程来运行它们。使用`type ls`可以检查某个命令属于哪类。

在AI工程的开发运维场景中，工程师每天需要在远程Linux服务器（通常是Ubuntu 20.04/22.04 LTS或CentOS 7/8）上管理训练任务、查看GPU占用、传输数据集、排查进程崩溃等，熟练使用Linux基础命令能将原本需要数分钟的排障时间压缩到数秒。

---

## 核心原理

### 文件系统导航与操作

Linux使用单一的目录树结构，根目录`/`是所有路径的起点，遵循FHS（Filesystem Hierarchy Standard）规范。`pwd`打印当前工作目录的绝对路径；`ls -lh`以人类可读格式（KB/MB/GB）列出文件详情，`-a`参数额外显示以`.`开头的隐藏文件（如`.bashrc`、`.env`）。

文件操作的五个核心命令形成完整的增删改查链路：
- `cp -r src/ dst/`：递归复制目录，`-p`参数保留文件的时间戳和权限
- `mv old new`：既可重命名文件，也可跨目录移动，底层使用`rename()`系统调用（同分区）或`copy+unlink`（跨分区）
- `rm -rf dir/`：**不可逆删除**，`-f`跳过确认，`-r`递归删除目录
- `mkdir -p a/b/c`：`-p`参数允许一次性创建多级嵌套目录
- `find /data -name "*.pt" -mtime -1`：在`/data`目录下查找过去24小时内修改过的`.pt`模型文件

### 文本处理三剑客

`grep`、`sed`、`awk`是Linux文本处理的黄金组合，在AI工程中常用于解析训练日志。

`grep -n "loss" train.log`：在训练日志中定位所有含"loss"的行并显示行号；`grep -E "epoch [0-9]+"` 使用扩展正则表达式匹配epoch信息；`grep -c "ERROR"` 直接统计错误行数。

`awk '{print $3, $5}' train.log`：按列提取数据，`$0`表示整行，`$NF`表示最后一列；`awk 'NR%100==0 {print NR, $0}'` 每隔100行采样一次，用于快速浏览长日志。

`sed -i 's/learning_rate=0.01/learning_rate=0.001/g' config.yaml`：`-i`参数直接修改原文件，`s/旧/新/g`替换所有匹配项，批量修改实验配置时极为高效。

### 进程与系统资源监控

`ps aux`输出当前所有进程的快照，其中`a`显示所有用户的进程，`u`以用户为导向的格式，`x`包含无终端的后台进程；配合`grep python`可快速找到训练脚本的PID（进程ID）。

`top`提供动态实时视图，默认每3秒刷新，按`P`键按CPU使用率降序排列，按`M`键按内存使用率排列，按`k`键输入PID可发送信号终止进程。`kill -9 PID`发送SIGKILL信号（编号9）强制终止无响应的训练进程，而`kill -15 PID`（SIGTERM）则是请求进程优雅退出。

`df -h`显示所有已挂载文件系统的磁盘使用情况；`du -sh /data/datasets/*`统计数据集目录中每个子目录的大小，帮助定位磁盘占用过高的来源。`free -m`以兆字节为单位显示内存总量、已用量和可用量。

### 权限与用户管理

Linux权限使用9位rwx模式（`rwxr-xr-x`）表示，前3位是所有者权限，中间3位是组权限，最后3位是其他用户权限，对应八进制数字为`chmod 755 script.sh`。`chmod +x run.sh`为训练启动脚本添加可执行权限是最常见操作。`chown user:group file`更改文件归属，在多人共享GPU服务器上管理数据集权限时必用。

---

## 实际应用

**场景一：下载并解压大型数据集**
```bash
wget -c https://example.com/imagenet.tar.gz -O /data/imagenet.tar.gz
tar -xzvf /data/imagenet.tar.gz -C /data/
```
`wget -c`的`-c`参数支持断点续传，对动辄几十GB的AI数据集至关重要；`tar -xzvf`中`x`解压、`z`处理gzip压缩、`v`显示进度、`f`指定文件名。

**场景二：后台运行训练任务并记录日志**
```bash
nohup python train.py > train.log 2>&1 &
echo $!
```
`nohup`使进程在终端关闭后继续运行，`2>&1`将stderr重定向合并到stdout，`&`放入后台，`$!`打印刚才启动的后台进程PID，方便后续用`kill`管理。

**场景三：实时监控训练loss**
```bash
tail -f train.log | grep --line-buffered "val_loss"
```
`tail -f`持续跟踪文件新增内容，`--line-buffered`确保`grep`逐行刷新输出而非等待缓冲区满，两者通过管道`|`连接，实现对验证集loss的实时追踪。

---

## 常见误区

**误区一：混淆`>`与`>>`重定向符号**  
`>`是覆盖重定向，每次执行`python eval.py > result.txt`都会清空`result.txt`重新写入；`>>`是追加重定向，适合将多次实验结果累积记录。在跑多组超参数实验时误用`>`会导致前几组结果永久丢失。

**误区二：在根目录执行`rm -rf *`**  
当前目录不是预期目录时（例如以为在`/data/tmp`实际在`/`），`rm -rf *`会删除整个文件系统中当前用户有权限的所有文件。正确习惯是执行删除前先用`pwd`确认位置，并优先使用完整绝对路径如`rm -rf /data/tmp/*`。

**误区三：`kill -9`是终止进程的首选**  
SIGKILL（-9）会立即强制终止进程，PyTorch的DDP训练进程或TensorFlow会话来不及保存checkpoint和释放共享内存（`/dev/shm`），可能导致下次启动时资源泄漏或checkpoint损坏。正确做法是先`kill -15`（SIGTERM）等待5-10秒，进程未退出再使用`-9`。

---

## 知识关联

Linux基础命令直接依赖**命令行基础**中建立的概念：路径（绝对路径vs相对路径）、工作目录、输入输出重定向和管道符`|`的工作方式——若不理解`|`将前一命令的stdout连接到下一命令的stdin，`grep | awk | sort`这类复合命令就无从理解。

掌握Linux基础命令后，下一步学习**Shell脚本**时，`for`循环批量提交训练任务、`if`判断GPU是否空闲等脚本逻辑，本质上是将本文的单行命令组合编排成可复用的自动化流程。学习**Docker基础**时，`docker exec -it container bash`进入容器后的操作完全依赖Linux命令；`docker cp`、`docker volume`的底层也是Linux的文件系统操作。在**日志聚合**场景中，将分散服务器上的日志汇总到ELK（Elasticsearch-Logstash-Kibana）栈之前，`grep`、`awk`、`sed`的本地预处理能力决定了日志清洗和字段提取的效率上限。