# Git LFS（大文件存储）

## 概述

Git LFS（Large File Storage，大文件存储）是由 GitHub、Atlassian、Microsoft 联合开发，于 2015 年 4 月以 v1.0 正式发布的 Git 扩展工具。其诞生背景直接源于 Git 在处理二进制大文件时的架构性缺陷：Git 的对象数据库（object database）基于 SHA-1 哈希寻址的内容存储，采用增量压缩（delta compression）机制处理文本文件的版本差异，但对 PNG 图片、PSD 设计稿、MP4 视频、机器学习模型权重（`.bin`、`.ckpt`、`.safetensors`）、Unity 场景文件等二进制格式无法提取有意义的差异，只能逐版本完整保存。

Git LFS 的解决思路是将"大文件实体"与"版本历史引用"彻底分离：仓库中存储的是一个约 130 字节的纯文本**指针文件**（pointer file），记录原始文件的 SHA-256 哈希与字节大小；文件实体本身上传至独立的 LFS 对象存储服务器，通过 HTTPS API 按需拉取。这一设计使得 `.git` 目录体积与项目所含资产总量解耦，即便项目积累了数百 GB 的历史游戏资产，`git clone` 默认只拉取指针与最新工作区文件，而非全部历史版本的原始二进制内容。

根据 Atlassian 官方文档（Atlassian, 2020）及 GitHub Engineering Blog 的多篇记录，Git LFS 目前已有超过 15 万个公开仓库启用，每月通过 GitHub LFS 传输的数据量超过 1 PB，覆盖游戏开发、影视后期、机器学习工程、嵌入式固件开发等大量需要管理二进制资产的工程场景。

## 核心原理

### 指针文件的数据结构

当文件被 Git LFS 追踪后，Git 仓库对象数据库中实际存储的是如下格式的指针文件：

```
version https://git-lfs.github.com/spec/v1
oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2393
size 132048
```

- `version` 字段标识 LFS 规范版本，当前固定为 `v1`；
- `oid`（Object ID）字段存储原始文件内容的 SHA-256 哈希，用于在 LFS 服务器上唯一定位文件实体；
- `size` 字段记录原始文件的字节数，供 LFS 客户端在下载前预估带宽消耗。

整个指针文件通常在 120～140 字节之间。Git 对这个纯文本文件执行常规的 delta 压缩和历史存储，因此提交、分支切换、历史浏览等操作均在毫秒级完成，与文件实际大小完全无关。

### Clean/Smudge 过滤器机制

Git LFS 通过 Git 的 **filter driver** 接口工作，该机制定义于 Git 官方手册 `gitattributes(5)` 中（Torvalds & Hamano, 2005 起持续维护）。LFS 注册了两个过滤器：

- **Clean filter**（写入阶段）：当执行 `git add` 时，Git 将文件内容通过 `git lfs clean` 管道处理，计算 SHA-256 哈希，将文件实体暂存至本地 LFS 缓存目录（默认 `~/.git/lfs/objects/`），并向 Git 返回生成的指针文件内容。
- **Smudge filter**（读取阶段）：当执行 `git checkout` 时，Git 将指针文件内容通过 `git lfs smudge` 管道处理，LFS 客户端根据 `oid` 哈希从本地缓存或远程 LFS 服务器下载原始文件，写入工作区。

这一设计对用户完全透明，`git add`/`git checkout` 的语义完全不变，LFS 过滤器在底层自动处理文件实体的上传与下载。

### .gitattributes 追踪规则

Git LFS 通过 `.gitattributes` 文件声明追踪规则。执行 `git lfs track "*.psd"` 后，该文件自动写入：

```
*.psd filter=lfs diff=lfs merge=lfs -text
```

四个属性的含义分别为：
- `filter=lfs`：启用 LFS 的 clean/smudge 过滤器；
- `diff=lfs`：使用 LFS 差异驱动，在 `git diff` 中显示指针差异而非乱码二进制；
- `merge=lfs`：合并冲突时使用 LFS 合并驱动，默认行为是保留当前分支版本并标记冲突；
- `-text`：告知 Git 该文件为二进制，禁用行尾换行符（CRLF/LF）自动转换。

`.gitattributes` 本身必须提交进仓库，否则新克隆的协作者不会激活 LFS 追踪，将把真实大文件而非指针直接提交，导致仓库体积失控。

### LFS Batch API 通信协议

Git LFS 客户端与服务器之间使用基于 HTTPS 的 **Batch API**（LFS Specification v1，GitHub, 2015）进行通信。每次 `git push` 或 `git pull` 时：

1. 客户端收集本次操作涉及的所有 LFS 对象的 `oid` 列表，通过 POST 请求发送至 `https://<lfs-server>/info/lfs/objects/batch`；
2. 服务器返回每个 `oid` 对应的上传或下载 URL（通常为预签名的对象存储 URL，如 AWS S3 presigned URL）及有效期；
3. 客户端并发地通过 HTTPS 直接与对象存储交互，传输文件实体；
4. 传输完成后，服务器端记录上传状态，客户端完成 `git push` 的 ref 更新。

这一设计将文件传输流量从 Git 服务器卸载（offload）至对象存储，使 LFS 服务器本身无需承担大带宽压力。

## 关键命令与操作

### 初始化与追踪

