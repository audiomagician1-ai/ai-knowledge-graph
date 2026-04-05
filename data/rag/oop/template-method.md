---
id: "template-method"
concept: "模板方法模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 4
is_milestone: false
tags: ["template", "hook", "design-pattern"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 模板方法模式

## 概述

模板方法模式（Template Method Pattern）是一种行为型设计模式，由GoF（Gang of Four）在1994年出版的《设计模式：可复用面向对象软件的基础》中正式提出。其核心定义是：**在抽象类中定义一个算法的骨架（模板方法），将算法中某些具体步骤延迟到子类中实现**，从而让子类在不改变整体算法结构的前提下，重写特定步骤的行为。

该模式的结构极为简洁，仅需两层角色：一个抽象类（AbstractClass）负责定义模板方法和各步骤的抽象接口，若干具体子类（ConcreteClass）分别实现那些可变步骤。模板方法本身通常用 `final` 关键字修饰（Java中），防止子类覆盖整个算法流程，只允许对指定的"钩子步骤"进行重写，这正是该模式与单纯继承的本质区别。

在AI工程场景中，许多训练流程、数据处理管道都呈现出"固定流程 + 可变实现"的结构。例如机器学习模型的训练流程通常包括：数据预处理→模型初始化→前向传播→计算损失→反向传播→参数更新，这六步的顺序固定，但每步的具体算法因模型而异，天然契合模板方法模式的应用场景。

---

## 核心原理

### 模板方法与抽象步骤的分层设计

模板方法本身是一个**具体方法（非抽象）**，它调用若干基本操作（primitive operations）。这些基本操作分为两类：

- **抽象方法（Abstract Method）**：子类必须实现的步骤，例如 `compute_loss()`。
- **钩子方法（Hook Method）**：在抽象类中提供默认空实现，子类可选择性重写，例如 `on_epoch_end()`。

伪代码结构如下：

```python
class ModelTrainer:
    def train(self):          # 模板方法，定义骨架
        self.load_data()      # 具体方法（不变）
        self.init_model()     # 抽象方法（子类必须实现）
        for epoch in range(self.epochs):
            self.forward_pass()   # 抽象方法
            self.compute_loss()   # 抽象方法
            self.backward_pass()  # 具体方法（不变）
            self.on_epoch_end()   # 钩子方法（可选重写）
```

子类 `CNNTrainer` 和 `TransformerTrainer` 分别实现 `init_model()`、`forward_pass()`、`compute_loss()`，而 `load_data()` 和 `backward_pass()` 的逻辑由抽象父类统一提供。

### 好莱坞原则与控制反转

模板方法模式体现了"好莱坞原则"（Hollywood Principle）："不要找我们，我们会找你"（Don't call us, we'll call you）。控制权始终在抽象类（父类）的模板方法手中，父类在执行过程中**主动调用**子类重写的步骤，而不是子类决定调用顺序。这与普通继承中子类主导调用不同——普通继承允许子类任意组合父类方法，模板方法模式则将调用顺序锁死在父类中。

### 钩子方法的精细控制

钩子方法的存在让模板方法模式拥有更细粒度的灵活性。一个布尔类型的钩子可以控制算法中某个步骤是否执行：

```python
def should_validate(self) -> bool:
    return True   # 默认执行验证

def train(self):
    ...
    if self.should_validate():
        self.validate()
```

子类若想跳过验证步骤，只需重写 `should_validate()` 返回 `False`，无需触碰训练主流程。PyTorch Lightning框架中的 `LightningModule` 正是大量运用了此技术，其 `training_step()`、`validation_step()`、`configure_optimizers()` 均为用户必须或可选重写的钩子/抽象方法，而整个训练循环的调度逻辑由 `Trainer` 类封装。

---

## 实际应用

### AI训练框架中的应用

PyTorch Lightning 的 `LightningModule` 是工业级模板方法模式的典型案例。用户继承该抽象类后，只需实现 `training_step(batch, batch_idx)` 和 `configure_optimizers()` 这两个抽象方法，`fit()` 方法（模板方法）自动完成分布式调度、混合精度训练、梯度裁剪等骨架逻辑。Scikit-learn 的 `BaseEstimator` 同理，`fit()` 方法构成骨架，具体学习算法在子类（如 `LinearRegression`、`RandomForestClassifier`）中实现。

### 数据预处理管道

在ETL（Extract-Transform-Load）数据管道设计中，提取、变换、加载三步的执行顺序固定，但变换逻辑因数据源而异。可以定义如下抽象类：

```python
class DataPipeline:
    def run(self):          # 模板方法
        raw = self.extract()
        cleaned = self.transform(raw)
        self.load(cleaned)
    
    def extract(self): ...  # 抽象
    def transform(self, data): ...  # 抽象
    def load(self, data):   # 具体，写入统一存储
        db.save(data)
```

`ImagePipeline` 和 `TextPipeline` 分别实现 `extract()` 和 `transform()`，共用同一个 `load()` 实现，避免重复代码。

---

## 常见误区

### 误区一：把所有步骤都设为抽象方法

初学者常将模板方法中的每一步都定义为抽象方法，迫使每个子类重写所有步骤，失去了代码复用的意义。正确做法是：**只有真正需要变化的步骤才设为抽象方法或钩子**，不变的公共逻辑应在抽象父类中直接实现。若所有步骤均为抽象，该模式退化为普通策略接口，丧失了"骨架复用"的核心价值。

### 误区二：模板方法应该设为 public

将模板方法设为 `public` 并不总是错误，但允许子类重写模板方法本身则是严重错误。在Java中应使用 `final` 修饰模板方法，在Python中可通过命名约定（双下划线）或文档约束防止覆盖。一旦子类覆盖了模板方法，整个算法骨架将被破坏，模式退化为无结构的多态重写。

### 误区三：模板方法模式等同于策略模式

两者都处理算法变化，但结构不同：模板方法模式通过**继承**在编译时确定变体，子类与父类紧耦合；策略模式通过**组合**在运行时动态替换算法对象，耦合度更低。当算法变体数量固定且变化不频繁时选用模板方法；当需要运行时切换算法，或变体数量庞大时，策略模式更合适。

---

## 知识关联

**与继承的关系**：模板方法模式是继承机制的一种**结构化约束**。普通继承允许子类自由重写任何方法，而模板方法模式通过将骨架方法标记为 `final`、将可变步骤标记为 `abstract`，对继承的使用加以规范，使父子类的职责边界清晰可见。

**与其他设计模式的对比**：工厂方法模式（Factory Method）本质上是模板方法模式的特殊形式——它将"创建对象"这一单一步骤延迟给子类实现，而不是延迟多个步骤。理解模板方法模式后，能更快把握工厂方法模式中 `createProduct()` 被设计为抽象方法的深层逻辑。**策略模式**解决同类问题但采用组合而非继承，两者是理解行为型模式谱系的重要对照组。

**在AI工程实践中的延伸**：掌握模板方法模式后，阅读 PyTorch Lightning、Keras（`Model.fit()` 机制）、Hugging Face Trainer 等主流AI框架的源码时，能迅速识别其抽象类骨架与用户可重写钩子之间的分层关系，大幅降低框架学习成本。