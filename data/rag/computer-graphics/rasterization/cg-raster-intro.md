# 光栅化概述

## 概述

光栅化（Rasterization）是将几何图形（如三角形、直线）转换为屏幕像素网格的过程。具体而言，它解决的问题是：给定一组三维顶点坐标，如何确定最终显示器上哪些像素应该被点亮，以及每个像素应显示什么颜色。现代显示器由数百万个离散的像素点组成，而三维场景中的物体是连续的几何体，光栅化正是连接这两个世界的桥梁算法。

光栅化的历史可追溯到1970年代。1974年，Edwin Catmull（后来成为皮克斯总裁）在其犹他大学博士论文中提出了Z-buffer（深度缓冲）算法，这是光栅化渲染能够正确处理遮挡关系的关键发明。同年，Catmull还提出了双线性插值纹理映射的概念，奠定了现代纹理渲染的基础。1980年代，随着SGI（Silicon Graphics Inc.）工作站的普及，硬件加速的光栅化流水线逐渐成型。1992年，OpenGL 1.0正式发布，将光栅化管线标准化并开放给开发者使用。到1999年，NVIDIA发布GeForce 256，将光栅化的顶点变换计算从CPU移入GPU，标志着现代硬件光栅化时代的真正开始。2001年发布的DirectX 8.0引入了可编程着色器（Programmable Shader），使片元着色器从固定功能管线进化为通用可编程单元，彻底改变了实时渲染效果的上限。Foley等人（1990）在其经典教材《Computer Graphics: Principles and Practice》中系统归纳了这一时期光栅化算法的理论基础，至今仍是该领域最权威的参考书之一。

光栅化之所以至今仍是实时图形渲染的主流方案，原因在于其极高的计算效率。与光线追踪相比，光栅化的计算复杂度与场景中的三角形数量线性相关，而非与像素和三角形的乘积相关。一块RTX 4090 GPU每秒可处理约1820亿个光栅化操作，使得60帧甚至120帧每秒的实时渲染成为可能。即便是2022年后大量商用的硬件光线追踪（RT Core），也通常以"光栅化为主、光线追踪为辅"的混合管线形式运作，足见光栅化在效率层面的不可替代性。

## 核心原理：从三维到二维的坐标变换链

### MVP变换：三个矩阵的依次作用

光栅化渲染管线的起点是三维空间中的顶点坐标。整个变换链称为**MVP变换**（Model-View-Projection），可以用以下矩阵公式表示：

$$\mathbf{p}_{clip} = M_{proj} \cdot M_{view} \cdot M_{model} \cdot \mathbf{p}_{local}$$

其中 $M_{model}$ 将顶点从局部坐标空间（Object Space）变换到世界空间（World Space），包含平移、旋转和缩放操作；$M_{view}$ 将世界空间变换到摄像机空间（Camera Space / Eye Space），等效于将整个世界"反向移动"到摄像机的正前方；$M_{proj}$ 将摄像机空间压缩到裁剪空间（Clip Space），分为透视投影（Perspective Projection）和正交投影（Orthographic Projection）两种形式。经过这三个矩阵的依次变换后，原本分布在三维世界中的几何体被压缩进标准化设备坐标（NDC，Normalized Device Coordinates）空间，其中 x、y、z 坐标均被映射到 $[-1, 1]$ 范围内（OpenGL约定；DirectX的z范围为 $[0, 1]$）。随后，**透视除法**（将 x、y、z 各分量除以齐次坐标 $w$）和**视口变换**将NDC坐标最终映射到屏幕像素坐标。

例如，一个位于世界坐标 $(3.0,\ 1.5,\ -5.0)$ 的顶点，经过视图矩阵平移和透视投影矩阵压缩后，可能变换为NDC坐标 $(0.42,\ 0.18,\ 0.87)$，再经过视口变换映射至 $1920 \times 1080$ 分辨率屏幕上的像素位置约为 $(883,\ 637)$。这一过程中，所有数学操作均在GPU的矩阵运算单元（如NVIDIA的Tensor Core或通用CUDA Core）上并行完成，成千上万个顶点同时被处理。

视口变换公式为：

$$x_{screen} = \left(\frac{x_{NDC} + 1}{2}\right) \cdot W, \quad y_{screen} = \left(\frac{1 - y_{NDC}}{2}\right) \cdot H$$

其中 $W$ 和 $H$ 分别为屏幕宽度和高度（像素数）。注意 $y$ 轴的翻转符号，这是因为NDC中 $y$ 轴向上为正，而屏幕像素坐标通常以左上角为原点、向下为正。

### 透视投影矩阵的结构

透视投影矩阵的标准形式（OpenGL右手坐标系）为：

$$M_{proj} = \begin{pmatrix} \frac{f}{aspect} & 0 & 0 & 0 \\ 0 & f & 0 & 0 \\ 0 & 0 & \frac{z_{far}+z_{near}}{z_{near}-z_{far}} & \frac{2 \cdot z_{far} \cdot z_{near}}{z_{near}-z_{far}} \\ 0 & 0 & -1 & 0 \end{pmatrix}$$

其中 $f = \cot(\text{fov}/2)$ 为焦距因子，$\text{fov}$ 为垂直视场角（Field of View），$aspect$ 为宽高比，$z_{near}$ 和 $z_{far}$ 分别为近裁剪面和远裁剪面距离。矩阵第四行的 $-1$ 使得变换后的 $w$ 分量等于原始的 $-z$，正是这个 $w$ 值在透视除法中产生近大远小的透视效果。

