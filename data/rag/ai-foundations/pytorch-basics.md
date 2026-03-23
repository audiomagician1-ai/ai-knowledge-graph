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
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# PyTorch基础

## 概述

PyTorch是由Facebook AI Research（FAIR）于2016年发布的开源深度学习框架，基于Lua语言的Torch库重写为Python版本。其核心设计哲学是"动态计算图"（Dynamic Computational Graph），与TensorFlow 1.x的静态图形成鲜明对比——PyTorch在代码执行时即时构建计算图，而非预先编译，这使得调试神经网络的过程与调试普通Python代码几乎完全相同。

PyTorch的基本数据结构是`torch.Tensor`，它与NumPy的`ndarray`高度相似但支持GPU加速计算。截至2024年，PyTorch已成为学术界最主流的深度学习框架，在Papers With Code统计的顶会论文中占比超过70%。理解PyTorch基础意味着能够用张量运算表达神经网络的前向传播，并借助自动微分机制完成参数更新。

---

## 核心原理

### 张量（Tensor）与设备管理

`torch.Tensor`是PyTorch中所有计算的基础单元。一个形状为`(batch_size, channels, H, W)`的4D张量是卷积网络中图像批次的标准表示。创建张量的常用方式包括：

```python
import torch
x = torch.zeros(3, 4)       # 形状(3,4)的全零张量
y = torch.randn(2, 3)       # 标准正态分布随机张量
z = torch.tensor([1.0, 2.0]) # 从Python列表创建
```

设备管理通过`.to(device)`或`.cuda()`实现，将张量从CPU迁移到GPU只需一行代码：`x = x.to("cuda")`。张量的`dtype`属性决定数值精度，`torch.float32`是训练时的默认类型，而推理阶段常使用`torch.float16`以节省显存。

### 自动微分（Autograd）

PyTorch的自动微分系统`torch.autograd`是反向传播的实现核心。当张量的`requires_grad=True`时，PyTorch会记录对该张量的所有运算，构成一个有向无环图（DAG）。调用`.backward()`时，PyTorch沿该图从输出到输入自动计算梯度，结果存储在每个叶子张量的`.grad`属性中。

链式法则的具体实现：若 $L = f(g(x))$，则 $\frac{\partial L}{\partial x} = \frac{\partial L}{\partial f} \cdot \frac{\partial f}{\partial g} \cdot \frac{\partial g}{\partial x}$。PyTorch通过记录每步操作对应的梯度函数（`grad_fn`）来完成这一链式计算。使用`torch.no_grad()`上下文管理器可暂停梯度追踪，推理时节省约30%的显存。

```python
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2 + 2 * x
y.backward()
print(x.grad)  # 输出 tensor(8.) = 2*3 + 2
```

### `nn.Module`与模型构建

`torch.nn.Module`是所有神经网络层和模型的基类。自定义网络必须继承`nn.Module`并实现`__init__`和`forward`两个方法。`__init__`中定义层结构，`forward`中定义数据流向：

```python
import torch.nn as nn

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)  # 输入784维，输出256维
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        return self.fc2(x)
```

`nn.Linear(in, out)`内部维护形状为`(out, in)`的权重矩阵和形状为`(out,)`的偏置向量，二者均为`requires_grad=True`的张量，由框架自动纳入梯度计算。

### 训练循环：优化器与损失函数

完整的PyTorch训练循环包含固定的五个步骤：①前向传播计算预测值；②计算损失（如`nn.CrossEntropyLoss`）；③调用`optimizer.zero_grad()`清空历史梯度；④调用`loss.backward()`计算新梯度；⑤调用`optimizer.step()`更新参数。

```python
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
criterion = nn.CrossEntropyLoss()

for inputs, labels in dataloader:
    outputs = model(inputs)
    loss = criterion(outputs, labels)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

遗漏第③步`zero_grad()`是初学者最常见的错误，会导致梯度在每个batch间累加，训练结果完全不可预期。

---

## 实际应用

**MNIST手写数字分类**是验证PyTorch基础掌握程度的标准任务。使用`torchvision.datasets.MNIST`加载数据，通过`torch.utils.data.DataLoader`设置`batch_size=64`进行批次迭代，配合上述`MLP`模型，在CPU上训练5个epoch通常可达97%以上的测试准确率。

**模型保存与加载**使用`torch.save(model.state_dict(), "model.pth")`保存参数字典，而非直接保存整个模型对象。加载时需先实例化模型类，再调用`model.load_state_dict(torch.load("model.pth"))`。这种方式使模型参数与架构定义分离，便于跨环境部署。

**GPU加速实战**中，将模型和数据同时迁移到同一设备是必要条件：`model.to(device)`和`inputs.to(device)`缺一不可，否则会触发`RuntimeError: Expected all tensors to be on the same device`。

---

## 常见误区

**误区一：混淆`model.train()`与`model.eval()`的作用。** 这两个方法并不影响梯度计算，而是控制`nn.Dropout`和`nn.BatchNorm`层的行为模式。`Dropout`在`eval()`模式下完全关闭（不随机丢弃神经元），`BatchNorm`在`eval()`模式下使用训练时统计的运行均值和方差而非当前批次统计量。验证集评估时若未切换到`eval()`模式，会导致结果因随机Dropout而产生波动。

**误区二：认为`loss.backward()`会自动重置梯度。** PyTorch的`backward()`只负责计算并累加梯度，绝不清零。如果训练循环中缺少`optimizer.zero_grad()`，第n步的梯度将叠加到第n-1步残留的梯度上，相当于使用了错误的梯度方向更新参数。

**误区三：在`forward()`中修改`requires_grad=False`的叶子张量。** 直接对参数做原地操作（如`param.data += 1`）会破坏autograd图，导致后续反向传播报错或梯度计算错误。参数更新应始终通过优化器完成。

---

## 知识关联

**与神经网络基础的衔接：** 神经网络基础中学习的全连接层、激活函数和损失函数，在PyTorch中分别对应`nn.Linear`、`torch.relu`/`torch.sigmoid`和`nn.CrossEntropyLoss`/`nn.MSELoss`。反向传播算法中手动推导的链式法则，在PyTorch中由`autograd`自动执行，学习PyTorch基础的过程本质上是将数学公式映射为可执行代码的过程。

**与函数概念的衔接：** Python函数是理解`nn.Module`工作机制的必要基础。`forward()`方法使得模型实例可以像函数一样被调用（`output = model(input)`），这依赖Python的`__call__`机制——`nn.Module`的`__call__`在执行用户定义的`forward`前后还会自动处理钩子（hooks）注册等底层操作。

掌握PyTorch基础后，可进一步学习卷积神经网络（使用`nn.Conv2d`）、循环神经网络（使用`nn.LSTM`）、以及基于`torch.utils.data.Dataset`的自定义数据集构建，这些均在PyTorch基础的张量操作和`nn.Module`体系之上扩展。
