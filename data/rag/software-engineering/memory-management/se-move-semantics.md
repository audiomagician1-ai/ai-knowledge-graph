# 移动语义

## 概述

移动语义（Move Semantics）是 C++11 标准（ISO/IEC 14882:2011，2011年9月正式发布）引入的核心语言特性，其本质是通过转移资源所有权而非复制资源内容，将对象间赋值操作的时间复杂度从 $O(n)$ 降至 $O(1)$。C++ 标准委员会成员 Howard Hinnant 于 2002 年提交右值引用提案 N1377，历经九年十余次修订（N1690、N2118、N2844 等），最终随 C++11 标准化落地。

移动语义解决的根本问题是：C++03 时代，编译器在以下三类场景中必须调用拷贝构造函数，即使源对象即将销毁——函数按值返回（Return Value）、向容器中插入临时对象、在容器扩容时重新排列元素。以一个持有 1MB 堆内存的 `std::string` 为例，拷贝操作需要调用 `malloc` 分配新内存并执行 `memcpy`；而移动操作仅需复制三个机器字（指针、长度、容量），将源对象的内部指针置为 `nullptr`，开销相差三到四个数量级。

Stroustrup 在《The C++ Programming Language, 4th Edition》（Stroustrup, 2013）中将移动语义称为 C++11 最重要的新特性之一，指出它使得"返回大型对象变得实际可行，而不再需要依赖输出参数或堆分配的返回值"。

---

## 核心原理

### 值类别体系：左值、纯右值与将亡值

C++11 将每个表达式的值类别（value category）重新划分为三种基本类型：
- **左值（lvalue）**：有名称、有持久地址的对象，如变量名 `x`、解引用表达式 `*p`。
- **纯右值（prvalue）**：字面量 `42`、函数调用返回的临时值（非引用返回）。
- **将亡值（xvalue，eXpiring value）**：即将销毁但资源可被转移的对象，如 `std::move(x)` 的结果、返回右值引用的函数调用。

纯右值和将亡值统称右值（rvalue）。右值引用 `T&&` 只能绑定到右值，而传统的左值引用 `T&` 只能绑定到左值（`const T&` 可兼容右值但只读）。这种区分使编译器在重载决议时能够精确选择移动版本的构造函数或赋值运算符。

Vandevoorde、Josuttis 与 Gregor 在《C++ Templates: The Complete Guide, 2nd Edition》（2017）中详细阐述了值类别对模板类型推导的影响：当函数参数类型为 `T&&` 且 `T` 为模板参数时，发生引用折叠（reference collapsing），这是完美转发的理论基础。

### 移动构造函数与移动赋值运算符

实现移动语义需定义两个特殊成员函数，均应标注 `noexcept`（对于标准库容器的优化至关重要）：

```cpp
class DynamicArray {
    double* data_;
    std::size_t size_;
public:
    // 移动构造函数：O(1) 接管堆内存
    DynamicArray(DynamicArray&& other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;   // 源对象进入"有效但未指定"状态
        other.size_ = 0;
    }

    // 移动赋值运算符：先释放自身资源，再接管
    DynamicArray& operator=(DynamicArray&& other) noexcept {
        if (this != &other) {
            delete[] data_;
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    ~DynamicArray() { delete[] data_; }
};
```

`noexcept` 标注的重要性：`std::vector` 在扩容时调用 `std::move_if_noexcept`，只有当移动构造函数声明为 `noexcept` 时才会选择移动而非拷贝。若移动构造函数可能抛出异常，`vector` 为保证强异常安全性（strong exception guarantee）会回退到拷贝，导致移动语义失效。这是 Scott Meyers 在《Effective Modern C++》（Meyers, 2014）条款 Item 14 中特别强调的细节。

### std::move 的本质：仅是类型转换

`std::move` 是一个无运行时开销的函数模板，等价于：

$$\texttt{std::move(x)} \equiv \texttt{static\_cast<typename std::remove\_reference<T>::type\&\&>(x)}$$

它不移动任何数据，仅将左值强制转换为右值引用，从而触发重载决议选择移动版本。以下代码揭示了一个常见陷阱：

```cpp
std::vector<std::string> v;
std::string s = "large string with heap data";
v.push_back(std::move(s));   // 正确：触发移动构造
// 此后 s 处于有效但未指定状态，不应继续使用其内容
std::cout << s.size();       // 合法但结果未定（通常为 0）
std::cout << s[0];           // 行为未定义（若 size==0）
```

---

## 完美转发与万能引用

### 引用折叠规则

当模板参数 `T` 被推导为引用类型时，C++11 引入引用折叠规则（reference collapsing）：

| 声明类型 | 实参类型 | 折叠结果 |
|---------|---------|---------|
| `T&` | `T&` | `T&` |
| `T&` | `T&&` | `T&` |
| `T&&` | `T&` | `T&` |
| `T&&` | `T&&` | `T&&` |

总结为：**只要有左值引用参与折叠，结果就是左值引用**；只有两个右值引用折叠才得到右值引用。

### 万能引用与完美转发

形如 `template<typename T> void f(T&& x)` 的参数 `x`，当 `T` 为模板参数（而非具体类型）时，称为万能引用（universal reference，Meyers 术语）或转发引用（forwarding reference，C++17 标准术语）。此时：
- 传入左值时，`T` 推导为 `T&`，`x` 实为左值引用。
- 传入右值时，`T` 推导为 `T`，`x` 实为右值引用。