案例：设 $\text{fov} = 60°$，$aspect = 16/9$，$z_{near} = 0.1$，$z_{far} = 1000$，则 $f = \cot(30°) \approx 1.732$，$f/aspect \approx 0.974$。一个位于摄像机空间 $z = -10$ 处的点，其 $w$ 分量在裁剪空间中将变为 $10$，透视除法后各分量均除以 $10$，从而使该点在屏幕上显示为正常大小；而同样的点若位于 $z = -100$ 处，则 $w = 100$，屏幕投影坐标缩小为十分之一，体现出"近大远小"效果。

## 三角形遍历：光栅化的核心步骤

### 重心坐标覆盖测试

GPU确定哪些像素位于三角形内部的方法基于**重心坐标（Barycentric Coordinates）**判断。对于屏幕上的像素点 $P$ 和三角形顶点 $A$、$B$、$C$，若 $P$ 可以表示为：

$$P = \alpha A + \beta B + \gamma C, \quad \alpha + \beta + \gamma = 1$$

且 $\alpha \geq 0,\ \beta \geq 0,\ \gamma \geq 0$，则该像素位于三角形内部，应被渲染。GPU对屏幕上三角形包围盒（Bounding Box）内的每个像素并行执行此判断，通常以 $2 \times 2$ 像素的"四元组（Quad）"为最小并行单元进行处理，这是GPU硬件架构对导数运算（dFdx/dFdy）支持的直接体现。

重心坐标的实际计算可通过有向面积的比值获得：

$$\alpha = \frac{\text{Area}(PBC)}{\text{Area}(ABC)}, \quad \beta = \frac{\text{Area}(APC)}{\text{Area}(ABC)}, \quad \gamma = \frac{\text{Area}(ABP)}{\text{Area}(ABC)}$$

其中三角形有向面积可用叉积高效计算：$\text{Area}(ABC) = \frac{1}{2}|(B-A) \times (C-A)|$，使得整个判断过程仅需少量乘加运算。边界像素的处理规则（即恰好落在三角形边上的像素归属哪个三角形）在OpenGL和DirectX规范中均有明确的"左上规则（Top-Left Rule）"定义，以避免共享边的两个三角形对同一像素重复着色。

### 顶点属性插值与透视矫正

重心坐标同时用于在三角形内部插值顶点属性，例如颜色、纹理坐标（UV）和法线向量，线性插值公式为：

$$\text{attr}(P) = \alpha \cdot \text{attr}(A) + \beta \cdot \text{attr}(B) + \gamma \cdot \text{attr}(C)$$

例如，若三角形三个顶点的UV坐标分别为 $(0,0)$、$(1,0)$、$(0,1)$，则三角形中心点（$\alpha = \beta = \gamma = 1/3$）处的UV值插值结果为 $(1/3,\ 1/3)$，可直接用于采样纹理贴图。

然而，上述线性插值在屏幕空间中直接执行会产生错误，因为透视投影是非线性变换。Shirley与Marschner（2009）在《Fundamentals of Computer Graphics》第三版中对此有详细推导，指出必须对插值量进行**透视矫正插值（Perspective-Correct Interpolation）**，正确公式为：

$$\text{attr}(P) = \frac{\alpha \cdot \text{attr}(A)/w_A + \beta \cdot \text{attr}(B)/w_B + \gamma \cdot \text{attr}(C)/w_C}{\alpha/w_A + \beta/w_B + \gamma/w_C}$$

其中 $w_A$、$w_B$、$w_C$ 为各顶点裁剪空间的 $w$ 分量（即各顶点的原始摄像机空间深度值）。若不进行透视矫正，纹理贴图在倾斜的多边形上将出现明显扭曲，这在早期3D游戏（如PS1时代游戏）中是常见的视觉瑕疵——PlayStation 1的GTE（Geometry Transformation Engine）协处理器没有实现透视矫正插值，导致大量游戏出现纹理"游动"现象，成为一代玩家的集体记忆。

？ **思考：为什么GPU以 $2 \times 2$ 像素四元组为单位执行片元着色器，即使某个三角形只覆盖了其中1个像素？这种设计在计算效率上有何代价？当场景中存在大量面积极小的三角形时，这一代价会如何被放大？**

## Z-Buffer深度测试与遮挡处理

Z-Buffer是光栅化正确处理物体遮挡关系的核心机制，由Edwin Catmull于1974年首次提出，Wolfgang Strasser于同年在其博士论文中也独立描述了等价算法。渲染开始时，深度缓冲区被初始化为最大深度值 $1.0$（在NDC空间中远裁剪面处）。每当一个片元（Fragment）通过三角形覆盖测试后，其深度值 $z$ 会与深度缓冲区中对应位置的已存储值进行比较：

$$\text{if } z_{new} < z_{buffer}[x][y]: \quad \text{更新颜色缓冲区及深度缓冲区}$$

若新片元的 $z$ 值更小（更靠近相机），则更新颜色缓冲区（Color Buffer）和深度缓冲区；否则该片元被丢弃，不执行后续的片元着色器计算。这一算法的空间复杂度为 $O(W \times H)$（$W$、$H$ 为屏幕分辨率），是与场景几何复杂度无关的常数级方法，代价是无法直接处理半透明物体的正确排序——半透明物体需要先从后向前排序，再使用Alpha Blending混合，即"画家算法（Painter's Algorithm）"的变体。

Z-Buffer算法的另一个重要工程价值在于支持**Early-Z**优化：现代GPU在执行片元着色器之前先执行深度测试，若片元未能通过测试则立即丢弃，完全跳过可能代价高昂的着色计算。这一机制在复杂场景中可将片元着色器的有效调用