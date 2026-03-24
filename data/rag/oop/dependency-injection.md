---
id: "dependency-injection"
concept: "依赖注入"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 6
is_milestone: false
tags: ["设计"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 依赖注入

## 概述

依赖注入（Dependency Injection，简称 DI）是一种将对象所依赖的外部资源从对象内部创建改为由外部传入的设计模式。其核心思想是：一个类不应该自己负责实例化它所需要的依赖对象，而应该通过构造函数、属性或方法参数接收这些依赖。这一模式是 SOLID 原则中依赖倒置原则（DIP）的具体实现方式——高层模块依赖抽象接口，而不是依赖具体实现类。

依赖注入的概念由 Martin Fowler 在 2004 年的文章《Inversion of Control Containers and the Dependency Injection pattern》中正式命名和系统化阐述。在此之前，该模式已经以"控制反转（IoC）"的名称存在于 Spring 等框架的早期实践中。Fowler 指出，IoC 过于宽泛，DI 才是准确描述这种"依赖关系由外部注入"特征的术语。

在 AI 工程场景中，依赖注入的价值尤为突出。一个机器学习推理服务往往需要切换不同的模型后端（如 TensorFlow、PyTorch、ONNX Runtime），若模型加载逻辑硬编码在业务类内部，替换成本极高。通过 DI，推理类只依赖抽象的 `ModelBackend` 接口，具体的 `TorchBackend` 或 `ONNXBackend` 由外部注入，使得 A/B 测试和模型热替换变得可行。

## 核心原理

### 三种注入方式

依赖注入有三种标准实现形式，各有其适用场景：

**构造函数注入（Constructor Injection）** 是最推荐的方式。依赖项在类实例化时通过构造函数传入，使对象一旦创建便处于完整可用状态。以 Python 为例：

```python
class InferenceService:
    def __init__(self, model_backend: ModelBackend, logger: Logger):
        self._backend = model_backend
        self._logger = logger
```

构造函数注入使依赖关系一目了然，且依赖项为 `final`（或 Python 中的 `__slots__`），防止运行时被意外替换。

**属性注入（Property/Setter Injection）** 适用于可选依赖，即存在合理默认值的场景。缺点是对象可能在依赖未完全设置前被调用，需要额外的空值检查。

**方法注入（Method Injection）** 仅在某次特定方法调用需要某个依赖时使用，例如 `process(data, validator: Validator)` 中的 `validator` 只在该次调用有效，不作为对象的长期状态。

### 依赖倒置与接口抽象

DI 要真正发挥作用，必须配合接口（抽象基类）使用。注入的不应是具体类，而应是抽象契约：

```python
from abc import ABC, abstractmethod

class EmbeddingModel(ABC):
    @abstractmethod
    def encode(self, text: str) -> list[float]: ...

class OpenAIEmbedding(EmbeddingModel):
    def encode(self, text: str) -> list[float]:
        # 调用 OpenAI API
        ...

class LocalSentenceTransformer(EmbeddingModel):
    def encode(self, text: str) -> list[float]:
        # 本地模型推理
        ...
```

`RAGPipeline` 类在构造时接收 `EmbeddingModel` 类型的参数，无论注入 `OpenAIEmbedding` 还是 `LocalSentenceTransformer`，其内部逻辑完全不变。这正是依赖倒置原则的精髓。

### 依赖注入容器

当项目中依赖层级复杂时（A 依赖 B，B 依赖 C、D），手动管理注入顺序变得繁琐。依赖注入容器（DI Container）自动解析依赖图并完成实例化。Python 生态中常用的 DI 框架包括 `dependency-injector`（GitHub stars 超过 3000）和 `injector`。以 `dependency-injector` 为例：

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    embedding_model = providers.Singleton(
        OpenAIEmbedding,
        api_key=config.openai.api_key
    )
    rag_pipeline = providers.Factory(
        RAGPipeline,
        embedding_model=embedding_model
    )
```

`Singleton` 提供者确保全局只创建一个 `OpenAIEmbedding` 实例（适合昂贵的模型加载），`Factory` 则每次请求创建新实例（适合无状态的处理管道）。

## 实际应用

**AI 推理服务的模型切换**：在生产 RAG 系统中，`RetrieverService` 通过构造函数注入接收 `VectorStore` 接口，测试时注入 `InMemoryVectorStore`，生产时注入 `PineconeVectorStore`，两套代码路径完全共享业务逻辑。

**单元测试中的 Mock 注入**：这是 DI 最直接的工程收益。若 `DataProcessor` 内部硬编码 `self.db = PostgresClient()`，测试时必须启动真实数据库。通过 DI，测试代码传入 `MockDatabase`，使测试在毫秒级完成且无需任何外部服务：

```python
def test_data_processor():
    mock_db = MockDatabase(return_data=[{"id": 1}])
    processor = DataProcessor(database=mock_db)  # 注入 mock
    result = processor.run()
    assert result == expected
```

**LLM 客户端抽象**：构建支持多 LLM 供应商的 Agent 框架时，定义 `LLMClient` 抽象接口，`OpenAIClient`、`AnthropicClient`、`LocalLlamaClient` 分别实现。Agent 类通过 DI 接收具体客户端，切换供应商无需修改 Agent 业务逻辑，满足开闭原则。

## 常见误区

**误区一：将依赖注入与依赖注入框架混为一谈**。DI 是一种设计模式，不需要任何框架即可实践——手动在调用处传入依赖对象本身就是 DI。`dependency-injector` 等框架只是自动化了依赖图的组装过程，对于小型项目，手动组装（即"穷人的 DI"，Poor Man's DI）往往更清晰。切勿因"没有用框架"而认为自己没有使用依赖注入。

**误区二：构造函数注入导致"构造函数爆炸"时应加参数**。当一个类的构造函数需要注入 7、8 个依赖时，真正的问题通常是该类违反了单一职责原则，应当拆分类而非容忍过长的依赖列表。依赖注入暴露了设计问题，但它本身不是问题所在。

**误区三：Service Locator 模式与依赖注入等价**。Service Locator 通过全局注册表（如 `ServiceLocator.get(EmbeddingModel)`）在类内部主动拉取依赖，类仍然控制着依赖获取过程。而 DI 是被动接收，外部推送依赖。Service Locator 的隐患在于依赖关系被隐藏在方法体内，无法从构造函数签名直接看出类的全部依赖，使代码可维护性下降。

## 知识关联

**与 SOLID 原则的关系**：依赖注入是依赖倒置原则（DIP，SOLID 中的 D）的落地机制，同时促进了开闭原则（OCP）——通过注入新的实现类扩展行为，而不修改已有类。单一职责原则（SRP）与 DI 相互强化：职责单一的类通常依赖较少，DI 的构造函数也更整洁。

**在 AI 工程架构中的位置**：掌握 DI 后，可以进一步理解 Clean Architecture 中的端口与适配器（Ports & Adapters）模式，其中"端口"对应抽象接口，"适配器"对应通过 DI 注入的具体实现。这一架构在构建可测试、可替换模型后端的 AI 系统时是主流选择。此外，Python 的 `FastAPI` 框架内置了基于类型注解的 DI 系统（`Depends()`），理解 DI 原理是高效使用该特性的前提。
