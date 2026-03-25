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
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.424
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Docker基础

## 概述

Docker是一个基于Linux容器技术（LXC）的开源平台，由Solomon Hykes于2013年3月在PyCon大会上首次公开发布。它通过将应用程序及其所有依赖打包进一个标准化的隔离单元——**容器（Container）**——来解决"在我机器上能跑"这一经典工程难题。与虚拟机不同，Docker容器直接共享宿主机的操作系统内核，不需要完整的Guest OS，使得单个容器的启动时间通常在毫秒到秒级，镜像体积也比虚拟机磁盘文件小几个数量级。

Docker的重要性在AI工程领域尤为突出：深度学习项目依赖复杂的Python包版本（如PyTorch 2.1.0搭配CUDA 12.1）、系统库和驱动程序，这些依赖在不同机器间极易冲突。Docker将训练环境、推理服务和数据处理管线分别封装，使得从开发笔记本到云端GPU集群的部署过程变得可重复、可版本化。自2013年至今，Docker Hub上的公开镜像数量已超过800万，成为软件分发的事实标准之一。

## 核心原理

### 镜像（Image）与分层文件系统

Docker镜像采用**联合文件系统（UnionFS）**构建，每个镜像由多个只读层（Layer）叠加而成。当你基于`python:3.11-slim`镜像安装PyTorch时，系统不会复制整个基础层，而是在其上添加一个新的差异层。这种分层机制使得多个容器可以共享相同的底层，节省磁盘空间。每一层由SHA-256哈希值唯一标识，例如`sha256:a3ed95caeb02`，保证了镜像内容的完整性和可复现性。

`Dockerfile`是定义镜像内容的文本文件，每条指令（`FROM`、`RUN`、`COPY`、`CMD`等）对应镜像中的一层。指令顺序直接影响构建缓存效率——将变动频繁的`COPY . .`放在安装依赖的`RUN pip install`之后，可以避免每次代码修改都重新下载所有Python包。

### 容器（Container）的隔离机制

容器是镜像的运行实例，Docker利用Linux内核的两个核心特性实现隔离：

- **Namespaces（命名空间）**：隔离进程ID（PID）、网络栈（NET）、文件系统挂载点（MNT）、主机名（UTS）等，使容器内的进程"看不到"宿主机或其他容器的资源。
- **Cgroups（控制组）**：限制容器可使用的CPU、内存、I/O等硬件资源。例如`docker run --memory="4g" --cpus="2"`将容器的内存限制在4GB、CPU限制在2核，防止单个AI推理服务耗尽整台服务器资源。

容器在镜像的只读层之上增加一个**可写层（Writable Layer）**，容器删除后该层消失，镜像本身不受影响。

### Docker网络与数据卷

Docker默认提供三种网络模式：`bridge`（容器间通过虚拟交换机通信）、`host`（容器直接使用宿主机网络栈，延迟最低）和`none`（完全隔离）。AI推理服务常用`bridge`模式，通过`-p 8080:80`将宿主机的8080端口映射到容器内的80端口对外提供API。

数据持久化通过**Volume（数据卷）**实现。使用`docker volume create model_weights`创建命名卷后，多个容器可以挂载同一份模型权重文件，避免在每个容器镜像内重复存储数GB的模型文件。Bind Mount（绑定挂载）则直接将宿主机目录挂载进容器，常用于开发阶段实时同步代码修改。

## 实际应用

**构建AI推理服务镜像**是Docker在AI工程中最典型的用法。一个标准流程如下：基于`nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04`官方镜像，通过`RUN pip install fastapi uvicorn torch==2.1.0`安装依赖，再`COPY`模型加载代码，最后用`CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]`启动服务。整个镜像可以推送至AWS ECR或Docker Hub，在任意支持Docker的GPU服务器上用一条`docker run`命令复现相同环境。

**多阶段构建（Multi-stage Build）**可大幅缩减最终镜像体积。在第一个`FROM`阶段编译C++扩展或安装build工具，第二阶段仅`COPY --from=builder`复制编译产物，去除gcc等编译工具，将镜像从数GB压缩至数百MB，显著缩短云端拉取时间。

**本地实验环境隔离**：在同一台开发机上同时运行TensorFlow 2.13和PyTorch 2.1的代码，无需担心Python包冲突，只需分别`docker exec -it tf_container bash`和`docker exec -it pt_container bash`进入各自环境。

## 常见误区

**误区一：容器等同于轻量级虚拟机。** 很多初学者认为容器提供了与虚拟机相同程度的隔离，但容器共享宿主机内核，这意味着容器内无法运行与宿主机不同的内核版本，也无法在Linux宿主机上运行Windows容器（Docker Desktop通过内置轻量VM绕过此限制）。内核级漏洞（如2019年的runc CVE-2019-5736）可能允许容器逃逸，而虚拟机的Hypervisor层提供更强的隔离边界。

**误区二：`docker commit`是构建镜像的正确方式。** 一些开发者通过`docker exec`手动在容器内安装软件，再用`docker commit`保存为镜像。这种方式产生的镜像没有可审计的构建记录，无法重现，也无法利用层缓存加速构建。正确做法始终是维护`Dockerfile`并通过`docker build`构建，保证镜像内容与代码仓库中的定义一致。

**误区三：容器内写入数据默认持久化。** 容器的可写层在`docker rm`后会被删除，所有写入容器文件系统的数据（包括训练中间checkpoint）都会丢失。必须通过`-v`参数挂载Volume或Bind Mount，将需要持久化的数据写入挂载点，这是AI训练任务中极易踩到的陷阱。

## 知识关联

**前置依赖**：Linux基础命令是使用Docker的必要基础——`docker exec`进入容器后本质上是在操作一个Linux环境，需要用`ps`、`ls`、`chmod`等命令排查问题；理解Linux的文件权限模型有助于正确配置容器内的用户权限，避免以root运行容器带来的安全风险。

**后续拓展**：掌握Docker单容器操作后，**Docker Compose**使用`docker-compose.yml`文件定义和编排多容器应用（例如将模型服务、Redis缓存和Nginx网关组合成一个可一键启动的系统），是Docker基础的直接延伸。**微服务入门**需要在Docker容器化单服务的基础上，理解服务注册、负载均衡等跨容器协作模式。进入Kubernetes生态后，**Helm Charts**将Docker镜像部署模板化，而**安全扫描**工具（如Trivy、Snyk）则专门检测Docker镜像各层中已知CVE漏洞，将DevOps中的安全实践与Docker镜像生命周期深度绑定。**基础设施即代码**实践中，Dockerfile本身就是"代码定义环境"理念的体现，是理解Terraform等工具的思维起点。
