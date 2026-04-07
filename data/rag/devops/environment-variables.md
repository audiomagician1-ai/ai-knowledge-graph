# 环境变量管理

## 概述

环境变量（Environment Variables）是操作系统层面的键值对配置机制，进程在启动时从父进程或系统配置中继承这些键值对，并通过标准接口（如 POSIX 的 `getenv()` 函数）读取。在 AI 工程开发中，环境变量专门用于将数据库连接字符串、API 密钥、模型服务端点、批量推理并发数等运行时参数从代码逻辑中剥离出来，使同一份代码能在开发、测试、生产三套环境中无需修改直接运行。

环境变量的概念源自 1979 年 Unix Version 7，由 Ken Thompson 在设计 shell 时引入（Ritchie & Thompson, 1974），最初目的是让用户自定义 `PATH`（可执行文件搜索路径）和 `HOME`（用户主目录）。到 2012 年，Adam Wiggins 发布的《十二要素应用》（The Twelve-Factor App）方法论将"在环境中存储配置"列为第三要素（Wiggins, 2012），明确规定代码与配置必须严格分离，该方法论迄今已被 Heroku、Google Cloud、AWS Elastic Beanstalk 等主流云平台作为标准最佳实践引用。

对于 AI 工程师而言，环境变量管理的重要性体现在：当调用 OpenAI、Anthropic 或本地部署的 Ollama 服务时，API 端点和密钥若硬编码在 Python 脚本中，极易随代码提交泄露到 GitHub 公开仓库。GitHub 官方安全报告（2023）显示，其秘密扫描功能每天在公开仓库中发现超过 **100,000 条**泄露凭证，涉及 AWS 访问密钥、OpenAI API Key、Stripe 支付密钥等超过 **200 种**凭证类型。正确使用环境变量则可从源头彻底规避此风险。

值得深入思考的问题：如果你的团队已经将一个含有 API Key 的 `.env` 文件提交到私有 Git 仓库，仅仅删除该文件并重新推送是否足够安全？为什么 Git 历史的不可变性（immutability）特性使得这一做法存在持续性风险，正确的补救流程（包括 `git filter-branch` 或 `git-filter-repo` 工具的使用以及强制密钥轮换）应该是什么？

## 核心原理

### 环境变量的作用域与继承机制

每个进程拥有独立的环境变量副本，子进程在 `fork()` 时从父进程完整继承环境，但子进程对环境的修改不会反向影响父进程。这解释了为什么在终端执行 `export MY_VAR=value` 后，当前 shell 及其启动的所有 Python 进程都能读到 `MY_VAR`，但关闭终端后该变量消失——它只存在于该 shell 进程的内存中。要使变量跨会话持久化，必须将 `export` 语句写入 `~/.bashrc`（Bash）或 `~/.zshrc`（Zsh）等 shell 配置文件。

进程间的环境变量继承关系可以用以下层次优先级公式描述：

$$P_{\text{effective}} = P_{\text{system}} \cup P_{\text{user}} \cup P_{\text{shell}} \cup P_{\text{process}}$$

其中各符号含义如下：$P_{\text{system}}$ 来自 `/etc/environment` 等系统全局配置文件，优先级最低；$P_{\text{user}}$ 来自 `~/.profile` 或 `~/.bash_profile` 等用户级配置；$P_{\text{shell}}$ 来自当前会话 `export` 语句；$P_{\text{process}}$ 为进程内通过 `os.environ["KEY"] = "VALUE"` 显式设置的变量，优先级最高，可覆盖所有上层同名变量。理解这一层次结构，是调试"为什么我设置了变量但程序读不到"问题的关键。

在 Linux 系统上，可以通过读取 `/proc/<PID>/environ` 文件（其中 `<PID>` 为目标进程的进程号）来查看任意运行中进程的完整环境变量快照，格式为 null 字节分隔的键值对序列，这一机制由 POSIX 标准（IEEE Std 1003.1-2017）明确规范（IEEE, 2017）。

### .env 文件与 python-dotenv 库

在 AI 项目中，最常见的管理模式是将所有配置写入项目根目录的 `.env` 文件，格式为每行一个 `KEY=VALUE`，然后用 `python-dotenv` 库（2013 年首发布，当前版本 1.0.1，PyPI 月下载量超过 **3,000 万次**）在程序启动时加载：

```python
from dotenv import load_dotenv
import os

load_dotenv()  # 默认读取当前目录的 .env 文件
api_key = os.getenv("OPENAI_API_KEY", "未设置")
```

`os.getenv()` 的第二个参数为默认值，可防止变量未设置时返回 `None` 导致的空指针错误。**关键操作**：`.env` 文件必须加入 `.gitignore`，而项目应提供 `.env.example` 文件（内含变量名但不含实际值）供团队成员参考。`python-dotenv` 的加载优先级规则为：已存在的系统环境变量优先于 `.env` 文件中的同名变量，除非使用 `load_dotenv(override=True)` 强制覆盖。

一个典型的 AI 工程项目 `.env.example` 文件内容如下：

```bash
# OpenAI 配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MODEL_ENDPOINT=https://api.openai.com/v1

# 向量数据库
PINECONE_API_KEY=
PINECONE_INDEX_NAME=my-index-prod

# 运行时参数
MAX_WORKERS=4
LLM_TEMPERATURE=0.7
DEBUG_MODE=false
APP_ENV=development
```

### 变量命名规范与类型转换