```bash
# 在仓库中初始化 Git LFS（写入 .git/hooks/pre-push 等钩子）
git lfs install

# 追踪特定扩展名
git lfs track "*.mp4"
git lfs track "*.psd"
git lfs track "models/**/*.bin"

# 查看当前追踪规则
git lfs track

# 查看当前工作区中被 LFS 管理的文件列表
git lfs ls-files
```

### 检查与迁移历史

对于已经将大文件直接提交进 Git 历史（未使用 LFS）的仓库，Git LFS 提供了 `migrate` 子命令进行历史重写（需要 git-lfs >= 2.2.0）：

```bash
# 将历史中所有 .psd 文件迁移至 LFS（重写提交历史）
git lfs migrate import --include="*.psd" --everything
```

此操作会重写受影响的全部提交，改变提交哈希，需要所有协作者重新克隆仓库，属于破坏性操作，应在团队协调后执行。

### 存储配额与带宽计费

Git LFS 采用独立于 Git 对象数据库的存储计费模型：

- **GitHub Free**：提供 1 GB LFS 存储空间 + 每月 1 GB 免费带宽；
- **GitHub Pro / Team**：存储和带宽均可按 $5/月购买 50 GB 数据包扩展；
- **GitLab**：每个项目的 LFS 配额由实例管理员配置，GitLab.com 免费层提供 10 GB 总存储（含 LFS）；
- **自托管方案**：可通过 `git-lfs-s3`、Gitea 内置 LFS、或 MinIO 搭建私有 LFS 服务器，无配额限制。

## 实际应用场景

### 游戏开发：Unity 项目资产管理

Unity 项目通常包含大量 `.png`、`.fbx`、`.wav`、`.unity` 场景文件。以一个中等规模的手游项目为例：美术资产约 2 GB，音效 500 MB，在 12 个月的开发周期内经历约 500 次提交，若不使用 LFS，仓库历史中积累的原始资产可能超过 50 GB，`git clone` 耗时超过 1 小时。启用 LFS 后，克隆时间取决于当前版本的资产大小（约 2.5 GB），通常在 5～10 分钟内完成，历史回溯时按需拉取指定版本文件。

Unity 官方文档（Unity Technologies, 2022）推荐在 `.gitattributes` 中追踪以下类型：

```
*.png filter=lfs diff=lfs merge=lfs -text
*.jpg filter=lfs diff=lfs merge=lfs -text
*.fbx filter=lfs diff=lfs merge=lfs -text
*.wav filter=lfs diff=lfs merge=lfs -text
*.mp3 filter=lfs diff=lfs merge=lfs -text
*.unity filter=lfs diff=lfs merge=lfs -text
*.asset filter=lfs diff=lfs merge=lfs -text
```

### 机器学习工程：模型权重版本管理

机器学习项目中，训练完成的模型权重文件（`.bin`、`.safetensors`、`.ckpt`）动辄数百 MB 至数十 GB。Hugging Face 的模型托管平台 `huggingface.co` 本身即基于 Git LFS 构建，每个模型仓库的权重文件均以 LFS 指针存储，用户通过 `git clone` 或 `huggingface_hub` 客户端按需下载特定版本的权重，实现模型的版本化管理与回滚（Wolf et al., 2020，*HuggingFace Transformers* 论文中对 model hub 架构有所描述）。

例如，一个 BERT-large 模型的权重文件约 1.3 GB，若在实验中产生 20 个 checkpoint，直接用 Git 管理将使仓库体积达到 26 GB；使用 LFS 后仓库本身仅存储 20 个指针文件（约 2.6 KB），实体文件按实验需要选择性下载。

### 嵌入式开发：固件二进制管理

嵌入式项目中，编译产物（`.hex`、`.elf`、`.bin` 固件文件）和第三方库的预编译静态库（`.a`、`.lib`）通常需要纳入版本控制以实现发布版本追溯。这些文件无法用文本差异表达，通过 LFS 管理可在保留发布历史的同时避免仓库膨胀。

## 常见误区

### 误区一：LFS 追踪必须在首次提交前设置

**错误认知**：许多开发者认为如果文件已经被普通 Git 提交过，就无法迁移至 LFS。

**事实**：`git lfs migrate import` 命令可重写历史，将已经进入 Git 对象数据库的大文件提取至 LFS。但重写历史会改变所有受影响提交的 SHA-1 哈希值，需要协调团队执行强制推送（`git push --force`）并要求所有协作者重新克隆。

### 误区二：所有大文件都应该用 LFS 管理

**事实**：LFS 适合**二进制文件**和**不可差异压缩的文件**。对于大型 SQL 转储文件（纯文本）、大型 CSV 数据集等，Git 的 zlib 压缩和 delta 存储可能已经足够高效。此外，如果文件每次修改变化极小但整体很大（例如一个持续追加的日志文件），LFS 因无法做差异压缩反而会占用更多存储。判断标准：**若文件是二进制格式，或文本文件但每次修改差异接近全文重写，则适合 LFS**。

### 误区三：.gitattributes 无需提交到仓库

**后果极其严重**：若 `.gitattributes` 未提交，新克隆仓库的协作者在执行 `git add *.psd` 时，LFS 过滤器不会激活，PSD 文件将以原始二进制形式直接提交进 Git 对象数据库，导致仓库体积急剧膨胀，且该问题在 `git push` 后才会被发现，回滚成本很高。

### 误区四：Git LFS 支持合并大文件冲突

**事实**：`merge=lfs` 属性并不实现真正的二进制差异合并。对于 PSD、FBX、模型权重等二进制文件，LFS 在遇到合并冲突时默认使用当前分支版本（`