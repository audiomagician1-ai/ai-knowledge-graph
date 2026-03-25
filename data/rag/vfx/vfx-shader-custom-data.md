---
id: "vfx-shader-custom-data"
concept: "自定义数据"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 自定义数据

## 概述

自定义数据（Custom Data）是Unity粒子系统中一种将每粒子自定义数值从CPU端传递至GPU Shader的专用管线机制。通过在粒子系统的**Custom Data**模块中配置最多两组数据流（CustomData1和CustomData2），开发者可以为每个粒子附加最多8个浮点数（每组4个分量，以Vector或Float形式存储），这些数值在粒子生命周期内随时间曲线动态变化，并最终通过顶点属性流（Vertex Streams）注入到Shader的输入结构中。

该机制的引入是为了解决粒子Shader中"纹理UV动画参数、溶解强度、自定义颜色混合权重"等无法通过内置属性表达的个性化控制需求。Unity 5.5版本正式将Custom Data模块纳入粒子系统标准功能集，配合同版本引入的Vertex Streams系统，形成完整的粒子自定义数据传输闭环。在此之前，开发者只能通过修改粒子颜色的Alpha通道"夹带"额外信息，极大限制了Shader的表达能力。

理解自定义数据管线对Shader特效开发至关重要：一个粒子特效中的每个粒子可能处于完全不同的生命周期阶段，若不借助Custom Data逐粒子传递差异化参数，Shader中的材质参数（如`_DissolveAmount`）只能是全局统一值，导致所有粒子同步变化，无法实现错位溶解、分散翻页等复杂效果。

---

## 核心原理

### Custom Data模块的数据结构

Custom Data模块提供两个独立的数据槽：**CustomData1**和**CustomData2**，均可配置为以下两种模式之一：

- **Vector模式**：输出XYZW四个分量，每个分量可绑定独立的曲线（MinMaxCurve）或常量，粒子在其生命周期（0~1归一化时间）内按曲线采样当前值。
- **Float模式**：仅输出单个浮点值，等效于Vector的X分量。

数据在CPU粒子更新阶段写入每粒子的结构体缓冲区，随后由粒子渲染器在提交Draw Call时将这些数值打包进顶点流，以每顶点属性的形式送往GPU。

### Vertex Streams的绑定配置

要让Shader收到Custom Data，必须在粒子系统渲染器（Renderer）组件的**Vertex Streams**列表中显式添加对应项：

| Vertex Stream名称 | 对应HLSL语义 | 数据内容 |
|---|---|---|
| Custom1.xyzw | TEXCOORD1 | CustomData1的四个分量 |
| Custom2.xyzw | TEXCOORD2 | CustomData2的四个分量 |

在Shader的顶点输入结构体中，需声明匹配的语义绑定，例如：

```hlsl
struct appdata {
    float4 vertex   : POSITION;
    float4 color    : COLOR;
    float4 texcoord : TEXCOORD0;  // 粒子UV
    float4 custom1  : TEXCOORD1;  // CustomData1
    float4 custom2  : TEXCOORD2;  // CustomData2
};
```

语义序号必须与Vertex Streams列表中的实际排列顺序严格对应，顺序错位会导致数据被映射到错误的变量，这是初学者最常见的配置失误。

### 数据在粒子生命周期内的动态采样

Custom Data的每个分量绑定的曲线以粒子**归一化生命时间（0=出生，1=消亡）**作为横轴进行采样，采样结果实时写入当前帧该粒子的顶点数据。这意味着同一批粒子在同一帧中，年龄不同的粒子其Custom Data值完全独立——例如配置CustomData1.x为从0到1的线性曲线，则出生时间0.3秒、总寿命1秒的粒子在该帧的custom1.x值为0.3，而出生时间0.7秒的粒子custom1.x值为0.7。这一逐粒子差异化特性是Custom Data区别于材质全局参数的本质优势。

---

## 实际应用

### 逐粒子溶解效果

