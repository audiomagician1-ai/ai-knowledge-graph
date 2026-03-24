---
id: "singleton"
concept: "单例模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 5
is_milestone: false
tags: ["设计模式"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 41.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 单例模式

## 概述

单例模式（Singleton Pattern）是一种创建型设计模式，其定义精确而严格：**一个类在整个程序生命周期内只允许存在唯一一个实例，并提供一个全局访问点来获取该实例**。单例模式由GoF（Gang of Four）在1994年出版的《Design Patterns: Elements of Reusable Object-Oriented Software》中正式系统化，是23种经典设计模式中实现频率最高、也最容易被误用的模式之一。

单例模式的诞生源于对全局状态管理的需求。在早期面向对象系统中，开发者频繁遇到这样的问题：某些资源（如数据库连接、日志记录器、配置文件读取器）若被多次实例化，会造成资源浪费、状态不一致或竞争条件。单例模式通过将构造函数私有化，强制所有调用方共享同一个对象，从根本上解决了这类问题。

在AI工程领域，单例模式的重要性尤为突出。一个机器学习推理服务中，模型加载（通常占用数GB内存）若每次请求都重新实例化，系统将在秒级崩溃。单例模式确保模型只加载一次，所有推理请求共享同一模型实例，是AI服务稳定运行的基础保障。

---

## 核心原理

### 三要素结构

单例模式的实现必须同时满足三个结构性要求：
1. **私有静态实例变量**：在类内部保存唯一实例，声明为 `private static`。
2. **私有构造函数**：禁止外部通过 `new` 关键字创建实例。
3. **公有静态访问方法**：通常命名为 `getInstance()`，是获取实例的唯一合法入口。

以Python为例，标准实现如下：

```python
class ModelManager:
    _instance = None  # 私有静态实例变量

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

上述代码中，`__new__` 方法在每次调用 `ModelManager()` 时都会执行，但仅在 `_instance` 为 `None` 时才真正创建新对象，后续调用直接返回已有实例。

### 懒汉式与饿汉式

单例的实例化时机分为两种策略，具有截然不同的性能特征：

- **懒汉式（Lazy Initialization）**：首次调用 `getInstance()` 时才创建实例。优点是节省启动时间和内存；缺点是在多线程环境下，若两个线程同时判断 `_instance is None`，可能创建两个实例，产生**竞争条件（Race Condition）**。
- **饿汉式（Eager Initialization）**：类加载时立即创建实例。优点是天然线程安全；缺点是即使从未使用该单例，也会占用资源。

### 线程安全的双重检验锁定

在多线程AI服务中（如多Worker的Flask/FastAPI服务），必须使用**双重检验锁定（Double-Checked Locking）**保证单例的线程安全性：

```python
import threading

class ModelManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:          # 第一次检验（性能优化）
            with cls._lock:
                if cls._instance is None:  # 第二次检验（安全保证）
                    cls._instance = super().__new__(cls)
        return cls._instance
```

第一次检验避免每次调用都进入加锁区域（锁竞争开销极大）；第二次检验在锁保护下确认实例仍未创建。这种"check-lock-check"模式将锁的开销从O(n)次请求降低到仅初始化阶段的1次。

---

## 实际应用

**AI模型推理服务中的单例**

在生产级AI系统中，`ModelManager` 通常设计为单例，内部持有已加载的神经网络权重。以一个ResNet-50模型为例，其权重文件约97MB，加载到GPU显存需要约3-5秒。若每次HTTP推理请求都重新加载，QPS（每秒查询数）将低于1。使用单例后，模型仅在服务启动时加载一次，推理延迟可降至毫秒级。

**配置管理器**

AI训练脚本中，超参数配置（学习率、batch size、模型架构参数）通常存储在YAML文件中。将配置读取器设计为单例，确保整个训练流程中所有模块（数据加载器、模型构造器、优化器）读取的是同一份配置，避免因多次解析文件导致的参数不一致问题。

**日志系统**

Python的标准库 `logging` 模块中，`logging.getLogger(name)` 本身就是单例模式的体现——对同一个 `name` 调用多次 `getLogger()`，始终返回同一个Logger对象，这保证了分布式训练中日志的集中汇聚。

---

## 常见误区

**误区一：将单例等同于全局变量**

单例不是全局变量的面向对象包装。全局变量在Python中可被任意重新赋值，缺乏保护机制。单例通过私有构造函数和受控访问点，提供了**类型安全**和**延迟初始化**能力。此外，单例可以继承接口、被Mock替换（用于单元测试），而全局变量无法做到这一点。

**误区二：多进程环境下单例依然唯一**

这是AI工程中最危险的误解。在使用 `multiprocessing` 或Gunicorn多进程部署时，每个进程拥有独立的内存空间，单例**在每个进程内唯一，但进程间各有各的实例**。若需要跨进程共享状态（如共享模型权重），必须使用共享内存（`multiprocessing.shared_memory`）或外部存储（Redis），单例模式本身无法解决跨进程问题。

**误区三：单例模式天然线程安全**

仅实现了基本的 `_instance is None` 检查的懒汉式单例在多线程下是不安全的。在CPython中，由于GIL（全局解释器锁）的存在，纯Python操作通常不会出现问题，但在Jython、PyPy或C扩展中GIL不存在，未加锁的单例会产生真实的竞争条件。养成使用 `threading.Lock` 的习惯是专业实践的基本要求。

---

## 知识关联

**与设计模式概述的关系**：设计模式概述中介绍了创建型、结构型、行为型三大分类。单例模式是创建型模式中规则最严格的一种——它不仅规定对象如何创建，还规定对象的数量上限为1。理解单例模式的"实例数量控制"思想，是后续学习工厂模式（控制对象创建方式）和对象池模式（控制实例数量上限为N）的重要对比基础。

**与依赖注入（DI）的关系**：在现代AI工程框架（如FastAPI + 依赖注入容器）中，单例模式常通过DI容器实现，即将单例实例注册为"scoped singleton"，由框架统一管理生命周期，而非在类内部手动实现 `_instance` 逻辑。这种方式让单例更易测试和替换，是从手动单例走向框架级依赖管理的演进路径。
