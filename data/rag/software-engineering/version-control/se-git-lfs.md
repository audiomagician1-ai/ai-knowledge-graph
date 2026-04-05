---
id: "se-git-lfs"
concept: "Git LFS"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 2
is_milestone: false
tags: ["大文件"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Git LFS（大文件存储）

## 概述

Git LFS（Large File Storage，大文件存储）是由 GitHub 于 2015 年 4 月发布的 Git 扩展工具，专门解决 Git 仓库中存储大文件和二进制资产时性能急剧下降的问题。其核心机制是：将仓库中的大文件替换为一个小型文本指针文件（pointer file），而实际的文件内容则上传到独立的 LFS 服务器上。这个指针文件仅有约 130 字节，记录了文件的 SHA-256 哈希值、文件大小以及 LFS 版本号。

Git 原生设计针对文本文件的差异存储（delta compression），对于 PNG 图片、PSD 设计稿、MP4 视频、训练好的 AI 模型权重文件（`.bin`、`.ckpt`）等二进制文件，Git 无法计算有意义的差异，只能每次提交时完整保存整个文件。若项目中包含 1 GB 的游戏资产，经过 20 次修改后，`.git` 目录可能膨胀至 20 GB 以上，克隆耗时数小时。Git LFS 通过指针替换机制，将这 20 GB 全部转移至 LFS 存储服务器，`.git` 目录仅保留 20 个约 130 字节的指针。

Git LFS 之所以在游戏开发、影视后期制作、机器学习工程、CAD 设计等领域被广泛采用，根本原因在于它保留了完整的 Git 工作流（提交、分支、合并）同时彻底解耦了仓库体积与资产体积的关系。

## 核心原理

### 指针文件结构

当一个文件被 Git LFS 追踪后，Git 仓库中实际存储的是如下格式的指针文件：

```
version https://git-lfs.github.com/spec/v1
oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2393
size 12345
```

其中 `oid`（Object ID）是原始文件内容的 SHA-256 哈希，`size` 是原始文件字节数。Git 追踪的是这个 130 字节左右的纯文本文件，而非原始二进制内容。当用户执行 `git checkout` 时，Git LFS 的 smudge filter 会自动将指针替换为从 LFS 服务器下载的真实文件；执行 `git add` 时，clean filter 会将真实文件转换回指针。

### 追踪配置与 .gitattributes

Git LFS 通过 `.gitattributes` 文件声明哪些文件类型需要被追踪。执行命令 `git lfs track "*.psd"` 后，`.gitattributes` 中会自动添加：

```
*.psd filter=lfs diff=lfs merge=lfs -text
```

四个属性中，`filter=lfs` 指定使用 LFS 的 clean/smudge 过滤器；`diff=lfs` 让 Git 使用 LFS 的差异比较方式；`merge=lfs` 指定 LFS 的合并策略；`-text` 告知 Git 该文件是二进制，不进行行尾换行符转换。`.gitattributes` 文件本身必须提交到仓库，以确保所有协作者共享相同的追踪规则。

### 存储与带宽计费模型

Git LFS 采用独立于 Git 对象数据库的存储体系。GitHub 为每个账户提供 1 GB 的免费 LFS 存储空间和每月 1 GB 的免费带宽。超出后按 $5/月购买 50 GB 存储包和 50 GB 带宽包。GitLab 和 Bitbucket 有各自不同的 LFS 配额策略。自托管方案可使用 MinIO、S3 或 `git-lfs-server` 实现零额外成本的私有 LFS 服务器。这一计费模型意味着克隆仓库（下载 LFS 对象）会消耗带宽配额，而不只是存储配额。

### 部分克隆与按需下载

Git LFS 支持通过 `GIT_LFS_SKIP_SMUDGE=1` 环境变量或 `git lfs install --skip-smudge` 跳过自动下载，此时检出的文件仅为指针文件。后续可以用 `git lfs pull` 批量下载，或 `git lfs fetch --include="path/to/specific/file"` 只下载特定文件。这一特性对 CI/CD 流水线尤为有价值——如果构建任务不需要设计稿，可完全跳过 LFS 下载，大幅缩短流水线运行时间。

## 实际应用

**游戏开发场景**：Unity 项目中通常将 `.fbx`（3D 模型）、`.png`（贴图）、`.wav`（音频）全部纳入 LFS 追踪。一个中型 Unity 游戏项目在使用 LFS 后，仓库克隆时间可从 45 分钟降至 2 分钟，因为 Git 只需下载指针文件和代码，美术资产按需拉取。

**机器学习工程场景**：存储 PyTorch 模型权重文件（`.pt`、`.safetensors`），每次实验后提交新版本权重，利用 Git LFS 的版本追踪记录模型演化历史。结合 `git lfs fetch --all` 可以回溯到任意版本的权重进行推理对比。

**迁移已有大文件**：对于已经直接提交了大文件的历史仓库，使用 `git lfs migrate import --include="*.psd"` 命令可以重写 Git 历史，将历史提交中的大文件全部转换为 LFS 指针，同时保留完整的提交历史结构。

## 常见误区

**误区一：LFS 文件也能像文本文件一样进行差异合并**。Git LFS 默认不支持对二进制文件的三方合并（three-way merge），当两个分支都修改了同一个 `.psd` 文件时，LFS 会将其标记为冲突，必须手动选择保留哪一个版本。`merge=lfs` 属性意味着合并策略由 LFS 处理，而非 Git 的自动文本合并，所以二进制文件的合并冲突必须通过保留一方来解决，不存在"合并两个图片版本"的操作。

**误区二：只要安装了 Git LFS 就会自动追踪所有大文件**。Git LFS 不会主动检测文件大小并自动追踪，必须显式运行 `git lfs track` 命令或手动编辑 `.gitattributes`。如果忘记追踪某个类型的文件就直接 `git add`，该文件将以原始二进制形式存入 Git 对象数据库，事后只能通过 `git lfs migrate` 重写历史来修正。

**误区三：删除 LFS 追踪的文件就能释放存储空间**。从仓库中删除一个 LFS 文件并提交，不会立即释放 LFS 服务器上的存储。LFS 对象的清理需要在服务器端执行专门的垃圾回收操作（GitHub 会在约 30 天后自动清理孤立对象），本地也需要运行 `git lfs prune` 来清理本地 LFS 缓存（默认位于 `~/.git/lfs/objects/`）。

## 知识关联

学习 Git LFS 需要理解 Git 对象模型（blob、tree、commit）的基础知识，以便明白为什么大文件直接存入 Git 对象数据库会造成仓库膨胀——每个历史版本的二进制 blob 都被完整保留在 `.git/objects/` 中，且无法被 pack 文件的 delta 压缩有效压缩。

掌握 Git LFS 之后，下一步自然延伸到**二进制版本控制**的更广泛话题，包括与 Git LFS 的替代或互补方案的比较：Perforce Helix Core（游戏行业传统选择，原生支持大文件锁定机制）、DVC（Data Version Control，专为机器学习数据集和模型设计，支持 S3/GCS/Azure 等多种后端）、以及 Git Annex（与 LFS 类似但采用符号链接机制，更适合离线场景）。理解 LFS 的指针文件机制也为理解 DVC 的 `.dvc` 元数据文件设计提供了直接的概念参照。