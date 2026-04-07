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
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 单例模式

## 概述

单例模式（Singleton Pattern）是一种创建型设计模式，其核心约束是：**一个类在整个程序运行期间只能被实例化一次**，且提供一个全局访问点供外部代码使用该唯一实例。这一模式由 GoF（Gang of Four）在1994年出版的《Design Patterns: Elements of Reusable Object-Oriented Software》中正式定义，是23种经典设计模式中最简单却最容易被误用的一种。

单例模式的起源需求来自于系统资源管理：当某个对象代表一种稀缺或共享资源时（例如数据库连接池、日志记录器、配置文件读取器），允许多个实例共存会导致资源竞争、状态不一致或内存浪费。在AI工程中，模型配置管理器、推理引擎实例、GPU资源调度器等组件通常以单例形式存在，确保整个推理流水线共享同一套配置和同一个调度状态。

单例模式的重要性不仅在于节省资源，更在于它强制实施了"全局唯一状态"的语义约束。当日志系统或指标收集器以单例形式运行时，任意模块写入的日志都流向同一个目标，避免了日志分散在多个对象中导致追踪困难的问题。

---

## 核心原理

### 私有化构造函数

单例模式的第一道屏障是将类的构造函数设为 `private`，从根本上禁止外部代码通过 `new` 关键字创建实例。类本身持有一个 `private static` 类型的自身引用作为唯一实例的存储位置。外部只能通过一个公开的静态方法（通常命名为 `getInstance()`）获取实例，该方法在实例不存在时负责创建，在实例已存在时直接返回缓存的引用。

```python
class ModelConfigManager:
    _instance = None  # 私有静态实例引用

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

上例中 Python 通过重写 `__new__` 方法实现单例，`_instance` 充当内部缓存，保证多次调用 `ModelConfigManager()` 返回同一对象的内存地址。

### 懒汉式与饿汉式

单例模式有两种初始化时机策略，各有适用场景：

- **饿汉式（Eager Initialization）**：类加载时立即创建实例，代码最简单，天然线程安全，但若实例始终未被使用则浪费资源。适合初始化代价低或确定会使用的场景，如 AI 系统启动时必须加载的全局日志器。

- **懒汉式（Lazy Initialization）**：首次调用 `getInstance()` 时才创建实例，节省启动开销，但在多线程环境下需要额外的同步保护。AI 推理服务中延迟加载大型语言模型权重（可能高达数十 GB）正是典型的懒汉式应用场景。

### 线程安全实现：双重检查锁定

在多线程环境下，朴素的懒汉式会产生竞态条件：两个线程同时判断 `_instance is None` 为真，导致创建两个实例。**双重检查锁定（Double-Checked Locking, DCL）** 通过两次判空加一次加锁将竞争窗口缩到最小：

```python
import threading

class InferenceEngine:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:            # 第一次检查（无锁，性能优先）
            with cls._lock:
                if cls._instance is None:    # 第二次检查（有锁，安全保证）
                    cls._instance = cls()
        return cls._instance
```

第一次检查避免了每次调用都争抢锁的性能损耗；第二次检查在持有锁后再次验证，防止两个线程都通过第一次检查后重复创建。这种模式在高并发 AI 服务中尤为重要，因为推理引擎的初始化耗时可能超过数秒。

---

## 实际应用

**AI 模型配置管理器**：在一个包含多个微服务的 AI 系统中，模型超参数（batch size、温度系数、最大 token 数）通常由单例配置管理器统一持有。当调用 `ConfigManager.get_instance().get("temperature")` 时，所有服务模块读取到完全一致的值，避免了配置漂移问题。

**GPU 显存池管理**：TensorFlow 和 PyTorch 内部均使用类似单例的机制管理 CUDA 上下文。以 PyTorch 为例，`torch.cuda` 模块在首次调用时初始化全局 CUDA 上下文，后续操作全部复用该上下文，确保显存分配和释放在统一的上下文下进行，避免多上下文导致的显存碎片。

**训练日志聚合器**：在分布式训练场景中，单节点内的单例日志器汇聚来自数据加载线程、前向传播、反向传播各阶段的指标（loss、accuracy、gradient norm），统一格式化后写入 TensorBoard 或 MLflow，保证时间戳的全局单调递增性。

---

## 常见误区

**误区一：将单例等同于全局变量**

单例模式与全局变量虽然都提供全局访问，但存在本质区别。全局变量在程序启动时即占用内存且无法控制初始化顺序；单例的实例化时机可精确控制（懒汉式），且构造函数私有化使得实例生命周期由类本身管理，外部无法随意替换。此外，单例类可以实现接口、被继承（受限），支持依赖注入框架对其进行 mock，而裸全局变量做不到这些，这在 AI 工程的单元测试中差别显著。

**误区二：单例在多进程环境下仍然全局唯一**

Python 多进程（`multiprocessing`）中，每个子进程拥有独立的内存空间，父进程中的单例实例**不会**被子进程继承（fork 方式除外，且 fork 后的实例是拷贝而非共享）。因此在使用 `torch.multiprocessing` 进行数据并行训练时，若将 GPU 资源管理器设计为单例，需意识到每个训练进程实际上各自持有一个独立的单例实例，进程间通信必须通过显式的 IPC 机制（共享内存、队列等）完成，而非依赖"全局唯一性"。

**误区三：单例天然解决线程安全问题**

单例模式仅保证实例的唯一性，不保证实例内部方法的线程安全。若单例的状态（如内部计数器、缓存字典）被多线程并发读写，依然需要在方法内部使用互斥锁或使用线程安全的数据结构（如 `threading.local`、`queue.Queue`）。很多 AI 工程师错误地认为"我用了单例，并发就安全了"，从而在推理日志器中出现日志条目乱序或计数错误的 bug。

---

## 知识关联

单例模式属于**创建型模式**，与工厂模式（Factory Pattern）的关系紧密：工厂方法内部常常维护一个单例注册表（Registry），通过类名映射到已创建的实例，避免重复创建重量级对象。在 AI 工程中，模型工厂（`ModelFactory.get("bert-base")`）的内部缓存逻辑本质上就是单例思想的扩展——从"全局唯一"泛化为"按键唯一"，也称为**多例模式（Multiton Pattern）**。

从前置知识**设计模式概述**延伸而来，单例模式是学习设计模式时最先接触的完整实现案例：它清晰展示了"封装变化点"（实例化过程被封装进 `getInstance()`）和"面向接口编程"两大 OOP 原则如何协同作用。掌握单例模式的线程安全实现（特别是 DCL 的 `volatile`/内存可见性问题）为后续学习并发设计模式（如读写锁模式、生产者-消费者模式）奠定了具体的代码直觉基础。