在火焰消散特效中，将CustomData1.x配置为"生命后半段从0线性升至1"的曲线，在片元Shader中将该值作为溶解噪声纹理的阈值：

```hlsl
float dissolveThreshold = i.custom1.x;
float noiseVal = tex2D(_NoiseTex, i.uv).r;
clip(noiseVal - dissolveThreshold);
```

每个粒子根据自身年龄独立溶解，新生粒子完整显示，老化粒子逐步镂空，整体呈现出有机的扩散消亡感，而非所有粒子同时消失。

### 序列帧UV动画的帧索引传递

粒子Shader播放Flipbook序列帧动画时，可用CustomData1.x存储当前帧索引（0~15对应4×4图集的16帧），在Shader中将该值换算为UV偏移量：

```hlsl
float frameIndex = floor(i.custom1.x * 16.0);
float2 frameUV = float2(
    fmod(frameIndex, 4.0) / 4.0,
    floor(frameIndex / 4.0) / 4.0
);
float2 finalUV = i.uv / 4.0 + frameUV;
```

这样每个粒子可以从图集的不同帧起播，避免所有粒子同帧同步的视觉规律感。

### 颜色混合权重控制

在技能命中特效中，用CustomData2.xyzw分别携带四种颜色状态（普通/暴击/元素/格挡）的混合权重，在Shader中执行加权混合，同一特效池的粒子可通过Custom Data区分命中类型，无需创建多套材质。

---

## 常见误区

### 误区一：认为Custom Data可以不配置Vertex Streams直接使用

Custom Data模块中的数值**不会自动**传入Shader。必须在渲染器的Vertex Streams列表中手动添加Custom1/Custom2条目，且Shader输入结构中的TEXCOORD语义序号必须与Vertex Streams列表的实际物理排列顺序一致，而非名称一致。如果Vertex Streams列表中UV在TEXCOORD0、Color在TEXCOORD1、Custom1在TEXCOORD2，则Shader中`TEXCOORD1`接收到的是Color数据而非Custom1。

### 误区二：将Custom Data与材质的`SetFloat`等同

通过`Material.SetFloat("_Param", value)`设置的材质属性是**全局常量**，同一批次所有粒子读取同一数值。Custom Data则是**逐顶点属性**，每个粒子携带独立数值。两者的传输路径完全不同：材质属性走Constant Buffer（cbuffer），Custom Data走顶点属性流（vertex attribute stream）。在需要粒子间差异化参数时错误地使用材质属性，无论如何调整曲线都只会得到全局统一的效果。

### 误区三：超过8个浮点数限制时试图增加第三组Custom Data

Unity粒子系统仅提供CustomData1和CustomData2共**2组×4分量=8个浮点数**的上限，不存在CustomData3。当参数需求超出此限制时，正确做法是将部分参数编码压缩（如将两个0~1范围的值打包进一个浮点数的整数部和小数部），或将静态参数改由纹理采样传递，而非期望系统提供更多数据槽。

---

## 知识关联

**前置知识衔接**：自定义数据管线依赖**渲染器类型**的选择——Billboard渲染器与Mesh渲染器的顶点数量不同，Vertex Streams中相同的Custom Data条目在两种渲染器下写入顶点缓冲区的行为相同，但Mesh渲染器的每个顶点都会收到**该粒子**的同一Custom Data值（非每三角面独立）。拖尾Shader（Trail Shader）中Custom Data的接入方式与普通粒子Shader完全相同，但拖尾的每个历史节点会保存各自捕获时刻的Custom Data快照，这导致一条拖尾上不同位置的节点可能携带不同的Custom Data值，是拖尾渐变效果的数据基础。

**后续知识延伸**：掌握Custom Data管线后，**混合模式**的学习将直接利用Custom Data携带的权重值——通过在Shader的Blend指令中搭配Custom Data分量作为动态混合系数，可以实现加法、乘法、Alpha混合在粒子生命周期内的动态过渡，而非固定使用某一种混合模式。Custom Data本质上是将混合控制权从材质级别下沉到了粒子个体级别。