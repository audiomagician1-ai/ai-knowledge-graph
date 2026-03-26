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
quality_tier: "B"
quality_score: 48.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
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

模板方法模式（Template Method Pattern）是一种行为型设计模式，由Gang of Four（GoF）在1994年的著作《设计模式：可复用面向对象软件的基础》中正式定义。其核心思想是：在一个抽象基类中定义算法的固定骨架（即"模板方法"），将算法中可变的步骤声明为抽象方法或钩子方法，由子类负责具体实现，而骨架本身不可被子类改变。

模板方法模式解决的典型问题是：多个子类中存在相同的执行流程，但每个步骤的具体逻辑各有差异。如果直接在每个子类中重写完整算法，会产生大量重复代码；而把整个算法集中在父类中，又无法兼容子类的差异化需求。模板方法通过"不变部分上移、可变部分下沉"的策略，精准解决了这一矛盾。

在AI工程场景中，模板方法模式高度契合机器学习训练流程的结构。例如，各类模型的训练过程通常都遵循"数据预处理 → 构建模型 → 训练循环 → 评估指标"这一固定骨架，而每个步骤的实现因模型类型不同而各异。使用该模式可以将训练流程标准化，同时保留每种模型的自定义能力。

---

## 核心原理

### 模板方法的结构组成

模板方法模式包含两个角色：**抽象类（AbstractClass）** 和 **具体类（ConcreteClass）**。抽象类中包含三类方法：

- **模板方法（Template Method）**：定义算法骨架，通常用 `final` 修饰（Java中）防止子类覆盖，调用其他步骤方法的顺序固定不变。
- **抽象方法（Abstract Method）**：强制子类必须实现的步骤，无默认逻辑。
- **钩子方法（Hook Method）**：在抽象类中提供默认实现（通常为空或返回布尔值），子类可选择性地覆盖，用于控制模板流程的条件分支。

伪代码结构如下：

```python
class AbstractTrainer:
    def train(self):          # 模板方法，固定骨架
        self.load_data()
        self.build_model()
        self.run_epochs()
        if self.need_evaluate():   # 钩子方法控制流程
            self.evaluate()

    def load_data(self): pass      # 抽象方法
    def build_model(self): pass    # 抽象方法
    def run_epochs(self): pass     # 抽象方法

    def need_evaluate(self):       # 钩子方法，默认返回True
        return True
```

### 好莱坞原则与控制反转

模板方法模式体现了"好莱坞原则"（Hollywood Principle）：**"不要打电话给我们，我们会打电话给你"**。父类（抽象类）掌控整体调用顺序，子类不主动驱动算法，而是被父类的模板方法在适当时机回调。这与依赖注入等控制反转机制在思路上一致，但实现手段是继承而非组合。这意味着子类只能影响被授权可覆盖的步骤，无法干预其他步骤或改变步骤的执行顺序。

### 抽象方法与钩子方法的区别

这是理解模板方法模式精细度的关键区分：

| 特征 | 抽象方法 | 钩子方法 |
|------|----------|----------|
| 子类是否必须实现 | 是，强制覆盖 | 否，可选覆盖 |
| 父类是否有默认实现 | 无 | 有（通常为空实现） |
| 典型用途 | 差异化核心逻辑 | 控制流程开关或扩展点 |

在AI训练框架中，`build_model()` 通常设计为抽象方法（每种模型架构必须自定义），而 `on_epoch_end()` 则适合设计为钩子方法（默认不做任何事，需要时子类覆盖用于日志记录或Early Stopping）。

---

## 实际应用

### PyTorch Lightning 中的模板方法模式

PyTorch Lightning 框架的 `LightningModule` 类是模板方法模式在AI工程中最典型的工业级实现。其 `Trainer.fit()` 方法内部调用固定的训练骨架，而 `training_step()`、`validation_step()`、`configure_optimizers()` 被设计为用户必须在子类中实现的抽象方法。`on_train_epoch_end()` 则是典型的钩子方法，框架默认为空实现，用户可选择覆盖以插入自定义逻辑。开发者无需关心训练循环的分布式同步、梯度累积等底层流程，因为这些已被固化在模板方法中。

### 数据处理流水线

在数据ETL（Extract-Transform-Load）流水线中，可以定义如下骨架：

```python
class DataPipeline:
    def run(self):           # 模板方法
        raw = self.extract()
        cleaned = self.transform(raw)
        self.load(cleaned)

class CSVPipeline(DataPipeline):
    def extract(self): ...   # 从CSV读取
    def transform(self, data): ...
    def load(self, data): ...

class APIDataPipeline(DataPipeline):
    def extract(self): ...   # 从REST API拉取
    def transform(self, data): ...
    def load(self, data): ...
```

两种流水线共享"提取→转换→加载"的执行顺序，各自实现差异化的数据源和处理逻辑，新增数据源类型时只需新增子类，无需改动骨架代码，符合开闭原则。

---

## 常见误区

### 误区一：钩子方法越多越好

部分开发者为追求"灵活性"，在模板方法中设置过多钩子方法，导致父类代码膨胀，子类需要了解大量可选覆盖点才能正确使用。模板方法模式的价值在于**约束**，过多的钩子方法会削弱固定骨架的约束力，使模式退化为毫无结构的策略堆积。通常，一个模板方法中抽象方法加钩子方法的总数不宜超过5～7个，否则应考虑拆分为多个模板类。

### 误区二：模板方法等同于普通的父类方法调用

普通的父类方法调用允许子类通过方法覆盖改变任意步骤，包括模板方法本身；而模板方法必须用 `final`（Java）或约定（Python中以单下划线前缀提示）**禁止子类覆盖骨架**。若不加保护，子类可能覆盖 `train()` 模板方法本身，破坏算法结构，使模式形同虚设。

### 误区三：与策略模式混淆

模板方法模式通过**继承**在编译时静态绑定算法变体，子类一旦创建就确定了各步骤的行为；而策略模式通过**组合**在运行时动态切换整个算法。如果需要在同一对象的生命周期内切换算法步骤的实现，应使用策略模式；如果算法骨架固定且子类变体在创建时已知，则模板方法更合适。在AI工程中，如果同一个训练器需要在不同优化器之间动态切换，策略模式更佳；若每种模型类型始终使用固定的训练逻辑，模板方法更恰当。

---

## 知识关联

**依赖前置概念**：模板方法模式的实现完全依赖**继承**机制——子类通过继承获得模板方法，并通过方法覆盖（override）实现抽象步骤。没有继承，"父类控制流程、子类实现细节"的结构无法成立。同时需要理解**抽象类**与**接口**的区别：模板方法必须放在抽象类中（需要有方法体），而非接口（不能包含有逻辑的模板方法）。

**与其他设计模式的关联**：模板方法模式与**工厂方法模式**常结合使用——模板方法的某个步骤可以是工厂方法，负责创建该步骤所需的对象。在AI框架中，`build_model()` 步骤既是模板方法中的抽象步骤，也可以是一个工厂方法，负责实例化不同的神经网络架构对象。理解这两种模式的协作，有助于设计出结构清晰、扩展性强的AI训练框架基类。