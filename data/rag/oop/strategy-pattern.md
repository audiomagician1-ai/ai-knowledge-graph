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
quality_tier: "pending-rescore"
quality_score: 41.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 策略模式

## 概述

策略模式（Strategy Pattern）是一种行为型设计模式，其核心定义是：将一组可互换的算法分别封装成独立的类，使它们可以在运行时动态替换，而调用方无需修改自身代码。GoF（四人帮）在1994年出版的《设计模式：可复用面向对象软件的基础》中将策略模式列为23种经典模式之一，正式奠定了其理论地位。

策略模式解决的根本问题是"算法爆炸"——当一个类需要支持多种行为变体时，若用条件分支（if-else/switch）直接堆砌，随着变体增加，代码的圈复杂度（Cyclomatic Complexity）会呈线性增长，维护成本急剧上升。策略模式通过将每种算法提取到独立的策略类中，使得新增算法只需添加新类，无需改动已有代码，严格遵守开闭原则（Open/Closed Principle）。

在AI工程领域，策略模式尤为重要：模型选择策略、提示词构造策略、结果后处理策略往往需要在同一系统中并存且可配置切换，策略模式为这类多算法共存场景提供了清晰的架构骨架。

## 核心原理

### 三角色结构

策略模式由三个核心角色构成，缺一不可：

- **Strategy（抽象策略接口）**：定义所有具体策略必须实现的统一方法签名，例如 `execute(context: Context) -> Result`。
- **ConcreteStrategy（具体策略类）**：实现抽象接口，封装具体算法逻辑。例如 `GreedySearchStrategy`、`BeamSearchStrategy`、`SamplingStrategy` 分别封装不同的文本生成搜索算法。
- **Context（上下文类）**：持有一个策略对象的引用，将客户端请求委托给当前策略执行，自身不含算法逻辑。

三者之间的关系是：Context 依赖 Strategy 接口而非具体类，这是策略模式实现解耦的关键所在——依赖倒置原则（DIP）的直接体现。

### 运行时切换机制

Context 通常暴露一个 `set_strategy(strategy: Strategy)` 方法，允许在对象生命周期内随时替换策略。以Python为例：

```python
class InferenceContext:
    def __init__(self, strategy: SearchStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SearchStrategy):
        self._strategy = strategy

    def run(self, input_ids):
        return self._strategy.search(input_ids)
```

调用方可在同一个 `InferenceContext` 实例上先用 `GreedySearchStrategy` 快速生成草稿，再切换为 `BeamSearchStrategy(beam_width=5)` 进行精细搜索，整个切换过程对 Context 内部逻辑零侵入。

### 策略与参数的边界

策略模式将**算法逻辑**与**算法参数**都封装在具体策略类内部。`BeamSearchStrategy` 持有 `beam_width`、`length_penalty` 等字段，这些参数在构造时注入（构造器注入或工厂方法创建），而不是暴露给 Context。这一设计使得策略对象本身是自洽的——同一个 Context 调用同一个方法，行为完全由当前策略决定，无需 Context 了解参数细节。

### UML结构与依赖方向

```
Client → Context ——(持有)——→ <<interface>> Strategy
                                    ↑         ↑         ↑
                          ConcreteStrategyA  B         C
```

依赖箭头严格单向：Context 知道 Strategy 接口，但不知道任何 ConcreteStrategy；ConcreteStrategy 知道 Strategy 接口契约，但彼此完全独立。这是策略模式能够支持无限扩展的结构保证。

## 实际应用

### AI推理引擎的解码策略

Hugging Face Transformers 库的 `GenerationMixin` 本质上就是策略模式的工业实现。`generate()` 方法根据参数（`do_sample=True/False`、`num_beams`）在运行时选择 `GreedySearchLogitsProcessor`、`BeamSearchScorer` 等策略对象。用户可以通过继承 `LogitsProcessor` 接口注入自定义解码策略，无需修改 Transformers 核心代码。

### 电商价格计算

一个经典教学案例：购物车 `ShoppingCart` 作为 Context，持有 `DiscountStrategy` 接口引用。具体策略包括 `NoDiscountStrategy`（无折扣）、`PercentageDiscountStrategy(rate=0.8)`（八折）、`BuyTwoGetOneFreeStrategy`（买二赠一）。结算时调用 `cart.calculate()` 即可，促销活动切换只需替换策略对象，不改动 `ShoppingCart` 类。

### RAG系统的检索策略

在检索增强生成（RAG）系统中，`Retriever` 可持有一个 `RetrievalStrategy` 接口，具体策略包括 `BM25Strategy`（基于词频统计）、`DenseEmbeddingStrategy`（基于向量相似度）、`HybridStrategy(alpha=0.5)`（混合检索，权重可调）。系统可根据查询类型在运行时切换策略，事实性问题走 BM25，语义推理问题走向量检索。

## 常见误区

### 误区一：把策略模式当成简单的函数指针替换

初学者常认为"把函数作为参数传入"就等同于策略模式。实际上，策略模式要求策略是**对象**而非裸函数——策略对象可以持有状态（如 `BeamSearchStrategy` 维护 beam 候选列表）、可以实现多个相关方法（初始化、执行、收尾）、可以参与依赖注入容器管理。Python中用 `Callable` 传参只能处理无状态的简单算法替换，无法承载复杂策略的完整生命周期。

### 误区二：Context 直接持有所有策略实例

错误做法是在 Context 构造时同时创建所有可能的策略对象备用。这违反了策略模式的意图——Context 应该只持有**当前活跃策略**的引用，策略的创建和选择应由工厂或客户端负责。若 Context 知晓全部 ConcreteStrategy 类型，则 Context 对具体策略产生了直接依赖，新增策略时仍需修改 Context，策略模式的扩展优势荡然无存。

### 误区三：混淆策略模式与模板方法模式

两者都处理算法变体问题，但策略模式用**组合**（Context 包含 Strategy 对象），模板方法模式用**继承**（子类重写父类中的抽象步骤）。策略模式在运行时可以动态切换算法，而模板方法的变体在编译时通过类继承确定，无法运行时替换。在AI工程中需要根据请求参数动态选择算法的场景，必须使用策略模式而非模板方法。

## 知识关联

**与设计模式概述的关系**：策略模式是理解"面向接口编程"和"组合优于继承"这两条设计原则的最直观载体。在学完设计模式基本原则后，策略模式是第一个将这两条原则同时落地的具体模式，代码结构最简洁，适合作为行为型模式的入门案例。

**通向命令模式**：命令模式将"操作请求"封装为对象，与策略模式将"算法"封装为对象在结构上相似（都有 `execute()` 方法），但命令模式额外支持操作的撤销（`undo()`）、队列化和日志记录，而策略模式的策略对象通常是无副作用的纯算法。区分二者的关键问题是：封装的目的是**替换算法**（策略模式）还是**延迟执行与撤销**（命令模式）。

**通向状态模式**：状态模式与策略模式的UML结构几乎完全相同——都有 Context 持有一个接口引用，都支持运行时替换。区别在于**谁来触发切换**：策略模式的切换由外部客户端主动调用 `set_strategy()` 完成，而状态模式的切换由状态对象自身或 Context 在特定条件下自动触发，代表对象生命周期中的状态流转逻辑。
