---
id: "modules-imports"
concept: "模块与导入"
domain: "ai-engineering"
subdomain: "programming-basics"
subdomain_name: "编程基础"
difficulty: 2
is_milestone: false
tags: ["模块化"]

# Quality Metadata (Schema v2)
content_version: 4
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

# 模块与导入

## 概述

模块（Module）是将相关代码组织在一个独立文件或命名空间中的编程机制。在Python中，每个`.py`文件天然就是一个模块；在JavaScript中，ES6（2015年）引入了原生模块系统`import/export`语法，彻底改变了此前依赖全局变量共享代码的混乱局面。模块的本质是将变量、函数、类等定义封装在独立作用域内，外部代码只能访问被显式导出的部分。

模块化思想解决的核心问题是**命名冲突**与**代码复用**。在没有模块系统的年代，浏览器中多个JavaScript文件共享同一个全局`window`对象，来自不同库的同名变量会互相覆盖。Node.js在2009年采用了CommonJS规范（`require/module.exports`），成为首个在服务端JavaScript中推广模块化的里程碑。Python的模块系统则从语言设计之初就内置，`import`语句在Python 1.0时期便已存在。

在AI工程的编程实践中，几乎所有核心库都通过模块导入使用：`import numpy as np`、`import torch`、`from sklearn.model_selection import train_test_split`。理解模块导入机制，意味着能够控制哪些名称进入当前命名空间，避免在数据处理管道中因意外的名称覆盖导致难以排查的数值错误。

---

## 核心原理

### Python的模块搜索路径

执行`import pandas`时，Python解释器按照`sys.path`列表中的目录顺序逐一搜索。`sys.path`的构成是：当前脚本所在目录 → `PYTHONPATH`环境变量指定的目录 → 标准库目录 → site-packages目录（第三方包的安装位置）。可以通过`import sys; print(sys.path)`查看完整搜索路径。这意味着，如果在项目根目录创建了名为`random.py`的文件，`import random`会导入自定义文件而非标准库，这是初学者最容易遇到的陷阱之一。

### 三种导入语法及其命名空间影响

**完整模块导入**：`import numpy`将`numpy`名称绑定到当前命名空间，访问时需要写`numpy.array()`，好处是来源清晰。

**别名导入**：`import numpy as np`是AI社区的约定俗成，`np`比`numpy`少打4个字符，且整个社区统一使用`np`、`pd`（pandas）、`plt`（matplotlib.pyplot）作为别名，提高代码可读性。

**选择性导入**：`from torch.nn import Linear, ReLU`只将`Linear`和`ReLU`两个名称导入当前命名空间，不引入`torch`或`nn`。这在构建神经网络时非常常见，但使用`from module import *`（通配符导入）会将模块的所有公开名称（即`__all__`列表中定义的名称，或所有不以下划线开头的名称）全部导入，强烈不推荐在生产代码中使用。

### `__init__.py`与包的构成

当一个目录包含`__init__.py`文件时，该目录成为一个**包（Package）**。包是模块的集合，支持多层级的命名空间。例如`sklearn`的目录结构中，`sklearn/model_selection/__init__.py`使得`from sklearn.model_selection import cross_val_score`这样的导入成为可能。`__init__.py`可以为空，也可以预先导入子模块中的常用内容，控制`from package import *`时暴露的接口。在Python 3.3+引入了**隐式命名空间包**，不再强制要求`__init__.py`存在，但显式声明仍是最佳实践。

### JavaScript的ES模块系统

ES6模块使用`export`导出、`import`导入，且是**静态分析**的——导入语句必须位于文件顶层，不能写在`if`语句或函数内部。这与Python的动态`import`不同，Python允许在函数体内执行`import`以实现懒加载。ES模块的静态特性使得打包工具（如Webpack、Vite）能够进行**Tree Shaking**，即在构建时自动移除未被使用的导出代码，减小最终打包体积。

```javascript
// 命名导出
export const MODEL_VERSION = "1.0";
export function preprocess(data) { ... }

// 默认导出（每个模块只能有一个）
export default class Predictor { ... }

// 导入
import Predictor, { MODEL_VERSION, preprocess } from './model.js';
```

---

## 实际应用

**AI项目的标准导入块**：在机器学习脚本的顶部，通常集中放置所有导入语句，按照"标准库 → 第三方库 → 本地模块"的顺序排列，这是`isort`工具默认强制执行的规范。例如：

```python
import os                              # 标准库
import numpy as np                     # 第三方库
import torch
from torch import nn
from .data_loader import load_dataset  # 相对导入（本地模块）
```

**相对导入与绝对导入**：在同一个包内，`from .utils import normalize`（单点表示当前包）和`from ..config import BATCH_SIZE`（双点表示父级包）是相对导入。绝对导入`from myproject.utils import normalize`则从项目根路径开始。大型AI项目通常优先使用绝对导入，因为重构时路径更清晰。

**条件导入处理兼容性**：AI工程中常见不同硬件环境（GPU/CPU），可用条件导入处理：
```python
try:
    import cupy as np   # GPU加速的numpy替代品
except ImportError:
    import numpy as np  # 回退到CPU版本
```

---

## 常见误区

**误区一：认为`from module import func`会减少内存占用**。实际上，`from numpy import array`执行时，Python依然加载了整个`numpy`模块并缓存在`sys.modules`字典中，只是没有把`numpy`名称绑定到当前命名空间。重复`import`同一模块不会造成重复加载，Python通过`sys.modules`缓存保证每个模块只初始化一次。

**误区二：循环导入（Circular Import）只是风格问题**。当模块A导入模块B，同时模块B又导入模块A时，Python会在第一个模块尚未完全初始化时尝试导入第二个，导致`ImportError: cannot import name 'X'`或得到不完整的模块对象。这在AI项目中常见于将`config.py`既被`model.py`导入，又反向依赖`model.py`中的常量。解决方案是将共享常量提取到独立的`constants.py`，或在函数内部进行延迟导入。

**误区三：`__all__`是访问控制机制**。`__all__ = ['Trainer', 'evaluate']`只影响`from module import *`的行为，并不阻止`from module import _private_func`这样的显式导入。Python没有强制性的私有访问限制，`__all__`仅是一种声明模块公开API的约定。

---

## 知识关联

模块与导入建立在**函数**概念之上：被导入的内容主要是函数、类和常量，理解函数作用域（局部变量不会污染模块命名空间）是理解模块隔离性的前提。

掌握模块机制后，**包管理**工具（pip、conda）的作用变得清晰——它们本质上是将第三方模块安装到`sys.path`可访问的`site-packages`目录中。`requirements.txt`和`pyproject.toml`记录的是项目依赖哪些外部模块及其版本。

在JavaScript方向，ES模块的`export/import`语法是**打包工具（Webpack/Vite）**的工作基础：Vite利用浏览器原生支持ES模块的特性实现了开发环境的零打包启动，而生产构建仍需Rollup对模块进行合并和Tree Shaking优化。理解模块边界，也是**测试基础**中"单元测试"的前提——一个测试单元通常对应一个模块中的一个导出函数，模拟（Mock）依赖项本质上是在测试运行时替换`sys.modules`中的模块对象。