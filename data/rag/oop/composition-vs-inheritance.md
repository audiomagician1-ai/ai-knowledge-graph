---
id: "composition-vs-inheritance"
concept: "组合优于继承"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 5
is_milestone: false
tags: ["设计"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 组合优于继承

## 概述

"组合优于继承"（Composition Over Inheritance）是面向对象设计中的经典原则，最早由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中明确提出。其核心主张是：当需要复用功能时，优先通过将多个对象组合在一起来实现，而不是通过建立父子类的继承关系。

继承是一种"is-a"关系（狗是动物），组合是一种"has-a"关系（狗拥有行为能力）。继承会在编译时固定类之间的耦合关系，而组合允许在运行时动态替换对象的组成部分。当一个系统频繁使用多层继承时，往往会出现"脆弱基类问题"：修改父类可能无意间破坏所有子类的行为，这是继承的结构性缺陷。

在AI工程的实践中，模型pipeline、Agent框架和数据处理组件的构建高度依赖组合模式。一个LLM推理服务可能需要同时具备"缓存能力""限流能力""日志能力"，若用继承实现，三者的排列组合会爆炸式产生大量子类，而组合只需三个独立组件按需装配。

## 核心原理

### 继承的结构性问题：菱形问题与脆弱基类

继承的最根本局限在于它将"类型层级"与"行为复用"强行绑定。当Python类`C`同时继承`A`和`B`，而`A`和`B`都继承`Base`时，`C`面临菱形继承问题（Diamond Problem），Python通过MRO（Method Resolution Order，C3线性化算法）解决调用顺序，但逻辑上的歧义依然存在。更严重的是脆弱基类问题：若父类`Animal`新增一个方法`breathe()`，所有子类（`Dog`、`Fish`、`Bird`）都会继承这个实现，即使`Fish`的呼吸逻辑完全不同，子类也很容易因为忘记覆盖而静默产生错误行为。

### 组合的实现机制：依赖注入与接口隔离

组合的典型实现方式是**依赖注入**：一个类不自己创建所依赖的对象，而是通过构造函数或方法参数将其传入。以AI推理服务为例：

```python
class InferenceService:
    def __init__(self, model, cache, logger):
        self.model = model      # 可替换为任意模型对象
        self.cache = cache      # 可替换为Redis或内存缓存
        self.logger = logger    # 可替换为不同日志后端
    
    def predict(self, input_data):
        self.logger.log(input_data)
        if self.cache.exists(input_data):
            return self.cache.get(input_data)
        result = self.model.run(input_data)
        self.cache.set(input_data, result)
        return result
```

`InferenceService`本身不继承任何`Model`或`Cache`，它通过持有这些对象的引用来获得其功能。更换底层模型时，只需传入不同的`model`对象，`InferenceService`的代码完全不变。这种灵活性是继承无法提供的。

### 组合与继承的选择判据：里氏替换原则检验

判断应该用继承还是组合，最直接的判据是**里氏替换原则（LSP）**：若B是A的子类，那么任何使用A的地方都必须能无感知地替换为B。若无法满足LSP，说明这个继承关系是错误的，应改用组合。一个典型反例是`Stack`继承`Vector`（Java早期标准库的设计错误）：`Stack`是一种受限的`Vector`，但继承使得`Stack`对象可以调用`insertElementAt()`在任意位置插入元素，破坏了栈的LIFO语义。正确做法是`Stack`内部持有一个`Vector`或`ArrayList`对象（组合），只对外暴露`push`、`pop`、`peek`三个方法。

### 组合的行为扩展：策略模式与装饰器模式

组合是许多设计模式的底层基础。**策略模式**将算法封装成独立对象，运行时通过组合切换：AI模型评估系统可以将`accuracy_fn`、`f1_fn`、`bleu_fn`作为不同策略对象注入评估器，无需为每种指标建立子类。**装饰器模式**则通过层层包裹同接口的对象来叠加功能，Python的`@lru_cache`本质上就是用组合对原函数进行包装，而不是修改函数所属类的继承链。

## 实际应用

**LangChain的链式组件设计**：LangChain框架中`LLMChain`并不继承`LLM`，而是将`llm`、`prompt`、`memory`、`output_parser`作为成员对象持有。用户可以自由替换其中任意一个组件，例如将`OpenAI`替换为`Anthropic`，将`ConversationBufferMemory`替换为`VectorStoreMemory`，无需修改`LLMChain`本身，也无需创建新的子类。

**PyTorch的模型组合**：`nn.Module`鼓励通过将子模块赋值给成员变量来组合网络层，而不是继承已有的网络架构。一个`TransformerBlock`通过组合持有`MultiHeadAttention`和`FeedForward`模块，可以在不同的Transformer变体中被重复组合，而无需建立`BertTransformerBlock`继承`TransformerBlock`这样的继承链。

**AI Agent的能力扩展**：构建一个具备搜索、代码执行、记忆三种能力的Agent时，用继承需要创建`SearchAgent`→`SearchCodeAgent`→`SearchCodeMemoryAgent`三级继承；用组合则是一个`Agent`类持有一个`tools: List[Tool]`列表，在构造时注入所需工具，运行时动态增删工具而不需要修改任何类定义。

## 常见误区

**误区一：认为"永远不要用继承"。** 组合优于继承并非"禁止继承"。当类之间确实存在严格的LSP关系时，继承是合理的。`HTTPException`继承`Exception`是正确的，因为它在所有需要`Exception`的地方都能被合法替换。真正应该避免的是"为了复用代码而继承"，例如为了让`Dog`能使用`Animal`的`eat()`方法而建立继承，此时用组合更清晰。

**误区二：认为组合会导致"接口爆炸"，代码更复杂。** 初学者常认为组合需要写大量的委托代码（`self.cache.get()`、`self.logger.log()`），不如继承直接调用父类方法简洁。但这种"复杂性"是必要的显式依赖声明，继承的"简洁"实际上隐藏了类之间的强耦合。Python的`__getattr__`和`dataclasses`，以及多数语言的接口/协议机制，都可以有效减少组合中的样板代码量。

**误区三：混淆"接口继承"与"实现继承"。** 继承一个抽象基类（ABC）或Protocol来声明"本类实现了某种接口"是完全合理的设计，这叫做接口继承。组合优于继承反对的是**实现继承**：从父类继承具体的方法实现。Python中`class MyModel(nn.Module)`是接口继承（声明本类是一个Module），而`class MyModel(ResNet)`只是为了复用ResNet的forward实现则是应该避免的实现继承。

## 知识关联

理解组合优于继承需要以**继承**为前提：必须先清楚继承中`super()`调用链、方法覆盖和属性查找的具体机制，才能识别出哪些场景下继承会产生脆弱基类问题。MRO和多重继承的复杂性是组合优于继承原则存在价值的直接原因——正是因为继承在多重行为组合场景下的复杂度呈指数增长，组合的线性复杂度才显得尤为重要。

本原则与**依赖倒置原则**（Depend on abstractions, not concretions）紧密配合：组合时应依赖接口而非具体类，才能真正实现运行时可替换性。它也是**策略模式**、**装饰器模式**、**依赖注入容器**等高级设计模式的共同理论基础，掌握本原则后，这些模式的动机和结构会变得非常直观。