# 模型合并

## 概述
模型合并(Model Merging)是一种不需要额外训练的模型组合技术, 通过直接操作模型权重将多个模型的能力融合到一个模型中。

## 核心技术

### 线性插值(Linear Interpolation)
最简单的合并方法: W_merged = α * W_A + (1-α) * W_B
- 适用于相同架构的模型
- α控制两个模型的混合比例

### SLERP (球面线性插值)
在权重空间的球面上进行插值:
- 保持权重向量的范数特性
- 产生更平滑的过渡
- 常用于合并两个模型

### TIES-Merging
1. **Trim**: 裁剪每个模型中微调后变化最小的权重
2. **Elect Sign**: 对冲突的权重方向投票决定符号
3. **Disjoint Merge**: 合并非冲突权重

### DARE (Drop And REscale)
- 随机丢弃一定比例的微调delta权重
- 重新缩放保留的权重以维持期望值
- 可与TIES组合使用(DARE-TIES)

### Task Arithmetic
- 计算任务向量: τ = W_finetuned - W_base
- 合并: W_merged = W_base + λ₁τ₁ + λ₂τ₂
- 支持任务加法、否定、组合

## 应用场景
- 开源社区模型定制(MergeKit工具)
- 多能力模型融合(代码+推理+创意)
- 无需GPU的模型改进
- A/B测试中的渐进迁移

## 工具
- **MergeKit**: 最流行的开源合并工具
- **LazyMergeKit**: Colab友好的简化版
- Hugging Face模型合并可视化

## 局限性
- 仅适用于相同架构的模型
- 合并效果不稳定, 需要实验调优
- 缺乏理论保证
