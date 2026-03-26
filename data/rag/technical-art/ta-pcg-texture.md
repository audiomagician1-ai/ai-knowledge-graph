---
id: "ta-pcg-texture"
concept: "程序化纹理"
domain: "technical-art"
subdomain: "pcg"
subdomain_name: "程序化生成"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 程序化纹理

## 概述

程序化纹理（Procedural Texture）是指通过数学公式、算法和节点逻辑生成的纹理图像，而非依赖手工绘制或扫描照片素材。与传统位图纹理不同，程序化纹理在任何分辨率下均可无损输出，因为其底层数据是描述"如何生成像素颜色"的函数，而非固定像素阵列。Substance Designer 是目前行业中最主流的程序化纹理创作工具，由 Allegorithmic 公司开发（2019年被 Adobe 收购），其核心工作模式是将各类噪波、滤镜、混合节点连接成有向无环图（DAG），最终输出 PBR 材质所需的 Base Color、Normal、Roughness、Metallic 等贴图通道。

程序化纹理的概念可追溯至1985年 Ken Perlin 为电影《电子世界争霸战》（Tron）开发的 Perlin Noise 算法，该噪波函数通过在三维空间中对随机梯度向量做插值，生成连续且自然的有机纹理图案，奠定了程序化纹理生成的数学基础。此后 Voronoi 细胞噪波、FBM（分形布朗运动）等算法相继被引入纹理生成领域，使程序化方法能够模拟从岩石到木纹的各类自然表面。

对技术美术而言，程序化纹理的价值在于参数驱动的可变性与无限平铺能力。一张手绘 2K 贴图只能表示一种固定外观，而同一套 Substance 节点图可通过调整"Seed"（随机种子）参数在数秒内输出数百个外观各异的变体，直接服务于开放世界游戏中的大规模地形资产管道。

---

## 核心原理

### 节点图与函数合成

Substance Designer 的程序化纹理以节点图（Node Graph）为载体。每个节点本质上是一个像素处理函数 `f(u, v) → color`，接收 UV 坐标作为输入，输出对应位置的颜色或灰度值。节点之间通过连线将上游节点的输出作为下游节点的输入，形成函数嵌套关系。例如，将一个 Gaussian Noise 节点输出接入 Histogram Scan 节点，再接入 Bevel 节点，等效于对同一 UV 坐标依次执行三个函数变换：`Bevel(HistogramScan(GaussianNoise(u, v)))`。整个节点图最终等价于一个从 UV 空间到像素颜色的复合函数，这正是程序化纹理"数学本质"的具体体现。

### 噪波函数的核心作用

几乎所有自然表面纹理的生成都依赖噪波函数提供随机性基底。Substance Designer 内置的噪波类型包括：

- **Perlin Noise**：公式核心为 `dot(gradient[hash(xi, yj)], (x - xi, y - yj))` 后做三次 Fade 插值，输出连续光滑的灰度场，适合生成云雾、大理石纹。
- **Voronoi（细胞噪波）**：对每个像素计算其到最近特征点的距离 `F1` 和次近距离 `F2`，`F2 - F1` 的组合可生成裂缝或细胞结构，广泛用于岩石节理、皮革纹理。
- **FBM（分形布朗运动）**：将多个不同频率（Octave）的 Perlin Noise 叠加，公式为 `Σ(amplitude_i × Perlin(frequency_i × uv))`，典型参数为 8 个八度，振幅以 0.5 的比率衰减，生成具有自相似分形特征的自然地表纹理。

选择噪波类型和调整其 Scale、Disorder、Randomness 参数是程序化纹理制作中最基础的创作决策。

### 灰度图驱动与通道解耦

Substance Designer 中的标准工作流将纹理生成拆分为"灰度构建阶段"与"颜色着色阶段"。在灰度阶段，技术美术首先构建一张描述表面高低起伏的高度图（Height Map），然后通过内置的 Normal Map 节点将其转换为切线空间法线贴图（使用 Sobel 算子对高度图求梯度）。Roughness 贴图通常来自对高度图的二次处理：越凸起的区域（高度值越大）往往对应更光滑的表面，可通过 Histogram Range 节点将高度值反转并压缩到 0.2–0.8 区间映射为粗糙度。这种灰度驱动彩色的策略保证了各 PBR 通道在视觉上的物理一致性，是工业级材质制作的核心规范。