`std::forward<T>(x)` 根据 `T` 的推导结果恢复原始值类别：

```cpp
template<typename T, typename... Args>
std::unique_ptr<T> make_unique(Args&&... args) {
    return std::unique_ptr<T>(new T(std::forward<Args>(args)...));
}
```

完美转发使工厂函数、容器的 `emplace` 系列方法能够将参数以原始值类别透传给构造函数，避免额外的拷贝或移动。例如 `std::vector::emplace_back` 相比 `push_back(T(...))` 可减少一次移动构造调用。

---

## 关键公式与性能模型

### 移动 vs 拷贝的复杂度对比

设容器持有 $n$ 字节的堆数据：

$$T_{\text{copy}} = T_{\text{malloc}}(n) + T_{\text{memcpy}}(n) \approx \alpha + \beta \cdot n$$

$$T_{\text{move}} = O(1) \text{（仅复制指针，与 } n \text{ 无关）}$$

对于 `std::vector<std::string>` 中存储均长 $L$ 字节字符串、容器扩容时需迁移 $N$ 个元素的场景：

$$\Delta T_{\text{扩容}} = N \cdot (T_{\text{copy}}(L) - T_{\text{move}}) \approx N \cdot \beta \cdot L$$

当 $L = 1\,\text{KB}$、$N = 10^4$ 时，移动语义可节省约 $10\,\text{GB}$ 的内存读写操作，性能差异在实测中通常体现为 5×～50× 的吞吐量提升。

### 五法则（Rule of Five）

C++11 将 C++03 的"三法则"（Rule of Three：析构函数、拷贝构造、拷贝赋值）扩展为**五法则**（Rule of Five），新增移动构造函数和移动赋值运算符。若手动定义了析构函数（意味着类管理资源），则必须显式定义全部五个特殊成员函数，否则编译器可能不自动生成移动版本：

1. 析构函数（Destructor）
2. 拷贝构造函数（Copy Constructor）
3. 拷贝赋值运算符（Copy Assignment Operator）
4. **移动构造函数（Move Constructor）** ← C++11 新增
5. **移动赋值运算符（Move Assignment Operator）** ← C++11 新增

---

## 实际应用

### std::unique_ptr 的所有权转移

`std::unique_ptr` 是移动语义在所有权管理中的标志性应用：其拷贝构造函数被 `= delete` 禁用，只能通过 `std::move` 转移所有权。

```cpp
auto p1 = std::make_unique<Widget>(42);
auto p2 = std::move(p1);   // p1 变为 nullptr，p2 独占 Widget
// p1.get() == nullptr，访问 p1->method() 将导致未定义行为
```

在函数间传递 `unique_ptr` 时，按值传参（`void f(std::unique_ptr<T> p)`）即表达"函数接管所有权"的语义，调用方必须显式 `std::move`，使所有权转移在代码中可见。

### 容器的 emplace 系列

`std::vector::emplace_back` 利用完美转发直接在容器内存中原地构造对象，相比 `push_back(T(args...))` 省去临时对象的构造与移动：

```cpp
std::vector<std::pair<std::string, int>> employees;
// push_back 版本：构造临时 pair，再移动进容器（共 1 次构造 + 1 次移动）
employees.push_back({"Alice", 30});
// emplace_back 版本：直接在容器内存中构造（1 次构造，0 次移动）
employees.emplace_back("Bob", 25);
```

### 返回值优化（RVO）与移动语义的关系

编译器的命名返回值优化（NRVO）优先级高于移动语义：当编译器能确定返回的局部变量就是函数的返回值时，直接在调用者提供的内存中构造，完全省略拷贝与移动。移动语义是 NRVO 无法触发时的"保底机制"。C++17 强制要求纯右值的拷贝消除（mandatory copy elision），进一步减少了显式 `std::move` 的必要性。

**例如**：以下函数在 C++17 中保证零拷贝，在 C++11/14 中依赖 NRVO（大多数编译器会优化，但标准不强制）：

```cpp
std::vector<int> make_large_vector() {
    std::vector<int> v(1000000);
    // ... 填充数据
    return v;  // C++17: 强制拷贝消除；C++11: NRVO 或移动
}
```

---

## 常见误区

### 误区一：对具名右值引用变量使用时无需 std::move

```cpp
void process(Widget&& w) {
    auto copy = w;           // 错误意图：w 是左值！调用拷贝构造
    auto moved = std::move(w);  // 正确：显式转为右值
}
```

具名的右值引用变量 `w` 在表达式中是**左值**（有名称、有地址），必须再次使用 `std::move` 才能触发移动。这是移动语义中最常见的认知错误。

### 误区二：移动后继续使用源对象的值

C++ 标准（[lib.types.movedfrom]）规定：被移动对象处于"有效但未指定（valid but unspecified）"状态，可以被赋值或销毁，但不能假设其内容。在实践中，标准库的 `std::string` 和 `std::vector` 移动后通常为空，但标准不保证这一点。

### 误区三：过度使用 std::move 反而阻止优化

```cpp
return std::move(local_var);  // 错误！阻止 NRVO/RVO
return local_var;             // 正确：编译器优先应用拷贝消除
```

对函数返回语句中的局部变量显式 `std::move`，会阻止编译器应用 NRVO，反而可能降低性能。Meyers（2014）在 Item 25 中明确