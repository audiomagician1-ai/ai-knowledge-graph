---
id: "strategy-pattern"
concept: "策略模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 5
is_milestone: false
tags: ["设计模式"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 策略模式

## 概述

策略模式（Strategy Pattern）是一种行为型设计模式，其核心思想是将一族可互换的算法分别封装为独立的类，并让这些类共享同一接口，使得算法可以在运行时动态替换，而不影响调用该算法的客户端代码。策略模式的本质在于"将变化的行为从不变的结构中分离出来"——客户端持有一个策略接口的引用，具体使用哪种算法取决于运行时传入的策略对象。

策略模式由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式提出，并归入行为型模式类别。在AI工程领域，策略模式的价值尤为突出：当需要在不同的模型推理策略（如贪婪解码、束搜索、Top-K采样）之间动态切换时，策略模式可以避免在主流程代码中堆砌大量`if-else`分支，使推理模块保持对扩展开放、对修改关闭的状态。

策略模式的意义在于它直接解决了"同一任务存在多种实现方式，且需要在运行时灵活选择"的工程问题。相比直接在客户端硬编码算法逻辑，策略模式将每一种算法的变化隔离在各自的策略类中，单独修改某一策略时不会波及其他策略或上下文类，显著降低了AI系统中算法迭代的风险。

---

## 核心原理

### 三个角色的组成结构

策略模式由三个核心角色构成：

- **Context（上下文类）**：持有一个`Strategy`接口的引用，负责与客户端交互，并在需要时调用策略对象执行算法。上下文类本身不实现具体算法。
- **Strategy（策略接口）**：定义所有具体策略必须实现的统一方法签名，例如`execute(data)`。
- **ConcreteStrategy（具体策略类）**：每个子类实现策略接口中定义的算法，例如`GreedySearchStrategy`、`BeamSearchStrategy`、`TopKSamplingStrategy`。

以Python伪代码说明结构：

```python
class Strategy(ABC):
    @abstractmethod
    def decode(self, logits): pass

class GreedyStrategy(Strategy):
    def decode(self, logits):
        return argmax(logits)

class BeamSearchStrategy(Strategy):
    def __init__(self, beam_size=5):
        self.beam_size = beam_size
    def decode(self, logits):
        return beam_search(logits, self.beam_size)

class InferenceContext:
    def __init__(self, strategy: Strategy):
        self._strategy = strategy
    def set_strategy(self, strategy: Strategy):
        self._strategy = strategy
    def run(self, logits):
        return self._strategy.decode(logits)
```

上例中，`InferenceContext`可在运行时通过`set_strategy()`切换不同的解码策略，而其自身代码无需改动。

### 开闭原则的具体体现

策略模式严格遵循开闭原则（Open/Closed Principle，OCP）：当需要新增一种解码算法（如Nucleus Sampling）时，只需新建一个实现`Strategy`接口的`NucleusSamplingStrategy`类，不需要修改`InferenceContext`或其他已有策略类的任何一行代码。这与直接使用`if-else`分支的做法形成对比——后者每次新增算法都需要修改主逻辑，引入回归风险。

### 策略的注入方式

策略对象可以通过以下两种方式注入到上下文中：

1. **构造函数注入**：在创建上下文对象时传入策略，适合策略在对象生命周期内不变的场景，如`InferenceContext(strategy=BeamSearchStrategy(beam_size=4))`。
2. **Setter注入（运行时切换）**：通过`set_strategy()`方法在运行过程中替换策略，适合需要根据输入数据动态选择算法的场景，例如对短文本使用贪婪解码、对长文本使用束搜索。

---

## 实际应用

### AI模型推理中的解码策略切换

在大语言模型（LLM）推理系统中，解码阶段需要支持多种采样策略。以Hugging Face Transformers库为例，其`GenerationMixin`类内部实际上使用了类似策略模式的机制，通过`generation_config`参数在`do_sample=False`（贪婪/束搜索）和`do_sample=True`（随机采样）之间切换行为。将这一机制显式地用策略模式重构后，可以将`TopKSampling`、`TemperatureSampling`、`MinPSampling`各自封装为独立策略类，新增采样方式无需触碰核心推理循环。

### 数据预处理流水线中的归一化策略

在AI工程的数据预处理阶段，同一批数据可能需要根据下游任务选择不同的归一化方式：图像分类任务使用ImageNet均值`[0.485, 0.456, 0.406]`进行标准化，而目标检测任务使用像素值直接缩放到`[0, 1]`区间。将这两种归一化方式分别封装为`ImageNetNormStrategy`和`MinMaxNormStrategy`，并由`PreprocessContext`持有策略引用，可以在同一套预处理框架中支持多任务场景，切换时只需调用`set_strategy()`，不改变流水线其余部分。

### 强化学习中的探索策略

在强化学习Agent的训练中，ε-贪婪探索策略和UCB（Upper Confidence Bound）探索策略具有完全不同的实现逻辑，但对Agent的接口完全一致——都是接收当前状态，返回动作选择。使用策略模式后，`RLAgent`类只依赖`ExplorationStrategy`接口，可以在训练早期使用高ε值的`EpsilonGreedyStrategy`，训练后期切换为`UCBStrategy`，两者通过相同的`select_action(state, q_values)`接口对Agent透明。

---

## 常见误区

### 误区一：策略模式等同于简单的函数替换

部分开发者认为策略模式可以直接用传递函数指针（或Python中的高阶函数）替代，认为两者等价。实际上，当具体策略需要**携带内部状态**时（例如`BeamSearchStrategy`需要维护`beam_size`参数，或者`AdaptiveSamplingStrategy`需要记录历史采样分布），封装为类的策略对象能够存储这些状态，而单纯的函数指针做不到。策略模式适用于"算法有配置参数或内部状态"的场景，简单无状态的情况才考虑高阶函数替代方案。

### 误区二：把所有if-else都改成策略模式

策略模式适用的前提是"同一接口下存在多个可互换的算法变体"。如果一段代码的条件分支处理的是完全不同的业务逻辑（如参数校验和异常处理），强行套用策略模式只会增加类的数量而不带来任何灵活性收益。引入策略模式的判断标准是：这些分支是否代表同一种操作的不同实现方式，且未来是否有独立扩展的需求。

### 误区三：策略模式与模板方法模式混淆

策略模式通过**组合（composition）** 实现算法替换——上下文类持有策略对象的引用；而模板方法模式通过**继承（inheritance）** 实现——子类重写父类中定义的算法步骤。两者的区分在于关系的类型：如果算法切换发生在运行时，且切换的是整个算法实体，应选择策略模式；如果算法骨架固定，只需在编译期由子类填充特定步骤，则使用模板方法模式。在AI推理系统中，解码算法的整体逻辑差异较大，适合策略模式；而"前向传播→损失计算→反向传播"的训练骨架固定，适合模板方法模式。

---

## 知识关联

策略模式建立在**设计模式概述**中介绍的"面向接口编程而非面向实现编程"原则之上，正是这一原则驱动了将具体算法抽象为`Strategy`接口的设计决策。没有接口抽象，策略模式的可替换性无从实现。

学习策略模式后，**命令模式**是顺理成章的延伸方向：命令模式同样封装"行为"，但其封装的是一次完整的请求（包括接收者、操作和参数），并支持请求的撤销、队列化和日志记录，而策略模式封装的是无需记录历史的算法逻辑。两者的区别在于意图——策略关注"如何做"，命令关注"做什么以及何时做"。**状态模式**同样与策略模式结构相似（都使用组合持有行为对象），但状态模式的核心是"对象在不同状态下表现不同行为，且状态之间存在自动转换逻辑"，而策略模式的策略切换完全由外部客户端主动控制，策略对象之间彼此独立，不存在状态迁移关系。