环境变量的值在操作系统层面**全部为字符串类型**，这是一个经常被忽视的事实。POSIX 标准（IEEE Std 1003.1-2017）明确规定环境变量值为以 null 字节结尾的字符序列，不存在整数或布尔的原生类型（IEEE, 2017）。当需要配置整型的并发线程数或布尔型的调试开关时，必须手动进行类型转换：

```python
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
DEBUG_MODE  = os.getenv("DEBUG_MODE", "false").lower() == "true"
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
```

命名规范上，AI 工程领域约定俗成使用全大写字母加下划线（SCREAMING_SNAKE_CASE），并用前缀区分来源：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`HUGGINGFACE_TOKEN` 是各平台官方使用的标准名称，遵循这些名称可让许多框架（如 LangChain 0.1+、LlamaIndex 0.10+）自动识别并注入，无需额外配置。此外，AWS SDK（boto3）约定使用 `AWS_ACCESS_KEY_ID` 与 `AWS_SECRET_ACCESS_KEY`，Google Cloud SDK 约定使用 `GOOGLE_APPLICATION_CREDENTIALS` 指向服务账号 JSON 文件路径——这些均属于行业标准命名，不应自创同义变量名以免破坏框架的自动发现机制。

### 多环境配置管理

生产级 AI 项目通常维护多套环境配置文件：`.env.development`、`.env.testing`、`.env.production`。通过读取 `APP_ENV` 变量决定加载哪套配置：

```python
env = os.getenv("APP_ENV", "development")
load_dotenv(f".env.{env}")
```

在 Docker 容器化部署场景中，环境变量通过 `docker run -e KEY=VALUE` 或 `docker-compose.yml` 的 `environment` 字段注入，完全不依赖 `.env` 文件，这是容器与本地开发的核心差异。以 Docker Compose 为例，典型配置如下：

```yaml
services:
  llm-api:
    image: my-llm-app:1.0
    env_file:
      - .env.production
    environment:
      - APP_ENV=production
      - MAX_WORKERS=8
```

在 Kubernetes 环境中，推荐使用 `Secret` 对象存储敏感凭证，通过 `envFrom.secretRef` 将整个 Secret 批量注入 Pod 的环境变量，而非将明文写入 `ConfigMap`。Kubernetes Secret 默认以 Base64 编码存储（注意：这不是加密，只是编码），生产环境应配合 AWS Secrets Manager、HashiCorp Vault 或 Google Secret Manager 等专用密钥管理系统使用。

## 关键公式与模型

### 优先级叠加模型

上文已介绍层次优先级公式 $P_{\text{effective}} = P_{\text{system}} \cup P_{\text{user}} \cup P_{\text{shell}} \cup P_{\text{process}}$，在实际调试中，可将其理解为"后加载的配置覆盖先加载的同名配置"。对于 `python-dotenv`，加载顺序为：

1. 操作系统环境（最先，优先级最高）
2. `.env.{APP_ENV}` 特定环境文件（使用 `override=False` 时被系统变量覆盖）
3. `.env` 通用文件（最后加载，优先级最低）

若使用 `override=True`，则顺序反转，`.env` 文件中的值将强制覆盖系统变量，适用于本地开发需要隔离测试的场景。

### 密钥暴露面量化模型

为了量化环境变量管理不当的风险，引入**密钥暴露面**（Secret Exposure Surface，SES）概念。在一个有 $n$ 名开发者、代码库历史提交数为 $c$、仓库克隆频率为 $r_{\text{clone}}$（次/月）的团队中，若密钥以明文硬编码存在，则理论上的泄露风险面为：

$$\text{SES} = n \times c \times r_{\text{clone}}$$

反之，若使用环境变量且密钥仅存储于各自本地或 Secrets Manager，则 $\text{SES} \approx 0$（理论上仅受本地机器入侵风险影响）。

例如，一个 10 人团队、1,000 次历史提交、每月被克隆 50 次的公开仓库，硬编码 API Key 的 $\text{SES} = 10 \times 1000 \times 50 = 500{,}000$，风险极高。即便仓库设为私有，仍需考虑内部人员误操作或仓库意外公开的场景，SES 模型依然适用于量化内部风险评估。

### 密钥轮换频率模型

对于需要定期轮换的 API Key（如 OpenAI 企业账号建议每 90 天轮换），可定义**密钥有效性衰减函数**：

$$V(t) = V_0 \cdot e^{-\lambda t}$$

其中 $V_0$ 为初始安全系数（设为 1.0），$\lambda$ 为泄露风险增长率（与密钥暴露范围、团队规模正相关），$t$ 为距上次轮换的时间（天）。当 $V(t)$ 降至预设阈值 $V_{\min}$（如 0.2）时，即触发强制轮换流程。例如，对于一个高暴露场景（$\lambda = 0.02$），代入公式可得轮换周期为：

$$t^* = \frac{\ln(V_0 / V_{\min})}{\lambda} = \frac{\ln(1.0 / 0.2)}{0.02} \approx 80.5 \text{ 天}$$

这与行业通行的 90 天轮换周期基本吻合，印证了该模型对实际策略的合理性描述。

## 实际应用

### 案例一：LangChain RAG 应用的多环境配置实践

以一个典型的检索增强生成（RAG）应用为例，该应用需要同时管理 OpenAI API 密钥、Pinecone 向量数据库凭证以及 Redis 缓存连接字符串。项目结构如下：

```
rag-app/
├── .env.example          # 提交到 Git（含变量名，不含值）
├── .env.development      # 本地开发用，加入 .gitignore
├── .env.testing          # CI/CD 测试环境，通过 GitHub Actions Secrets 注入
├── .env.production       # 生产环境，由 AWS Secrets Manager 动态生成
├── config.py             # 集中式配置加载模块
└── main