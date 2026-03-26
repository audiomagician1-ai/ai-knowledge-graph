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
quality_tier: "B"
quality_score: 47.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.5
last_scored: "2026-03-22"
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

Git LFS（Large File Storage，大文件存储）是由 GitHub、Atlassian、Microsoft 等公司联合开发的 Git 扩展协议，于 2015 年 4 月正式发布（版本 1.0）。它通过将大型二进制文件（如图片、视频、音频、训练模型、压缩包）的实际内容存储在独立服务器上，而在 Git 仓库本身只保存指针文件（pointer file），从而解决 Git 在处理大文件时仓库体积膨胀的根本问题。

普通 Git 仓库对每个文件的每次修改都会存储完整的对象快照，一个 100MB 的 PSD 文件若被修改 50 次，仓库将积累超过 5GB 的数据。Git LFS 打破了这一模式：仓库中的指针文件仅有约 130 字节，而真实的文件内容存放在 LFS 服务端，克隆时只拉取当前工作区实际需要的版本，大幅减少磁盘占用与网络传输量。

Git LFS 已被 GitHub、GitLab、Bitbucket 等主流平台原生支持，并广泛应用于游戏开发、影视制作、机器学习等需要频繁管理大型二进制资产的领域。GitHub 免费账户提供 1GB LFS 存储与每月 1GB 带宽配额，超出部分需购买数据包。

---

## 核心原理

### 指针文件机制

当用户执行 `git lfs track "*.psd"` 并提交一个 PSD 文件时，Git LFS 拦截该文件，将其上传至 LFS 服务端，并在仓库中写入如下格式的指针文件：

```
version https://git-lfs.github.com/spec/v1
oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2393
size 12345678
```

其中 `oid`（Object Identifier）是文件内容的 SHA-256 哈希值，`size` 是字节数。这个 130 字节左右的文本文件被正常纳入 Git 版本控制，而实际内容通过哈希值在 LFS 服务端独立追踪。

### `.gitattributes` 追踪规则

Git LFS 通过 `.gitattributes` 文件定义哪些路径或扩展名交由 LFS 管理。执行 `git lfs track "*.mp4"` 后，`.gitattributes` 中会自动添加：

```
*.mp4 filter=lfs diff=lfs merge=lfs -text
```

这四个属性告诉 Git：该类文件在 smudge（检出）阶段由 LFS filter 替换指针为真实内容，在 clean（暂存）阶段将真实内容替换为指针；`diff=lfs` 和 `merge=lfs` 则指定专属的差异对比与合并驱动程序。**必须将 `.gitattributes` 文件本身提交到仓库**，否则团队其他成员的 LFS 规则不会生效。

### 传输协议与 Batch API

Git LFS 使用独立的 Batch API（批量 API）进行文件传输，而非直接走 Git 的 pack 协议。客户端在推送或拉取时，先向 LFS 服务端的 `<remote>/info/lfs/objects/batch` 端点发送包含所有所需 OID 的 JSON 请求，服务端返回每个对象对应的临时下载或上传 URL（通常是预签名的 S3 等对象存储 URL），客户端再通过标准 HTTPS 完成实际传输。这种设计使 LFS 存储可以与 Git 远端完全解耦，支持将文件存放在 S3、Azure Blob 等任意对象存储后端。

---

## 实际应用

**游戏开发场景**：Unity 或 Unreal Engine 项目中存在大量 `.fbx` 模型、`.wav` 音效和 `.png` 纹理贴图。通过配置 `git lfs track "*.fbx"` `git lfs track "Assets/**/*.png"` 等规则，美术资产可以像代码一样接受版本管理，而仓库克隆时间可从数小时压缩到数分钟。

**机器学习场景**：数据科学团队使用 `git lfs track "*.h5"` 追踪 Keras 训练好的模型权重文件（常见体积 200MB–2GB），配合 DVC 等工具可实现模型与数据集的版本对应关系记录，复现实验结果时直接 `git checkout <commit>` 即可恢复对应的模型文件。

**查看与管理命令**：执行 `git lfs ls-files` 可列出当前仓库中所有受 LFS 管理的文件及其 OID；`git lfs migrate import --include="*.zip"` 可将历史提交中的大文件批量迁移到 LFS，从而缩减已有仓库的体积；`git lfs prune` 可清理本地缓存中不再需要的 LFS 对象，默认保留最近 10 天或当前 HEAD 引用的对象。

---

## 常见误区

**误区一：认为 `git clone` 后就自动拥有所有大文件**。实际上，若本地未安装 `git-lfs` 客户端，克隆后工作目录中得到的只是 130 字节的指针文件文本，而非真实内容。在 CI/CD 环境或新机器上操作前，必须先执行 `git lfs install` 安装钩子，再 `git lfs pull` 拉取实际文件。

**误区二：以为 Git LFS 能解决所有大文件的历史追踪问题，提交后修改自由**。LFS 同样对每个版本存储完整的二进制快照，并不做增量差异（delta）压缩。一个 500MB 的视频文件每次细微修改都会在 LFS 服务端新增 500MB 的存储占用。因此，对于极高频率修改的超大文件，LFS 依然会产生可观的存储账单，需要结合 `git lfs prune` 和服务端保留策略控制成本。

**误区三：认为已追踪的规则会自动应用于历史提交**。`git lfs track` 只对之后的新提交生效。若要将现有仓库历史中的大文件迁移，必须使用 `git lfs migrate import` 命令重写提交历史，该操作会修改所有涉及文件的提交 SHA，需要团队所有成员重新克隆仓库，务必在充分沟通后执行。

---

## 知识关联

学习 Git LFS 之前，了解 Git 的基本对象模型（blob、tree、commit）有助于理解为何普通仓库会因大文件膨胀——Git 将每个文件版本存为独立 blob 对象，无法对二进制内容做有效 delta 压缩，这正是 LFS 要替代存储的原因。

Git LFS 是进入**二进制版本控制**这一更宽泛主题的直接入口。掌握 LFS 的指针机制和 Batch API 后，可以进一步学习 DVC（Data Version Control）——DVC 借鉴了 LFS 的指针思想，但将追踪范围扩展到数据集目录，并支持在 Git 仓库之外独立管理数据流水线的版本。同时，Perforce Helix Core 等专为二进制资产设计的版本控制系统在游戏行业的使用场景，也与 Git LFS 所解决的问题高度重叠，对比两者的锁文件机制（LFS file locking vs. Perforce exclusive checkout）是深入理解二进制版本控制权衡取舍的重要视角。