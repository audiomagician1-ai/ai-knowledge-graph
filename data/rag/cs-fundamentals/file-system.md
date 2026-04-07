# 文件系统

## 概述

文件系统（File System）是操作系统中负责管理持久化数据存储的子系统，它定义了数据在存储介质上的组织方式、命名规则和访问方法。具体而言，文件系统将原始的磁盘扇区（sector，通常为512字节或4096字节）抽象为用户可见的"文件"和"目录"层次结构，使程序员无需关心数据实际存储在磁盘的哪个物理位置。没有文件系统，磁盘就只是一段连续的字节序列，毫无结构可言。

文件系统的历史可追溯至1960年代。IBM在OS/360（1964年）中引入了早期的文件管理概念，而Unix在1969年设计的UFS（Unix File System）奠定了现代文件系统的基本架构——inode结构、目录树、硬链接等概念均源自此处。1984年，McKusick等人在UC Berkeley开发的FFS（Fast File System，发表于ACM Transactions on Computer Systems）首次引入柱面组（cylinder group）概念，将相关文件尽量分配到邻近磁盘区域，使HDD顺序读写速度提升约10倍（McKusick et al., 1984）。1993年发布的ext2是Linux世界的重要里程碑，其继任者ext4（2008年正式合并入Linux 2.6.28内核）至今仍是众多Linux服务器的默认文件系统，支持单卷最大1EB（$10^{18}$ 字节）的容量。Windows则采用NTFS（New Technology File System，1993年随Windows NT 3.1推出），支持单文件最大16EB的理论容量，MFT（Master File Table）记录每个文件的完整元数据。

在AI工程领域，文件系统的重要性体现在训练数据的读取效率上。当用PyTorch 2.x或TensorFlow 2.x训练大模型时，数据加载的I/O瓶颈往往比GPU计算瓶颈更早出现。例如，在8块A100 GPU的训练节点上，每张卡的理论算力约为312 TFLOPS，若文件系统读取速度不足，GPU利用率会跌至30%以下，白白浪费昂贵的算力资源。理解文件系统的缓存机制、块大小（block size）和目录遍历开销，能帮助工程师正确配置数据预处理流水线，避免GPU空等数据的情况（Tanenbaum & Bos, 2014）。

## 核心原理

### 基本数据结构：inode与目录项

文件系统用**inode**（index node，索引节点）记录文件的元数据。一个inode包含：文件大小、权限位（rwx）、时间戳（创建/修改/访问）、数据块指针，但**不包含文件名**。文件名存储在目录项（directory entry，dentry）中，目录项是一个 $\langle\text{文件名},\ \text{inode号}\rangle$ 的映射表。这种设计使得硬链接成为可能：多个目录项可以指向同一个inode，inode中的 $\text{link\_count}$ 字段记录有多少个目录项引用它，当满足条件：

$$\text{link\_count} = 0 \;\wedge\; \text{open\_count} = 0$$

时，文件才真正被删除，操作系统才将对应数据块标记为空闲并释放空间。

在ext4中，每个inode大小默认为256字节（早期ext2为128字节，ext4扩展以支持纳秒级时间戳和扩展属性），一个文件系统的inode总数在执行 `mkfs.ext4` 格式化时确定，默认每16KB存储空间分配一个inode。这意味着即使磁盘空间充足，若inode耗尽，也无法创建新文件——在存储海量小文件（如机器学习数据集的每条样本存为独立文件）时，这是一个常见的陷阱。可通过 `df -i` 命令查看inode使用情况。

ext4的inode数据块指针采用**扩展（extent）**结构而非传统的三级间接指针（indirect block）：一个extent记录 $\langle\text{逻辑块号}, \text{物理块号}, \text{连续块数}\rangle$ 三元组，单个extent最多描述128MB（32768个4KB块）的连续空间。对于大文件，ext4的inode内嵌4个extent，若文件足够连续，无需任何间接块即可描述高达512MB的数据，相比ext2的三级间接指针方案减少了大量额外I/O（Love, 2010）。

### 块分配与碎片化

文件系统以**块**（block）为单位分配存储空间，ext4默认块大小为4096字节（4KB）。即使一个文件只有1字节，也会占用一整个4KB块，这被称为**内部碎片**（internal fragmentation）。设文件实际大小为 $S$ 字节，块大小为 $B$ 字节，则实际占用磁盘空间为：

$$\text{占用块数} = \left\lceil \frac{S}{B} \right\rceil$$

由此产生的空间浪费为 $\left\lceil S/B \right\rceil \times B - S$ 字节。相反，当文件被反复修改、删除后，磁盘上空闲块分散分布，新文件的数据块无法连续存放，产生**外部碎片**（external fragmentation），读取时磁头需要频繁寻道，导致I/O性能下降。HDD的顺序读取速度（约100–200 MB/s）远高于随机读取速度（约0.5–1 MB/s），而NVMe SSD的随机读取速度（约500K IOPS）远高于HDD，使碎片化对SSD的性能影响相对较小。但在HDD上存储大量小图片文件时（例如ImageNet的128万张JPEG图片未经打包），碎片化会显著降低训练数据的读取吞吐量，实测可使吞吐量下降50%以上。

ext4通过**延迟分配**（delayed allocation）和**多块分配器**（multi-block allocator，mballoc）缓解碎片问题：写入数据时不立即分配磁盘块，而是等到数据真正刷盘时一次性分配连续的多个块，从而减少外部碎片（Mathur et al., 2007）。此外，`e4defrag` 工具可对已碎片化的ext4卷进行在线碎片整理，无需卸载文件系统，对正在运行的训练任务影响较小。

