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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

"组合优于继承"（Composition over Inheritance）是面向对象设计中的一条重要原则，最早由 Gang of Four（GoF）在 1994 年出版的《设计模式：可复用面向对象软件的基础》中明确提出。其核心主张是：在需要复用代码或扩展功能时，优先选择将功能封装在独立对象中并通过引用来使用，而不是通过建立父子继承关系来实现。

这一原则的产生背景是工程界对"深层继承树"所带来的脆弱性和耦合度问题的反思。当继承层次超过 2~3 层时，修改父类往往会在子类中引发意想不到的连锁反应，导致代码难以维护。组合方式通过"has-a"（拥有）关系替代"is-a"（是一种）关系，使得各功能模块可以独立变化、独立测试，大幅降低了模块间的耦合度。

在 AI 工程领域，模型管道、数据预处理器、特征工程组件等通常需要频繁替换和组合，继承结构会严重限制这种灵活性。组合方式允许在运行时动态切换组件，例如在同一推理流水线中轻松替换不同的向量化策略或评分模块，这正是该原则在实际工程中价值最突出的场景。

---

## 核心原理

### 1. "has-a" 关系与委托机制

组合的实现依赖于**对象委托**（Delegation）：一个类持有另一个类的实例，并将特定行为的调用转发给该实例。以 Python 为例：

```python
class TextVectorizer:
    def vectorize(self, text): ...

class DocumentProcessor:
    def __init__(self, vectorizer: TextVectorizer):
        self.vectorizer = vectorizer  # 组合关系
    
    def process(self, doc):
        return self.vectorizer.vectorize(doc)
```

`DocumentProcessor` 不继承 `TextVectorizer`，而是持有其引用。当需要更换向量化策略时，只需在构造时传入不同实现，而无需修改 `DocumentProcessor` 本身。这一模式直接对应 GoF 书中"针对接口编程，而非针对实现编程"的设计准则。

### 2. 脆弱基类问题（Fragile Base Class Problem）

继承的最大风险之一是**脆弱基类问题**：父类的任何修改都可能无意中破坏所有子类的行为。例如，若 `BaseModel` 的 `fit()` 方法内部调用顺序从 `preprocess → train` 改为 `train → preprocess`，则所有重写了 `fit()` 的子类可能全部失效。这一问题在大型 AI 工程项目中尤为严重，因为基类往往由不同团队维护。

组合方式将功能分散在独立的小对象中，每个对象只对自身的行为负责，父子依赖链被彻底消除，修改某个功能模块不会影响其他模块。

### 3. 里氏替换原则（LSP）的天然满足

里氏替换原则（Liskov Substitution Principle，1987 年由 Barbara Liskov 提出）要求子类必须能在任何使用父类的场合透明替换父类。继承关系极容易违反 LSP——例如 `Square` 继承 `Rectangle` 时，`setWidth` 的语义就会产生冲突。组合不建立父子类型关系，因此从根本上规避了违反 LSP 的风险，接口的契约由显式定义的协议（Protocol）或抽象基类保证，而非隐式的继承链。

### 4. 开放-封闭原则的支持方式

组合模式天然契合**开放-封闭原则（OCP）**：通过注入不同的组件对象来扩展行为，而无需修改已有类的代码。以 AI 流水线为例，若需新增一种特征归一化策略，只需实现新的 `Normalizer` 类并注入 `Pipeline`，`Pipeline` 自身代码不做任何改动。继承方式则需要新增子类并可能重写多个方法，风险面更大。

---

## 实际应用

### AI 推理流水线的动态组装

在 Scikit-learn 的 `Pipeline` 类中，每个处理步骤（如 `TfidfVectorizer`、`StandardScaler`、`LogisticRegression`）都是独立对象，通过组合方式嵌入流水线。用户可以在不修改 `Pipeline` 源码的情况下，任意替换或增删步骤，这正是组合原则的经典实现。

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipe = Pipeline([
    ('scaler', StandardScaler()),   # 组合：持有 StandardScaler 实例
    ('clf', LogisticRegression())   # 组合：持有 LogisticRegression 实例
])
```

### 强化学习环境包装器

OpenAI Gym 的 `Wrapper` 体系使用**装饰器模式**（本质上是组合），通过 `ObservationWrapper`、`RewardWrapper` 等类持有原始 `env` 对象的引用，而非继承具体环境类。这使得研究人员可以将多个包装器嵌套叠加（如先归一化观察值，再裁剪奖励），而每个包装器逻辑保持独立可测试。

---

## 常见误区

### 误区一：组合意味着完全不能用继承

组合优于继承并非禁止继承，而是限制其适用范围。继承应仅在**真正存在"is-a"语义**时使用，例如 `Dog` 确实是 `Animal` 的一种。当继承仅仅是为了复用某几个方法时，就应改用组合。经验法则是：若子类需要重写父类超过 50% 的方法，几乎可以确定这是滥用继承。

### 误区二：组合会导致代码冗长，委托调用太繁琐

Python 的 `__getattr__` 魔法方法和现代语言的 Mixin 机制可以大幅减少委托代码的重复性。此外，Python 3.10+ 的结构化模式匹配和 Protocol 类型提示使组合关系的表达更加简洁。代码量略有增加换来的是模块独立可测试的巨大工程收益，这笔账在中大型项目中始终是合算的。

### 误区三：继承的多态性无法用组合实现

组合配合**策略模式**（Strategy Pattern）可以完整实现继承的多态效果。将可变行为抽象为接口（或 Python 的 Protocol），不同实现类满足该接口，通过依赖注入传入，就可以在运行时实现行为切换。与继承多态不同的是，组合多态可以在不修改调用方代码的情况下，在**运行时**而非**编译时**完成切换，灵活性更高。

---

## 知识关联

理解**继承**（包括单继承与多重继承的机制、MRO 方法解析顺序）是掌握本原则的必要前提——只有清楚继承在什么情况下会带来脆弱基类问题和菱形继承冲突，才能真正感受到组合方案的优越性。

组合优于继承与**策略模式**、**装饰器模式**、**依赖注入**等设计模式高度关联：这些模式都是该原则的具体实现形态。在 AI 工程中，**面向接口编程**（通过 Python `abc.ABC` 或 `typing.Protocol` 定义契约）是安全使用组合的技术基础，确保注入的组件能够被正确替换而不破坏调用方逻辑。