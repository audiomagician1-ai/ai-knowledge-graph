---
id: "docker-basics"
concept: "Docker基础"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 4
is_milestone: false
tags: ["容器"]

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
updated_at: 2026-03-30
---

# Docker基础

## 概述

Docker是一个基于Linux容器技术（LXC）的开源平台，由Solomon Hykes于2013年3月在PyCon大会上首次公开发布。Docker的核心创新在于将应用程序及其所有依赖项打包进一个称为"容器"（Container）的标准化单元，使其能在任何安装了Docker Engine的环境中以完全一致的方式运行，从根本上解决了"在我机器上能跑"这一历史性难题。

与传统虚拟机（VM）相比，Docker容器不需要完整的Guest OS，而是直接共享宿主机的Linux内核。一台普通服务器运行10个虚拟机可能需要消耗数十GB内存，而运行100个Docker容器只需数百MB额外开销。这种轻量化特性使Docker迅速成为云原生应用开发与部署的标准工具，也是Kubernetes、CI/CD流水线等现代AI工程基础设施的底层支撑。

在AI工程场景中，Docker尤为关键：一个包含CUDA 11.8、PyTorch 2.0、特定Python版本及数十个依赖库的深度学习训练环境，可以被精确复现在任何GPU服务器或云实例上，无需手动配置环境，极大降低了模型训练与推理服务的部署复杂度。

## 核心原理

### 镜像（Image）与联合文件系统

Docker镜像是一个只读的分层文件系统，采用OverlayFS（或旧版的AUFS）实现联合挂载。每一层（Layer）对应Dockerfile中的一条指令，层与层之间通过SHA256哈希值唯一标识。例如，一个PyTorch推理镜像可能包含：基础Ubuntu层 → Python安装层 → pip依赖层 → 模型代码层，共4层叠加。

镜像存储在镜像仓库（Registry）中，Docker Hub是最常用的公共仓库。镜像名称格式为 `[仓库地址/]用户名/镜像名:标签`，例如 `nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04`。构建镜像的核心文件是Dockerfile，其中`FROM`指令指定基础镜像，`RUN`执行命令，`COPY`复制文件，`CMD`或`ENTRYPOINT`定义容器启动时执行的命令。

### 容器（Container）运行机制

容器是镜像的运行实例。Docker在宿主机Linux内核上通过三项技术实现容器隔离：**Namespace**（隔离进程、网络、文件系统等视图）、**cgroups**（限制CPU、内存、磁盘I/O等资源用量）、**Capabilities**（精细控制进程权限）。执行`docker run`时，Docker Engine会基于指定镜像在只读层之上叠加一层可写的容器层，所有运行时写入操作均发生在该层，镜像本身保持不变。

常用运行参数直接影响AI工作负载的行为：`-m 8g`限制内存为8GB；`--gpus all`将宿主机所有GPU暴露给容器（需安装nvidia-container-toolkit）；`-v /data:/workspace/data`将宿主机目录挂载到容器内，确保训练数据持久化。

### Dockerfile最佳实践

构建高效Dockerfile需遵循层缓存原理：Docker按顺序执行指令，某一层变化会导致其后所有层的缓存失效。因此应将变动频率低的指令（如安装系统依赖）放在前面，将频繁变动的代码复制放在最后。多阶段构建（Multi-stage Build）可显著减小最终镜像体积：在第一阶段（builder）中编译代码，在第二阶段仅复制可执行文件，最终AI推理服务镜像可从数GB压缩至数百MB。

```dockerfile
# 多阶段构建示例
FROM python:3.10-slim AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
COPY ./app /app
CMD ["python", "/app/serve.py"]
```

### 网络与数据卷

Docker提供bridge（默认，容器间通过虚拟网桥通信）、host（直接使用宿主机网络，延迟最低）、overlay（跨主机容器通信，用于集群）三种网络模式。数据卷（Volume）是Docker管理的持久化存储，与绑定挂载（Bind Mount）不同，Volume存储在`/var/lib/docker/volumes/`下，生命周期独立于容器，适合存储模型权重文件等需长期保留的数据。

## 实际应用

**AI模型推理服务容器化**：将FastAPI推理服务、模型权重（如1.3GB的BERT模型）、ONNX Runtime等打包为单一镜像，通过`docker run -p 8080:8080 --gpus device=0 myorg/bert-inference:v2.1`在GPU服务器上一键启动，对外暴露8080端口提供HTTP接口。

**实验环境标准化**：团队所有成员使用`docker pull myorg/ml-dev:cuda11.8-torch2.0`获取完全相同的开发环境，杜绝因Python版本（3.9 vs 3.10）或CUDA驱动差异导致的实验不可复现问题。通过`docker exec -it <container_id> bash`可进入运行中容器进行交互式调试。

**CI/CD流水线集成**：在GitHub Actions或Jenkins中，每次代码提交触发`docker build`构建新镜像，`docker push`推送至私有Registry（如Harbor），再通过`docker pull` + `docker run`完成测试环境部署，全程无需手动介入。

## 常见误区

**误区一：容器即虚拟机**。许多初学者将Docker容器与虚拟机等同看待，在容器内安装systemd、运行多个服务进程。实际上，Docker容器的设计哲学是"一个容器只运行一个进程"，容器的生命周期与其主进程（PID 1）绑定，主进程退出则容器停止。在容器内管理多服务会破坏这一设计，增加排障难度。

**误区二：数据写入容器层等同于持久化**。容器可写层中的数据在`docker rm`后永久丢失。将模型训练输出、数据库文件等直接写入容器文件系统而不使用Volume或Bind Mount，是导致数据丢失的常见原因。正确做法是通过`-v`参数明确声明需要持久化的目录。

**误区三：使用`latest`标签保证稳定性**。`latest`标签只是一个可变的别名，`docker pull nginx:latest`在不同时间获取的可能是不同版本的镜像。在生产AI推理服务中应始终使用精确的版本标签（如`pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime`），确保部署的可追溯性与稳定性。

## 知识关联

Docker基础以Linux基础命令为前提，`docker exec`、文件挂载路径、用户权限（`--user`参数）等操作均需要对Linux文件系统和进程模型有基本理解。

掌握Docker基础后，可自然延伸至**Docker Compose**——使用YAML文件定义由多个容器（如训练服务 + Redis + Nginx）组成的应用栈，通过单条`docker compose up`命令编排启动。在更大规模的集群场景下，**Helm Charts**将Docker镜像的部署配置模板化，用于Kubernetes集群的应用发布管理。**基础设施即代码**实践中，Dockerfile本身就是对运行环境的代码化描述，与Terraform等工具共同构成可版本控制的基础设施体系。此外，理解镜像分层结构后，**安全扫描**工具（如Trivy、Snyk）能对每一层的依赖包进行CVE漏洞检测，这是AI服务上线前的必要安全步骤。