### 日志机制（Journaling）

现代文件系统普遍采用**日志（Journal）**技术防止断电或崩溃导致的数据不一致。ext4的日志位于文件系统的一个特殊区域（默认大小为128MB），每次写操作前先将"意图"写入日志，再执行实际写入，最后标记日志条目为已完成（commit）。若中间断电，重启后文件系统只需重放（redo）或撤销（undo）日志中未完成的条目，恢复时间从数分钟（`fsck` 全盘扫描，对于1TB磁盘可能耗时10分钟以上）缩短至数秒（通常3–5秒）。

ext4支持三种日志模式：

| 模式 | 安全性 | 性能 | 说明 |
|---|---|---|---|
| `journal` | 最高 | 最低 | 数据和元数据均写入日志，写放大约2倍 |
| `ordered` | 中等 | 中等 | 默认模式，数据先于元数据落盘，不记录数据日志 |
| `writeback` | 最低 | 最高 | 仅记录元数据日志，不保证数据写入顺序 |

AI训练场景通常使用 `ordered` 模式，在安全性和性能之间取得平衡；对于模型检查点的写入，若使用 `fsync()` 系统调用强制刷盘，则无论哪种模式都能保证持久性，但 `writeback` 模式下 `fsync()` 之前若系统崩溃，文件内容可能损坏。

日志本身也存在**写放大**（Write Amplification）问题：一次4KB的用户写操作可能引发日志区的4KB写入加上数据区的4KB写入，实际磁盘写入量翻倍。对于NVMe SSD，写放大因子（WAF）还会叠加闪存层面的擦写放大（通常为1.5–3×），因此在SSD上长期运行高写入负载时需监控SSD的P/E循环次数（每个闪存单元典型寿命为3,000–100,000次擦写周期）。

### 文件系统层次结构（FHS）

Linux遵循**文件系统层次结构标准**（Filesystem Hierarchy Standard，FHS，当前版本3.0，2015年发布），规定了各目录的用途：`/etc` 存放配置文件、`/var` 存放运行时可变数据（如日志，`/var/log`）、`/tmp` 存放临时文件（重启后清空，通常使用tmpfs挂载在内存中，默认大小为物理内存的一半）、`/home` 存放用户数据、`/proc` 和 `/sys` 为虚拟文件系统，暴露内核状态。AI工程中，训练产出的模型检查点（checkpoint）通常放在 `/data` 或挂载的网络文件系统路径下，而非 `/tmp`，否则系统重启后数据丢失。

`/proc` 虚拟文件系统由内核动态生成，读取 `/proc/PID/status` 可获取指定进程的内存、CPU占用等实时信息，读取 `/proc/diskstats` 可获取磁盘I/O统计数据（包括读写次数、扇区数、等待时间），是诊断文件系统I/O瓶颈的重要工具，`iostat` 命令底层的数据来源正是此处。

## 关键公式与性能模型

### I/O 吞吐量上界

文件系统的实际读写吞吐量受到存储介质、块大小、队列深度等多个因素共同制约。对于一个顺序读取场景，理论最大吞吐量可表示为：

$$T_{\text{seq}} = \min\left(T_{\text{media}},\ T_{\text{bus}},\ T_{\text{cpu}}\right)$$

其中 $T_{\text{media}}$ 为存储介质带宽（如NVMe SSD约7 GB/s），$T_{\text{bus}}$ 为PCIe总线带宽（PCIe 4.0 ×4约8 GB/s），$T_{\text{cpu}}$ 为内核I/O路径处理能力。实际工程中，存储介质往往是瓶颈，但在网络文件系统（NFS/HDFS）场景下，网络带宽 $T_{\text{net}}$ 也需纳入 $\min(\cdot)$ 中。

### 随机读有效吞吐量

对于随机小文件读取（如ImageNet中每张JPEG平均约100KB），HDD的有效吞吐量受寻道时间主导：

$$T_{\text{rand}} = \frac{\text{block\_size}}{t_{\text{seek}} + t_{\text{rotation}} + t_{\text{transfer}}}$$

以7200rpm HDD为例，$t_{\text{seek}} \approx 8\text{ ms}$，$t_{\text{rotation}} \approx 4\text{ ms}$，$t_{\text{transfer}} \approx 0.5\text{ ms}$（4KB块），则每秒随机读约 $1000/12.5 \approx 80$ IOPS，对应约320 KB/s——远低于其200 MB/s的顺序读带宽，两者相差约625倍。这正是为何AI训练中必须将大量小文件打包为WebDataset（.tar）或TFRecord格式。

### Page Cache命中率与磁盘I/O

Linux内核将空闲物理内存用作**Page Cache**（页缓存），对文件系统读写进行透明缓存。设 $R$ 为总读请求次数，$H$ 为命中Page Cache的次数，则：

$$\text{Cache Hit Rate} = \frac{H}{R}, \quad \text{Disk I/O} = R \times (1 - \text{Hit Rate})$$

在一台256GB内存的训练服务器上，若训练数据集总大小为100GB，第一个epoch完成后数据集理论上可全部驻留在Page Cache中（假设无其他内存竞争）。从第二个epoch起，Hit Rate趋近1.0，磁盘I/O降为零，数据加载延迟从毫秒级降至微秒级（DRAM访问约100ns）。可通过 `free -h` 观察cached列，或 `/proc/meminfo` 中的 `Cached:` 字段确认缓存使用量。

## 性能量化分析

理解文件系统性能需要掌握几个关键指标：**吞