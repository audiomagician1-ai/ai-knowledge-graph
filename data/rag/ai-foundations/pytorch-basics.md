---
id: "pytorch-basics"
concept: "PyTorch基础"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 5
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 93.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# PyTorch基础

## 概述

PyTorch是由Facebook AI Research（FAIR）团队于2016年发布的开源深度学习框架，基于Lua语言的Torch库重构而来，采用Python作为主要接口。与TensorFlow 1.x的静态计算图不同，PyTorch从设计之初就采用**动态计算图**（Define-by-Run）机制，即计算图在代码执行时即时构建，而非预先编译，这使得调试神经网络模型与调试普通Python程序几乎没有区别。

PyTorch的核心数据结构是**张量（Tensor）**，它是多维数组的推广，可以看作是NumPy的ndarray在GPU加速和自动微分上的升级版本。一个标量是0维张量，向量是1维张量，矩阵是2维张量，卷积神经网络中的图像批次则通常是形如`(N, C, H, W)`的4维张量，其中N为批次大小、C为通道数、H和W为空间维度。

PyTorch在学术研究领域占据主导地位，截至2023年，超过60%的顶会论文（NeurIPS、ICML等）使用PyTorch实现实验。其重要性不仅在于提供数值计算工具，更在于它将**自动微分**与**GPU加速**封装成对开发者透明的接口，让研究者能够专注于模型架构设计而非底层矩阵运算。

---

## 核心原理

### 张量操作与内存管理

PyTorch张量支持与NumPy几乎一致的切片、广播和矩阵运算语法。创建张量的常用方式包括：`torch.zeros(3, 4)`创建全零矩阵，`torch.randn(2, 3)`从标准正态分布采样，`torch.tensor([1.0, 2.0, 3.0])`从Python列表直接转换。

**内存共享机制**是PyTorch区别于NumPy的重要细节：通过`.view()`操作重塑张量时，新旧张量共享同一块内存；而`.reshape()`在数据不连续时会触发内存拷贝。张量的`.contiguous()`方法可强制使内存连续，这在跨操作传递张量时往往是必要的前置步骤。张量设备迁移通过`.to('cuda')`或`.cuda()`完成，从GPU取回数据则需`.cpu()`，混用CPU和GPU张量会触发`RuntimeError`。

### 自动微分与计算图

PyTorch的`autograd`模块实现了反向传播所需的自动微分。当张量的`requires_grad=True`时，PyTorch会追踪所有对该张量的操作，并在内存中构建一张有向无环图（DAG），图中每个节点存储一个`grad_fn`对象，记录产生该张量的运算及其局部梯度函数。

对标量损失调用`.backward()`时，PyTorch沿计算图逆向执行链式法则，将梯度累积到每个叶子张量的`.grad`属性上。公式上，对于复合函数 $L = f(g(x))$，链式法则给出：

$$\frac{\partial L}{\partial x} = \frac{\partial L}{\partial g} \cdot \frac{\partial g}{\partial x}$$

**梯度累积**是初学者常踩的陷阱：PyTorch默认将新梯度**累加**到`.grad`上，因此训练循环中必须在每次反向传播前调用`optimizer.zero_grad()`清零梯度，否则梯度会跨迭代叠加，导致参数更新错误。

### `nn.Module`与模型构建

`torch.nn.Module`是所有神经网络层和模型的基类。自定义模型需继承`nn.Module`并实现`__init__`和`forward`两个方法：`__init__`中用`self.fc = nn.Linear(128, 64)`等语句注册可训练参数，`forward`定义数据流向。框架会自动通过`.parameters()`方法收集所有已注册的参数，供优化器使用。

`nn.Sequential`提供了一种按顺序堆叠层的简写形式：`nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 10))`可直接构成一个两层MLP。`nn.Linear(in, out)`内部持有形状为`(out, in)`的权重矩阵和形状为`(out,)`的偏置向量，执行运算 $y = xW^T + b$。

---

## 实际应用

**标准训练循环**是使用PyTorch的核心范式，由五个固定步骤构成：
1. `optimizer.zero_grad()`——清零梯度
2. `outputs = model(inputs)`——前向传播
3. `loss = criterion(outputs, labels)`——计算损失（如`nn.CrossEntropyLoss`已内置Softmax）
4. `loss.backward()`——反向传播
5. `optimizer.step()`——更新参数（如`torch.optim.Adam(model.parameters(), lr=1e-3)`）

**数据加载**方面，PyTorch提供`Dataset`和`DataLoader`两个抽象。自定义`Dataset`需实现`__len__`和`__getitem__`；`DataLoader`则负责批次化、多进程预取（`num_workers=4`）和随机打乱（`shuffle=True`）。对于图像任务，`torchvision.datasets.ImageFolder`可直接读取按类别子目录组织的图片，配合`transforms.Compose([transforms.Resize(224), transforms.ToTensor(), transforms.Normalize(mean, std)])`完成预处理流水线。

**模型保存与加载**推荐只保存参数字典：`torch.save(model.state_dict(), 'model.pth')`，加载时先实例化模型再`model.load_state_dict(torch.load('model.pth'))`，避免保存整个模型对象导致的类路径依赖问题。

---

## 常见误区

**误区一：忘记调用`model.eval()`进行推理**
`Dropout`层在训练时随机屏蔽神经元，在推理时需关闭；`BatchNorm`层在训练时使用批次统计量，在推理时使用运行均值和方差。`model.eval()`会切换这两类层的行为，而`model.train()`还原。仅用`torch.no_grad()`（禁止梯度计算以节省显存）并不能替代`model.eval()`，两者作用不同，推理时应同时使用。

**误区二：混淆`nn.CrossEntropyLoss`的输入格式**
`nn.CrossEntropyLoss`期望模型输出为**未经Softmax的原始logits**，形状为`(N, C)`，标签为整数类别索引，形状为`(N,)`。若在模型末尾已加`nn.Softmax`后再传入此损失函数，会导致数值梯度异常（因为对log(softmax(softmax(x)))求导会错误压缩梯度范围）。

**误区三：在CPU和GPU间传递张量时忘记同步**
GPU操作是异步的，`loss.item()`会强制同步CPU和GPU，而直接打印张量或对GPU张量调用Python标量运算同样会触发同步。在性能敏感的训练循环中，每步都调用`.item()`会显著降低吞吐量；建议每N步打印一次损失，或使用`torch.cuda.synchronize()`在明确需要同步时手动调用。

---

## 知识关联

学习PyTorch基础需要扎实的**函数**概念基础：`forward`方法本质上是将输入张量映射到输出张量的数学函数，而`autograd`对这些函数进行符号微分，因此理解函数的复合与链式法则是理解反向传播计算图的前提。

**神经网络基础**中的感知机、激活函数、损失函数等概念直接对应PyTorch中的`nn.Linear`、`nn.ReLU`/`nn.Sigmoid`、`nn.MSELoss`/`nn.CrossEntropyLoss`等模块，PyTorch将这些数学结构具象化为可组合的Python对象。掌握PyTorch基础后，可进一步学习卷积神经网络（`nn.Conv2d`、`nn.MaxPool2d`）、循环神经网络（`nn.LSTM`）以及使用`torch.jit.script`将动态图转为静态图以部署到生产环境等进阶话题。