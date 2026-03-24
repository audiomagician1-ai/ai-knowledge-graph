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
quality_tier: "pending-rescore"
quality_score: 41.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 模块与导入

## 概述

模块（Module）是将相关代码组织在独立文件中的编程单元，通过导入（Import）机制在不同文件间共享功能。Python 中每个 `.py` 文件天然就是一个模块，而 JavaScript 在 ES2015（ES6）标准引入 `import/export` 语法之前，长期依赖 CommonJS 的 `require()` 函数实现类似功能。

模块化的核心价值在于**命名空间隔离**：两个不同模块中都可以定义名为 `calculate` 的函数，不会产生冲突，因为它们分别属于各自的模块作用域。这解决了早期 JavaScript 全局变量污染的历史问题——在 `<script>` 标签时代，所有变量都挂载在 `window` 对象上，大型项目极易出现命名碰撞。

在 AI 工程实践中，模块与导入是组织数据预处理、模型训练、推理服务等不同功能代码的基础手段。PyTorch 的 `torch.nn`、`torch.optim` 等子模块，以及 Hugging Face 的 `transformers.AutoModel`，都依赖 Python 的模块系统进行组织和分发。

---

## 核心原理

### Python 的模块导入机制

Python 解释器执行 `import numpy as np` 时，按以下顺序查找模块：
1. `sys.modules` 缓存（已导入则直接返回，不重复执行）
2. 内置模块（如 `math`、`os`）
3. `sys.path` 列表中的目录（包含当前目录、安装包路径等）

这意味着同一进程中多次 `import` 同一模块，其顶层代码**只执行一次**。AI 训练脚本中加载大型词表或配置文件时，通常利用此特性做全局单例缓存。

Python 支持四种导入语法：
```python
import os                        # 导入整个模块
from pathlib import Path         # 从模块导入特定名称
from sklearn.metrics import *    # 通配符导入（不推荐）
import numpy as np               # 别名导入
```

通配符导入 `import *` 会将目标模块 `__all__` 列表中的所有名称注入当前命名空间，在大型 AI 项目中极易造成名称遮蔽（shadowing），应当避免。

### JavaScript 的 ES Module 与 CommonJS 对比

ES Module（ESM）使用静态的 `import/export` 语法，在代码解析阶段（非执行阶段）就确定依赖关系，使打包工具如 Webpack 和 Vite 能够执行 **Tree Shaking**（死代码消除）。CommonJS 的 `require()` 是运行时动态加载，无法静态分析，因此无法做 Tree Shaking。

```javascript
// ESM - 静态导入，支持 Tree Shaking
import { pipeline } from '@huggingface/transformers';

// CommonJS - 动态导入，运行时才确定依赖
const { pipeline } = require('@huggingface/transformers');
```

ESM 的 `export` 分为**命名导出**（Named Export）和**默认导出**（Default Export）两类，对应不同的导入语法：
```javascript
// 命名导出与导入
export function preprocess(text) { ... }
import { preprocess } from './utils.js';

// 默认导出与导入
export default class ModelWrapper { ... }
import ModelWrapper from './model.js';
```

### Python 包（Package）与 `__init__.py`

当目录中存在 `__init__.py` 文件时，该目录被识别为 Python **包**（Package）。`__init__.py` 在包被首次导入时自动执行，常用于控制对外暴露的公共 API。例如在 AI 项目中：

```python
# myproject/__init__.py
from .data_loader import DataLoader
from .trainer import Trainer
__all__ = ['DataLoader', 'Trainer']  # 明确声明公共接口
```

Python 3.3 起引入了**命名空间包**（Namespace Package），不需要 `__init__.py` 也能识别包，但无法在 `__init__.py` 中集中控制 API，通常不适合用于需要明确接口的 AI 库开发。

---

## 实际应用

**AI 项目标准目录结构中的模块划分**：典型的 PyTorch 训练项目会将代码拆分为 `dataset.py`（数据加载）、`model.py`（网络结构）、`train.py`（训练循环）、`evaluate.py`（评估逻辑）等模块，`train.py` 通过 `from model import TransformerNet` 导入模型类。这种划分使不同团队成员能并行修改不同模块而不产生 Git 冲突。

**循环导入的排查**：`module_a` 导入 `module_b`，而 `module_b` 又导入 `module_a`，Python 会抛出 `ImportError: cannot import name 'X' from partially initialized module`。解决方案通常是将共享的类型定义提取到第三个模块（如 `types.py`）中，或将导入语句移入函数体内延迟执行。

**`importlib` 动态加载模型**：AI 推理服务需要根据请求参数动态加载不同版本的模型时，可使用 `importlib.import_module('models.v2.bert')` 在运行时按字符串路径导入模块，而非在启动时静态导入所有模型占用内存。

---

## 常见误区

**误区一：认为 `from module import func` 比 `import module` 更高效**。两者执行时，Python 都会完整加载并缓存整个模块文件，区别仅在于将哪个名称绑定到当前命名空间。`from numpy import array` 并不会只加载 NumPy 的 `array` 函数，整个 NumPy 照样被初始化。

**误区二：混淆 Python 的相对导入和绝对导入**。`from .utils import helper` 中的点号表示**相对导入**，从当前包的同级目录查找；而 `from utils import helper` 是**绝对导入**，从 `sys.path` 根目录查找。直接运行某个模块文件（`python mypackage/train.py`）时，相对导入会报 `ImportError`，必须以包的方式运行（`python -m mypackage.train`）才能正确解析相对路径。

**误区三：将 `__init__.py` 写得过于臃肿**。将大量业务逻辑堆入 `__init__.py` 会导致任何 `import mypackage` 操作都触发重量级初始化，拖慢 AI 服务的冷启动时间。`__init__.py` 应只做轻量的 API 再导出，具体实现保留在子模块中。

---

## 知识关联

模块与导入建立在**函数**概念之上：模块的本质是将多个函数（及类、常量）按职责分组打包，`import` 语句让调用方能访问这些函数而不必复制代码。没有函数级别的代码封装，模块化就失去了意义。

掌握模块与导入后，可以直接进入 **Webpack/Vite 等打包工具**的学习——这些工具的核心工作就是分析 ESM 的 `import` 依赖图、合并模块、消除死代码；理解静态 `import` 与动态 `import()` 的区别是理解代码分割（Code Splitting）的前提。**包管理**（npm/pip）是模块的分发层，`pip install torch` 本质是将 `torch` 这个包放入 `sys.path` 可访问的位置，使 `import torch` 能够成功解析。**测试基础**中，每个测试文件本身就是一个独立模块，测试框架通过模块导入机制自动发现并执行测试函数。
