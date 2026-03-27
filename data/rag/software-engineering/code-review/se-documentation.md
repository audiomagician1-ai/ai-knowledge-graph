---
id: "se-documentation"
concept: "文档实践"
domain: "software-engineering"
subdomain: "code-review"
subdomain_name: "代码审查"
difficulty: 2
is_milestone: false
tags: ["文档"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.536
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 文档实践

## 概述

文档实践（Documentation Practice）是代码审查流程中对文档完整性与质量的系统性检查，具体涵盖三类核心文档：API文档、README文件和架构决策记录（Architecture Decision Record，简称ADR）。审查者在检查代码实现的同时，必须同步验证这三类文档是否准确反映代码的实际行为与设计意图。

文档实践作为正式审查标准可追溯至1990年代开源运动的兴起。Linux内核社区在1991年后逐渐形成了强制要求贡献者附带文档的惯例，GitHub在2008年上线后将README文件置于仓库首页的设计决定，则将README的重要性提升至工程文化层面。ADR由Michael Nygard于2011年在其博客中正式提出格式规范，成为记录架构决策背景与后果的标准工具。

在代码审查中忽视文档质量会导致具体的工程损失：调用方无法正确使用API导致集成错误，新成员无法通过README快速搭建开发环境导致入职时间延长，架构决策未记录导致团队数月后重复讨论同一问题。文档实践的审查目标正是预防这三类问题。

---

## 核心原理

### API文档的审查标准

API文档审查要求每个公开接口必须包含四个具体要素：**功能描述**（该函数做什么）、**参数说明**（每个参数的类型、取值范围、是否必填）、**返回值说明**（包括成功响应的数据结构和所有可能的错误码）、**使用示例**（至少一个可直接复制运行的代码片段）。

以Python为例，符合文档实践标准的函数必须包含docstring，且内容具体如下：

```python
def calculate_discount(price: float, rate: float) -> float:
    """
    计算折扣后的商品价格。

    Args:
        price: 商品原价，单位为元，必须大于 0。
        rate: 折扣率，取值范围 0.0 到 1.0，例如 0.9 表示九折。

    Returns:
        折扣后的价格，保留两位小数。

    Raises:
        ValueError: 当 price <= 0 或 rate 不在 [0, 1] 范围内时抛出。

    Example:
        >>> calculate_discount(100.0, 0.8)
        80.0
    """
```

代码审查中发现API文档缺少`Raises`部分或`Args`类型说明，应标记为必须修复（blocker），而非建议优化（suggestion）。

### README文件的必备结构

README审查遵循"五分钟测试"原则：一名从未接触该项目的工程师，阅读README五分钟后应能独立完成本地环境搭建并运行第一个请求或测试。具体来说，审查者检查README是否包含：**项目用途**（一句话描述）、**环境依赖**（精确到版本号，如`Node.js >= 18.0.0`）、**安装命令**（逐行可复制的shell命令）、**快速开始示例**（最小化的端到端用例）、**配置项说明**（环境变量列表及其含义）。

审查时需特别检查版本号是否与`package.json`、`requirements.txt`等依赖文件保持一致。README中写`Python 3.8`但`requirements.txt`中使用了仅Python 3.10支持的语法，是文档审查应拦截的典型错误。

### 架构决策记录（ADR）的格式与触发条件

ADR采用Michael Nygard定义的标准结构，包含五个固定字段：**标题**（编号+简短描述，如`ADR-0012: 选择PostgreSQL作为主数据库`）、**状态**（Proposed/Accepted/Deprecated/Superseded四选一）、**背景**（决策时面临的具体技术约束）、**决策**（选择了什么方案）、**后果**（该决策带来的正面与负面影响）。

代码审查中，以下三类代码变更必须要求提交对应ADR：引入新的第三方依赖框架、更改服务间通信协议（如从REST改为gRPC）、修改数据库表结构中的不可逆操作（如删除字段）。审查者发现PR中引入了新的消息队列中间件但无对应ADR，应在审查意见中明确要求补充，不得仅凭口头讨论通过。

---

## 实际应用

**场景一：开源库的API文档审查**

某Python HTTP客户端库提交了新增`retry`参数的PR。审查者检查API文档时发现，`retry`参数的docstring只写了"重试次数"，缺少默认值（应标注默认值为`3`）、最大允许值（未说明超过`10`时的行为）和与`timeout`参数的交互说明（重试是否重置超时计时器）。审查者将此标记为blocker，要求文档补充后方可合并。

**场景二：微服务项目的README更新**

团队将认证方式从Basic Auth迁移到JWT，代码PR同时修改了三个微服务的实现。文档实践审查要求：每个服务的README中"认证"章节必须同步更新，移除Basic Auth的curl示例，替换为携带`Authorization: Bearer <token>`头的新示例。审查者逐一核对三个服务的README，发现其中一个服务遗漏更新，要求补充后合并。

**场景三：ADR记录数据库分片决策**

工程团队决定对用户表实施水平分片，相关PR修改了数据访问层代码。按文档实践标准，该PR必须附带ADR，记录以下内容：选择按`user_id`哈希分片而非按地区分片的原因（背景：90%查询按user_id检索）、分片数量定为16的依据（后果：扩容时需重新分片，风险已评估）。没有该ADR，六个月后新成员无从得知为何不能简单地按时间范围分片。

---

## 常见误区

**误区一：代码可以自我说明，API文档是冗余的**

这一观点混淆了"代码说明实现"与"文档说明契约"的区别。函数签名`def process(data, mode=2)`无法告知调用方`mode=2`与`mode=1`的行为差异，也不说明`data`为`None`时是返回空结果还是抛出异常。代码审查要求文档覆盖所有边界行为，而这些边界行为恰好是最难从代码中直接读出的。Stripe的API文档之所以成为行业标杆，正是因为每个参数都有明确的约束描述，而非依赖调用方读懂其服务端源码。

**误区二：ADR只在架构重大变更时才需要编写**

实践中，最昂贵的不是显而易见的大决策，而是那些"当时觉得理所当然"的小决策。例如，选择使用`snake_case`还是`camelCase`作为JSON字段命名风格，两年后团队成员轮换后可能引发争议并导致不一致的新字段出现。ADR的触发阈值应是"三个月后如果看到这段代码，新成员是否会质疑这个选择"，而不是"这是否是一个重大技术决策"。

**误区三：文档更新可以在合并后单独提交**

代码审查实践证明，"稍后补文档"的承诺兑现率极低。GitHub的工程博客数据显示，超过60%的"文档待补充"标签最终未被关闭。正确做法是将文档更新设为PR合并的前置条件（pre-merge requirement），在CI流水线中配置文档覆盖率检查，或在PR模板中加入文档checklist，强制提交者在创建PR时自查文档完整性。

---

## 知识关联

文档实践在代码审查中与**代码注释规范**紧密相关：代码注释解释"为什么这样实现"（面向维护者），而API文档解释"如何使用"（面向调用方），两者审查侧重点不同，不可相互替代。审查者需区分inline comment的充分性检查与API docstring的完整性检查，使用不同的评审标准。

在工具层面，文档实践依赖具体的自动化工具落地：Python项目常用`pydocstyle`在CI中检查docstring格式合规性，JavaScript项目使用`JSDoc`生成API文档并通过`documentation.js`验证覆盖率，ADR管理则常用`adr-tools`命令行工具维护编号连续性和状态流转。了解这些工具的配置方式，是将文档实践从人工审查升级为自动化门禁的关键路径。

文档实践的质量直接影响后续的**代码可维护性度量**：如果ADR缺失，技术债务的来源将难以追溯；如果README不完整，新成员的入职成本将无法准确量化。因此，文档完整性也是工程效能度量体系中的一个独立指标维度。