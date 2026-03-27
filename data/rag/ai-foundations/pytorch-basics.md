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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# PyTorch基础

## 概述

PyTorch是由Facebook AI Research（FAIR）团队于2016年发布的开源深度学习框架，基于Torch库用Python重新实现。与早期的静态计算图框架（如TensorFlow 1.x）不同，PyTorch采用**动态计算图（Dynamic Computational Graph）**机制，即"Define-by-Run"模式，允许在运行时构建和修改计算图，使调试过程更接近普通Python代码的体验。

PyTorch的核心数据结构是`torch.Tensor`，它是一个支持GPU加速的多维数组，在语法上高度兼容NumPy的`ndarray`。截至2023年，PyTorch已成为学术界最主流的深度学习框架，NeurIPS、ICML等顶级会议中超过70%的论文实现使用PyTorch。掌握PyTorch是将神经网络理论转化为可运行代码的关键一步。

---

## 核心原理

### 1. Tensor（张量）：PyTorch的基本单位

`torch.Tensor`是PyTorch中所有计算的基础。张量可以理解为神经网络基础中"权重矩阵"的实际载体。创建张量的常见方式包括：

```python
import torch
x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])  # 从Python列表创建
y = torch.zeros(3, 4)       # 3行4列的全零张量
z = torch.randn(2, 3)       # 服从标准正态分布的随机张量
```

张量具有三个关键属性：`dtype`（数据类型，如`torch.float32`）、`shape`（形状，如`torch.Size([2, 3])`）和`device`（所在设备，`cpu`或`cuda:0`）。将张量移动到GPU只需调用`.to('cuda')`或`.cuda()`方法，这一操作直接对应神经网络训练时的GPU并行加速。

### 2. Autograd：自动微分机制

PyTorch的自动微分系统`torch.autograd`是反向传播算法的工程实现。当一个张量的`requires_grad=True`时，PyTorch会追踪所有对它的操作，并构建一个有向无环图（DAG）来记录计算历史。

调用`.backward()`时，PyTorch按链式法则（Chain Rule）从结果节点向输入节点逐层计算梯度，结果存储在每个叶子张量的`.grad`属性中。以一个简单的标量函数为例：

```python
x = torch.tensor(3.0, requires_grad=True)
y = x ** 2 + 2 * x          # y = x² + 2x
y.backward()
print(x.grad)                # 输出 tensor(8.)，即 dy/dx = 2x+2 在x=3处的值
```

这一机制让函数（如均方误差、交叉熵）的梯度计算完全自动化，无需手工推导。

### 3. `nn.Module`：构建神经网络的标准方式

`torch.nn.Module`是定义神经网络层和完整模型的基类。一个自定义网络需要继承`nn.Module`并实现两个方法：`__init__`（定义层的结构）和`forward`（定义前向传播逻辑）。

```python
import torch.nn as nn

class SimpleMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 128)   # 输入784维，输出128维
        self.fc2 = nn.Linear(128, 10)    # 输出10个类别
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)
```

`nn.Linear(in, out)`内部自动创建形状为`(out, in)`的权重矩阵和形状为`(out,)`的偏置向量，并默认设置`requires_grad=True`，与神经网络基础中线性层公式 $\mathbf{y} = W\mathbf{x} + \mathbf{b}$ 直接对应。

### 4. 训练循环：优化器与损失函数

一个标准的PyTorch训练迭代（单个batch）包含以下五个步骤，顺序不可颠倒：

```python
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
loss_fn = nn.CrossEntropyLoss()

# 标准训练步骤
optimizer.zero_grad()          # ① 清空上一步累积的梯度
outputs = model(inputs)        # ② 前向传播
loss = loss_fn(outputs, labels) # ③ 计算损失
loss.backward()                # ④ 反向传播，计算梯度
optimizer.step()               # ⑤ 更新参数
```

`optimizer.zero_grad()`必须在每次`backward()`前调用，因为PyTorch默认会将梯度**累加**而非覆盖，这是初学者最常遗漏的一步。

---

## 实际应用

**图像分类的完整流程**：使用`torchvision.datasets.MNIST`加载手写数字数据集，配合`torch.utils.data.DataLoader`进行批量加载（`batch_size=64`），将28×28像素图像展平为784维向量后，输入上述`SimpleMLP`进行10分类训练。整个流程从数据加载到模型保存（`torch.save(model.state_dict(), 'model.pth')`）可在约50行Python代码内完成。

**迁移学习**：调用`torchvision.models.resnet50(pretrained=True)`加载预训练的ResNet-50模型，冻结特征提取层的梯度（`param.requires_grad = False`），仅替换并训练最后的全连接层，可在小数据集上快速获得高精度分类器，这是PyTorch在工业实践中最高频的使用模式之一。

---

## 常见误区

**误区一：忘记调用`model.eval()`导致测试结果不稳定**  
`nn.Dropout`和`nn.BatchNorm`在训练和推理阶段行为不同。训练时需调用`model.train()`，推理时必须调用`model.eval()`切换模式，否则Dropout会继续随机丢弃神经元，BatchNorm会使用batch统计量而非存储的滑动均值，导致每次推理结果不同。

**误区二：将NumPy数组和Tensor混用导致设备不匹配**  
NumPy数组只能存在于CPU内存，若模型已移至GPU（`.cuda()`），将NumPy数组直接传入模型会报错`RuntimeError: Expected all tensors to be on the same device`。正确做法是先用`torch.from_numpy(arr)`将NumPy数组转换为Tensor，再调用`.to(device)`统一设备。

**误区三：误以为`.backward()`可以多次调用**  
默认情况下，调用一次`.backward()`后，PyTorch会**释放**计算图以节省内存。若需要多次反向传播（如某些元学习算法），必须在第一次调用时传入参数`loss.backward(retain_graph=True)`，否则第二次调用会抛出`RuntimeError: Trying to backward through the graph a second time`。

---

## 知识关联

**与函数的关联**：PyTorch中的激活函数（ReLU、Sigmoid、Tanh）和损失函数（MSELoss、CrossEntropyLoss）都以Python可调用对象形式存在。`nn.ReLU()`本质上是将数学函数 $f(x) = \max(0, x)$ 封装为`nn.Module`，其求导行为（次梯度）由Autograd自动处理。理解函数的定义域和值域直接决定了选择哪种损失函数——回归任务使用MSE，分类任务使用CrossEntropyLoss（内部已整合了Softmax运算）。

**与神经网络基础的关联**：神经网络基础中抽象描述的"层"、"权重"、"偏置"、"前向传播"和"反向传播"，在PyTorch中分别对应`nn.Linear`/`nn.Conv2d`、`.weight`属性、`.bias`属性、`forward()`方法和`.backward()`调用。PyTorch的`nn.Sequential`容器可直接将若干层按顺序串联，对应神经网络基础中"多层感知机"的层叠结构。掌握PyTorch后，可进一步学习`torch.nn.Transformer`等复杂模块，以及使用`torch.onnx.export`进行模型部署。