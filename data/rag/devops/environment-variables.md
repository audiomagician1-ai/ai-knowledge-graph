---
id: "environment-variables"
concept: "环境变量管理"
domain: "ai-engineering"
subdomain: "devops"
subdomain_name: "开发运维"
difficulty: 3
is_milestone: false
tags: ["配置"]

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

# 环境变量管理

## 概述

环境变量（Environment Variables）是操作系统层面的键值对配置机制，进程在启动时从父进程或系统配置中继承这些键值对，并通过标准接口（如 POSIX 的 `getenv()` 函数）读取。在 AI 工程开发中，环境变量专门用于将数据库连接字符串、API 密钥、模型服务端点、批量推理并发数等运行时参数从代码逻辑中剥离出来，使同一份代码能在开发、测试、生产三套环境中无需修改直接运行。

环境变量的概念源自 1979 年 Unix Version 7，由 Ken Thompson 在设计 shell 时引入，最初目的是让用户自定义 `PATH`（可执行文件搜索路径）和 `HOME`（用户主目录）。到 2000 年代，随着十二要素应用（The Twelve-Factor App）方法论的普及，"在环境中存储配置"成为云原生应用的第三要素，明确规定代码与配置必须严格分离。

对于 AI 工程师而言，环境变量管理的重要性体现在：当调用 OpenAI、Anthropic 或本地部署的 Ollama 服务时，API 端点和密钥若硬编码在 Python 脚本中，极易随代码提交泄露到 GitHub 公开仓库——GitHub 官方数据显示每天发现超过 10 万条泄露密钥。正确使用环境变量则可彻底规避此风险。

## 核心原理

### 环境变量的作用域与继承机制

每个进程拥有独立的环境变量副本，子进程在 `fork()` 时从父进程完整继承环境，但子进程对环境的修改不会反向影响父进程。这解释了为什么在终端执行 `export MY_VAR=value` 后，当前 shell 及其启动的所有 Python 进程都能读到 `MY_VAR`，但关闭终端后该变量消失——它只存在于该 shell 进程的内存中。要使变量跨会话持久化，必须将 `export` 语句写入 `~/.bashrc`（Bash）或 `~/.zshrc`（Zsh）等 shell 配置文件。

### .env 文件与 python-dotenv 库

在 AI 项目中，最常见的管理模式是将所有配置写入项目根目录的 `.env` 文件，格式为每行一个 `KEY=VALUE`，然后用 `python-dotenv` 库在程序启动时加载：

```python
from dotenv import load_dotenv
import os

load_dotenv()  # 默认读取当前目录的 .env 文件
api_key = os.getenv("OPENAI_API_KEY", "未设置")
```

`os.getenv()` 的第二个参数为默认值，可防止变量未设置时返回 `None` 导致的空指针错误。**关键操作**：`.env` 文件必须加入 `.gitignore`，而项目应提供 `.env.example` 文件（内含变量名但不含实际值）供团队成员参考。`python-dotenv` 的加载优先级规则为：已存在的系统环境变量优先于 `.env` 文件中的同名变量，除非使用 `load_dotenv(override=True)`。

### 变量命名规范与类型转换

环境变量的值在操作系统层面**全部为字符串类型**，这是一个经常被忽视的事实。当需要配置整型的并发线程数或布尔型的调试开关时，必须手动转换：

```python
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
DEBUG_MODE  = os.getenv("DEBUG_MODE", "false").lower() == "true"
```

命名规范上，AI 工程领域约定俗成使用全大写字母加下划线，并用前缀区分来源：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`HUGGINGFACE_TOKEN` 是各平台官方使用的标准名称，遵循这些名称可让许多框架（如 LangChain）自动识别并注入，无需额外配置。

### 多环境配置管理

生产级 AI 项目通常维护多套环境配置文件：`.env.development`、`.env.testing`、`.env.production`。通过读取 `APP_ENV` 变量决定加载哪套配置：

```python
env = os.getenv("APP_ENV", "development")
load_dotenv(f".env.{env}")
```

在 Docker 容器化部署场景中，环境变量通过 `docker run -e KEY=VALUE` 或 `docker-compose.yml` 的 `environment` 字段注入，完全不依赖 `.env` 文件，这是容器与本地开发的核心差异。

## 实际应用

**场景一：配置多模型 API 切换**
在 LLM 应用开发中，测试环境使用本地 Ollama（`MODEL_ENDPOINT=http://localhost:11434`），生产环境使用 OpenAI（`MODEL_ENDPOINT=https://api.openai.com/v1`）。通过环境变量控制端点，切换环境无需改动任何业务代码。

**场景二：控制向量数据库连接**
Pinecone、Weaviate 等向量数据库的连接字符串包含账户信息，通过 `PINECONE_API_KEY` 和 `PINECONE_ENVIRONMENT` 两个环境变量注入，开发团队各成员使用各自的账户凭证而不互相影响。

**场景三：GPU 资源配置**
深度学习训练任务中，用 `CUDA_VISIBLE_DEVICES=0,1` 限定进程只能使用 0 号和 1 号 GPU，在多人共用服务器时避免资源争抢，无需修改训练脚本即可灵活分配硬件资源。

## 常见误区

**误区一：将 .env 文件提交到 Git 仓库**
许多初学者认为 `.env` 文件加了注释"仅供本地使用"就安全了，实际上一旦 `git add .` 提交并推送，密钥就永久存在于 Git 历史中，即使后续删除文件，攻击者仍可通过 `git log` 找回。正确做法是在创建项目时立即将 `.env` 写入 `.gitignore`，而不是事后补救。

**误区二：混淆 `export` 与普通赋值的作用域**
在 shell 中执行 `MY_VAR=hello`（不加 `export`）只在当前 shell 中设置局部变量，子进程（包括 `python script.py`）无法继承，`os.getenv("MY_VAR")` 将返回 `None`。必须使用 `export MY_VAR=hello` 才能让子进程可见，这是环境变量区别于 shell 局部变量的本质差异。

**误区三：在容器中依赖 .env 文件**
Docker 容器内默认不包含 `.env` 文件（也不应该包含），若代码依赖 `load_dotenv()` 且容器内无 `.env` 文件，应用会静默失败——因为 `load_dotenv()` 在文件不存在时不会报错，只是不做任何操作。正确做法是在 `docker-compose.yml` 用 `env_file: .env` 字段显式注入，或通过 Kubernetes Secret 挂载。

## 知识关联

**前置知识：命令行基础**
掌握命令行是使用 `export`、`printenv`、`env` 等环境变量操作命令的前提。`printenv` 可列出当前进程所有环境变量，`env KEY=VALUE python script.py` 可为单次命令临时设置变量而不污染全局环境，这两个命令在调试配置问题时极为实用。

**后续主题：密钥管理**
环境变量只是密钥存储的**最简方案**，适用于个人项目和小团队。当团队超过 5 人或进入生产环境时，需要升级到专用密钥管理系统——如 HashiCorp Vault、AWS Secrets Manager 或 Azure Key Vault。这些系统在环境变量概念的基础上增加了访问审计、密钥轮换、细粒度权限控制和加密存储等能力，是企业级 AI 应用的标配基础设施。