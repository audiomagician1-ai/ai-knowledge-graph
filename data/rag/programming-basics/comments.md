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
---
# 注释

## 概述

注释（Comment）是源代码中被编译器或解释器完全忽略、不参与程序执行的文本标记。注释的唯一目的是为阅读代码的人类提供说明信息，无论是原作者、团队协作者，还是几个月后回头看自己代码的自己。在Python中，单行注释以`#`符号开头；在C/C++和Java中，单行注释使用`//`，多行注释使用`/* ... */`包裹。

注释的历史可以追溯到1950年代早期的汇编语言时代。FORTRAN（1957年发布）是最早引入结构化注释机制的高级编程语言之一，允许程序员在打孔卡的特定列位置写入说明文字。随着软件工程在1970-1980年代逐步成熟，注释从"可选装饰"演变为团队协作和代码维护的必要工具。

在AI工程场景下，注释的价值被进一步放大。一个训练神经网络的脚本往往涉及复杂的数学变换、超参数选择和数据预处理逻辑，若不加注释，即便是原作者在两周后也难以快速理解某个`learning_rate=0.0003`的来由。注释是让实验可复现、让代码可交接的第一道保障。

---

## 核心原理

### 注释的语法规则与解析机制

Python解释器在词法分析（Lexical Analysis）阶段遇到`#`字符后，会跳过该字符直到行尾的所有内容，不生成任何Token。这意味着以下两段代码在执行效果上完全等价：

```python
# 设置学习率，根据消融实验结果选取0.001
learning_rate = 0.001
```

```python
learning_rate = 0.001
```

Python没有原生的多行注释语法，但程序员常用三引号字符串`"""..."""`或`'''...'''`来模拟多行注释效果。严格来说，这是一个字符串字面量（String Literal），解释器会解析它但不会赋值给任何变量，在优化阶段会被丢弃。这与真正的注释在字节码层面存在细微差异，但实际效果相同。

### 注释的三种功能类型

**解释型注释（Explanatory Comment）** 说明"这段代码做什么"，适合逻辑不直观的地方：

```python
# 将标签从 [0,1] 映射到 [-1,1]，满足SVM的决策边界要求
labels = labels * 2 - 1
```

**待办型注释（TODO Comment）** 标记未完成或需改进之处，通常写为`# TODO:`或`# FIXME:`格式。许多IDE（如VS Code、PyCharm）会自动高亮这类注释并在问题列表中聚合显示：

```python
# TODO: 替换为动态batch size，当前硬编码32仅适用于单GPU
batch_size = 32
```

**文档型注释（Docstring）** 位于函数、类或模块的第一行，使用三引号编写，供`help()`函数和自动化文档工具（如Sphinx）读取：

```python
def normalize(tensor, mean, std):
    """
    对输入张量进行Z-score标准化。
    
    Args:
        tensor: 形状为 (N, C, H, W) 的float32张量
        mean: 各通道均值，长度为C的列表
        std: 各通道标准差，长度为C的列表
    Returns:
        标准化后的张量，形状不变
    """
```

### 注释密度与可读性的平衡

过少的注释让代码难以维护，但过多的注释同样有害——它会引入"注释噪音"，让读者忽略真正重要的说明。业界经验规则是：**注释应解释"为什么"，而非"是什么"**。代码本身能清晰表达"是什么"，但选择某种算法、某个阈值的原因只有注释才能传达。例如，`i += 1  # 将i加1`是完全无价值的注释，而`threshold = 0.85  # 低于此值的预测在A/B测试中精确率下降超过12%`则提供了无法从代码本身获取的关键信息。

---

## 实际应用

**AI实验脚本中的超参数注释**

在模型训练代码中，超参数的选择往往基于实验结果或论文数据，必须用注释记录来源：

```python
# dropout率参照 "Dropout: A Simple Way to Prevent Neural Networks from Overfitting"
# (Srivastava et al., 2014) 推荐值，适用于全连接层
dropout_rate = 0.5

# warmup步数 = 总步数的10%，来自Google BERT原始实现
warmup_steps = total_steps // 10
```

**数据预处理的步骤注释**

数据清洗流程包含多个顺序依赖的步骤，注释能防止误操作：

```python
# 步骤1：先过滤缺失值，必须在归一化之前执行
# 否则NaN会导致均值计算偏移
df = df.dropna(subset=['feature_col'])

# 步骤2：归一化到[0,1]区间
df['feature_col'] = (df['feature_col'] - df['feature_col'].min()) / \
                    (df['feature_col'].max() - df['feature_col'].min())
```

**临时注释掉代码进行调试**

调试时常将某段代码用`#`暂时屏蔽，以对比执行效果。这是注释在开发过程中最高频的即时用法，但调试完成后应及时清理，避免遗留"僵尸代码"污染代码库。

---

## 常见误区

**误区一：注释可以替代清晰的变量命名**

有些初学者用`x`、`tmp`、`data2`等无意义变量名，然后依赖注释来解释含义，例如`x = 0.001  # 学习率`。正确做法是直接命名`learning_rate = 0.001`，注释留给变量名无法传达的深层原因。好的变量名和好的注释是互补关系，而非替代关系。

**误区二：注释掉的代码可以长期保留**

在版本控制系统（如Git）普及之前，程序员会注释掉旧代码以备"万一还要用"。但在使用Git的现代开发流程中，历史代码可以随时通过`git log`找回，注释掉的代码块只会让当前文件更难阅读。AI项目的训练脚本尤其容易积累大量被注释的实验代码，应定期清理或移入独立的实验分支。

**误区三：Docstring和普通注释功能相同**

Docstring（`"""..."""`）和`#`注释在用途上有本质区别。Docstring在运行时可通过`函数名.__doc__`属性访问，是Python反射机制的一部分，也是`help()`和Sphinx等工具自动生成API文档的数据来源。而`#`注释在运行时完全消失。将函数说明写成`#`注释而非Docstring，会导致自动文档生成工具无法提取任何信息。

---

## 知识关联

注释建立在对**Hello World**程序的理解之上——当你写下第一行`print("Hello World")`时，在其上方加`# 输出问候语`就是注释的最基础形态。掌握注释是后续所有编程学习的书写规范基础：学习**变量与数据类型**时，需要注释说明变量的物理含义；学习**函数定义**时，Docstring成为函数接口的正式说明；在AI工程的**模型训练流程**中，注释记录实验假设与超参数来源，是实验可复现性的保障工具。
