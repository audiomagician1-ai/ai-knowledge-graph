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
quality_tier: "pending-rescore"
quality_score: 42.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 智能指针

## 概述

智能指针是C++标准库提供的RAII（Resource Acquisition Is Initialization）包装器，通过将原始指针封装在对象中，使指针的生命周期与对象的作用域绑定，从而实现自动内存释放。当智能指针对象离开作用域时，其析构函数会自动调用`delete`，彻底消除手动`delete`遗漏导致的内存泄漏问题。

智能指针的思想最早可追溯至1994年C++标准委员会的`auto_ptr`提案，但`auto_ptr`因转移语义不清晰、不能与STL容器配合使用等缺陷，在C++11中被废弃（C++17中正式移除）。C++11引入了现代化的三种智能指针：`std::unique_ptr`、`std::shared_ptr`和`std::weak_ptr`，均定义在头文件`<memory>`中，从根本上解决了`auto_ptr`的设计缺陷。

在堆内存管理中，智能指针解决了两类最常见的bug：内存泄漏（忘记`delete`）和悬空指针（`delete`后继续访问）。特别是在有异常抛出的代码路径中，传统的`new/delete`配对极易因异常跳过`delete`而泄漏，而智能指针的析构函数无论正常退出还是异常退出都会被调用。

---

## 核心原理

### unique_ptr：独占所有权

`std::unique_ptr<T>`实现独占语义：同一时刻只有一个`unique_ptr`实例可以持有某块堆内存的所有权。它的拷贝构造函数和拷贝赋值运算符被显式`= delete`，因此无法复制，只能通过`std::move()`转移所有权。

```cpp
std::unique_ptr<int> p1 = std::make_unique<int>(42); // C++14起推荐
std::unique_ptr<int> p2 = std::move(p1); // p1变为nullptr，p2接管
```

`unique_ptr`的运行时开销几乎为零：sizeof(unique_ptr<T>) 与原始指针相同（默认删除器情况下均为8字节），适合绝大多数单一所有权场景。

### shared_ptr：共享引用计数

`std::shared_ptr<T>`通过维护一个**控制块（control block）**实现共享所有权，控制块中包含两个计数器：强引用计数（shared count）和弱引用计数（weak count）。每次拷贝`shared_ptr`，强引用计数加1；每次析构，强引用计数减1；当强引用计数归零时，堆对象被销毁（调用`delete`），但控制块本身需等到弱引用计数也为0才释放。

使用`std::make_shared<T>()`创建`shared_ptr`时，对象和控制块在**同一次内存分配**中完成，比`shared_ptr<T>(new T())`少一次`malloc`调用，也避免了异常安全漏洞。`shared_ptr`本身的大小通常是原始指针的2倍（16字节），因为它需要同时存储数据指针和控制块指针。

### weak_ptr：打破循环引用

`std::weak_ptr<T>`是对`shared_ptr`所管理对象的**非拥有性观察**，它不增加强引用计数，因此不影响对象的生命周期。使用`weak_ptr`前必须通过`lock()`方法尝试获取一个临时`shared_ptr`：

```cpp
std::weak_ptr<Node> wp = sp; // 不增加强引用计数
if (auto locked = wp.lock()) {  // 返回shared_ptr，若对象已销毁则返回nullptr
    locked->doSomething();
}
```

`weak_ptr`最典型的用途是打破双向链表或父子节点之间的**循环引用**。例如，若父节点`shared_ptr<Child>`指向子节点，子节点也用`shared_ptr<Parent>`反向持有父节点，则两者的强引用计数永远不会归零，造成内存泄漏。将其中一个改为`weak_ptr<Parent>`即可解决。

---

## 实际应用

**工厂函数返回值**：工厂函数应返回`unique_ptr`而非裸指针，调用方获得明确所有权。若调用方需要共享，可直接将`unique_ptr`赋值给`shared_ptr`（允许隐式转换）：

```cpp
std::unique_ptr<Widget> factory() { return std::make_unique<Widget>(); }
std::shared_ptr<Widget> sp = factory(); // 合法转换
```

**观察者模式中的weak_ptr**：在GUI框架中，事件源（Subject）持有观察者列表时，若使用`shared_ptr`存储Observer，Observer被UI销毁后内存仍被Subject持有。改为`vector<weak_ptr<Observer>>`后，每次触发事件前通过`lock()`检查Observer是否存活，已失效的直接跳过，避免了悬空回调。

**unique_ptr管理C资源**：`unique_ptr`支持自定义删除器，可用于管理`FILE*`等C资源：`std::unique_ptr<FILE, decltype(&fclose)> f(fopen("a.txt","r"), fclose);`，文件句柄在智能指针析构时自动关闭。

---

## 常见误区

**误区1：用同一个裸指针初始化两个shared_ptr**  
`shared_ptr<int> a(raw); shared_ptr<int> b(raw);`会创建**两个独立的控制块**，各自认为自己是唯一所有者，导致`raw`被`delete`两次，触发未定义行为。正确做法是只从`make_shared`或从已有`shared_ptr`拷贝来创建新`shared_ptr`。

**误区2：在类内用this构造shared_ptr**  
在成员函数中写`return shared_ptr<MyClass>(this)`同样是从裸指针重复构造控制块的问题。C++标准提供了`std::enable_shared_from_this<T>`基类，继承后可安全调用`shared_from_this()`获取与外部`shared_ptr`共享同一控制块的指针。

**误区3：unique_ptr误认为有运行时开销**  
部分开发者因为"智能"二字而担心性能，实际上`unique_ptr`在优化编译下与裸指针生成的汇编代码几乎一致（析构即`delete`的内联展开），不存在虚函数调用或引用计数操作，适合对性能敏感的场景。

---

## 知识关联

**前置概念——栈与堆**：智能指针本身作为对象分配在**栈**上，但它所管理的资源位于**堆**上。理解栈的LIFO销毁顺序正是RAII机制有效运作的基础：函数退出时栈帧弹出，触发`unique_ptr`析构，进而释放堆内存，整个过程由栈的生命周期驱动。

**后续概念——移动语义**：`unique_ptr`不可拷贝的设计直接推动了C++11移动语义的完善。`std::move()`将左值转换为右值引用，激活`unique_ptr`的移动构造函数完成所有权转移而非复制。学习`unique_ptr`是理解移动语义必要性和右值引用实际价值的最佳切入点，因为所有权转移的需求使得移动语义的设计意图清晰可见。
