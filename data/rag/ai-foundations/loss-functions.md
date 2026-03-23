---
id: "loss-functions"
concept: "损失函数"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 5
is_milestone: false
tags: ["DL"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "pending-rescore"
quality_score: 41.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 损失函数

## 概述

损失函数（Loss Function），又称代价函数（Cost Function）或目标函数（Objective Function），是衡量机器学习模型预测值与真实值之间偏差程度的数学函数。其形式化定义为 $L(\hat{y}, y)$，其中 $\hat{y}$ 为模型预测值，$y$ 为真实标签。损失函数的核心作用是将模型的"预测质量"量化为一个标量值，使得梯度下降等优化算法得以调整模型参数。历史上，最小二乘法（OLS）于1805年由勒让德（Adrien-Marie Legendre）正式发表，这是最早被系统化使用的损失函数形式之一，比高斯在1809年发布的版本还早四年。

损失函数的选择直接决定了模型优化的方向。以均方误差（MSE）为例，其对大误差施加的惩罚是小误差的平方倍，这一特性使得模型会优先修正预测偏差极大的样本；而交叉熵损失则通过对数形式对错误分类的置信度进行指数级惩罚，适合概率输出的分类任务。Goodfellow等人在《Deep Learning》（Goodfellow et al., 2016）中明确指出，损失函数的设计是神经网络工程中影响训练稳定性和最终性能最重要的超参数决策之一。

## 核心原理

### 回归任务的损失函数

均方误差（Mean Squared Error，MSE）是回归任务中最常用的损失函数，定义为：

$$L_{\text{MSE}} = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2$$

MSE对异常值极为敏感，因为单个大误差被平方后会在总损失中占据主导地位。为缓解这一问题，Huber损失函数（由Peter Huber于1964年提出）引入了分段函数形式：当残差 $|y - \hat{y}| \leq \delta$ 时采用二次形式，超过阈值 $\delta$ 后改用线性形式，从而在MSE和平均绝对误差（MAE）之间取得平衡：

$$L_{\delta}(y, \hat{y}) = \begin{cases} \frac{1}{2}(y - \hat{y})^2 & \text{若 } |y - \hat{y}| \leq \delta \\ \delta |y - \hat{y}| - \frac{\delta^2}{2} & \text{否则} \end{cases}$$

MAE（平均绝对误差）定义为 $L_{\text{MAE}} = \frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|$，其梯度在残差为零处不连续，这是MAE在深度学习中训练稳定性不如MSE的核心原因。

### 分类任务的损失函数

二元交叉熵（Binary Cross-Entropy）是二分类任务的标准损失函数，其数学形式来源于最大似然估计：

$$L_{\text{BCE}} = -\frac{1}{n}\sum_{i=1}^{n}\left[y_i \log(\hat{y}_i) + (1 - y_i)\log(1 - \hat{y}_i)\right]$$

对于多分类问题，交叉熵推广为：

$$L_{\text{CE}} = -\sum_{c=1}^{C} y_c \log(\hat{p}_c)$$

其中 $C$ 为类别总数，$\hat{p}_c$ 为Softmax层输出的第 $c$ 类概率。值得注意的是，交叉熵损失与KL散度（Kullback-Leibler Divergence）之间存在直接关联：$L_{\text{CE}} = H(y, \hat{p}) = H(y) + D_{\text{KL}}(y \| \hat{p})$，在真实标签为one-hot分布时，$H(y) = 0$，因此最小化交叉熵等价于最小化KL散度。

### 特殊任务的损失函数

合页损失（Hinge Loss）专为支持向量机（SVM）设计，定义为 $L_{\text{hinge}} = \max(0, 1 - y \cdot \hat{y})$，其中 $y \in \{-1, +1\}$。这一形式保证了只有支持向量才对最终损失有贡献，内部点（置信度超过边界的样本）贡献为零，这是SVM稀疏解特性的数学根源。

生成对抗网络（GAN）中的损失函数设计尤为复杂。Goodfellow在2014年提出的原始GAN使用二元交叉熵，判别器损失为 $L_D = -[\log D(x) + \log(1 - D(G(z)))]$，但这导致了训练初期生成器梯度消失的问题。Arjovsky等人（Arjovsky et al., 2017）在Wasserstein GAN中引入Earth Mover距离，将判别器改为Critic，彻底规避了JS散度在分布不重叠时梯度为零的理论缺陷。

## 实际应用

**PyTorch中的损失函数实现**：以下代码展示了在图像分类任务中使用交叉熵损失的标准写法：

```python
import torch
import torch.nn as nn

# 多分类交叉熵：内置了LogSoftmax + NLLLoss
criterion = nn.CrossEntropyLoss()

# logits: [batch_size, num_classes]，注意不需要先经过Softmax
logits = model(images)  # shape: [32, 10]
labels = torch.tensor([3, 7, 1, ...])  # 整数类别索引

loss = criterion(logits, labels)
loss.backward()  # 反向传播计算梯度
```

需特别注意：`nn.CrossEntropyLoss` 内部已包含Softmax计算，若在模型末层手动添加Softmax后再传入此函数，会导致重复计算，产生数值错误。

**医学影像分割中的Dice损失**：在语义分割任务中，当目标区域面积占比极小（如肿瘤分割中阳性像素不足1%）时，交叉熵损失会退化为几乎只预测背景类的平凡解。Dice损失通过直接优化Dice系数 $\text{Dice} = \frac{2|A \cap B|}{|A| + |B|}$ 来缓解类别不平衡问题，其损失形式为 $L_{\text{Dice}} = 1 - \frac{2\sum p_i g_i}{\sum p_i + \sum g_i}$，其中 $p_i$ 和 $g_i$ 分别为预测概率和真实标签。

**推荐系统中的BPR损失**：贝叶斯个性化排序（Bayesian Personalized Ranking, Rendle et al., 2009）使用专门的排序损失 $L_{\text{BPR}} = -\sum_{(u,i,j) \in D} \ln \sigma(\hat{x}_{ui} - \hat{x}_{uj})$，其中样本三元组 $(u, i, j)$ 表示用户 $u$ 对物品 $i$ 的偏好高于物品 $j$，直接优化物品的相对排序而非绝对评分预测。

## 常见误区

**误区一：损失函数越小，模型性能越好。** 损失值低仅说明模型在训练集上的拟合程度高，与测试集上的泛化性能无直接因果关系。当正则化项缺失时，过拟合模型的训练损失可以无限趋近于零，但测试集精度可能急剧下降。正确做法是同时监控训练损失与验证集评估指标，两者出现持续背离时即为过拟合信号。

**误区二：回归任务默认用MSE，分类任务默认用交叉熵，无需思考选择。** 这一"默认规则"在特定场景下会失效。例如，当预测目标存在长尾分布（如房价预测）时，直接对原始值使用MSE会导致高价房屋主导梯度；此时应对目标变量取对数，或改用分位数回归损失（Quantile Loss）$L_\alpha = \max(\alpha(y - \hat{y}), (\alpha - 1)(y - \hat{y}))$。类似地，目标检测中的边界框回归使用IoU损失而非MSE，因为后者无法反映框的重叠程度。

**误区三：损失函数与评估指标可以互换使用。** AUC、F1分数、mAP等评估指标因不可微（含有阈值操作、排序操作）而无法直接用于梯度优化。损失函数必须在参数空间几乎处处可微，而评估指标关注的是最终业务效果。两者的不一致性是"代理指标问题"的来源，需通过合理的损失函数设计来间接优化目标评估指标。

## 思考题

1. 假设你正在训练一个识别罕见疾病的二分类模型，数据集中阳性样本仅占0.1%。标准二元交叉熵损失会导致什么问题？Focal Loss（Lin et al., 2017）通过引入参数 $(1 - \hat{p}_t)^\gamma$ 调制因子如何解决这一问题？请说明 $\gamma > 0$ 时该调制因子对易分类样本梯度的抑制效果。

2. 在GAN的训练中，为什么不能用MSE作为生成器的损失函数，直接最小化生成图像与真实图像在像素空间的距离？从感知质量的角度，这种做法会产生什么具体问题（提示：思考"平均脸"现象）？

3. 同样是优化交叉熵损失，为什么标签平滑（Label Smoothing）技术——将one-hot标签中的1替换为 $1 - \epsilon$，将0替换为 $\epsilon / (C-1)$——能提高模型在测试集上的校准性（Calibration）？这一修改对交叉熵损失的梯度产生了怎样的具体影响？