---

## 实际应用

**游戏地形材质制作**：在 Substance Designer 中制作一套苔藓岩石材质时，典型流程为：① 用 FBM Noise 生成岩石基础轮廓高度图；② 用 Slope Blur 节点模拟风化侵蚀效果；③ 用 Ambient Occlusion 节点烘焙高度图的遮蔽信息；④ 将 AO 贴图与两张手工绘制的颜色样本在 Gradient Map 节点中混合，分别着色岩石基底（灰褐色）和苔藓区域（绿色）；⑤ 输出分辨率可在 256×256 到 4096×4096 之间任意切换而无需修改节点逻辑。该流程在 AAA 游戏项目中可将一名技术美术每周处理的地形材质变体数量从约 5 个提升至 30 个以上。

**Substance 图的参数化暴露**：Substance Designer 允许将节点内部参数"暴露"（Expose）为图层级别的公开参数，打包成 `.sbsar` 格式后，引擎端（如 Unreal Engine 5 的 Substance Plugin）可在运行时动态传入参数值实时更新贴图内容。例如，将苔藓覆盖率（Moss Coverage）参数暴露后，场景设计师可在引擎中直接拖动滑条从 0% 到 100% 控制苔藓密度，实现程序化材质在游戏世界中的实例化多样性。

---

## 常见误区

**误区一：程序化纹理与位图纹理不能混用**

实际上 Substance Designer 完全支持将扫描照片（Bitmap）或手绘纹理导入为输入节点，与程序化噪波混合。许多专业管道采用"扫描驱动的程序化材质"策略：用真实岩石扫描图提供微观细节的颜色信息，用程序化噪波控制宏观形态和可平铺性，二者结合兼顾真实感与可复用性。认为程序化纹理必须100%由算法生成、完全排斥位图输入是错误的工作假设。

**误区二：更高的 Noise 八度数总是带来更好的细节**

FBM 中叠加更多 Octave 会增加高频细节，但当 Octave 超过 8 层后，在 2K 分辨率的输出贴图中高频分量会因像素采样限制而变成锯齿噪点，不仅视觉效果下降，还会额外增加 Substance 图的计算时间。根据目标输出分辨率和贴图的 Texel Density，4–6 个八度通常是兼顾细节与计算效率的最优参数范围。盲目堆叠 Octave 是初学者最常见的参数滥用问题。

**误区三：程序化纹理自动具有物理正确的 PBR 输出**

节点图的拓扑结构本身不保证 PBR 正确性。例如，若 Base Color 贴图中混入了烘焙光照信息（类似 Diffuse 贴图的旧管线做法），即使在 PBR 渲染管线中使用也会导致错误的光照叠加。程序化纹理流程必须在节点设计阶段明确区分"光照无关的 Albedo 数据"与"几何信息派生的 Normal/Roughness 数据"，才能保证最终材质在不同光照环境下的物理一致表现。

---

## 知识关联

程序化纹理的学习以**程序化生成概述**为前置知识，后者建立了"用算法代替手工资产"的基本思维模型，而程序化纹理则是该思维在二维像素域的具体实现——理解 Perlin Noise 如何从一维连续函数扩展到二维 UV 空间是进入 Substance Designer 节点图学习的关键跨越。

从工具链角度，Substance Designer 生成的 `.sbsar` 包与 **Substance Painter** 的智能材质系统直接对接，前者负责材质的程序化定义，后者负责在三维模型表面进行手工绘制覆盖；理解程序化纹理的通道结构（Height → Normal 的派生关系、AO 的叠加逻辑）是使用 Substance Painter 智能材质时调参的必要基础。在游戏引擎侧，Unreal Engine 5 的 Substrate 材质系统和 Unity 的 Shader Graph 均支持将程序化纹理的输出直接接入 PBR 着色器，掌握程序化纹理各通道的物理意义是正确配置引擎材质参数的前提条件。