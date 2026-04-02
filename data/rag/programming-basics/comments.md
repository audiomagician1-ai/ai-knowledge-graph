---
id: "comments"
concept: "注释"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 注释

## 概述

注释（Comment）是源代码中不会被编译器或解释器执行的文本内容，专门用于向人类读者解释代码的意图、逻辑或注意事项。Python 解释器在运行代码时会完全跳过注释行，不产生任何字节码指令，因此注释对程序的运行结果没有任何影响。

注释的历史几乎与编程语言一样悠久。FORTRAN 语言（1957年发布）就已引入注释机制，用字母 `C` 放在行首标记注释行。此后每种主流语言都发展出自己的注释语法：C 语言使用 `/* */` 包裹块注释，Python 使用 `#` 符号，HTML 使用 `<!-- -->`。这一机制从诞生至今从未被取消，说明它对软件开发不可或缺。

在 AI 工程中，注释的重要性被进一步放大。一段训练数据预处理脚本可能在数月后被重新使用，一个模型推理接口可能由多名工程师协作维护。没有注释的代码会让接手者不得不逆向推断每一行的意图，大幅增加出错风险。注释是程序员留给未来自己和同事的"使用说明书"。

## 核心原理

### Python 中的单行注释

Python 使用井号 `#` 标记单行注释。`#` 之后直到该行末尾的所有内容都属于注释，不会被执行。

```python
# 加载训练数据集，路径相对于项目根目录
data_path = "./data/train.csv"

learning_rate = 0.001  # 推荐范围：0.0001 到 0.01
```

第一种写法将注释单独放一行，适合解释接下来整段代码的目的；第二种写法将注释跟在代码同行之后（称为"行尾注释"或"内联注释"），适合对单个变量或参数做简短说明。PEP 8 规范建议内联注释与代码之间至少保留 **2个空格**，`#` 后跟 **1个空格**再写注释文字。

### Python 中的多行注释

Python 没有专门的多行注释语法，但有两种常用做法：

**方式一**：连续使用多个 `#`，每行单独注释。

```python
# 数据归一化步骤：
# 1. 计算训练集的均值和标准差
# 2. 用同一组参数变换验证集和测试集
# 注意：不能用验证集的统计量，否则会造成数据泄露
```

**方式二**：使用三重引号 `"""` 或 `'''` 包裹文本。严格来说，三重引号创建的是字符串字面量而非真正的注释，但当它不被赋值给任何变量时，Python 解释器会忽略该字符串的值，效果与注释相同。这种写法最常见于函数或类的**文档字符串（Docstring）**，位于 `def` 或 `class` 语句的第一行之后：

```python
def normalize(data, mean, std):
    """
    对输入数据进行 Z-score 标准化。
    公式：z = (x - mean) / std
    参数：
        data  - 原始数值列表
        mean  - 训练集均值
        std   - 训练集标准差，不能为 0
    返回：标准化后的列表
    """
    return [(x - mean) / std for x in data]
```

### 注释的本质：代码不执行，但影响可读性

可以用一个简单实验验证注释不被执行：将任意一行赋值语句改为注释，该变量就不再存在，后续引用会抛出 `NameError`。

```python
# model_version = "GPT-4"   ← 这行被注释掉了
print(model_version)         # 运行时报错：NameError: name 'model_version' is not defined
```

这个特性也让注释成为调试时的利器——临时"关闭"某行代码只需在行首加 `#`，无需删除，之后去掉 `#` 即可恢复。

## 实际应用

**场景一：解释超参数选择理由**

```python
batch_size = 32  # 经实验，64会导致GPU显存溢出（VRAM 8GB限制）
epochs = 50      # 验证集损失在第47轮趋于平稳，多训练几轮作为安全边际
```

直接写数字而不注释，三个月后连作者本人也不记得为什么选 32 而不是 64。

**场景二：标记待办事项（TODO）**

许多 AI 工程团队约定用 `# TODO:` 前缀标记尚未完成的工作：

```python
# TODO: 当前只支持 CSV 格式，后续需要兼容 Parquet 和 JSON
def load_data(file_path):
    return pd.read_csv(file_path)
```

`TODO` 注释可以被 VSCode、PyCharm 等编辑器高亮显示，方便全局搜索未完成项。

**场景三：暂时禁用代码段**

```python
# 调试阶段：先用小样本快速验证流程
train_data = train_data[:500]
# train_data = load_full_dataset()  ← 正式训练时取消注释此行，并注释上面一行
```

## 常见误区

**误区一：注释越多越好**

注释应解释"为什么"，而不是逐字翻译代码在"做什么"。以下注释毫无价值：

```python
i = i + 1  # 将 i 加 1
```

这类注释被称为"废话注释"（Noise Comment），不仅不增加信息量，还让读者在大量注释中找不到真正重要的说明。好的注释描述的是代码无法直接表达的意图，例如"跳过索引 0 是因为第一行是列标题"。

**误区二：用注释保存废弃代码**

一些开发者习惯将不用的代码注释掉而不删除，导致文件中出现大段被注释的"僵尸代码"。在使用 Git 等版本控制系统的项目中，这种做法是不必要的——历史版本永远可以通过 `git log` 找回。建议直接删除无用代码，保持文件整洁。

**误区三：误以为三重引号就是注释**

`"""文字"""` 在 Python 中创建的是一个**字符串对象**。如果写在模块顶层且没有赋值，CPython 解释器通常会优化掉它；但如果写在某些上下文中，它会占用内存并可通过 `__doc__` 属性访问。因此三重引号与 `#` 注释并不完全等价，不能混用。函数的 Docstring 可以通过 `help(normalize)` 命令直接查看，而 `#` 注释则无法在运行时访问。

## 知识关联

**前置概念——Hello World**：在第一个 Hello World 程序中，你已经见过 `print("Hello, World!")` 这一行代码。为这行代码添加注释 `# 向用户打印问候语` 是学习注释最直接的起点，帮助你理解注释与可执行语句之间的区别。

**延伸方向——变量与数据类型**：当你开始声明变量时，注释的价值会显著体现——为什么这个变量叫 `lr` 而不是 `learning_rate`？它的单位是什么？取值范围是多少？这些信息都需要通过注释传递。

**延伸方向——函数定义**：学习 `def` 关键字定义函数后，Docstring 的写法将成为注释技能的重要升级。Docstring 是 Python 内置文档系统的基础，`help()` 函数和自动化文档生成工具（如 Sphinx）都依赖它工作。

**工程实践关联**：在 AI 工程项目中，Jupyter Notebook 将注释文化推向了新形式——Markdown 单元格可以插入标题、公式、图片，使数据分析过程本身成为一份可读的报告。这是 `#` 注释思想的自然延伸。