---
id: "error-handling"
concept: "错误处理(try/catch)"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 3
is_milestone: false
tags: ["鲁棒性"]

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

# 错误处理（try/catch）

## 概述

错误处理（try/catch）是一种结构化的异常捕获机制，允许程序在运行时遇到错误时，不立即崩溃退出，而是跳转到指定的处理代码块继续执行。这一机制由 try 块、catch 块和可选的 finally 块三部分组成：try 块包裹可能抛出异常的代码，catch 块定义异常发生后的处理逻辑，finally 块则无论是否发生异常都会执行（常用于资源释放）。

try/catch 最早在 CLU 语言（1975年，MIT）中以"异常处理"形式出现，后被 C++（1990年）、Java（1995年）标准化并广泛推广。Python 使用 `try/except` 语法，JavaScript 使用 `try/catch`，两者语义相同但关键字不同。在 AI 工程中，调用外部 API、加载模型权重文件、解析用户输入时，随时可能遇到网络超时、文件缺失、类型不匹配等运行时错误，若不加处理，整个推理服务会直接崩溃。

try/catch 的价值在于将"正常流程"与"错误流程"分离。没有它，开发者需要在每一步操作后手动检查返回值（类似 C 语言的 `if (err != NULL)` 模式），代码嵌套层级极深。使用 try/catch 后，正常逻辑保持线性可读，错误路径集中管理。

---

## 核心原理

### 异常的传播机制（调用栈展开）

当 try 块内某行代码抛出异常时，Python/JavaScript 解释器会立即停止执行该块的后续语句，并沿**调用栈向上查找**最近的匹配 catch/except 块。这个过程称为"栈展开"（Stack Unwinding）。若函数 A 调用函数 B，函数 B 内抛出异常但未被捕获，该异常会冒泡到函数 A 的 catch 块。若整个调用栈都没有捕获，程序抛出未处理异常并终止。

```python
def load_model(path):
    with open(path, 'rb') as f:   # 若文件不存在，抛出 FileNotFoundError
        return pickle.load(f)

def run_inference(path, input_data):
    try:
        model = load_model(path)   # 异常从 load_model 冒泡到此处
        return model.predict(input_data)
    except FileNotFoundError as e:
        print(f"模型文件缺失: {e}")
        return None
```

### 异常类型与精确捕获

catch/except 可以指定捕获的异常类型。Python 的内置异常形成继承树：`BaseException → Exception → ValueError / TypeError / IOError` 等。捕获父类（如 `Exception`）会拦截所有子类异常；捕获 `BaseException` 还会拦截 `KeyboardInterrupt` 和 `SystemExit`，这在 AI 服务中极危险——用户按 Ctrl+C 停止进程的信号会被吞掉，导致服务无法正常退出。

正确做法是**从最具体的异常到最宽泛的异常**依次排列多个 except 块：

```python
try:
    response = requests.get(api_url, timeout=5)
    data = response.json()
except requests.exceptions.Timeout:
    log("API 超时，启用本地缓存")
except requests.exceptions.ConnectionError:
    log("网络不可达")
except ValueError:
    log("响应不是合法 JSON")
except Exception as e:
    log(f"未预期错误: {type(e).__name__}: {e}")
```

### finally 块与资源保证

finally 块在 try/catch 执行完毕后**无条件运行**，即使 catch 块内又抛出新异常，即使代码中有 `return` 语句。这一特性专门用于释放文件句柄、数据库连接、GPU 显存等资源。在 AI 推理服务中，若加载一个大型模型后发生异常，未释放的显存会导致后续所有请求失败。

```python
model = None
try:
    model = load_large_model()
    result = model.infer(data)
finally:
    if model is not None:
        model.release_gpu_memory()  # 无论是否出错都执行
```

### 主动抛出与自定义异常

`raise` 语句主动抛出异常，可用于在检测到非法状态时提前终止。自定义异常类继承自 `Exception`，可携带额外上下文信息：

```python
class ModelNotWarmedException(Exception):
    def __init__(self, model_name, wait_seconds):
        super().__init__(f"{model_name} 尚未预热，需等待 {wait_seconds}s")
        self.model_name = model_name
```

---

## 实际应用

**场景一：调用 OpenAI API 时的超时与限流处理**  
OpenAI API 在触发速率限制时返回 HTTP 429，客户端库将其映射为 `openai.error.RateLimitError`。正确的处理方式是捕获该异常后进行指数退避重试（如等待 2^n 秒），而非直接返回空结果或崩溃。

**场景二：加载 JSON 配置文件**  
AI 项目常用 JSON 存储超参数配置。`json.loads()` 在输入不合法时抛出 `json.JSONDecodeError`（Python 3.5+ 中是 `ValueError` 的子类）。捕获它后应打印出具体的行号和列号（`e.lineno`, `e.colno`），帮助快速定位配置文件错误位置。

**场景三：NumPy/PyTorch 运算中的形状不匹配**  
矩阵乘法 `np.dot(A, B)` 在 A 的列数与 B 的行数不匹配时抛出 `ValueError: shapes (3,4) and (5,6) not aligned`。在批量推理循环中捕获此异常，记录出错的样本索引，可以跳过该样本继续处理其余数据，而不是终止整批推理。

---

## 常见误区

**误区一：用裸 `except:` 或 `except Exception` 捕获一切**  
许多初学者写 `except:` 吞掉所有错误只为"程序不崩溃"。这会掩盖真实 bug——比如变量名拼写错误产生的 `NameError` 也会被静默忽略，导致后续逻辑以错误的中间状态继续运行，产生难以追踪的结果偏差。正确做法是只捕获**预期会发生的特定异常类型**。

**误区二：在 finally 块中使用 return**  
若 finally 块内有 `return` 语句，它会**覆盖** try 或 catch 块中的 `return` 值，且会**吞掉**正在传播中的异常。这是 Python 和 JavaScript 共同的陷阱。例如 finally 里 `return None` 会使调用方永远收不到原始异常，错误被静默丢弃。

**误区三：混淆"异常"与"错误返回码"两种模式**  
try/catch 的设计前提是异常是**例外情况**，不应用于控制正常业务流程。在 AI 工程中，有些开发者用抛出/捕获异常来做条件分支（如用 `try: value = dict[key] except KeyError: value = default`），虽然在 Python 中是惯用法（EAFP 风格），但在热路径（如每秒万次推理的批处理循环）中，频繁抛出异常的开销远高于 `dict.get(key, default)`，可能导致吞吐量下降 3-5 倍。

---

## 知识关联

try/catch 建立在**函数**的基础上：异常沿调用栈传播的路径就是函数调用链，理解函数的执行帧（frame）才能正确判断异常会在哪一层被捕获。

向前延伸，try/catch 直接支撑**后端错误处理**——HTTP 服务框架（如 FastAPI）的全局异常处理器（`@app.exception_handler`）本质上是在最外层 catch 块的基础上封装的。**文件 I/O** 操作中每一次磁盘读写都依赖 try/finally 保证文件句柄正确关闭（Python 的 `with` 语句是 try/finally 的语法糖，底层调用 `__exit__` 方法）。**日志基础**与 catch 块深度结合：捕获异常后应使用 `logger.exception(e)` 而非 `print(e)`，前者会自动记录完整的堆栈跟踪（traceback）。**契约式设计**中的前置条件违反（precondition violation）通常通过 `raise ValueError` 实现，与 try/catch 形成完整的防御性编程闭环。