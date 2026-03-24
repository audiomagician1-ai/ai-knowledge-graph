---
id: "builder-pattern"
concept: "建造者模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 3
is_milestone: false
tags: ["builder", "fluent-api", "design-pattern"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 建造者模式

## 概述

建造者模式（Builder Pattern）是一种创建型设计模式，专门用于分步骤构建由多个可选部件组成的复杂对象，同时将对象的**构建过程**与其**最终表示**彻底分离。与工厂模式一次性返回完整对象不同，建造者模式允许客户端代码逐步指定构建步骤，最终通过调用 `build()` 方法获得成品对象。

该模式由 GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式收录，属于23种经典设计模式之一。建造者模式最早的应用场景是文档转换系统——同一份内容可以被"建造"成 PDF、HTML 或纯文本三种不同表示，三种表示共享相同的构建流程，但各自的装配细节不同。

在 AI 工程场景中，建造者模式尤其适合构建"配置对象"。一个大语言模型的推理请求往往包含十几个可选参数：`model`、`temperature`、`max_tokens`、`top_p`、`system_prompt`、`stop_sequences` 等。如果用构造函数传递所有参数，函数签名会极度臃肿且易出错（即所谓的"伸缩构造函数反模式"，Telescoping Constructor Anti-Pattern）。建造者模式将每个参数的赋值封装为独立的链式调用方法，使代码可读性和可维护性大幅提升。

---

## 核心原理

### 四个角色及其职责

建造者模式的标准结构包含四个角色：

| 角色 | 名称 | 职责 |
|------|------|------|
| Product | 产品 | 最终要构建的复杂对象 |
| Builder | 抽象建造者 | 声明构建各部件的抽象方法 |
| ConcreteBuilder | 具体建造者 | 实现构建步骤，维护部件状态 |
| Director | 指挥者 | 定义构建步骤的调用顺序（可选）|

`Director` 不是必须的。在现代"流式建造者"（Fluent Builder）风格中，客户端代码直接调用链式方法，省略 Director，这在 Python 和 Java 中均已成为主流写法。

### 方法链（Method Chaining）实现机制

流式建造者的关键在于每个 `setXxx()` 方法都返回 `self`（Python）或 `this`（Java），从而支持链式调用：

```python
class LLMRequestBuilder:
    def __init__(self):
        self._config = {}

    def model(self, name: str) -> "LLMRequestBuilder":
        self._config["model"] = name
        return self  # 返回自身，支持链式调用

    def temperature(self, t: float) -> "LLMRequestBuilder":
        assert 0.0 <= t <= 2.0, "temperature 必须在 [0.0, 2.0] 之间"
        self._config["temperature"] = t
        return self

    def max_tokens(self, n: int) -> "LLMRequestBuilder":
        self._config["max_tokens"] = n
        return self

    def build(self) -> dict:
        if "model" not in self._config:
            raise ValueError("model 字段为必填项")
        return self._config.copy()

# 客户端调用
request = (LLMRequestBuilder()
           .model("gpt-4o")
           .temperature(0.7)
           .max_tokens(1024)
           .build())
```

注意 `build()` 方法中的校验逻辑——这是建造者模式的另一大优势：可以在对象正式生成前集中做参数合法性检查，而不是将校验分散在对象各处。

### 建造者模式与工厂模式的本质区别

工厂模式解决的问题是"**创建哪种类型**的对象"（多态选择），而建造者模式解决的是"**如何一步步装配**同一类对象"（构建过程控制）。具体区分标准如下：

- **参数数量**：当构造参数超过 **4个** 时，业界普遍建议改用建造者模式（来自《Effective Java》第3版 Item 2）。
- **参数可选性**：工厂模式通常所有参数都必须提供；建造者模式天然支持大量可选参数。
- **对象一致性**：建造者可在 `build()` 前做跨字段联合校验，工厂方法无此能力。

---

## 实际应用

### AI 推理管道的 Pipeline 构建

在 AI 工程中，LangChain 框架大量使用建造者风格构建 `Chain` 对象。例如，一个 RAG（检索增强生成）管道可以通过链式调用逐步装配：向量检索器、提示模板、LLM 模型、输出解析器四个组件，最终调用 `.build()` 或 `|` 运算符（LangChain的LCEL语法）组装为可运行管道。每个组件相互独立，替换某一组件不影响其余部分的构建逻辑。

### 神经网络模型配置

PyTorch 生态中的 `torchvision.models` 以及 Hugging Face 的 `TrainingArguments` 类均体现建造者思想。`TrainingArguments` 接收超过 **80个** 可选参数，通过 dataclass 配合默认值实现类似建造者的效果：用户只需显式指定需要修改的字段，其余使用默认值，最终传入 `Trainer` 完成构建。

### 测试数据工厂

在 AI 系统的单元测试中，建造者模式常用于构造测试用的复杂数据对象。例如构建一条包含"用户输入、对话历史、系统提示、工具调用结果"的多轮对话样本时，使用 `ConversationBuilder` 可以针对不同测试场景灵活组合字段，而无需为每种场景单独定义数据结构。

---

## 常见误区

### 误区一：认为所有复杂对象都需要建造者模式

建造者模式引入了额外的 Builder 类，增加代码量约 30%~50%。对于参数少于 4 个、构建过程简单的对象，直接使用构造函数或工厂方法反而更清晰。过度使用建造者模式会造成"设计模式堆砌"，降低代码可读性。判断标准：构造参数是否超过 4 个，且其中是否有大量可选参数。

### 误区二：将建造者模式与原型模式混淆

原型模式通过**克隆已有对象**来创建新对象（调用 `clone()` 或 `copy.deepcopy()`），适用于对象创建成本高的场景；建造者模式是从**零开始按步骤构造**新对象。两者共同点是都返回复杂对象，但解决路径截然不同。在 AI 场景中，克隆一个已训练的模型权重对象应用原型模式，而组装一个新的推理请求配置应使用建造者模式。

### 误区三：忽略 `build()` 方法中的校验职责

很多初学者将 `build()` 写成仅仅返回 `self._product` 的空壳方法，把校验逻辑放在各个 `setXxx()` 方法中。这会导致无法做**跨字段联合校验**——例如，只有当 `use_beam_search=True` 时 `num_beams` 字段才有意义。这类跨字段约束必须在 `build()` 中统一检查，这正是建造者模式集中校验能力的核心价值所在。

---

## 知识关联

**前置知识衔接**：建造者模式是创建型设计模式家族的成员，与工厂模式共享"封装对象创建逻辑"的出发点。工厂模式处理"创建哪种子类"的多态决策，而建造者模式接管工厂模式无法优雅处理的场景——当同一类产品需要多个可选配置步骤时。理解工厂模式中"客户端不直接调用构造函数"的原则，有助于快速接受建造者模式中"必须通过 `build()` 获取对象"的约束。

**横向关联**：建造者模式产出的对象往往是**不可变对象（Immutable Object）**——一旦 `build()` 返回，对象不再允许修改。这与 Python dataclass 的 `frozen=True` 选项、Java 的 `final` 字段设计一脉相承，在多线程 AI 推理服务中尤其重要，可避免请求配置在并发环境下被意外篡改。
