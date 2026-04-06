---
id: "file-system"
concept: "文件系统"
domain: "ai-engineering"
subdomain: "cs-fundamentals"
subdomain_name: "计算机基础"
difficulty: 2
is_milestone: false
tags: ["基础", "OS"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "A"
quality_score: 82.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "academic"
    author: "Tanenbaum, A. S., & Bos, H."
    year: 2014
    title: "Modern Operating Systems (4th ed.)"
    publisher: "Pearson"
  - type: "academic"
    author: "Mathur, A., Cao, M., Bhattacharya, S., Dilger, A., Tomas, A., & Vivier, L."
    year: 2007
    title: "The new ext4 filesystem: current status and future plans"
    venue: "Proceedings of the Linux Symposium"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---

# 文件系统

## 概述

文件系统（File System）是操作系统中负责管理持久化数据存储的子系统，它定义了数据在存储介质上的组织方式、命名规则和访问方法。具体而言，文件系统将原始的磁盘扇区（sector，通常为512字节或4096字节）抽象为用户可见的"文件"和"目录"层次结构，使程序员无需关心数据实际存储在磁盘的哪个物理位置。没有文件系统，磁盘就只是一段连续的字节序列，毫无结构可言。

文件系统的历史可追溯至1960年代。IBM在OS/360（1964年）中引入了早期的文件管理概念，而Unix在1969年设计的UFS（Unix File System）奠定了现代文件系统的基本架构——inode结构、目录树、硬链接等概念均源自此处。1993年发布的ext2是Linux世界的重要里程碑，其继任者ext4（2008年正式合并入Linux 2.6.28内核）至今仍是众多Linux服务器的默认文件系统，支持单卷最大1EB（$10^{18}$ 字节）的容量。Windows则采用NTFS（New Technology File System，1993年随Windows NT 3.1推出），支持单文件最大16EB的理论容量，MFT（Master File Table）记录每个文件的完整元数据。

在AI工程领域，文件系统的重要性体现在训练数据的读取效率上。当用PyTorch 2.x或TensorFlow 2.x训练大模型时，数据加载的I/O瓶颈往往比GPU计算瓶颈更早出现。例如，在8块A100 GPU的训练节点上，每张卡的理论算力约为312 TFLOPS，若文件系统读取速度不足，GPU利用率会跌至30%以下，白白浪费昂贵的算力资源。理解文件系统的缓存机制、块大小（block size）和目录遍历开销，能帮助工程师正确配置数据预处理流水线，避免GPU空等数据的情况（Tanenbaum & Bos, 2014）。

## 核心原理

### 基本数据结构：inode与目录项

文件系统用**inode**（index node，索引节点）记录文件的元数据。一个inode包含：文件大小、权限位（rwx）、时间戳（创建/修改/访问）、数据块指针，但**不包含文件名**。文件名存储在目录项（directory entry，dentry）中，目录项是一个 $\langle\text{文件名},\ \text{inode号}\rangle$ 的映射表。这种设计使得硬链接成为可能：多个目录项可以指向同一个inode，inode中的 $\text{link\_count}$ 字段记录有多少个目录项引用它，当满足条件：

$$\text{link\_count} = 0 \;\wedge\; \text{open\_count} = 0$$

时，文件才真正被删除，操作系统才将对应数据块标记为空闲并释放空间。

在ext4中，每个inode大小默认为256字节（早期ext2为128字节，ext4扩展以支持纳秒级时间戳和扩展属性），一个文件系统的inode总数在执行 `mkfs.ext4` 格式化时确定，默认每16KB存储空间分配一个inode。这意味着即使磁盘空间充足，若inode耗尽，也无法创建新文件——在存储海量小文件（如机器学习数据集的每条样本存为独立文件）时，这是一个常见的陷阱。可通过 `df -i` 命令查看inode使用情况。

### 块分配与碎片化

文件系统以**块**（block）为单位分配存储空间，ext4默认块大小为4096字节（4KB）。即使一个文件只有1字节，也会占用一整个4KB块，这被称为**内部碎片**（internal fragmentation）。设文件实际大小为 $S$ 字节，块大小为 $B$ 字节，则实际占用磁盘空间为：

$$\text{占用块数} = \left\lceil \frac{S}{B} \right\rceil$$

由此产生的空间浪费为 $\left\lceil S/B \right\rceil \times B - S$ 字节。相反，当文件被反复修改、删除后，磁盘上空闲块分散分布，新文件的数据块无法连续存放，产生**外部碎片**（external fragmentation），读取时磁头需要频繁寻道，导致I/O性能下降。HDD的顺序读取速度（约100–200 MB/s）远高于随机读取速度（约0.5–1 MB/s），而NVMe SSD的随机读取速度（约500K IOPS）远高于HDD，使碎片化对SSD的性能影响相对较小。但在HDD上存储大量小图片文件时（例如ImageNet的128万张JPEG图片未经打包），碎片化会显著降低训练数据的读取吞吐量，实测可使吞吐量下降50%以上。

ext4通过**延迟分配**（delayed allocation）和**多块分配器**（multi-block allocator，mballoc）缓解碎片问题：写入数据时不立即分配磁盘块，而是等到数据真正刷盘时一次性分配连续的多个块，从而减少外部碎片（Mathur et al., 2007）。

### 日志机制（Journaling）

现代文件系统普遍采用**日志（Journal）**技术防止断电或崩溃导致的数据不一致。ext4的日志位于文件系统的一个特殊区域（默认大小为128MB），每次写操作前先将"意图"写入日志，再执行实际写入，最后标记日志条目为已完成（commit）。若中间断电，重启后文件系统只需重放（redo）或撤销（undo）日志中未完成的条目，恢复时间从数分钟（`fsck` 全盘扫描，对于1TB磁盘可能耗时10分钟以上）缩短至数秒（通常3–5秒）。

ext4支持三种日志模式：

| 模式 | 安全性 | 性能 | 说明 |
|---|---|---|---|
| `journal` | 最高 | 最低 | 数据和元数据均写入日志，写放大约2倍 |
| `ordered` | 中等 | 中等 | 默认模式，数据先于元数据落盘，不记录数据日志 |
| `writeback` | 最低 | 最高 | 仅记录元数据日志，不保证数据写入顺序 |

AI训练场景通常使用 `ordered` 模式，在安全性和性能之间取得平衡；对于模型检查点的写入，若使用 `fsync()` 系统调用强制刷盘，则无论哪种模式都能保证持久性，但 `writeback` 模式下 `fsync()` 之前若系统崩溃，文件内容可能损坏。

### 文件系统层次结构（FHS）

Linux遵循**文件系统层次结构标准**（Filesystem Hierarchy Standard，FHS，当前版本3.0，2015年发布），规定了各目录的用途：`/etc` 存放配置文件、`/var` 存放运行时可变数据（如日志，`/var/log`）、`/tmp` 存放临时文件（重启后清空，通常使用tmpfs挂载在内存中，默认大小为物理内存的一半）、`/home` 存放用户数据、`/proc` 和 `/sys` 为虚拟文件系统，暴露内核状态。AI工程中，训练产出的模型检查点（checkpoint）通常放在 `/data` 或挂载的网络文件系统路径下，而非 `/tmp`，否则系统重启后数据丢失。

## 性能量化分析

理解文件系统性能需要掌握几个关键指标：**吞吐量**（Throughput，MB/s）衡量连续读写速度，**IOPS**（Input/Output Operations Per Second）衡量随机读写能力，**延迟**（Latency，μs或ms）衡量单次操作响应时间。

典型的存储介质性能对比如下：

| 存储介质 | 顺序读（MB/s） | 随机读（IOPS） | 典型延迟 |
|---|---|---|---|
| HDD（7200rpm） | 100–200 | 100–200 | 5–10 ms |
| SATA SSD | 500–600 | 80,000–100,000 | 0.1–0.2 ms |
| NVMe SSD | 3000–7000 | 500,000–1,000,000 | 0.02–0.1 ms |
| RAM（tmpfs） | 10,000–50,000 | >10,000,000 | <0.001 ms |

例如，将ImageNet数据集（约144GB）从HDD迁移到NVMe SSD后，单卡训练的数据加载时间可从每batch约50ms降至约5ms，若使用多进程预取（`DataLoader(num_workers=8)`），可进一步将I/O等待时间隐藏到GPU计算之后。

文件系统的**页缓存**（page cache）命中率对性能影响极大。设缓存命中率为 $h$，缓存访问延迟为 $T_{\text{cache}}$（约100ns），磁盘访问延迟为 $T_{\text{disk}}$，则平均访问延迟为：

$$\bar{T} = h \cdot T_{\text{cache}} + (1 - h) \cdot T_{\text{disk}}$$

当 $h = 0.95$、$T_{\text{disk}} = 5\,\text{ms}$ 时，$\bar{T} \approx 0.25\,\text{ms}$，而当 $h = 0$ 时 $\bar{T} = 5\,\text{ms}$，相差20倍。这解释了为什么训练数据在"热身"几个epoch后速度会明显加快——数据已被缓存至内存。

## 实际应用

**大规模数据集存储**：ImageNet包含约128万张图片，总大小约144GB，若每张图片存为独立的JPEG文件放在同一目录下，目录项的线性查找（对于非哈希目录结构）会极慢，甚至 `ls` 命令都需要数十秒。实际部署时通常将图片按1000个类别分散到1000个子目录（每目录约1280张），或打包为HDF5（分层数据格式）、TFRecord（TensorFlow专用二进制格式）等格式，绕过文件系统的目录层次，直接顺序读取，吞吐量可提升3–10倍。例如，使用TFRecord格式存储ImageNet后，在相同NVMe SSD上的读取吞吐量可从约800 MB/s提升至约4000 MB/s。

**挂载网络文件系统**：多机分布式训练时，NFS（Network File System，由Sun Microsystems于1984年开发）或更高性能的Lustre文件系统用于让所有训练节点共享同一份数据。Lustre专为HPC集群设计，采用分离的元数据服务器（MDS）和对象存储服务器（OSS）架构，可提供数百GB/s的聚合带宽（世界前500强超算中心中超过70%使用Lustre），是很多超算中心存储训练数据的首选。普通NFS在高并发小文件读取时（例如100个训练进程同时随机读取小图片），元数据服务器容易成为瓶颈，RTT延迟可能高达1–10ms。

**Docker与文件系统**：Docker