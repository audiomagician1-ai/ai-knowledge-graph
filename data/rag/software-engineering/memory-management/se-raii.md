---
id: "se-raii"
concept: "RAII"
domain: "software-engineering"
subdomain: "memory-management"
subdomain_name: "内存管理"
difficulty: 2
is_milestone: false
tags: ["C++"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# RAII（资源获取即初始化）

## 概述

RAII 是 **Resource Acquisition Is Initialization** 的缩写，中文译为"资源获取即初始化"。其核心思想是：将资源的生命周期与对象的生命周期绑定，在构造函数中获取资源，在析构函数中释放资源。由于 C++ 保证对象离开作用域时析构函数必然被调用，因此资源释放变得自动且确定。

RAII 由 C++ 之父 Bjarne Stroustrup 在 1980 年代设计 C++ 时提出，最初用于解决文件句柄和互斥锁的管理问题。传统 C 语言要求程序员手动配对 `malloc`/`free`、`fopen`/`fclose`，一旦中间路径出现异常或提前返回，资源就会泄漏。RAII 通过将这种配对关系封装进类的构造与析构，从语言机制层面消除了这类遗漏。

RAII 之所以重要，是因为它提供了**异常安全**的唯一可靠保障。当函数抛出异常时，C++ 运行时会沿调用栈展开（stack unwinding），逐一调用局部对象的析构函数。依赖 RAII 的代码无需 `try/finally` 块即可保证资源不泄漏，而 Java 和 Python 中需要 `try-with-resources` 或 `with` 语句才能实现类似效果。

---

## 核心原理

### 构造函数获取，析构函数释放

RAII 类的结构遵循固定模式：构造函数负责申请资源并在失败时抛出异常，析构函数无条件释放资源。以文件管理为例：

```cpp
class FileGuard {
    FILE* fp_;
public:
    explicit FileGuard(const char* path) {
        fp_ = fopen(path, "r");
        if (!fp_) throw std::runtime_error("打开文件失败");
    }
    ~FileGuard() { fclose(fp_); }  // 析构时必然执行
};
```

当 `FileGuard` 对象建立在栈上时，无论函数以何种方式退出——正常返回、抛出异常、或调用 `return`——`fclose` 都会被执行。这与手动 `fclose` 相比，省去了每个退出路径上的清理代码。

### 栈展开与析构顺序

C++ 标准规定，同一作用域内的局部对象按**构造顺序的逆序**析构。利用这一性质，RAII 可以正确处理多资源的依赖关系：先构造的互斥锁后释放，先构造的数据库连接在事务对象之后析构，保证操作顺序不颠倒。当异常在第 N 个对象构造时抛出，已完成构造的前 N-1 个对象会全部被析构，不留任何资源泄漏。

### 所有权语义与禁止复制

RAII 类通常**独占**所管理的资源，因此必须处理复制语义。默认生成的复制构造函数会浅拷贝原始指针，导致两个对象析构时对同一资源执行两次释放（double-free）。正确做法有两种：

- **删除复制操作**（如 `std::unique_ptr`）：`FileGuard(const FileGuard&) = delete;`
- **实现深拷贝或引用计数**（如 `std::shared_ptr`）：维护一个引用计数器，计数降为 0 时才真正释放资源。

C++11 引入移动语义后，RAII 类还应实现移动构造函数，将资源所有权从临时对象转移，而不发生额外的分配与释放。

### RAII 与三/五法则

在 C++11 之前，实现 RAII 类需遵循**三法则**（Rule of Three）：若定义了析构函数，则必须同时定义复制构造函数和复制赋值运算符。C++11 后扩展为**五法则**（Rule of Five），额外要求定义移动构造函数和移动赋值运算符。标准库的 `std::lock_guard`、`std::unique_ptr` 和 `std::fstream` 均是五法则的典型实现。

---

## 实际应用

**互斥锁管理**：`std::lock_guard<std::mutex>` 是最常见的 RAII 用例。构造时调用 `mutex.lock()`，析构时调用 `mutex.unlock()`。如果锁定后函数因异常退出，锁依然会被释放，避免死锁。相比手动调用 `unlock()`，`lock_guard` 将临界区的边界明确限定在一个代码块内，可读性与安全性同时提升。

**智能指针**：`std::unique_ptr` 和 `std::shared_ptr`（C++11 标准引入）都是 RAII 的直接体现。`unique_ptr` 离开作用域时自动调用 `delete`，`shared_ptr` 在最后一个持有者析构时释放堆内存。使用它们后，裸指针的 `new`/`delete` 配对问题在大多数场景下可以彻底消除。

**数据库事务**：在数据库访问层，可以设计一个 `Transaction` RAII 类，构造时执行 `BEGIN`，析构时若未显式提交则自动执行 `ROLLBACK`。这样即使业务逻辑中途抛出异常，事务也不会停留在半提交状态，保证了数据一致性。

---

## 常见误区

**误区一：在析构函数中抛出异常**

RAII 的析构函数绝对不能抛出异常。在栈展开过程中，若已有一个异常正在传播，而析构函数又抛出第二个异常，C++ 标准规定程序将直接调用 `std::terminate()` 终止运行。因此，析构函数中的资源释放操作（如 `fclose`、`unlock`）必须吞下所有错误，或在内部记录日志后静默处理。

**误区二：将 RAII 对象放在堆上**

```cpp
// 错误！RAII 失效
FileGuard* fg = new FileGuard("data.txt");
// 若忘记 delete fg，析构函数永远不会被调用
```

RAII 依赖栈上对象的自动析构，若将 RAII 对象本身用 `new` 分配到堆上，则析构函数只有手动 `delete` 才会触发，完全丧失了自动管理的意义。如果确实需要动态生命周期，应将 RAII 对象本身包装进 `unique_ptr`。

**误区三：认为 RAII 只适用于内存**

RAII 管理的"资源"范围远超内存，包括：文件描述符、网络套接字、数据库连接、GPU 上下文、线程句柄、临时文件路径等一切需要配对操作的资源。凡是存在"申请—使用—释放"模式的场景，均可用 RAII 封装。

---

## 知识关联

**前置概念**：理解 RAII 需要先掌握**栈与堆**的区别——RAII 利用的正是栈对象在离开作用域时自动调用析构函数这一机制，堆上对象没有此保证。**智能指针**是 RAII 在内存管理上的标准库实现，`unique_ptr` 的 `deleter` 机制可以管理任意资源，而不仅限于 `delete`。

**后续概念**：掌握 RAII 之后，**内存泄漏检测**工具（如 Valgrind、AddressSanitizer）的输出会更易于解读——若代码充分使用了 RAII，这类工具的报告数量会大幅减少，剩余的泄漏往往集中在第三方 C 接口或裸指针的遗留代码中，定位更加精准。