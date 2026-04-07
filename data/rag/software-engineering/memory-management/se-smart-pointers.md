---
id: "se-smart-pointers"
concept: "智能指针"
domain: "software-engineering"
subdomain: "memory-management"
subdomain_name: "内存管理"
difficulty: 2
is_milestone: true
tags: ["C++"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
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

# 智能指针

## 概述

智能指针是C++标准库提供的RAII包装类，用于自动管理堆内存的生命周期。与原始指针（raw pointer）不同，智能指针在其析构函数中自动调用`delete`或`delete[]`，确保堆上分配的对象在智能指针离开作用域时被正确释放，从根本上消除了忘记调用`delete`导致的内存泄漏问题。

智能指针的概念由Bjarne Stroustrup在1984年提出雏形，并随C++11标准（2011年正式发布）进入`<memory>`头文件，成为标准库的正式组成部分。C++11引入了`unique_ptr`、`shared_ptr`和`weak_ptr`三种智能指针，同时废弃了C++98中存在设计缺陷的`auto_ptr`。在此之前，Boost库已提供类似实现长达数年，C++标准委员会基于Boost的实践经验完成了标准化设计。

智能指针解决了C++手动内存管理中最常见的两类错误：内存泄漏（分配后忘记释放）和悬空指针（对象已释放但指针仍被使用）。现代C++ Core Guidelines明确建议：除非有极特殊的性能需求，否则应始终使用智能指针替代原始指针进行堆内存管理。

---

## 核心原理

### unique_ptr：独占所有权

`unique_ptr<T>`表示对一个堆对象的**独占所有权**，任何时刻只能有一个`unique_ptr`实例指向同一个对象。其内存开销与原始指针完全相同（sizeof为8字节，在64位系统上），运行时也不存在引用计数的维护成本。由于所有权是独占的，`unique_ptr`**禁止拷贝构造和拷贝赋值**（编译期删除），只允许通过`std::move()`转移所有权：

```cpp
auto p1 = std::make_unique<int>(42);
auto p2 = std::move(p1); // p1变为nullptr，p2接管所有权
```

`make_unique<T>`是创建`unique_ptr`的推荐方式，自C++14起可用，避免了直接使用`new`时可能产生的异常安全问题。

### shared_ptr：共享所有权与引用计数

`shared_ptr<T>`允许多个指针实例共同拥有同一个堆对象，内部维护一个**控制块（control block）**，其中包含两个计数器：强引用计数（strong ref count）和弱引用计数（weak ref count）。当强引用计数降为0时，被管理对象的析构函数被调用并释放其内存；当弱引用计数也降为0时，控制块本身才被释放。

`shared_ptr`的拷贝操作会原子性地递增引用计数，因此线程安全地共享所有权，但对其所指向的对象本身的访问并不是线程安全的。`shared_ptr`的大小是原始指针的两倍（16字节），因为它同时持有指向对象的指针和指向控制块的指针。推荐使用`std::make_shared<T>()`而非`new`来创建，因为`make_shared`将对象与控制块分配在同一块内存中，减少了一次堆分配。

### weak_ptr：打破循环引用

`weak_ptr<T>`是`shared_ptr`的非拥有型观察者，它不增加强引用计数，因此不阻止被管理对象的析构。`weak_ptr`的核心用途是**打破`shared_ptr`之间的循环引用**。例如，双向链表或父子节点互相持有`shared_ptr`时，会导致引用计数永远无法降至0，形成内存泄漏——将其中一个方向改为`weak_ptr`即可解决。

使用`weak_ptr`时必须先调用`lock()`方法，它返回一个`shared_ptr`，若原对象已被析构则返回空的`shared_ptr`：

```cpp
std::weak_ptr<Node> weak = shared_node;
if (auto locked = weak.lock()) {
    // 安全访问对象
}
```

---

## 实际应用

**场景一：工厂函数返回资源所有权**  
游戏引擎中加载纹理资源时，工厂函数`loadTexture()`返回`unique_ptr<Texture>`，明确向调用方传递所有权语义。调用方可以将其存入容器，或通过`std::move`转移给场景管理器，整个过程无需手动释放。

**场景二：多个模块共享同一数据**  
网络服务器中，一个`Connection`对象可能同时被`SessionManager`和`LoggingModule`持有。使用`shared_ptr<Connection>`，两个模块均可安全持有引用，当两者都不再需要时，连接对象自动析构，无需协调谁负责释放。

**场景三：Observer模式中的weak_ptr**  
事件系统中，`EventBus`持有观察者列表。若用`shared_ptr`存储观察者，则观察者对象永远不会被析构。改用`weak_ptr`存储后，`EventBus`在通知前调用`lock()`检查对象是否仍存活，已析构的观察者自动从通知列表中跳过，这是现代C++中实现观察者模式的标准做法。

---

## 常见误区

**误区一：用原始指针初始化多个shared_ptr**  
以下代码会导致双重释放（double-free）崩溃：
```cpp
int* raw = new int(10);
shared_ptr<int> p1(raw);
shared_ptr<int> p2(raw); // 错误！两个独立的控制块，各自引用计数为1
```
两个`shared_ptr`拥有独立的控制块，各自认为自己是唯一所有者，当两者都析构时，`delete raw`被调用两次。正确做法是只从`make_shared`或从同一个`shared_ptr`拷贝。

**误区二：在构造函数中使用shared_from_this失败**  
若某类继承`enable_shared_from_this<T>`，在其构造函数内调用`shared_from_this()`会抛出`std::bad_weak_ptr`异常，因为控制块尚未建立。`shared_from_this()`只能在对象已经被`shared_ptr`管理之后调用，通常在成员函数中使用而非构造函数中。

**误区三：shared_ptr的引用计数不等同于线程安全**  
引用计数的增减操作本身是原子的，但这只保证了`shared_ptr`对象的管理操作线程安全，**不保证**对所指向对象数据成员的并发读写安全。两个线程同时修改同一个`shared_ptr<vector<int>>`所指向的`vector`，仍然需要额外的互斥锁保护。

---

## 知识关联

**前置概念**：理解智能指针需要熟悉栈与堆的区别——智能指针本身分配在栈上，而它所管理的对象位于堆上。智能指针的析构函数在栈展开（stack unwinding）时自动调用，这是其自动释放堆内存的物理基础。

**后续概念**：`unique_ptr`只支持移动不支持拷贝的设计，是学习**移动语义**（move semantics）和右值引用的绝佳切入点——`std::move`将`unique_ptr`从左值转为右值引用，触发移动构造函数而非拷贝构造函数。智能指针本身也是**RAII（Resource Acquisition Is Initialization）**原则的最典型实现案例：资源（堆内存）在构造时获取，在析构时释放，将资源的生命周期与对象的生命周期绑定，这一原则同样适用于文件句柄、互斥锁等一切需要配对操作的资源。